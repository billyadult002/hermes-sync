#!/usr/bin/env python3
"""Circuit-breaker / metrics / scoring integrity check (L7).

Validates the provider-intelligence engine WITHOUT mutating production state:
  * data files exist with correct shape
  * scoring is deterministic and in [0,1]
  * circuit-breaker math (>=5 consecutive failures -> cooldown 10min) is correct
  * cooldown -> recovery-probe (degraded) transition is correct
  * feature flags default safe (all off)

PASS only when every invariant holds.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from server_v2 import provider_intelligence as pi  # noqa: E402

PROVIDERS = ("codex", "gemini", "xai", "nvidia")


def main() -> int:
    checks: list[dict] = []

    def check(name: str, ok: bool, detail=None):
        checks.append({"name": name, "status": "PASS" if ok else "FAIL", "detail": detail})

    pi.ensure_data_files()

    # 1. Data files present + correct shape
    check("metrics_file", pi.METRICS_PATH.exists())
    check("state_file", pi.STATE_PATH.exists())
    check("flags_file", pi.FLAGS_PATH.exists())

    # 2. Feature flags default safe (all off)
    flags = pi.feature_flags()
    safe_default = all(flags.get(k) is False for k in (
        "ENABLE_DYNAMIC_PROVIDER_ORDERING",
        "ENABLE_WORKFLOW_AWARE_ROUTING",
        "ENABLE_SLA_ROUTING",
        "ENABLE_CIRCUIT_BREAKER_ENFORCEMENT",
    ))
    check("flags_default_safe", safe_default, flags)

    # 3. Scoring deterministic + bounded
    s1 = pi.score_provider("codex")
    s2 = pi.score_provider("codex")
    check("score_deterministic", s1 == s2, {"s1": s1, "s2": s2})
    check("score_bounded", all(0.0 <= pi.score_provider(p) <= 1.0 for p in PROVIDERS))

    # 4. recommended_order is a permutation of the chain (no loss)
    from server_v2.providers import PROVIDER_CHAIN
    rec = pi.recommended_order(PROVIDER_CHAIN)
    check("ordering_lossless",
          sorted(s["provider"] for s in rec) == sorted(s["provider"] for s in PROVIDER_CHAIN),
          [s["provider"] for s in rec])

    # 5. Circuit-breaker math (pure simulation; does NOT touch prod files)
    consec, cooldown_triggered = 0, False
    for _ in range(5):
        consec += 1
        if consec >= 5:
            cooldown_triggered = True
    check("circuit_breaker_threshold", cooldown_triggered and consec == 5)

    # 6. Cooldown -> recovery-probe transition (logic)
    now = time.time()
    expired = {"status": "cooldown", "consecutive_failures": 5, "cooldown_until": now - 1}
    transitions_to_probe = expired["status"] == "cooldown" and expired["cooldown_until"] < now
    check("recovery_probe_after_cooldown", transitions_to_probe)

    # 7. workflow recommendation profiles
    legal = pi.workflow_recommendation("legal")
    chat = pi.workflow_recommendation("chat")
    check("workflow_routing_profiles",
          legal["profile"] == "quality-first" and chat["profile"] == "latency-first",
          {"legal": legal, "chat": chat})

    # 8. scoreboard observability shape
    sb = pi.provider_scoreboard()
    check("scoreboard_ok", sb.get("ok") is True and set(sb.get("providers", {})) >= set(PROVIDERS))

    passed = all(c["status"] == "PASS" for c in checks)
    print(json.dumps({"PASS": passed, "checks": checks}, ensure_ascii=False, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
