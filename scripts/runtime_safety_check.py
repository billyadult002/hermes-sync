#!/usr/bin/env python3
"""L10 Runtime Safety Check — no infinite loops / recursion / provider storms.

Static + bounded-simulation verification of the safety invariants. Does NOT
mutate state or run real provider calls.
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

    from server_v2.governance import safety_guard, MAX_PROVIDER_REROUTE, MAX_ROUTING_RECURSION
    from server_v2.agent_society import MAX_AGENT_ROUNDS
    from server_v2.providers import MAX_ATTEMPTS_PER_PROVIDER, PROVIDER_CHAIN

    # 1. Bounded retry: chain attempts are finite.
    max_total = len(PROVIDER_CHAIN) * MAX_ATTEMPTS_PER_PROVIDER
    chk("retry_bounded", max_total <= 24, {"max_total_attempts": max_total})

    # 2. Agent recursion bounded.
    chk("agent_rounds_bounded", MAX_AGENT_ROUNDS <= 2, {"MAX_AGENT_ROUNDS": MAX_AGENT_ROUNDS})

    # 3. Routing recursion bounded.
    chk("routing_recursion_bounded", MAX_ROUTING_RECURSION <= 1,
        {"MAX_ROUTING_RECURSION": MAX_ROUTING_RECURSION})

    # 4. Safety guard catches provider storm.
    storm = safety_guard({"provider_reroutes": MAX_PROVIDER_REROUTE + 5})
    chk("detects_provider_storm", "provider_storm" in storm["violations"] and not storm["ok"])

    # 5. Safety guard catches retry explosion.
    explode = safety_guard({"total_attempts": 999})
    chk("detects_retry_explosion", "retry_explosion" in explode["violations"])

    # 6. Healthy state passes.
    healthy = safety_guard({"provider_reroutes": 1, "routing_recursion": 0,
                            "agent_rounds": 1, "total_attempts": 3})
    chk("healthy_state_ok", healthy["ok"] is True)

    # 7. No stuck agents — agent society is single-pass (rounds_used <= max).
    from server_v2.agent_society import run_agent_society
    from server_v2.cognitive import cognitive_analyze
    soc = run_agent_society("x", cognitive_analyze("x", "legal"), True)
    chk("agent_single_pass", soc.get("rounds_used", 0) <= MAX_AGENT_ROUNDS)

    passed = all(c["status"] == "PASS" for c in checks)
    print(json.dumps({"PASS": passed, "checks": checks}, ensure_ascii=False, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
