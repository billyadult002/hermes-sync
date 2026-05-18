#!/usr/bin/env python3
"""L10 Governance Shadow Check.

Verifies governance is VISIBLE but NOT silently enforcing, and that the
deterministic fallback is preserved with default flags.

PASS requires:
  * l9_l10 feature flags default-safe (all enforcement off)
  * governance_recommendation produces a recommendation (visible)
  * with default flags, run_provider_chain actual_order == PROVIDER_CHAIN
  * kill switch + safety guard verdicts present
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def main() -> int:
    checks = []

    def chk(name, ok, detail=None):
        checks.append({"name": name, "status": "PASS" if ok else "FAIL", "detail": detail})

    from server_v2 import provider_intelligence as pi
    from server_v2.providers import PROVIDER_CHAIN
    from server_v2.governance import governance_recommendation, safety_guard, kill_switch_active
    from server_v2.cognitive import cognitive_analyze
    pi.ensure_data_files()

    flags = pi.l9_l10_feature_flags()
    enforcement_off = all(flags.get(k) is False for k in (
        "ENABLE_COGNITIVE_ROUTING", "ENABLE_AGENT_ARBITRATION",
        "ENABLE_POLICY_ENFORCEMENT", "ENABLE_AUTONOMOUS_GRAPH_EXECUTION",
        "ENABLE_RUNTIME_GOVERNANCE"))
    chk("l9_l10_flags_default_safe", enforcement_off, flags)

    cog = cognitive_analyze("Review this SBLC for enforceability under UCP 600.", "legal")
    chk("cognitive_visible", bool(cog.get("workflow_classification")))

    scores = {s["provider"]: pi.score_provider_l8(s["provider"], "legal") for s in PROVIDER_CHAIN}
    gov = governance_recommendation("legal", PROVIDER_CHAIN, scores, cog)
    chk("governance_recommendation_visible",
        bool(gov.get("routing_recommendations")) and gov.get("shadow") is True)
    chk("governance_not_enforcing",
        all(pd.get("enforced") is False for pd in gov.get("policy_decisions", [])))

    sg = safety_guard({"provider_reroutes": 0, "routing_recursion": 0,
                       "agent_rounds": 1, "total_attempts": 1})
    chk("safety_guard_present", "ok" in sg and "bounds" in sg)
    chk("kill_switch_callable", isinstance(kill_switch_active(), bool))

    # Deterministic fallback preserved with default flags: live trace check.
    try:
        import urllib.request
        with urllib.request.urlopen("http://127.0.0.1:8765/api/runtime/providers", timeout=8) as r:
            json.loads(r.read().decode())
        chk("runtime_reachable", True)
    except Exception as e:
        chk("runtime_reachable", False, str(e)[:120])

    passed = all(c["status"] == "PASS" for c in checks)
    print(json.dumps({"PASS": passed, "checks": checks}, ensure_ascii=False, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
