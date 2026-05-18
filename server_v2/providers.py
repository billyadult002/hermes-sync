"""AI provider calls — extracted from app_server.py.

Implements known_good_chat_path and safe_provider_call using httpx streaming
against the same cliproxy (8317) and hermes-bridge (8642) endpoints.
"""
from __future__ import annotations

import json
import os
import re
import time
from pathlib import Path

import httpx

from .config import (
    CHATGPT_FALLBACK_MODEL,
    CHATGPT_TARGET_MODEL,
    CLIPROXY_API,
    HERMES_API,
    HERMES_HOME,
    MAX_PROVIDER_ATTEMPTS,
    MAX_PROVIDER_TOTAL_SECONDS,
    MAX_SINGLE_PROVIDER_SECONDS,
)

_ENV_PATH = HERMES_HOME / ".env"

# ---------------------------------------------------------------------------
# Env helpers
# ---------------------------------------------------------------------------

def env_value(*keys: str) -> str:
    for key in keys:
        value = os.environ.get(key, "")
        if value:
            return value
    if not _ENV_PATH.exists():
        return ""
    values: dict[str, str] = {}
    for line in _ENV_PATH.read_text(encoding="utf-8").splitlines():
        if "=" not in line or line.lstrip().startswith("#"):
            continue
        k, v = line.split("=", 1)
        values[k.strip()] = v.strip().strip('"').strip("'")
    for key in keys:
        value = values.get(key, "")
        if value:
            return value
    return ""


def api_key() -> str:
    return env_value("API_SERVER_KEY", "HERMES_API_KEY")


# ---------------------------------------------------------------------------
# Output quality helpers
# ---------------------------------------------------------------------------

_FALLBACK_MARKERS = frozenset({
    "工作流启动失败",
    "系统繁忙",
    "兜底回复",
    "fallback response generated",
    "no substantive content",
    "step failed:",
    "step fallback:",
    "⚠️",
})

_FAILURE_MARKERS = frozenset({
    "provider_failed",
    "legal_provider_failed",
    "auth_failed",
    "no_valid_provider",
})


def is_low_quality(text: str | None) -> bool:
    if not text:
        return True
    value = str(text).strip()
    if len(value) < 30:
        return True
    lower = value.lower()
    if "sorry" in lower:
        return True
    for marker in _FALLBACK_MARKERS:
        if marker.lower() in lower:
            return True
    return False


def classify_result(text: str | None) -> str:
    if not text:
        return "empty"
    value = str(text).strip()
    for marker in _FALLBACK_MARKERS:
        if marker.lower() in value.lower():
            return "fallback"
    if len(value) < 40:
        return "low_quality"
    if is_low_quality(value):
        return "degraded"
    return "success"


def is_provider_failure(output: str | None) -> bool:
    if not output:
        return True
    lower = str(output).lower()
    for marker in _FAILURE_MARKERS:
        if marker in lower:
            return True
    return False


# ---------------------------------------------------------------------------
# SSE streaming parser
# ---------------------------------------------------------------------------

def _content_text(content: object) -> str:
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                if isinstance(item.get("text"), str):
                    parts.append(item["text"])
                elif isinstance(item.get("content"), str):
                    parts.append(item["content"])
        return "".join(parts)
    if isinstance(content, dict):
        for key in ("text", "content", "output_text"):
            value = content.get(key)
            if isinstance(value, str):
                return value
    return str(content)


def _error_text(body: bytes) -> str:
    text = body.decode("utf-8", errors="ignore").strip()
    if not text:
        return ""
    try:
        payload = json.loads(text)
    except Exception:
        return text
    if isinstance(payload, dict):
        error = payload.get("error")
        if isinstance(error, dict):
            message = error.get("message")
            if isinstance(message, str):
                return message
        if isinstance(error, str):
            return error
        message = payload.get("message")
        if isinstance(message, str):
            return message
    return text


def _stream_chat_completion(url: str, headers: dict, payload: dict, timeout: float) -> tuple[str, str]:
    """Stream a chat completion SSE response, return (content, reasoning)."""
    content_parts: list[str] = []
    reasoning_parts: list[str] = []
    with httpx.stream("POST", url, headers=headers, json=payload, timeout=timeout) as resp:
        if not resp.is_success:
            try:
                raw_error = resp.read().decode("utf-8", errors="ignore")
            except Exception:
                raw_error = f"HTTP {resp.status_code}"
            raise RuntimeError(_error_text(raw_error.encode("utf-8")) or f"HTTP {resp.status_code}")
        buffer = ""
        for chunk in resp.iter_text():
            if not chunk:
                continue
            buffer += chunk
            while "\n\n" in buffer:
                block, buffer = buffer.split("\n\n", 1)
                for line in block.splitlines():
                    if not line.strip().startswith("data:"):
                        continue
                    raw = line.split("data:", 1)[1].strip()
                    if not raw or raw == "[DONE]":
                        continue
                    try:
                        parsed = json.loads(raw)
                    except Exception:
                        continue
                    choices = parsed.get("choices") if isinstance(parsed.get("choices"), list) else [{}]
                    choice = choices[0] if choices else {}
                    delta = choice.get("delta") if isinstance(choice, dict) else {}
                    if isinstance(delta, dict):
                        content = _content_text(delta.get("content"))
                        if content:
                            content_parts.append(content)
                        reasoning = _content_text(delta.get("reasoning_content"))
                        if reasoning:
                            reasoning_parts.append(reasoning)
    return "".join(content_parts).strip(), "".join(reasoning_parts).strip()


def _masked_credential(value: str) -> str:
    text = str(value or "")
    if not text:
        return ""
    return text[:6] if len(text) <= 8 else f"{text[:4]}...{text[-2:]}"


# ---------------------------------------------------------------------------
# Deterministic provider chain: Codex -> Gemini -> xAI -> NVIDIA
# (server_v2 owns the cross-provider fallback decision; cliproxy is only the
#  transport for codex/gemini/xai accounts. NOT round-robin across providers.)
# ---------------------------------------------------------------------------

MAX_ATTEMPTS_PER_PROVIDER = int(env_value("HERMES_MAX_ATTEMPTS_PER_PROVIDER") or "3")

# Models are env-overridable; defaults are real, currently-available models.
PROVIDER_CHAIN: list[dict] = [
    {"provider": "codex",  "model": env_value("HERMES_CHAIN_CODEX_MODEL")  or CHATGPT_TARGET_MODEL, "transport": "cliproxy"},
    {"provider": "gemini", "model": env_value("HERMES_CHAIN_GEMINI_MODEL") or "gemini-2.5-pro",     "transport": "cliproxy"},
    {"provider": "xai",    "model": env_value("HERMES_CHAIN_XAI_MODEL")    or "grok-4.3",            "transport": "cliproxy"},
    {"provider": "nvidia", "model": env_value("HERMES_CHAIN_NVIDIA_MODEL") or "minimaxai/minimax-m2.7", "transport": "nvidia"},
]

_AUTH_ERROR_MARKERS = (
    "auth_unavailable", "no auth available", "401", "unauthorized", "token expired",
    "deauthorized", "no codex credentials", "sign in again", "invalid api key",
    "missing api key", "authentication", "credentials stored",
)
_QUOTA_ERROR_MARKERS = (
    "quota exceeded", "quota_exceeded", "rate limit", "rate_limit", "429",
    "insufficient_quota", "resource_exhausted", "exhausted", "too many requests",
    "usage limit", "cooling down", "all credentials", "credentials for model",
    "limit has been reached",
)
_TIMEOUT_MARKERS = ("timeout", "timed out", "deadline", "readtimeout", "connecttimeout")


def is_auth_error(message: str | None) -> bool:
    low = str(message or "").lower()
    return any(m in low for m in _AUTH_ERROR_MARKERS)


def is_quota_error(message: str | None) -> bool:
    low = str(message or "").lower()
    return any(m in low for m in _QUOTA_ERROR_MARKERS)


def is_timeout_error(message: str | None) -> bool:
    low = str(message or "").lower()
    return any(m in low for m in _TIMEOUT_MARKERS)


def is_substantive(text: str | None) -> bool:
    if is_low_quality(text) or is_provider_failure(text):
        return False
    return classify_result(text) == "success"


def _call_provider(step: dict, prompt: str, single_timeout: float) -> dict:
    """Exactly ONE provider attempt. Returns {ok, output, error, latency_ms}."""
    transport = step["transport"]
    model = step["model"]
    messages = [{"role": "user", "content": prompt}]
    if transport == "cliproxy":
        key = env_value("CLIPROXYAPI_API_KEY")
        if not key:
            return {"ok": False, "output": "", "error": "cliproxy_key_missing", "latency_ms": 0}
        url = f"{CLIPROXY_API}/chat/completions"
        headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
        payload = {"model": model, "stream": True, "messages": messages, "agent": "auto"}
    elif transport == "nvidia":
        key = env_value("NVIDIA_API_KEY")
        if not key:
            return {"ok": False, "output": "", "error": "nvidia_key_missing", "latency_ms": 0}
        base = (env_value("NVIDIA_BASE_URL") or "https://integrate.api.nvidia.com/v1").rstrip("/")
        url = f"{base}/chat/completions"
        headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
        payload = {"model": model, "stream": True, "messages": messages}
    else:
        return {"ok": False, "output": "", "error": f"unknown_transport:{transport}", "latency_ms": 0}

    started = time.time()
    try:
        output, reasoning = _stream_chat_completion(url, headers, payload, timeout=single_timeout)
        return {
            "ok": True, "output": output, "error": "",
            "latency_ms": int((time.time() - started) * 1000),
            "reasoning_chars": len(reasoning),
        }
    except Exception as exc:
        return {
            "ok": False, "output": "", "error": str(exc)[:500],
            "latency_ms": int((time.time() - started) * 1000),
        }


def run_provider_chain(prompt: str, *, task_id: str = "", total_timeout: float = 90.0,
                        mode: str = "legal") -> dict:
    """Deterministic Codex -> Gemini -> xAI -> NVIDIA execution.

    Within each provider, attempts are serial (fill-first / cliproxy rotation
    supplies the next account). Switch provider on auth/quota errors or two
    consecutive empties; retry same provider on transient timeout.

    L7 intelligence is layered on as SHADOW by default: metrics/state are
    recorded passively; ordering/circuit-breaker only alter execution when
    the corresponding feature flag is explicitly enabled. With default flags
    the execution order is exactly PROVIDER_CHAIN (L6 baseline preserved).
    """
    try:
        from . import provider_intelligence as _pi
        _pi.ensure_data_files()
        flags = _pi.feature_flags()
        rec_order = _pi.recommended_order(PROVIDER_CHAIN)
        wf_rec = _pi.workflow_recommendation(mode)
    except Exception:
        _pi = None
        flags = {}
        rec_order = list(PROVIDER_CHAIN)
        wf_rec = {"mode": mode, "profile": "balanced", "sla": "balanced"}

    use_dynamic = bool(flags.get("ENABLE_DYNAMIC_PROVIDER_ORDERING"))
    enforce_breaker = bool(flags.get("ENABLE_CIRCUIT_BREAKER_ENFORCEMENT"))
    exec_chain = rec_order if use_dynamic else list(PROVIDER_CHAIN)

    # Circuit-breaker enforcement (flag-gated). Safety: never skip ALL providers.
    if _pi is not None and enforce_breaker:
        live = [s for s in exec_chain if not _pi.is_cooled_down(s["provider"])]
        if live:
            exec_chain = live

    started = time.time()
    attempts: list[dict] = []
    chain_ids = [f'{s["provider"]}:{s["model"]}' for s in PROVIDER_CHAIN]
    rec_ids = [f'{s["provider"]}:{s["model"]}' for s in rec_order]
    actual_ids = [f'{s["provider"]}:{s["model"]}' for s in exec_chain]

    def _pexec(selected: dict | None) -> dict:
        pe = {
            "chain": chain_ids,
            "recommended_order": rec_ids,
            "actual_order": actual_ids,
            "attempts": attempts,
            "selected": selected,
            "selected_provider": selected["provider"] if selected else None,
            "selected_model": selected["model"] if selected else None,
            "workflow_recommendation": wf_rec,
            "flags": flags,
            "total_latency_ms": sum(int(a.get("latency_ms") or 0) for a in attempts),
        }
        try:
            if _pi is not None:
                pe["provider_state"] = _pi.provider_state()
        except Exception:
            pass
        return pe

    def _log(entry: dict) -> None:
        try:
            if _pi is not None:
                _pi.record_attempt(entry["provider"], entry.get("status", ""),
                                   int(entry.get("latency_ms") or 0), str(entry.get("error") or ""))
        except Exception:
            pass
        attempts.append(entry)

    for step in exec_chain:
        provider, model = step["provider"], step["model"]
        empty_streak = 0
        n = 0
        while n < MAX_ATTEMPTS_PER_PROVIDER:
            n += 1
            remaining = total_timeout - (time.time() - started)
            if remaining <= 2:
                _log({"provider": provider, "model": model, "transport": step["transport"],
                      "attempt": n, "status": "chain_timeout", "latency_ms": 0,
                      "error": "provider_chain_total_timeout"})
                return {"ok": False, "error": "provider_chain_timeout", "trace": attempts,
                        "provider_execution": _pexec(None)}
            single = max(15.0, min(55.0, remaining))
            r = _call_provider(step, prompt, single)
            entry = {"provider": provider, "model": model, "transport": step["transport"],
                     "attempt": n, "latency_ms": r["latency_ms"]}

            if r["ok"] and is_substantive(r["output"]):
                entry["status"] = "success"
                _log(entry)
                return {"ok": True, "output": r["output"], "provider": provider, "model": model,
                        "trace": attempts,
                        "provider_execution": _pexec({"provider": provider, "model": model})}

            err = r.get("error") or ("empty_or_non_substantive_result" if r["ok"] else "unknown_error")
            entry["error"] = str(err)[:300]

            if not r["ok"] and is_auth_error(err):
                entry["status"] = "auth_error"
                _log(entry)
                break  # switch provider immediately
            if not r["ok"] and is_quota_error(err):
                entry["status"] = "quota_error"
                _log(entry)
                break  # switch provider immediately
            if not r["ok"] and is_timeout_error(err):
                entry["status"] = "timeout"
                _log(entry)
                continue  # transient: retry SAME provider

            # empty / low-quality / other non-auth error
            entry["status"] = "empty" if r["ok"] else "error"
            _log(entry)
            if r["ok"]:
                empty_streak += 1
                if empty_streak >= 2:
                    break  # two consecutive empties -> switch provider
            # otherwise retry same provider until MAX_ATTEMPTS_PER_PROVIDER

    return {"ok": False, "error": "provider_chain_failed", "trace": attempts,
            "provider_execution": _pexec(None)}


def known_good_chat_path(prompt: str, *, task_id: str = "", total_timeout: float = 60.0) -> dict:
    """Deterministic provider-chain entry point (contract-compatible).

    Returns {"ok": True, "output", "provider", "model", "trace"(list)}
    or       {"ok": False, "error", "trace"(list)}.
    """
    return run_provider_chain(prompt, task_id=task_id, total_timeout=total_timeout)


# ---------------------------------------------------------------------------
# Quality scoring
# ---------------------------------------------------------------------------

def compute_quality_score(text: str | None, steps: list[dict] | None = None) -> int:
    if not text:
        return 0
    value = str(text).strip()
    score = 0
    if len(value) > 200:
        score += 40
    if len(value) > 1000:
        score += 20
    if len(value) > 5000:
        score += 10
    done_steps = sum(1 for s in (steps or []) if isinstance(s, dict) and s.get("status") == "done")
    score += done_steps * 10
    for heading in ("Executive", "Analysis", "Review", "Recommendation", "Decision"):
        if heading.lower() in value.lower():
            score += 5
    return min(score, 100)


def generate_decision(result: dict) -> dict:
    score = int(result.get("quality_score") or 0)
    if score >= 70:
        verdict = "approve"
    elif score >= 40:
        verdict = "review"
    else:
        verdict = "reject"
    return {
        "verdict": verdict,
        "quality_score": score,
        "reasoning": f"Quality score {score}/100 — {'substantive output' if score >= 40 else 'insufficient content'}",
        "generated_at": time.time(),
    }
