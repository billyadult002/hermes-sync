"""L8 Enterprise Provider Policy Engine (advisory by default).

Deterministic allow/deny + SLA constraints per workflow. Returns a decision
record for auditability. ENFORCEMENT is flag-gated (ENABLE_POLICY_ROUTING);
default = advisory only, execution unchanged. Never raises.
"""
from __future__ import annotations

_POLICY = {
    "legal": {
        "allow": ["codex", "gemini", "xai", "nvidia"],
        "deny": [],
        "latency_max_ms": None,
        "min_score": 0.0,
    },
    "war_room": {
        "allow": ["codex", "gemini", "xai", "nvidia"],
        "deny": [],
        "latency_max_ms": 5000,
        "min_score": 0.0,
    },
    "chat": {
        "allow": ["codex", "gemini", "xai", "nvidia"],
        "deny": [],
        "latency_max_ms": 8000,
        "min_score": 0.0,
    },
}


def policy_for(mode: str) -> dict:
    return _POLICY.get((mode or "").lower(), _POLICY["legal"])


def evaluate(mode: str, chain: list[dict], scores: dict | None = None) -> dict:
    """Return {allowed_chain, denied, reason, policy, enforced:False}."""
    try:
        pol = policy_for(mode)
        scores = scores or {}
        allowed, denied = [], []
        for step in chain:
            p = step.get("provider")
            reason = None
            if pol["deny"] and p in pol["deny"]:
                reason = "deny_list"
            elif pol["allow"] and p not in pol["allow"]:
                reason = "not_in_allow_list"
            elif pol["min_score"] and float(scores.get(p, 1.0)) < pol["min_score"]:
                reason = "below_min_score"
            if reason:
                denied.append({"provider": p, "reason": reason})
            else:
                allowed.append(step)
        # Safety: never produce an empty chain (deterministic fallback).
        if not allowed:
            allowed = list(chain)
            denied = []
        return {
            "policy": pol,
            "allowed_chain": [f'{s["provider"]}:{s["model"]}' for s in allowed],
            "allowed_steps": allowed,
            "denied": denied,
            "enforced": False,  # advisory unless ENABLE_POLICY_ROUTING flips it
            "reason": "advisory_evaluation",
        }
    except Exception as exc:
        return {"policy": {}, "allowed_chain": [], "allowed_steps": list(chain),
                "denied": [], "enforced": False, "reason": f"policy_error:{str(exc)[:120]}"}
