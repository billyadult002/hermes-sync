"""L8 Multi-Agent Orchestration (shadow planner; flag-gated execution).

Planner / Execution / Validator / Arbitration roles. With ENABLE_MULTI_AGENT
off (default) this only produces a PLAN recommendation in the trace — the
single-provider chain still does the real work. No hidden execution.
"""
from __future__ import annotations


def plan(prompt: str, profile: dict) -> dict:
    """Planner Agent — decompose + choose execution strategy (advisory)."""
    complexity = profile.get("complexity", "medium")
    if complexity in ("critical", "complex"):
        strategy = "single_provider_high_quality_with_validation"
        steps = ["analyze", "generate", "validate", "finalize"]
    else:
        strategy = "single_provider_fast"
        steps = ["generate", "finalize"]
    return {
        "agent": "planner",
        "strategy": strategy,
        "steps": steps,
        "preferred_providers": profile.get("preferred_providers", []),
        "sla": profile.get("sla", "balanced"),
    }


def validate_output(text: str) -> dict:
    """Validator Agent — heuristic hallucination / substance / policy check."""
    t = (text or "").strip()
    low = t.lower()
    banned = ("fallback response generated", "系统繁忙", "兜底回复", "no substantive content")
    hallucination_flags = [b for b in banned if b in low]
    return {
        "agent": "validator",
        "length": len(t),
        "substantive": len(t) > 200 and not hallucination_flags,
        "hallucination_flags": hallucination_flags,
        "policy_compliant": not hallucination_flags,
    }


def arbitrate(candidates: list[dict]) -> dict:
    """Arbitration Agent — pick best candidate (deterministic, by length+valid)."""
    valid = [c for c in candidates if c.get("valid")]
    pool = valid or candidates
    if not pool:
        return {"agent": "arbitration", "selected": None, "reason": "no_candidates"}
    best = max(pool, key=lambda c: (1 if c.get("valid") else 0, int(c.get("length") or 0)))
    return {"agent": "arbitration", "selected": best.get("provider"),
            "reason": "highest_valid_length", "considered": len(pool)}


def plan_only_shadow(prompt: str, profile: dict, enabled: bool) -> dict:
    """Return the multi-agent plan; execution remains single-chain unless enabled."""
    p = plan(prompt, profile)
    return {
        "enabled": bool(enabled),
        "mode": "active" if enabled else "shadow",
        "planner": p,
        "roles": ["planner", "execution", "validator", "arbitration"],
        "note": "shadow: plan recorded, real execution via deterministic chain"
                if not enabled else "active",
    }
