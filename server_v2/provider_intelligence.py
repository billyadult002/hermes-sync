"""L7 Provider Intelligence Platform — metrics, scoring, state, circuit breaker.

Design invariants (CRITICAL — must never break the L6 baseline):
  * Every public function is crash-safe: any I/O / parse error is swallowed and
    a safe default returned. Intelligence must NEVER raise into the workflow.
  * Recording (metrics/state) is ACTIVE but PASSIVE — it never alters routing.
  * Ordering / workflow-routing / SLA / circuit-breaker ENFORCEMENT is gated by
    feature flags that default to OFF, so run_provider_chain behaves exactly as
    the L6 deterministic chain unless an operator explicitly activates a flag.
  * JSON files are atomic-write, size-capped, and auto-recover on corruption.
"""
from __future__ import annotations

import json
import os
import tempfile
import time
from pathlib import Path

from .config import ROOT

_DATA = ROOT / "data"
METRICS_PATH = _DATA / "provider_metrics.json"
STATE_PATH = _DATA / "provider_state.json"
FLAGS_PATH = _DATA / "provider_feature_flags.json"

_PROVIDERS = ("codex", "gemini", "xai", "nvidia")

_CIRCUIT_FAILURE_THRESHOLD = 5
_COOLDOWN_SECONDS = int(os.getenv("HERMES_PROVIDER_COOLDOWN_S", "600"))  # 10 min
_MAX_FILE_BYTES = 256 * 1024

_DEFAULT_FLAGS = {
    "ENABLE_DYNAMIC_PROVIDER_ORDERING": False,
    "ENABLE_WORKFLOW_AWARE_ROUTING": False,
    "ENABLE_SLA_ROUTING": False,
    "ENABLE_CIRCUIT_BREAKER_ENFORCEMENT": False,
}

# --- L8 ---
L8_FLAGS_PATH = _DATA / "l8_feature_flags.json"
EXEC_MEMORY_PATH = _DATA / "execution_memory.jsonl"
LEARNING_REPORT_PATH = _DATA / "runtime_learning_report.json"
_EXEC_MEMORY_MAX_LINES = 2000

_DEFAULT_L8_FLAGS = {
    "ENABLE_ADAPTIVE_ROUTING": False,
    "ENABLE_POLICY_ROUTING": False,
    "ENABLE_MULTI_AGENT": False,
    "ENABLE_SELF_HEALING_RECOVERY": True,
}


def _blank_metric() -> dict:
    return {
        "success_count": 0, "failure_count": 0, "timeout_count": 0,
        "quota_error_count": 0, "auth_error_count": 0,
        "avg_latency_ms": 0, "success_rate": 0.0,
        "last_success_ts": None, "last_failure_ts": None,
    }


def _blank_state() -> dict:
    return {"status": "healthy", "consecutive_failures": 0,
            "cooldown_until": None, "last_failure_reason": None}


def _load(path: Path, default_factory) -> dict:
    try:
        if not path.exists() or path.stat().st_size > _MAX_FILE_BYTES:
            return {p: default_factory() for p in _PROVIDERS}
        data = json.loads(path.read_text(encoding="utf-8") or "{}")
        if not isinstance(data, dict):
            raise ValueError("not a dict")
        for p in _PROVIDERS:
            if not isinstance(data.get(p), dict):
                data[p] = default_factory()
        return data
    except Exception:
        # Corruption auto-recover: reset to safe defaults.
        return {p: default_factory() for p in _PROVIDERS}


def _atomic_write(path: Path, payload: dict) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=".pi_", suffix=".tmp")
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False)
        os.replace(tmp, path)
    except Exception:
        pass  # never raise into workflow


def feature_flags() -> dict:
    try:
        if FLAGS_PATH.exists():
            data = json.loads(FLAGS_PATH.read_text(encoding="utf-8") or "{}")
            if isinstance(data, dict):
                return {**_DEFAULT_FLAGS, **{k: bool(v) for k, v in data.items() if k in _DEFAULT_FLAGS}}
    except Exception:
        pass
    return dict(_DEFAULT_FLAGS)


def ensure_data_files() -> None:
    """Idempotently materialize the three data files with safe defaults."""
    try:
        if not METRICS_PATH.exists():
            _atomic_write(METRICS_PATH, {p: _blank_metric() for p in _PROVIDERS})
        if not STATE_PATH.exists():
            _atomic_write(STATE_PATH, {p: _blank_state() for p in _PROVIDERS})
        if not FLAGS_PATH.exists():
            _atomic_write(FLAGS_PATH, dict(_DEFAULT_FLAGS))
        if not L8_FLAGS_PATH.exists():
            _atomic_write(L8_FLAGS_PATH, dict(_DEFAULT_L8_FLAGS))
    except Exception:
        pass


def l8_feature_flags() -> dict:
    try:
        if L8_FLAGS_PATH.exists():
            data = json.loads(L8_FLAGS_PATH.read_text(encoding="utf-8") or "{}")
            if isinstance(data, dict):
                return {**_DEFAULT_L8_FLAGS,
                        **{k: bool(v) for k, v in data.items() if k in _DEFAULT_L8_FLAGS}}
    except Exception:
        pass
    return dict(_DEFAULT_L8_FLAGS)


def record_execution_memory(entry: dict) -> None:
    """Append one workflow execution record (capped, crash-safe)."""
    try:
        EXEC_MEMORY_PATH.parent.mkdir(parents=True, exist_ok=True)
        line = json.dumps(entry, ensure_ascii=False)
        with EXEC_MEMORY_PATH.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")
        # Cap: keep last N lines.
        if EXEC_MEMORY_PATH.stat().st_size > _MAX_FILE_BYTES * 4:
            lines = EXEC_MEMORY_PATH.read_text(encoding="utf-8").splitlines()[-_EXEC_MEMORY_MAX_LINES:]
            tmp = EXEC_MEMORY_PATH.with_suffix(".tmp")
            tmp.write_text("\n".join(lines) + "\n", encoding="utf-8")
            os.replace(tmp, EXEC_MEMORY_PATH)
    except Exception:
        pass


def read_execution_memory(limit: int = 200) -> list[dict]:
    try:
        if not EXEC_MEMORY_PATH.exists():
            return []
        out = []
        for ln in EXEC_MEMORY_PATH.read_text(encoding="utf-8").splitlines()[-limit:]:
            try:
                out.append(json.loads(ln))
            except Exception:
                continue
        return out
    except Exception:
        return []


def build_learning_report() -> dict:
    """Analyze execution memory: best chain, best provider per workflow."""
    try:
        mem = read_execution_memory(limit=_EXEC_MEMORY_MAX_LINES)
        by_provider: dict = {}
        by_mode: dict = {}
        for r in mem:
            p = r.get("selected_provider")
            mode = r.get("mode") or "unknown"
            ok = bool(r.get("success"))
            if p:
                d = by_provider.setdefault(p, {"runs": 0, "success": 0, "latency_sum": 0})
                d["runs"] += 1
                d["success"] += 1 if ok else 0
                d["latency_sum"] += int(r.get("latency_ms") or 0)
            md = by_mode.setdefault(mode, {"runs": 0, "success": 0})
            md["runs"] += 1
            md["success"] += 1 if ok else 0
        for p, d in by_provider.items():
            d["success_rate"] = round(d["success"] / d["runs"], 4) if d["runs"] else 0.0
            d["avg_latency_ms"] = int(d["latency_sum"] / d["runs"]) if d["runs"] else 0
        best_provider = max(by_provider.items(),
                            key=lambda kv: (kv[1]["success_rate"], -kv[1]["avg_latency_ms"]),
                            default=(None, {}))[0]
        report = {
            "ok": True,
            "total_records": len(mem),
            "by_provider": by_provider,
            "by_mode": by_mode,
            "most_stable_provider": best_provider,
            "generated_at": time.time(),
        }
        _atomic_write(LEARNING_REPORT_PATH, report)
        return report
    except Exception as exc:
        return {"ok": False, "error": str(exc)[:160], "total_records": 0}


def score_provider_l8(provider: str, mode: str = "legal") -> float:
    """L8 weighted score: quality·0.35 + success·0.25 + latency·0.15
    + cost_efficiency·0.15 + reliability·0.10. Deterministic; never raises."""
    try:
        m = (_load(METRICS_PATH, _blank_metric)).get(provider) or _blank_metric()
        s = provider_state(provider)
        total = m.get("success_count", 0) + m.get("failure_count", 0)
        success_rate = float(m.get("success_rate") or (0.6 if total == 0 else 0.0))
        cq = m.get("completion_quality") if isinstance(m.get("completion_quality"), dict) else {}
        quality = float(cq.get(mode, m.get("quality_score", 0.85)) if total else 0.85)
        avg = float(m.get("avg_latency_ms") or 0)
        latency_score = 1.0 if avg <= 0 else max(0.0, min(1.0, 1.0 - avg / 120000.0))
        cost = float(m.get("cost_efficiency", 0.8))
        reliability = 1.0 if total == 0 else max(0.0, 1.0 - m.get("failure_count", 0) / max(1, total))
        recent = min(1.0, int(s.get("consecutive_failures") or 0) / 5.0)
        score = (quality * 0.35 + success_rate * 0.25 + latency_score * 0.15
                 + cost * 0.15 + reliability * 0.10) - recent * 0.05
        return round(max(0.0, min(1.0, score)), 4)
    except Exception:
        return 0.5


def adaptive_order(chain: list[dict], mode: str = "legal") -> list[dict]:
    """L8 adaptive ordering — score-sorted, deterministic, stable, lossless.
    Never mutates input; pure recommendation."""
    try:
        return sorted(chain, key=lambda step: (-score_provider_l8(step["provider"], mode),
                                               step["provider"]))
    except Exception:
        return list(chain)


def _classify(status: str, error: str) -> str:
    e = (error or "").lower()
    if status == "success":
        return "success"
    if status == "auth_error" or "auth" in e or "401" in e or "unauthorized" in e:
        return "auth_error"
    if status == "quota_error" or "quota" in e or "rate limit" in e or "cooling down" in e or "usage limit" in e:
        return "quota_error"
    if status == "timeout" or "timeout" in e or "timed out" in e:
        return "timeout"
    return "failure"


def record_attempt(provider: str, status: str, latency_ms: int, error: str = "") -> None:
    """Update metrics + state for one provider attempt. Never raises."""
    try:
        if provider not in _PROVIDERS:
            return
        now = time.time()
        kind = _classify(status, error)

        metrics = _load(METRICS_PATH, _blank_metric)
        m = metrics.get(provider) or _blank_metric()
        if kind == "success":
            m["success_count"] += 1
            m["last_success_ts"] = now
            prev_n = max(0, m["success_count"] - 1)
            m["avg_latency_ms"] = int((m["avg_latency_ms"] * prev_n + latency_ms) / max(1, m["success_count"]))
        else:
            m["failure_count"] += 1
            m["last_failure_ts"] = now
            if kind == "timeout":
                m["timeout_count"] += 1
            elif kind == "quota_error":
                m["quota_error_count"] += 1
            elif kind == "auth_error":
                m["auth_error_count"] += 1
        total = m["success_count"] + m["failure_count"]
        m["success_rate"] = round(m["success_count"] / total, 4) if total else 0.0
        metrics[provider] = m
        _atomic_write(METRICS_PATH, metrics)

        state = _load(STATE_PATH, _blank_state)
        s = state.get(provider) or _blank_state()
        if kind == "success":
            s["status"] = "healthy"
            s["consecutive_failures"] = 0
            s["cooldown_until"] = None
            s["last_failure_reason"] = None
        else:
            s["consecutive_failures"] += 1
            s["last_failure_reason"] = kind
            if s["consecutive_failures"] >= _CIRCUIT_FAILURE_THRESHOLD:
                s["status"] = "cooldown"
                s["cooldown_until"] = now + _COOLDOWN_SECONDS
            else:
                s["status"] = "degraded"
        state[provider] = s
        _atomic_write(STATE_PATH, state)
    except Exception:
        pass


def provider_state(provider: str | None = None) -> dict:
    state = _load(STATE_PATH, _blank_state)
    now = time.time()
    for p in _PROVIDERS:
        s = state.get(p) or _blank_state()
        cu = s.get("cooldown_until")
        if s.get("status") == "cooldown" and cu and now >= cu:
            # Cooldown elapsed -> allow a single recovery probe (degraded).
            s["status"] = "degraded"
            s["cooldown_until"] = None
            state[p] = s
    if provider:
        return state.get(provider) or _blank_state()
    return state


def is_cooled_down(provider: str) -> bool:
    s = provider_state(provider)
    cu = s.get("cooldown_until")
    return s.get("status") == "cooldown" and bool(cu) and time.time() < float(cu)


def score_provider(provider: str) -> float:
    """Deterministic score in [0,1]. Exceptions -> neutral 0.5 (never raises)."""
    try:
        m = (_load(METRICS_PATH, _blank_metric)).get(provider) or _blank_metric()
        s = provider_state(provider)
        success_rate = float(m.get("success_rate") or 0.0)
        total = m.get("success_count", 0) + m.get("failure_count", 0)
        reliability = 1.0 if total == 0 else max(0.0, 1.0 - m.get("failure_count", 0) / max(1, total))
        avg = float(m.get("avg_latency_ms") or 0)
        latency_score = 1.0 if avg <= 0 else max(0.0, min(1.0, 1.0 - (avg / 120000.0)))
        recent_failures = min(1.0, int(s.get("consecutive_failures") or 0) / 5.0)
        if total == 0:
            success_rate = 0.6  # unproven providers get a neutral-positive prior
        score = success_rate * 0.4 + reliability * 0.3 + latency_score * 0.2 - recent_failures * 0.1
        return round(max(0.0, min(1.0, score)), 4)
    except Exception:
        return 0.5


def recommended_order(chain: list[dict]) -> list[dict]:
    """Score-sorted chain (stable). Pure; never mutates the input chain."""
    try:
        return sorted(chain, key=lambda step: -score_provider(step["provider"]))
    except Exception:
        return list(chain)


_WORKFLOW_PROFILE = {
    "legal": "quality-first",
    "chat": "latency-first",
    "war_room": "low-latency-first",
}


def workflow_recommendation(mode: str) -> dict:
    profile = _WORKFLOW_PROFILE.get((mode or "").lower(), "balanced")
    sla = {"quality-first": "high_quality", "latency-first": "low_latency",
           "low-latency-first": "low_latency"}.get(profile, "balanced")
    return {"mode": mode, "profile": profile, "sla": sla}


def provider_scoreboard() -> dict:
    """Observability snapshot for API/UI. Never raises."""
    try:
        metrics = _load(METRICS_PATH, _blank_metric)
        state = provider_state()
        out = {}
        for p in _PROVIDERS:
            m = metrics.get(p) or _blank_metric()
            s = state.get(p) or _blank_state()
            out[p] = {
                "score": score_provider(p),
                "status": s.get("status"),
                "success_rate": m.get("success_rate"),
                "avg_latency_ms": m.get("avg_latency_ms"),
                "success_count": m.get("success_count"),
                "failure_count": m.get("failure_count"),
                "consecutive_failures": s.get("consecutive_failures"),
                "cooldown_until": s.get("cooldown_until"),
                "last_failure_reason": s.get("last_failure_reason"),
            }
        return {"ok": True, "providers": out, "flags": feature_flags()}
    except Exception:
        return {"ok": False, "providers": {}, "flags": dict(_DEFAULT_FLAGS)}
