"""/api/orchestrate — enqueues a workflow task and returns task_id for polling."""
from __future__ import annotations

import sys
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException

from ..deps import require_auth
from ..models import OrchestrateRequest
from ..routers.runtime import _default_orchestrate_steps, _status_payload, get_queue

router = APIRouter()


@router.post("/api/orchestrate", status_code=202)
async def orchestrate(
    body: OrchestrateRequest,
    _user: dict = Depends(require_auth),
) -> dict:
    task_text = (body.task or body.prompt or body.title or "").strip()
    if not task_text:
        raise HTTPException(status_code=400, detail="task_required")

    skill = body.skill.strip()
    skill_type = body.workflow_type or body.type or ""
    if skill == "trade-finance-instruments#legal":
        skill_type = "legal_contract_revision"

    orchestrate_data: dict = {
        "task": task_text,
        "skill": "contract_review" if skill == "trade-finance-instruments#legal" else skill,
        "type": skill_type,
        "history": body.history,
        "skip_memory": False,
    }

    payload = {
        "title": task_text,
        "prompt": task_text,
        "source": body.source,
        "skill": skill,
        "workflow_type": skill_type,
        "orchestrate": orchestrate_data,
    }

    steps = _default_orchestrate_steps({"title": task_text, "skill": skill})
    q = get_queue()
    task = q.push({"type": "orchestrate", "payload": payload, "steps": steps})
    task_id = str(task.get("id") or "")

    return {
        "ok": True,
        "accepted": True,
        "task_id": task_id,
        "id": task_id,
        "status": "processing",
        "message": "Workflow accepted for async processing.",
        "task": task,
    }
