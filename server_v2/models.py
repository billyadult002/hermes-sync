"""Pydantic v2 request/response models for server_v2."""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, field_validator


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

class LoginRequest(BaseModel):
    identifier: str = ""
    email: str = ""
    password: str

    @field_validator("identifier", "email", mode="before")
    @classmethod
    def _strip(cls, v: Any) -> str:
        return str(v or "").strip()

    def resolved_identifier(self) -> str:
        return self.identifier or self.email


class LoginResponse(BaseModel):
    ok: bool
    authenticated: bool = False
    user: dict | None = None
    session_token: str | None = None
    idle_timeout_seconds: int = 0
    error: str | None = None


class SessionResponse(BaseModel):
    ok: bool = True
    authenticated: bool
    user: dict | None = None
    idle_timeout_seconds: int = 0
    idle_remaining_seconds: int = 0


class LogoutResponse(BaseModel):
    ok: bool = True


# ---------------------------------------------------------------------------
# Runtime / queue
# ---------------------------------------------------------------------------

class EnqueueTaskRequest(BaseModel):
    type: str = "workflow"
    payload: dict[str, Any] | None = None
    title: str = ""
    prompt: str = ""
    task: str = ""
    source: str = "api"


class TaskResponse(BaseModel):
    ok: bool = True
    task: dict[str, Any]
    runtime: dict[str, Any] | None = None


class TaskDetailResponse(BaseModel):
    ok: bool = True
    id: str
    status: str
    result: dict[str, Any] | None = None
    steps: list[dict[str, Any]] = []
    error: str | None = None
    created_at: float | None = None
    updated_at: float | None = None
    completed_at: float | None = None
    failed_at: float | None = None
    assigned_agent: str | None = None
    attempts: int = 0
    progress: str | None = None


class TasksListResponse(BaseModel):
    ok: bool = True
    items: list[dict[str, Any]]
    metrics: dict[str, Any]


class RuntimeStatusResponse(BaseModel):
    ok: bool = True
    running_agents: int = 0
    queue_size: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    pending_tasks: int = 0
    running_tasks: int = 0
    agent_pool_size: int = 3
    max_parallel_tasks: int = 3
    agents: list[dict[str, Any]] = []
    recent_workflow_steps: list[dict[str, Any]] = []


# ---------------------------------------------------------------------------
# Orchestrate (Week 2)
# ---------------------------------------------------------------------------

class OrchestrateRequest(BaseModel):
    task: str = ""
    skill: str = ""
    type: str = ""
    prompt: str = ""
    title: str = ""
    history: list[dict[str, Any]] = []
    workflow_type: str = ""
    source: str = "ui"


class OrchestrateAcceptedResponse(BaseModel):
    ok: bool = True
    accepted: bool = True
    task_id: str
    status: str = "pending"


# ---------------------------------------------------------------------------
# Chat (Week 2)
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    messages: list[dict[str, Any]] = []
    prompt: str = ""
    skill: str = ""
    model: str = ""
    provider: str = ""
    stream: bool = False


class ChatResponse(BaseModel):
    ok: bool = True
    output: str = ""
    provider: str = ""
    model: str = ""


# ---------------------------------------------------------------------------
# Copilots / AI agent registry
# ---------------------------------------------------------------------------

class CopilotEntry(BaseModel):
    id: str
    name: str
    description: str = ""
    type: str = "ai_agent"
    status: str = "active"


class CopilotRegistryResponse(BaseModel):
    ok: bool = True
    agents: list[dict[str, Any]] = []
    copilots: list[dict[str, Any]] = []


# ---------------------------------------------------------------------------
# Error
# ---------------------------------------------------------------------------

class ErrorResponse(BaseModel):
    ok: bool = False
    error: str
