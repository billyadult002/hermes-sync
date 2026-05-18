"""L8 Workflow Intelligence — complexity / SLA / provider-affinity classifier.

Pure, deterministic, no I/O, never raises. Produces an execution PROFILE that
the chain consumes in SHADOW (recommendation only) unless a flag enables it.
"""
from __future__ import annotations

_LEGAL_COMPLEX_MARKERS = (
    "sblc", "ucp 600", "isp98", "enforceability", "transferab", "indemnif",
    "arbitration", "governing law", "jurisdiction", "force majeure",
    "letter of credit", "guarantee", "amendment", "compliance", "sanctions",
)


def estimate_tokens(text: str) -> int:
    # ~4 chars/token heuristic; deterministic.
    return max(1, int(len(text or "") / 4))


def analyze_prompt(prompt: str, mode: str = "legal") -> dict:
    """Return {complexity, sla, preferred_providers, tokens, signals}."""
    text = (prompt or "")
    low = text.lower()
    tokens = estimate_tokens(text)
    legal_hits = sum(1 for m in _LEGAL_COMPLEX_MARKERS if m in low)
    multi_step = low.count("\n1.") + low.count("\n2.") + low.count("step ")
    latency_sensitive = mode in ("chat", "war_room")

    if mode == "legal" or legal_hits >= 1:
        complexity = "critical" if (legal_hits >= 4 or tokens > 1500) else "complex"
    elif tokens > 1200 or multi_step >= 3:
        complexity = "complex"
    elif tokens > 400:
        complexity = "medium"
    else:
        complexity = "simple"

    sla = {
        "critical": "high_quality",
        "complex": "high_quality",
        "medium": "balanced",
        "simple": "low_latency" if latency_sensitive else "balanced",
    }[complexity]

    # Provider affinity (advisory): quality-first workflows prefer codex/gemini.
    if sla == "high_quality":
        preferred = ["codex", "gemini", "xai", "nvidia"]
    elif sla == "low_latency":
        preferred = ["nvidia", "xai", "gemini", "codex"]
    else:
        preferred = ["codex", "gemini", "xai", "nvidia"]

    return {
        "mode": mode,
        "complexity": complexity,
        "sla": sla,
        "preferred_providers": preferred,
        "tokens": tokens,
        "signals": {
            "legal_marker_hits": legal_hits,
            "multi_step": multi_step,
            "latency_sensitive": latency_sensitive,
        },
    }
