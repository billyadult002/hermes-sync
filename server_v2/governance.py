"""L10 Governance Runtime — policy + recommendation + safety guard + kill switch.

Shadow/advisory by default. Governance NEVER silently enforces: every decision
is recorded in trace.governance. Enforcement requires an explicit flag AND is
still bounded by the deterministic-fallback and safety-guard invariants.
A one-line kill switch (EMERGENCY_DISABLE_GOVERNANCE) forces pure deterministic.
"""
from __future__ import annotations

import os

from .provider_policy import evaluate as _policy_eval

# Hard safety bounds (LAYER 7).
MAX_PROVIDER_REROUTE = 4
MAX_ROUTING_RECURSION = 1
MAX_GOVERNANCE_ROUNDS = 1


def kill_switch_active() -> bool:
    """EMERGENCY_DISABLE_GOVERNANCE -> instant deterministic fallback."""
    return os.getenv("EMERGENCY_DISABLE_GOVERNANCE", "").strip().lower() in ("1", "true", "yes")


def governance_recommendation(mode: str, chain: list[dict], scores: dict,
                              cognition: dict) -> dict:
    """Pure advisory governance decision (no execution side-effects)."""
    try:
        pol = _policy_eval(mode, chain, scores)
        cls = cognition.get("workflow_classification", {})
        sla = cls.get("sla", "balanced")
        risk = cognition.get("risk_analysis", {}).get("level", "normal")
        rec_order = [s["provider"] for s in
                     sorted(chain, key=lambda s: (-float(scores.get(s["provider"], 0.5)),
                                                  s["provider"]))]
        policy_action = "require_validation" if (mode == "legal" and risk in ("critical", "high")) \
            else "none"
        return {
            "policy_decisions": [{
                "mode": mode,
                "allowed_chain": pol.get("allowed_chain"),
                "denied": pol.get("denied"),
                "enforced": False,
            }],
            "routing_recommendations": [{"recommended_provider_order": rec_order}],
            "sla_recommendations": [{"recommended_sla": sla, "risk_level": risk}],
            "recommended_policy_action": policy_action,
            "shadow": True,
        }
    except Exception as exc:
        return {"policy_decisions": [], "routing_recommendations": [],
                "sla_recommendations": [], "shadow": True, "error": str(exc)[:160]}


def safety_guard(state: dict) -> dict:
    """Detect governance deadlock / provider storm / runaway recursion.

    Pure check over a small state dict; returns violations + a safe verdict.
    """
    reroutes = int(state.get("provider_reroutes", 0) or 0)
    recursion = int(state.get("routing_recursion", 0) or 0)
    agent_rounds = int(state.get("agent_rounds", 0) or 0)
    attempts = int(state.get("total_attempts", 0) or 0)
    violations = []
    if reroutes > MAX_PROVIDER_REROUTE:
        violations.append("provider_storm")
    if recursion > MAX_ROUTING_RECURSION:
        violations.append("routing_recursion")
    if agent_rounds > 2:
        violations.append("agent_debate_loop")
    if attempts > 24:  # 4 providers * up to 3 attempts, generous ceiling
        violations.append("retry_explosion")
    return {
        "ok": not violations,
        "violations": violations,
        "bounds": {
            "MAX_PROVIDER_REROUTE": MAX_PROVIDER_REROUTE,
            "MAX_ROUTING_RECURSION": MAX_ROUTING_RECURSION,
            "MAX_GOVERNANCE_ROUNDS": MAX_GOVERNANCE_ROUNDS,
        },
        "kill_switch_active": kill_switch_active(),
    }
