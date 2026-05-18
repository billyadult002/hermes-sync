#!/usr/bin/env python3
from __future__ import annotations

import http.cookiejar
import json
import os
import sys
import time
import urllib.request


BASE_URL = os.getenv("HERMES_DIAG_BASE_URL", "http://127.0.0.1:8765")

# /api/runtime/* requires auth. Real login (same mechanism as the health gate)
# so diagnostics reflect the genuine authenticated runtime.
_BROWSER_SESSION = f"diag-{int(time.time())}"
_OPENER: urllib.request.OpenerDirector | None = None


def _authenticate() -> None:
    global _OPENER
    email = os.getenv("HERMES_HEALTH_EMAIL", "bill@fastonegroup.com")
    password = os.getenv("HERMES_HEALTH_PASSWORD", "")
    jar = http.cookiejar.CookieJar()
    _OPENER = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    if not password:
        return
    raw = json.dumps({"email": email, "password": password}).encode("utf-8")
    req = urllib.request.Request(
        f"{BASE_URL}/api/auth/login",
        data=raw,
        headers={"Content-Type": "application/json", "X-Hermes-Browser-Session": _BROWSER_SESSION},
        method="POST",
    )
    try:
        with _OPENER.open(req, timeout=15):
            pass
    except Exception:
        pass


def get_json(path: str) -> dict:
    if _OPENER is None:
        _authenticate()
    req = urllib.request.Request(
        f"{BASE_URL}{path}",
        headers={"X-Hermes-Browser-Session": _BROWSER_SESSION},
        method="GET",
    )
    with (_OPENER or urllib.request).open(req, timeout=10) as resp:
        return json.loads(resp.read().decode("utf-8") or "{}")


def task_has_structured_result(task: dict) -> bool:
    result = task.get("result")
    if not isinstance(result, dict):
        return False
    if task.get("status") == "done":
        return bool(str(result.get("final_output") or result.get("output") or "").strip())
    if task.get("status") == "failed":
        return bool(result.get("error") or task.get("error")) and isinstance(result.get("trace"), dict)
    return True


def running_steps(task: dict) -> list[dict]:
    return [
        step
        for step in task.get("steps", [])
        if isinstance(step, dict) and step.get("status") == "running"
    ]


def main() -> int:
    diagnostics = get_json("/api/runtime/diagnostics")
    tasks_payload = get_json("/api/runtime/tasks?limit=50")
    tasks = [task for task in tasks_payload.get("items", []) if isinstance(task, dict)]
    terminal_tasks = [task for task in tasks if task.get("status") in {"done", "failed"}]
    bad_terminal = [task.get("id") for task in terminal_tasks if not task_has_structured_result(task)]
    terminal_running = [task.get("id") for task in terminal_tasks if running_steps(task)]
    stale_running = diagnostics.get("stale_running") if isinstance(diagnostics.get("stale_running"), list) else []
    stuck_running = [item for item in stale_running if item.get("STUCK_RUNNING")]
    metrics = diagnostics.get("metrics") if isinstance(diagnostics.get("metrics"), dict) else {}
    completed_limit = int(metrics.get("max_completed_history") or 0)
    failed_limit = int(metrics.get("max_failed_history") or 0)
    completed_count = int(metrics.get("completed_tasks") or 0)
    failed_count = int(metrics.get("failed_tasks") or 0)
    completed_history_within_cap = completed_limit <= 0 or completed_count <= completed_limit
    failed_history_within_cap = failed_limit <= 0 or failed_count <= failed_limit
    archive_ok = not bool(metrics.get("last_archive_error"))
    now = time.time()
    heartbeat_at = float(diagnostics.get("heartbeat_updated_at") or 0)
    report = {
        "PASS": bool(
            diagnostics.get("queue_dispatch") == "ok"
            and diagnostics.get("worker_alive") is True
            and heartbeat_at
            and now - heartbeat_at < 20
            and not stuck_running
            and not bad_terminal
            and not terminal_running
            and completed_history_within_cap
            and failed_history_within_cap
            and archive_ok
        ),
        "queue_dispatch": diagnostics.get("queue_dispatch"),
        "worker_alive": diagnostics.get("worker_alive"),
        "heartbeat_age_sec": round(now - heartbeat_at, 1) if heartbeat_at else None,
        "stuck_running": stuck_running,
        "bad_terminal_result_tasks": bad_terminal,
        "terminal_tasks_with_running_steps": terminal_running,
        "history_cap": {
            "completed_history_within_cap": completed_history_within_cap,
            "failed_history_within_cap": failed_history_within_cap,
            "archive_ok": archive_ok,
            "completed_limit": completed_limit,
            "failed_limit": failed_limit,
        },
        "metrics": metrics,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["PASS"] else 1


if __name__ == "__main__":
    sys.exit(main())
