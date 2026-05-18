#!/usr/bin/env python3
from __future__ import annotations

import argparse
import http.cookiejar
import json
import os
import sys
import time
import urllib.error
import urllib.request

# /api/orchestrate and /api/runtime/task require auth. Use a real login (same
# mechanism as workbench_health_gate.py) so the L6 check exercises the genuine
# authenticated workflow path. The workflow RESULT is never faked.
_BROWSER_SESSION = f"runtime-e2e-{int(time.time())}"
_OPENER: urllib.request.OpenerDirector | None = None


def _auth_headers() -> dict:
    return {"X-Hermes-Browser-Session": _BROWSER_SESSION}


def authenticate(base_url: str) -> tuple[bool, dict]:
    """Real login; binds a session cookie into the module opener."""
    global _OPENER
    email = os.getenv("HERMES_HEALTH_EMAIL", "bill@fastonegroup.com")
    password = os.getenv("HERMES_HEALTH_PASSWORD", "")
    if not password:
        return False, {"error": "missing HERMES_HEALTH_PASSWORD"}
    jar = http.cookiejar.CookieJar()
    _OPENER = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    raw = json.dumps({"email": email, "password": password}).encode("utf-8")
    req = urllib.request.Request(
        f"{base_url.rstrip('/')}/api/auth/login",
        data=raw,
        headers={"Content-Type": "application/json", **_auth_headers()},
        method="POST",
    )
    try:
        with _OPENER.open(req, timeout=15) as resp:
            body = json.loads(resp.read().decode("utf-8") or "{}")
            return resp.status == 200 and bool(body.get("authenticated")), body
    except urllib.error.HTTPError as exc:
        return False, {"status": exc.code, "raw": exc.read().decode("utf-8", "ignore")[:300]}


def _open(req: urllib.request.Request, timeout: int):
    opener = _OPENER or urllib.request
    return opener.open(req, timeout=timeout)


def post_json(base_url: str, path: str, payload: dict, timeout: int = 15) -> tuple[int, dict]:
    raw = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{base_url.rstrip('/')}{path}",
        data=raw,
        headers={"Content-Type": "application/json", **_auth_headers()},
        method="POST",
    )
    try:
        with _open(req, timeout) as resp:
            return int(resp.status), json.loads(resp.read().decode("utf-8") or "{}")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="ignore")
        try:
            payload = json.loads(body or "{}")
        except Exception:
            payload = {"raw": body}
        return int(exc.code), payload


def get_json(base_url: str, path: str, timeout: int = 10) -> tuple[int, dict]:
    req = urllib.request.Request(
        f"{base_url.rstrip('/')}{path}",
        headers=_auth_headers(),
        method="GET",
    )
    try:
        with _open(req, timeout) as resp:
            return int(resp.status), json.loads(resp.read().decode("utf-8") or "{}")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="ignore")
        try:
            payload = json.loads(body or "{}")
        except Exception:
            payload = {"raw": body}
        return int(exc.code), payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default=os.getenv("HERMES_RUNTIME_E2E_BASE_URL", "http://127.0.0.1:8765"))
    parser.add_argument("--timeout", type=int, default=int(os.getenv("HERMES_RUNTIME_E2E_TIMEOUT", "360")))
    parser.add_argument("--test-mode", action="store_true", default=os.getenv("HERMES_RUNTIME_E2E_TEST_MODE") == "1")
    parser.add_argument("--require-done", action="store_true", default=os.getenv("HERMES_RUNTIME_E2E_REQUIRE_DONE") == "1")
    parser.add_argument("--platform", default="trade-finance-instruments",
                        choices=["trade-finance-instruments"],
                        help="Business platform under L6 gate (only trade-finance-instruments is supported).")
    parser.add_argument("--mode", default="legal", choices=["legal"],
                        help="Workflow mode under L6 gate (only legal is supported).")
    args = parser.parse_args()

    request_payload = {
        "skill": "trade-finance-instruments#legal",
        "task": "Review this SBLC legal workflow runtime e2e check for enforceability, expiry, transferability, and claim procedure.",
        "skip_memory": True,
        "max_iter": 1,
    }
    if args.test_mode:
        request_payload["test_mode"] = True

    ok_auth, auth_body = authenticate(args.base_url)
    if not ok_auth:
        print(json.dumps({"PASS": False, "FAILED_REASON": "authentication_failed", "payload": auth_body}, ensure_ascii=False))
        return 1

    status, accepted = post_json(args.base_url, "/api/orchestrate", request_payload)
    task_id = str(accepted.get("task_id") or "")
    if status != 202 or not task_id:
        print(json.dumps({"PASS": False, "FAILED_REASON": "workflow_not_accepted", "status": status, "payload": accepted}, ensure_ascii=False))
        return 1

    seen_statuses: list[str] = ["accepted"]
    deadline = time.time() + max(30, args.timeout)
    latest: dict = {}
    while time.time() < deadline:
        task_status, latest = get_json(args.base_url, f"/api/runtime/task/{task_id}")
        if task_status != 200:
            print(json.dumps({"PASS": False, "FAILED_REASON": "task_status_unreadable", "status": task_status, "payload": latest}, ensure_ascii=False))
            return 1
        current_status = str(latest.get("status") or "")
        if current_status and current_status not in seen_statuses:
            seen_statuses.append(current_status)
        if current_status in {"done", "failed"}:
            break
        time.sleep(2)

    result = latest.get("result") if isinstance(latest.get("result"), dict) else {}
    final_output = str(result.get("final_output") or result.get("output") or "")
    lowered_output = final_output.lower()
    trace = result.get("trace") if isinstance(result.get("trace"), dict) else {}
    steps = latest.get("steps") if isinstance(latest.get("steps"), list) else []
    running_steps = [step for step in steps if isinstance(step, dict) and step.get("status") == "running"]
    done_pass = (
        latest.get("status") == "done"
        and len(final_output.strip()) > (100 if args.require_done else 0)
        and isinstance(result.get("artifact"), dict)
        and bool(result.get("artifact"))
        and isinstance(result.get("decision"), dict)
        and bool(result.get("decision"))
        and isinstance(trace, dict)
        and bool(trace)
        and "fallback response generated" not in lowered_output
        and "系统繁忙" not in final_output
        and "兜底回复" not in final_output
        and "no substantive content" not in lowered_output
    )
    failed_pass = (
        latest.get("status") == "failed"
        and bool(latest.get("error") or result.get("error"))
        and isinstance(result, dict)
        and isinstance(trace, dict)
        and trace.get("failure_layer") == "provider_loop"
        and not running_steps
    )
    passed = done_pass if args.require_done else (done_pass or failed_pass)
    report = {
        "PASS": passed,
        "PASS_DONE": done_pass,
        "PASS_FAILED_DETERMINISTIC": failed_pass,
        "task_id": task_id,
        "workflow": " -> ".join(seen_statuses),
        "status": latest.get("status"),
        "final_output_exists": bool(final_output.strip()),
        "artifact_exists": isinstance(result.get("artifact"), dict) and bool(result.get("artifact")),
        "decision_exists": isinstance(result.get("decision"), dict) and bool(result.get("decision")),
        "trace_exists": bool(trace),
        "failure_layer": trace.get("failure_layer"),
        "running_steps": running_steps,
        "result_exists": bool(result),
        "error": latest.get("error"),
        "test_mode": bool(args.test_mode),
        "require_done": bool(args.require_done),
        "final_output_length": len(final_output.strip()),
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
