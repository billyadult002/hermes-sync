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
# Primary provider path
# ---------------------------------------------------------------------------

def known_good_chat_path(
    prompt: str,
    *,
    task_id: str = "",
    total_timeout: float = 60.0,
) -> dict:
    """Try cliproxy first, fall back to hermes-bridge.

    Returns {"ok": True, "output": str, "provider": str, "model": str, "trace": list}
    or       {"ok": False, "error": str, "trace": list}.
    """
    started_at = time.time()
    trace: list[dict] = []
    messages = [{"role": "user", "content": prompt}]

    # --- Path 1: cliproxy direct
    cliproxy_key = env_value("CLIPROXYAPI_API_KEY")
    if cliproxy_key:
        attempt_started = time.time()
        provider = "chatgpt"
        model = CHATGPT_TARGET_MODEL
        try:
            output, reasoning = _stream_chat_completion(
                f"{CLIPROXY_API}/chat/completions",
                {"Authorization": f"Bearer {cliproxy_key}", "Content-Type": "application/json"},
                {"model": model, "stream": True, "messages": messages, "agent": "auto"},
                timeout=max(10.0, total_timeout - (time.time() - started_at)),
            )
            latency = int((time.time() - attempt_started) * 1000)
            trace.append({
                "provider": provider,
                "model": model,
                "auth": "cliproxy",
                "status": "success" if not is_low_quality(output) else "low_quality",
                "latency": latency,
                "error": "" if not is_low_quality(output) else "empty_or_non_substantive_result",
                "reasoning_chars": len(reasoning),
            })
            if not is_low_quality(output):
                return {"ok": True, "output": output, "provider": provider, "model": model, "trace": trace}
        except Exception as exc:
            trace.append({
                "provider": provider,
                "model": model,
                "auth": "cliproxy",
                "status": "timeout" if "timeout" in str(exc).lower() else "failed",
                "latency": int((time.time() - attempt_started) * 1000),
                "error": str(exc)[:500],
            })

    # --- Path 2: hermes bridge (up to 3 attempts)
    remaining = max(1.0, total_timeout - (time.time() - started_at))
    if remaining > 5:
        bearer = api_key()
        headers: dict[str, str] = {"Content-Type": "application/json"}
        if bearer:
            headers["Authorization"] = f"Bearer {bearer}"
        for _attempt in range(min(3, MAX_PROVIDER_ATTEMPTS)):
            if time.time() - started_at >= total_timeout:
                break
            attempt_started = time.time()
            try:
                output, reasoning = _stream_chat_completion(
                    f"{HERMES_API}/chat/completions",
                    headers,
                    {"model": "hermes-agent", "stream": True, "messages": messages, "agent": "auto"},
                    timeout=max(5.0, min(MAX_SINGLE_PROVIDER_SECONDS, total_timeout - (time.time() - started_at))),
                )
                latency = int((time.time() - attempt_started) * 1000)
                trace.append({
                    "provider": "chatgpt",
                    "model": CHATGPT_TARGET_MODEL,
                    "auth": "hermes-bridge",
                    "status": "success" if not is_low_quality(output) else "low_quality",
                    "latency": latency,
                    "error": "" if not is_low_quality(output) else "empty_or_non_substantive_result",
                    "reasoning_chars": len(reasoning),
                })
                if not is_low_quality(output):
                    return {"ok": True, "output": output, "provider": "chatgpt", "model": CHATGPT_TARGET_MODEL, "trace": trace}
            except Exception as exc:
                trace.append({
                    "provider": "chatgpt",
                    "model": CHATGPT_TARGET_MODEL,
                    "auth": "hermes-bridge",
                    "status": "timeout" if "timeout" in str(exc).lower() else "failed",
                    "latency": int((time.time() - attempt_started) * 1000),
                    "error": str(exc)[:500],
                })

    return {"ok": False, "error": "legal_provider_failed", "trace": trace}


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
