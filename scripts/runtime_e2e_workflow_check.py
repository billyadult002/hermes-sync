#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request


def post_json(base_url: str, path: str, payload: dict, timeout: int = 15) -> tuple[int, dict]:
    raw = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{base_url.rstrip('/')}{path}",
        data=raw,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return int(resp.status), json.loads(resp.read().decode("utf-8") or "{}")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="ignore")
        try:
            payload = json.loads(body or "{}")
        except Exception:
            payload = {"raw": body}
        return int(exc.code), payload


def get_json(base_url: str, path: str, timeout: int = 10) -> tuple[int, dict]:
    try:
        with urllib.request.urlopen(f"{base_url.rstrip('/')}{path}", timeout=timeout) as resp:
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
