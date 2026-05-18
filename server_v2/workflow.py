"""Legal and orchestrate workflow execution — extracted from app_server.py.

run_legal_workflow_direct and run_workflow are the two main entry points.
They are called by the autonomous worker (in app_server.py during migration,
and directly by server_v2 workers once fully migrated).
"""
from __future__ import annotations

import sys
import threading
import time
from pathlib import Path

from .providers import (
    PROVIDER_CHAIN,
    classify_result,
    compute_quality_score,
    generate_decision,
    is_low_quality,
    is_provider_failure,
    run_provider_chain,
)

# Import shared queue manager
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
from queue_manager import QueueManager  # noqa: E402


# ---------------------------------------------------------------------------
# Legal task detection and prompt building
# ---------------------------------------------------------------------------

_LEGAL_TOKENS = frozenset({"trade-finance-instruments#legal", "contract_review", "legal", "sblc", "dlc"})


def is_legal_task(task: dict) -> bool:
    payload = task.get("payload") if isinstance(task.get("payload"), dict) else {}
    orchestration_data = payload.get("orchestrate") if isinstance(payload.get("orchestrate"), dict) else {}
    searchable = " ".join(
        str(v or "")
        for v in [
            payload.get("skill"),
            payload.get("workflow_type"),
            payload.get("title"),
            payload.get("prompt"),
            orchestration_data.get("skill"),
            orchestration_data.get("type"),
            orchestration_data.get("task"),
        ]
    ).lower()
    return any(token in searchable for token in _LEGAL_TOKENS)


def build_legal_prompt(task: dict) -> str:
    payload = task.get("payload") if isinstance(task.get("payload"), dict) else {}
    orchestration_data = payload.get("orchestrate") if isinstance(payload.get("orchestrate"), dict) else {}
    source_text = str(
        orchestration_data.get("task")
        or orchestration_data.get("prompt")
        or payload.get("prompt")
        or payload.get("title")
        or ""
    ).strip()
    return (
        "Return only the final answer. Do not include hidden reasoning.\n\n"
        "You are a senior trade finance legal reviewer for SBLC, DLC, standby credit, "
        "contract review, and bank instrument workflows. Produce a substantive legal review "
        "memorandum suitable for Fastone Finance Workbench production use.\n\n"
        "Required headings:\n"
        "1. Executive Legal Conclusion\n"
        "2. Issues Reviewed\n"
        "3. Enforceability Analysis\n"
        "4. Expiry and Presentation Risk\n"
        "5. Transferability Analysis\n"
        "6. Claim Procedure Review\n"
        "7. Recommended Revisions\n"
        "8. Decision\n\n"
        "Do not say the system is busy. Do not provide a fallback response. If source facts "
        "are incomplete, state the assumptions and give concrete review controls.\n\n"
        f"Source workflow request:\n{source_text}"
    )


def _compact_text(text: object, limit: int = 900) -> str:
    value = str(text or "").strip()
    return value[:limit] + "..." if len(value) > limit else value


# ---------------------------------------------------------------------------
# Result building
# ---------------------------------------------------------------------------

def build_legal_structured_result(final_output: str, task: dict, provider_result: dict) -> dict:
    steps = [
        {
            "name": "run legal analysis",
            "status": "done",
            "output": _compact_text(final_output, 900),
            "provider": provider_result.get("provider"),
        },
        {
            "name": "generate structured result",
            "status": "done",
            "output": "Structured legal artifact generated.",
            "provider": "runtime",
        },
        {
            "name": "review result",
            "status": "done",
            "output": "Result reviewed for minimum legal substance and fallback markers.",
            "provider": "runtime",
        },
    ]
    score = compute_quality_score(final_output, steps)
    decision = generate_decision({"quality_score": score})
    attempts = provider_result.get("trace") if isinstance(provider_result.get("trace"), list) else []
    # Pass through the rich provider_execution produced by run_provider_chain
    # (recommended_order / actual_order / provider_state / flags / workflow_rec).
    pexec = provider_result.get("provider_execution") if isinstance(provider_result.get("provider_execution"), dict) else {}
    if not pexec:
        pexec = {
            "chain": [f'{c["provider"]}:{c["model"]}' for c in PROVIDER_CHAIN],
            "attempts": attempts,
            "selected_provider": provider_result.get("provider"),
            "selected_model": provider_result.get("model"),
            "total_latency_ms": sum(int(a.get("latency_ms") or 0) for a in attempts if isinstance(a, dict)),
        }
    trace = {
        "runtime_task_id": task.get("id"),
        "mode": "legal_direct",
        "provider_attempts": attempts,
        "selected_provider": provider_result.get("provider"),
        "selected_model": provider_result.get("model"),
        "provider_execution": pexec,
        "quality_score": score,
        "fake_fallback": False,
        "completed_at": time.time(),
    }
    artifact_text = final_output.strip()
    return {
        "status": "success",
        "output": artifact_text,
        "final_output": artifact_text,
        "artifact": {"type": "markdown", "text": artifact_text},
        "decision": decision,
        "trace": trace,
        "steps": steps,
        "quality_score": score,
        "provider": provider_result.get("provider"),
        "model": provider_result.get("model"),
    }


# ---------------------------------------------------------------------------
# Direct legal workflow
# ---------------------------------------------------------------------------

class WorkflowError(RuntimeError):
    """Carries provider trace so failed tasks get a structured result."""

    def __init__(self, message: str, trace: list | None = None, layer: str = "workflow") -> None:
        super().__init__(message)
        self.trace = trace if isinstance(trace, list) else []
        self.layer = layer


def run_legal_workflow_direct(task: dict) -> dict:
    """Call the AI provider and build a structured legal result.

    Raises WorkflowError (with provider trace) on failure so the worker can
    persist a structured failure result.
    """
    prompt = build_legal_prompt(task)
    task_id = str(task.get("id") or "")
    # Single unified entry point — deterministic Codex->Gemini->xAI->NVIDIA chain.
    provider_result = run_provider_chain(prompt, task_id=task_id, total_timeout=90.0, mode="legal")
    trace = provider_result.get("trace") if isinstance(provider_result.get("trace"), list) else []
    if not provider_result.get("ok"):
        raise WorkflowError(str(provider_result.get("error") or "legal_provider_failed"), trace, "legal_provider_path")
    output = str(provider_result.get("output") or "").strip()
    if is_provider_failure(output) or classify_result(output) in {"empty", "low_quality", "fallback"}:
        raise WorkflowError("legal_provider_non_substantive", trace, "legal_provider_path")
    return build_legal_structured_result(output, task, provider_result)


# ---------------------------------------------------------------------------
# Full workflow runner (mirrors app_server.py run_workflow for orchestrate tasks)
# ---------------------------------------------------------------------------

def run_workflow(task: dict, agent_id: str, queue: QueueManager) -> dict:
    """Execute a queued workflow task, updating the queue at each step.

    This is a drop-in replacement for app_server.py's run_workflow.
    """
    task_id = str(task.get("id") or "")
    payload = task.get("payload") if isinstance(task.get("payload"), dict) else {}

    # Determine steps
    raw_steps = task.get("steps") if isinstance(task.get("steps"), list) else []
    if not raw_steps:
        raw_steps = [
            {"name": "analyze", "status": "pending"},
            {"name": "generate", "status": "pending"},
            {"name": "review", "status": "pending"},
        ]
    steps = [s if isinstance(s, dict) else {"name": str(s), "status": "pending"} for s in raw_steps]
    queue.update(task_id, steps=steps)

    if task.get("type") == "orchestrate" and is_legal_task(task):
        return _run_legal_orchestrate(task, task_id, agent_id, steps, queue)

    # Generic workflow: each step gets a stub result
    for idx, step in enumerate(steps):
        step["status"] = "running"
        step["started_at"] = time.time()
        queue.update(task_id, steps=steps, assigned_agent=agent_id)
        time.sleep(0.1)
        step["status"] = "done"
        step["completed_at"] = time.time()
        queue.update(task_id, steps=steps)

    result = {
        "status": "success",
        "output": "Workflow complete.",
        "final_output": "Workflow complete.",
        "task_id": task_id,
        "agent": agent_id,
        "completed_at": time.time(),
    }
    queue.update(task_id, status="done", result=result, completed_at=result["completed_at"], progress="Workflow complete")
    return result


def _run_legal_orchestrate(
    task: dict,
    task_id: str,
    agent_id: str,
    steps: list[dict],
    queue: QueueManager,
) -> dict:
    result_payload: dict | None = None

    for idx, step in enumerate(steps):
        step["status"] = "running"
        step["started_at"] = time.time()
        queue.update(task_id, steps=steps, assigned_agent=agent_id)

        if idx == 0:
            queue.update(task_id, progress="Running legal analysis...")
            result_payload = run_legal_workflow_direct(task)
        elif idx == 1:
            queue.update(task_id, progress="Generating structured legal result...")
            if not isinstance(result_payload, dict):
                raise RuntimeError("legal_result_missing")
        else:
            queue.update(task_id, progress="Reviewing legal result...")
            final_output = str((result_payload or {}).get("final_output") or "")
            if is_provider_failure(final_output) or classify_result(final_output) in {"empty", "low_quality", "fallback"}:
                raise RuntimeError("legal_result_review_failed")

        time.sleep(0.1)
        step["status"] = "done"
        step["completed_at"] = time.time()
        queue.update(task_id, steps=steps)

    result = dict(result_payload or {})
    result["task_id"] = task_id
    result["agent"] = agent_id
    result["completed_at"] = time.time()
    queue.update(task_id, status="done", result=result, completed_at=result["completed_at"], progress="Workflow complete")
    return result


# ---------------------------------------------------------------------------
# Autonomous worker pool (mirrors app_server.py autonomous_worker)
# ---------------------------------------------------------------------------

# Worker liveness registry (real heartbeat, mirrors app_server.py agents).
_WORKER_HEARTBEATS: dict[str, float] = {}
_WORKERS_STARTED = False
_HEARTBEAT_LOCK = threading.Lock()


def _touch_heartbeat(agent_id: str) -> None:
    with _HEARTBEAT_LOCK:
        _WORKER_HEARTBEATS[agent_id] = time.time()


def worker_diagnostics() -> dict:
    """Genuine worker-pool liveness for /api/runtime/diagnostics."""
    now = time.time()
    with _HEARTBEAT_LOCK:
        agents = [
            {"agent_id": aid, "last_seen": ts, "age_sec": round(now - ts, 1)}
            for aid, ts in _WORKER_HEARTBEATS.items()
        ]
        started = _WORKERS_STARTED
    last_seens = [a["last_seen"] for a in agents] or [0.0]
    return {
        "agents": agents,
        "worker_alive": any(now - ls < 15 for ls in last_seens) if agents else False,
        "queue_dispatch": "ok" if started else "not_started",
        "heartbeat_updated_at": max(last_seens),
    }


def start_workers(queue: QueueManager, pool_size: int = 3, max_parallel: int = 3) -> None:
    """Spawn daemon worker threads that process the queue."""
    global _WORKERS_STARTED
    for idx in range(min(pool_size, max_parallel)):
        thread = threading.Thread(
            target=_worker_loop,
            args=(queue, idx + 1),
            daemon=True,
            name=f"v2-worker-{idx + 1}",
        )
        thread.start()
    _WORKERS_STARTED = True


def _worker_loop(queue: QueueManager, agent_index: int) -> None:
    agent_id = f"v2-agent-{agent_index}"
    while True:
        try:
            _touch_heartbeat(agent_id)
            task = queue.next(agent_id)
            if task is None:
                time.sleep(1.5)
                continue
            task_id = str(task.get("id") or "")
            try:
                run_workflow(task, agent_id, queue)
            except Exception as exc:
                trace = getattr(exc, "trace", []) or []
                layer = getattr(exc, "layer", "workflow")
                now = time.time()
                current = queue.get(task_id) or task
                current_steps = current.get("steps") if isinstance(current.get("steps"), list) else []
                for step in current_steps:
                    if not isinstance(step, dict):
                        continue
                    if step.get("status") == "running":
                        step["status"] = "failed"
                        step["failed_at"] = now
                        step["error"] = str(exc)[:500]
                    elif step.get("status") == "pending":
                        step["status"] = "skipped"
                        step["skipped_at"] = now
                        step["skip_reason"] = "prior_step_failed"
                failure_result = {
                    "status": "failed",
                    "error": str(exc)[:1000],
                    "failure_layer": layer,
                    "trace": {
                        "provider_attempts": trace,
                        "failure": str(exc)[:500],
                        "failure_layer": layer,
                    },
                    "completed_at": now,
                }
                queue.update(
                    task_id,
                    status="failed",
                    steps=current_steps,
                    error=str(exc)[:1000],
                    failed_at=now,
                    result=failure_result,
                )
            _touch_heartbeat(agent_id)
        except Exception:
            time.sleep(2)
