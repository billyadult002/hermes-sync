"""L9 Cognitive Runtime — workflow cognition + execution graph (shadow).

Pure, deterministic, no I/O, never raises. Produces a cognitive trace and a
recommended execution graph. Recommendation only — never takes over execution
unless a feature flag explicitly activates it.
"""
from __future__ import annotations

from .workflow_intelligence import analyze_prompt

_LEGAL_GRAPH = ["compliance", "risk", "contract_review", "sanctions", "synthesis"]
_GENERIC_GRAPH = ["analyze", "generate", "review"]


def reasoning_depth(profile: dict) -> str:
    c = profile.get("complexity", "medium")
    return {"critical": "deep", "complex": "deep", "medium": "moderate", "simple": "shallow"}.get(c, "moderate")


def risk_level(profile: dict, mode: str) -> str:
    c = profile.get("complexity", "medium")
    if mode == "legal" and c in ("critical", "complex"):
        return "critical"
    if c == "critical":
        return "high"
    if c == "complex":
        return "elevated"
    return "normal"


def build_execution_graph(mode: str, profile: dict) -> dict:
    """Deterministic dependency graph (recommendation/shadow)."""
    if mode == "legal":
        nodes = list(_LEGAL_GRAPH)
    else:
        nodes = list(_GENERIC_GRAPH)
    edges = [{"from": nodes[i], "to": nodes[i + 1]} for i in range(len(nodes) - 1)]
    return {
        "nodes": nodes,
        "edges": edges,
        "decomposition": nodes,
        "parallelizable": [],
        "critical_path": nodes,
    }


def cognitive_analyze(prompt: str, mode: str = "legal") -> dict:
    """Top-level cognitive trace (shadow recommendation)."""
    try:
        profile = analyze_prompt(prompt, mode)
        graph = build_execution_graph(mode, profile)
        return {
            "workflow_classification": {
                "workflow_type": mode,
                "complexity": profile.get("complexity"),
                "reasoning_depth": reasoning_depth(profile),
                "risk_level": risk_level(profile, mode),
                "sla": profile.get("sla"),
                "preferred_providers": profile.get("preferred_providers", []),
            },
            "execution_graph": graph,
            "risk_analysis": {
                "level": risk_level(profile, mode),
                "tokens": profile.get("tokens"),
                "signals": profile.get("signals", {}),
            },
            "shadow": True,  # recommendation only
        }
    except Exception as exc:
        return {"shadow": True, "error": str(exc)[:160],
                "workflow_classification": {"workflow_type": mode}}
