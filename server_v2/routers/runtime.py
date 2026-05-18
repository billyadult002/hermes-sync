"""Runtime queue API: /api/runtime/*."""
from __future__ import annotations

import sys
import time
from pathlib import Path
from typing import Any

import asyncio
import contextlib

from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect

from ..config import (
    AGENT_POOL_SIZE,
    MAX_PARALLEL_TASKS,
    TASK_QUEUE_ARCHIVE_PATH,
    TASK_QUEUE_PATH,
    MAX_COMPLETED_TASK_HISTORY,
    MAX_FAILED_TASK_HISTORY,
)
from ..deps import optional_auth, require_auth
from ..models import EnqueueTaskRequest

# Import shared queue manager from parent package
_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
from queue_manager import QueueManager  # noqa: E402

router = APIRouter()

# One shared QueueManager instance — reads/writes the same task_queue.json
# that the production autonomous worker also uses.
_queue: QueueManager | None = None
_agent_state: dict[str, dict] = {}


def get_queue() -> QueueManager:
    global _queue
    if _queue is None:
        _queue = QueueManager(
            TASK_QUEUE_PATH,
            max_completed_history=MAX_COMPLETED_TASK_HISTORY,
            max_failed_history=MAX_FAILED_TASK_HISTORY,
            archive_path=TASK_QUEUE_ARCHIVE_PATH,
        )
    return _queue


def _default_steps(payload: dict | None = None) -> list[dict]:
    p = payload or {}
    raw = p.get("steps") if isinstance(p.get("steps"), list) else []
    steps: list[dict] = []
    for idx, step in enumerate(raw, start=1):
        name = step.get("name") or step.get("type") or f"step_{idx}" if isinstance(step, dict) else str(step or f"step_{idx}")
        if name:
            steps.append({"name": name, "status": "pending"})
    return steps or [
        {"name": "analyze", "status": "pending"},
        {"name": "generate", "status": "pending"},
        {"name": "review", "status": "pending"},
    ]


def _default_orchestrate_steps(payload: dict) -> list[dict]:
    title = str(payload.get("title") or payload.get("prompt") or payload.get("task") or "").lower()
    skill = str(payload.get("skill") or "").lower()
    if any(kw in title for kw in ("legal", "contract", "sblc", "dlc")) or skill in {"contract_review", "trade-finance-instruments#legal"}:
        return [
            {"name": "run legal analysis", "status": "pending"},
            {"name": "generate structured result", "status": "pending"},
            {"name": "review result", "status": "pending"},
        ]
    return [
        {"name": "analyze", "status": "pending"},
        {"name": "generate", "status": "pending"},
        {"name": "review", "status": "pending"},
    ]


def _task_title(task: dict) -> str:
    payload = task.get("payload") if isinstance(task.get("payload"), dict) else {}
    title = payload.get("title") or payload.get("prompt") or payload.get("task") or task.get("type") or "workflow"
    return str(title).strip()[:160] or "workflow"


def _status_payload(q: QueueManager) -> dict:
    tasks = q.all()
    metrics = q.metrics()
    recent = sorted(tasks, key=lambda t: float(t.get("updated_at") or t.get("created_at") or 0), reverse=True)[:8]
    return {
        "ok": True,
        "running_agents": 0,
        "queue_size": metrics.get("queue_size", 0),
        "completed_tasks": metrics.get("completed_tasks", 0),
        "failed_tasks": metrics.get("failed_tasks", 0),
        "pending_tasks": metrics.get("pending_tasks", 0),
        "running_tasks": metrics.get("running_tasks", 0),
        "agent_pool_size": AGENT_POOL_SIZE,
        "max_parallel_tasks": MAX_PARALLEL_TASKS,
        "max_completed_history": q.max_completed_history,
        "max_failed_history": q.max_failed_history,
        "terminal_history_limit": metrics.get("terminal_history_limit", 0),
        "task_queue_file_bytes": metrics.get("task_queue_file_bytes", 0),
        "task_queue_archive_file_bytes": metrics.get("task_queue_archive_file_bytes", 0),
        "task_queue_archive_enabled": bool(q.archive_path),
        "last_archive_count": metrics.get("last_archive_count", 0),
        "last_archive_error": metrics.get("last_archive_error"),
        "agents": [],
        "recent_workflow_steps": [
            {
                "id": t.get("id"),
                "title": _task_title(t),
                "status": t.get("status"),
                "assigned_agent": t.get("assigned_agent"),
                "steps": t.get("steps") if isinstance(t.get("steps"), list) else [],
                "updated_at": t.get("updated_at"),
            }
            for t in recent
        ],
    }


@router.get("/api/runtime/status")
async def runtime_status(_user: dict | None = Depends(optional_auth)) -> dict:
    # Public read (parity with legacy app_server.py): the React dashboard polls
    # this unauthenticated for the live status widget.
    return _status_payload(get_queue())


@router.get("/api/runtime/providers")
async def runtime_providers(_user: dict | None = Depends(optional_auth)) -> dict:
    """L7 observability: provider score / state / metrics for Dashboard + War Room."""
    try:
        from ..provider_intelligence import provider_scoreboard
        return provider_scoreboard()
    except Exception as exc:  # never break the dashboard
        return {"ok": False, "providers": {}, "error": str(exc)[:200]}


@router.get("/api/runtime/tasks")
async def list_tasks(
    limit: int = Query(default=100, ge=1, le=500),
    _user: dict | None = Depends(optional_auth),
) -> dict:
    q = get_queue()
    tasks = sorted(q.all(), key=lambda t: float(t.get("created_at") or 0), reverse=True)[:limit]
    return {"ok": True, "items": tasks, "metrics": q.metrics()}


@router.get("/api/runtime/task/{task_id}")
async def get_task(task_id: str, _user: dict = Depends(require_auth)) -> dict:
    task = get_queue().get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="task_not_found")
    return {
        "ok": True,
        "id": task.get("id"),
        "status": task.get("status"),
        "result": task.get("result"),
        "error": task.get("error"),
        "steps": task.get("steps") if isinstance(task.get("steps"), list) else [],
        "task": task,
    }


@router.post("/api/runtime/tasks", status_code=202)
async def enqueue_task(
    body: EnqueueTaskRequest,
    _user: dict = Depends(require_auth),
) -> dict:
    q = get_queue()
    payload = body.payload or {}
    if not payload:
        payload = {
            "title": body.title or body.task or body.prompt or "Autonomous workflow",
            "prompt": body.prompt or body.task or body.title or "",
            "source": body.source,
        }
    if not payload.get("steps"):
        payload["steps"] = ["analyze", "generate", "review"]

    steps = _default_orchestrate_steps(payload) if body.type == "orchestrate" else _default_steps(payload)
    task = q.push({"type": body.type, "payload": payload, "steps": steps})
    return {"ok": True, "task": task, "runtime": _status_payload(q)}


@router.websocket("/ws/metrics")
async def ws_metrics(ws: WebSocket) -> None:
    """Native live metrics stream (parity with legacy app_server.py /ws/metrics).

    server_v2 owns the runtime, so it serves this directly rather than proxying.
    Public, like the legacy endpoint — the React Control panel subscribes to it.
    """
    await ws.accept()
    try:
        q = get_queue()
        await ws.send_json({"type": "metrics", **q.metrics()})
        while True:
            await asyncio.sleep(15)
            await ws.send_json({"type": "metrics", **get_queue().metrics()})
            await ws.send_json({"type": "ping", "timestamp": int(time.time() * 1000)})
    except WebSocketDisconnect:
        pass
    except Exception:
        with contextlib.suppress(Exception):
            await ws.close()


@router.get("/api/runtime/diagnostics")
async def runtime_diagnostics(_user: dict = Depends(require_auth)) -> dict:
    now = time.time()
    q = get_queue()
    tasks = q.all()
    stale_running = []
    for task in tasks:
        if not isinstance(task, dict) or task.get("status") != "running":
            continue
        updated = float(task.get("updated_at") or task.get("started_at") or 0)
        steps = task.get("steps") if isinstance(task.get("steps"), list) else []
        current_step = next((s for s in steps if isinstance(s, dict) and s.get("status") == "running"), steps[-1] if steps else {})
        stale_running.append({
            "task_id": task.get("id"),
            "assigned_agent": task.get("assigned_agent"),
            "current_step": current_step.get("name") if isinstance(current_step, dict) else None,
            "last_update": updated,
            "age_since_update_sec": round(now - updated, 1) if updated else None,
            "STUCK_RUNNING": bool(updated and now - updated > 30),
            "result_empty": not bool(task.get("result")),
        })
    from ..workflow import worker_diagnostics
    wd = worker_diagnostics()
    return {
        "ok": True,
        "worker_alive": wd["worker_alive"],
        "queue_dispatch": wd["queue_dispatch"],
        "heartbeat_updated_at": wd["heartbeat_updated_at"],
        "agents": wd["agents"],
        "metrics": q.metrics(),
        "stale_running": stale_running,
    }
