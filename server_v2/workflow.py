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
    classify_result,
    compute_quality_score,
    generate_decision,
    is_low_quality,
    is_provider_failure,
    known_good_chat_path,
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
    trace = {
        "runtime_task_id": task.get("id"),
        "mode": "legal_direct",
        "provider_attempts": provider_result.get("trace") if isinstance(provider_result.get("trace"), list) else [],
        "selected_provider": provider_result.get("provider"),
        "selected_model": provider_result.get("model"),
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

def run_legal_workflow_direct(task: dict) -> dict:
    """Call the AI provider and build a structured legal result.

    Raises RuntimeError on failure so the worker can mark the task failed.
    """
    prompt = build_legal_prompt(task)
    task_id = str(task.get("id") or "")
    provider_result = known_good_chat_path(prompt, task_id=task_id, total_timeout=90.0)
    if not provider_result.get("ok"):
        raise RuntimeError(str(provider_result.get("error") or "legal_provider_failed"))
    output = str(provider_result.get("output") or "").strip()
    if is_provider_failure(output) or classify_result(output) in {"empty", "low_quality", "fallback"}:
        raise RuntimeError("legal_provider_non_substantive")
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

def start_workers(queue: QueueManager, pool_size: int = 3, max_parallel: int = 3) -> None:
    """Spawn daemon worker threads that process the queue."""
    for idx in range(min(pool_size, max_parallel)):
        thread = threading.Thread(
            target=_worker_loop,
            args=(queue, idx + 1),
            daemon=True,
            name=f"v2-worker-{idx + 1}",
        )
        thread.start()


def _worker_loop(queue: QueueManager, agent_index: int) -> None:
    agent_id = f"v2-agent-{agent_index}"
    while True:
        try:
            task = queue.next(agent_id)
            if task is None:
                time.sleep(1.5)
                continue
            task_id = str(task.get("id") or "")
            try:
                run_workflow(task, agent_id, queue)
            except Exception as exc:
                queue.update(
                    task_id,
                    status="failed",
                    error=str(exc)[:1000],
                    failed_at=time.time(),
                )
        except Exception:
            time.sleep(2)
