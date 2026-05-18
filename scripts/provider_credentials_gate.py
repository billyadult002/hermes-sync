#!/usr/bin/env python3
"""Provider Credential Gate (L6).

Hard release gate: verifies that a REAL LLM provider call can be made before
any business-workflow completion (legal/trade-finance) is allowed to PASS.

This intentionally does NOT accept:
  - a present-but-unusable env key as success,
  - a fake/test key,
  - test mode,
  - a fallback / low-quality response as provider success.

Exit code 0 + {"PASS": true}  only when a live provider returns substantive
output. Otherwise exit code 1 + {"PASS": false, "blocked_reason": ...}.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from server_v2.providers import (  # noqa: E402
    api_key,
    env_value,
    is_low_quality,
    known_good_chat_path,
)

# Markers that prove the upstream provider has no real auth, even when the
# gateway key itself is accepted. These must NEVER count as PASS.
_UPSTREAM_AUTH_FAILURE_MARKERS = (
    "auth_unavailable",
    "no auth available",
    "no codex credentials",
    "run `hermes auth`",
    "run hermes auth",
    "invalid api key",
    "missing api key",
    "unauthorized",
    "credentials stored",
)

_PROBE_PROMPT = (
    "Provider credential gate probe. Reply with one substantive paragraph "
    "(at least 60 words) confirming you can perform legal trade-finance "
    "analysis, mentioning SBLC enforceability and UCP 600."
)


def main() -> int:
    missing: list[str] = []

    cliproxy_key = env_value("CLIPROXYAPI_API_KEY")
    bridge_key = api_key()  # API_SERVER_KEY / HERMES_API_KEY

    if not cliproxy_key:
        missing.append("CLIPROXYAPI_API_KEY")
    if not bridge_key:
        missing.append("API_SERVER_KEY")

    # Even when env keys are present, the gateway's upstream provider auth may
    # be absent. The only trustworthy signal is a real call.
    started = time.time()
    call = known_good_chat_path(_PROBE_PROMPT, task_id="provider-credentials-gate", total_timeout=60.0)
    elapsed_ms = int((time.time() - started) * 1000)

    trace = call.get("trace") if isinstance(call.get("trace"), list) else []
    trace_blob = json.dumps(trace, ensure_ascii=False).lower()
    upstream_auth_failed = any(m in trace_blob for m in _UPSTREAM_AUTH_FAILURE_MARKERS)

    output = str(call.get("output") or "")
    real_success = (
        bool(call.get("ok"))
        and not is_low_quality(output)
        and len(output.strip()) > 200
        and not upstream_auth_failed
    )

    if real_success:
        print(json.dumps({
            "PASS": True,
            "provider": call.get("provider"),
            "model": call.get("model"),
            "output_chars": len(output.strip()),
            "latency_ms": elapsed_ms,
        }, ensure_ascii=False))
        return 0

    if upstream_auth_failed and not missing:
        # Keys exist but the upstream LLM auth (e.g. Codex) is not stored.
        missing.append("UPSTREAM_PROVIDER_AUTH (run `hermes auth` / configure cliproxy codex)")

    if not missing:
        missing.append("USABLE_PROVIDER_CALL (no substantive live response)")

    print(json.dumps({
        "PASS": False,
        "blocked_reason": "missing_provider_credentials",
        "missing": missing,
        "provider_call_ok": bool(call.get("ok")),
        "provider_error": call.get("error", ""),
        "upstream_auth_failed": upstream_auth_failed,
        "latency_ms": elapsed_ms,
        "trace": trace[-6:],
    }, ensure_ascii=False))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
