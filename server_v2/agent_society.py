"""L9 Multi-Agent Shadow Society — planner / validator / challenger / arbitration.

Advisory only by default. With ENABLE_AGENT_ARBITRATION the arbitration result
may influence the EXECUTION RECOMMENDATION (never the deterministic fallback,
never a hidden reroute). Hard recursion bound: MAX_AGENT_ROUNDS = 2.
"""
from __future__ import annotations

MAX_AGENT_ROUNDS = 2


def planner_agent(prompt: str, cognition: dict) -> dict:
    cls = cognition.get("workflow_classification", {})
    depth = cls.get("reasoning_depth", "moderate")
    steps = cognition.get("execution_graph", {}).get("nodes", [])
    return {
        "agent": "planner",
        "recommendation": {
            "strategy": "high_quality_single_provider_with_validation"
            if depth == "deep" else "fast_single_provider",
            "steps": steps,
            "preferred_providers": cls.get("preferred_providers", []),
        },
    }


def validator_agent(cognition: dict) -> dict:
    risk = cognition.get("risk_analysis", {}).get("level", "normal")
    return {
        "agent": "validator",
        "recommendation": {
            "require_validation": risk in ("critical", "high"),
            "checks": ["hallucination", "legal_consistency", "policy"],
            "min_output_chars": 200,
        },
    }


def challenger_agent(cognition: dict) -> dict:
    cls = cognition.get("workflow_classification", {})
    weak = cls.get("complexity") in ("simple", "medium") and cls.get("workflow_type") == "legal"
    return {
        "agent": "challenger",
        "recommendation": {
            "challenge": "verify_depth_sufficient_for_legal" if weak else "none",
            "force_alternative": bool(weak),
            "weak_reasoning_suspected": bool(weak),
        },
    }


def arbitration_agent(planner: dict, validator: dict, challenger: dict) -> dict:
    """Deterministic arbitration — no debate loop; single pass, bounded."""
    require_validation = bool(validator.get("recommendation", {}).get("require_validation"))
    force_alt = bool(challenger.get("recommendation", {}).get("force_alternative"))
    decision = "execute_with_validation" if require_validation else "execute_standard"
    if force_alt:
        decision = "execute_with_validation_and_alternative_review"
    return {
        "agent": "arbitration",
        "rounds": 1,
        "max_rounds": MAX_AGENT_ROUNDS,
        "decision": decision,
        "based_on": ["planner", "validator", "challenger"],
        "preferred_providers": planner.get("recommendation", {}).get("preferred_providers", []),
    }


def run_agent_society(prompt: str, cognition: dict, enabled: bool) -> dict:
    """Single bounded pass. Shadow unless `enabled` (still recommendation-only
    w.r.t. the deterministic chain — never a hidden reroute)."""
    try:
        p = planner_agent(prompt, cognition)
        v = validator_agent(cognition)
        c = challenger_agent(cognition)
        a = arbitration_agent(p, v, c)
        return {
            "enabled": bool(enabled),
            "mode": "active_recommendation" if enabled else "shadow",
            "planner_recommendation": p,
            "validator_recommendation": v,
            "challenger_recommendation": c,
            "arbitration_result": a,
            "max_rounds": MAX_AGENT_ROUNDS,
            "rounds_used": 1,
        }
    except Exception as exc:
        return {"enabled": False, "mode": "shadow", "error": str(exc)[:160],
                "rounds_used": 0, "max_rounds": MAX_AGENT_ROUNDS}
