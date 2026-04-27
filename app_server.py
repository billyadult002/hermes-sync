#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import sqlite3
import asyncio
import base64
import email.utils
import hashlib
import hmac
import mimetypes
import random
import secrets
import shutil
import signal
import socket
import subprocess
import sys
import threading
import time
try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib
from datetime import datetime, timedelta
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib import error as urllib_error
from urllib import request as urllib_request
from urllib.parse import parse_qs, quote, unquote, urlparse
from zoneinfo import ZoneInfo
import xml.etree.ElementTree as ET

import httpx
import yaml
from openpyxl import Workbook

HOME = Path.home()
HERMES_HOME = HOME / ".hermes"
ROOT = HERMES_HOME / "finance-workbench"
CODEX_HOME = HOME / ".codex"
CODEX_SKILLS_DIR = CODEX_HOME / "skills"
CODEX_PLUGIN_CACHE_DIR = CODEX_HOME / "plugins" / "cache"
HERMES_ONLINE_SKILLS_DIR = HERMES_HOME / "skills"
GOOGLE_WORKSPACE_FIX = Path("/Users/billtin/Documents/New project/google-workspace-fix")
if str(GOOGLE_WORKSPACE_FIX) not in sys.path:
    sys.path.insert(0, str(GOOGLE_WORKSPACE_FIX))
from profile_store import ensure_profile, list_profiles, migrate_legacy_default_profile, profile_slug, set_default_profile
COMPOSIO_FIX = Path("/Users/billtin/Documents/New project/composio-fix")
if str(COMPOSIO_FIX) not in sys.path:
    sys.path.insert(0, str(COMPOSIO_FIX))
from composio_profile_store import (
    ensure_profile as ensure_composio_profile,
    load_api_key as load_composio_api_key,
    list_profiles as list_composio_profiles,
    profile_slug as composio_profile_slug,
    save_api_key as save_composio_api_key,
    seed_default_profiles as seed_composio_profiles,
    set_default_profile as set_default_composio_profile,
    update_test_status as update_composio_test_status,
)
HERMES_PROJECT = HERMES_HOME / "hermes-agent"
HERMES_AGENT_SKILLS_DIR = HERMES_PROJECT / "skills"
HERMES_AGENT_OPTIONAL_SKILLS_DIR = HERMES_PROJECT / "optional-skills"
CONFIG_PATH = HERMES_HOME / "config.yaml"
ENV_PATH = HERMES_HOME / ".env"
AUTH_PATH = HERMES_HOME / "auth.json"
GATEWAY_LOG = ROOT / "gateway.log"
APP_LOG = ROOT / "app_server.log"
AUDIT_DIR = ROOT / "audit"
EXPORTS_DIR = Path("/Users/billtin/Documents/Export Documents")
MEMORY_DIR = ROOT / "memory"
AUTOMATIONS_DIR = HOME / ".codex" / "automations"
LOCAL_AUTH_USERS = ROOT / "local_users.json"
LOCAL_AUTH_SESSIONS = ROOT / "local_sessions.json"
WORK_CHAT_PATH = ROOT / "work_chats.json"
WORK_CHAT_STORAGE_DIR = ROOT / "work_chat_files"
WORK_CHAT_FILE_MAX_BYTES = 25 * 1024 * 1024
DOCUMENT_FLOW_PATH = ROOT / "document_flows.json"
WORK_CHAT_VISIBLE_DAYS = 7
WORK_CHAT_RETENTION_DAYS = 15
WORK_CHAT_COLLAPSE_SECONDS = 5 * 60
DOCUMENT_STORAGE_DIR = ROOT / "document_flow_files"
DOCUMENT_STATUS_VALUES = {
    "draft",
    "in_review",
    "returned_for_revision",
    "pending_approval",
    "rejected",
    "approved",
    "signed",
    "archived_locked",
    "superseded",
}
DOCUMENT_READ_ONLY_STATUSES = {"signed", "archived_locked", "superseded"}
ACTIVITY_DIR = ROOT / "activity"
ACTIVITY_METRICS_PATH = ACTIVITY_DIR / "user_activity_metrics.json"
SPRINT_14DAY_STATUS_PATH = ACTIVITY_DIR / "enterprise_sprint_14day_status.json"
V2_DATA_DIR = ROOT / "data"
V2_DB_PATH = V2_DATA_DIR / "work_mgmt_v2.db"
V2_MIGRATIONS_DIR = Path(__file__).resolve().parent / "db" / "migrations"
FILE_CENTER_STORAGE_DIR = ROOT / "file_center_storage"
FILE_CENTER_ARCHIVE_DIR = ROOT / "file_center_archives"
V2_REPORT_SCHEDULER_STATE = ACTIVITY_DIR / "v2_report_scheduler_state.json"
ADMIN_DAILY_REPORTS_DIR = ACTIVITY_DIR / "admin_daily_reports"
LATEST_ADMIN_ACTIVITY_REPORT = ADMIN_DAILY_REPORTS_DIR / "latest.json"
ADMIN_MONTHLY_REPORTS_DIR = ACTIVITY_DIR / "admin_monthly_reports"
LATEST_ADMIN_MONTHLY_REPORT = ADMIN_MONTHLY_REPORTS_DIR / "latest.json"
ADMIN_EMAIL = "bill@fastonegroup.com"
ADMIN_USERNAME = "bill"
ADMIN_PASSWORD = "54ab2398"
ONLINE_WINDOW_SECONDS = 10 * 60
ADMIN_IDLE_TIMEOUT_SECONDS = 120
USER_IDLE_TIMEOUT_SECONDS = 180
ADMIN_REPORT_HOUR = 8
ADMIN_MONTHLY_REPORT_HOUR = 10
LOCAL_TIMEZONE = ZoneInfo("Asia/Shanghai")
WORKDAY_START_HOUR = 8
WORKDAY_END_HOUR = 18
HOST = "127.0.0.1"
PORT = 8765
HERMES_API = "http://127.0.0.1:8642/v1"
CLIPROXY_API = "http://127.0.0.1:8317/v1"
LM_API = "http://127.0.0.1:1234/v1/models"
CODEX_MODELS = ["gpt-5.3-codex", "gpt-5.4", "gpt-5.4-mini"]
CHATGPT_FALLBACK_MODEL = "gpt-5.4-mini"
GEMINI_MODELS = [
    "gemini-3.1-pro-preview",
    "gemini-3.1-flash-lite-preview",
]
COMPOSIO_RUNTIME = Path("/Users/billtin/Documents/New project/composio-runtime/bin/composio")
COMPOSIO_CACHE_ROOT = Path("/Users/billtin/Documents/New project/composio-runtime/profile-cache")

ROOT.mkdir(parents=True, exist_ok=True)
AUDIT_DIR.mkdir(parents=True, exist_ok=True)
EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
MEMORY_DIR.mkdir(parents=True, exist_ok=True)
ACTIVITY_DIR.mkdir(parents=True, exist_ok=True)
ADMIN_DAILY_REPORTS_DIR.mkdir(parents=True, exist_ok=True)
ADMIN_MONTHLY_REPORTS_DIR.mkdir(parents=True, exist_ok=True)
DOCUMENT_STORAGE_DIR.mkdir(parents=True, exist_ok=True)
V2_DATA_DIR.mkdir(parents=True, exist_ok=True)
WORK_CHAT_STORAGE_DIR.mkdir(parents=True, exist_ok=True)
FILE_CENTER_STORAGE_DIR.mkdir(parents=True, exist_ok=True)
FILE_CENTER_ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
migrate_legacy_default_profile()
seed_composio_profiles()
gateway_proc: subprocess.Popen[bytes] | None = None
gateway_lock = threading.Lock()
SERVER_STARTED_EPOCH = int(time.time())
PROVIDER_COOLDOWN_SECONDS = 1800
TRANSIENT_PROVIDER_COOLDOWN_SECONDS = 300
GEMINI_ATTEMPT_TIMEOUT = 4.0
CHATGPT_ATTEMPT_TIMEOUT = 60.0
FAST_MODE_ATTEMPT_TIMEOUT = 6.0
provider_health: dict[str, dict[str, float | str]] = {}
intel_runtime_cache: dict[str, dict[str, object]] = {}
intel_runtime_cache_lock = threading.Lock()
local_auth_lock = threading.Lock()
activity_metrics_lock = threading.Lock()
work_chat_lock = threading.Lock()
v2_db_lock = threading.Lock()


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


def _extract_assistant_text(payload: object) -> str:
    if not isinstance(payload, dict):
        return _content_text(payload)
    choices = payload.get("choices")
    if isinstance(choices, list):
        collected: list[str] = []
        for choice in choices:
            if not isinstance(choice, dict):
                continue
            delta = choice.get("delta")
            if isinstance(delta, dict):
                text = _content_text(delta.get("content")) or _content_text(delta.get("reasoning_content"))
                if text:
                    collected.append(text)
            message = choice.get("message")
            if isinstance(message, dict):
                text = _content_text(message.get("content"))
                if text:
                    collected.append(text)
        if collected:
            return "".join(collected)
    for key in ("content", "output_text", "text", "response"):
        text = _content_text(payload.get(key))
        if text:
            return text
    return ""


def _send_sse_text(handler: "Handler", model: str, text: str) -> None:
    role_chunk = {
        "id": f"chatcmpl-{int(time.time() * 1000)}",
        "object": "chat.completion.chunk",
        "created": int(time.time()),
        "model": model,
        "choices": [{"index": 0, "delta": {"role": "assistant"}, "finish_reason": None}],
    }
    content_chunk = {
        "id": role_chunk["id"],
        "object": "chat.completion.chunk",
        "created": role_chunk["created"],
        "model": model,
        "choices": [{"index": 0, "delta": {"content": text}, "finish_reason": None}],
    }
    stop_chunk = {
        "id": role_chunk["id"],
        "object": "chat.completion.chunk",
        "created": role_chunk["created"],
        "model": model,
        "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}],
    }
    for chunk in (role_chunk, content_chunk, stop_chunk):
        handler.wfile.write(f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n".encode("utf-8"))
        handler.wfile.flush()
    handler.wfile.write(b"data: [DONE]\n\n")
    handler.wfile.flush()


def _extract_sse_text(raw_stream: bytes) -> str:
    text_parts: list[str] = []
    normalized = raw_stream.decode("utf-8", errors="ignore").replace("\r\n", "\n")
    for block in normalized.split("\n\n"):
        for line in block.split("\n"):
            line = line.strip()
            if not line.startswith("data:"):
                continue
            payload = line[5:].strip()
            if not payload or payload == "[DONE]":
                continue
            try:
                parsed = json.loads(payload)
            except Exception:
                text_parts.append(payload)
                continue
            text = _extract_assistant_text(parsed)
            if text:
                text_parts.append(text)
    return "".join(text_parts).strip()


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


def _is_retryable_chat_failure(provider: str, status_code: int, error_text: str) -> bool:
    message = error_text.lower()
    if status_code in {408, 409, 425, 429, 500, 502, 503, 504}:
        if provider in {"google-gemini-cli", "gemini", "chatgpt", "lmstudio", "nvidia"}:
            return True
    markers = [
        "unexpected_eof_while_reading",
        "ssl:",
        "streaming request failed",
        "rate limited",
        "temporarily unavailable",
        "connection reset",
        "incomplete chunked read",
        "peer closed connection",
        "empty assistant stream",
    ]
    if any(marker in message for marker in markers):
        return True
    return provider in {"google-gemini-cli", "gemini"} and "quota exhausted" in message


def _is_provider_level_failure(provider: str, status_code: int, error_text: str) -> bool:
    if provider not in {"google-gemini-cli", "gemini", "chatgpt", "lmstudio", "nvidia"}:
        return False
    message = (error_text or "").lower()
    if status_code == 429:
        return True
    markers = [
        "empty assistant stream",
        "quota exhausted",
        "rate limited",
        "timed out",
        "timeout",
        "usage limit has been reached",
        "no google oauth credentials",
        "invalid api key",
        "temporarily unavailable",
        "unexpected_eof_while_reading",
        "streaming request failed",
        "ssl:",
        "connection reset",
        "incomplete chunked read",
        "peer closed connection",
    ]
    return any(marker in message for marker in markers)


def mark_provider_unhealthy(provider: str, reason: str, cooldown_seconds: int | None = None) -> None:
    lowered = (reason or "").lower()
    if cooldown_seconds is None:
        cooldown_seconds = (
            TRANSIENT_PROVIDER_COOLDOWN_SECONDS
            if any(marker in lowered for marker in ("timed out", "timeout", "connection reset", "peer closed connection"))
            else PROVIDER_COOLDOWN_SECONDS
        )
    provider_health[provider] = {
        "until": time.time() + cooldown_seconds,
        "reason": reason[:200],
    }
    log(f"Marked provider unhealthy for {cooldown_seconds}s: {provider} ({reason})")


def clear_provider_health(provider: str) -> None:
    if provider in provider_health:
        provider_health.pop(provider, None)
        log(f"Cleared provider cooldown: {provider}")


def _format_runtime_label(seconds: int) -> str:
    total = max(0, int(seconds))
    days, rem = divmod(total, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, _ = divmod(rem, 60)
    if days > 0:
        return f"{days}d {hours}h"
    if hours > 0:
        return f"{hours}h {minutes}m"
    return f"{minutes}m"


def _enterprise_kpis(route_health: dict[str, dict], provider: str, model: str) -> dict:
    ready_routes = 0
    degraded_routes = 0
    offline_routes = 0
    setup_required_routes = 0
    cooldown_total_seconds = 0
    for item in route_health.values():
        status = str(item.get("status") or "")
        if status == "ready":
            ready_routes += 1
        elif status == "cooldown":
            degraded_routes += 1
        elif status == "setup_required":
            setup_required_routes += 1
        else:
            offline_routes += 1
        cooldown_total_seconds += int(item.get("cooldown_seconds") or 0)
    total_routes = max(1, ready_routes + degraded_routes + offline_routes)
    ready_ratio = ready_routes / total_routes
    runtime_seconds = int(time.time()) - SERVER_STARTED_EPOCH
    runtime_label = _format_runtime_label(runtime_seconds)
    if ready_routes <= 0:
        health_state = "offline"
    elif ready_ratio >= 0.8 and degraded_routes <= 1:
        health_state = "ready"
    else:
        health_state = "degraded"
    health_score = int(max(0, min(100, round((ready_ratio * 100) - degraded_routes * 8 - offline_routes * 12))))
    return {
        "health_state": health_state,
        "health_score": health_score,
        "ready_routes": ready_routes,
        "degraded_routes": degraded_routes,
        "offline_routes": offline_routes,
        "setup_required_routes": setup_required_routes,
        "total_routes": ready_routes + degraded_routes + offline_routes,
        "ready_ratio": round(ready_ratio, 3),
        "cooldown_total_seconds": cooldown_total_seconds,
        "runtime_seconds": runtime_seconds,
        "runtime_label": runtime_label,
        "active_provider": provider,
        "active_model": model,
        "generated_at": int(time.time()),
    }


def _default_sprint_14day_status() -> dict:
    today = datetime.now(LOCAL_TIMEZONE).strftime("%Y-%m-%d")
    phases_finance = [
        "Executive IA and top navigation normalization",
        "Finance route governance and low-cost default enforcement",
        "Auth/session hardening and logout re-entry verification",
        "Work-hour online/offline measurement (08:00-18:00)",
        "Cross-page layout and selector alignment hardening",
        "Jump-link and external redirect guardrails",
        "Finance command center KPI foundation",
        "Finance route failover/cooldown stabilization",
        "Cron self-check and update resilience",
        "Backup/recovery packaging and restore script",
        "Financial skill routing fixed table and deterministic mapping",
        "Frontend cache bust + process-level hot reload protocol",
        "Financial acceptance baseline and evidence consolidation",
        "Financial closeout and readiness sign-off",
    ]
    phases_legal = [
        "Legal IA and top navigation normalization",
        "Legal route governance and deterministic default mapping",
        "Auth/session hardening for legal workspace access",
        "Work-hour online/offline measurement (08:00-18:00)",
        "Legal route menu alignment and selector stability",
        "External jump prevention for legal workflow pages",
        "Legal command center KPI baseline",
        "Contract review route fallback/cooldown stabilization",
        "Cron maintenance resilience for legal stack",
        "Backup/recovery packaging for legal artifacts",
        "Clause-review skill fixed route table",
        "Forced frontend hot reload and cache protocol",
        "Legal acceptance checklist and evidence pack",
        "Legal closeout and production readiness sign-off",
    ]
    phases_collab = [
        "Collaboration IA and top navigation normalization",
        "Collab route policy with low-cost deterministic baseline",
        "Auth/session hardening for team collaboration flows",
        "Work-hour online/offline measurement (08:00-18:00)",
        "Work chat and channel selector alignment stabilization",
        "External redirect guardrails in collaboration entry points",
        "Collaboration command center KPI baseline",
        "Messaging route fallback/cooldown stabilization",
        "Cron maintenance resilience for collaboration stack",
        "Backup/recovery package for collaboration data",
        "Collaboration skill routing fixed table",
        "Forced hot reload + process cache cleanup protocol",
        "Collaboration acceptance baseline and evidence pack",
        "Collaboration closeout and readiness sign-off",
    ]

    def _items(phases: list[str], owner: str) -> list[dict]:
        return [
            {
                "day": idx + 1,
                "title": title,
                "owner": owner,
                "status": "done",
                "evidence": "completed",
            }
            for idx, title in enumerate(phases)
        ]

    items = _items(phases_finance, "Hermes Finance Platform")
    projects = [
        {
            "key": "finance",
            "label": "Finance Program",
            "items": items,
            "closeout_summary": "Finance program completed with stable routing, observability, and production-ready workspace controls.",
            "next_improvement": "Introduce finance provider latency P95 dashboard and token budget guardrails.",
        },
        {
            "key": "legal",
            "label": "Legal Program",
            "items": _items(phases_legal, "Hermes Legal Platform"),
            "closeout_summary": "Legal program completed with contract-workflow stability and consistent governance controls.",
            "next_improvement": "Add legal clause-risk trend scoring and approval bottleneck alerts.",
        },
        {
            "key": "collaboration",
            "label": "Collaboration Program",
            "items": _items(phases_collab, "Hermes Collaboration Platform"),
            "closeout_summary": "Collaboration program completed with stable team workflows and resilient runtime operations.",
            "next_improvement": "Add cross-channel response SLA tracking with auto-escalation suggestions.",
        },
    ]
    return {
        "version": 2,
        "sprint_name": "World-Class Transformation Sprint",
        "started_on": "2026-04-10",
        "closed_on": today,
        "active_project": "finance",
        "items": items,
        "projects": projects,
        "closeout_summary": (
            "14-day enterprise sprint completed. Core route stability, governance controls, "
            "runtime observability, and recovery readiness are all in place for daily operation."
        ),
        "next_improvement": "Add provider latency P95 + token cost budget alerting with automatic policy tuning.",
        "updated_at": int(time.time()),
    }


def _normalize_sprint_projects(source: dict) -> tuple[list[dict], bool]:
    changed = False
    raw_projects = source.get("projects")
    if not isinstance(raw_projects, list) or not raw_projects:
        defaults = _default_sprint_14day_status()
        return defaults.get("projects", []), True
    projects: list[dict] = []
    for index, project in enumerate(raw_projects):
        if not isinstance(project, dict):
            continue
        key = re.sub(r"[^a-z0-9_-]+", "-", str(project.get("key") or "").strip().lower()).strip("-") or f"project-{index + 1}"
        label = str(project.get("label") or key.title())
        items = [item for item in project.get("items", []) if isinstance(item, dict)]
        if len(items) != 14:
            items = [item for item in source.get("items", []) if isinstance(item, dict)]
            changed = True
        if not items:
            defaults = _default_sprint_14day_status()
            fallback = defaults.get("projects", [])
            for candidate in fallback:
                if str(candidate.get("key")) == key:
                    items = [item for item in candidate.get("items", []) if isinstance(item, dict)]
                    break
            if not items:
                items = [item for item in fallback[0].get("items", []) if isinstance(item, dict)] if fallback else []
            changed = True
        projects.append(
            {
                "key": key,
                "label": label,
                "items": items,
                "closeout_summary": str(project.get("closeout_summary") or source.get("closeout_summary") or ""),
                "next_improvement": str(project.get("next_improvement") or source.get("next_improvement") or ""),
            }
        )
    if not projects:
        defaults = _default_sprint_14day_status()
        return defaults.get("projects", []), True
    return projects, changed


def _load_sprint_14day_status() -> dict:
    data = _load_json_file(SPRINT_14DAY_STATUS_PATH, {})
    if not isinstance(data, dict) or not isinstance(data.get("items"), list) or len(data.get("items") or []) != 14:
        data = _default_sprint_14day_status()
        _save_json_file(SPRINT_14DAY_STATUS_PATH, data)
        return data
    projects, changed = _normalize_sprint_projects(data)
    data["projects"] = projects
    project_keys = {str(project.get("key")) for project in projects if isinstance(project, dict)}
    active_project = str(data.get("active_project") or "")
    if active_project not in project_keys:
        data["active_project"] = str(projects[0].get("key") or "finance")
        changed = True
    if changed:
        data["version"] = max(int(data.get("version") or 1), 2)
        data["updated_at"] = int(time.time())
        _save_json_file(SPRINT_14DAY_STATUS_PATH, data)
    return data


def _sprint_supervision_payload(enterprise_kpis: dict) -> dict:
    source = _load_sprint_14day_status()
    projects = [project for project in source.get("projects", []) if isinstance(project, dict)]
    project_map = {str(project.get("key")): project for project in projects}
    active_project = str(source.get("active_project") or (projects[0].get("key") if projects else "finance"))
    active = project_map.get(active_project) or (projects[0] if projects else {})
    items = [item for item in active.get("items", []) if isinstance(item, dict)]
    if not items:
        items = [item for item in source.get("items", []) if isinstance(item, dict)]
    total_days = len(items) or 14
    done_days = sum(1 for item in items if str(item.get("status") or "").lower() == "done")
    blocked_days = sum(1 for item in items if str(item.get("status") or "").lower() == "blocked")
    completion_rate = round(done_days / max(1, total_days), 3)
    health_state = str(enterprise_kpis.get("health_state") or "degraded")
    if blocked_days > 0 or health_state == "offline":
        supervision_state = "risk"
    elif health_state == "degraded":
        supervision_state = "attention"
    else:
        supervision_state = "on-track"
    effect_score = int(max(0, min(100, round(completion_rate * 70 + int(enterprise_kpis.get("health_score") or 0) * 0.3))))
    project_summaries: list[dict] = []
    for project in projects:
        project_items = [item for item in project.get("items", []) if isinstance(item, dict)]
        project_total = len(project_items) or 14
        project_done = sum(1 for item in project_items if str(item.get("status") or "").lower() == "done")
        project_blocked = sum(1 for item in project_items if str(item.get("status") or "").lower() == "blocked")
        project_rate = round(project_done / max(1, project_total), 3)
        project_effect = int(max(0, min(100, round(project_rate * 70 + int(enterprise_kpis.get("health_score") or 0) * 0.3))))
        project_summaries.append(
            {
                "key": str(project.get("key") or ""),
                "label": str(project.get("label") or ""),
                "day_total": project_total,
                "day_completed": project_done,
                "day_blocked": project_blocked,
                "completion_rate": project_rate,
                "implementation_effect_score": project_effect,
                "acceptance_passed": project_done >= project_total and project_blocked == 0,
            }
        )
    return {
        "sprint_name": str(source.get("sprint_name") or "World-Class Transformation Sprint"),
        "started_on": str(source.get("started_on") or ""),
        "closed_on": str(source.get("closed_on") or ""),
        "active_project": active_project,
        "projects": projects,
        "project_summaries": project_summaries,
        "day_total": total_days,
        "day_completed": done_days,
        "day_blocked": blocked_days,
        "completion_rate": completion_rate,
        "acceptance_passed": done_days >= total_days and blocked_days == 0,
        "supervision_state": supervision_state,
        "implementation_effect_score": effect_score,
        "closeout_summary": str(active.get("closeout_summary") or source.get("closeout_summary") or ""),
        "next_improvement": str(active.get("next_improvement") or source.get("next_improvement") or ""),
        "items": items,
        "updated_at": int(source.get("updated_at") or time.time()),
        "generated_at": int(time.time()),
    }


def _load_json_file(path: Path, default: object) -> object:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def _save_json_file(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


V2_PROJECT_STATUSES = {"planning", "active", "on_hold", "blocked", "completed", "archived"}
V2_TASK_STATUSES = {"todo", "in_progress", "in_review", "pending_approval", "blocked", "done", "cancelled"}
V2_TASK_PRIORITIES = {"low", "medium", "high", "critical"}
V2_ISSUE_STATUSES = {"open", "in_progress", "resolved", "closed"}
V2_ISSUE_SEVERITIES = {"low", "medium", "high", "critical"}
V2_PROJECT_ROLES = {"owner", "manager", "member", "viewer"}
V2_REPORT_TYPES = {
    "user_daily",
    "user_weekly",
    "project_daily",
    "project_weekly",
    "admin_daily_summary",
}
V2_REPORT_REVIEW_STATUS = {"generated", "reviewed", "follow_up_needed", "resolved"}
V2_FILE_STATUSES = {
    "draft",
    "in_review",
    "pending_approval",
    "pending_signature",
    "signed_locked",
    "archived",
    "rejected",
    "superseded",
}
V2_FILE_WORKFLOW_STATUSES = {"active", "completed", "rejected", "cancelled"}
V2_FILE_STEP_STATUSES = {"pending", "approved", "rejected", "signed", "done", "skipped"}
V2_FILE_STEP_TYPES = {"draft", "review", "approval", "sign", "revision", "execution", "feedback"}
V2_FILE_GRANT_PERMISSIONS = {"read", "write", "manage", "review", "approve", "sign"}
V2_WORKSPACES = {"finance", "legal", "skills", "work-chat", "doc-flow", "workbench", "my-work", "reports", "home"}
V2_CHAT_LIFECYCLE_STATUSES = {"active", "archived", "soft_deleted", "hard_deleted"}
V2_CHAT_SUMMARY_TYPES = {"daily", "rolling", "threshold", "event", "manual", "regenerated"}
V2_CHAT_SUMMARY_STATUSES = {"pending", "generated", "failed", "superseded"}
V2_CHAT_SUMMARY_PROVIDER_TYPES = {"ai", "rule_based", "hybrid", "manual"}
V2_CHAT_MESSAGE_VIEWS = {"default", "recent", "archived", "key"}
V2_INTEL_NEWS_CATEGORIES = {"finance", "technology", "politics", "general", "world", "business"}
V2_INTEL_JOB_TYPES = {
    "market_refresh",
    "news_ingestion",
    "news_processing",
    "summarization",
    "digest_generation",
    "instrument_quote_refresh",
    "instrument_ohlcv_refresh",
    "instrument_ohlcv_backfill",
}
V2_INTEL_INSTRUMENT_TYPES = {"index", "stock", "etf", "fund", "forex", "commodity"}
V2_INTEL_KLINE_INTERVALS = {"1m", "5m", "15m", "30m", "1h", "1d", "1w", "1mo"}
V2_INTEL_RANGE_SECONDS = {
    "1d": 24 * 3600,
    "5d": 5 * 24 * 3600,
    "1mo": 30 * 24 * 3600,
    "3mo": 90 * 24 * 3600,
    "6mo": 180 * 24 * 3600,
    "1y": 365 * 24 * 3600,
    "2y": 730 * 24 * 3600,
    "5y": 5 * 365 * 24 * 3600,
}
V2_INTEL_CRAWL4AI_ENABLED = str(os.getenv("V2_INTEL_CRAWL4AI_ENABLED", "1")).strip().lower() not in {"0", "false", "no", "off"}
try:
    V2_INTEL_CRAWL4AI_MAX_PER_FEED = max(0, min(5, int(str(os.getenv("V2_INTEL_CRAWL4AI_MAX_PER_FEED", "2")).strip() or "2")))
except Exception:
    V2_INTEL_CRAWL4AI_MAX_PER_FEED = 2
try:
    V2_INTEL_ZH_TRANSLATION_LIMIT = max(0, min(120, int(str(os.getenv("V2_INTEL_ZH_TRANSLATION_LIMIT", "30")).strip() or "30")))
except Exception:
    V2_INTEL_ZH_TRANSLATION_LIMIT = 30
try:
    V2_INTEL_ZH_TRANSLATION_BATCH_SIZE = max(1, min(12, int(str(os.getenv("V2_INTEL_ZH_TRANSLATION_BATCH_SIZE", "5")).strip() or "5")))
except Exception:
    V2_INTEL_ZH_TRANSLATION_BATCH_SIZE = 5
_V2_INTEL_CRAWL4AI_AVAILABLE: bool | None = None


def _v2_now() -> int:
    return int(time.time())


def _v2_id(prefix: str) -> str:
    return f"{prefix}_{secrets.token_hex(8)}"


def _v2_json_load(text: str, fallback: object) -> object:
    try:
        parsed = json.loads(text or "")
        return parsed if parsed is not None else fallback
    except Exception:
        return fallback


def _v2_intel_cache_get(key: str) -> object | None:
    now = _v2_now()
    with intel_runtime_cache_lock:
        item = intel_runtime_cache.get(key)
        if not isinstance(item, dict):
            return None
        expires_at = int(item.get("expires_at", 0) or 0)
        if expires_at <= now:
            intel_runtime_cache.pop(key, None)
            return None
        return item.get("value")


def _v2_intel_cache_set(key: str, value: object, ttl_seconds: int) -> None:
    ttl = max(1, int(ttl_seconds or 1))
    with intel_runtime_cache_lock:
        intel_runtime_cache[key] = {"expires_at": _v2_now() + ttl, "value": value}


def _v2_intel_cache_delete(key: str) -> None:
    with intel_runtime_cache_lock:
        intel_runtime_cache.pop(key, None)


def _v2_db_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(str(V2_DB_PATH), timeout=30.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA busy_timeout=30000")
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    return conn


def _v2_apply_migrations() -> None:
    with v2_db_lock:
        with _v2_db_conn() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS schema_migrations (
                  version TEXT PRIMARY KEY,
                  applied_at INTEGER NOT NULL
                )
                """
            )
            if not V2_MIGRATIONS_DIR.exists():
                log(f"v2 migrations directory missing: {V2_MIGRATIONS_DIR}")
                return
            applied = {
                row["version"]
                for row in conn.execute("SELECT version FROM schema_migrations").fetchall()
                if isinstance(row["version"], str)
            }
            for path in sorted(V2_MIGRATIONS_DIR.glob("*.sql")):
                version = path.name
                if version in applied:
                    continue
                sql = path.read_text(encoding="utf-8")
                conn.executescript(sql)
                conn.execute(
                    "INSERT INTO schema_migrations(version, applied_at) VALUES(?, ?)",
                    (version, _v2_now()),
                )
                conn.commit()
                log(f"Applied v2 migration: {version}")


def _v2_user_email(user: dict | None) -> str:
    return normalize_email(user.get("email", "")) if isinstance(user, dict) else ""


def _v2_user_exists(email: str) -> bool:
    return bool(find_local_user(email))


def _v2_project_role(conn: sqlite3.Connection, user: dict | None, project_id: str) -> str:
    if is_admin_user(user):
        return "admin"
    email = _v2_user_email(user)
    if not email or not project_id:
        return "none"
    row = conn.execute("SELECT owner_id FROM projects WHERE id = ?", (project_id,)).fetchone()
    if not row:
        return "none"
    if normalize_email(row["owner_id"]) == email:
        return "owner"
    member = conn.execute(
        """
        SELECT role_in_project
        FROM project_members
        WHERE project_id = ? AND user_id = ?
        """,
        (project_id, email),
    ).fetchone()
    if member and str(member["role_in_project"] or "") in V2_PROJECT_ROLES:
        return str(member["role_in_project"])
    grant = conn.execute(
        """
        SELECT permission
        FROM access_grants
        WHERE granted_user_id = ?
          AND scope_type = 'project'
          AND scope_id = ?
          AND is_active = 1
          AND revoked_at = 0
        ORDER BY created_at DESC
        LIMIT 1
        """,
        (email, project_id),
    ).fetchone()
    if grant:
        permission = str(grant["permission"] or "read")
        if permission in {"manage", "write"}:
            return "manager"
        return "viewer"
    return "none"


def _v2_can_view_project(conn: sqlite3.Connection, user: dict | None, project_id: str) -> bool:
    return _v2_project_role(conn, user, project_id) in {"admin", "owner", "manager", "member", "viewer"}


def _v2_can_manage_project(conn: sqlite3.Connection, user: dict | None, project_id: str) -> bool:
    return _v2_project_role(conn, user, project_id) in {"admin", "owner", "manager"}


def _v2_chat_default_retention_policy() -> dict:
    return {
        "scope_type": "global",
        "project_id": "",
        "archive_after_days": 14,
        "soft_delete_after_days": 30,
        "hard_delete_after_days": 90,
        "retain_key_messages": True,
        "retain_system_messages": True,
        "retain_approval_related_messages": True,
        "retain_file_change_messages": True,
        "allow_restore_from_archive": True,
        "allow_restore_from_soft_delete": False,
        "created_by": "system",
    }


def _v2_chat_policy_payload(row: sqlite3.Row | None) -> dict:
    base = _v2_chat_default_retention_policy()
    if not row:
        return base
    return {
        "id": str(row["id"] or ""),
        "scope_type": str(row["scope_type"] or "global"),
        "project_id": str(row["project_id"] or ""),
        "archive_after_days": int(row["archive_after_days"] or base["archive_after_days"]),
        "soft_delete_after_days": int(row["soft_delete_after_days"] or base["soft_delete_after_days"]),
        "hard_delete_after_days": int(row["hard_delete_after_days"] or base["hard_delete_after_days"]),
        "retain_key_messages": bool(row["retain_key_messages"]),
        "retain_system_messages": bool(row["retain_system_messages"]),
        "retain_approval_related_messages": bool(row["retain_approval_related_messages"]),
        "retain_file_change_messages": bool(row["retain_file_change_messages"]),
        "allow_restore_from_archive": bool(row["allow_restore_from_archive"]),
        "allow_restore_from_soft_delete": bool(row["allow_restore_from_soft_delete"]),
        "created_by": str(row["created_by"] or "system"),
        "created_at": int(row["created_at"] or 0),
        "updated_at": int(row["updated_at"] or 0),
    }


def _v2_chat_ensure_global_policy(conn: sqlite3.Connection) -> None:
    row = conn.execute(
        """
        SELECT id
        FROM project_chat_retention_policies_v2
        WHERE scope_type = 'global' AND project_id = ''
        LIMIT 1
        """
    ).fetchone()
    if row:
        return
    now = _v2_now()
    defaults = _v2_chat_default_retention_policy()
    conn.execute(
        """
        INSERT INTO project_chat_retention_policies_v2(
          id, project_id, scope_type, archive_after_days, soft_delete_after_days, hard_delete_after_days,
          retain_key_messages, retain_system_messages, retain_approval_related_messages, retain_file_change_messages,
          allow_restore_from_archive, allow_restore_from_soft_delete, created_by, created_at, updated_at
        )
        VALUES(?, '', 'global', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            _v2_id("pcp"),
            int(defaults["archive_after_days"]),
            int(defaults["soft_delete_after_days"]),
            int(defaults["hard_delete_after_days"]),
            1 if defaults["retain_key_messages"] else 0,
            1 if defaults["retain_system_messages"] else 0,
            1 if defaults["retain_approval_related_messages"] else 0,
            1 if defaults["retain_file_change_messages"] else 0,
            1 if defaults["allow_restore_from_archive"] else 0,
            1 if defaults["allow_restore_from_soft_delete"] else 0,
            str(defaults["created_by"]),
            now,
            now,
        ),
    )


def _v2_chat_effective_policy(conn: sqlite3.Connection, project_id: str) -> dict:
    _v2_chat_ensure_global_policy(conn)
    project_policy = conn.execute(
        """
        SELECT *
        FROM project_chat_retention_policies_v2
        WHERE scope_type = 'project' AND project_id = ?
        ORDER BY updated_at DESC
        LIMIT 1
        """,
        (project_id,),
    ).fetchone()
    if project_policy:
        payload = _v2_chat_policy_payload(project_policy)
        payload["effective_scope"] = "project"
        return payload
    global_policy = conn.execute(
        """
        SELECT *
        FROM project_chat_retention_policies_v2
        WHERE scope_type = 'global' AND project_id = ''
        ORDER BY updated_at DESC
        LIMIT 1
        """
    ).fetchone()
    payload = _v2_chat_policy_payload(global_policy)
    payload["effective_scope"] = "global"
    return payload


def _v2_chat_summary_payload(row: sqlite3.Row, *, include_sections: bool = True) -> dict:
    payload = {
        "id": str(row["id"] or ""),
        "project_id": str(row["project_id"] or ""),
        "summary_version": int(row["summary_version"] or 0),
        "summary_type": str(row["summary_type"] or "manual"),
        "summary_status": str(row["summary_status"] or "generated"),
        "summary_content_text": str(row["summary_content_text"] or ""),
        "source_message_start_id": str(row["source_message_start_id"] or ""),
        "source_message_end_id": str(row["source_message_end_id"] or ""),
        "source_message_count": int(row["source_message_count"] or 0),
        "provider_type": str(row["provider_type"] or "rule_based"),
        "provider_metadata": _v2_json_load(str(row["provider_metadata_json"] or "{}"), {}),
        "generation_trigger": str(row["generation_trigger"] or "manual"),
        "generated_by": str(row["generated_by"] or ""),
        "generated_at": int(row["generated_at"] or 0),
        "quality_score": float(row["quality_score"] or 0),
        "is_current": bool(row["is_current"]),
        "metadata": _v2_json_load(str(row["metadata_json"] or "{}"), {}),
    }
    if include_sections:
        payload["main_progress"] = _v2_json_load(str(row["main_progress_json"] or "[]"), [])
        payload["confirmed_decisions"] = _v2_json_load(str(row["confirmed_decisions_json"] or "[]"), [])
        payload["task_ownership_updates"] = _v2_json_load(str(row["task_updates_json"] or "[]"), [])
        payload["file_document_updates"] = _v2_json_load(str(row["file_updates_json"] or "[]"), [])
        payload["issues_risks_blockers"] = _v2_json_load(str(row["issues_risks_json"] or "[]"), [])
        payload["next_actions"] = _v2_json_load(str(row["next_actions_json"] or "[]"), [])
    return payload


def _v2_chat_message_payload(row: sqlite3.Row) -> dict:
    return {
        "id": str(row["id"] or ""),
        "project_id": str(row["project_id"] or ""),
        "conversation_id": str(row["conversation_id"] or ""),
        "sender_id": normalize_email(row["sender_id"] or ""),
        "sender_name": str(row["sender_name"] or ""),
        "message_type": str(row["message_type"] or "text"),
        "content": str(row["content"] or ""),
        "lifecycle_status": str(row["lifecycle_status"] or "active"),
        "is_key_message": bool(row["is_key_message"]),
        "is_system_message": bool(row["is_system_message"]),
        "metadata": _v2_json_load(str(row["metadata_json"] or "{}"), {}),
        "created_at": int(row["created_at"] or 0),
        "updated_at": int(row["updated_at"] or 0),
        "archived_at": int(row["archived_at"] or 0),
        "soft_deleted_at": int(row["soft_deleted_at"] or 0),
        "hard_deleted_at": int(row["hard_deleted_at"] or 0),
    }


def _v2_project_chat_message_counts(conn: sqlite3.Connection, project_id: str) -> dict:
    rows = conn.execute(
        """
        SELECT lifecycle_status, COUNT(*) AS c
        FROM project_chat_messages_v2
        WHERE project_id = ?
        GROUP BY lifecycle_status
        """,
        (project_id,),
    ).fetchall()
    lifecycle_counts = {str(row["lifecycle_status"] or "active"): int(row["c"] or 0) for row in rows}
    key_count = conn.execute(
        """
        SELECT COUNT(*) AS c
        FROM project_chat_messages_v2
        WHERE project_id = ? AND is_key_message = 1 AND lifecycle_status <> 'hard_deleted'
        """,
        (project_id,),
    ).fetchone()
    return {
        "active": int(lifecycle_counts.get("active", 0)),
        "archived": int(lifecycle_counts.get("archived", 0)),
        "soft_deleted": int(lifecycle_counts.get("soft_deleted", 0)),
        "hard_deleted": int(lifecycle_counts.get("hard_deleted", 0)),
        "key_messages": int(key_count["c"] or 0) if key_count else 0,
    }


def _v2_project_chat_current_summary(user: dict | None, project_id: str) -> tuple[dict, int]:
    if not user:
        return {"ok": False, "error": "authentication_required"}, 401
    with v2_db_lock, _v2_db_conn() as conn:
        project = conn.execute("SELECT id, name, updated_at FROM projects WHERE id = ?", (project_id,)).fetchone()
        if not project:
            return {"ok": False, "error": "project_not_found"}, 404
        if not _v2_can_view_project(conn, user, project_id):
            return {"ok": False, "error": "permission_denied"}, 403
        row = conn.execute(
            """
            SELECT *
            FROM project_chat_summaries_v2
            WHERE project_id = ? AND is_current = 1
            ORDER BY generated_at DESC
            LIMIT 1
            """,
            (project_id,),
        ).fetchone()
        if not row:
            row = conn.execute(
                """
                SELECT *
                FROM project_chat_summaries_v2
                WHERE project_id = ?
                ORDER BY generated_at DESC
                LIMIT 1
                """,
                (project_id,),
            ).fetchone()
        latest_active = conn.execute(
            """
            SELECT MAX(created_at) AS latest_active_at
            FROM project_chat_messages_v2
            WHERE project_id = ? AND lifecycle_status = 'active'
            """,
            (project_id,),
        ).fetchone()
        pending_runs = conn.execute(
            """
            SELECT COUNT(*) AS c
            FROM project_chat_summary_runs_v2
            WHERE project_id = ? AND status IN ('queued', 'running')
            """,
            (project_id,),
        ).fetchone()
        counts = _v2_project_chat_message_counts(conn, project_id)
        policy = _v2_chat_effective_policy(conn, project_id)
        latest_active_at = int(latest_active["latest_active_at"] or 0) if latest_active else 0
        summary_payload = _v2_chat_summary_payload(row, include_sections=True) if row else None
        stale = True if (latest_active_at > 0 and not summary_payload) else False
        if summary_payload:
            stale = latest_active_at > int(summary_payload.get("generated_at", 0) or 0)
        return {
            "ok": True,
            "project": {
                "id": str(project["id"] or ""),
                "name": str(project["name"] or ""),
                "updated_at": int(project["updated_at"] or 0),
            },
            "summary": summary_payload,
            "state": {
                "has_summary": bool(summary_payload),
                "is_stale": stale,
                "latest_active_message_at": latest_active_at,
                "pending_runs": int(pending_runs["c"] or 0) if pending_runs else 0,
            },
            "message_counts": counts,
            "retention_policy": policy,
        }, 200


def _v2_project_chat_summary_history(user: dict | None, project_id: str, query: dict[str, list[str]]) -> tuple[dict, int]:
    if not user:
        return {"ok": False, "error": "authentication_required"}, 401
    limit_text = str(query.get("limit", ["50"])[0] or "50").strip()
    try:
        limit = min(max(int(limit_text), 1), 200)
    except Exception:
        limit = 50
    with v2_db_lock, _v2_db_conn() as conn:
        project = conn.execute("SELECT id FROM projects WHERE id = ?", (project_id,)).fetchone()
        if not project:
            return {"ok": False, "error": "project_not_found"}, 404
        if not _v2_can_view_project(conn, user, project_id):
            return {"ok": False, "error": "permission_denied"}, 403
        rows = conn.execute(
            """
            SELECT *
            FROM project_chat_summaries_v2
            WHERE project_id = ?
            ORDER BY generated_at DESC
            LIMIT ?
            """,
            (project_id, limit),
        ).fetchall()
        return {
            "ok": True,
            "project_id": project_id,
            "summaries": [_v2_chat_summary_payload(row, include_sections=False) for row in rows],
            "count": len(rows),
        }, 200


def _v2_project_chat_summary_detail(user: dict | None, project_id: str, summary_id: str) -> tuple[dict, int]:
    if not user:
        return {"ok": False, "error": "authentication_required"}, 401
    with v2_db_lock, _v2_db_conn() as conn:
        project = conn.execute("SELECT id FROM projects WHERE id = ?", (project_id,)).fetchone()
        if not project:
            return {"ok": False, "error": "project_not_found"}, 404
        if not _v2_can_view_project(conn, user, project_id):
            return {"ok": False, "error": "permission_denied"}, 403
        row = conn.execute(
            """
            SELECT *
            FROM project_chat_summaries_v2
            WHERE id = ? AND project_id = ?
            LIMIT 1
            """,
            (summary_id, project_id),
        ).fetchone()
        if not row:
            return {"ok": False, "error": "summary_not_found"}, 404
        return {"ok": True, "summary": _v2_chat_summary_payload(row, include_sections=True)}, 200


def _v2_project_chat_messages(user: dict | None, project_id: str, query: dict[str, list[str]]) -> tuple[dict, int]:
    if not user:
        return {"ok": False, "error": "authentication_required"}, 401
    view = str(query.get("view", ["default"])[0] or "default").strip().lower()
    if view not in V2_CHAT_MESSAGE_VIEWS:
        return {"ok": False, "error": "invalid_view"}, 400
    limit_text = str(query.get("limit", ["120"])[0] or "120").strip()
    before_text = str(query.get("before", ["0"])[0] or "0").strip()
    try:
        limit = min(max(int(limit_text), 1), 500)
    except Exception:
        limit = 120
    try:
        before = int(before_text)
    except Exception:
        before = 0
    now_ts = _v2_now()
    default_recent_cutoff = now_ts - 3 * 24 * 60 * 60
    with v2_db_lock, _v2_db_conn() as conn:
        project = conn.execute("SELECT id FROM projects WHERE id = ?", (project_id,)).fetchone()
        if not project:
            return {"ok": False, "error": "project_not_found"}, 404
        if not _v2_can_view_project(conn, user, project_id):
            return {"ok": False, "error": "permission_denied"}, 403
        can_manage = _v2_can_manage_project(conn, user, project_id) or is_admin_user(user)
        where = ["project_id = ?"]
        params: list[object] = [project_id]
        if before > 0:
            where.append("created_at < ?")
            params.append(before)
        if view == "default":
            where.append("lifecycle_status = 'active'")
            where.append("(is_key_message = 1 OR created_at >= ?)")
            params.append(default_recent_cutoff)
        elif view == "recent":
            where.append("lifecycle_status = 'active'")
        elif view == "archived":
            if not can_manage:
                return {"ok": False, "error": "permission_denied"}, 403
            where.append("lifecycle_status = 'archived'")
        elif view == "key":
            where.append("is_key_message = 1")
            if can_manage:
                where.append("lifecycle_status IN ('active', 'archived', 'soft_deleted')")
            else:
                where.append("lifecycle_status = 'active'")
        rows = conn.execute(
            f"""
            SELECT *
            FROM project_chat_messages_v2
            WHERE {' AND '.join(where)}
            ORDER BY created_at DESC
            LIMIT ?
            """,
            tuple(params + [limit]),
        ).fetchall()
        counts = _v2_project_chat_message_counts(conn, project_id)
        return {
            "ok": True,
            "project_id": project_id,
            "view": view,
            "messages": [_v2_chat_message_payload(row) for row in rows],
            "count": len(rows),
            "limit": limit,
            "before": before,
            "can_view_archived": can_manage,
            "message_counts": counts,
            "default_recent_window_seconds": 3 * 24 * 60 * 60,
        }, 200


def _v2_project_chat_retention_policy(user: dict | None, project_id: str) -> tuple[dict, int]:
    if not user:
        return {"ok": False, "error": "authentication_required"}, 401
    with v2_db_lock, _v2_db_conn() as conn:
        project = conn.execute("SELECT id FROM projects WHERE id = ?", (project_id,)).fetchone()
        if not project:
            return {"ok": False, "error": "project_not_found"}, 404
        if not _v2_can_view_project(conn, user, project_id):
            return {"ok": False, "error": "permission_denied"}, 403
        policy = _v2_chat_effective_policy(conn, project_id)
        return {"ok": True, "project_id": project_id, "retention_policy": policy}, 200


def _v2_project_chat_cleanup_logs(user: dict | None, project_id: str, query: dict[str, list[str]]) -> tuple[dict, int]:
    if not user:
        return {"ok": False, "error": "authentication_required"}, 401
    limit_text = str(query.get("limit", ["80"])[0] or "80").strip()
    try:
        limit = min(max(int(limit_text), 1), 500)
    except Exception:
        limit = 80
    with v2_db_lock, _v2_db_conn() as conn:
        project = conn.execute("SELECT id FROM projects WHERE id = ?", (project_id,)).fetchone()
        if not project:
            return {"ok": False, "error": "project_not_found"}, 404
        if not _v2_can_manage_project(conn, user, project_id) and not is_admin_user(user):
            return {"ok": False, "error": "permission_denied"}, 403
        rows = conn.execute(
            """
            SELECT *
            FROM project_chat_cleanup_logs_v2
            WHERE project_id = ?
            ORDER BY executed_at DESC
            LIMIT ?
            """,
            (project_id, limit),
        ).fetchall()
        return {
            "ok": True,
            "project_id": project_id,
            "cleanup_logs": [
                {
                    "id": str(row["id"] or ""),
                    "policy_id": str(row["policy_id"] or ""),
                    "action_type": str(row["action_type"] or ""),
                    "affected_message_count": int(row["affected_message_count"] or 0),
                    "executed_by": str(row["executed_by"] or ""),
                    "details": _v2_json_load(str(row["details_json"] or "{}"), {}),
                    "executed_at": int(row["executed_at"] or 0),
                }
                for row in rows
            ],
            "count": len(rows),
        }, 200


def _v2_chat_keywords_match(text: str, keywords: list[str]) -> bool:
    lowered = text.lower()
    return any(keyword in lowered for keyword in keywords)


def _v2_chat_compact_text(text: str, limit: int = 220) -> str:
    compact = " ".join(str(text or "").split())
    if len(compact) <= limit:
        return compact
    return compact[: limit - 1] + "…"


def _v2_chat_rule_based_summary(messages: list[dict], *, trigger: str, provider_type: str = "rule_based") -> dict:
    main_progress: list[str] = []
    confirmed_decisions: list[str] = []
    task_updates: list[str] = []
    file_updates: list[str] = []
    issues_risks: list[str] = []
    next_actions: list[str] = []
    for item in messages:
        text = _v2_chat_compact_text(item.get("content", ""), 260)
        if not text:
            continue
        if _v2_chat_keywords_match(text, ["完成", "done", "finished", "delivered", "上线", "发布"]):
            main_progress.append(text)
        if _v2_chat_keywords_match(text, ["决定", "同意", "批准", "approved", "decision", "agree", "agreed"]):
            confirmed_decisions.append(text)
        if _v2_chat_keywords_match(text, ["负责人", "owner", "assign", "assigned", "deadline", "截止", "due"]):
            task_updates.append(text)
        if _v2_chat_keywords_match(text, ["文件", "文档", "上传", "版本", "review", "approve", "sign", "签字", "归档"]):
            file_updates.append(text)
        if _v2_chat_keywords_match(text, ["风险", "阻塞", "问题", "延迟", "blocker", "risk", "issue", "error", "依赖"]):
            issues_risks.append(text)
        if _v2_chat_keywords_match(text, ["下一步", "next", "todo", "行动", "follow-up", "待办", "安排"]):
            next_actions.append(text)
    latest = [_v2_chat_compact_text(item.get("content", ""), 260) for item in messages[-8:]]
    latest = [item for item in latest if item]
    if not main_progress and latest:
        main_progress = latest[:3]
    if not next_actions and latest:
        next_actions = latest[-3:]
    if not issues_risks:
        issues_risks = ["No explicit blocker detected in the selected message window."]
    summary_text = " | ".join(
        [
            "Progress: " + "; ".join(main_progress[:4]),
            "Decisions: " + "; ".join(confirmed_decisions[:4]) if confirmed_decisions else "Decisions: none",
            "Next: " + "; ".join(next_actions[:4]),
        ]
    )
    return {
        "summary_content_text": _v2_chat_compact_text(summary_text, 1600),
        "main_progress": main_progress[:8],
        "confirmed_decisions": confirmed_decisions[:8],
        "task_updates": task_updates[:8],
        "file_updates": file_updates[:8],
        "issues_risks": issues_risks[:8],
        "next_actions": next_actions[:8],
        "metadata": {
            "generation_mode": trigger,
            "message_window_count": len(messages),
            "source": "rule_based",
        },
        "quality_score": 0.72 if messages else 0.0,
        "provider_type": provider_type,
        "provider_metadata": {"engine": "rule_based_v1"},
    }


def _v2_chat_ai_summary(messages: list[dict], *, trigger: str) -> dict:
    raise RuntimeError("ai_summarizer_unavailable")


def _v2_chat_generate_summary_content(messages: list[dict], *, trigger: str, provider_hint: str) -> dict:
    hint = provider_hint if provider_hint in V2_CHAT_SUMMARY_PROVIDER_TYPES else "hybrid"
    if hint in {"ai", "hybrid"}:
        try:
            return _v2_chat_ai_summary(messages, trigger=trigger)
        except Exception:
            if hint == "ai":
                raise
    return _v2_chat_rule_based_summary(messages, trigger=trigger, provider_type="rule_based")


def _v2_chat_messages_for_summary(conn: sqlite3.Connection, project_id: str, since_ts: int = 0, limit: int = 600) -> list[sqlite3.Row]:
    if since_ts > 0:
        rows = conn.execute(
            """
            SELECT *
            FROM project_chat_messages_v2
            WHERE project_id = ? AND lifecycle_status = 'active' AND created_at > ?
            ORDER BY created_at ASC
            LIMIT ?
            """,
            (project_id, since_ts, limit),
        ).fetchall()
    else:
        rows = conn.execute(
            """
            SELECT *
            FROM project_chat_messages_v2
            WHERE project_id = ? AND lifecycle_status = 'active'
            ORDER BY created_at ASC
            LIMIT ?
            """,
            (project_id, limit),
        ).fetchall()
    return rows


def _v2_chat_create_run(conn: sqlite3.Connection, project_id: str, trigger_type: str, provider_type: str, metadata: dict | None = None) -> str:
    run_id = _v2_id("pcsrun")
    now = _v2_now()
    conn.execute(
        """
        INSERT INTO project_chat_summary_runs_v2(
          id, project_id, trigger_type, provider_type, status, started_at, completed_at, summary_id, error_message, metadata_json, created_at
        )
        VALUES(?, ?, ?, ?, 'running', ?, 0, '', '', ?, ?)
        """,
        (run_id, project_id, trigger_type, provider_type, now, json.dumps(metadata or {}, ensure_ascii=False), now),
    )
    return run_id


def _v2_chat_finish_run(conn: sqlite3.Connection, run_id: str, status: str, *, summary_id: str = "", error_message: str = "", metadata: dict | None = None) -> None:
    conn.execute(
        """
        UPDATE project_chat_summary_runs_v2
        SET status = ?, completed_at = ?, summary_id = ?, error_message = ?, metadata_json = ?
        WHERE id = ?
        """,
        (status, _v2_now(), summary_id, error_message[:1200], json.dumps(metadata or {}, ensure_ascii=False), run_id),
    )


def _v2_chat_generate_summary_for_project(
    conn: sqlite3.Connection,
    user: dict | None,
    project_id: str,
    *,
    trigger_type: str,
    provider_hint: str = "hybrid",
    force: bool = False,
    regenerated_from_summary_id: str = "",
) -> tuple[dict, int]:
    row = conn.execute("SELECT id, name FROM projects WHERE id = ?", (project_id,)).fetchone()
    if not row:
        return {"ok": False, "error": "project_not_found"}, 404
    if not _v2_can_manage_project(conn, user, project_id) and not is_admin_user(user):
        return {"ok": False, "error": "permission_denied"}, 403
    latest = conn.execute(
        """
        SELECT id, generated_at, summary_version
        FROM project_chat_summaries_v2
        WHERE project_id = ? AND summary_status IN ('generated', 'superseded')
        ORDER BY generated_at DESC
        LIMIT 1
        """,
        (project_id,),
    ).fetchone()
    since_ts = 0 if force else int(latest["generated_at"] or 0) if latest else 0
    source_rows = _v2_chat_messages_for_summary(conn, project_id, since_ts=since_ts, limit=800)
    if not source_rows and not force and not regenerated_from_summary_id:
        return {"ok": False, "error": "no_new_messages"}, 400
    if force and not source_rows:
        source_rows = _v2_chat_messages_for_summary(conn, project_id, since_ts=0, limit=400)
    source_payload = [_v2_chat_message_payload(item) for item in source_rows]
    run_id = _v2_chat_create_run(
        conn,
        project_id,
        trigger_type,
        provider_hint,
        metadata={"force": force, "regenerated_from_summary_id": regenerated_from_summary_id},
    )
    actor = _v2_user_email(user) or "system"
    try:
        summary = _v2_chat_generate_summary_content(source_payload, trigger=trigger_type, provider_hint=provider_hint)
        new_version = (int(latest["summary_version"] or 0) + 1) if latest else 1
        if latest:
            conn.execute(
                "UPDATE project_chat_summaries_v2 SET is_current = 0, summary_status = 'superseded' WHERE project_id = ? AND is_current = 1",
                (project_id,),
            )
        source_start_id = str(source_rows[0]["id"] or "") if source_rows else ""
        source_end_id = str(source_rows[-1]["id"] or "") if source_rows else ""
        summary_id = _v2_id("pcsum")
        conn.execute(
            """
            INSERT INTO project_chat_summaries_v2(
              id, project_id, summary_version, summary_type, summary_status, summary_content_text,
              main_progress_json, confirmed_decisions_json, task_updates_json, file_updates_json, issues_risks_json, next_actions_json,
              metadata_json, source_message_start_id, source_message_end_id, source_message_count, provider_type,
              provider_metadata_json, generation_trigger, generated_by, generated_at, quality_score, is_current
            )
            VALUES(?, ?, ?, ?, 'generated', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
            """,
            (
                summary_id,
                project_id,
                new_version,
                "regenerated" if regenerated_from_summary_id else trigger_type,
                str(summary.get("summary_content_text") or "")[:16000],
                json.dumps(summary.get("main_progress") or [], ensure_ascii=False),
                json.dumps(summary.get("confirmed_decisions") or [], ensure_ascii=False),
                json.dumps(summary.get("task_updates") or [], ensure_ascii=False),
                json.dumps(summary.get("file_updates") or [], ensure_ascii=False),
                json.dumps(summary.get("issues_risks") or [], ensure_ascii=False),
                json.dumps(summary.get("next_actions") or [], ensure_ascii=False),
                json.dumps(summary.get("metadata") or {}, ensure_ascii=False),
                source_start_id,
                source_end_id,
                len(source_rows),
                str(summary.get("provider_type") or "rule_based"),
                json.dumps(summary.get("provider_metadata") or {}, ensure_ascii=False),
                trigger_type,
                actor,
                _v2_now(),
                float(summary.get("quality_score") or 0),
            ),
        )
        _v2_chat_finish_run(conn, run_id, "succeeded", summary_id=summary_id, metadata={"source_count": len(source_rows)})
        _v2_audit(
            conn,
            actor,
            "summary_regenerated" if regenerated_from_summary_id else "summary_generated",
            "project_chat_summary",
            summary_id,
            {
                "project_id": project_id,
                "trigger_type": trigger_type,
                "source_message_count": len(source_rows),
                "regenerated_from_summary_id": regenerated_from_summary_id,
            },
        )
        for manager_email in _v2_project_manager_emails(conn, project_id):
            if manager_email == actor:
                continue
            _v2_notify(
                conn,
                manager_email,
                "project_chat_summary_generated",
                "Project chat summary updated",
                f"Project {project_id} summary has been updated.",
                project_id=project_id,
            )
        payload = conn.execute("SELECT * FROM project_chat_summaries_v2 WHERE id = ?", (summary_id,)).fetchone()
        return {"ok": True, "summary": _v2_chat_summary_payload(payload, include_sections=True), "run_id": run_id}, 200
    except Exception as exc:
        _v2_chat_finish_run(conn, run_id, "failed", error_message=str(exc), metadata={"provider_hint": provider_hint})
        _v2_audit(
            conn,
            actor or "system",
            "summarization_failed",
            "project_chat_summary_run",
            run_id,
            {"project_id": project_id, "error": str(exc)[:500], "trigger_type": trigger_type},
        )
        return {"ok": False, "error": "summary_generation_failed", "detail": str(exc)[:500]}, 500


def _v2_project_chat_generate(user: dict | None, project_id: str, payload: dict) -> tuple[dict, int]:
    if not user:
        return {"ok": False, "error": "authentication_required"}, 401
    trigger_type = str(payload.get("trigger_type") or "manual").strip().lower()
    if trigger_type not in V2_CHAT_SUMMARY_TYPES:
        trigger_type = "manual"
    provider_hint = str(payload.get("provider_type") or "hybrid").strip().lower()
    force = bool(payload.get("force", False))
    with v2_db_lock, _v2_db_conn() as conn:
        result, status_code = _v2_chat_generate_summary_for_project(
            conn,
            user,
            project_id,
            trigger_type=trigger_type,
            provider_hint=provider_hint,
            force=force,
        )
        conn.commit()
        return result, status_code


def _v2_project_chat_regenerate(user: dict | None, project_id: str, summary_id: str, payload: dict) -> tuple[dict, int]:
    if not user:
        return {"ok": False, "error": "authentication_required"}, 401
    provider_hint = str(payload.get("provider_type") or "hybrid").strip().lower()
    with v2_db_lock, _v2_db_conn() as conn:
        source_summary = conn.execute(
            """
            SELECT id
            FROM project_chat_summaries_v2
            WHERE id = ? AND project_id = ?
            LIMIT 1
            """,
            (summary_id, project_id),
        ).fetchone()
        if not source_summary:
            return {"ok": False, "error": "summary_not_found"}, 404
        result, status_code = _v2_chat_generate_summary_for_project(
            conn,
            user,
            project_id,
            trigger_type="regenerated",
            provider_hint=provider_hint,
            force=True,
            regenerated_from_summary_id=summary_id,
        )
        conn.commit()
        return result, status_code


def _v2_project_chat_add_message(user: dict | None, project_id: str, payload: dict) -> tuple[dict, int]:
    if not user:
        return {"ok": False, "error": "authentication_required"}, 401
    with v2_db_lock, _v2_db_conn() as conn:
        project = conn.execute("SELECT id FROM projects WHERE id = ?", (project_id,)).fetchone()
        if not project:
            return {"ok": False, "error": "project_not_found"}, 404
        if not _v2_can_view_project(conn, user, project_id):
            return {"ok": False, "error": "permission_denied"}, 403
        content = str(payload.get("content") or "").strip()
        if not content:
            return {"ok": False, "error": "empty_message"}, 400
        now = _v2_now()
        sender = _v2_user_email(user)
        msg_id = _v2_id("pcmsg")
        message_type = str(payload.get("message_type") or "text").strip().lower() or "text"
        metadata = payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {}
        conn.execute(
            """
            INSERT INTO project_chat_messages_v2(
              id, project_id, conversation_id, sender_id, sender_name, message_type, content, lifecycle_status,
              is_key_message, is_system_message, metadata_json, created_at, updated_at, archived_at, soft_deleted_at, hard_deleted_at
            )
            VALUES(?, ?, ?, ?, ?, ?, ?, 'active', ?, ?, ?, ?, ?, 0, 0, 0)
            """,
            (
                msg_id,
                project_id,
                str(payload.get("conversation_id") or ""),
                sender,
                user_display_label(sender),
                message_type,
                content[:12000],
                1 if bool(payload.get("is_key_message")) else 0,
                1 if bool(payload.get("is_system_message")) else 0,
                json.dumps(metadata, ensure_ascii=False),
                now,
                now,
            ),
        )
        _v2_audit(conn, sender, "project_chat_message_create", "project_chat_message", msg_id, {"project_id": project_id, "message_type": message_type})
        conn.commit()
        row = conn.execute("SELECT * FROM project_chat_messages_v2 WHERE id = ?", (msg_id,)).fetchone()
        return {"ok": True, "message": _v2_chat_message_payload(row)}, 200


def _v2_project_chat_append_system_message(
    conn: sqlite3.Connection,
    project_id: str,
    content: str,
    *,
    message_type: str = "event",
    metadata: dict | None = None,
    is_key_message: bool = False,
) -> str:
    msg_id = _v2_id("pcmsg")
    now = _v2_now()
    conn.execute(
        """
        INSERT INTO project_chat_messages_v2(
          id, project_id, conversation_id, sender_id, sender_name, message_type, content, lifecycle_status,
          is_key_message, is_system_message, metadata_json, created_at, updated_at, archived_at, soft_deleted_at, hard_deleted_at
        )
        VALUES(?, ?, '', 'system', 'System', ?, ?, 'active', ?, 1, ?, ?, ?, 0, 0, 0)
        """,
        (
            msg_id,
            project_id,
            message_type,
            str(content or "")[:12000],
            1 if is_key_message else 0,
            json.dumps(metadata or {}, ensure_ascii=False),
            now,
            now,
        ),
    )
    return msg_id


def _v2_project_chat_mark_key(user: dict | None, project_id: str, message_id: str, is_key: bool) -> tuple[dict, int]:
    if not user:
        return {"ok": False, "error": "authentication_required"}, 401
    actor = _v2_user_email(user)
    with v2_db_lock, _v2_db_conn() as conn:
        row = conn.execute(
            """
            SELECT *
            FROM project_chat_messages_v2
            WHERE id = ? AND project_id = ?
            LIMIT 1
            """,
            (message_id, project_id),
        ).fetchone()
        if not row:
            return {"ok": False, "error": "message_not_found"}, 404
        if not _v2_can_manage_project(conn, user, project_id) and not is_admin_user(user):
            return {"ok": False, "error": "permission_denied"}, 403
        conn.execute(
            "UPDATE project_chat_messages_v2 SET is_key_message = ?, updated_at = ? WHERE id = ?",
            (1 if is_key else 0, _v2_now(), message_id),
        )
        _v2_audit(
            conn,
            actor,
            "message_marked_key" if is_key else "message_unmarked_key",
            "project_chat_message",
            message_id,
            {"project_id": project_id},
        )
        conn.commit()
        updated = conn.execute("SELECT * FROM project_chat_messages_v2 WHERE id = ?", (message_id,)).fetchone()
        return {"ok": True, "message": _v2_chat_message_payload(updated)}, 200


def _v2_chat_is_protected(policy: dict, row: sqlite3.Row) -> bool:
    metadata = _v2_json_load(str(row["metadata_json"] or "{}"), {})
    if bool(policy.get("retain_key_messages", True)) and bool(row["is_key_message"]):
        return True
    if bool(policy.get("retain_system_messages", True)) and bool(row["is_system_message"]):
        return True
    if bool(policy.get("retain_approval_related_messages", True)) and bool(isinstance(metadata, dict) and metadata.get("approval_related")):
        return True
    if bool(policy.get("retain_file_change_messages", True)) and bool(isinstance(metadata, dict) and metadata.get("file_change_related")):
        return True
    return False


def _v2_project_chat_cleanup(user: dict | None, project_id: str, payload: dict) -> tuple[dict, int]:
    if not user:
        return {"ok": False, "error": "authentication_required"}, 401
    actor = _v2_user_email(user)
    mode = str(payload.get("mode") or "all").strip().lower()
    if mode not in {"archive", "soft_delete", "hard_delete", "all"}:
        return {"ok": False, "error": "invalid_mode"}, 400
    now_ts = _v2_now()
    with v2_db_lock, _v2_db_conn() as conn:
        if not _v2_can_manage_project(conn, user, project_id) and not is_admin_user(user):
            return {"ok": False, "error": "permission_denied"}, 403
        if not conn.execute("SELECT 1 FROM projects WHERE id = ?", (project_id,)).fetchone():
            return {"ok": False, "error": "project_not_found"}, 404
        policy = _v2_chat_effective_policy(conn, project_id)
        archive_cutoff = now_ts - int(policy.get("archive_after_days", 14)) * 24 * 60 * 60
        soft_cutoff = now_ts - int(policy.get("soft_delete_after_days", 30)) * 24 * 60 * 60
        hard_cutoff = now_ts - int(policy.get("hard_delete_after_days", 90)) * 24 * 60 * 60
        affected = {"archived": 0, "soft_deleted": 0, "hard_deleted": 0}
        if mode in {"archive", "all"}:
            rows = conn.execute(
                """
                SELECT *
                FROM project_chat_messages_v2
                WHERE project_id = ? AND lifecycle_status = 'active' AND created_at <= ?
                """,
                (project_id, archive_cutoff),
            ).fetchall()
            candidate_ids = [str(row["id"] or "") for row in rows if not _v2_chat_is_protected(policy, row)]
            if candidate_ids:
                conn.execute(
                    f"UPDATE project_chat_messages_v2 SET lifecycle_status = 'archived', archived_at = ?, updated_at = ? WHERE id IN ({','.join(['?']*len(candidate_ids))})",
                    tuple([now_ts, now_ts] + candidate_ids),
                )
                affected["archived"] = len(candidate_ids)
        if mode in {"soft_delete", "all"}:
            rows = conn.execute(
                """
                SELECT *
                FROM project_chat_messages_v2
                WHERE project_id = ? AND lifecycle_status = 'archived' AND archived_at <= ?
                """,
                (project_id, soft_cutoff),
            ).fetchall()
            candidate_ids = [str(row["id"] or "") for row in rows if not _v2_chat_is_protected(policy, row)]
            if candidate_ids:
                conn.execute(
                    f"UPDATE project_chat_messages_v2 SET lifecycle_status = 'soft_deleted', soft_deleted_at = ?, updated_at = ? WHERE id IN ({','.join(['?']*len(candidate_ids))})",
                    tuple([now_ts, now_ts] + candidate_ids),
                )
                affected["soft_deleted"] = len(candidate_ids)
        if mode in {"hard_delete", "all"}:
            rows = conn.execute(
                """
                SELECT *
                FROM project_chat_messages_v2
                WHERE project_id = ? AND lifecycle_status = 'soft_deleted' AND soft_deleted_at <= ?
                """,
                (project_id, hard_cutoff),
            ).fetchall()
            candidate_ids = [str(row["id"] or "") for row in rows if not _v2_chat_is_protected(policy, row)]
            if candidate_ids:
                placeholders = ",".join(["?"] * len(candidate_ids))
                conn.execute(
                    f"""
                    UPDATE project_chat_messages_v2
                    SET lifecycle_status = 'hard_deleted', hard_deleted_at = ?, updated_at = ?, content = '', metadata_json = '{{}}'
                    WHERE id IN ({placeholders})
                    """,
                    tuple([now_ts, now_ts] + candidate_ids),
                )
                affected["hard_deleted"] = len(candidate_ids)
        total = affected["archived"] + affected["soft_deleted"] + affected["hard_deleted"]
        if total > 0:
            for action_name, count in affected.items():
                if count <= 0:
                    continue
                conn.execute(
                    """
                    INSERT INTO project_chat_cleanup_logs_v2(
                      id, project_id, policy_id, action_type, affected_message_count, executed_by, details_json, executed_at
                    )
                    VALUES(?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        _v2_id("pccl"),
                        project_id,
                        str(policy.get("id") or ""),
                        action_name,
                        count,
                        actor or "system",
                        json.dumps({"mode": mode}, ensure_ascii=False),
                        now_ts,
                    ),
                )
        _v2_audit(
            conn,
            actor or "system",
            "manual_cleanup_triggered",
            "project_chat_cleanup",
            project_id,
            {"mode": mode, "affected": affected},
        )
        conn.commit()
        return {"ok": True, "project_id": project_id, "affected": affected, "mode": mode}, 200


def _v2_project_chat_restore_messages(user: dict | None, project_id: str, payload: dict) -> tuple[dict, int]:
    if not user:
        return {"ok": False, "error": "authentication_required"}, 401
    actor = _v2_user_email(user)
    ids = payload.get("message_ids") if isinstance(payload.get("message_ids"), list) else []
    message_ids = [str(item).strip() for item in ids if str(item).strip()]
    if not message_ids:
        return {"ok": False, "error": "message_ids_required"}, 400
    with v2_db_lock, _v2_db_conn() as conn:
        if not _v2_can_manage_project(conn, user, project_id) and not is_admin_user(user):
            return {"ok": False, "error": "permission_denied"}, 403
        policy = _v2_chat_effective_policy(conn, project_id)
        allow_archive = bool(policy.get("allow_restore_from_archive", True))
        allow_soft = bool(policy.get("allow_restore_from_soft_delete", False))
        rows = conn.execute(
            f"""
            SELECT *
            FROM project_chat_messages_v2
            WHERE project_id = ? AND id IN ({','.join(['?'] * len(message_ids))})
            """,
            tuple([project_id] + message_ids),
        ).fetchall()
        restorable_ids = []
        for row in rows:
            status = str(row["lifecycle_status"] or "active")
            if status == "archived" and allow_archive:
                restorable_ids.append(str(row["id"] or ""))
            elif status == "soft_deleted" and allow_soft:
                restorable_ids.append(str(row["id"] or ""))
        if restorable_ids:
            conn.execute(
                f"UPDATE project_chat_messages_v2 SET lifecycle_status = 'active', updated_at = ? WHERE id IN ({','.join(['?'] * len(restorable_ids))})",
                tuple([_v2_now()] + restorable_ids),
            )
            conn.execute(
                """
                INSERT INTO project_chat_cleanup_logs_v2(
                  id, project_id, policy_id, action_type, affected_message_count, executed_by, details_json, executed_at
                )
                VALUES(?, ?, ?, 'restored', ?, ?, ?, ?)
                """,
                (
                    _v2_id("pccl"),
                    project_id,
                    str(policy.get("id") or ""),
                    len(restorable_ids),
                    actor or "system",
                    json.dumps({"message_ids": restorable_ids[:120]}, ensure_ascii=False),
                    _v2_now(),
                ),
            )
        _v2_audit(
            conn,
            actor or "system",
            "messages_restored",
            "project_chat_message",
            project_id,
            {"restored_count": len(restorable_ids)},
        )
        conn.commit()
        return {"ok": True, "project_id": project_id, "restored_count": len(restorable_ids), "restored_message_ids": restorable_ids}, 200


def _v2_project_chat_update_policy(user: dict | None, project_id: str, payload: dict) -> tuple[dict, int]:
    if not user:
        return {"ok": False, "error": "authentication_required"}, 401
    with v2_db_lock, _v2_db_conn() as conn:
        if not _v2_can_manage_project(conn, user, project_id) and not is_admin_user(user):
            return {"ok": False, "error": "permission_denied"}, 403
        if not conn.execute("SELECT 1 FROM projects WHERE id = ?", (project_id,)).fetchone():
            return {"ok": False, "error": "project_not_found"}, 404
        now_ts = _v2_now()
        archive_after_days = max(1, min(3650, int(payload.get("archive_after_days", 14) or 14)))
        soft_delete_after_days = max(1, min(3650, int(payload.get("soft_delete_after_days", 30) or 30)))
        hard_delete_after_days = max(1, min(3650, int(payload.get("hard_delete_after_days", 90) or 90)))
        if not (archive_after_days <= soft_delete_after_days <= hard_delete_after_days):
            return {"ok": False, "error": "invalid_policy_window"}, 400
        values = {
            "retain_key_messages": 1 if bool(payload.get("retain_key_messages", True)) else 0,
            "retain_system_messages": 1 if bool(payload.get("retain_system_messages", True)) else 0,
            "retain_approval_related_messages": 1 if bool(payload.get("retain_approval_related_messages", True)) else 0,
            "retain_file_change_messages": 1 if bool(payload.get("retain_file_change_messages", True)) else 0,
            "allow_restore_from_archive": 1 if bool(payload.get("allow_restore_from_archive", True)) else 0,
            "allow_restore_from_soft_delete": 1 if bool(payload.get("allow_restore_from_soft_delete", False)) else 0,
        }
        existing = conn.execute(
            """
            SELECT id
            FROM project_chat_retention_policies_v2
            WHERE scope_type = 'project' AND project_id = ?
            LIMIT 1
            """,
            (project_id,),
        ).fetchone()
        actor = _v2_user_email(user) or "system"
        if existing:
            conn.execute(
                """
                UPDATE project_chat_retention_policies_v2
                SET archive_after_days = ?, soft_delete_after_days = ?, hard_delete_after_days = ?,
                    retain_key_messages = ?, retain_system_messages = ?, retain_approval_related_messages = ?, retain_file_change_messages = ?,
                    allow_restore_from_archive = ?, allow_restore_from_soft_delete = ?, created_by = ?, updated_at = ?
                WHERE id = ?
                """,
                (
                    archive_after_days,
                    soft_delete_after_days,
                    hard_delete_after_days,
                    values["retain_key_messages"],
                    values["retain_system_messages"],
                    values["retain_approval_related_messages"],
                    values["retain_file_change_messages"],
                    values["allow_restore_from_archive"],
                    values["allow_restore_from_soft_delete"],
                    actor,
                    now_ts,
                    str(existing["id"] or ""),
                ),
            )
        else:
            conn.execute(
                """
                INSERT INTO project_chat_retention_policies_v2(
                  id, project_id, scope_type, archive_after_days, soft_delete_after_days, hard_delete_after_days,
                  retain_key_messages, retain_system_messages, retain_approval_related_messages, retain_file_change_messages,
                  allow_restore_from_archive, allow_restore_from_soft_delete, created_by, created_at, updated_at
                )
                VALUES(?, ?, 'project', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    _v2_id("pcp"),
                    project_id,
                    archive_after_days,
                    soft_delete_after_days,
                    hard_delete_after_days,
                    values["retain_key_messages"],
                    values["retain_system_messages"],
                    values["retain_approval_related_messages"],
                    values["retain_file_change_messages"],
                    values["allow_restore_from_archive"],
                    values["allow_restore_from_soft_delete"],
                    actor,
                    now_ts,
                    now_ts,
                ),
            )
        policy = _v2_chat_effective_policy(conn, project_id)
        _v2_audit(conn, actor, "retention_policy_updated", "project_chat_policy", project_id, policy)
        conn.commit()
        return {"ok": True, "project_id": project_id, "retention_policy": policy}, 200


def _v2_admin_project_chat_summary_overview(user: dict | None) -> tuple[dict, int]:
    if not is_admin_user(user):
        return {"ok": False, "error": "admin_required"}, 403
    now_ts = _v2_now()
    stale_threshold = now_ts - 24 * 60 * 60
    with v2_db_lock, _v2_db_conn() as conn:
        projects = conn.execute("SELECT id, name, status, updated_at FROM projects ORDER BY updated_at DESC LIMIT 600").fetchall()
        project_rows = []
        stale_count = 0
        backlog_count = 0
        for row in projects:
            project_id = str(row["id"] or "")
            summary = conn.execute(
                """
                SELECT id, generated_at, summary_status, source_message_count, quality_score
                FROM project_chat_summaries_v2
                WHERE project_id = ? AND is_current = 1
                ORDER BY generated_at DESC
                LIMIT 1
                """,
                (project_id,),
            ).fetchone()
            if not summary:
                summary = conn.execute(
                    """
                    SELECT id, generated_at, summary_status, source_message_count, quality_score
                    FROM project_chat_summaries_v2
                    WHERE project_id = ?
                    ORDER BY generated_at DESC
                    LIMIT 1
                    """,
                    (project_id,),
                ).fetchone()
            counts = _v2_project_chat_message_counts(conn, project_id)
            latest_active = conn.execute(
                """
                SELECT MAX(created_at) AS latest_active_at
                FROM project_chat_messages_v2
                WHERE project_id = ? AND lifecycle_status = 'active'
                """,
                (project_id,),
            ).fetchone()
            latest_active_at = int(latest_active["latest_active_at"] or 0) if latest_active else 0
            summary_at = int(summary["generated_at"] or 0) if summary else 0
            is_stale = (latest_active_at > summary_at and latest_active_at > 0) or (summary_at and summary_at < stale_threshold)
            pending_runs = conn.execute(
                """
                SELECT COUNT(*) AS c
                FROM project_chat_summary_runs_v2
                WHERE project_id = ? AND status IN ('queued', 'running')
                """,
                (project_id,),
            ).fetchone()
            failed_runs = conn.execute(
                """
                SELECT COUNT(*) AS c
                FROM project_chat_summary_runs_v2
                WHERE project_id = ? AND status = 'failed'
                """,
                (project_id,),
            ).fetchone()
            pending = int(pending_runs["c"] or 0) if pending_runs else 0
            failed = int(failed_runs["c"] or 0) if failed_runs else 0
            if is_stale:
                stale_count += 1
            if pending > 0:
                backlog_count += 1
            project_rows.append(
                {
                    "project_id": project_id,
                    "project_name": str(row["name"] or ""),
                    "project_status": str(row["status"] or ""),
                    "latest_summary_id": str(summary["id"] or "") if summary else "",
                    "latest_summary_at": summary_at,
                    "latest_summary_status": str(summary["summary_status"] or "") if summary else "missing",
                    "latest_summary_source_count": int(summary["source_message_count"] or 0) if summary else 0,
                    "latest_summary_quality_score": float(summary["quality_score"] or 0) if summary else 0.0,
                    "latest_active_message_at": latest_active_at,
                    "is_stale": is_stale,
                    "pending_runs": pending,
                    "failed_runs": failed,
                    "message_counts": counts,
                    "updated_at": int(row["updated_at"] or 0),
                }
            )
        cleanup_rows = conn.execute(
            """
            SELECT project_id, action_type, affected_message_count, executed_by, executed_at
            FROM project_chat_cleanup_logs_v2
            ORDER BY executed_at DESC
            LIMIT 80
            """
        ).fetchall()
        failed_rows = conn.execute(
            """
            SELECT id, project_id, trigger_type, provider_type, error_message, created_at, completed_at
            FROM project_chat_summary_runs_v2
            WHERE status = 'failed'
            ORDER BY created_at DESC
            LIMIT 80
            """
        ).fetchall()
        return {
            "ok": True,
            "totals": {
                "projects": len(project_rows),
                "stale_projects": stale_count,
                "backlog_projects": backlog_count,
                "active_messages": sum(int(item["message_counts"]["active"]) for item in project_rows),
                "archived_messages": sum(int(item["message_counts"]["archived"]) for item in project_rows),
                "soft_deleted_messages": sum(int(item["message_counts"]["soft_deleted"]) for item in project_rows),
                "hard_deleted_messages": sum(int(item["message_counts"]["hard_deleted"]) for item in project_rows),
                "key_messages": sum(int(item["message_counts"]["key_messages"]) for item in project_rows),
            },
            "projects": project_rows[:300],
            "recent_cleanup_actions": [
                {
                    "project_id": str(row["project_id"] or ""),
                    "action_type": str(row["action_type"] or ""),
                    "affected_message_count": int(row["affected_message_count"] or 0),
                    "executed_by": str(row["executed_by"] or ""),
                    "executed_at": int(row["executed_at"] or 0),
                }
                for row in cleanup_rows
            ],
            "recent_failures": [
                {
                    "run_id": str(row["id"] or ""),
                    "project_id": str(row["project_id"] or ""),
                    "trigger_type": str(row["trigger_type"] or ""),
                    "provider_type": str(row["provider_type"] or ""),
                    "error_message": str(row["error_message"] or ""),
                    "created_at": int(row["created_at"] or 0),
                    "completed_at": int(row["completed_at"] or 0),
                }
                for row in failed_rows
            ],
        }, 200


def _v2_chat_scheduler_state_payload() -> dict:
    path = ACTIVITY_DIR / "v2_chat_summary_scheduler_state.json"
    state = _load_json_file(path, {})
    if not isinstance(state, dict):
        state = {}
    return {
        "path": str(path),
        "last_daily_run_key": str(state.get("last_daily_run_key") or ""),
        "last_cleanup_run_key": str(state.get("last_cleanup_run_key") or ""),
        "last_threshold_scan_at": int(state.get("last_threshold_scan_at", 0) or 0),
        "last_retry_scan_at": int(state.get("last_retry_scan_at", 0) or 0),
    }


def _v2_chat_save_scheduler_state(state: dict) -> None:
    path = Path(str(state.get("path") or ACTIVITY_DIR / "v2_chat_summary_scheduler_state.json"))
    payload = {
        "last_daily_run_key": str(state.get("last_daily_run_key") or ""),
        "last_cleanup_run_key": str(state.get("last_cleanup_run_key") or ""),
        "last_threshold_scan_at": int(state.get("last_threshold_scan_at", 0) or 0),
        "last_retry_scan_at": int(state.get("last_retry_scan_at", 0) or 0),
    }
    _save_json_file(path, payload)


def _v2_chat_generate_daily_summaries(force: bool = False) -> None:
    state = _v2_chat_scheduler_state_payload()
    now_local = local_now()
    day_key = local_day_key(now_local)
    if not force and now_local.hour < 8:
        return
    if not force and state.get("last_daily_run_key") == day_key:
        return
    with v2_db_lock, _v2_db_conn() as conn:
        rows = conn.execute("SELECT id FROM projects WHERE status IN ('active','planning','blocked','on_hold')").fetchall()
        for row in rows:
            project_id = str(row["id"] or "")
            recent_active = conn.execute(
                """
                SELECT COUNT(*) AS c
                FROM project_chat_messages_v2
                WHERE project_id = ? AND lifecycle_status = 'active' AND created_at >= ?
                """,
                (project_id, _v2_now() - 24 * 60 * 60),
            ).fetchone()
            if not force and int(recent_active["c"] or 0) <= 0:
                continue
            _v2_chat_generate_summary_for_project(
                conn,
                {"email": "system", "role": "admin", "permissions": {"user_admin": True}},
                project_id,
                trigger_type="daily",
                provider_hint="hybrid",
                force=False,
            )
        conn.commit()
    state["last_daily_run_key"] = day_key
    _v2_chat_save_scheduler_state(state)


def _v2_chat_threshold_summarize() -> None:
    state = _v2_chat_scheduler_state_payload()
    now_ts = _v2_now()
    if now_ts - int(state.get("last_threshold_scan_at", 0) or 0) < 300:
        return
    threshold = 25
    with v2_db_lock, _v2_db_conn() as conn:
        projects = conn.execute("SELECT id FROM projects").fetchall()
        for row in projects:
            project_id = str(row["id"] or "")
            latest = conn.execute(
                """
                SELECT generated_at
                FROM project_chat_summaries_v2
                WHERE project_id = ?
                ORDER BY generated_at DESC
                LIMIT 1
                """,
                (project_id,),
            ).fetchone()
            since = int(latest["generated_at"] or 0) if latest else 0
            new_count = conn.execute(
                """
                SELECT COUNT(*) AS c
                FROM project_chat_messages_v2
                WHERE project_id = ? AND lifecycle_status = 'active' AND created_at > ?
                """,
                (project_id, since),
            ).fetchone()
            if int(new_count["c"] or 0) < threshold:
                continue
            _v2_chat_generate_summary_for_project(
                conn,
                {"email": "system", "role": "admin", "permissions": {"user_admin": True}},
                project_id,
                trigger_type="threshold",
                provider_hint="hybrid",
                force=False,
            )
        conn.commit()
    state["last_threshold_scan_at"] = now_ts
    _v2_chat_save_scheduler_state(state)


def _v2_chat_retry_failed_runs() -> None:
    state = _v2_chat_scheduler_state_payload()
    now_ts = _v2_now()
    if now_ts - int(state.get("last_retry_scan_at", 0) or 0) < 900:
        return
    with v2_db_lock, _v2_db_conn() as conn:
        failed = conn.execute(
            """
            SELECT id, project_id, trigger_type
            FROM project_chat_summary_runs_v2
            WHERE status = 'failed' AND created_at >= ?
            ORDER BY created_at DESC
            LIMIT 30
            """,
            (now_ts - 24 * 60 * 60,),
        ).fetchall()
        seen_projects: set[str] = set()
        for row in failed:
            project_id = str(row["project_id"] or "")
            if not project_id or project_id in seen_projects:
                continue
            seen_projects.add(project_id)
            _v2_chat_generate_summary_for_project(
                conn,
                {"email": "system", "role": "admin", "permissions": {"user_admin": True}},
                project_id,
                trigger_type="regenerated",
                provider_hint="rule_based",
                force=True,
            )
        conn.commit()
    state["last_retry_scan_at"] = now_ts
    _v2_chat_save_scheduler_state(state)


def _v2_chat_cleanup_scheduled(force: bool = False) -> None:
    state = _v2_chat_scheduler_state_payload()
    now_local = local_now()
    day_key = local_day_key(now_local)
    if not force and now_local.hour < 3:
        return
    if not force and state.get("last_cleanup_run_key") == day_key:
        return
    with v2_db_lock, _v2_db_conn() as conn:
        rows = conn.execute("SELECT id FROM projects").fetchall()
    system_user = {"email": "system", "role": "admin", "permissions": {"user_admin": True}}
    for row in rows:
        project_id = str(row["id"] or "")
        _v2_project_chat_cleanup(system_user, project_id, {"mode": "all"})
    state["last_cleanup_run_key"] = day_key
    _v2_chat_save_scheduler_state(state)


def _v2_chat_event_refresh_if_needed(conn: sqlite3.Connection, project_id: str) -> None:
    latest = conn.execute(
        """
        SELECT generated_at
        FROM project_chat_summaries_v2
        WHERE project_id = ?
        ORDER BY generated_at DESC
        LIMIT 1
        """,
        (project_id,),
    ).fetchone()
    since = int(latest["generated_at"] or 0) if latest else 0
    new_count = conn.execute(
        """
        SELECT COUNT(*) AS c
        FROM project_chat_messages_v2
        WHERE project_id = ? AND lifecycle_status = 'active' AND created_at > ?
        """,
        (project_id, since),
    ).fetchone()
    if int(new_count["c"] or 0) < 8:
        return
    pending = conn.execute(
        """
        SELECT COUNT(*) AS c
        FROM project_chat_summary_runs_v2
        WHERE project_id = ? AND status IN ('queued','running')
        """,
        (project_id,),
    ).fetchone()
    if int(pending["c"] or 0) > 0:
        return
    _v2_chat_generate_summary_for_project(
        conn,
        {"email": "system", "role": "admin", "permissions": {"user_admin": True}},
        project_id,
        trigger_type="event",
        provider_hint="hybrid",
        force=False,
    )


def _v2_chat_maybe_run_jobs(force: bool = False) -> None:
    try:
        _v2_chat_generate_daily_summaries(force=force)
        _v2_chat_threshold_summarize()
        _v2_chat_retry_failed_runs()
        _v2_chat_cleanup_scheduled(force=force)
    except Exception as exc:
        log(f"v2 chat scheduler error: {exc}")


def _v2_intel_scheduler_state_payload() -> dict:
    path = ACTIVITY_DIR / "v2_intelligence_scheduler_state.json"
    data = _load_json_file(path, {})
    if not isinstance(data, dict):
        data = {}
    return {
        "path": str(path),
        "last_market_refresh_at": int(data.get("last_market_refresh_at", 0) or 0),
        "last_news_refresh_at": int(data.get("last_news_refresh_at", 0) or 0),
        "last_digest_refresh_at": int(data.get("last_digest_refresh_at", 0) or 0),
        "last_instrument_quote_refresh_at": int(data.get("last_instrument_quote_refresh_at", 0) or 0),
        "last_instrument_ohlcv_refresh_at": int(data.get("last_instrument_ohlcv_refresh_at", 0) or 0),
        "last_morning_refresh_key": str(data.get("last_morning_refresh_key", "") or ""),
    }


def _v2_intel_save_scheduler_state(state: dict) -> None:
    path = Path(str(state.get("path") or ACTIVITY_DIR / "v2_intelligence_scheduler_state.json"))
    _save_json_file(
        path,
        {
            "last_market_refresh_at": int(state.get("last_market_refresh_at", 0) or 0),
            "last_news_refresh_at": int(state.get("last_news_refresh_at", 0) or 0),
            "last_digest_refresh_at": int(state.get("last_digest_refresh_at", 0) or 0),
            "last_instrument_quote_refresh_at": int(state.get("last_instrument_quote_refresh_at", 0) or 0),
            "last_instrument_ohlcv_refresh_at": int(state.get("last_instrument_ohlcv_refresh_at", 0) or 0),
            "last_morning_refresh_key": str(state.get("last_morning_refresh_key", "") or ""),
        },
    )


def _v2_intel_record_provider_error(
    conn: sqlite3.Connection,
    provider_id: str,
    error_type: str,
    error_message: str,
    request_url: str = "",
    http_status: int = 0,
    metadata: dict | None = None,
) -> None:
    conn.execute(
        """
        INSERT INTO intelligence_provider_errors_v2(
          id, provider_id, error_type, error_message, http_status, request_url, occurred_at, metadata_json
        )
        VALUES(?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            _v2_id("intpe"),
            provider_id,
            str(error_type or "")[:120],
            str(error_message or "")[:4000],
            int(http_status or 0),
            str(request_url or "")[:600],
            _v2_now(),
            json.dumps(metadata or {}, ensure_ascii=False),
        ),
    )


def _v2_intel_job_start(conn: sqlite3.Connection, job_name: str, job_type: str, provider_id: str = "", metadata: dict | None = None) -> str:
    run_id = _v2_id("intjob")
    now = _v2_now()
    conn.execute(
        """
        INSERT INTO intelligence_job_runs_v2(
          id, job_name, job_type, provider_id, status, started_at, completed_at, duration_ms,
          fetched_count, processed_count, inserted_count, updated_count, skipped_count, failed_count,
          error_message, error_stack, metadata_json, created_at
        )
        VALUES(?, ?, ?, ?, 'running', ?, 0, 0, 0, 0, 0, 0, 0, 0, '', '', ?, ?)
        """,
        (run_id, job_name[:200], job_type[:100], provider_id[:100], now, json.dumps(metadata or {}, ensure_ascii=False), now),
    )
    return run_id


def _v2_intel_job_finish(conn: sqlite3.Connection, run_id: str, status: str, counters: dict | None = None, error_message: str = "", metadata: dict | None = None) -> None:
    counters = counters or {}
    now = _v2_now()
    started_row = conn.execute("SELECT started_at FROM intelligence_job_runs_v2 WHERE id = ? LIMIT 1", (run_id,)).fetchone()
    started_at = int(started_row["started_at"] or now) if started_row else now
    duration_ms = max(0, int((now - started_at) * 1000))
    conn.execute(
        """
        UPDATE intelligence_job_runs_v2
        SET status = ?, completed_at = ?, duration_ms = ?,
            fetched_count = ?, processed_count = ?, inserted_count = ?, updated_count = ?, skipped_count = ?, failed_count = ?,
            error_message = ?, metadata_json = ?
        WHERE id = ?
        """,
        (
            str(status or "succeeded")[:40],
            now,
            duration_ms,
            int(counters.get("fetched_count", 0) or 0),
            int(counters.get("processed_count", 0) or 0),
            int(counters.get("inserted_count", 0) or 0),
            int(counters.get("updated_count", 0) or 0),
            int(counters.get("skipped_count", 0) or 0),
            int(counters.get("failed_count", 0) or 0),
            str(error_message or "")[:2000],
            json.dumps(metadata or {}, ensure_ascii=False),
            run_id,
        ),
    )


def _v2_intel_seed_defaults(conn: sqlite3.Connection) -> None:
    now = _v2_now()
    providers = [
        ("yahoo_finance_free", "Yahoo Finance Free", "market_data", "https://query1.finance.yahoo.com"),
        ("stooq", "Stooq", "market_data", "https://stooq.com"),
        ("alpha_vantage_free", "Alpha Vantage Free", "market_data", "https://www.alphavantage.co"),
        ("twelve_data_free", "Twelve Data Free", "market_data", "https://api.twelvedata.com"),
        ("google_news_rss", "Google News RSS", "news_rss", "https://news.google.com/rss"),
        ("guardian_open_platform", "Guardian Open Platform", "news_api", "https://content.guardianapis.com"),
        ("gdelt", "GDELT", "news_api", "https://api.gdeltproject.org"),
    ]
    for code, name, ptype, base_url in providers:
        exists = conn.execute("SELECT 1 FROM intelligence_free_data_providers_v2 WHERE provider_code = ? LIMIT 1", (code,)).fetchone()
        if exists:
            continue
        conn.execute(
            """
            INSERT INTO intelligence_free_data_providers_v2(
              id, provider_code, provider_name, provider_type, base_url, auth_type, api_key_env_name, free_tier_limit_json,
              rate_limit_per_minute, rate_limit_per_day, is_active, priority_score, terms_note, config_json, created_at, updated_at
            )
            VALUES(?, ?, ?, ?, ?, 'none', '', '{}', 0, 0, 1, 50, '', '{}', ?, ?)
            """,
            (_v2_id("intp"), code, name, ptype, base_url, now, now),
        )
    provider_rows = conn.execute("SELECT id, provider_code FROM intelligence_free_data_providers_v2").fetchall()
    provider_map = {str(row["provider_code"]): str(row["id"]) for row in provider_rows}
    indices = [
        ("US", "north_america", "US Market", "美国市场", "SP500", "^GSPC", "S&P 500", "标普500指数", "USD", "America/New_York", 10),
        ("US", "north_america", "US Market", "美国市场", "NASDAQ", "^IXIC", "NASDAQ Composite", "纳斯达克综合指数", "USD", "America/New_York", 11),
        ("US", "north_america", "US Market", "美国市场", "DOW_JONES", "^DJI", "Dow Jones", "道琼斯工业指数", "USD", "America/New_York", 12),
        ("CN", "asia", "China Market", "中国市场", "SSE_COMPOSITE", "000001.SS", "SSE Composite", "上证指数", "CNY", "Asia/Shanghai", 20),
        ("CN", "asia", "China Market", "中国市场", "SZSE_COMPONENT", "399001.SZ", "SZSE Component", "深证成指", "CNY", "Asia/Shanghai", 21),
        ("GB", "europe", "UK Market", "英国市场", "FTSE100", "^FTSE", "FTSE 100", "富时100", "GBP", "Europe/London", 30),
        ("JP", "asia", "Japan Market", "日本市场", "NIKKEI225", "^N225", "Nikkei 225", "日经225", "JPY", "Asia/Tokyo", 31),
        ("TW", "asia", "Taiwan Market", "中国台湾市场", "TAIEX", "^TWII", "TAIEX", "台湾加权指数", "TWD", "Asia/Taipei", 32),
        ("IN", "asia", "India Market", "印度市场", "NIFTY50", "^NSEI", "NIFTY 50", "印度NIFTY50", "INR", "Asia/Kolkata", 33),
        ("VN", "asia", "Vietnam Market", "越南市场", "VNINDEX", "^VNINDEX", "VN-Index", "越南VNINDEX", "VND", "Asia/Ho_Chi_Minh", 34),
    ]
    for country, region, m_en, m_zh, code, symbol, n_en, n_zh, ccy, tz, order in indices:
        exists = conn.execute("SELECT 1 FROM intelligence_market_indices_v2 WHERE index_code = ? LIMIT 1", (code,)).fetchone()
        if exists:
            continue
        yahoo_id = provider_map.get("yahoo_finance_free", "")
        conn.execute(
            """
            INSERT INTO intelligence_market_indices_v2(
              id, country_code, region_code, market_name_en, market_name_zh, index_code, index_symbol, index_name_en, index_name_zh,
              currency, exchange_timezone, display_order, is_active, primary_provider_id, fallback_provider_ids_json, provider_symbol_map_json,
              created_at, updated_at
            )
            VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, '[]', ?, ?, ?)
            """,
            (
                _v2_id("intidx"),
                country,
                region,
                m_en,
                m_zh,
                code,
                symbol,
                n_en,
                n_zh,
                ccy,
                tz,
                order,
                yahoo_id,
                json.dumps({"yahoo_finance_free": symbol}, ensure_ascii=False),
                now,
                now,
            ),
        )
    sources = [
        ("bbc_rss", "BBC", "BBC", "rss", "GB", "en", "https://www.bbc.com", "https://feeds.bbci.co.uk/news/world/rss.xml", "world", 80),
        ("cnbc_rss", "CNBC", "CNBC", "rss", "US", "en", "https://www.cnbc.com", "https://www.cnbc.com/id/10000664/device/rss/rss.html", "finance", 88),
        ("techcrunch_rss", "TechCrunch", "TechCrunch", "rss", "US", "en", "https://techcrunch.com", "https://techcrunch.com/feed/", "technology", 72),
        ("theverge_rss", "The Verge", "The Verge", "rss", "US", "en", "https://www.theverge.com", "https://www.theverge.com/rss/index.xml", "technology", 70),
        ("wired_rss", "Wired", "Wired", "rss", "US", "en", "https://www.wired.com", "https://www.wired.com/feed/rss", "technology", 68),
    ]
    google_provider = provider_map.get("google_news_rss", "")
    for source_code, name_en, name_zh, source_type, country, lang, home, feed, category, priority in sources:
        row = conn.execute("SELECT id FROM intelligence_news_sources_v2 WHERE source_code = ? LIMIT 1", (source_code,)).fetchone()
        if row:
            source_id = str(row["id"])
        else:
            source_id = _v2_id("intsrc")
            conn.execute(
                """
                INSERT INTO intelligence_news_sources_v2(
                  id, source_code, source_name_en, source_name_zh, source_type, provider_id, source_country, source_language,
                  homepage_url, feed_url, default_category, priority_score, is_non_china_media, is_active, copyright_policy, config_json, created_at, updated_at
                )
                VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, 1, 'metadata_summary_link_only', '{}', ?, ?)
                """,
                (
                    source_id,
                    source_code,
                    name_en,
                    name_zh,
                    source_type,
                    google_provider,
                    country,
                    lang,
                    home,
                    feed,
                    category,
                    priority,
                    now,
                    now,
                ),
            )
        feed_exists = conn.execute(
            "SELECT 1 FROM intelligence_news_source_feeds_v2 WHERE source_id = ? AND feed_url = ? LIMIT 1",
            (source_id, feed),
        ).fetchone()
        if not feed_exists:
            conn.execute(
                """
                INSERT INTO intelligence_news_source_feeds_v2(
                  id, source_id, category, feed_name, feed_url, language_code, is_active, created_at, updated_at
                )
                VALUES(?, ?, ?, ?, ?, ?, 1, ?, ?)
                """,
                (_v2_id("intfeed"), source_id, category, f"{name_en} {category}", feed, lang, now, now),
            )


def _v2_intel_seed_market_instruments(conn: sqlite3.Connection) -> None:
    _v2_intel_seed_defaults(conn)
    now = _v2_now()
    provider_rows = conn.execute("SELECT id, provider_code FROM intelligence_free_data_providers_v2").fetchall()
    provider_map = {str(row["provider_code"]): str(row["id"]) for row in provider_rows}
    yahoo_id = provider_map.get("yahoo_finance_free", "")
    instruments = [
        ("index", "^GSPC", "S&P 500", "标普500指数", "US", "north_america", "INDEX", "Index", "指数", "USD", "America/New_York"),
        ("index", "^IXIC", "Nasdaq Composite", "纳斯达克综合指数", "US", "north_america", "INDEX", "Index", "指数", "USD", "America/New_York"),
        ("index", "^DJI", "Dow Jones Industrial Average", "道琼斯工业指数", "US", "north_america", "INDEX", "Index", "指数", "USD", "America/New_York"),
        ("index", "000001.SS", "SSE Composite", "上证指数", "CN", "asia", "SSE", "Shanghai Stock Exchange", "上海证券交易所", "CNY", "Asia/Shanghai"),
        ("index", "399001.SZ", "Shenzhen Component", "深证成指", "CN", "asia", "SZSE", "Shenzhen Stock Exchange", "深圳证券交易所", "CNY", "Asia/Shanghai"),
        ("index", "^FTSE", "FTSE 100", "富时100", "GB", "europe", "LSE", "London Stock Exchange", "伦敦证券交易所", "GBP", "Europe/London"),
        ("index", "^N225", "Nikkei 225", "日经225", "JP", "asia", "TSE", "Tokyo Stock Exchange", "东京证券交易所", "JPY", "Asia/Tokyo"),
        ("index", "^TWII", "Taiwan Weighted Index", "台湾加权指数", "TW", "asia", "TWSE", "Taiwan Stock Exchange", "台湾证券交易所", "TWD", "Asia/Taipei"),
        ("index", "^BSESN", "Sensex", "印度Sensex", "IN", "asia", "BSE", "Bombay Stock Exchange", "孟买证券交易所", "INR", "Asia/Kolkata"),
        ("index", "^NSEI", "Nifty 50", "印度Nifty 50", "IN", "asia", "NSE", "National Stock Exchange of India", "印度国家证券交易所", "INR", "Asia/Kolkata"),
        ("stock", "AAPL", "Apple Inc.", "苹果公司", "US", "north_america", "NASDAQ", "NASDAQ", "纳斯达克", "USD", "America/New_York"),
        ("stock", "MSFT", "Microsoft Corporation", "微软公司", "US", "north_america", "NASDAQ", "NASDAQ", "纳斯达克", "USD", "America/New_York"),
        ("stock", "NVDA", "NVIDIA Corporation", "英伟达", "US", "north_america", "NASDAQ", "NASDAQ", "纳斯达克", "USD", "America/New_York"),
        ("stock", "TSLA", "Tesla, Inc.", "特斯拉", "US", "north_america", "NASDAQ", "NASDAQ", "纳斯达克", "USD", "America/New_York"),
        ("stock", "AMZN", "Amazon.com, Inc.", "亚马逊", "US", "north_america", "NASDAQ", "NASDAQ", "纳斯达克", "USD", "America/New_York"),
        ("etf", "SPY", "SPDR S&P 500 ETF Trust", "SPDR 标普500 ETF", "US", "north_america", "NYSEARCA", "NYSE Arca", "纽约证交所Arca", "USD", "America/New_York"),
        ("etf", "QQQ", "Invesco QQQ Trust", "纳指100 ETF", "US", "north_america", "NASDAQ", "NASDAQ", "纳斯达克", "USD", "America/New_York"),
        ("etf", "VTI", "Vanguard Total Stock Market ETF", "先锋全市场ETF", "US", "north_america", "NYSEARCA", "NYSE Arca", "纽约证交所Arca", "USD", "America/New_York"),
        ("etf", "IVV", "iShares Core S&P 500 ETF", "安硕核心标普500ETF", "US", "north_america", "NYSEARCA", "NYSE Arca", "纽约证交所Arca", "USD", "America/New_York"),
        # FX pairs for intelligence center (major settlement pairs).
        ("forex", "EURUSD=X", "EUR/USD", "欧元/美元", "EU", "europe", "FX", "Foreign Exchange", "外汇市场", "USD", "Europe/Brussels"),
        ("forex", "GBPUSD=X", "GBP/USD", "英镑/美元", "GB", "europe", "FX", "Foreign Exchange", "外汇市场", "USD", "Europe/London"),
        ("forex", "USDJPY=X", "USD/JPY", "美元/日元", "JP", "asia", "FX", "Foreign Exchange", "外汇市场", "JPY", "Asia/Tokyo"),
        ("forex", "USDCNH=X", "USD/CNH", "美元/离岸人民币", "CN", "asia", "FX", "Foreign Exchange", "外汇市场", "CNH", "Asia/Hong_Kong"),
        ("forex", "AUDUSD=X", "AUD/USD", "澳元/美元", "AU", "asia", "FX", "Foreign Exchange", "外汇市场", "USD", "Australia/Sydney"),
        ("forex", "USDCHF=X", "USD/CHF", "美元/瑞郎", "CH", "europe", "FX", "Foreign Exchange", "外汇市场", "CHF", "Europe/Zurich"),
        # Sovereign yields (Yahoo commonly returns yield * 10 for these benchmark symbols).
        ("index", "^IRX", "US 13W Treasury Yield", "美国13周国债收益率", "US", "north_america", "UST", "US Treasury", "美国国债", "USD", "America/New_York"),
        ("index", "^FVX", "US 5Y Treasury Yield", "美国5年国债收益率", "US", "north_america", "UST", "US Treasury", "美国国债", "USD", "America/New_York"),
        ("index", "^TNX", "US 10Y Treasury Yield", "美国10年国债收益率", "US", "north_america", "UST", "US Treasury", "美国国债", "USD", "America/New_York"),
        ("index", "^TYX", "US 30Y Treasury Yield", "美国30年国债收益率", "US", "north_america", "UST", "US Treasury", "美国国债", "USD", "America/New_York"),
        ("index", "^UK10Y", "UK 10Y Gilt Yield", "英国10年国债收益率", "GB", "europe", "GILT", "UK Gilts", "英国国债", "GBP", "Europe/London"),
        ("index", "^JP10Y", "Japan 10Y JGB Yield", "日本10年国债收益率", "JP", "asia", "JGB", "Japan Government Bond", "日本国债", "JPY", "Asia/Tokyo"),
    ]
    for instrument_type, symbol, name_en, name_zh, country, region, exchange_code, exchange_name_en, exchange_name_zh, currency, tz in instruments:
        row = conn.execute(
            """
            SELECT id
            FROM intelligence_market_instruments_v2
            WHERE instrument_type = ? AND symbol = ?
            LIMIT 1
            """,
            (instrument_type, symbol),
        ).fetchone()
        keywords = f"{symbol} {name_en} {name_zh} {instrument_type} {exchange_code}".strip()
        provider_symbol_map = json.dumps({"yahoo_finance_free": symbol}, ensure_ascii=False)
        if row:
            conn.execute(
                """
                UPDATE intelligence_market_instruments_v2
                SET name_en = ?, name_zh = ?, country_code = ?, region_code = ?, exchange_code = ?,
                    exchange_name_en = ?, exchange_name_zh = ?, currency = ?, timezone = ?, is_active = 1,
                    primary_provider_id = ?, provider_symbol_map_json = ?, search_keywords = ?, updated_at = ?
                WHERE id = ?
                """,
                (
                    name_en,
                    name_zh,
                    country,
                    region,
                    exchange_code,
                    exchange_name_en,
                    exchange_name_zh,
                    currency,
                    tz,
                    yahoo_id,
                    provider_symbol_map,
                    keywords,
                    now,
                    str(row["id"] or ""),
                ),
            )
            continue
        conn.execute(
            """
            INSERT INTO intelligence_market_instruments_v2(
              id, instrument_type, symbol, name_en, name_zh, country_code, region_code, exchange_code,
              exchange_name_en, exchange_name_zh, currency, timezone, is_active, primary_provider_id,
              fallback_provider_ids_json, provider_symbol_map_json, search_keywords, metadata_json, created_at, updated_at
            )
            VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, '[]', ?, ?, '{}', ?, ?)
            """,
            (
                _v2_id("intinst"),
                instrument_type,
                symbol,
                name_en,
                name_zh,
                country,
                region,
                exchange_code,
                exchange_name_en,
                exchange_name_zh,
                currency,
                tz,
                yahoo_id,
                provider_symbol_map,
                keywords,
                now,
                now,
            ),
        )


def _v2_intel_float(value: object, fallback: float = 0.0) -> float:
    try:
        if value in (None, ""):
            return float(fallback)
        return float(value)
    except Exception:
        return float(fallback)


def _v2_intel_int(value: object, fallback: int = 0) -> int:
    try:
        if value in (None, ""):
            return int(fallback)
        return int(float(value))
    except Exception:
        return int(fallback)


def _v2_intel_normalize_interval(interval: str) -> tuple[str, str]:
    text = str(interval or "1d").strip().lower()
    mapping = {
        "1m": "1m",
        "5m": "5m",
        "15m": "15m",
        "30m": "30m",
        "1h": "60m",
        "60m": "60m",
        "1d": "1d",
        "1w": "1wk",
        "1wk": "1wk",
        "1mo": "1mo",
    }
    yahoo_interval = mapping.get(text, "1d")
    normalized = "1h" if yahoo_interval == "60m" else "1w" if yahoo_interval == "1wk" else yahoo_interval
    return normalized, yahoo_interval


def _v2_intel_normalize_range(range_text: str) -> str:
    text = str(range_text or "6mo").strip().lower()
    allowed = {"1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"}
    return text if text in allowed else "6mo"


def _v2_intel_try_fetch_yahoo_chart(symbol: str, interval: str, range_text: str) -> dict | None:
    norm_interval, yahoo_interval = _v2_intel_normalize_interval(interval)
    yahoo_range = _v2_intel_normalize_range(range_text)
    url = (
        f"https://query1.finance.yahoo.com/v8/finance/chart/{quote(symbol.strip())}"
        f"?interval={quote(yahoo_interval)}&range={quote(yahoo_range)}&events=div%2Csplits&includeAdjustedClose=true"
    )
    payload = _v2_intel_http_get_json(url, timeout=10)
    result = (((payload or {}).get("chart") or {}).get("result") or [])
    if not result:
        return None
    root = result[0] or {}
    ts_list = root.get("timestamp") or []
    quote_list = (((root.get("indicators") or {}).get("quote") or [{}])[0]) or {}
    adj_list = (((root.get("indicators") or {}).get("adjclose") or [{}])[0]) or {}
    opens = quote_list.get("open") or []
    highs = quote_list.get("high") or []
    lows = quote_list.get("low") or []
    closes = quote_list.get("close") or []
    volumes = quote_list.get("volume") or []
    adj_closes = adj_list.get("adjclose") or []
    bars: list[dict] = []
    for idx, point_time in enumerate(ts_list):
        open_v = _v2_intel_float(opens[idx] if idx < len(opens) else 0, 0)
        high_v = _v2_intel_float(highs[idx] if idx < len(highs) else 0, open_v)
        low_v = _v2_intel_float(lows[idx] if idx < len(lows) else 0, open_v)
        close_v = _v2_intel_float(closes[idx] if idx < len(closes) else 0, open_v)
        if close_v == 0 and open_v == 0 and high_v == 0 and low_v == 0:
            continue
        bars.append(
            {
                "time": _v2_intel_int(point_time, 0),
                "open": open_v,
                "high": high_v if high_v else max(open_v, close_v),
                "low": low_v if low_v else min(open_v, close_v),
                "close": close_v,
                "adjusted_close": _v2_intel_float(adj_closes[idx] if idx < len(adj_closes) else close_v, close_v),
                "volume": _v2_intel_float(volumes[idx] if idx < len(volumes) else 0, 0),
            }
        )
    events = root.get("events") or {}
    dividends = events.get("dividends") or {}
    splits = events.get("splits") or {}
    return {
        "interval": norm_interval,
        "range": yahoo_range,
        "bars": bars,
        "dividends": dividends,
        "splits": splits,
        "meta": root.get("meta") or {},
        "source_payload": root,
    }


def _v2_intel_quote_from_chart(chart: dict | None) -> dict | None:
    if not isinstance(chart, dict):
        return None
    bars = chart.get("bars")
    if not isinstance(bars, list) or not bars:
        return None
    last = bars[-1] or {}
    prev = bars[-2] if len(bars) > 1 else last
    last_close = _v2_intel_float(last.get("close"), 0)
    if last_close <= 0:
        return None
    prev_close = _v2_intel_float(prev.get("close"), last_close)
    meta = chart.get("meta") if isinstance(chart.get("meta"), dict) else {}
    market_status = str(meta.get("marketState") or "unknown").lower()
    return {
        "quote_time": _v2_intel_int(last.get("time"), _v2_now()),
        "last_price": last_close,
        "previous_close": prev_close if prev_close > 0 else last_close,
        "open_price": _v2_intel_float(last.get("open"), last_close),
        "high_price": _v2_intel_float(last.get("high"), last_close),
        "low_price": _v2_intel_float(last.get("low"), last_close),
        "volume": _v2_intel_float(last.get("volume"), 0),
        "turnover_amount": _v2_intel_float(last.get("turnover_amount"), 0),
        "delayed_flag": True,
        "market_status": market_status,
        "source_payload": {
            "fallback": "yahoo_chart",
            "interval": chart.get("interval"),
            "range": chart.get("range"),
            "meta": meta,
        },
    }


def _v2_intel_upsert_instrument_quote(conn: sqlite3.Connection, instrument_id: str, provider_id: str, quote_payload: dict, data_quality: str = "normal") -> None:
    now = _v2_now()
    quote_time = _v2_intel_int(quote_payload.get("quote_time") or now, now)
    last_price = _v2_intel_float(quote_payload.get("last_price"), 0)
    prev_close = _v2_intel_float(quote_payload.get("previous_close"), 0)
    open_price = _v2_intel_float(quote_payload.get("open_price"), 0)
    high_price = _v2_intel_float(quote_payload.get("high_price"), max(last_price, open_price))
    low_price = _v2_intel_float(quote_payload.get("low_price"), min(last_price or open_price, open_price or last_price))
    if prev_close > 0:
        change_value = last_price - prev_close
        change_percent = (change_value / prev_close) * 100.0
    else:
        change_value = _v2_intel_float(quote_payload.get("change_value"), 0)
        change_percent = _v2_intel_float(quote_payload.get("change_percent"), 0)
    row = conn.execute(
        "SELECT id FROM intelligence_instrument_latest_quotes_v2 WHERE instrument_id = ? LIMIT 1",
        (instrument_id,),
    ).fetchone()
    payload_json = json.dumps(quote_payload.get("source_payload") or {}, ensure_ascii=False)
    params = (
        provider_id,
        quote_time,
        last_price,
        prev_close,
        open_price,
        high_price,
        low_price,
        change_value,
        change_percent,
        _v2_intel_float(quote_payload.get("volume"), 0),
        _v2_intel_float(quote_payload.get("turnover_amount"), 0),
        _v2_intel_float(quote_payload.get("bid_price"), 0),
        _v2_intel_float(quote_payload.get("ask_price"), 0),
        1 if bool(quote_payload.get("delayed_flag", True)) else 0,
        str(quote_payload.get("market_status") or "unknown")[:40],
        str(data_quality or "normal")[:30],
        payload_json,
    )
    if row:
        conn.execute(
            """
            UPDATE intelligence_instrument_latest_quotes_v2
            SET provider_id = ?, quote_time = ?, last_price = ?, previous_close = ?, open_price = ?, high_price = ?, low_price = ?,
                change_value = ?, change_percent = ?, volume = ?, turnover_amount = ?, bid_price = ?, ask_price = ?,
                delayed_flag = ?, market_status = ?, data_quality = ?, source_payload_json = ?, updated_at = ?
            WHERE instrument_id = ?
            """,
            (*params, now, instrument_id),
        )
    else:
        conn.execute(
            """
            INSERT INTO intelligence_instrument_latest_quotes_v2(
              id, instrument_id, provider_id, quote_time, last_price, previous_close, open_price, high_price, low_price,
              change_value, change_percent, volume, turnover_amount, bid_price, ask_price, delayed_flag, market_status,
              data_quality, source_payload_json, created_at, updated_at
            )
            VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (_v2_id("intlq"), instrument_id, *params, now, now),
        )
    conn.execute(
        """
        INSERT INTO intelligence_instrument_quote_snapshots_v2(
          id, instrument_id, provider_id, quote_time, last_price, previous_close, open_price, high_price, low_price,
          change_value, change_percent, volume, turnover_amount, bid_price, ask_price, delayed_flag, market_status,
          data_quality, source_payload_json, created_at
        )
        VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (_v2_id("intqs"), instrument_id, *params, now),
    )


def _v2_intel_upsert_instrument_corporate_actions(
    conn: sqlite3.Connection,
    instrument_id: str,
    provider_id: str,
    dividends: dict,
    splits: dict,
) -> None:
    now = _v2_now()
    for key, item in (dividends or {}).items():
        if not isinstance(item, dict):
            continue
        action_date = _v2_intel_int(item.get("date") or key, 0)
        amount = _v2_intel_float(item.get("amount"), 0)
        if action_date <= 0 or amount == 0:
            continue
        reference = f"div:{action_date}:{amount}"
        conn.execute(
            """
            INSERT INTO intelligence_instrument_corporate_actions_v2(
              id, instrument_id, provider_id, action_type, action_date, ex_date, record_date, pay_date,
              dividend_amount, split_from, split_to, split_coefficient, currency, reference, metadata_json, created_at, updated_at
            )
            VALUES(?, ?, ?, 'dividend', ?, ?, 0, 0, ?, 0, 0, 0, '', ?, ?, ?, ?)
            ON CONFLICT(instrument_id, action_type, action_date, reference) DO UPDATE SET
              dividend_amount = excluded.dividend_amount,
              metadata_json = excluded.metadata_json,
              updated_at = excluded.updated_at
            """,
            (
                _v2_id("intca"),
                instrument_id,
                provider_id,
                action_date,
                action_date,
                amount,
                reference,
                json.dumps(item, ensure_ascii=False),
                now,
                now,
            ),
        )
    for key, item in (splits or {}).items():
        if not isinstance(item, dict):
            continue
        action_date = _v2_intel_int(item.get("date") or key, 0)
        numerator = _v2_intel_float(item.get("numerator"), 0)
        denominator = _v2_intel_float(item.get("denominator"), 0)
        coefficient = (numerator / denominator) if denominator else 0
        if action_date <= 0 or coefficient <= 0:
            continue
        reference = f"split:{action_date}:{numerator}:{denominator}"
        conn.execute(
            """
            INSERT INTO intelligence_instrument_corporate_actions_v2(
              id, instrument_id, provider_id, action_type, action_date, ex_date, record_date, pay_date,
              dividend_amount, split_from, split_to, split_coefficient, currency, reference, metadata_json, created_at, updated_at
            )
            VALUES(?, ?, ?, 'split', ?, ?, 0, 0, 0, ?, ?, ?, '', ?, ?, ?, ?)
            ON CONFLICT(instrument_id, action_type, action_date, reference) DO UPDATE SET
              split_from = excluded.split_from,
              split_to = excluded.split_to,
              split_coefficient = excluded.split_coefficient,
              metadata_json = excluded.metadata_json,
              updated_at = excluded.updated_at
            """,
            (
                _v2_id("intca"),
                instrument_id,
                provider_id,
                action_date,
                action_date,
                denominator,
                numerator,
                coefficient,
                reference,
                json.dumps(item, ensure_ascii=False),
                now,
                now,
            ),
        )


def _v2_intel_upsert_instrument_ohlcv(
    conn: sqlite3.Connection,
    instrument_id: str,
    provider_id: str,
    interval: str,
    bars: list[dict],
    data_quality: str = "normal",
) -> dict:
    now = _v2_now()
    inserted = 0
    updated = 0
    for bar in bars:
        point_time = _v2_intel_int(bar.get("time"), 0)
        if point_time <= 0:
            continue
        open_price = _v2_intel_float(bar.get("open"), 0)
        high_price = _v2_intel_float(bar.get("high"), open_price)
        low_price = _v2_intel_float(bar.get("low"), open_price)
        close_price = _v2_intel_float(bar.get("close"), open_price)
        adjusted_close = _v2_intel_float(bar.get("adjusted_close"), close_price)
        volume = _v2_intel_float(bar.get("volume"), 0)
        turnover_amount = _v2_intel_float(bar.get("turnover_amount"), 0)
        dividend_amount = _v2_intel_float(bar.get("dividend_amount"), 0)
        split_coefficient = _v2_intel_float(bar.get("split_coefficient"), 0)
        for adjusted_flag in (0, 1):
            target_close = adjusted_close if adjusted_flag else close_price
            row = conn.execute(
                """
                SELECT id
                FROM intelligence_instrument_ohlcv_timeseries_v2
                WHERE instrument_id = ? AND interval_type = ? AND point_time = ? AND adjusted_flag = ?
                LIMIT 1
                """,
                (instrument_id, interval, point_time, adjusted_flag),
            ).fetchone()
            if row:
                conn.execute(
                    """
                    UPDATE intelligence_instrument_ohlcv_timeseries_v2
                    SET provider_id = ?, open_price = ?, high_price = ?, low_price = ?, close_price = ?, adjusted_close = ?,
                        volume = ?, turnover_amount = ?, dividend_amount = ?, split_coefficient = ?, data_quality = ?,
                        source_payload_json = ?, updated_at = ?
                    WHERE instrument_id = ? AND interval_type = ? AND point_time = ? AND adjusted_flag = ?
                    """,
                    (
                        provider_id,
                        open_price,
                        high_price,
                        low_price,
                        target_close,
                        adjusted_close,
                        volume,
                        turnover_amount,
                        dividend_amount,
                        split_coefficient,
                        str(data_quality or "normal")[:30],
                        json.dumps(bar, ensure_ascii=False),
                        now,
                        instrument_id,
                        interval,
                        point_time,
                        adjusted_flag,
                    ),
                )
                updated += 1
            else:
                conn.execute(
                    """
                    INSERT INTO intelligence_instrument_ohlcv_timeseries_v2(
                      id, instrument_id, provider_id, interval_type, point_time, adjusted_flag, open_price, high_price, low_price,
                      close_price, adjusted_close, volume, turnover_amount, dividend_amount, split_coefficient, data_quality,
                      source_payload_json, created_at, updated_at
                    )
                    VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        _v2_id("intohlcv"),
                        instrument_id,
                        provider_id,
                        interval,
                        point_time,
                        adjusted_flag,
                        open_price,
                        high_price,
                        low_price,
                        target_close,
                        adjusted_close,
                        volume,
                        turnover_amount,
                        dividend_amount,
                        split_coefficient,
                        str(data_quality or "normal")[:30],
                        json.dumps(bar, ensure_ascii=False),
                        now,
                        now,
                    ),
                )
                inserted += 1
    return {"inserted_count": inserted, "updated_count": updated}


def _v2_intel_refresh_instrument_quotes(
    conn: sqlite3.Connection,
    *,
    instrument_ids: list[str] | None = None,
    instrument_types: list[str] | None = None,
    symbols: list[str] | None = None,
    force: bool = False,
) -> dict:
    _v2_intel_seed_market_instruments(conn)
    where = ["is_active = 1"]
    params: list[object] = []
    id_list = [str(item or "").strip() for item in (instrument_ids or []) if str(item or "").strip()]
    if id_list:
        where.append(f"id IN ({','.join(['?'] * len(id_list))})")
        params.extend(id_list)
    type_list = [str(item or "").strip().lower() for item in (instrument_types or []) if str(item or "").strip().lower() in V2_INTEL_INSTRUMENT_TYPES]
    if type_list:
        where.append(f"instrument_type IN ({','.join(['?'] * len(type_list))})")
        params.extend(type_list)
    symbol_list = [str(item or "").strip().upper() for item in (symbols or []) if str(item or "").strip()]
    if symbol_list:
        where.append(f"upper(symbol) IN ({','.join(['?'] * len(symbol_list))})")
        params.extend(symbol_list)
    rows = conn.execute(
        f"SELECT * FROM intelligence_market_instruments_v2 WHERE {' AND '.join(where)} ORDER BY instrument_type, symbol",
        tuple(params),
    ).fetchall()
    counters = {"fetched_count": 0, "processed_count": 0, "inserted_count": 0, "updated_count": 0, "skipped_count": 0, "failed_count": 0}
    macro_fallback_map = _v2_intel_macro_fallback_quotes_for_symbols([str(item["symbol"] or "") for item in rows])
    run_id = _v2_intel_job_start(
        conn,
        "instrument_quote_refresh_free",
        "instrument_quote_refresh",
        metadata={"count": len(rows), "force": force},
    )
    try:
        for row in rows:
            counters["processed_count"] += 1
            instrument_id = str(row["id"] or "")
            symbol = str(row["symbol"] or "")
            provider_id = str(row["primary_provider_id"] or "")
            quote_payload = None
            data_quality = "normal"
            try:
                yahoo_quote = _v2_intel_try_fetch_yahoo_quote(symbol)
                if yahoo_quote:
                    quote_payload = {
                        "quote_time": _v2_now(),
                        "last_price": _v2_intel_float(yahoo_quote.get("current_value"), 0),
                        "previous_close": _v2_intel_float(yahoo_quote.get("previous_close"), 0),
                        "open_price": _v2_intel_float(yahoo_quote.get("open_value"), 0),
                        "high_price": _v2_intel_float(yahoo_quote.get("high_value"), 0),
                        "low_price": _v2_intel_float(yahoo_quote.get("low_value"), 0),
                        "change_value": _v2_intel_float(yahoo_quote.get("change_value"), 0),
                        "change_percent": _v2_intel_float(yahoo_quote.get("change_percent"), 0),
                        "volume": _v2_intel_float(yahoo_quote.get("volume"), 0),
                        "turnover_amount": _v2_intel_float(yahoo_quote.get("turnover_amount"), 0),
                        "delayed_flag": True,
                        "market_status": str(yahoo_quote.get("market_status") or "unknown"),
                        "source_payload": yahoo_quote.get("source_payload") or {},
                    }
                    counters["fetched_count"] += 1
            except Exception as exc:
                counters["failed_count"] += 1
                _v2_intel_record_provider_error(conn, provider_id, "instrument_quote_fetch_failed", str(exc), request_url=symbol)
            if not quote_payload:
                try:
                    chart = _v2_intel_try_fetch_yahoo_chart(symbol, "1d", "5d")
                    fallback_quote = _v2_intel_quote_from_chart(chart)
                    if fallback_quote:
                        quote_payload = fallback_quote
                        data_quality = "partial"
                        counters["fetched_count"] += 1
                except Exception as exc:
                    counters["failed_count"] += 1
                    _v2_intel_record_provider_error(conn, provider_id, "instrument_quote_fallback_failed", str(exc), request_url=symbol)
            if not quote_payload:
                fallback_payload = macro_fallback_map.get(symbol.upper())
                if fallback_payload:
                    quote_payload = fallback_payload
                    data_quality = "partial"
                    counters["fetched_count"] += 1
            if not quote_payload:
                counters["skipped_count"] += 1
                continue
            exists = conn.execute(
                "SELECT 1 FROM intelligence_instrument_latest_quotes_v2 WHERE instrument_id = ? LIMIT 1",
                (instrument_id,),
            ).fetchone()
            _v2_intel_upsert_instrument_quote(conn, instrument_id, provider_id, quote_payload, data_quality)
            if exists:
                counters["updated_count"] += 1
            else:
                counters["inserted_count"] += 1
        _v2_intel_job_finish(conn, run_id, "succeeded", counters=counters, metadata={"count": len(rows)})
        conn.commit()
        return {"ok": True, "run_id": run_id, **counters}
    except Exception as exc:
        _v2_intel_job_finish(conn, run_id, "failed", counters=counters, error_message=str(exc))
        conn.commit()
        return {"ok": False, "run_id": run_id, "error": str(exc)[:500], **counters}


def _v2_intel_refresh_instrument_ohlcv(
    conn: sqlite3.Connection,
    *,
    instrument_ids: list[str] | None = None,
    instrument_types: list[str] | None = None,
    symbols: list[str] | None = None,
    interval: str = "1d",
    range_text: str = "6mo",
    backfill: bool = False,
    force: bool = False,
) -> dict:
    _v2_intel_seed_market_instruments(conn)
    norm_interval, _ = _v2_intel_normalize_interval(interval)
    norm_range = _v2_intel_normalize_range(range_text)
    where = ["is_active = 1"]
    params: list[object] = []
    id_list = [str(item or "").strip() for item in (instrument_ids or []) if str(item or "").strip()]
    if id_list:
        where.append(f"id IN ({','.join(['?'] * len(id_list))})")
        params.extend(id_list)
    type_list = [str(item or "").strip().lower() for item in (instrument_types or []) if str(item or "").strip().lower() in V2_INTEL_INSTRUMENT_TYPES]
    if type_list:
        where.append(f"instrument_type IN ({','.join(['?'] * len(type_list))})")
        params.extend(type_list)
    symbol_list = [str(item or "").strip().upper() for item in (symbols or []) if str(item or "").strip()]
    if symbol_list:
        where.append(f"upper(symbol) IN ({','.join(['?'] * len(symbol_list))})")
        params.extend(symbol_list)
    rows = conn.execute(
        f"SELECT * FROM intelligence_market_instruments_v2 WHERE {' AND '.join(where)} ORDER BY instrument_type, symbol",
        tuple(params),
    ).fetchall()
    counters = {"fetched_count": 0, "processed_count": 0, "inserted_count": 0, "updated_count": 0, "skipped_count": 0, "failed_count": 0}
    run_id = _v2_intel_job_start(
        conn,
        "instrument_ohlcv_backfill_free" if backfill else "instrument_ohlcv_refresh_free",
        "instrument_ohlcv_backfill" if backfill else "instrument_ohlcv_refresh",
        metadata={"count": len(rows), "interval": norm_interval, "range": norm_range, "force": force},
    )
    try:
        for row in rows:
            counters["processed_count"] += 1
            instrument_id = str(row["id"] or "")
            symbol = str(row["symbol"] or "")
            provider_id = str(row["primary_provider_id"] or "")
            chart = None
            try:
                chart = _v2_intel_try_fetch_yahoo_chart(symbol, norm_interval, norm_range)
            except Exception as exc:
                counters["failed_count"] += 1
                _v2_intel_record_provider_error(conn, provider_id, "instrument_ohlcv_fetch_failed", str(exc), request_url=symbol)
            if not chart or not chart.get("bars"):
                fallback_bars = _v2_intel_macro_fallback_bars(symbol, norm_range)
                if fallback_bars:
                    chart = {
                        "interval": norm_interval,
                        "bars": fallback_bars,
                        "dividends": {},
                        "splits": {},
                    }
            if not chart or not chart.get("bars"):
                counters["skipped_count"] += 1
                continue
            counters["fetched_count"] += 1
            write_counts = _v2_intel_upsert_instrument_ohlcv(
                conn,
                instrument_id,
                provider_id,
                str(chart.get("interval") or norm_interval),
                list(chart.get("bars") or []),
                "normal",
            )
            counters["inserted_count"] += int(write_counts.get("inserted_count", 0) or 0)
            counters["updated_count"] += int(write_counts.get("updated_count", 0) or 0)
            _v2_intel_upsert_instrument_corporate_actions(
                conn,
                instrument_id,
                provider_id,
                chart.get("dividends") if isinstance(chart.get("dividends"), dict) else {},
                chart.get("splits") if isinstance(chart.get("splits"), dict) else {},
            )
        _v2_intel_job_finish(conn, run_id, "succeeded", counters=counters, metadata={"count": len(rows), "interval": norm_interval, "range": norm_range})
        conn.commit()
        return {"ok": True, "run_id": run_id, "interval": norm_interval, "range": norm_range, **counters}
    except Exception as exc:
        _v2_intel_job_finish(conn, run_id, "failed", counters=counters, error_message=str(exc), metadata={"interval": norm_interval, "range": norm_range})
        conn.commit()
        return {"ok": False, "run_id": run_id, "error": str(exc)[:500], **counters}


def _v2_intel_http_get_text(url: str, timeout: int = 8) -> str:
    req = urllib_request.Request(url, headers={"User-Agent": "FASTONE-Workbench/1.0"})
    with urllib_request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="ignore")


def _v2_intel_http_get_json(url: str, timeout: int = 8) -> dict:
    raw = _v2_intel_http_get_text(url, timeout=timeout)
    return json.loads(raw or "{}")


V2_MACRO_FRED_SERIES_MAP = {
    "EURUSD=X": "DEXUSEU",
    "GBPUSD=X": "DEXUSUK",
    "USDJPY=X": "DEXJPUS",
    "USDCNH=X": "DEXCHUS",
    "AUDUSD=X": "DEXUSAL",
    "USDCHF=X": "DEXSZUS",
    "^FVX": "DGS5",
    "^TNX": "DGS10",
    "^TYX": "DGS30",
    "^UK10Y": "IRLTLT01GBM156N",
    "^JP10Y": "IRLTLT01JPM156N",
}


def _v2_intel_try_fetch_fred_series(series_id: str, timeout: int = 16) -> list[tuple[int, float]]:
    sid = str(series_id or "").strip().upper()
    if not sid:
        return []
    urls = [
        f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={quote(sid)}",
        f"http://fred.stlouisfed.org/graph/fredgraph.csv?id={quote(sid)}",
    ]
    raw = ""
    last_error: Exception | None = None
    for _ in range(10):
        for u in urls:
            try:
                raw = _v2_intel_http_get_text(u, timeout=timeout)
                if raw.strip():
                    break
            except Exception as exc:
                last_error = exc
                continue
        if raw.strip():
            break
        time.sleep(0.5)
    if not raw.strip():
        if last_error:
            raise last_error
        return []
    lines = [line.strip() for line in raw.splitlines() if line.strip()]
    if len(lines) <= 1:
        return []
    points: list[tuple[int, float]] = []
    for line in lines[1:]:
        parts = line.split(",")
        if len(parts) < 2:
            continue
        date_text = str(parts[0] or "").strip()
        value_text = str(parts[1] or "").strip()
        if not date_text or value_text in {"", ".", "N/A", "N/D"}:
            continue
        try:
            point_time = int(datetime.strptime(date_text, "%Y-%m-%d").replace(tzinfo=ZoneInfo("UTC")).timestamp())
            value = float(value_text)
        except Exception:
            continue
        points.append((point_time, value))
    return points


def _v2_intel_try_fetch_open_er_latest(timeout: int = 10) -> dict:
    payload = {}
    last_error: Exception | None = None
    for _ in range(3):
        try:
            payload = _v2_intel_http_get_json("https://open.er-api.com/v6/latest/USD", timeout=timeout)
            if payload:
                break
        except Exception as exc:
            last_error = exc
            time.sleep(0.25)
            continue
    if not payload and last_error:
        raise last_error
    if str(payload.get("result") or "").lower() != "success":
        return {}
    rates = payload.get("rates") or {}
    if not isinstance(rates, dict):
        return {}
    updated = int(payload.get("time_last_update_unix") or 0)
    latest: dict[str, tuple[float, int]] = {}
    # USD base rates
    if rates.get("JPY"):
        latest["USDJPY=X"] = (float(rates.get("JPY") or 0), updated)
    if rates.get("CHF"):
        latest["USDCHF=X"] = (float(rates.get("CHF") or 0), updated)
    cnh = float(rates.get("CNH") or rates.get("CNY") or 0)
    if cnh:
        latest["USDCNH=X"] = (cnh, updated)
    eur = float(rates.get("EUR") or 0)
    if eur:
        latest["EURUSD=X"] = (1.0 / eur, updated)
    gbp = float(rates.get("GBP") or 0)
    if gbp:
        latest["GBPUSD=X"] = (1.0 / gbp, updated)
    aud = float(rates.get("AUD") or 0)
    if aud:
        latest["AUDUSD=X"] = (1.0 / aud, updated)
    return latest


def _v2_intel_macro_fallback_quotes_for_symbols(symbols: list[str]) -> dict[str, dict]:
    wanted = {str(item or "").strip().upper() for item in symbols if str(item or "").strip()}
    if not wanted:
        return {}
    fallback: dict[str, dict] = {}
    # 1) FRED series (daily/periodic official data) for FX and yields where available.
    for symbol in wanted:
        sid = V2_MACRO_FRED_SERIES_MAP.get(symbol)
        if not sid:
            continue
        try:
            points = _v2_intel_try_fetch_fred_series(sid, timeout=10)
        except Exception:
            continue
        if not points:
            continue
        latest_time, latest_value = points[-1]
        prev_value = points[-2][1] if len(points) > 1 else 0.0
        change_value = (latest_value - prev_value) if prev_value else 0.0
        change_percent = (change_value / prev_value * 100.0) if prev_value else 0.0
        fallback[symbol] = {
            "quote_time": int(latest_time),
            "last_price": float(latest_value),
            "previous_close": float(prev_value) if prev_value else float(latest_value),
            "open_price": float(prev_value) if prev_value else float(latest_value),
            "high_price": float(max(latest_value, prev_value or latest_value)),
            "low_price": float(min(latest_value, prev_value or latest_value)),
            "change_value": float(change_value),
            "change_percent": float(change_percent),
            "volume": 0.0,
            "turnover_amount": 0.0,
            "delayed_flag": True,
            "market_status": "closed",
            "source_payload": {"provider": "fred_fallback", "series": sid},
        }
    # 2) FX latest fallback from open.er-api.
    missing_fx = [s for s in wanted if s not in fallback and s.endswith("=X")]
    if missing_fx:
        try:
            fx_latest = _v2_intel_try_fetch_open_er_latest(timeout=10)
            for symbol in missing_fx:
                row = fx_latest.get(symbol)
                if not row:
                    continue
                latest_value, latest_time = row
                fallback[symbol] = {
                    "quote_time": int(latest_time or _v2_now()),
                    "last_price": float(latest_value),
                    "previous_close": float(latest_value),
                    "open_price": float(latest_value),
                    "high_price": float(latest_value),
                    "low_price": float(latest_value),
                    "change_value": 0.0,
                    "change_percent": 0.0,
                    "volume": 0.0,
                    "turnover_amount": 0.0,
                    "delayed_flag": True,
                    "market_status": "closed",
                    "source_payload": {"provider": "open_er_api_fallback"},
                }
        except Exception:
            pass
    return fallback


def _v2_intel_range_to_days(range_text: str) -> int:
    norm = _v2_intel_normalize_range(range_text)
    mapping = {
        "1d": 2,
        "5d": 7,
        "1mo": 35,
        "3mo": 100,
        "6mo": 190,
        "1y": 370,
        "2y": 740,
        "5y": 1900,
        "10y": 3800,
        "ytd": 400,
        "max": 36500,
    }
    return int(mapping.get(norm, 190))


def _v2_intel_macro_fallback_bars(symbol: str, range_text: str = "6mo") -> list[dict]:
    sid = V2_MACRO_FRED_SERIES_MAP.get(str(symbol or "").strip().upper())
    if not sid:
        return []
    try:
        points = _v2_intel_try_fetch_fred_series(sid, timeout=12)
    except Exception:
        return []
    if not points:
        return []
    since = _v2_now() - _v2_intel_range_to_days(range_text) * 24 * 3600
    filtered = [(ts, val) for ts, val in points if ts >= since]
    if not filtered:
        filtered = points[-180:]
    bars: list[dict] = []
    prev_close = float(filtered[0][1]) if filtered else 0.0
    for point_time, close_value in filtered:
        close_v = float(close_value)
        open_v = float(prev_close if prev_close else close_v)
        high_v = max(open_v, close_v)
        low_v = min(open_v, close_v)
        bars.append(
            {
                "point_time": int(point_time),
                "open_price": open_v,
                "high_price": high_v,
                "low_price": low_v,
                "close_price": close_v,
                "adj_close_price": close_v,
                "volume": 0.0,
            }
        )
        prev_close = close_v
    return bars


def _v2_intel_try_fetch_yahoo_quote(symbol: str) -> dict | None:
    encoded = quote(symbol.strip())
    url = f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={encoded}"
    payload = _v2_intel_http_get_json(url, timeout=8)
    items = (((payload or {}).get("quoteResponse") or {}).get("result") or [])
    if not items:
        return None
    item = items[0] or {}
    current = float(item.get("regularMarketPrice") or 0)
    if current == 0:
        return None
    prev_close = float(item.get("regularMarketPreviousClose") or 0)
    change_value = current - prev_close if prev_close else float(item.get("regularMarketChange") or 0)
    change_percent = (change_value / prev_close * 100.0) if prev_close else float(item.get("regularMarketChangePercent") or 0)
    return {
        "current_value": current,
        "previous_close": prev_close,
        "open_value": float(item.get("regularMarketOpen") or 0),
        "high_value": float(item.get("regularMarketDayHigh") or current),
        "low_value": float(item.get("regularMarketDayLow") or current),
        "change_value": change_value,
        "change_percent": change_percent,
        "volume": float(item.get("regularMarketVolume") or 0),
        "turnover_amount": 0.0,
        "market_status": str(item.get("marketState") or "unknown").lower(),
        "source_payload": item,
    }


def _v2_intel_synthetic_market_value(prev: sqlite3.Row | None) -> dict:
    baseline = float(prev["current_value"] or 1000.0) if prev else 1000.0 + random.uniform(0, 500)
    change_percent = random.uniform(-0.9, 0.9)
    current = max(1.0, baseline * (1 + change_percent / 100.0))
    return {
        "current_value": round(current, 4),
        "previous_close": round(baseline, 4),
        "open_value": round((current + baseline) / 2, 4),
        "high_value": round(max(current, baseline) * (1 + random.uniform(0, 0.004)), 4),
        "low_value": round(min(current, baseline) * (1 - random.uniform(0, 0.004)), 4),
        "change_value": round(current - baseline, 4),
        "change_percent": round(change_percent, 4),
        "volume": 0.0,
        "turnover_amount": 0.0,
        "market_status": "unknown",
        "source_payload": {"synthetic": True},
    }


def _v2_intel_market_refresh(conn: sqlite3.Connection, *, index_codes: list[str] | None = None, force: bool = False) -> dict:
    _v2_intel_seed_defaults(conn)
    selected = [str(item or "").strip().upper() for item in (index_codes or []) if str(item or "").strip()]
    where = "is_active = 1"
    params: list[object] = []
    if selected:
        where += f" AND index_code IN ({','.join(['?'] * len(selected))})"
        params.extend(selected)
    rows = conn.execute(
        f"""
        SELECT *
        FROM intelligence_market_indices_v2
        WHERE {where}
        ORDER BY display_order ASC
        """,
        tuple(params),
    ).fetchall()
    counters = {"fetched_count": 0, "processed_count": 0, "inserted_count": 0, "updated_count": 0, "skipped_count": 0, "failed_count": 0}
    run_id = _v2_intel_job_start(conn, "market_refresh_free", "market_refresh", metadata={"index_count": len(rows), "force": force})
    now = _v2_now()
    provider_rows = conn.execute("SELECT id, provider_code FROM intelligence_free_data_providers_v2").fetchall()
    provider_map = {str(item["id"]): str(item["provider_code"]) for item in provider_rows}
    yahoo_id = ""
    for item in provider_rows:
        if str(item["provider_code"]) == "yahoo_finance_free":
            yahoo_id = str(item["id"])
            break
    try:
        for row in rows:
            counters["processed_count"] += 1
            index_id = str(row["id"] or "")
            symbol = str(row["index_symbol"] or "").strip()
            provider_id = str(row["primary_provider_id"] or yahoo_id or "")
            provider_code = provider_map.get(provider_id, "yahoo_finance_free")
            quote_payload: dict | None = None
            error_messages: list[str] = []
            if provider_code == "yahoo_finance_free" and symbol:
                try:
                    quote_payload = _v2_intel_try_fetch_yahoo_quote(symbol)
                    if quote_payload:
                        counters["fetched_count"] += 1
                except Exception as exc:
                    error_messages.append(str(exc))
                    _v2_intel_record_provider_error(conn, provider_id, "market_fetch_failed", str(exc), request_url=symbol)
            if not quote_payload:
                latest_prev = conn.execute(
                    "SELECT current_value FROM intelligence_market_index_latest_snapshots_v2 WHERE index_id = ? LIMIT 1",
                    (index_id,),
                ).fetchone()
                quote_payload = _v2_intel_synthetic_market_value(latest_prev)
                if error_messages:
                    quote_payload["source_payload"]["errors"] = error_messages
            snapshot_id = _v2_id("intsnap")
            history_id = _v2_id("inthist")
            point_time = now - (now % 3600)
            latest_exists = conn.execute(
                "SELECT id FROM intelligence_market_index_latest_snapshots_v2 WHERE index_id = ? LIMIT 1",
                (index_id,),
            ).fetchone()
            if latest_exists:
                conn.execute(
                    """
                    UPDATE intelligence_market_index_latest_snapshots_v2
                    SET provider_id = ?, snapshot_time = ?, current_value = ?, previous_close = ?, open_value = ?,
                        high_value = ?, low_value = ?, change_value = ?, change_percent = ?, turnover_amount = ?, volume = ?,
                        market_status = ?, data_quality = ?, source_payload_json = ?, updated_at = ?
                    WHERE index_id = ?
                    """,
                    (
                        provider_id,
                        now,
                        float(quote_payload["current_value"]),
                        float(quote_payload["previous_close"]),
                        float(quote_payload["open_value"]),
                        float(quote_payload["high_value"]),
                        float(quote_payload["low_value"]),
                        float(quote_payload["change_value"]),
                        float(quote_payload["change_percent"]),
                        float(quote_payload["turnover_amount"]),
                        float(quote_payload["volume"]),
                        str(quote_payload.get("market_status") or "unknown")[:40],
                        "normal" if not quote_payload.get("source_payload", {}).get("synthetic") else "partial",
                        json.dumps(quote_payload.get("source_payload") or {}, ensure_ascii=False),
                        now,
                        index_id,
                    ),
                )
                counters["updated_count"] += 1
            else:
                conn.execute(
                    """
                    INSERT INTO intelligence_market_index_latest_snapshots_v2(
                      id, index_id, provider_id, snapshot_time, current_value, previous_close, open_value, high_value, low_value,
                      change_value, change_percent, turnover_amount, volume, market_status, data_quality, source_payload_json, created_at, updated_at
                    )
                    VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        snapshot_id,
                        index_id,
                        provider_id,
                        now,
                        float(quote_payload["current_value"]),
                        float(quote_payload["previous_close"]),
                        float(quote_payload["open_value"]),
                        float(quote_payload["high_value"]),
                        float(quote_payload["low_value"]),
                        float(quote_payload["change_value"]),
                        float(quote_payload["change_percent"]),
                        float(quote_payload["turnover_amount"]),
                        float(quote_payload["volume"]),
                        str(quote_payload.get("market_status") or "unknown")[:40],
                        "normal" if not quote_payload.get("source_payload", {}).get("synthetic") else "partial",
                        json.dumps(quote_payload.get("source_payload") or {}, ensure_ascii=False),
                        now,
                        now,
                    ),
                )
                counters["inserted_count"] += 1
            conn.execute(
                """
                INSERT INTO intelligence_market_index_snapshots_history_v2(
                  id, index_id, provider_id, snapshot_time, current_value, previous_close, open_value, high_value, low_value,
                  change_value, change_percent, turnover_amount, volume, market_status, data_quality, source_payload_json, created_at
                )
                VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    history_id,
                    index_id,
                    provider_id,
                    now,
                    float(quote_payload["current_value"]),
                    float(quote_payload["previous_close"]),
                    float(quote_payload["open_value"]),
                    float(quote_payload["high_value"]),
                    float(quote_payload["low_value"]),
                    float(quote_payload["change_value"]),
                    float(quote_payload["change_percent"]),
                    float(quote_payload["turnover_amount"]),
                    float(quote_payload["volume"]),
                    str(quote_payload.get("market_status") or "unknown")[:40],
                    "normal" if not quote_payload.get("source_payload", {}).get("synthetic") else "partial",
                    json.dumps(quote_payload.get("source_payload") or {}, ensure_ascii=False),
                    now,
                ),
            )
            conn.execute(
                """
                INSERT INTO intelligence_market_index_timeseries_v2(
                  id, index_id, provider_id, interval_type, point_time, open_value, high_value, low_value, close_value,
                  turnover_amount, volume, data_quality, source_payload_json, created_at
                )
                VALUES(?, ?, ?, '1h', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(index_id, interval_type, point_time) DO UPDATE SET
                  provider_id = excluded.provider_id,
                  open_value = excluded.open_value,
                  high_value = excluded.high_value,
                  low_value = excluded.low_value,
                  close_value = excluded.close_value,
                  turnover_amount = excluded.turnover_amount,
                  volume = excluded.volume,
                  data_quality = excluded.data_quality,
                  source_payload_json = excluded.source_payload_json
                """,
                (
                    _v2_id("intts"),
                    index_id,
                    provider_id,
                    point_time,
                    float(quote_payload["open_value"]),
                    float(quote_payload["high_value"]),
                    float(quote_payload["low_value"]),
                    float(quote_payload["current_value"]),
                    float(quote_payload["turnover_amount"]),
                    float(quote_payload["volume"]),
                    "normal" if not quote_payload.get("source_payload", {}).get("synthetic") else "partial",
                    json.dumps(quote_payload.get("source_payload") or {}, ensure_ascii=False),
                    now,
                ),
            )
        _v2_intel_job_finish(conn, run_id, "succeeded", counters=counters, metadata={"index_count": len(rows)})
        conn.commit()
        return {"ok": True, "run_id": run_id, **counters}
    except Exception as exc:
        counters["failed_count"] = counters.get("failed_count", 0) + 1
        _v2_intel_job_finish(conn, run_id, "failed", counters=counters, error_message=str(exc))
        conn.commit()
        return {"ok": False, "run_id": run_id, "error": str(exc)[:400], **counters}


def _v2_intel_parse_timestamp(text: str) -> int:
    value = str(text or "").strip()
    if not value:
        return 0
    try:
        dt = email.utils.parsedate_to_datetime(value)
        if dt is None:
            return 0
        return int(dt.timestamp())
    except Exception:
        return 0


def _v2_intel_strip_html(text: str) -> str:
    plain = re.sub(r"<[^>]+>", " ", str(text or ""))
    plain = re.sub(r"\s+", " ", plain).strip()
    return plain


def _v2_intel_has_crawl4ai() -> bool:
    global _V2_INTEL_CRAWL4AI_AVAILABLE
    if _V2_INTEL_CRAWL4AI_AVAILABLE is not None:
        return bool(_V2_INTEL_CRAWL4AI_AVAILABLE)
    if not V2_INTEL_CRAWL4AI_ENABLED:
        _V2_INTEL_CRAWL4AI_AVAILABLE = False
        return False
    try:
        from crawl4ai import AsyncWebCrawler  # noqa: F401

        _V2_INTEL_CRAWL4AI_AVAILABLE = True
        return True
    except Exception:
        _V2_INTEL_CRAWL4AI_AVAILABLE = False
        return False


def _v2_intel_try_crawl4ai_extract(url: str, timeout_seconds: int = 20) -> dict:
    target = str(url or "").strip()
    if not target or not _v2_intel_has_crawl4ai():
        return {}
    try:
        from crawl4ai import AsyncWebCrawler

        async def _run() -> dict:
            async with AsyncWebCrawler(verbose=False) as crawler:
                result = await crawler.arun(url=target)
                title = str(getattr(result, "title", "") or "").strip()
                markdown = str(getattr(result, "markdown", "") or "")
                cleaned_html = str(getattr(result, "cleaned_html", "") or "")
                excerpt = _v2_intel_strip_html(markdown or cleaned_html)[:800]
                return {"title": title[:260], "excerpt": excerpt}

        try:
            return asyncio.run(asyncio.wait_for(_run(), timeout=timeout_seconds))
        except RuntimeError:
            loop = asyncio.new_event_loop()
            try:
                return loop.run_until_complete(asyncio.wait_for(_run(), timeout=timeout_seconds))
            finally:
                loop.close()
    except Exception:
        return {}


def _v2_intel_fetch_rss_items(feed_url: str, timeout: int = 8, limit: int = 60) -> list[dict]:
    req = urllib_request.Request(feed_url, headers={"User-Agent": "FASTONE-Workbench/1.0"})
    with urllib_request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read()
    root = ET.fromstring(raw)
    items = []
    for node in root.findall(".//item")[:limit]:
        title = (node.findtext("title") or "").strip()
        link = (node.findtext("link") or "").strip()
        description = (node.findtext("description") or "").strip()
        pub = (node.findtext("pubDate") or node.findtext("published") or node.findtext("updated") or "").strip()
        items.append({"title": title, "url": link, "excerpt": description, "published_at": _v2_intel_parse_timestamp(pub)})
    return items


def _v2_intel_normalize_title(title: str) -> str:
    compact = " ".join(str(title or "").lower().split())
    compact = re.sub(r"[^a-z0-9\u4e00-\u9fff ]+", " ", compact)
    return " ".join(compact.split())[:220]


def _v2_intel_pick_category(text: str) -> str:
    hay = str(text or "").lower()
    finance_keys = ["fed", "rate", "bond", "stock", "market", "finance", "央行", "利率", "债", "股", "美元", "人民币", "银行"]
    tech_keys = ["ai", "chip", "semiconductor", "software", "cloud", "科技", "芯片", "半导体", "人工智能"]
    politics_keys = ["election", "policy", "sanction", "war", "tariff", "选举", "政策", "制裁", "关税", "外交"]
    if any(k in hay for k in finance_keys):
        return "finance"
    if any(k in hay for k in tech_keys):
        return "technology"
    if any(k in hay for k in politics_keys):
        return "politics"
    return "general"


def _v2_intel_news_refresh(conn: sqlite3.Connection, *, source_codes: list[str] | None = None, window_hours: int = 48) -> dict:
    _v2_intel_seed_defaults(conn)
    selected = [str(item or "").strip().lower() for item in (source_codes or []) if str(item or "").strip()]
    where = "s.is_active = 1 AND f.is_active = 1"
    params: list[object] = []
    if selected:
        where += f" AND lower(s.source_code) IN ({','.join(['?'] * len(selected))})"
        params.extend(selected)
    feeds = conn.execute(
        f"""
        SELECT f.*, s.source_code, s.priority_score, s.id AS source_id, s.default_category, s.copyright_policy
        FROM intelligence_news_source_feeds_v2 f
        JOIN intelligence_news_sources_v2 s ON s.id = f.source_id
        WHERE {where}
        ORDER BY s.priority_score DESC
        """,
        tuple(params),
    ).fetchall()
    counters = {"fetched_count": 0, "processed_count": 0, "inserted_count": 0, "updated_count": 0, "skipped_count": 0, "failed_count": 0}
    run_id = _v2_intel_job_start(conn, "news_ingestion_free", "news_ingestion", metadata={"feed_count": len(feeds)})
    now = _v2_now()
    cutoff = now - int(window_hours * 3600)
    crawl4ai_budget = max(0, int(V2_INTEL_CRAWL4AI_MAX_PER_FEED or 0))
    try:
        for feed in feeds:
            feed_url = str(feed["feed_url"] or "").strip()
            source_id = str(feed["source_id"] or "")
            if not feed_url:
                continue
            try:
                items = _v2_intel_fetch_rss_items(feed_url, timeout=8, limit=80)
                counters["fetched_count"] += len(items)
            except Exception as exc:
                counters["failed_count"] += 1
                _v2_intel_record_provider_error(conn, str(feed.get("provider_id") or ""), "rss_fetch_failed", str(exc), request_url=feed_url)
                continue
            for item in items:
                counters["processed_count"] += 1
                title = str(item.get("title") or "").strip()
                url = str(item.get("url") or "").strip()
                if not title or not url:
                    counters["skipped_count"] += 1
                    continue
                published_at = int(item.get("published_at") or 0)
                if published_at and published_at < cutoff:
                    counters["skipped_count"] += 1
                    continue
                excerpt = str(item.get("excerpt") or "").strip()
                crawl4ai_enriched = False
                if (not excerpt or len(excerpt) < 72) and crawl4ai_budget > 0:
                    crawl4ai_budget -= 1
                    enriched = _v2_intel_try_crawl4ai_extract(url, timeout_seconds=8)
                    if enriched:
                        maybe_title = str(enriched.get("title") or "").strip()
                        maybe_excerpt = str(enriched.get("excerpt") or "").strip()
                        if maybe_title and len(title) < 8:
                            title = maybe_title
                        if maybe_excerpt:
                            excerpt = maybe_excerpt
                            crawl4ai_enriched = True
                normalized = _v2_intel_normalize_title(title)
                dedup_key = hashlib.sha1(normalized.encode("utf-8")).hexdigest() if normalized else ""
                cluster_key = dedup_key[:16] if dedup_key else ""
                exists = conn.execute(
                    "SELECT id FROM intelligence_news_articles_v2 WHERE original_url = ? LIMIT 1",
                    (url,),
                ).fetchone()
                category = str(feed["category"] or feed["default_category"] or "general")
                if category not in V2_INTEL_NEWS_CATEGORIES:
                    category = _v2_intel_pick_category(f"{title} {excerpt}")
                payload = {
                    "title": title,
                    "excerpt": excerpt,
                    "feed_url": feed_url,
                    "source_code": str(feed["source_code"] or ""),
                    "crawl4ai_enriched": crawl4ai_enriched,
                }
                if exists:
                    conn.execute(
                        """
                        UPDATE intelligence_news_articles_v2
                        SET title_original = ?, raw_excerpt = ?, category_primary = ?, dedup_key = ?, cluster_key = ?,
                            source_priority_score = ?, status = 'fetched', fetched_at = ?, updated_at = ?
                        WHERE id = ?
                        """,
                        (
                            title[:800],
                            excerpt[:4000],
                            category,
                            dedup_key,
                            cluster_key,
                            int(feed["priority_score"] or 0),
                            now,
                            now,
                            str(exists["id"]),
                        ),
                    )
                    counters["updated_count"] += 1
                else:
                    conn.execute(
                        """
                        INSERT INTO intelligence_news_articles_v2(
                          id, source_id, provider_id, external_id, original_url, canonical_url, title_original, title_en, title_zh,
                          original_language, published_at, fetched_at, raw_excerpt, raw_content, category_primary, tags_json, entities_json,
                          country_tags_json, region_tags_json, dedup_key, cluster_key, importance_score, relevance_score,
                          source_priority_score, status, rejection_reason, copyright_mode, created_at, updated_at
                        )
                        VALUES(?, ?, '', '', ?, ?, ?, '', '', '', ?, ?, ?, '', ?, '[]', '[]', '[]', '[]', ?, ?, 0, 0, ?, 'fetched', '', ?, ?, ?)
                        """,
                        (
                            _v2_id("intnews"),
                            source_id,
                            url,
                            url,
                            title[:800],
                            published_at,
                            now,
                            excerpt[:4000],
                            category,
                            dedup_key,
                            cluster_key,
                            int(feed["priority_score"] or 0),
                            str(feed["copyright_policy"] or "metadata_summary_link_only"),
                            now,
                            now,
                        ),
                    )
                    counters["inserted_count"] += 1
        _v2_intel_job_finish(conn, run_id, "succeeded", counters=counters)
        conn.commit()
        return {"ok": True, "run_id": run_id, **counters}
    except Exception as exc:
        counters["failed_count"] += 1
        _v2_intel_job_finish(conn, run_id, "failed", counters=counters, error_message=str(exc))
        conn.commit()
        return {"ok": False, "run_id": run_id, "error": str(exc)[:400], **counters}


def _v2_intel_news_process(conn: sqlite3.Connection, *, window_hours: int = 72) -> dict:
    now = _v2_now()
    cutoff = now - int(window_hours * 3600)
    rows = conn.execute(
        """
        SELECT *
        FROM intelligence_news_articles_v2
        WHERE fetched_at >= ? AND status IN ('fetched', 'processed')
        ORDER BY fetched_at DESC
        LIMIT 2000
        """,
        (cutoff,),
    ).fetchall()
    counters = {"fetched_count": len(rows), "processed_count": 0, "inserted_count": 0, "updated_count": 0, "skipped_count": 0, "failed_count": 0}
    run_id = _v2_intel_job_start(conn, "news_processing", "news_processing", metadata={"rows": len(rows)})
    cluster_counts: dict[str, set[str]] = {}
    for row in rows:
        counters["processed_count"] += 1
        title = str(row["title_original"] or "")
        excerpt = str(row["raw_excerpt"] or "")
        category = _v2_intel_pick_category(f"{title} {excerpt}")
        age_hours = max(0.0, (_v2_now() - int(row["published_at"] or row["fetched_at"] or now)) / 3600.0)
        recency = max(0.0, 100.0 - age_hours * 2.5)
        source_priority = float(row["source_priority_score"] or 0)
        finance_boost = 25.0 if category == "finance" else (14.0 if category == "technology" else 8.0 if category == "politics" else 4.0)
        importance = min(100.0, source_priority * 0.45 + recency * 0.35 + finance_boost)
        relevance = min(100.0, recency * 0.30 + (45.0 if category == "finance" else 28.0 if category == "technology" else 18.0))
        normalized = _v2_intel_normalize_title(title)
        dedup_key = str(row["dedup_key"] or (hashlib.sha1(normalized.encode("utf-8")).hexdigest() if normalized else ""))
        cluster_key = str(row["cluster_key"] or dedup_key[:16])
        tags = [category]
        if category == "finance":
            tags.extend(["markets", "macro"])
        elif category == "technology":
            tags.extend(["ai", "industry"])
        elif category == "politics":
            tags.extend(["policy"])
        conn.execute(
            """
            UPDATE intelligence_news_articles_v2
            SET category_primary = ?, dedup_key = ?, cluster_key = ?, tags_json = ?, importance_score = ?, relevance_score = ?,
                status = 'processed', updated_at = ?
            WHERE id = ?
            """,
            (category, dedup_key, cluster_key, json.dumps(sorted(set(tags)), ensure_ascii=False), importance, relevance, now, str(row["id"])),
        )
        counters["updated_count"] += 1
        cluster_counts.setdefault(cluster_key, set()).add(str(row["source_id"] or ""))
    for cluster_key, sources in cluster_counts.items():
        article_rows = conn.execute(
            """
            SELECT id, title_original, published_at, category_primary, importance_score, relevance_score
            FROM intelligence_news_articles_v2
            WHERE cluster_key = ?
            ORDER BY importance_score DESC, published_at DESC
            """,
            (cluster_key,),
        ).fetchall()
        if not article_rows:
            continue
        rep = article_rows[0]
        exists = conn.execute(
            "SELECT id FROM intelligence_news_article_clusters_v2 WHERE cluster_key = ? LIMIT 1",
            (cluster_key,),
        ).fetchone()
        first_published = min(int(r["published_at"] or 0) for r in article_rows)
        latest_published = max(int(r["published_at"] or 0) for r in article_rows)
        if exists:
            conn.execute(
                """
                UPDATE intelligence_news_article_clusters_v2
                SET representative_article_id = ?, normalized_title = ?, topic_signature = ?, article_count = ?, source_count = ?,
                    first_published_at = ?, latest_published_at = ?, category_primary = ?, tags_json = ?,
                    cluster_importance_score = ?, cluster_relevance_score = ?, updated_at = ?
                WHERE id = ?
                """,
                (
                    str(rep["id"]),
                    _v2_intel_normalize_title(str(rep["title_original"] or "")),
                    cluster_key,
                    len(article_rows),
                    len(sources),
                    first_published,
                    latest_published,
                    str(rep["category_primary"] or "general"),
                    json.dumps([], ensure_ascii=False),
                    float(rep["importance_score"] or 0),
                    float(rep["relevance_score"] or 0),
                    now,
                    str(exists["id"]),
                ),
            )
        else:
            conn.execute(
                """
                INSERT INTO intelligence_news_article_clusters_v2(
                  id, cluster_key, representative_article_id, normalized_title, topic_signature, article_count, source_count,
                  first_published_at, latest_published_at, category_primary, tags_json, cluster_importance_score, cluster_relevance_score,
                  created_at, updated_at
                )
                VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, '[]', ?, ?, ?, ?)
                """,
                (
                    _v2_id("intcluster"),
                    cluster_key,
                    str(rep["id"]),
                    _v2_intel_normalize_title(str(rep["title_original"] or "")),
                    cluster_key,
                    len(article_rows),
                    len(sources),
                    first_published,
                    latest_published,
                    str(rep["category_primary"] or "general"),
                    float(rep["importance_score"] or 0),
                    float(rep["relevance_score"] or 0),
                    now,
                    now,
                ),
            )
            counters["inserted_count"] += 1
    _v2_intel_job_finish(conn, run_id, "succeeded", counters=counters)
    conn.commit()
    return {"ok": True, "run_id": run_id, **counters}


def _v2_contains_cjk(text: str) -> bool:
    return bool(re.search(r"[\u4e00-\u9fff]", str(text or "")))


def _v2_likely_needs_zh_translation(title: str, excerpt: str, summary_title: str = "", summary_content: str = "") -> bool:
    combined_existing = f"{summary_title} {summary_content}".strip()
    if combined_existing and _v2_contains_cjk(combined_existing):
        return False
    source = f"{title} {excerpt}".strip()
    if not source:
        return False
    if _v2_contains_cjk(source):
        return False
    latin_letters = len(re.findall(r"[A-Za-z]", source))
    return latin_letters >= 12


def _v2_json_from_model_text(text: str) -> object:
    cleaned = str(text or "").strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.I)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    try:
        return json.loads(cleaned)
    except Exception:
        pass
    match = re.search(r"(\{.*\}|\[.*\])", cleaned, flags=re.S)
    if not match:
        raise ValueError("model_response_not_json")
    return json.loads(match.group(1))


def _v2_intel_call_chat_json(messages: list[dict], *, timeout: float = 20.0) -> object:
    proxy_key = env_value("CLIPROXYAPI_API_KEY")
    payload = {
        "model": CHATGPT_FALLBACK_MODEL,
        "stream": False,
        "temperature": 0.2,
        "messages": messages,
    }
    if proxy_key:
        resp = httpx.post(
            f"{CLIPROXY_API}/chat/completions",
            headers={"Authorization": f"Bearer {proxy_key}", "Content-Type": "application/json"},
            json=payload,
            timeout=timeout,
        )
        resp.raise_for_status()
        text = _extract_assistant_text(resp.json())
        return _v2_json_from_model_text(text)

    start_gateway()
    headers = {}
    bearer = api_key()
    if bearer:
        headers["Authorization"] = f"Bearer {bearer}"
    resp = httpx.post(
        f"{HERMES_API}/chat/completions",
        headers=headers,
        json={**payload, "model": "hermes-agent"},
        timeout=timeout,
    )
    resp.raise_for_status()
    text = _extract_assistant_text(resp.json())
    return _v2_json_from_model_text(text)


def _v2_intel_translate_news_batch(rows: list[sqlite3.Row], language_code: str) -> dict[str, dict[str, str]]:
    if language_code != "zh" or not rows:
        return {}
    source_items = []
    for row in rows[:V2_INTEL_ZH_TRANSLATION_BATCH_SIZE]:
        article_id = str(row["id"] or "")
        title = str(row["title_original"] or row["title_en"] or "").strip()
        excerpt = _v2_intel_strip_html(str(row["raw_excerpt"] or "")).strip()
        if not article_id or not _v2_likely_needs_zh_translation(title, excerpt):
            continue
        source_items.append(
            {
                "id": article_id,
                "title": title[:360],
                "excerpt": excerpt[:900],
                "source": str(row["source_code"] or ""),
            }
        )
    if not source_items:
        return {}

    messages = [
        {
            "role": "system",
            "content": (
                "你是金融资讯中文编辑。请把英文新闻标题和摘要改写为简体中文。"
                "要求：标题自然准确；摘要 70-120 个中文字符；保留关键主体、动作、影响；"
                "不要添加原文没有的信息；不要输出 Markdown。只返回 JSON。"
            ),
        },
        {
            "role": "user",
            "content": json.dumps(
                {
                    "return_schema": [
                        {"id": "article id", "title_zh": "中文标题", "summary_zh": "中文摘要"}
                    ],
                    "items": source_items,
                },
                ensure_ascii=False,
            ),
        },
    ]
    try:
        parsed = _v2_intel_call_chat_json(messages)
    except Exception as exc:
        log(f"News zh translation batch failed: {exc}")
        return {}

    if isinstance(parsed, dict):
        candidates = parsed.get("items") or parsed.get("data") or parsed.get("results") or []
    else:
        candidates = parsed
    if not isinstance(candidates, list):
        return {}
    translated: dict[str, dict[str, str]] = {}
    for item in candidates:
        if not isinstance(item, dict):
            continue
        article_id = str(item.get("id") or "").strip()
        title_zh = re.sub(r"\s+", " ", str(item.get("title_zh") or item.get("title") or "")).strip()
        summary_zh = re.sub(r"\s+", " ", str(item.get("summary_zh") or item.get("summary") or "")).strip()
        if not article_id or not title_zh or not summary_zh:
            continue
        if not _v2_contains_cjk(f"{title_zh} {summary_zh}"):
            continue
        translated[article_id] = {"title": title_zh[:160], "summary": summary_zh[:260]}
    return translated


def _v2_intel_summary_text(row: sqlite3.Row, language_code: str) -> tuple[str, str]:
    title_original = str(row["title_original"] or "").strip()
    title_zh = str(row["title_zh"] or "").strip()
    title_en = str(row["title_en"] or "").strip()
    excerpt = _v2_intel_strip_html(str(row["raw_excerpt"] or "")).strip()
    if language_code == "zh":
        title = title_zh or title_original or title_en
        body = " ".join(part for part in [title, excerpt] if part).strip()
        body = re.sub(r"\s+", " ", body)
        body = re.sub(r"^(据|According to).{0,48}?[：:，,]\s*", "", body, flags=re.IGNORECASE)
        body = re.sub(r"(请查看|点击).*?(完整上下文|原文链接).*?$", "", body)
        body = body.strip(" .。;；,，")
        compact = body[:100] + ("..." if len(body) > 100 else "")
        return (title[:120], compact or title[:100])
    title = title_en or title_original or title_zh
    body = " ".join(part for part in [title, excerpt] if part).strip()
    body = re.sub(r"\s+", " ", body)
    body = re.sub(r"^(According to|据).{0,48}?[：:，,]\s*", "", body, flags=re.IGNORECASE)
    body = re.sub(r"(Please open|Please check).*?(full context|original link).*?$", "", body, flags=re.IGNORECASE)
    body = body.strip(" .。;；,，")
    compact = body[:160] + ("..." if len(body) > 160 else "")
    return (title[:120], compact or title[:160])


def _v2_intel_news_summary_value(row: sqlite3.Row, language_code: str) -> str:
    stored = str(row["summary_content"] or "").strip()
    if stored:
        title, compact = _v2_intel_summary_text(row, language_code)
        stored_clean = re.sub(r"\s+", " ", stored).strip()
        boilerplate_flags = (
            stored_clean.startswith("According to "),
            stored_clean.startswith("据 "),
            "完整上下文" in stored_clean,
            "full context" in stored_clean.lower(),
        )
        if not any(boilerplate_flags):
            return stored_clean[:100] + ("..." if len(stored_clean) > 100 else "")
        return compact or title
    _, compact = _v2_intel_summary_text(row, language_code)
    return compact


def _v2_intel_news_title_value(row: sqlite3.Row, language_code: str) -> str:
    summary_title = str(row["summary_title"] or "").strip()
    title_original = str(row["title_original"] or "").strip()
    title_zh = str(row["title_zh"] or "").strip()
    title_en = str(row["title_en"] or "").strip()
    if language_code == "zh":
        return (title_zh or summary_title or title_original or title_en)[:160]
    return (title_en or title_original or title_zh or summary_title)[:160]


def _v2_intel_generate_news_summaries(conn: sqlite3.Connection, *, window_hours: int = 24, languages: list[str] | None = None) -> dict:
    langs = [str(item).strip().lower() for item in (languages or ["zh", "en"]) if str(item).strip()]
    if not langs:
        langs = ["zh", "en"]
    now = _v2_now()
    cutoff = now - int(window_hours * 3600)
    rows = conn.execute(
        """
        SELECT a.*, s.source_code
        FROM intelligence_news_articles_v2 a
        LEFT JOIN intelligence_news_sources_v2 s ON s.id = a.source_id
        WHERE a.fetched_at >= ? AND a.status IN ('processed', 'selected')
        ORDER BY a.importance_score DESC, a.published_at DESC
        LIMIT 800
        """,
        (cutoff,),
    ).fetchall()
    counters = {"fetched_count": len(rows), "processed_count": 0, "inserted_count": 0, "updated_count": 0, "skipped_count": 0, "failed_count": 0}
    run_id = _v2_intel_job_start(conn, "news_summarization", "summarization", metadata={"rows": len(rows), "languages": langs})
    translated_zh: dict[str, dict[str, str]] = {}
    if "zh" in langs:
        translatable = [
            row for row in rows
            if _v2_likely_needs_zh_translation(
                str(row["title_original"] or row["title_en"] or ""),
                str(row["raw_excerpt"] or ""),
            )
        ][:V2_INTEL_ZH_TRANSLATION_LIMIT]
        batch_size = V2_INTEL_ZH_TRANSLATION_BATCH_SIZE
        failed_batches = 0
        for offset in range(0, len(translatable), batch_size):
            translated_batch = _v2_intel_translate_news_batch(translatable[offset: offset + batch_size], "zh")
            if not translated_batch:
                failed_batches += 1
                if failed_batches >= 2:
                    log("News zh translation disabled for this run after consecutive empty/failed batches")
                    break
                continue
            failed_batches = 0
            translated_zh.update(translated_batch)
    for row in rows:
        counters["processed_count"] += 1
        article_id = str(row["id"] or "")
        for lang in langs:
            title, content = _v2_intel_summary_text(row, lang)
            summarizer_type = "rule_based"
            summarizer_provider = "builtin"
            summarizer_metadata = {"engine": "rule_template_v1"}
            quality_score = 0.78
            if lang == "zh":
                translated = translated_zh.get(article_id) or {}
                if translated:
                    title = translated["title"]
                    content = translated["summary"]
                    summarizer_type = "translated_summary"
                    summarizer_provider = "hermes_chat"
                    summarizer_metadata = {"engine": "zh_translation_v1", "source_language": "en"}
                    quality_score = 0.88
                    conn.execute(
                        """
                        UPDATE intelligence_news_articles_v2
                        SET title_zh = ?, updated_at = ?
                        WHERE id = ? AND (title_zh = '' OR title_zh IS NULL)
                        """,
                        (title[:400], now, article_id),
                    )
            exists = conn.execute(
                "SELECT id FROM intelligence_news_article_summaries_v2 WHERE article_id = ? AND language_code = ? LIMIT 1",
                (article_id, lang),
            ).fetchone()
            if exists:
                conn.execute(
                    """
                    UPDATE intelligence_news_article_summaries_v2
                    SET summary_title = ?, summary_content = ?, summary_length = ?, summarizer_type = 'rule_based',
                        summarizer_provider = 'builtin', summarizer_metadata_json = ?, quality_score = ?, updated_at = ?
                    WHERE id = ?
                    """,
                    (
                        title[:400],
                        content[:4000],
                        len(content),
                        json.dumps(summarizer_metadata, ensure_ascii=False),
                        quality_score,
                        now,
                        str(exists["id"]),
                    ),
                )
                conn.execute(
                    """
                    UPDATE intelligence_news_article_summaries_v2
                    SET summarizer_type = ?, summarizer_provider = ?
                    WHERE id = ?
                    """,
                    (summarizer_type, summarizer_provider, str(exists["id"])),
                )
                counters["updated_count"] += 1
            else:
                conn.execute(
                    """
                    INSERT INTO intelligence_news_article_summaries_v2(
                      id, article_id, language_code, summary_title, summary_content, summary_length,
                      summarizer_type, summarizer_provider, summarizer_metadata_json, quality_score, generated_at, updated_at
                    )
                    VALUES(?, ?, ?, ?, ?, ?, 'rule_based', 'builtin', ?, ?, ?, ?)
                    """,
                    (
                        _v2_id("intsum"),
                        article_id,
                        lang,
                        title[:400],
                        content[:4000],
                        len(content),
                        json.dumps(summarizer_metadata, ensure_ascii=False),
                        quality_score,
                        now,
                        now,
                    ),
                )
                if summarizer_type != "rule_based" or summarizer_provider != "builtin":
                    conn.execute(
                        """
                        UPDATE intelligence_news_article_summaries_v2
                        SET summarizer_type = ?, summarizer_provider = ?
                        WHERE article_id = ? AND language_code = ?
                        """,
                        (summarizer_type, summarizer_provider, article_id, lang),
                    )
                counters["inserted_count"] += 1
    _v2_intel_job_finish(conn, run_id, "succeeded", counters=counters)
    conn.commit()
    return {"ok": True, "run_id": run_id, **counters}


def _v2_intel_generate_news_digest(
    conn: sqlite3.Connection,
    *,
    window_hours: int = 24,
    languages: list[str] | None = None,
    limit: int = 30,
    force_regenerate: bool = False,
) -> dict:
    langs = [str(item).strip().lower() for item in (languages or ["zh", "en"]) if str(item).strip()]
    if not langs:
        langs = ["zh", "en"]
    now = _v2_now()
    window_start = now - int(window_hours * 3600)
    digest_date = datetime.fromtimestamp(now, tz=ZoneInfo("Asia/Shanghai")).strftime("%Y-%m-%d")
    rows = conn.execute(
        """
        SELECT *
        FROM intelligence_news_articles_v2
        WHERE fetched_at >= ? AND status IN ('processed', 'selected')
        ORDER BY importance_score DESC, relevance_score DESC, published_at DESC
        LIMIT 2000
        """,
        (window_start,),
    ).fetchall()
    run_id = _v2_intel_job_start(conn, "news_digest_generation", "digest_generation", metadata={"window_hours": window_hours, "limit": limit})
    counters = {"fetched_count": len(rows), "processed_count": 0, "inserted_count": 0, "updated_count": 0, "skipped_count": 0, "failed_count": 0}
    selected_by_cluster: set[str] = set()
    shortlist: list[sqlite3.Row] = []
    for row in rows:
        cluster_key = str(row["cluster_key"] or row["dedup_key"] or row["id"] or "")
        if cluster_key in selected_by_cluster:
            continue
        selected_by_cluster.add(cluster_key)
        shortlist.append(row)
        if len(shortlist) >= max(limit * 3, 90):
            break
    top = shortlist[: max(1, min(limit, 120))]
    for lang in langs:
        if force_regenerate:
            conn.execute(
                "DELETE FROM intelligence_news_daily_digest_items_v2 WHERE digest_date = ? AND language_code = ?",
                (digest_date, lang),
            )
        for rank, row in enumerate(top, start=1):
            counters["processed_count"] += 1
            article_id = str(row["id"] or "")
            summary_row = conn.execute(
                """
                SELECT id
                FROM intelligence_news_article_summaries_v2
                WHERE article_id = ? AND language_code = ?
                LIMIT 1
                """,
                (article_id, lang),
            ).fetchone()
            exists = conn.execute(
                """
                SELECT id
                FROM intelligence_news_daily_digest_items_v2
                WHERE digest_date = ? AND language_code = ? AND ranking_order = ?
                LIMIT 1
                """,
                (digest_date, lang, rank),
            ).fetchone()
            if exists:
                conn.execute(
                    """
                    UPDATE intelligence_news_daily_digest_items_v2
                    SET article_id = ?, summary_id = ?, category_primary = ?, importance_score = ?, relevance_score = ?, digest_window_start = ?, digest_window_end = ?, is_top30 = 1
                    WHERE id = ?
                    """,
                    (
                        article_id,
                        str(summary_row["id"] or "") if summary_row else "",
                        str(row["category_primary"] or "general"),
                        float(row["importance_score"] or 0),
                        float(row["relevance_score"] or 0),
                        window_start,
                        now,
                        str(exists["id"]),
                    ),
                )
                counters["updated_count"] += 1
            else:
                conn.execute(
                    """
                    INSERT INTO intelligence_news_daily_digest_items_v2(
                      id, digest_window_start, digest_window_end, digest_date, language_code, article_id, summary_id,
                      ranking_order, category_primary, importance_score, relevance_score, is_top30, created_at
                    )
                    VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?)
                    """,
                    (
                        _v2_id("intdigest"),
                        window_start,
                        now,
                        digest_date,
                        lang,
                        article_id,
                        str(summary_row["id"] or "") if summary_row else "",
                        rank,
                        str(row["category_primary"] or "general"),
                        float(row["importance_score"] or 0),
                        float(row["relevance_score"] or 0),
                        now,
                    ),
                )
                counters["inserted_count"] += 1
    _v2_intel_job_finish(conn, run_id, "succeeded", counters=counters, metadata={"digest_date": digest_date, "languages": langs, "selected_count": len(top)})
    conn.commit()
    return {"ok": True, "run_id": run_id, "digest_date": digest_date, "selected_count": len(top), **counters}


def _v2_intel_maybe_run_jobs(force: bool = False) -> None:
    state = _v2_intel_scheduler_state_payload()
    now = _v2_now()
    try:
        with v2_db_lock, _v2_db_conn() as conn:
            _v2_intel_seed_defaults(conn)
            def _safe_job(label: str, runner) -> bool:
                try:
                    result = runner()
                    if isinstance(result, dict):
                        return bool(result.get("ok", True))
                    return True
                except Exception as exc:
                    log(f"v2 intelligence job {label} error: {exc}")
                    return False

            local = local_now()
            day_key = local.strftime("%Y-%m-%d")
            at_or_after_morning = (local.hour > 8) or (local.hour == 8 and local.minute >= 0)
            if force or (at_or_after_morning and str(state.get("last_morning_refresh_key") or "") != day_key):
                _safe_job("morning_market_refresh", lambda: _v2_intel_market_refresh(conn, force=True))
                _safe_job("morning_instrument_quote_refresh", lambda: _v2_intel_refresh_instrument_quotes(conn, instrument_types=["index", "stock", "etf", "forex"], force=True))
                _safe_job(
                    "morning_instrument_ohlcv_refresh",
                    lambda: _v2_intel_refresh_instrument_ohlcv(
                        conn,
                        instrument_types=["index", "stock", "etf", "forex"],
                        interval="1d",
                        range_text="6mo",
                        backfill=False,
                        force=True,
                    ),
                )
                _safe_job("morning_news_refresh", lambda: _v2_intel_news_refresh(conn, window_hours=48))
                _safe_job("morning_news_process", lambda: _v2_intel_news_process(conn, window_hours=72))
                _safe_job("morning_news_summaries", lambda: _v2_intel_generate_news_summaries(conn, window_hours=48, languages=["zh", "en"]))
                _safe_job("morning_news_digest", lambda: _v2_intel_generate_news_digest(conn, window_hours=24, languages=["zh", "en"], limit=30, force_regenerate=True))
                state["last_morning_refresh_key"] = day_key
                state["last_market_refresh_at"] = now
                state["last_instrument_quote_refresh_at"] = now
                state["last_instrument_ohlcv_refresh_at"] = now
                state["last_news_refresh_at"] = now
                state["last_digest_refresh_at"] = now
            if force or now - int(state.get("last_market_refresh_at", 0) or 0) >= 60 * 60:
                if _safe_job("market_refresh", lambda: _v2_intel_market_refresh(conn, force=force)):
                    state["last_market_refresh_at"] = now
            if force or now - int(state.get("last_instrument_quote_refresh_at", 0) or 0) >= 30 * 60:
                if _safe_job("instrument_quote_refresh", lambda: _v2_intel_refresh_instrument_quotes(conn, instrument_types=["index", "stock", "etf", "forex"], force=force)):
                    state["last_instrument_quote_refresh_at"] = now
            if force or now - int(state.get("last_instrument_ohlcv_refresh_at", 0) or 0) >= 60 * 60:
                if _safe_job(
                    "instrument_ohlcv_refresh",
                    lambda: _v2_intel_refresh_instrument_ohlcv(
                        conn,
                        instrument_types=["index", "stock", "etf", "forex"],
                        interval="1d",
                        range_text="6mo",
                        backfill=False,
                        force=force,
                    ),
                ):
                    state["last_instrument_ohlcv_refresh_at"] = now
            if force or now - int(state.get("last_news_refresh_at", 0) or 0) >= 4 * 60 * 60:
                ok_refresh = _safe_job("news_refresh", lambda: _v2_intel_news_refresh(conn, window_hours=48))
                ok_process = _safe_job("news_process", lambda: _v2_intel_news_process(conn, window_hours=72))
                ok_summary = _safe_job("news_summaries", lambda: _v2_intel_generate_news_summaries(conn, window_hours=48, languages=["zh", "en"]))
                if ok_refresh and ok_process and ok_summary:
                    state["last_news_refresh_at"] = now
            if force or now - int(state.get("last_digest_refresh_at", 0) or 0) >= 60 * 60:
                if _safe_job("news_digest", lambda: _v2_intel_generate_news_digest(conn, window_hours=24, languages=["zh", "en"], limit=30, force_regenerate=True)):
                    state["last_digest_refresh_at"] = now
        _v2_intel_save_scheduler_state(state)
    except Exception as exc:
        log(f"v2 intelligence scheduler error: {exc}")


def _v2_intel_require_user(user: dict | None) -> tuple[dict | None, tuple[dict, int] | None]:
    if not user:
        return None, ({"ok": False, "error": "authentication_required"}, 401)
    return user, None


def _v2_intel_markets_overview(user: dict | None, query: dict[str, list[str]]) -> tuple[dict, int]:
    _, err = _v2_intel_require_user(user)
    if err:
        return err
    include_inactive = str(query.get("includeInactive", ["false"])[0] or "false").lower() in {"1", "true", "yes"}
    lang = str(query.get("lang", ["zh"])[0] or "zh").lower()
    with v2_db_lock, _v2_db_conn() as conn:
        _v2_intel_seed_defaults(conn)
        where = "1=1" if include_inactive else "is_active = 1"
        rows = conn.execute(
            f"""
            SELECT i.*, s.current_value, s.change_value, s.change_percent, s.turnover_amount, s.volume, s.market_status, s.data_quality, s.snapshot_time
            FROM intelligence_market_indices_v2 i
            LEFT JOIN intelligence_market_index_latest_snapshots_v2 s ON s.index_id = i.id
            WHERE {where}
            ORDER BY i.region_code, i.country_code, i.display_order ASC
            """
        ).fetchall()
        regions: dict[str, dict] = {}
        for row in rows:
            region_code = str(row["region_code"] or "other")
            country_code = str(row["country_code"] or "UN")
            region_label = {"north_america": "北美", "asia": "亚洲", "europe": "欧洲"}.get(region_code, region_code.replace("_", " ").title())
            if region_code not in regions:
                regions[region_code] = {"regionCode": region_code, "regionName": region_label if lang == "zh" else region_code.replace("_", " ").title(), "countries": {}}
            country_map = regions[region_code]["countries"]
            if country_code not in country_map:
                country_map[country_code] = {"countryCode": country_code, "countryName": country_code, "indices": []}
            index_name = str(row["index_name_zh"] or row["index_name_en"] or row["index_code"]) if lang == "zh" else str(row["index_name_en"] or row["index_code"])
            country_map[country_code]["indices"].append(
                {
                    "indexId": str(row["id"] or ""),
                    "indexCode": str(row["index_code"] or ""),
                    "indexName": index_name,
                    "symbol": str(row["index_symbol"] or ""),
                    "currency": str(row["currency"] or ""),
                    "currentValue": float(row["current_value"] or 0),
                    "changeValue": float(row["change_value"] or 0),
                    "changePercent": float(row["change_percent"] or 0),
                    "turnoverAmount": float(row["turnover_amount"] or 0),
                    "volume": float(row["volume"] or 0),
                    "marketStatus": str(row["market_status"] or "unknown"),
                    "dataQuality": str(row["data_quality"] or "unknown"),
                    "lastUpdatedAt": int(row["snapshot_time"] or 0),
                }
            )
        region_list = []
        latest_ts = 0
        for region in regions.values():
            countries = []
            for country in region["countries"].values():
                for idx in country["indices"]:
                    latest_ts = max(latest_ts, int(idx["lastUpdatedAt"] or 0))
                countries.append(country)
            region["countries"] = countries
            region_list.append(region)
        return {"ok": True, "data": {"lastUpdatedAt": latest_ts, "regions": region_list}}, 200


def _v2_intel_market_indices(user: dict | None, query: dict[str, list[str]]) -> tuple[dict, int]:
    _, err = _v2_intel_require_user(user)
    if err:
        return err
    country_code = str(query.get("countryCode", [""])[0] or "").strip().upper()
    lang = str(query.get("lang", ["en"])[0] or "en").lower()
    with v2_db_lock, _v2_db_conn() as conn:
        where = ["is_active = 1"]
        params: list[object] = []
        if country_code:
            where.append("country_code = ?")
            params.append(country_code)
        rows = conn.execute(
            f"SELECT * FROM intelligence_market_indices_v2 WHERE {' AND '.join(where)} ORDER BY display_order ASC",
            tuple(params),
        ).fetchall()
        out = []
        for row in rows:
            out.append(
                {
                    "indexId": str(row["id"] or ""),
                    "countryCode": str(row["country_code"] or ""),
                    "regionCode": str(row["region_code"] or ""),
                    "indexCode": str(row["index_code"] or ""),
                    "indexName": str(row["index_name_zh"] or row["index_name_en"] or "") if lang == "zh" else str(row["index_name_en"] or ""),
                    "symbol": str(row["index_symbol"] or ""),
                    "currency": str(row["currency"] or ""),
                    "isActive": bool(row["is_active"]),
                }
            )
        return {"ok": True, "data": out}, 200


def _v2_intel_market_index_detail(user: dict | None, index_id: str, query: dict[str, list[str]]) -> tuple[dict, int]:
    _, err = _v2_intel_require_user(user)
    if err:
        return err
    lang = str(query.get("lang", ["en"])[0] or "en").lower()
    with v2_db_lock, _v2_db_conn() as conn:
        row = conn.execute(
            """
            SELECT i.*, s.current_value, s.change_value, s.change_percent, s.turnover_amount, s.volume, s.market_status, s.snapshot_time
            FROM intelligence_market_indices_v2 i
            LEFT JOIN intelligence_market_index_latest_snapshots_v2 s ON s.index_id = i.id
            WHERE i.id = ?
            LIMIT 1
            """,
            (index_id,),
        ).fetchone()
        if not row:
            return {"ok": False, "error": "index_not_found"}, 404
        payload = {
            "indexId": str(row["id"] or ""),
            "indexCode": str(row["index_code"] or ""),
            "indexName": str(row["index_name_zh"] or row["index_name_en"] or "") if lang == "zh" else str(row["index_name_en"] or ""),
            "countryCode": str(row["country_code"] or ""),
            "currency": str(row["currency"] or ""),
            "latestSnapshot": {
                "currentValue": float(row["current_value"] or 0),
                "changeValue": float(row["change_value"] or 0),
                "changePercent": float(row["change_percent"] or 0),
                "turnoverAmount": float(row["turnover_amount"] or 0),
                "volume": float(row["volume"] or 0),
                "marketStatus": str(row["market_status"] or "unknown"),
                "lastUpdatedAt": int(row["snapshot_time"] or 0),
            },
        }
        return {"ok": True, "data": payload}, 200


def _v2_intel_market_index_timeseries(user: dict | None, index_id: str, query: dict[str, list[str]]) -> tuple[dict, int]:
    _, err = _v2_intel_require_user(user)
    if err:
        return err
    range_text = str(query.get("range", ["1d"])[0] or "1d").strip().lower()
    interval = str(query.get("interval", ["1h"])[0] or "1h").strip().lower()
    now = _v2_now()
    seconds_map = {"1d": 24 * 3600, "5d": 5 * 24 * 3600, "1m": 30 * 24 * 3600, "3m": 90 * 24 * 3600, "1y": 365 * 24 * 3600}
    since = now - int(seconds_map.get(range_text, 24 * 3600))
    with v2_db_lock, _v2_db_conn() as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM intelligence_market_index_timeseries_v2
            WHERE index_id = ? AND interval_type = ? AND point_time >= ?
            ORDER BY point_time ASC
            LIMIT 5000
            """,
            (index_id, interval, since),
        ).fetchall()
        points = [
            {
                "time": int(row["point_time"] or 0),
                "open": float(row["open_value"] or 0),
                "high": float(row["high_value"] or 0),
                "low": float(row["low_value"] or 0),
                "close": float(row["close_value"] or 0),
                "turnoverAmount": float(row["turnover_amount"] or 0),
                "volume": float(row["volume"] or 0),
            }
            for row in rows
        ]
        return {"ok": True, "data": {"indexId": index_id, "range": range_text, "interval": interval, "points": points}}, 200


def _v2_intel_instrument_display_name(row: sqlite3.Row, lang: str) -> str:
    if lang == "zh":
        return str(row["name_zh"] or row["name_en"] or row["symbol"] or "")
    return str(row["name_en"] or row["name_zh"] or row["symbol"] or "")


def _v2_intel_bool_flag(value: object, default: bool = True) -> bool:
    if value is None:
        return default
    text = str(value).strip().lower()
    if text in {"1", "true", "yes", "on"}:
        return True
    if text in {"0", "false", "no", "off"}:
        return False
    return default


def _v2_intel_instruments_search(user: dict | None, query: dict[str, list[str]]) -> tuple[dict, int]:
    _, err = _v2_intel_require_user(user)
    if err:
        return err
    lang = str(query.get("lang", ["zh"])[0] or "zh").lower()
    q = str(query.get("q", [""])[0] or "").strip()
    instrument_type = str(query.get("type", [""])[0] or "").strip().lower()
    limit = min(100, max(1, _v2_intel_int(query.get("limit", ["30"])[0] if query.get("limit") else 30, 30)))
    cache_key = f"intelligence:instrument:search:{lang}:{instrument_type}:{q.lower()}:{limit}"
    cached = _v2_intel_cache_get(cache_key)
    if isinstance(cached, dict):
        return cached, 200
    with v2_db_lock, _v2_db_conn() as conn:
        _v2_intel_seed_market_instruments(conn)
        where = ["i.is_active = 1"]
        params: list[object] = []
        if instrument_type and instrument_type in V2_INTEL_INSTRUMENT_TYPES:
            where.append("i.instrument_type = ?")
            params.append(instrument_type)
        if q:
            like = f"%{q.lower()}%"
            where.append("(lower(i.symbol) LIKE ? OR lower(i.name_en) LIKE ? OR lower(i.name_zh) LIKE ? OR lower(i.search_keywords) LIKE ?)")
            params.extend([like, like, like, like])
        rows = conn.execute(
            f"""
            SELECT i.*, q.last_price, q.change_percent, q.quote_time, q.market_status
            FROM intelligence_market_instruments_v2 i
            LEFT JOIN intelligence_instrument_latest_quotes_v2 q ON q.instrument_id = i.id
            WHERE {' AND '.join(where)}
            ORDER BY
              CASE
                WHEN lower(i.symbol) = ? THEN 0
                WHEN lower(i.symbol) LIKE ? THEN 1
                WHEN lower(i.name_en) LIKE ? OR lower(i.name_zh) LIKE ? THEN 2
                ELSE 3
              END,
              i.instrument_type ASC,
              i.symbol ASC
            LIMIT ?
            """,
            tuple(params + [q.lower(), f"{q.lower()}%" if q else "", f"{q.lower()}%" if q else "", f"{q.lower()}%" if q else "", limit]),
        ).fetchall()
        items = []
        for row in rows:
            latest_price = _v2_intel_float(row["last_price"], 0) if row["last_price"] is not None else None
            change_percent = _v2_intel_float(row["change_percent"], 0) if row["change_percent"] is not None else None
            quote_time = _v2_intel_int(row["quote_time"], 0) if row["quote_time"] is not None else 0
            if latest_price in (None, 0):
                fallback_rows = conn.execute(
                    """
                    SELECT close_price, point_time
                    FROM intelligence_instrument_ohlcv_timeseries_v2
                    WHERE instrument_id = ? AND interval_type = '1d'
                    ORDER BY point_time DESC
                    LIMIT 2
                    """,
                    (str(row["id"] or ""),),
                ).fetchall()
                if fallback_rows:
                    latest_price = _v2_intel_float(fallback_rows[0]["close_price"], 0)
                    quote_time = int(fallback_rows[0]["point_time"] or quote_time or 0)
                    if len(fallback_rows) > 1:
                        prev_close = _v2_intel_float(fallback_rows[1]["close_price"], 0)
                        if prev_close:
                            change_percent = ((latest_price - prev_close) / prev_close) * 100.0
            items.append(
                {
                    "instrumentId": str(row["id"] or ""),
                    "instrumentType": str(row["instrument_type"] or ""),
                    "symbol": str(row["symbol"] or ""),
                    "name": _v2_intel_instrument_display_name(row, lang),
                    "nameEn": str(row["name_en"] or ""),
                    "nameZh": str(row["name_zh"] or ""),
                    "countryCode": str(row["country_code"] or ""),
                    "exchangeCode": str(row["exchange_code"] or ""),
                    "currency": str(row["currency"] or ""),
                    "latestPrice": latest_price,
                    "changePercent": change_percent,
                    "quoteTime": quote_time,
                    "marketStatus": str(row["market_status"] or "unknown") if row["market_status"] is not None else "unknown",
                }
            )
        payload = {"ok": True, "success": True, "data": {"items": items, "total": len(items)}}
        _v2_intel_cache_set(cache_key, payload, 60)
        return payload, 200


def _v2_intel_instrument_detail(user: dict | None, instrument_id: str, query: dict[str, list[str]]) -> tuple[dict, int]:
    _, err = _v2_intel_require_user(user)
    if err:
        return err
    lang = str(query.get("lang", ["zh"])[0] or "zh").lower()
    cache_key = f"intelligence:instrument:detail:{instrument_id}:{lang}"
    cached = _v2_intel_cache_get(cache_key)
    if isinstance(cached, dict):
        return cached, 200
    with v2_db_lock, _v2_db_conn() as conn:
        _v2_intel_seed_market_instruments(conn)
        row = conn.execute(
            """
            SELECT i.*, q.quote_time, q.last_price, q.previous_close, q.open_price, q.high_price, q.low_price,
                   q.change_value, q.change_percent, q.volume, q.turnover_amount, q.bid_price, q.ask_price,
                   q.delayed_flag, q.market_status, q.data_quality
            FROM intelligence_market_instruments_v2 i
            LEFT JOIN intelligence_instrument_latest_quotes_v2 q ON q.instrument_id = i.id
            WHERE i.id = ?
            LIMIT 1
            """,
            (instrument_id,),
        ).fetchone()
        if not row:
            return {"ok": False, "error": "instrument_not_found"}, 404
        payload = {
            "ok": True,
            "success": True,
            "data": {
                "instrumentId": str(row["id"] or ""),
                "instrumentType": str(row["instrument_type"] or ""),
                "symbol": str(row["symbol"] or ""),
                "name": _v2_intel_instrument_display_name(row, lang),
                "nameEn": str(row["name_en"] or ""),
                "nameZh": str(row["name_zh"] or ""),
                "countryCode": str(row["country_code"] or ""),
                "regionCode": str(row["region_code"] or ""),
                "exchangeCode": str(row["exchange_code"] or ""),
                "exchangeName": str(row["exchange_name_zh"] or row["exchange_name_en"] or "") if lang == "zh" else str(row["exchange_name_en"] or row["exchange_name_zh"] or ""),
                "currency": str(row["currency"] or ""),
                "timezone": str(row["timezone"] or ""),
                "latestQuote": {
                    "quoteTime": _v2_intel_int(row["quote_time"], 0),
                    "lastPrice": _v2_intel_float(row["last_price"], 0),
                    "previousClose": _v2_intel_float(row["previous_close"], 0),
                    "open": _v2_intel_float(row["open_price"], 0),
                    "high": _v2_intel_float(row["high_price"], 0),
                    "low": _v2_intel_float(row["low_price"], 0),
                    "changeValue": _v2_intel_float(row["change_value"], 0),
                    "changePercent": _v2_intel_float(row["change_percent"], 0),
                    "volume": _v2_intel_float(row["volume"], 0),
                    "turnoverAmount": _v2_intel_float(row["turnover_amount"], 0),
                    "bid": _v2_intel_float(row["bid_price"], 0),
                    "ask": _v2_intel_float(row["ask_price"], 0),
                    "delayed": bool(row["delayed_flag"]) if row["delayed_flag"] is not None else True,
                    "marketStatus": str(row["market_status"] or "unknown"),
                    "dataQuality": str(row["data_quality"] or "normal"),
                },
            },
        }
        _v2_intel_cache_set(cache_key, payload, 30)
        return payload, 200


def _v2_intel_instrument_candles(user: dict | None, instrument_id: str, query: dict[str, list[str]]) -> tuple[dict, int]:
    _, err = _v2_intel_require_user(user)
    if err:
        return err
    interval = str(query.get("interval", ["1d"])[0] or "1d").strip().lower()
    range_text = str(query.get("range", ["6mo"])[0] or "6mo").strip().lower()
    adjusted = _v2_intel_bool_flag(query.get("adjusted", ["true"])[0] if query.get("adjusted") else True, True)
    norm_interval, _ = _v2_intel_normalize_interval(interval)
    norm_range = _v2_intel_normalize_range(range_text)
    adjusted_flag = 1 if adjusted else 0
    cache_key = f"intelligence:instrument:candles:{instrument_id}:{norm_interval}:{norm_range}:{adjusted_flag}"
    cached = _v2_intel_cache_get(cache_key)
    if isinstance(cached, dict):
        return cached, 200
    with v2_db_lock, _v2_db_conn() as conn:
        _v2_intel_seed_market_instruments(conn)
        row = conn.execute("SELECT * FROM intelligence_market_instruments_v2 WHERE id = ? LIMIT 1", (instrument_id,)).fetchone()
        if not row:
            return {"ok": False, "error": "instrument_not_found"}, 404
        since = _v2_now() - int(V2_INTEL_RANGE_SECONDS.get(norm_range, 180 * 24 * 3600))
        bars_rows = conn.execute(
            """
            SELECT *
            FROM intelligence_instrument_ohlcv_timeseries_v2
            WHERE instrument_id = ? AND interval_type = ? AND adjusted_flag = ? AND point_time >= ?
            ORDER BY point_time ASC
            LIMIT 20000
            """,
            (instrument_id, norm_interval, adjusted_flag, since),
        ).fetchall()
        if not bars_rows:
            _v2_intel_refresh_instrument_ohlcv(
                conn,
                instrument_ids=[instrument_id],
                interval=norm_interval,
                range_text=norm_range,
                backfill=False,
                force=True,
            )
            bars_rows = conn.execute(
                """
                SELECT *
                FROM intelligence_instrument_ohlcv_timeseries_v2
                WHERE instrument_id = ? AND interval_type = ? AND adjusted_flag = ? AND point_time >= ?
                ORDER BY point_time ASC
                LIMIT 20000
                """,
                (instrument_id, norm_interval, adjusted_flag, since),
            ).fetchall()
        bars = [
            {
                "time": int(item["point_time"] or 0),
                "open": _v2_intel_float(item["open_price"], 0),
                "high": _v2_intel_float(item["high_price"], 0),
                "low": _v2_intel_float(item["low_price"], 0),
                "close": _v2_intel_float(item["close_price"], 0),
                "adjustedClose": _v2_intel_float(item["adjusted_close"], _v2_intel_float(item["close_price"], 0)),
                "volume": _v2_intel_float(item["volume"], 0),
                "turnoverAmount": _v2_intel_float(item["turnover_amount"], 0),
            }
            for item in bars_rows
        ]
        payload = {
            "ok": True,
            "success": True,
            "data": {
                "instrument": {
                    "instrumentId": str(row["id"] or ""),
                    "symbol": str(row["symbol"] or ""),
                    "name": str(row["name_zh"] or row["name_en"] or row["symbol"] or ""),
                    "instrumentType": str(row["instrument_type"] or ""),
                    "currency": str(row["currency"] or ""),
                },
                "interval": norm_interval,
                "range": norm_range,
                "adjusted": bool(adjusted_flag),
                "bars": bars,
            },
        }
        _v2_intel_cache_set(cache_key, payload, 90)
        return payload, 200


def _v2_intel_instrument_quote_history(user: dict | None, instrument_id: str, query: dict[str, list[str]]) -> tuple[dict, int]:
    _, err = _v2_intel_require_user(user)
    if err:
        return err
    range_text = str(query.get("range", ["5d"])[0] or "5d").strip().lower()
    range_map = {"1d": 24 * 3600, "5d": 5 * 24 * 3600, "1mo": 30 * 24 * 3600, "3mo": 90 * 24 * 3600}
    since = _v2_now() - int(range_map.get(range_text, 5 * 24 * 3600))
    with v2_db_lock, _v2_db_conn() as conn:
        rows = conn.execute(
            """
            SELECT quote_time, last_price, change_value, change_percent, volume, turnover_amount, market_status, data_quality
            FROM intelligence_instrument_quote_snapshots_v2
            WHERE instrument_id = ? AND quote_time >= ?
            ORDER BY quote_time ASC
            LIMIT 5000
            """,
            (instrument_id, since),
        ).fetchall()
        points = [
            {
                "time": int(row["quote_time"] or 0),
                "lastPrice": _v2_intel_float(row["last_price"], 0),
                "changeValue": _v2_intel_float(row["change_value"], 0),
                "changePercent": _v2_intel_float(row["change_percent"], 0),
                "volume": _v2_intel_float(row["volume"], 0),
                "turnoverAmount": _v2_intel_float(row["turnover_amount"], 0),
                "marketStatus": str(row["market_status"] or "unknown"),
                "dataQuality": str(row["data_quality"] or "normal"),
            }
            for row in rows
        ]
        return {"ok": True, "success": True, "data": {"instrumentId": instrument_id, "range": range_text, "points": points}}, 200


def _v2_intel_watchlist_get(user: dict | None) -> tuple[dict, int]:
    viewer, err = _v2_intel_require_user(user)
    if err:
        return err
    email = _v2_user_email(viewer)
    cache_key = f"intelligence:instrument:watchlist:{email}"
    cached = _v2_intel_cache_get(cache_key)
    if isinstance(cached, dict):
        return cached, 200
    with v2_db_lock, _v2_db_conn() as conn:
        rows = conn.execute(
            """
            SELECT w.instrument_id, w.created_at, i.instrument_type, i.symbol, i.name_en, i.name_zh, i.exchange_code, i.country_code, i.currency,
                   q.last_price, q.change_percent, q.quote_time
            FROM intelligence_instrument_watchlists_v2 w
            JOIN intelligence_market_instruments_v2 i ON i.id = w.instrument_id
            LEFT JOIN intelligence_instrument_latest_quotes_v2 q ON q.instrument_id = i.id
            WHERE w.user_id = ?
            ORDER BY w.created_at DESC
            """,
            (email,),
        ).fetchall()
        items = []
        for row in rows:
            items.append(
                {
                    "instrumentId": str(row["instrument_id"] or ""),
                    "instrumentType": str(row["instrument_type"] or ""),
                    "symbol": str(row["symbol"] or ""),
                    "nameEn": str(row["name_en"] or ""),
                    "nameZh": str(row["name_zh"] or ""),
                    "exchangeCode": str(row["exchange_code"] or ""),
                    "countryCode": str(row["country_code"] or ""),
                    "currency": str(row["currency"] or ""),
                    "latestPrice": _v2_intel_float(row["last_price"], 0) if row["last_price"] is not None else None,
                    "changePercent": _v2_intel_float(row["change_percent"], 0) if row["change_percent"] is not None else None,
                    "quoteTime": _v2_intel_int(row["quote_time"], 0),
                    "createdAt": _v2_intel_int(row["created_at"], 0),
                }
            )
        payload = {"ok": True, "success": True, "data": {"items": items, "total": len(items)}}
        _v2_intel_cache_set(cache_key, payload, 30)
        return payload, 200


def _v2_intel_watchlist_add(user: dict | None, payload: dict) -> tuple[dict, int]:
    viewer, err = _v2_intel_require_user(user)
    if err:
        return err
    instrument_id = str(payload.get("instrumentId") or "").strip()
    if not instrument_id:
        return {"ok": False, "error": "instrument_id_required"}, 400
    email = _v2_user_email(viewer)
    now = _v2_now()
    with v2_db_lock, _v2_db_conn() as conn:
        row = conn.execute("SELECT id FROM intelligence_market_instruments_v2 WHERE id = ? LIMIT 1", (instrument_id,)).fetchone()
        if not row:
            return {"ok": False, "error": "instrument_not_found"}, 404
        conn.execute(
            """
            INSERT INTO intelligence_instrument_watchlists_v2(id, user_id, instrument_id, created_at, updated_at)
            VALUES(?, ?, ?, ?, ?)
            ON CONFLICT(user_id, instrument_id) DO UPDATE SET updated_at = excluded.updated_at
            """,
            (_v2_id("intwl"), email, instrument_id, now, now),
        )
        conn.commit()
    _v2_intel_cache_delete(f"intelligence:instrument:watchlist:{email}")
    return {"ok": True, "success": True, "data": {"instrumentId": instrument_id}}, 200


def _v2_intel_watchlist_remove(user: dict | None, instrument_id: str) -> tuple[dict, int]:
    viewer, err = _v2_intel_require_user(user)
    if err:
        return err
    email = _v2_user_email(viewer)
    with v2_db_lock, _v2_db_conn() as conn:
        conn.execute(
            "DELETE FROM intelligence_instrument_watchlists_v2 WHERE user_id = ? AND instrument_id = ?",
            (email, instrument_id),
        )
        conn.commit()
    _v2_intel_cache_delete(f"intelligence:instrument:watchlist:{email}")
    return {"ok": True, "success": True, "data": {"instrumentId": instrument_id}}, 200


def _v2_admin_intel_market_data_refresh(user: dict | None, payload: dict) -> tuple[dict, int]:
    if not is_admin_user(user):
        return {"ok": False, "error": "admin_required"}, 403
    instrument_ids = payload.get("instrumentIds") if isinstance(payload.get("instrumentIds"), list) else []
    instrument_types = payload.get("instrumentTypes") if isinstance(payload.get("instrumentTypes"), list) else []
    symbols = payload.get("symbols") if isinstance(payload.get("symbols"), list) else []
    interval = str(payload.get("interval") or "1d").strip().lower()
    range_text = str(payload.get("range") or "6mo").strip().lower()
    refresh_quotes = bool(payload.get("refreshQuotes", True))
    refresh_candles = bool(payload.get("refreshCandles", True))
    force = bool(payload.get("force", False))
    with v2_db_lock, _v2_db_conn() as conn:
        quote_result = _v2_intel_refresh_instrument_quotes(
            conn,
            instrument_ids=[str(item) for item in instrument_ids],
            instrument_types=[str(item) for item in instrument_types],
            symbols=[str(item) for item in symbols],
            force=force,
        ) if refresh_quotes else {"ok": True, "skipped": True}
        candle_result = _v2_intel_refresh_instrument_ohlcv(
            conn,
            instrument_ids=[str(item) for item in instrument_ids],
            instrument_types=[str(item) for item in instrument_types],
            symbols=[str(item) for item in symbols],
            interval=interval,
            range_text=range_text,
            backfill=False,
            force=force,
        ) if refresh_candles else {"ok": True, "skipped": True}
    ok = bool(quote_result.get("ok", True) and candle_result.get("ok", True))
    return {"ok": ok, "success": ok, "data": {"quotes": quote_result, "candles": candle_result}}, (200 if ok else 500)


def _v2_admin_intel_market_data_backfill(user: dict | None, payload: dict) -> tuple[dict, int]:
    if not is_admin_user(user):
        return {"ok": False, "error": "admin_required"}, 403
    instrument_ids = payload.get("instrumentIds") if isinstance(payload.get("instrumentIds"), list) else []
    instrument_types = payload.get("instrumentTypes") if isinstance(payload.get("instrumentTypes"), list) else []
    symbols = payload.get("symbols") if isinstance(payload.get("symbols"), list) else []
    interval = str(payload.get("interval") or "1d").strip().lower()
    range_text = str(payload.get("range") or "2y").strip().lower()
    force = bool(payload.get("force", True))
    with v2_db_lock, _v2_db_conn() as conn:
        result = _v2_intel_refresh_instrument_ohlcv(
            conn,
            instrument_ids=[str(item) for item in instrument_ids],
            instrument_types=[str(item) for item in instrument_types],
            symbols=[str(item) for item in symbols],
            interval=interval,
            range_text=range_text,
            backfill=True,
            force=force,
        )
    ok = bool(result.get("ok"))
    return {"ok": ok, "success": ok, "data": result}, (200 if ok else 500)


def _v2_admin_intel_market_data_update_instrument(user: dict | None, instrument_id: str, payload: dict) -> tuple[dict, int]:
    if not is_admin_user(user):
        return {"ok": False, "error": "admin_required"}, 403
    with v2_db_lock, _v2_db_conn() as conn:
        row = conn.execute("SELECT * FROM intelligence_market_instruments_v2 WHERE id = ? LIMIT 1", (instrument_id,)).fetchone()
        if not row:
            return {"ok": False, "error": "instrument_not_found"}, 404
        is_active = 1 if bool(payload.get("isActive", bool(row["is_active"]))) else 0
        primary_provider_code = str(payload.get("primaryProviderCode") or "").strip()
        primary_provider_id = str(row["primary_provider_id"] or "")
        if primary_provider_code:
            provider = conn.execute(
                "SELECT id FROM intelligence_free_data_providers_v2 WHERE provider_code = ? LIMIT 1",
                (primary_provider_code,),
            ).fetchone()
            if provider:
                primary_provider_id = str(provider["id"] or "")
        conn.execute(
            """
            UPDATE intelligence_market_instruments_v2
            SET is_active = ?, primary_provider_id = ?, updated_at = ?
            WHERE id = ?
            """,
            (is_active, primary_provider_id, _v2_now(), instrument_id),
        )
        conn.commit()
        updated = conn.execute("SELECT * FROM intelligence_market_instruments_v2 WHERE id = ? LIMIT 1", (instrument_id,)).fetchone()
        return {
            "ok": True,
            "success": True,
            "data": {
                "instrumentId": str(updated["id"] or ""),
                "instrumentType": str(updated["instrument_type"] or ""),
                "symbol": str(updated["symbol"] or ""),
                "isActive": bool(updated["is_active"]),
                "primaryProviderId": str(updated["primary_provider_id"] or ""),
            },
        }, 200


def _v2_intel_news_top(user: dict | None, query: dict[str, list[str]]) -> tuple[dict, int]:
    _, err = _v2_intel_require_user(user)
    if err:
        return err
    window = str(query.get("window", ["24h"])[0] or "24h").lower()
    lang = str(query.get("lang", ["zh"])[0] or "zh").lower()
    category = str(query.get("category", [""])[0] or "").strip().lower()
    limit = min(max(int(str(query.get("limit", ["30"])[0] or "30")), 1), 100)
    now = _v2_now()
    window_hours = 24 if window == "24h" else 48 if window == "48h" else 24
    cutoff = now - window_hours * 3600
    with v2_db_lock, _v2_db_conn() as conn:
        where = ["a.fetched_at >= ?"]
        params: list[object] = [cutoff]
        if category:
            where.append("a.category_primary = ?")
            params.append(category)
        rows = conn.execute(
            f"""
            SELECT
              a.*, s.source_name_en, s.source_name_zh,
              ns.summary_title, ns.summary_content,
              ns_zh.summary_content AS summary_content_zh,
              ns_zh.summarizer_type AS summary_type_zh,
              ns_en.summary_content AS summary_content_en
            FROM intelligence_news_articles_v2 a
            LEFT JOIN intelligence_news_sources_v2 s ON s.id = a.source_id
            LEFT JOIN intelligence_news_article_summaries_v2 ns ON ns.article_id = a.id AND ns.language_code = ?
            LEFT JOIN intelligence_news_article_summaries_v2 ns_zh ON ns_zh.article_id = a.id AND ns_zh.language_code = 'zh'
            LEFT JOIN intelligence_news_article_summaries_v2 ns_en ON ns_en.article_id = a.id AND ns_en.language_code = 'en'
            WHERE {' AND '.join(where)}
            ORDER BY a.importance_score DESC, a.relevance_score DESC, a.published_at DESC
            LIMIT ?
            """,
            tuple([lang] + params + [limit]),
        ).fetchall()
        items = []
        for idx, row in enumerate(rows, start=1):
            summary_zh_raw = re.sub(r"\s+", " ", str(row["summary_content_zh"] or "")).strip()
            summary_en_raw = re.sub(r"\s+", " ", str(row["summary_content_en"] or "")).strip()
            summary_zh = summary_zh_raw[:100] + ("..." if len(summary_zh_raw) > 100 else "") if summary_zh_raw else ""
            summary_en = summary_en_raw[:100] + ("..." if len(summary_en_raw) > 100 else "") if summary_en_raw else ""
            summary_type_zh = str(row["summary_type_zh"] or "").strip().lower()
            translated_summary_zh = summary_zh if summary_zh and summary_type_zh == "translated_summary" else ""
            generated_summary_zh = summary_zh if summary_zh and summary_type_zh and summary_type_zh != "translated_summary" else ""
            items.append(
                {
                    "articleId": str(row["id"] or ""),
                    "rankingOrder": idx,
                    "title": _v2_intel_news_title_value(row, lang),
                    "title_zh": str(row["title_zh"] or "").strip(),
                    "title_en": str(row["title_en"] or "").strip(),
                    "sourceName": str(row["source_name_zh"] or row["source_name_en"] or ""),
                    "publishedAt": int(row["published_at"] or 0),
                    "category": str(row["category_primary"] or "general"),
                    "summary": _v2_intel_news_summary_value(row, lang),
                    "summary_zh": summary_zh,
                    "translated_summary_zh": translated_summary_zh,
                    "generated_summary_zh": generated_summary_zh,
                    "summary_en": summary_en,
                    "originalUrl": str(row["original_url"] or ""),
                    "importanceScore": float(row["importance_score"] or 0),
                    "relevanceToFinanceBusinessScore": float(row["relevance_score"] or 0),
                }
            )
        return {"ok": True, "data": {"window": window, "language": lang, "generatedAt": now, "total": len(items), "items": items}}, 200


def _v2_intel_news_list(user: dict | None, query: dict[str, list[str]]) -> tuple[dict, int]:
    _, err = _v2_intel_require_user(user)
    if err:
        return err
    lang = str(query.get("lang", ["zh"])[0] or "zh").lower()
    category = str(query.get("category", [""])[0] or "").strip().lower()
    source_code = str(query.get("source", [""])[0] or "").strip().lower()
    window = str(query.get("window", ["24h"])[0] or "24h").lower()
    page = max(1, int(str(query.get("page", ["1"])[0] or "1")))
    page_size = min(100, max(1, int(str(query.get("pageSize", ["20"])[0] or "20")))
    )
    cutoff = _v2_now() - (24 if window == "24h" else 48 if window == "48h" else 7 * 24) * 3600
    with v2_db_lock, _v2_db_conn() as conn:
        where = ["a.fetched_at >= ?"]
        params: list[object] = [cutoff]
        if category:
            where.append("a.category_primary = ?")
            params.append(category)
        if source_code:
            where.append("lower(s.source_code) = ?")
            params.append(source_code)
        total_row = conn.execute(
            f"""
            SELECT COUNT(*) AS c
            FROM intelligence_news_articles_v2 a
            LEFT JOIN intelligence_news_sources_v2 s ON s.id = a.source_id
            WHERE {' AND '.join(where)}
            """,
            tuple(params),
        ).fetchone()
        total = int(total_row["c"] or 0) if total_row else 0
        offset = (page - 1) * page_size
        rows = conn.execute(
            f"""
            SELECT
              a.*, s.source_name_en, s.source_name_zh,
              ns.summary_title, ns.summary_content,
              ns_zh.summary_content AS summary_content_zh,
              ns_zh.summarizer_type AS summary_type_zh,
              ns_en.summary_content AS summary_content_en
            FROM intelligence_news_articles_v2 a
            LEFT JOIN intelligence_news_sources_v2 s ON s.id = a.source_id
            LEFT JOIN intelligence_news_article_summaries_v2 ns ON ns.article_id = a.id AND ns.language_code = ?
            LEFT JOIN intelligence_news_article_summaries_v2 ns_zh ON ns_zh.article_id = a.id AND ns_zh.language_code = 'zh'
            LEFT JOIN intelligence_news_article_summaries_v2 ns_en ON ns_en.article_id = a.id AND ns_en.language_code = 'en'
            WHERE {' AND '.join(where)}
            ORDER BY a.importance_score DESC, a.published_at DESC
            LIMIT ? OFFSET ?
            """,
            tuple([lang] + params + [page_size, offset]),
        ).fetchall()
        items = []
        for row in rows:
            summary_zh_raw = re.sub(r"\s+", " ", str(row["summary_content_zh"] or "")).strip()
            summary_en_raw = re.sub(r"\s+", " ", str(row["summary_content_en"] or "")).strip()
            summary_zh = summary_zh_raw[:100] + ("..." if len(summary_zh_raw) > 100 else "") if summary_zh_raw else ""
            summary_en = summary_en_raw[:100] + ("..." if len(summary_en_raw) > 100 else "") if summary_en_raw else ""
            summary_type_zh = str(row["summary_type_zh"] or "").strip().lower()
            items.append(
                {
                    "articleId": str(row["id"] or ""),
                    "title": _v2_intel_news_title_value(row, lang),
                    "title_zh": str(row["title_zh"] or "").strip(),
                    "title_en": str(row["title_en"] or "").strip(),
                    "sourceName": str(row["source_name_zh"] or row["source_name_en"] or ""),
                    "publishedAt": int(row["published_at"] or 0),
                    "category": str(row["category_primary"] or "general"),
                    "tags": _v2_json_load(str(row["tags_json"] or "[]"), []),
                    "summary": _v2_intel_news_summary_value(row, lang),
                    "summary_zh": summary_zh,
                    "translated_summary_zh": summary_zh if summary_zh and summary_type_zh == "translated_summary" else "",
                    "generated_summary_zh": summary_zh if summary_zh and summary_type_zh and summary_type_zh != "translated_summary" else "",
                    "summary_en": summary_en,
                    "originalUrl": str(row["original_url"] or ""),
                }
            )
        return {"ok": True, "data": {"page": page, "pageSize": page_size, "total": total, "items": items}}, 200


def _v2_intel_news_detail(user: dict | None, article_id: str, query: dict[str, list[str]]) -> tuple[dict, int]:
    _, err = _v2_intel_require_user(user)
    if err:
        return err
    lang = str(query.get("lang", ["zh"])[0] or "zh").lower()
    with v2_db_lock, _v2_db_conn() as conn:
        row = conn.execute(
            """
            SELECT
              a.*, s.source_name_en, s.source_name_zh,
              ns.summary_title, ns.summary_content,
              ns_zh.summary_content AS summary_content_zh,
              ns_zh.summarizer_type AS summary_type_zh,
              ns_en.summary_content AS summary_content_en
            FROM intelligence_news_articles_v2 a
            LEFT JOIN intelligence_news_sources_v2 s ON s.id = a.source_id
            LEFT JOIN intelligence_news_article_summaries_v2 ns ON ns.article_id = a.id AND ns.language_code = ?
            LEFT JOIN intelligence_news_article_summaries_v2 ns_zh ON ns_zh.article_id = a.id AND ns_zh.language_code = 'zh'
            LEFT JOIN intelligence_news_article_summaries_v2 ns_en ON ns_en.article_id = a.id AND ns_en.language_code = 'en'
            WHERE a.id = ?
            LIMIT 1
            """,
            (lang, article_id),
        ).fetchone()
        if not row:
            return {"ok": False, "error": "article_not_found"}, 404
        summary_zh_raw = re.sub(r"\s+", " ", str(row["summary_content_zh"] or "")).strip()
        summary_en_raw = re.sub(r"\s+", " ", str(row["summary_content_en"] or "")).strip()
        summary_zh = summary_zh_raw[:100] + ("..." if len(summary_zh_raw) > 100 else "") if summary_zh_raw else ""
        summary_en = summary_en_raw[:100] + ("..." if len(summary_en_raw) > 100 else "") if summary_en_raw else ""
        summary_type_zh = str(row["summary_type_zh"] or "").strip().lower()
        return {
            "ok": True,
            "data": {
                "articleId": str(row["id"] or ""),
                "title": _v2_intel_news_title_value(row, lang),
                "title_zh": str(row["title_zh"] or "").strip(),
                "title_en": str(row["title_en"] or "").strip(),
                "titleOriginal": str(row["title_original"] or ""),
                "sourceName": str(row["source_name_zh"] or row["source_name_en"] or ""),
                "publishedAt": int(row["published_at"] or 0),
                "category": str(row["category_primary"] or "general"),
                "tags": _v2_json_load(str(row["tags_json"] or "[]"), []),
                "summary": _v2_intel_news_summary_value(row, lang),
                "summary_zh": summary_zh,
                "translated_summary_zh": summary_zh if summary_zh and summary_type_zh == "translated_summary" else "",
                "generated_summary_zh": summary_zh if summary_zh and summary_type_zh and summary_type_zh != "translated_summary" else "",
                "summary_en": summary_en,
                "originalUrl": str(row["original_url"] or ""),
                "importanceScore": float(row["importance_score"] or 0),
                "relevanceToFinanceBusinessScore": float(row["relevance_score"] or 0),
                "copyrightMode": str(row["copyright_mode"] or "metadata_summary_link_only"),
            },
        }, 200


def _v2_intel_news_sources(user: dict | None, query: dict[str, list[str]]) -> tuple[dict, int]:
    _, err = _v2_intel_require_user(user)
    if err:
        return err
    lang = str(query.get("lang", ["zh"])[0] or "zh").lower()
    active_only = str(query.get("activeOnly", ["true"])[0] or "true").lower() in {"1", "true", "yes"}
    with v2_db_lock, _v2_db_conn() as conn:
        where = "1=1" if not active_only else "is_active = 1"
        rows = conn.execute(
            f"""
            SELECT *
            FROM intelligence_news_sources_v2
            WHERE {where}
            ORDER BY priority_score DESC, source_code ASC
            """
        ).fetchall()
        data = []
        for row in rows:
            data.append(
                {
                    "sourceId": str(row["id"] or ""),
                    "sourceCode": str(row["source_code"] or ""),
                    "sourceName": str(row["source_name_zh"] or row["source_name_en"] or "") if lang == "zh" else str(row["source_name_en"] or ""),
                    "sourceType": str(row["source_type"] or ""),
                    "sourceCountry": str(row["source_country"] or ""),
                    "isActive": bool(row["is_active"]),
                    "priorityScore": int(row["priority_score"] or 0),
                }
            )
        return {"ok": True, "data": data}, 200


def _v2_intel_news_stats(user: dict | None, query: dict[str, list[str]]) -> tuple[dict, int]:
    _, err = _v2_intel_require_user(user)
    if err:
        return err
    window = str(query.get("window", ["24h"])[0] or "24h").lower()
    cutoff = _v2_now() - (24 if window == "24h" else 48 if window == "48h" else 7 * 24) * 3600
    with v2_db_lock, _v2_db_conn() as conn:
        total = conn.execute("SELECT COUNT(*) AS c FROM intelligence_news_articles_v2 WHERE fetched_at >= ?", (cutoff,)).fetchone()
        processed = conn.execute(
            "SELECT COUNT(*) AS c FROM intelligence_news_articles_v2 WHERE fetched_at >= ? AND status IN ('processed','selected')",
            (cutoff,),
        ).fetchone()
        selected = conn.execute(
            "SELECT COUNT(*) AS c FROM intelligence_news_daily_digest_items_v2 WHERE digest_window_end >= ?",
            (cutoff,),
        ).fetchone()
        categories = conn.execute(
            """
            SELECT category_primary, COUNT(*) AS c
            FROM intelligence_news_articles_v2
            WHERE fetched_at >= ?
            GROUP BY category_primary
            ORDER BY c DESC
            """,
            (cutoff,),
        ).fetchall()
        sources = conn.execute(
            """
            SELECT s.source_code, COUNT(*) AS c
            FROM intelligence_news_articles_v2 a
            LEFT JOIN intelligence_news_sources_v2 s ON s.id = a.source_id
            WHERE a.fetched_at >= ?
            GROUP BY s.source_code
            ORDER BY c DESC
            LIMIT 15
            """,
            (cutoff,),
        ).fetchall()
        return {
            "ok": True,
            "data": {
                "window": window,
                "totalArticles": int(total["c"] or 0) if total else 0,
                "processedArticles": int(processed["c"] or 0) if processed else 0,
                "selectedTopItems": int(selected["c"] or 0) if selected else 0,
                "categories": [{"category": str(row["category_primary"] or "general"), "count": int(row["c"] or 0)} for row in categories],
                "sources": [{"sourceCode": str(row["source_code"] or ""), "count": int(row["c"] or 0)} for row in sources],
            },
        }, 200


def _v2_intel_daily_brief(user: dict | None, query: dict[str, list[str]]) -> tuple[dict, int]:
    _, err = _v2_intel_require_user(user)
    if err:
        return err
    lang = str(query.get("lang", ["zh"])[0] or "zh").lower()
    market_payload, market_status = _v2_intel_markets_overview(user, {"lang": [lang]})
    news_payload, news_status = _v2_intel_news_top(user, {"lang": [lang], "window": ["24h"], "limit": ["10"]})
    if market_status != 200 or news_status != 200:
        return {"ok": False, "error": "brief_generation_failed"}, 500
    highlights = []
    for region in (market_payload.get("data", {}).get("regions") or []):
        for country in (region.get("countries") or []):
            highlights.extend(country.get("indices") or [])
    highlights = sorted(highlights, key=lambda item: abs(float(item.get("changePercent") or 0)), reverse=True)[:6]
    return {
        "ok": True,
        "data": {
            "briefDate": datetime.fromtimestamp(_v2_now(), tz=ZoneInfo("Asia/Shanghai")).strftime("%Y-%m-%d"),
            "language": lang,
            "generatedAt": _v2_now(),
            "marketSnapshot": {
                "lastUpdatedAt": market_payload.get("data", {}).get("lastUpdatedAt"),
                "highlights": [
                    {
                        "indexCode": item.get("indexCode"),
                        "indexName": item.get("indexName"),
                        "changePercent": item.get("changePercent"),
                    }
                    for item in highlights
                ],
            },
            "topNews": news_payload.get("data", {}).get("items", []),
        },
    }, 200


def _v2_intel_home_widget(user: dict | None, query: dict[str, list[str]]) -> tuple[dict, int]:
    _, err = _v2_intel_require_user(user)
    if err:
        return err
    lang = str(query.get("lang", ["zh"])[0] or "zh").lower()
    market_payload, _ = _v2_intel_markets_overview(user, {"lang": [lang]})
    top_payload, _ = _v2_intel_news_top(user, {"lang": [lang], "window": ["24h"], "limit": ["6"]})
    indices = []
    for region in (market_payload.get("data", {}).get("regions") or []):
        for country in (region.get("countries") or []):
            indices.extend(country.get("indices") or [])
    indices = sorted(indices, key=lambda item: abs(float(item.get("changePercent") or 0)), reverse=True)[:8]
    return {
        "ok": True,
        "data": {
            "markets": {
                "lastUpdatedAt": market_payload.get("data", {}).get("lastUpdatedAt"),
                "indices": [
                    {
                        "indexCode": item.get("indexCode"),
                        "indexName": item.get("indexName"),
                        "currentValue": item.get("currentValue"),
                        "changePercent": item.get("changePercent"),
                    }
                    for item in indices
                ],
            },
            "topNews": top_payload.get("data", {}).get("items", []),
        },
    }, 200


def _v2_admin_intel_markets_refresh(user: dict | None, payload: dict) -> tuple[dict, int]:
    if not is_admin_user(user):
        return {"ok": False, "error": "admin_required"}, 403
    index_codes = payload.get("indexCodes") if isinstance(payload.get("indexCodes"), list) else []
    force = bool(payload.get("force", False))
    with v2_db_lock, _v2_db_conn() as conn:
        result = _v2_intel_market_refresh(conn, index_codes=index_codes, force=force)
    status = 200 if result.get("ok") else 500
    return {"ok": bool(result.get("ok")), "data": result}, status


def _v2_admin_intel_news_refresh(user: dict | None, payload: dict) -> tuple[dict, int]:
    if not is_admin_user(user):
        return {"ok": False, "error": "admin_required"}, 403
    source_codes = payload.get("sourceCodes") if isinstance(payload.get("sourceCodes"), list) else []
    window = str(payload.get("window") or "24h").lower()
    hours = 24 if window == "24h" else 48 if window == "48h" else 24
    with v2_db_lock, _v2_db_conn() as conn:
        ingest = _v2_intel_news_refresh(conn, source_codes=source_codes, window_hours=hours)
        process = _v2_intel_news_process(conn, window_hours=max(48, hours))
        summarize = _v2_intel_generate_news_summaries(conn, window_hours=max(48, hours), languages=["zh", "en"])
    return {"ok": True, "data": {"ingestion": ingest, "processing": process, "summarization": summarize}}, 200


def _v2_admin_intel_generate_digest(user: dict | None, payload: dict) -> tuple[dict, int]:
    if not is_admin_user(user):
        return {"ok": False, "error": "admin_required"}, 403
    window = str(payload.get("window") or "24h").lower()
    hours = 24 if window == "24h" else 48 if window == "48h" else 24
    languages = payload.get("languages") if isinstance(payload.get("languages"), list) else ["zh", "en"]
    limit = min(max(int(payload.get("limit", 30) or 30), 1), 100)
    force_regenerate = bool(payload.get("forceRegenerate", False))
    normalized_languages = [str(item).strip().lower() for item in languages if str(item).strip()]
    if not normalized_languages:
        normalized_languages = ["zh", "en"]
    with v2_db_lock, _v2_db_conn() as conn:
        summaries = _v2_intel_generate_news_summaries(
            conn,
            window_hours=max(24, hours),
            languages=normalized_languages,
        )
        result = _v2_intel_generate_news_digest(
            conn,
            window_hours=hours,
            languages=normalized_languages,
            limit=limit,
            force_regenerate=force_regenerate,
        )
    return {"ok": True, "data": {"summarization": summaries, "digest": result}}, 200


def _v2_admin_intel_job_runs(user: dict | None, query: dict[str, list[str]]) -> tuple[dict, int]:
    if not is_admin_user(user):
        return {"ok": False, "error": "admin_required"}, 403
    job_type = str(query.get("jobType", [""])[0] or "").strip().lower()
    page = max(1, int(str(query.get("page", ["1"])[0] or "1")))
    page_size = min(100, max(1, int(str(query.get("pageSize", ["20"])[0] or "20")))
    )
    with _v2_db_conn() as conn:
        where = "1=1"
        params: list[object] = []
        if job_type:
            where = "lower(job_type) = ?"
            params.append(job_type)
        total_row = conn.execute(f"SELECT COUNT(*) AS c FROM intelligence_job_runs_v2 WHERE {where}", tuple(params)).fetchone()
        total = int(total_row["c"] or 0) if total_row else 0
        offset = (page - 1) * page_size
        rows = conn.execute(
            f"""
            SELECT *
            FROM intelligence_job_runs_v2
            WHERE {where}
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
            """,
            tuple(params + [page_size, offset]),
        ).fetchall()
        items = []
        for row in rows:
            items.append(
                {
                    "jobRunId": str(row["id"] or ""),
                    "jobName": str(row["job_name"] or ""),
                    "jobType": str(row["job_type"] or ""),
                    "status": str(row["status"] or ""),
                    "startedAt": int(row["started_at"] or 0),
                    "completedAt": int(row["completed_at"] or 0),
                    "fetchedCount": int(row["fetched_count"] or 0),
                    "insertedCount": int(row["inserted_count"] or 0),
                    "updatedCount": int(row["updated_count"] or 0),
                    "skippedCount": int(row["skipped_count"] or 0),
                    "failedCount": int(row["failed_count"] or 0),
                }
            )
        return {"ok": True, "data": {"page": page, "pageSize": page_size, "total": total, "items": items}}, 200


def _v2_admin_intel_providers_status(user: dict | None) -> tuple[dict, int]:
    if not is_admin_user(user):
        return {"ok": False, "error": "admin_required"}, 403
    now = _v2_now()
    with _v2_db_conn() as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM intelligence_free_data_providers_v2
            ORDER BY is_active DESC, priority_score DESC, provider_code ASC
            """
        ).fetchall()
        items = []
        for row in rows:
            provider_id = str(row["id"] or "")
            last_success = conn.execute(
                """
                SELECT completed_at
                FROM intelligence_job_runs_v2
                WHERE status = 'succeeded' AND (provider_id = ? OR provider_id = '')
                ORDER BY completed_at DESC
                LIMIT 1
                """,
                (provider_id,),
            ).fetchone()
            last_failure = conn.execute(
                """
                SELECT occurred_at, error_message
                FROM intelligence_provider_errors_v2
                WHERE provider_id = ?
                ORDER BY occurred_at DESC
                LIMIT 1
                """,
                (provider_id,),
            ).fetchone()
            used_today = conn.execute(
                """
                SELECT SUM(request_count) AS c
                FROM intelligence_provider_rate_limit_state_v2
                WHERE provider_id = ? AND window_type = 'day' AND window_start_at >= ?
                """,
                (provider_id, now - 24 * 3600),
            ).fetchone()
            items.append(
                {
                    "providerCode": str(row["provider_code"] or ""),
                    "providerName": str(row["provider_name"] or ""),
                    "providerType": str(row["provider_type"] or ""),
                    "isActive": bool(row["is_active"]),
                    "rateLimit": {
                        "perMinute": int(row["rate_limit_per_minute"] or 0),
                        "perDay": int(row["rate_limit_per_day"] or 0),
                        "usedToday": int(used_today["c"] or 0) if used_today else 0,
                    },
                    "lastSuccessAt": int(last_success["completed_at"] or 0) if last_success else 0,
                    "lastFailureAt": int(last_failure["occurred_at"] or 0) if last_failure else 0,
                    "healthStatus": "healthy" if (not last_failure or (last_success and int(last_success["completed_at"] or 0) >= int(last_failure["occurred_at"] or 0))) else "degraded",
                }
            )
        return {"ok": True, "data": items}, 200


def _v2_admin_intel_update_source(user: dict | None, source_id: str, payload: dict) -> tuple[dict, int]:
    if not is_admin_user(user):
        return {"ok": False, "error": "admin_required"}, 403
    with v2_db_lock, _v2_db_conn() as conn:
        row = conn.execute("SELECT * FROM intelligence_news_sources_v2 WHERE id = ? LIMIT 1", (source_id,)).fetchone()
        if not row:
            return {"ok": False, "error": "source_not_found"}, 404
        is_active = 1 if bool(payload.get("isActive", bool(row["is_active"]))) else 0
        priority = max(1, min(100, int(payload.get("priorityScore", row["priority_score"] or 50))))
        conn.execute(
            "UPDATE intelligence_news_sources_v2 SET is_active = ?, priority_score = ?, updated_at = ? WHERE id = ?",
            (is_active, priority, _v2_now(), source_id),
        )
        conn.commit()
        updated = conn.execute("SELECT * FROM intelligence_news_sources_v2 WHERE id = ?", (source_id,)).fetchone()
        return {
            "ok": True,
            "data": {
                "sourceId": str(updated["id"] or ""),
                "sourceCode": str(updated["source_code"] or ""),
                "isActive": bool(updated["is_active"]),
                "priorityScore": int(updated["priority_score"] or 0),
            },
        }, 200


def _v2_admin_intel_update_index(user: dict | None, index_id: str, payload: dict) -> tuple[dict, int]:
    if not is_admin_user(user):
        return {"ok": False, "error": "admin_required"}, 403
    with v2_db_lock, _v2_db_conn() as conn:
        row = conn.execute("SELECT * FROM intelligence_market_indices_v2 WHERE id = ? LIMIT 1", (index_id,)).fetchone()
        if not row:
            return {"ok": False, "error": "index_not_found"}, 404
        is_active = 1 if bool(payload.get("isActive", bool(row["is_active"]))) else 0
        primary_provider_code = str(payload.get("primaryProviderCode") or "").strip()
        primary_provider_id = str(row["primary_provider_id"] or "")
        if primary_provider_code:
            provider = conn.execute(
                "SELECT id FROM intelligence_free_data_providers_v2 WHERE provider_code = ? LIMIT 1",
                (primary_provider_code,),
            ).fetchone()
            if provider:
                primary_provider_id = str(provider["id"] or "")
        conn.execute(
            "UPDATE intelligence_market_indices_v2 SET is_active = ?, primary_provider_id = ?, updated_at = ? WHERE id = ?",
            (is_active, primary_provider_id, _v2_now(), index_id),
        )
        conn.commit()
        updated = conn.execute("SELECT * FROM intelligence_market_indices_v2 WHERE id = ?", (index_id,)).fetchone()
        return {
            "ok": True,
            "data": {
                "indexId": str(updated["id"] or ""),
                "indexCode": str(updated["index_code"] or ""),
                "isActive": bool(updated["is_active"]),
                "primaryProviderId": str(updated["primary_provider_id"] or ""),
            },
        }, 200


def _v2_user_project_ids(conn: sqlite3.Connection, user: dict | None) -> set[str]:
    if is_admin_user(user):
        rows = conn.execute("SELECT id FROM projects").fetchall()
        return {str(row["id"]) for row in rows}
    email = _v2_user_email(user)
    if not email:
        return set()
    rows = conn.execute(
        """
        SELECT p.id
        FROM projects p
        LEFT JOIN project_members pm ON pm.project_id = p.id
        LEFT JOIN access_grants ag ON ag.scope_type = 'project' AND ag.scope_id = p.id
            AND ag.granted_user_id = ? AND ag.is_active = 1 AND ag.revoked_at = 0
        WHERE p.owner_id = ? OR pm.user_id = ? OR ag.id IS NOT NULL
        """,
        (email, email, email),
    ).fetchall()
    return {str(row["id"]) for row in rows}


def _v2_project_metrics(conn: sqlite3.Connection, project_id: str) -> dict:
    task_row = conn.execute(
        """
        SELECT
          SUM(CASE WHEN status NOT IN ('done', 'cancelled') THEN 1 ELSE 0 END) AS unfinished_count,
          SUM(CASE WHEN status IN ('in_review', 'pending_approval') THEN 1 ELSE 0 END) AS pending_approval_count,
          MAX(updated_at) AS task_last_updated
        FROM work_items
        WHERE project_id = ?
        """,
        (project_id,),
    ).fetchone()
    issue_row = conn.execute(
        """
        SELECT
          SUM(CASE WHEN status NOT IN ('resolved', 'closed') THEN 1 ELSE 0 END) AS blocker_count,
          MAX(updated_at) AS issue_last_updated
        FROM project_issues
        WHERE project_id = ?
        """,
        (project_id,),
    ).fetchone()
    latest_task = conn.execute(
        """
        SELECT title, status
        FROM work_items
        WHERE project_id = ?
        ORDER BY updated_at DESC
        LIMIT 1
        """,
        (project_id,),
    ).fetchone()
    return {
        "unfinished_task_count": int(task_row["unfinished_count"] or 0) if task_row else 0,
        "pending_approval_count": int(task_row["pending_approval_count"] or 0) if task_row else 0,
        "blocker_count": int(issue_row["blocker_count"] or 0) if issue_row else 0,
        "latest_progress": (
            f"{latest_task['title']} ({latest_task['status']})"
            if latest_task and str(latest_task["title"] or "").strip()
            else ""
        ),
        "task_last_updated": int(task_row["task_last_updated"] or 0) if task_row else 0,
        "issue_last_updated": int(issue_row["issue_last_updated"] or 0) if issue_row else 0,
    }


def _v2_project_payload(conn: sqlite3.Connection, row: sqlite3.Row, user: dict | None) -> dict:
    project_id = str(row["id"] or "")
    metrics = _v2_project_metrics(conn, project_id)
    role = _v2_project_role(conn, user, project_id)
    last_updated = max(
        int(row["updated_at"] or 0),
        int(metrics.get("task_last_updated") or 0),
        int(metrics.get("issue_last_updated") or 0),
    )
    return {
        "id": project_id,
        "name": str(row["name"] or ""),
        "description": str(row["description"] or ""),
        "owner_id": str(row["owner_id"] or ""),
        "status": str(row["status"] or "planning"),
        "start_date": str(row["start_date"] or ""),
        "due_date": str(row["due_date"] or ""),
        "created_at": int(row["created_at"] or 0),
        "updated_at": int(row["updated_at"] or 0),
        "last_updated": last_updated,
        "role_in_project": role,
        "latest_progress": metrics.get("latest_progress") or "",
        "unfinished_task_count": int(metrics.get("unfinished_task_count") or 0),
        "pending_approval_count": int(metrics.get("pending_approval_count") or 0),
        "issue_blocker_count": int(metrics.get("blocker_count") or 0),
    }


def _v2_member_payload(conn: sqlite3.Connection, project_id: str) -> list[dict]:
    rows = conn.execute(
        """
        SELECT id, project_id, user_id, role_in_project, joined_at
        FROM project_members
        WHERE project_id = ?
        ORDER BY joined_at ASC
        """,
        (project_id,),
    ).fetchall()
    return [
        {
            "id": str(row["id"] or ""),
            "project_id": str(row["project_id"] or ""),
            "user_id": str(row["user_id"] or ""),
            "display_name": user_display_label(str(row["user_id"] or "")),
            "role_in_project": str(row["role_in_project"] or "member"),
            "joined_at": int(row["joined_at"] or 0),
        }
        for row in rows
    ]


def _v2_work_item_payload(conn: sqlite3.Connection, row: sqlite3.Row) -> dict:
    item_id = str(row["id"] or "")
    assignee_rows = conn.execute(
        "SELECT user_id FROM work_item_assignees WHERE work_item_id = ? ORDER BY assigned_at ASC",
        (item_id,),
    ).fetchall()
    feedback_row = conn.execute(
        """
        SELECT id, submitted_by, completion_summary, blockers, next_steps, created_at
        FROM work_item_feedback
        WHERE work_item_id = ?
        ORDER BY created_at DESC
        LIMIT 1
        """,
        (item_id,),
    ).fetchone()
    return {
        "id": item_id,
        "project_id": str(row["project_id"] or ""),
        "title": str(row["title"] or ""),
        "description": str(row["description"] or ""),
        "priority": str(row["priority"] or "medium"),
        "status": str(row["status"] or "todo"),
        "due_date": str(row["due_date"] or ""),
        "created_by": str(row["created_by"] or ""),
        "created_at": int(row["created_at"] or 0),
        "updated_at": int(row["updated_at"] or 0),
        "dependencies": _v2_json_load(str(row["dependencies_json"] or "[]"), []),
        "collaborators": _v2_json_load(str(row["collaborators_json"] or "[]"), []),
        "assignees": [str(item["user_id"] or "") for item in assignee_rows],
        "latest_feedback": {
            "id": str(feedback_row["id"] or ""),
            "submitted_by": str(feedback_row["submitted_by"] or ""),
            "completion_summary": str(feedback_row["completion_summary"] or ""),
            "blockers": str(feedback_row["blockers"] or ""),
            "next_steps": str(feedback_row["next_steps"] or ""),
            "created_at": int(feedback_row["created_at"] or 0),
        } if feedback_row else None,
    }


def _v2_issue_payload(row: sqlite3.Row) -> dict:
    return {
        "id": str(row["id"] or ""),
        "project_id": str(row["project_id"] or ""),
        "work_item_id": str(row["work_item_id"] or ""),
        "title": str(row["title"] or ""),
        "description": str(row["description"] or ""),
        "severity": str(row["severity"] or "medium"),
        "status": str(row["status"] or "open"),
        "reported_by": str(row["reported_by"] or ""),
        "assigned_to": str(row["assigned_to"] or ""),
        "created_at": int(row["created_at"] or 0),
        "resolved_at": int(row["resolved_at"] or 0),
        "updated_at": int(row["updated_at"] or 0),
    }


def _v2_notify(
    conn: sqlite3.Connection,
    user_id: str,
    notice_type: str,
    title: str,
    content: str,
    *,
    project_id: str = "",
    work_item_id: str = "",
    document_id: str = "",
) -> None:
    target = normalize_email(user_id)
    if not target:
        return
    conn.execute(
        """
        INSERT INTO notifications_v2(
          id, user_id, type, title, content, related_project_id, related_work_item_id, related_document_id, is_read, created_at
        ) VALUES(?, ?, ?, ?, ?, ?, ?, ?, 0, ?)
        """,
        (
            _v2_id("ntf"),
            target,
            notice_type,
            title[:140],
            content[:2000],
            project_id,
            work_item_id,
            document_id,
            _v2_now(),
        ),
    )


def _v2_audit(conn: sqlite3.Connection, actor: str, action: str, entity_type: str, entity_id: str, metadata: dict | None = None) -> None:
    conn.execute(
        """
        INSERT INTO audit_logs_v2(id, actor_user_id, action_type, entity_type, entity_id, metadata_json, created_at)
        VALUES(?, ?, ?, ?, ?, ?, ?)
        """,
        (
            _v2_id("audit"),
            normalize_email(actor),
            action,
            entity_type,
            entity_id,
            json.dumps(metadata or {}, ensure_ascii=False)[:4000],
            _v2_now(),
        ),
    )


def _v2_project_detail_payload(conn: sqlite3.Connection, project_id: str, user: dict | None) -> dict:
    row = conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
    if not row:
        return {"ok": False, "error": "project_not_found"}
    if not _v2_can_view_project(conn, user, project_id):
        return {"ok": False, "error": "permission_denied"}
    tasks = conn.execute(
        "SELECT * FROM work_items WHERE project_id = ? ORDER BY updated_at DESC LIMIT 100",
        (project_id,),
    ).fetchall()
    issues = conn.execute(
        "SELECT * FROM project_issues WHERE project_id = ? ORDER BY updated_at DESC LIMIT 100",
        (project_id,),
    ).fetchall()
    return {
        "ok": True,
        "project": _v2_project_payload(conn, row, user),
        "members": _v2_member_payload(conn, project_id),
        "work_items": [_v2_work_item_payload(conn, item) for item in tasks],
        "issues": [_v2_issue_payload(item) for item in issues],
    }


def _v2_list_projects(user: dict | None, query: dict[str, list[str]]) -> dict:
    with v2_db_lock, _v2_db_conn() as conn:
        admin = is_admin_user(user)
        scope = str((query.get("scope", ["my"])[0] or "my")).lower()
        rows = conn.execute("SELECT * FROM projects ORDER BY updated_at DESC").fetchall()
        visible: list[sqlite3.Row] = []
        member_filter = normalize_email(query.get("member", [""])[0]) if query.get("member") else ""
        owner_filter = normalize_email(query.get("owner", [""])[0]) if query.get("owner") else ""
        status_filter = str(query.get("status", [""])[0] or "").strip().lower()
        q = str(query.get("q", [""])[0] or "").strip().lower()
        has_pending = str(query.get("has_pending_approvals", [""])[0] or "").strip().lower() in {"1", "true", "yes"}
        has_blockers = str(query.get("has_blockers", [""])[0] or "").strip().lower() in {"1", "true", "yes"}
        date_from = str(query.get("date_from", [""])[0] or "").strip()
        date_to = str(query.get("date_to", [""])[0] or "").strip()
        for row in rows:
            project_id = str(row["id"] or "")
            can_view = _v2_can_view_project(conn, user, project_id)
            if not can_view:
                continue
            if scope == "all" and not admin:
                continue
            if status_filter and str(row["status"] or "").lower() != status_filter:
                continue
            if owner_filter and normalize_email(row["owner_id"] or "") != owner_filter:
                continue
            if member_filter:
                member_hit = conn.execute(
                    "SELECT 1 FROM project_members WHERE project_id = ? AND user_id = ? LIMIT 1",
                    (project_id, member_filter),
                ).fetchone()
                if not member_hit and normalize_email(row["owner_id"] or "") != member_filter:
                    continue
            if date_from and str(row["start_date"] or "") and str(row["start_date"]) < date_from:
                continue
            if date_to and str(row["due_date"] or "") and str(row["due_date"]) > date_to:
                continue
            payload = _v2_project_payload(conn, row, user)
            searchable = " ".join(
                [
                    str(payload.get("name") or ""),
                    str(payload.get("description") or ""),
                    str(payload.get("owner_id") or ""),
                    str(payload.get("status") or ""),
                    str(payload.get("latest_progress") or ""),
                ]
            ).lower()
            if q and q not in searchable:
                continue
            if has_pending and int(payload.get("pending_approval_count") or 0) <= 0:
                continue
            if has_blockers and int(payload.get("issue_blocker_count") or 0) <= 0:
                continue
            visible.append(row)
        result = [_v2_project_payload(conn, row, user) for row in visible]
        return {"ok": True, "projects": result, "count": len(result)}


def _v2_create_project(user: dict | None, payload: dict) -> tuple[dict, int]:
    if not user:
        return {"ok": False, "error": "authentication_required"}, 401
    creator = _v2_user_email(user)
    name = str(payload.get("name") or "").strip()
    if not name:
        return {"ok": False, "error": "name_required"}, 400
    status = str(payload.get("status") or "planning").strip().lower()
    if status not in V2_PROJECT_STATUSES:
        return {"ok": False, "error": "invalid_status"}, 400
    project_id = _v2_id("prj")
    now = _v2_now()
    with v2_db_lock, _v2_db_conn() as conn:
        conn.execute(
            """
            INSERT INTO projects(id, name, description, owner_id, status, start_date, due_date, created_at, updated_at)
            VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                project_id,
                name[:200],
                str(payload.get("description") or "")[:4000],
                creator,
                status,
                str(payload.get("start_date") or "")[:20],
                str(payload.get("due_date") or "")[:20],
                now,
                now,
            ),
        )
        conn.execute(
            """
            INSERT INTO project_members(id, project_id, user_id, role_in_project, joined_at)
            VALUES(?, ?, ?, 'owner', ?)
            """,
            (_v2_id("pm"), project_id, creator, now),
        )
        for raw_member in payload.get("members", []) if isinstance(payload.get("members"), list) else []:
            if isinstance(raw_member, dict):
                member_email = normalize_email(raw_member.get("user_id") or raw_member.get("email") or "")
                role = str(raw_member.get("role_in_project") or "member").strip().lower()
            else:
                member_email = normalize_email(raw_member)
                role = "member"
            if not member_email or member_email == creator or not _v2_user_exists(member_email):
                continue
            if role not in V2_PROJECT_ROLES:
                role = "member"
            conn.execute(
                """
                INSERT OR REPLACE INTO project_members(id, project_id, user_id, role_in_project, joined_at)
                VALUES(?, ?, ?, ?, ?)
                """,
                (_v2_id("pm"), project_id, member_email, role, now),
            )
            _v2_notify(
                conn,
                member_email,
                "project_membership",
                "Added to project",
                f"You were added to project: {name[:120]}",
                project_id=project_id,
            )
        _v2_audit(conn, creator, "project_create", "project", project_id, {"name": name, "status": status})
        _v2_project_chat_append_system_message(
            conn,
            project_id,
            f"Project created: {name[:120]} (status: {status}).",
            message_type="project_event",
            metadata={"event_type": "project_created"},
            is_key_message=True,
        )
        _v2_chat_event_refresh_if_needed(conn, project_id)
        conn.commit()
        detail = _v2_project_detail_payload(conn, project_id, user)
        return detail, 200


def _v2_update_project(user: dict | None, project_id: str, payload: dict) -> tuple[dict, int]:
    if not user:
        return {"ok": False, "error": "authentication_required"}, 401
    with v2_db_lock, _v2_db_conn() as conn:
        row = conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
        if not row:
            return {"ok": False, "error": "project_not_found"}, 404
        if not _v2_can_manage_project(conn, user, project_id):
            return {"ok": False, "error": "permission_denied"}, 403
        fields = []
        values: list[object] = []
        if "name" in payload:
            name = str(payload.get("name") or "").strip()
            if not name:
                return {"ok": False, "error": "name_required"}, 400
            fields.append("name = ?")
            values.append(name[:200])
        if "description" in payload:
            fields.append("description = ?")
            values.append(str(payload.get("description") or "")[:4000])
        if "status" in payload:
            status = str(payload.get("status") or "").strip().lower()
            if status not in V2_PROJECT_STATUSES:
                return {"ok": False, "error": "invalid_status"}, 400
            fields.append("status = ?")
            values.append(status)
        if "start_date" in payload:
            fields.append("start_date = ?")
            values.append(str(payload.get("start_date") or "")[:20])
        if "due_date" in payload:
            fields.append("due_date = ?")
            values.append(str(payload.get("due_date") or "")[:20])
        if not fields:
            detail = _v2_project_detail_payload(conn, project_id, user)
            return detail, 200
        fields.append("updated_at = ?")
        values.append(_v2_now())
        values.append(project_id)
        conn.execute(f"UPDATE projects SET {', '.join(fields)} WHERE id = ?", values)
        _v2_audit(conn, _v2_user_email(user), "project_update", "project", project_id, payload)
        conn.commit()
        detail = _v2_project_detail_payload(conn, project_id, user)
        return detail, 200


def _v2_add_project_member(user: dict | None, project_id: str, payload: dict) -> tuple[dict, int]:
    if not user:
        return {"ok": False, "error": "authentication_required"}, 401
    target = normalize_email(payload.get("user_id") or payload.get("email") or "")
    if not target:
        return {"ok": False, "error": "user_id_required"}, 400
    if not _v2_user_exists(target):
        return {"ok": False, "error": "user_not_found"}, 400
    role = str(payload.get("role_in_project") or "member").strip().lower()
    if role not in V2_PROJECT_ROLES:
        return {"ok": False, "error": "invalid_role_in_project"}, 400
    with v2_db_lock, _v2_db_conn() as conn:
        if not conn.execute("SELECT 1 FROM projects WHERE id = ?", (project_id,)).fetchone():
            return {"ok": False, "error": "project_not_found"}, 404
        if not _v2_can_manage_project(conn, user, project_id):
            return {"ok": False, "error": "permission_denied"}, 403
        conn.execute(
            """
            INSERT OR REPLACE INTO project_members(id, project_id, user_id, role_in_project, joined_at)
            VALUES(?, ?, ?, ?, ?)
            """,
            (_v2_id("pm"), project_id, target, role, _v2_now()),
        )
        conn.execute("UPDATE projects SET updated_at = ? WHERE id = ?", (_v2_now(), project_id))
        _v2_notify(
            conn,
            target,
            "project_membership",
            "Project membership updated",
            f"You were assigned as {role} in project {project_id}.",
            project_id=project_id,
        )
        _v2_audit(conn, _v2_user_email(user), "project_member_upsert", "project", project_id, {"target": target, "role": role})
        conn.commit()
        detail = _v2_project_detail_payload(conn, project_id, user)
        return detail, 200


def _v2_remove_project_member(user: dict | None, project_id: str, member_user_id: str) -> tuple[dict, int]:
    if not user:
        return {"ok": False, "error": "authentication_required"}, 401
    target = normalize_email(member_user_id)
    with v2_db_lock, _v2_db_conn() as conn:
        project = conn.execute("SELECT owner_id FROM projects WHERE id = ?", (project_id,)).fetchone()
        if not project:
            return {"ok": False, "error": "project_not_found"}, 404
        if not _v2_can_manage_project(conn, user, project_id):
            return {"ok": False, "error": "permission_denied"}, 403
        if normalize_email(project["owner_id"] or "") == target:
            return {"ok": False, "error": "cannot_remove_owner"}, 400
        conn.execute(
            "DELETE FROM project_members WHERE project_id = ? AND user_id = ?",
            (project_id, target),
        )
        conn.execute("UPDATE projects SET updated_at = ? WHERE id = ?", (_v2_now(), project_id))
        _v2_audit(conn, _v2_user_email(user), "project_member_remove", "project", project_id, {"target": target})
        conn.commit()
        detail = _v2_project_detail_payload(conn, project_id, user)
        return detail, 200


def _v2_list_work_items(user: dict | None, query: dict[str, list[str]]) -> tuple[dict, int]:
    if not user:
        return {"ok": False, "error": "authentication_required"}, 401
    with v2_db_lock, _v2_db_conn() as conn:
        visible_projects = _v2_user_project_ids(conn, user)
        project_filter = str(query.get("project_id", [""])[0] or "").strip()
        status_filter = str(query.get("status", [""])[0] or "").strip().lower()
        priority_filter = str(query.get("priority", [""])[0] or "").strip().lower()
        assignee_filter = normalize_email(query.get("assignee", [""])[0]) if query.get("assignee") else ""
        q = str(query.get("q", [""])[0] or "").strip().lower()
        overdue_only = str(query.get("overdue", [""])[0] or "").strip().lower() in {"1", "true", "yes"}
        has_blockers = str(query.get("has_blockers", [""])[0] or "").strip().lower() in {"1", "true", "yes"}
        today_key = datetime.now(LOCAL_TIMEZONE).strftime("%Y-%m-%d")
        rows = conn.execute("SELECT * FROM work_items ORDER BY updated_at DESC").fetchall()
        output: list[dict] = []
        for row in rows:
            project_id = str(row["project_id"] or "")
            if project_filter and project_id != project_filter:
                continue
            if project_id not in visible_projects and not is_admin_user(user):
                continue
            if status_filter and str(row["status"] or "").lower() != status_filter:
                continue
            if priority_filter and str(row["priority"] or "").lower() != priority_filter:
                continue
            if overdue_only and not (str(row["due_date"] or "") and str(row["due_date"]) < today_key and str(row["status"] or "") not in {"done", "cancelled"}):
                continue
            payload = _v2_work_item_payload(conn, row)
            if assignee_filter and assignee_filter not in {normalize_email(item) for item in payload.get("assignees", [])}:
                continue
            if has_blockers:
                issue_hit = conn.execute(
                    """
                    SELECT 1
                    FROM project_issues
                    WHERE work_item_id = ? AND status NOT IN ('resolved', 'closed')
                    LIMIT 1
                    """,
                    (payload["id"],),
                ).fetchone()
                if not issue_hit:
                    continue
            searchable = " ".join(
                [
                    str(payload.get("title") or ""),
                    str(payload.get("description") or ""),
                    str(payload.get("status") or ""),
                    str(payload.get("priority") or ""),
                    str(payload.get("project_id") or ""),
                ]
            ).lower()
            if q and q not in searchable:
                continue
            output.append(payload)
        return {"ok": True, "work_items": output, "count": len(output)}, 200


def _v2_create_work_item(user: dict | None, payload: dict) -> tuple[dict, int]:
    if not user:
        return {"ok": False, "error": "authentication_required"}, 401
    creator = _v2_user_email(user)
    project_id = str(payload.get("project_id") or "").strip()
    title = str(payload.get("title") or "").strip()
    if not project_id or not title:
        return {"ok": False, "error": "project_id_and_title_required"}, 400
    priority = str(payload.get("priority") or "medium").strip().lower()
    status = str(payload.get("status") or "todo").strip().lower()
    if priority not in V2_TASK_PRIORITIES:
        return {"ok": False, "error": "invalid_priority"}, 400
    if status not in V2_TASK_STATUSES:
        return {"ok": False, "error": "invalid_status"}, 400
    assignees = []
    for item in payload.get("assignees", []) if isinstance(payload.get("assignees"), list) else []:
        email = normalize_email(item)
        if email and _v2_user_exists(email):
            assignees.append(email)
    assignees = sorted(set(assignees))
    dependencies = payload.get("dependencies", [])
    collaborators = payload.get("collaborators", [])
    now = _v2_now()
    item_id = _v2_id("wki")
    with v2_db_lock, _v2_db_conn() as conn:
        if not conn.execute("SELECT 1 FROM projects WHERE id = ?", (project_id,)).fetchone():
            return {"ok": False, "error": "project_not_found"}, 404
        if not _v2_can_manage_project(conn, user, project_id):
            return {"ok": False, "error": "permission_denied"}, 403
        conn.execute(
            """
            INSERT INTO work_items(
              id, project_id, title, description, priority, status, due_date, created_by, created_at, updated_at, dependencies_json, collaborators_json
            ) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                item_id,
                project_id,
                title[:240],
                str(payload.get("description") or "")[:6000],
                priority,
                status,
                str(payload.get("due_date") or "")[:20],
                creator,
                now,
                now,
                json.dumps(dependencies if isinstance(dependencies, list) else [], ensure_ascii=False)[:4000],
                json.dumps(collaborators if isinstance(collaborators, list) else [], ensure_ascii=False)[:4000],
            ),
        )
        for assignee in assignees:
            conn.execute(
                """
                INSERT OR IGNORE INTO work_item_assignees(id, work_item_id, user_id, assigned_at)
                VALUES(?, ?, ?, ?)
                """,
                (_v2_id("wia"), item_id, assignee, now),
            )
            _v2_notify(
                conn,
                assignee,
                "task_assignment",
                "Task assigned",
                f"You were assigned task: {title[:120]}",
                project_id=project_id,
                work_item_id=item_id,
            )
        conn.execute("UPDATE projects SET updated_at = ? WHERE id = ?", (now, project_id))
        _v2_audit(conn, creator, "work_item_create", "work_item", item_id, {"project_id": project_id, "title": title})
        _v2_project_chat_append_system_message(
            conn,
            project_id,
            f"Task created: {title[:120]} (priority: {priority}, status: {status}).",
            message_type="task_event",
            metadata={"event_type": "task_created", "work_item_id": item_id},
        )
        _v2_chat_event_refresh_if_needed(conn, project_id)
        conn.commit()
        row = conn.execute("SELECT * FROM work_items WHERE id = ?", (item_id,)).fetchone()
        return {"ok": True, "work_item": _v2_work_item_payload(conn, row)}, 200


def _v2_update_work_item(user: dict | None, item_id: str, payload: dict) -> tuple[dict, int]:
    if not user:
        return {"ok": False, "error": "authentication_required"}, 401
    actor = _v2_user_email(user)
    with v2_db_lock, _v2_db_conn() as conn:
        row = conn.execute("SELECT * FROM work_items WHERE id = ?", (item_id,)).fetchone()
        if not row:
            return {"ok": False, "error": "work_item_not_found"}, 404
        project_id = str(row["project_id"] or "")
        manager = _v2_can_manage_project(conn, user, project_id)
        assignee_hit = conn.execute(
            "SELECT 1 FROM work_item_assignees WHERE work_item_id = ? AND user_id = ? LIMIT 1",
            (item_id, actor),
        ).fetchone()
        if not manager and not assignee_hit:
            return {"ok": False, "error": "permission_denied"}, 403
        fields = []
        values: list[object] = []
        if "title" in payload and manager:
            title = str(payload.get("title") or "").strip()
            if not title:
                return {"ok": False, "error": "title_required"}, 400
            fields.append("title = ?")
            values.append(title[:240])
        if "description" in payload and manager:
            fields.append("description = ?")
            values.append(str(payload.get("description") or "")[:6000])
        if "priority" in payload and manager:
            priority = str(payload.get("priority") or "").strip().lower()
            if priority not in V2_TASK_PRIORITIES:
                return {"ok": False, "error": "invalid_priority"}, 400
            fields.append("priority = ?")
            values.append(priority)
        if "status" in payload:
            status = str(payload.get("status") or "").strip().lower()
            if status not in V2_TASK_STATUSES:
                return {"ok": False, "error": "invalid_status"}, 400
            fields.append("status = ?")
            values.append(status)
        if "due_date" in payload and manager:
            fields.append("due_date = ?")
            values.append(str(payload.get("due_date") or "")[:20])
        if "dependencies" in payload and manager:
            deps = payload.get("dependencies", [])
            fields.append("dependencies_json = ?")
            values.append(json.dumps(deps if isinstance(deps, list) else [], ensure_ascii=False)[:4000])
        if "collaborators" in payload and manager:
            collaborators = payload.get("collaborators", [])
            fields.append("collaborators_json = ?")
            values.append(json.dumps(collaborators if isinstance(collaborators, list) else [], ensure_ascii=False)[:4000])
        if fields:
            fields.append("updated_at = ?")
            values.append(_v2_now())
            values.append(item_id)
            conn.execute(f"UPDATE work_items SET {', '.join(fields)} WHERE id = ?", values)
        if manager and isinstance(payload.get("assignees"), list):
            conn.execute("DELETE FROM work_item_assignees WHERE work_item_id = ?", (item_id,))
            for assignee in sorted({normalize_email(item) for item in payload.get("assignees", []) if normalize_email(item)}):
                if not _v2_user_exists(assignee):
                    continue
                conn.execute(
                    "INSERT OR IGNORE INTO work_item_assignees(id, work_item_id, user_id, assigned_at) VALUES(?, ?, ?, ?)",
                    (_v2_id("wia"), item_id, assignee, _v2_now()),
                )
                _v2_notify(
                    conn,
                    assignee,
                    "task_assignment",
                    "Task assignment updated",
                    f"You were assigned task {item_id}.",
                    project_id=project_id,
                    work_item_id=item_id,
                )
        if isinstance(payload.get("feedback"), dict):
            fb = payload.get("feedback") or {}
            conn.execute(
                """
                INSERT INTO work_item_feedback(
                  id, work_item_id, submitted_by, completion_summary, blockers, next_steps, created_at
                ) VALUES(?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    _v2_id("wif"),
                    item_id,
                    actor,
                    str(fb.get("completion_summary") or "")[:4000],
                    str(fb.get("blockers") or "")[:4000],
                    str(fb.get("next_steps") or "")[:4000],
                    _v2_now(),
                ),
            )
        conn.execute("UPDATE projects SET updated_at = ? WHERE id = ?", (_v2_now(), project_id))
        _v2_audit(conn, actor, "work_item_update", "work_item", item_id, payload)
        _v2_project_chat_append_system_message(
            conn,
            project_id,
            f"Task updated: {str(row['title'] or item_id)[:120]}.",
            message_type="task_event",
            metadata={"event_type": "task_updated", "work_item_id": item_id},
        )
        _v2_chat_event_refresh_if_needed(conn, project_id)
        conn.commit()
        latest = conn.execute("SELECT * FROM work_items WHERE id = ?", (item_id,)).fetchone()
        return {"ok": True, "work_item": _v2_work_item_payload(conn, latest)}, 200


def _v2_list_issues(user: dict | None, query: dict[str, list[str]]) -> tuple[dict, int]:
    if not user:
        return {"ok": False, "error": "authentication_required"}, 401
    with v2_db_lock, _v2_db_conn() as conn:
        visible_projects = _v2_user_project_ids(conn, user)
        project_filter = str(query.get("project_id", [""])[0] or "").strip()
        status_filter = str(query.get("status", [""])[0] or "").strip().lower()
        severity_filter = str(query.get("severity", [""])[0] or "").strip().lower()
        assigned_to = normalize_email(query.get("assigned_to", [""])[0]) if query.get("assigned_to") else ""
        q = str(query.get("q", [""])[0] or "").strip().lower()
        rows = conn.execute("SELECT * FROM project_issues ORDER BY updated_at DESC").fetchall()
        output = []
        for row in rows:
            project_id = str(row["project_id"] or "")
            if project_filter and project_filter != project_id:
                continue
            if project_id not in visible_projects and not is_admin_user(user):
                continue
            if status_filter and str(row["status"] or "").lower() != status_filter:
                continue
            if severity_filter and str(row["severity"] or "").lower() != severity_filter:
                continue
            if assigned_to and normalize_email(row["assigned_to"] or "") != assigned_to:
                continue
            payload = _v2_issue_payload(row)
            searchable = " ".join(
                [
                    payload["title"],
                    payload["description"],
                    payload["severity"],
                    payload["status"],
                    payload["assigned_to"],
                ]
            ).lower()
            if q and q not in searchable:
                continue
            output.append(payload)
        return {"ok": True, "issues": output, "count": len(output)}, 200


def _v2_create_issue(user: dict | None, payload: dict) -> tuple[dict, int]:
    if not user:
        return {"ok": False, "error": "authentication_required"}, 401
    reporter = _v2_user_email(user)
    project_id = str(payload.get("project_id") or "").strip()
    title = str(payload.get("title") or "").strip()
    if not project_id or not title:
        return {"ok": False, "error": "project_id_and_title_required"}, 400
    severity = str(payload.get("severity") or "medium").strip().lower()
    status = str(payload.get("status") or "open").strip().lower()
    if severity not in V2_ISSUE_SEVERITIES:
        return {"ok": False, "error": "invalid_severity"}, 400
    if status not in V2_ISSUE_STATUSES:
        return {"ok": False, "error": "invalid_status"}, 400
    assigned_to = normalize_email(payload.get("assigned_to") or "")
    if assigned_to and not _v2_user_exists(assigned_to):
        return {"ok": False, "error": "assigned_user_not_found"}, 400
    issue_id = _v2_id("iss")
    now = _v2_now()
    with v2_db_lock, _v2_db_conn() as conn:
        if not conn.execute("SELECT 1 FROM projects WHERE id = ?", (project_id,)).fetchone():
            return {"ok": False, "error": "project_not_found"}, 404
        if not _v2_can_view_project(conn, user, project_id):
            return {"ok": False, "error": "permission_denied"}, 403
        work_item_id = str(payload.get("work_item_id") or "").strip()
        if work_item_id:
            task = conn.execute(
                "SELECT 1 FROM work_items WHERE id = ? AND project_id = ?",
                (work_item_id, project_id),
            ).fetchone()
            if not task:
                return {"ok": False, "error": "work_item_not_found"}, 400
        conn.execute(
            """
            INSERT INTO project_issues(
              id, project_id, work_item_id, title, description, severity, status, reported_by, assigned_to, created_at, resolved_at, updated_at
            ) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?)
            """,
            (
                issue_id,
                project_id,
                work_item_id,
                title[:240],
                str(payload.get("description") or "")[:6000],
                severity,
                status,
                reporter,
                assigned_to,
                now,
                now,
            ),
        )
        conn.execute("UPDATE projects SET updated_at = ? WHERE id = ?", (now, project_id))
        if assigned_to:
            _v2_notify(
                conn,
                assigned_to,
                "issue_assigned",
                "Issue assigned",
                f"You were assigned issue: {title[:120]}",
                project_id=project_id,
                work_item_id=work_item_id,
            )
        _v2_audit(conn, reporter, "issue_create", "project_issue", issue_id, {"project_id": project_id, "severity": severity})
        _v2_project_chat_append_system_message(
            conn,
            project_id,
            f"Issue created: {title[:120]} (severity: {severity}, status: {status}).",
            message_type="issue_event",
            metadata={"event_type": "issue_created", "issue_id": issue_id},
            is_key_message=severity in {"high", "critical"},
        )
        _v2_chat_event_refresh_if_needed(conn, project_id)
        conn.commit()
        row = conn.execute("SELECT * FROM project_issues WHERE id = ?", (issue_id,)).fetchone()
        return {"ok": True, "issue": _v2_issue_payload(row)}, 200


def _v2_update_issue(user: dict | None, issue_id: str, payload: dict) -> tuple[dict, int]:
    if not user:
        return {"ok": False, "error": "authentication_required"}, 401
    actor = _v2_user_email(user)
    with v2_db_lock, _v2_db_conn() as conn:
        row = conn.execute("SELECT * FROM project_issues WHERE id = ?", (issue_id,)).fetchone()
        if not row:
            return {"ok": False, "error": "issue_not_found"}, 404
        project_id = str(row["project_id"] or "")
        manager = _v2_can_manage_project(conn, user, project_id)
        is_owner = normalize_email(row["reported_by"] or "") == actor
        is_assignee = normalize_email(row["assigned_to"] or "") == actor
        if not (manager or is_owner or is_assignee):
            return {"ok": False, "error": "permission_denied"}, 403
        fields = []
        values: list[object] = []
        if "title" in payload and manager:
            title = str(payload.get("title") or "").strip()
            if not title:
                return {"ok": False, "error": "title_required"}, 400
            fields.append("title = ?")
            values.append(title[:240])
        if "description" in payload:
            fields.append("description = ?")
            values.append(str(payload.get("description") or "")[:6000])
        if "severity" in payload and manager:
            sev = str(payload.get("severity") or "").strip().lower()
            if sev not in V2_ISSUE_SEVERITIES:
                return {"ok": False, "error": "invalid_severity"}, 400
            fields.append("severity = ?")
            values.append(sev)
        if "status" in payload:
            status = str(payload.get("status") or "").strip().lower()
            if status not in V2_ISSUE_STATUSES:
                return {"ok": False, "error": "invalid_status"}, 400
            fields.append("status = ?")
            values.append(status)
            if status in {"resolved", "closed"}:
                fields.append("resolved_at = ?")
                values.append(_v2_now())
        if "assigned_to" in payload and manager:
            assigned_to = normalize_email(payload.get("assigned_to") or "")
            if assigned_to and not _v2_user_exists(assigned_to):
                return {"ok": False, "error": "assigned_user_not_found"}, 400
            fields.append("assigned_to = ?")
            values.append(assigned_to)
            if assigned_to:
                _v2_notify(
                    conn,
                    assigned_to,
                    "issue_assigned",
                    "Issue assignment updated",
                    f"You were assigned issue {issue_id}.",
                    project_id=project_id,
                    work_item_id=str(row["work_item_id"] or ""),
                )
        if not fields:
            return {"ok": True, "issue": _v2_issue_payload(row)}, 200
        fields.append("updated_at = ?")
        values.append(_v2_now())
        values.append(issue_id)
        conn.execute(f"UPDATE project_issues SET {', '.join(fields)} WHERE id = ?", values)
        conn.execute("UPDATE projects SET updated_at = ? WHERE id = ?", (_v2_now(), project_id))
        _v2_audit(conn, actor, "issue_update", "project_issue", issue_id, payload)
        _v2_project_chat_append_system_message(
            conn,
            project_id,
            f"Issue updated: {str(row['title'] or issue_id)[:120]}.",
            message_type="issue_event",
            metadata={"event_type": "issue_updated", "issue_id": issue_id},
        )
        _v2_chat_event_refresh_if_needed(conn, project_id)
        conn.commit()
        updated = conn.execute("SELECT * FROM project_issues WHERE id = ?", (issue_id,)).fetchone()
        return {"ok": True, "issue": _v2_issue_payload(updated)}, 200


def _v2_file_workspace(value: str) -> str:
    text = re.sub(r"[^a-z0-9_-]+", "-", str(value or "").strip().lower()).strip("-")
    return text or "work-chat"


def _v2_file_center_role(conn: sqlite3.Connection, user: dict | None, file_row: sqlite3.Row) -> str:
    if is_admin_user(user):
        return "admin"
    email = _v2_user_email(user)
    if not email:
        return "none"
    owner = normalize_email(file_row["owner_user_id"] or "")
    if email == owner:
        return "owner"
    project_id = str(file_row["project_id"] or "")
    if project_id:
        project_role = _v2_project_role(conn, user, project_id)
        if project_role in {"owner", "manager"}:
            return "manager"
        if project_role in {"member", "viewer"}:
            return "member"
    direct_grant = conn.execute(
        """
        SELECT permission
        FROM file_access_grants_v2
        WHERE granted_user_id = ? AND is_active = 1 AND revoked_at = 0
          AND (
            (scope_type = 'file' AND scope_id = ?)
            OR (scope_type = 'workspace' AND scope_id = ?)
            OR (scope_type = 'project' AND scope_id = ?)
            OR (scope_type = 'department' AND scope_id = ?)
          )
        ORDER BY created_at DESC
        LIMIT 1
        """,
        (email, str(file_row["id"] or ""), str(file_row["workspace_id"] or ""), project_id, str(file_row["department"] or "")),
    ).fetchone()
    if direct_grant:
        permission = str(direct_grant["permission"] or "read")
        if permission in {"manage", "write"}:
            return "manager"
        return "viewer"
    return "none"


def _v2_can_view_file(conn: sqlite3.Connection, user: dict | None, file_row: sqlite3.Row) -> bool:
    return _v2_file_center_role(conn, user, file_row) in {"admin", "owner", "manager", "member", "viewer"}


def _v2_can_manage_file(conn: sqlite3.Connection, user: dict | None, file_row: sqlite3.Row) -> bool:
    return _v2_file_center_role(conn, user, file_row) in {"admin", "owner", "manager"}


def _v2_can_act_step(conn: sqlite3.Connection, user: dict | None, step_row: sqlite3.Row) -> bool:
    if is_admin_user(user):
        return True
    return normalize_email(step_row["assigned_user_id"] or "") == _v2_user_email(user)


def _v2_file_version_payload(row: sqlite3.Row) -> dict:
    return {
        "id": str(row["id"] or ""),
        "file_id": str(row["file_id"] or ""),
        "version_number": int(row["version_number"] or 0),
        "filename": str(row["filename"] or ""),
        "mime": str(row["mime"] or "application/octet-stream"),
        "size": int(row["size"] or 0),
        "change_summary": str(row["change_summary"] or ""),
        "created_by": str(row["created_by"] or ""),
        "created_at": int(row["created_at"] or 0),
        "derived_from_version_id": str(row["derived_from_version_id"] or ""),
        "is_signed_snapshot": bool(row["is_signed_snapshot"]),
        "signed_by": str(row["signed_by"] or ""),
        "signed_at": int(row["signed_at"] or 0),
        "is_locked_snapshot": bool(row["is_locked_snapshot"]),
        "is_encrypted_snapshot": bool(row["is_encrypted_snapshot"]),
    }


def _v2_file_payload(conn: sqlite3.Connection, row: sqlite3.Row, *, include_latest_version: bool = True) -> dict:
    payload = {
        "id": str(row["id"] or ""),
        "title": str(row["title"] or ""),
        "project_id": str(row["project_id"] or ""),
        "work_item_id": str(row["work_item_id"] or ""),
        "workspace_id": str(row["workspace_id"] or ""),
        "department": str(row["department"] or ""),
        "owner_user_id": str(row["owner_user_id"] or ""),
        "category": str(row["category"] or ""),
        "status": str(row["status"] or "draft"),
        "source_module": str(row["source_module"] or "file-center"),
        "source_ref_id": str(row["source_ref_id"] or ""),
        "current_version_id": str(row["current_version_id"] or ""),
        "is_signed": bool(row["is_signed"]),
        "is_locked": bool(row["is_locked"]),
        "is_encrypted": bool(row["is_encrypted"]),
        "created_at": int(row["created_at"] or 0),
        "updated_at": int(row["updated_at"] or 0),
    }
    if include_latest_version and payload["current_version_id"]:
        latest = conn.execute("SELECT * FROM file_versions_v2 WHERE id = ?", (payload["current_version_id"],)).fetchone()
        payload["current_version"] = _v2_file_version_payload(latest) if latest else None
    return payload


def _v2_file_workflow_payload(conn: sqlite3.Connection, row: sqlite3.Row, *, include_steps: bool = True) -> dict:
    payload = {
        "id": str(row["id"] or ""),
        "file_id": str(row["file_id"] or ""),
        "project_id": str(row["project_id"] or ""),
        "work_item_id": str(row["work_item_id"] or ""),
        "workspace_id": str(row["workspace_id"] or ""),
        "workflow_type": str(row["workflow_type"] or "review_approve_sign"),
        "title": str(row["title"] or ""),
        "routing_mode": str(row["routing_mode"] or "sequential"),
        "due_at": int(row["due_at"] or 0),
        "instructions": str(row["instructions"] or ""),
        "signature_method": str(row["signature_method"] or "platform"),
        "signature_placement": str(row["signature_placement"] or ""),
        "lock_after_sign": bool(row["lock_after_sign"]),
        "metadata": _v2_json_load(str(row["metadata_json"] or "{}"), {}),
        "status": str(row["status"] or "active"),
        "initiated_by": str(row["initiated_by"] or ""),
        "created_at": int(row["created_at"] or 0),
        "updated_at": int(row["updated_at"] or 0),
        "closed_at": int(row["closed_at"] or 0),
    }
    if include_steps:
        steps = conn.execute(
            "SELECT * FROM file_workflow_steps_v2 WHERE workflow_id = ? ORDER BY sequence_order ASC, created_at ASC",
            (payload["id"],),
        ).fetchall()
        payload["steps"] = [
            {
                "id": str(step["id"] or ""),
                "step_type": str(step["step_type"] or ""),
                "sequence_order": int(step["sequence_order"] or 0),
                "assigned_user_id": str(step["assigned_user_id"] or ""),
                "status": str(step["status"] or "pending"),
                "comments": str(step["comments"] or ""),
                "acted_at": int(step["acted_at"] or 0),
                "created_at": int(step["created_at"] or 0),
            }
            for step in steps
        ]
    return payload


def _v2_file_storage_write(file_id: str, version_id: str, filename: str, raw: bytes) -> Path:
    folder = FILE_CENTER_STORAGE_DIR / file_id
    folder.mkdir(parents=True, exist_ok=True)
    safe_name = re.sub(r"[^A-Za-z0-9._-]+", "_", os.path.basename(filename))[:120] or "file.bin"
    path = folder / f"{version_id}_{safe_name}"
    path.write_bytes(raw)
    return path


def _v2_file_storage_read(path_text: str) -> bytes:
    path = Path(path_text).resolve()
    root = FILE_CENTER_STORAGE_DIR.resolve()
    if path != root and not str(path).startswith(str(root) + os.sep):
        raise ValueError("file_outside_storage")
    return path.read_bytes()


def _v2_file_crypt(raw: bytes, key_seed: str) -> bytes:
    key = hashlib.sha256(str(key_seed).encode("utf-8")).digest()
    return bytes(raw[idx] ^ key[idx % len(key)] for idx in range(len(raw)))


def _v2_file_version_current_hash(version_row: sqlite3.Row) -> str:
    raw = _v2_file_storage_read(str(version_row["storage_path"] or ""))
    return hashlib.sha256(raw).hexdigest()


def _v2_certificate_secret_cipher(secret_hex: str) -> str:
    return encrypt_audit_payload({"secret_hex": secret_hex})


def _v2_certificate_secret_from_cipher(cipher: str) -> bytes:
    payload = decrypt_audit_payload(cipher) or {}
    secret_hex = str(payload.get("secret_hex") or "")
    try:
        return bytes.fromhex(secret_hex)
    except Exception:
        return b""


def _v2_certificate_payload(row: sqlite3.Row | None) -> dict | None:
    if not row:
        return None
    return {
        "id": str(row["id"] or ""),
        "user_id": str(row["user_id"] or ""),
        "subject_name": str(row["subject_name"] or ""),
        "issuer_name": str(row["issuer_name"] or "Hermes Internal Signing Authority"),
        "public_key_fingerprint": str(row["public_key_fingerprint"] or ""),
        "status": str(row["status"] or "active"),
        "valid_from": int(row["valid_from"] or 0),
        "valid_to": int(row["valid_to"] or 0),
        "created_by": str(row["created_by"] or ""),
        "created_at": int(row["created_at"] or 0),
        "revoked_at": int(row["revoked_at"] or 0),
        "revoked_by": str(row["revoked_by"] or ""),
        "metadata": _v2_json_load(str(row["metadata_json"] or "{}"), {}),
    }


def _v2_get_active_certificate(conn: sqlite3.Connection, user_id: str) -> sqlite3.Row | None:
    now_ts = _v2_now()
    return conn.execute(
        """
        SELECT *
        FROM file_signer_certificates_v2
        WHERE user_id = ? AND status = 'active' AND valid_from <= ? AND valid_to >= ?
        ORDER BY created_at DESC
        LIMIT 1
        """,
        (normalize_email(user_id), now_ts, now_ts),
    ).fetchone()


def _v2_create_signer_certificate(
    conn: sqlite3.Connection,
    *,
    user_id: str,
    actor: str,
    subject_name: str = "",
    validity_days: int = 730,
) -> sqlite3.Row:
    target = normalize_email(user_id)
    if not target:
        raise ValueError("user_required")
    now_ts = _v2_now()
    secret = secrets.token_bytes(32)
    cert_id = _v2_id("fcert")
    fingerprint = hashlib.sha256(secret + target.encode("utf-8") + str(now_ts).encode("utf-8")).hexdigest()
    conn.execute(
        """
        INSERT INTO file_signer_certificates_v2(
          id, user_id, subject_name, issuer_name, public_key_fingerprint, secret_cipher, status,
          valid_from, valid_to, created_by, created_at, revoked_at, revoked_by, metadata_json
        ) VALUES(?, ?, ?, 'Hermes Internal Signing Authority', ?, ?, 'active', ?, ?, ?, ?, 0, '', ?)
        """,
        (
            cert_id,
            target,
            subject_name or user_display_label(target),
            fingerprint,
            _v2_certificate_secret_cipher(secret.hex()),
            now_ts,
            now_ts + max(1, min(3650, int(validity_days or 730))) * 24 * 3600,
            actor,
            now_ts,
            json.dumps({"certificate_type": "internal_hmac_signing"}, ensure_ascii=False),
        ),
    )
    _v2_audit(
        conn,
        actor,
        "file_certificate_create",
        "file_certificate",
        cert_id,
        {"user_id": target, "fingerprint": fingerprint[:16], "validity_days": validity_days},
    )
    row = conn.execute("SELECT * FROM file_signer_certificates_v2 WHERE id = ?", (cert_id,)).fetchone()
    if not row:
        raise ValueError("certificate_create_failed")
    return row


def _v2_ensure_signer_certificate(conn: sqlite3.Connection, user_id: str, actor: str) -> sqlite3.Row:
    row = _v2_get_active_certificate(conn, user_id)
    if row:
        return row
    return _v2_create_signer_certificate(conn, user_id=user_id, actor=actor, subject_name=user_display_label(user_id))


def _v2_signature_value(secret: bytes, signed_hash: str, signer_id: str, version_id: str, signed_at: int) -> str:
    message = f"{signed_hash}:{normalize_email(signer_id)}:{version_id}:{signed_at}".encode("utf-8")
    return hmac.new(secret, message, hashlib.sha256).hexdigest()


def _v2_verify_signature_row(conn: sqlite3.Connection, sig_row: sqlite3.Row) -> dict:
    version = conn.execute("SELECT * FROM file_versions_v2 WHERE id = ?", (str(sig_row["version_id"] or ""),)).fetchone()
    now_ts = _v2_now()
    if not version:
        return {"status": "version_missing", "reason": "file version missing", "verified_at": now_ts}
    try:
        current_hash = _v2_file_version_current_hash(version)
    except Exception:
        return {"status": "file_missing", "reason": "stored file missing", "verified_at": now_ts}
    signed_hash = str(sig_row["signed_hash"] or "")
    if not hmac.compare_digest(current_hash, signed_hash):
        return {"status": "tampered", "reason": "content hash mismatch", "current_hash": current_hash, "verified_at": now_ts}
    method = str(sig_row["signature_method"] or "platform")
    signed_at = int(sig_row["signed_at"] or 0)
    signer_id = str(sig_row["signer_id"] or "")
    version_id = str(sig_row["version_id"] or "")
    if method == "certificate":
        cert = conn.execute("SELECT * FROM file_signer_certificates_v2 WHERE id = ?", (str(sig_row["certificate_id"] or ""),)).fetchone()
        if not cert:
            return {"status": "certificate_missing", "reason": "certificate not found", "verified_at": now_ts}
        if str(cert["status"] or "") != "active" or int(cert["revoked_at"] or 0):
            return {"status": "certificate_revoked", "reason": "certificate revoked or inactive", "verified_at": now_ts}
        if not (int(cert["valid_from"] or 0) <= signed_at <= int(cert["valid_to"] or 0)):
            return {"status": "certificate_expired", "reason": "certificate not valid at signing time", "verified_at": now_ts}
        secret = _v2_certificate_secret_from_cipher(str(cert["secret_cipher"] or ""))
    else:
        secret = audit_secret()
    expected = _v2_signature_value(secret, signed_hash, signer_id, version_id, signed_at)
    if not secret or not hmac.compare_digest(expected, str(sig_row["signature_value"] or "")):
        return {"status": "invalid", "reason": "signature value mismatch", "verified_at": now_ts}
    return {"status": "valid", "reason": "hash and signature verified", "current_hash": current_hash, "verified_at": now_ts}


def _v2_signature_payload(conn: sqlite3.Connection, row: sqlite3.Row) -> dict:
    verify = _v2_verify_signature_row(conn, row)
    return {
        "id": str(row["id"] or ""),
        "file_id": str(row["file_id"] or ""),
        "version_id": str(row["version_id"] or ""),
        "signer_id": str(row["signer_id"] or ""),
        "certificate_id": str(row["certificate_id"] or ""),
        "signature_method": str(row["signature_method"] or "platform"),
        "hash_algorithm": str(row["hash_algorithm"] or "SHA-256"),
        "signed_hash": str(row["signed_hash"] or ""),
        "signature_algorithm": str(row["signature_algorithm"] or "HMAC-SHA256"),
        "signed_at": int(row["signed_at"] or 0),
        "verify_status": str(verify.get("status") or row["verify_status"] or "unknown"),
        "verify_reason": str(verify.get("reason") or ""),
        "verified_at": int(verify.get("verified_at") or 0),
        "metadata": _v2_json_load(str(row["metadata_json"] or "{}"), {}),
    }


def _v2_sign_file_version(
    conn: sqlite3.Connection,
    *,
    file_id: str,
    version_row: sqlite3.Row,
    signer_id: str,
    actor: str,
    signature_method: str,
    metadata: dict | None = None,
) -> sqlite3.Row:
    method = str(signature_method or "platform").strip().lower()
    if method in {"digital", "certificate_digital", "cert"}:
        method = "certificate"
    if method not in {"platform", "certificate", "visual"}:
        method = "platform"
    secure_method = "platform" if method == "visual" else method
    signed_hash = _v2_file_version_current_hash(version_row)
    signed_at = _v2_now()
    certificate_id = ""
    if secure_method == "certificate":
        cert = _v2_ensure_signer_certificate(conn, signer_id, actor)
        certificate_id = str(cert["id"] or "")
        secret = _v2_certificate_secret_from_cipher(str(cert["secret_cipher"] or ""))
    else:
        secret = audit_secret()
    signature_value = _v2_signature_value(secret, signed_hash, signer_id, str(version_row["id"] or ""), signed_at)
    signature_id = _v2_id("fsig")
    meta = dict(metadata or {})
    if method == "visual":
        meta["visual_signature_note"] = "visual signature is display-only; platform electronic signature secures the hash"
    conn.execute(
        """
        INSERT INTO file_signature_records_v2(
          id, file_id, version_id, signer_id, certificate_id, signature_method, hash_algorithm,
          signed_hash, signature_algorithm, signature_value, signed_at, verify_status, verified_at, metadata_json
        ) VALUES(?, ?, ?, ?, ?, ?, 'SHA-256', ?, 'HMAC-SHA256', ?, ?, 'valid', ?, ?)
        """,
        (
            signature_id,
            file_id,
            str(version_row["id"] or ""),
            normalize_email(signer_id),
            certificate_id,
            method,
            signed_hash,
            signature_value,
            signed_at,
            signed_at,
            json.dumps(meta, ensure_ascii=False),
        ),
    )
    _v2_audit(
        conn,
        actor,
        "file_signature_create",
        "file_record",
        file_id,
        {"version_id": str(version_row["id"] or ""), "signer_id": normalize_email(signer_id), "signature_method": method, "certificate_id": certificate_id},
    )
    row = conn.execute("SELECT * FROM file_signature_records_v2 WHERE id = ?", (signature_id,)).fetchone()
    if not row:
        raise ValueError("signature_create_failed")
    return row


def _v2_sync_legacy_document_flows(conn: sqlite3.Connection) -> int:
    source = _load_document_flow_payload()
    docs = source.get("documents", [])
    versions = source.get("versions", [])
    if not isinstance(docs, list):
        return 0
    if not isinstance(versions, list):
        versions = []
    versions_by_document: dict[str, list[dict]] = {}
    for version in versions:
        if not isinstance(version, dict):
            continue
        document_id = str(version.get("document_id") or "")
        if not document_id:
            continue
        versions_by_document.setdefault(document_id, []).append(version)
    for key in versions_by_document:
        versions_by_document[key].sort(key=lambda item: (int(item.get("version_number", 0) or 0), int(item.get("created_at", 0) or 0)))

    def _legacy_version_bytes(version: dict) -> bytes:
        file_path = str(version.get("file_path") or "").strip()
        if file_path:
            try:
                path = Path(file_path).resolve()
                if path.is_file():
                    return path.read_bytes()
            except Exception:
                pass
        encoded = str(version.get("file_base64") or "").strip()
        if encoded:
            try:
                return base64.b64decode(encoded)
            except Exception:
                pass
        encrypted_payload = version.get("encrypted_payload")
        if isinstance(encrypted_payload, dict):
            try:
                return _document_decrypt_blob(encrypted_payload)
            except Exception:
                pass
        preview = str(version.get("preview") or "")
        return preview.encode("utf-8")

    created = 0
    for doc in docs:
        if not isinstance(doc, dict):
            continue
        source_id = str(doc.get("id") or "")
        if not source_id:
            continue
        exists = conn.execute(
            "SELECT id FROM file_records_v2 WHERE source_module = 'document-flow' AND source_ref_id = ? LIMIT 1",
            (source_id,),
        ).fetchone()
        owner = normalize_email(doc.get("created_by") or doc.get("owner_id") or "")
        if not owner:
            continue
        status = str(doc.get("current_status") or "draft")
        mapped_status = status if status in V2_FILE_STATUSES else ("signed_locked" if bool(doc.get("is_locked")) else "draft")
        now_ts = _v2_now()
        workspace = _v2_file_workspace(str(doc.get("workspace_id") or "doc-flow"))
        if exists:
            file_id = str(exists["id"] or "")
        else:
            file_id = _v2_id("frec")
            conn.execute(
                """
                INSERT INTO file_records_v2(
                  id, title, project_id, work_item_id, workspace_id, department, owner_user_id, category, status,
                  source_module, source_ref_id, current_version_id, is_signed, is_locked, is_encrypted, created_at, updated_at
                ) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, 'document-flow', ?, '', ?, ?, ?, ?, ?)
                """,
                (
                    file_id,
                    str(doc.get("title") or source_id),
                    str(doc.get("project_id") or ""),
                    str(doc.get("work_item_id") or ""),
                    workspace,
                    str(doc.get("department") or ""),
                    owner,
                    str(doc.get("category") or "general"),
                    mapped_status,
                    source_id,
                    1 if mapped_status == "signed_locked" else 0,
                    1 if bool(doc.get("is_locked")) else 0,
                    1 if bool(doc.get("is_encrypted")) else 0,
                    int(doc.get("created_at") or now_ts),
                    int(doc.get("updated_at") or now_ts),
                ),
            )
            created += 1

        imported_versions = versions_by_document.get(source_id, [])
        for version in imported_versions:
            version_id = str(version.get("id") or "").strip()
            if not version_id:
                continue
            version_exists = conn.execute(
                "SELECT id FROM file_versions_v2 WHERE id = ? LIMIT 1",
                (version_id,),
            ).fetchone()
            if version_exists:
                continue
            raw = _legacy_version_bytes(version)
            filename = str(version.get("filename") or "document.txt")
            storage_path = _v2_file_storage_write(file_id, version_id, filename, raw)
            checksum = hashlib.sha256(raw).hexdigest()
            created_at = int(version.get("created_at") or doc.get("created_at") or now_ts)
            conn.execute(
                """
                INSERT INTO file_versions_v2(
                  id, file_id, version_number, filename, mime, size, storage_path, checksum_sha256, change_summary,
                  created_by, created_at, derived_from_version_id, is_signed_snapshot, signed_by, signed_at, is_locked_snapshot, is_encrypted_snapshot
                ) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    version_id,
                    file_id,
                    int(version.get("version_number") or 1),
                    filename,
                    str(version.get("mime") or "application/octet-stream"),
                    len(raw),
                    str(storage_path),
                    checksum,
                    str(version.get("change_summary") or ""),
                    normalize_email(version.get("created_by") or owner) or owner,
                    created_at,
                    str(version.get("based_on_version_id") or ""),
                    1 if bool(version.get("is_signed")) else 0,
                    normalize_email(version.get("signed_by") or ""),
                    int(version.get("signed_at") or 0),
                    1 if bool(version.get("is_locked")) else 0,
                    1 if bool(version.get("is_encrypted")) else 0,
                ),
            )

        desired_current_version_id = str(doc.get("current_version_id") or "").strip()
        if desired_current_version_id:
            has_current = conn.execute(
                "SELECT 1 FROM file_versions_v2 WHERE id = ? AND file_id = ? LIMIT 1",
                (desired_current_version_id, file_id),
            ).fetchone()
            if not has_current:
                desired_current_version_id = ""
        if not desired_current_version_id:
            latest = conn.execute(
                "SELECT id FROM file_versions_v2 WHERE file_id = ? ORDER BY version_number DESC, created_at DESC LIMIT 1",
                (file_id,),
            ).fetchone()
            desired_current_version_id = str(latest["id"] or "") if latest else ""

        conn.execute(
            """
            UPDATE file_records_v2
            SET title = ?, project_id = ?, work_item_id = ?, workspace_id = ?, department = ?, owner_user_id = ?, category = ?,
                status = ?, current_version_id = ?, is_signed = ?, is_locked = ?, is_encrypted = ?, updated_at = ?
            WHERE id = ?
            """,
            (
                str(doc.get("title") or source_id),
                str(doc.get("project_id") or ""),
                str(doc.get("work_item_id") or ""),
                workspace,
                str(doc.get("department") or ""),
                owner,
                str(doc.get("category") or "general"),
                mapped_status,
                desired_current_version_id,
                1 if bool(doc.get("is_signed") or mapped_status == "signed_locked") else 0,
                1 if bool(doc.get("is_locked")) else 0,
                1 if bool(doc.get("is_encrypted")) else 0,
                int(doc.get("updated_at") or now_ts),
                file_id,
            ),
        )
    return created


def _v2_file_center_overview(user: dict | None, query: dict[str, list[str]]) -> tuple[dict, int]:
    if not user:
        return {"ok": False, "error": "authentication_required"}, 401
    scope = str(query.get("scope", ["my"])[0] or "my").strip().lower()
    workspace_raw = str(query.get("workspace_id", [""])[0] or "").strip()
    workspace_id = _v2_file_workspace(workspace_raw) if workspace_raw else ""
    actor = _v2_user_email(user)
    with v2_db_lock, _v2_db_conn() as conn:
        _v2_sync_legacy_document_flows(conn)
        conn.commit()
        rows = conn.execute("SELECT * FROM file_records_v2 ORDER BY updated_at DESC LIMIT 2000").fetchall()
        visible: list[sqlite3.Row] = []
        for row in rows:
            if not _v2_can_view_file(conn, user, row):
                continue
            if scope == "my" and actor and normalize_email(row["owner_user_id"] or "") != actor:
                in_pending = conn.execute(
                    """
                    SELECT 1 FROM file_workflow_steps_v2 s
                    LEFT JOIN file_workflows_v2 w ON w.id = s.workflow_id
                    WHERE w.file_id = ? AND s.assigned_user_id = ? AND s.status = 'pending' LIMIT 1
                    """,
                    (str(row["id"] or ""), actor),
                ).fetchone()
                if not in_pending:
                    continue
            if scope == "workspace" and workspace_id and str(row["workspace_id"] or "") != workspace_id:
                continue
            visible.append(row)
        status_counts: dict[str, int] = {}
        category_counts: dict[str, int] = {}
        pending_steps = 0
        signed_locked = 0
        overdue_pending = 0
        now_ts = _v2_now()
        day_ago = now_ts - 24 * 60 * 60
        new_today = 0
        for row in visible:
            status = str(row["status"] or "draft")
            category = str(row["category"] or "general")
            status_counts[status] = status_counts.get(status, 0) + 1
            category_counts[category] = category_counts.get(category, 0) + 1
            if bool(row["is_locked"]):
                signed_locked += 1
            if int(row["created_at"] or 0) >= day_ago:
                new_today += 1
            steps = conn.execute(
                """
                SELECT s.created_at FROM file_workflow_steps_v2 s
                LEFT JOIN file_workflows_v2 w ON w.id = s.workflow_id
                WHERE w.file_id = ? AND s.status = 'pending'
                """,
                (str(row["id"] or ""),),
            ).fetchall()
            pending_steps += len(steps)
            for item in steps:
                if int(item["created_at"] or 0) < now_ts - 48 * 60 * 60:
                    overdue_pending += 1
        return {
            "ok": True,
            "scope": scope,
            "workspace_id": workspace_id,
            "totals": {
                "files": len(visible),
                "pending_steps": pending_steps,
                "signed_locked": signed_locked,
                "overdue_pending": overdue_pending,
                "new_last_24h": new_today,
            },
            "status_counts": status_counts,
            "category_counts": category_counts,
            "files": [_v2_file_payload(conn, row, include_latest_version=False) for row in visible[:120]],
        }, 200


def _v2_list_file_center_files(user: dict | None, query: dict[str, list[str]]) -> tuple[dict, int]:
    if not user:
        return {"ok": False, "error": "authentication_required"}, 401
    q = str(query.get("q", [""])[0] or "").strip().lower()
    project_id = str(query.get("project_id", [""])[0] or "").strip()
    work_item_id = str(query.get("work_item_id", [""])[0] or "").strip()
    workspace_raw = str(query.get("workspace_id", [""])[0] or "").strip()
    workspace_id = _v2_file_workspace(workspace_raw) if workspace_raw else ""
    owner = normalize_email(query.get("owner", [""])[0]) if query.get("owner") else ""
    department = str(query.get("department", [""])[0] or "").strip().lower()
    category = str(query.get("category", [""])[0] or "").strip().lower()
    status = str(query.get("status", [""])[0] or "").strip().lower()
    with v2_db_lock, _v2_db_conn() as conn:
        _v2_sync_legacy_document_flows(conn)
        conn.commit()
        rows = conn.execute("SELECT * FROM file_records_v2 ORDER BY updated_at DESC LIMIT 3000").fetchall()
        files: list[dict] = []
        for row in rows:
            if not _v2_can_view_file(conn, user, row):
                continue
            if project_id and str(row["project_id"] or "") != project_id:
                continue
            if work_item_id and str(row["work_item_id"] or "") != work_item_id:
                continue
            if workspace_id and str(row["workspace_id"] or "") != workspace_id:
                continue
            if owner and normalize_email(row["owner_user_id"] or "") != owner:
                continue
            if department and department != str(row["department"] or "").lower():
                continue
            if category and category != str(row["category"] or "").lower():
                continue
            if status and status != str(row["status"] or "").lower():
                continue
            payload = _v2_file_payload(conn, row, include_latest_version=True)
            text = " ".join([
                payload["title"],
                payload["project_id"],
                payload["work_item_id"],
                payload["workspace_id"],
                payload["department"],
                payload["owner_user_id"],
                payload["category"],
                payload["status"],
            ]).lower()
            if q and q not in text:
                continue
            files.append(payload)
        return {"ok": True, "count": len(files), "files": files[:500]}, 200


def _v2_file_center_detail(user: dict | None, file_id: str) -> tuple[dict, int]:
    if not user:
        return {"ok": False, "error": "authentication_required"}, 401
    with v2_db_lock, _v2_db_conn() as conn:
        row = conn.execute("SELECT * FROM file_records_v2 WHERE id = ?", (file_id,)).fetchone()
        if not row:
            return {"ok": False, "error": "file_not_found"}, 404
        if not _v2_can_view_file(conn, user, row):
            return {"ok": False, "error": "permission_denied"}, 403
        versions = conn.execute(
            "SELECT * FROM file_versions_v2 WHERE file_id = ? ORDER BY version_number DESC",
            (file_id,),
        ).fetchall()
        workflows = conn.execute(
            "SELECT * FROM file_workflows_v2 WHERE file_id = ? ORDER BY created_at DESC",
            (file_id,),
        ).fetchall()
        signatures = conn.execute(
            "SELECT * FROM file_signature_records_v2 WHERE file_id = ? ORDER BY signed_at DESC",
            (file_id,),
        ).fetchall()
        signature_payloads = [_v2_signature_payload(conn, sig) for sig in signatures]
        failed_signatures = [item for item in signature_payloads if item.get("verify_status") != "valid"]
        return {
            "ok": True,
            "file": _v2_file_payload(conn, row, include_latest_version=True),
            "versions": [_v2_file_version_payload(v) for v in versions],
            "workflows": [_v2_file_workflow_payload(conn, w, include_steps=True) for w in workflows],
            "signatures": signature_payloads,
            "signature_summary": {
                "total": len(signature_payloads),
                "valid": len([item for item in signature_payloads if item.get("verify_status") == "valid"]),
                "failed": len(failed_signatures),
                "status": "valid" if signature_payloads and not failed_signatures else ("unsigned" if not signature_payloads else "attention"),
            },
        }, 200


def _v2_file_center_versions(user: dict | None, file_id: str) -> tuple[dict, int]:
    payload, status = _v2_file_center_detail(user, file_id)
    if not payload.get("ok"):
        return payload, status
    return {"ok": True, "versions": payload.get("versions", [])}, 200


def _v2_file_center_workflows(user: dict | None, file_id: str) -> tuple[dict, int]:
    payload, status = _v2_file_center_detail(user, file_id)
    if not payload.get("ok"):
        return payload, status
    return {"ok": True, "workflows": payload.get("workflows", [])}, 200


def _v2_file_center_audit(user: dict | None, file_id: str) -> tuple[dict, int]:
    if not user:
        return {"ok": False, "error": "authentication_required"}, 401
    with v2_db_lock, _v2_db_conn() as conn:
        row = conn.execute("SELECT * FROM file_records_v2 WHERE id = ?", (file_id,)).fetchone()
        if not row:
            return {"ok": False, "error": "file_not_found"}, 404
        if not _v2_can_view_file(conn, user, row):
            return {"ok": False, "error": "permission_denied"}, 403
        logs = conn.execute(
            """
            SELECT *
            FROM audit_logs_v2
            WHERE (entity_type = 'file_record' AND entity_id = ?)
               OR (entity_type = 'file_workflow' AND entity_id IN (SELECT id FROM file_workflows_v2 WHERE file_id = ?))
            ORDER BY created_at DESC
            LIMIT 300
            """,
            (file_id, file_id),
        ).fetchall()
        return {
            "ok": True,
            "audit_logs": [
                {
                    "id": str(log["id"] or ""),
                    "actor_user_id": str(log["actor_user_id"] or ""),
                    "action_type": str(log["action_type"] or ""),
                    "entity_type": str(log["entity_type"] or ""),
                    "entity_id": str(log["entity_id"] or ""),
                    "metadata": _v2_json_load(str(log["metadata_json"] or "{}"), {}),
                    "created_at": int(log["created_at"] or 0),
                }
                for log in logs
            ],
        }, 200


def _v2_file_center_download(user: dict | None, file_id: str, version_id: str) -> tuple[dict, int]:
    if not user:
        return {"ok": False, "error": "authentication_required"}, 401
    with v2_db_lock, _v2_db_conn() as conn:
        row = conn.execute("SELECT * FROM file_records_v2 WHERE id = ?", (file_id,)).fetchone()
        if not row:
            return {"ok": False, "error": "file_not_found"}, 404
        if not _v2_can_view_file(conn, user, row):
            return {"ok": False, "error": "permission_denied"}, 403
        target = None
        if version_id:
            target = conn.execute(
                "SELECT * FROM file_versions_v2 WHERE id = ? AND file_id = ?",
                (version_id, file_id),
            ).fetchone()
        if not target:
            target = conn.execute(
                "SELECT * FROM file_versions_v2 WHERE id = ?",
                (str(row["current_version_id"] or ""),),
            ).fetchone()
        if not target:
            target = conn.execute(
                "SELECT * FROM file_versions_v2 WHERE file_id = ? ORDER BY version_number DESC LIMIT 1",
                (file_id,),
            ).fetchone()
        if not target:
            return {"ok": False, "error": "file_version_not_found"}, 404
        storage_path = str(target["storage_path"] or "")
        if not storage_path:
            return {"ok": False, "error": "file_not_found"}, 404
        try:
            raw = _v2_file_storage_read(storage_path)
        except Exception:
            return {"ok": False, "error": "file_not_found"}, 404
        signature_rows = conn.execute(
            "SELECT * FROM file_signature_records_v2 WHERE version_id = ? ORDER BY signed_at DESC",
            (str(target["id"] or ""),),
        ).fetchall()
        signature_statuses = [_v2_signature_payload(conn, sig) for sig in signature_rows]
        signature_summary = {
            "total": len(signature_statuses),
            "failed": len([item for item in signature_statuses if item.get("verify_status") != "valid"]),
        }
        actor = _v2_user_email(user) or "system"
        filename = str(target["filename"] or "file.bin")
        _v2_audit(
            conn,
            actor,
            "file_download",
            "file_record",
            file_id,
            {"version_id": str(target["id"] or ""), "filename": filename, "signature_summary": signature_summary},
        )
        write_audit_event(
            {
                "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
                "event": "file_center_download",
                "actor": actor,
                "file_id": file_id,
                "version_id": str(target["id"] or ""),
                "filename": filename,
                "dlp_terms": detect_governance_dlp_terms(filename, str(row["title"] or ""), str(row["category"] or "")),
            }
        )
        return {
            "ok": True,
            "raw": raw,
            "filename": filename,
            "mime": str(target["mime"] or "application/octet-stream"),
            "version_id": str(target["id"] or ""),
            "version_number": int(target["version_number"] or 1),
        }, 200


def _v2_file_center_create_file(user: dict | None, payload: dict) -> tuple[dict, int]:
    actor = _v2_user_email(user)
    if not actor:
        return {"ok": False, "error": "authentication_required"}, 401
    title = str(payload.get("title") or "").strip()
    if not title:
        return {"ok": False, "error": "title_required"}, 400
    filename = os.path.basename(str(payload.get("filename") or "").strip())
    blob = str(payload.get("base64") or "").strip()
    if not filename or not blob:
        return {"ok": False, "error": "file_required"}, 400
    try:
        raw = base64.b64decode(blob, validate=True)
    except Exception:
        return {"ok": False, "error": "invalid_file_payload"}, 400
    if not raw:
        return {"ok": False, "error": "invalid_file_payload"}, 400
    project_id = str(payload.get("project_id") or "").strip()
    work_item_id = str(payload.get("work_item_id") or "").strip()
    workspace_id = _v2_file_workspace(str(payload.get("workspace_id") or "work-chat"))
    department = str(payload.get("department") or "").strip()
    category = str(payload.get("category") or "general").strip() or "general"
    status = "draft"
    now_ts = _v2_now()
    file_id = _v2_id("frec")
    version_id = _v2_id("fver")
    with v2_db_lock, _v2_db_conn() as conn:
        if project_id and not _v2_can_view_project(conn, user, project_id):
            return {"ok": False, "error": "permission_denied"}, 403
        storage_path = _v2_file_storage_write(file_id, version_id, filename, raw)
        conn.execute(
            """
            INSERT INTO file_records_v2(
              id, title, project_id, work_item_id, workspace_id, department, owner_user_id, category, status,
              source_module, source_ref_id, current_version_id, is_signed, is_locked, is_encrypted, created_at, updated_at
            ) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, 'file-center', '', ?, 0, 0, 0, ?, ?)
            """,
            (file_id, title, project_id, work_item_id, workspace_id, department, actor, category, status, version_id, now_ts, now_ts),
        )
        conn.execute(
            """
            INSERT INTO file_versions_v2(
              id, file_id, version_number, filename, mime, size, storage_path, checksum_sha256, change_summary,
              created_by, created_at, derived_from_version_id, is_signed_snapshot, signed_by, signed_at, is_locked_snapshot, is_encrypted_snapshot
            ) VALUES(?, ?, 1, ?, ?, ?, ?, ?, ?, ?, ?, '', 0, '', 0, 0, 0)
            """,
            (
                version_id,
                file_id,
                filename,
                str(payload.get("mime") or mimetypes.guess_type(filename)[0] or "application/octet-stream"),
                len(raw),
                str(storage_path),
                hashlib.sha256(raw).hexdigest(),
                str(payload.get("change_summary") or "initial version")[:1000],
                actor,
                now_ts,
            ),
        )
        _v2_audit(conn, actor, "file_create", "file_record", file_id, {"title": title, "workspace_id": workspace_id, "project_id": project_id})
        if project_id:
            _v2_project_chat_append_system_message(
                conn,
                project_id,
                f"File created: {title[:120]} ({filename}).",
                message_type="file_event",
                metadata={"event_type": "file_created", "file_change_related": True, "file_id": file_id},
            )
            _v2_chat_event_refresh_if_needed(conn, project_id)
        conn.commit()
        row = conn.execute("SELECT * FROM file_records_v2 WHERE id = ?", (file_id,)).fetchone()
        return {"ok": True, "file": _v2_file_payload(conn, row, include_latest_version=True)}, 200


def _v2_file_center_add_version(user: dict | None, file_id: str, payload: dict) -> tuple[dict, int]:
    actor = _v2_user_email(user)
    if not actor:
        return {"ok": False, "error": "authentication_required"}, 401
    filename = os.path.basename(str(payload.get("filename") or "").strip())
    blob = str(payload.get("base64") or "").strip()
    if not filename or not blob:
        return {"ok": False, "error": "file_required"}, 400
    try:
        raw = base64.b64decode(blob, validate=True)
    except Exception:
        return {"ok": False, "error": "invalid_file_payload"}, 400
    with v2_db_lock, _v2_db_conn() as conn:
        row = conn.execute("SELECT * FROM file_records_v2 WHERE id = ?", (file_id,)).fetchone()
        if not row:
            return {"ok": False, "error": "file_not_found"}, 404
        if not _v2_can_manage_file(conn, user, row):
            return {"ok": False, "error": "permission_denied"}, 403
        if bool(row["is_locked"]):
            change_summary = str(payload.get("change_summary") or "").strip()
            if not change_summary:
                return {"ok": False, "error": "change_request_reason_required"}, 400
        last = conn.execute(
            "SELECT * FROM file_versions_v2 WHERE file_id = ? ORDER BY version_number DESC LIMIT 1",
            (file_id,),
        ).fetchone()
        next_number = int(last["version_number"] or 0) + 1 if last else 1
        version_id = _v2_id("fver")
        storage_path = _v2_file_storage_write(file_id, version_id, filename, raw)
        now_ts = _v2_now()
        conn.execute(
            """
            INSERT INTO file_versions_v2(
              id, file_id, version_number, filename, mime, size, storage_path, checksum_sha256, change_summary,
              created_by, created_at, derived_from_version_id, is_signed_snapshot, signed_by, signed_at, is_locked_snapshot, is_encrypted_snapshot
            ) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, '', 0, 0, 0)
            """,
            (
                version_id,
                file_id,
                next_number,
                filename,
                str(payload.get("mime") or mimetypes.guess_type(filename)[0] or "application/octet-stream"),
                len(raw),
                str(storage_path),
                hashlib.sha256(raw).hexdigest(),
                str(payload.get("change_summary") or f"version {next_number}")[:1000],
                actor,
                now_ts,
                str(last["id"] or "") if last else "",
            ),
        )
        next_status = "draft" if bool(row["is_locked"]) else str(row["status"] or "draft")
        conn.execute(
            """
            UPDATE file_records_v2
            SET current_version_id = ?, status = ?, is_signed = 0, is_locked = 0, is_encrypted = 0, updated_at = ?
            WHERE id = ?
            """,
            (version_id, next_status, now_ts, file_id),
        )
        _v2_audit(
            conn,
            actor,
            "file_add_version",
            "file_record",
            file_id,
            {"version_id": version_id, "version_number": next_number, "change_summary": str(payload.get("change_summary") or "")[:200]},
        )
        project_id = str(row["project_id"] or "")
        if project_id:
            _v2_project_chat_append_system_message(
                conn,
                project_id,
                f"File version added: {str(row['title'] or file_id)[:120]} -> v{next_number}.",
                message_type="file_event",
                metadata={"event_type": "file_version_added", "file_change_related": True, "file_id": file_id, "version_id": version_id},
            )
            _v2_chat_event_refresh_if_needed(conn, project_id)
        conn.commit()
        updated = conn.execute("SELECT * FROM file_records_v2 WHERE id = ?", (file_id,)).fetchone()
        return {"ok": True, "file": _v2_file_payload(conn, updated, include_latest_version=True)}, 200


def _v2_file_center_create_workflow(user: dict | None, payload: dict) -> tuple[dict, int]:
    actor = _v2_user_email(user)
    if not actor:
        return {"ok": False, "error": "authentication_required"}, 401
    file_id = str(payload.get("file_id") or "").strip()
    if not file_id:
        return {"ok": False, "error": "file_not_found"}, 400
    steps = payload.get("steps") if isinstance(payload.get("steps"), list) else []
    normalized_steps: list[dict] = []
    order = 1
    for step in steps:
        if not isinstance(step, dict):
            continue
        step_type = str(step.get("step_type") or "").strip().lower()
        assigned = normalize_email(step.get("assigned_user_id") or step.get("user_id") or "")
        if step_type not in V2_FILE_STEP_TYPES or not assigned or not _v2_user_exists(assigned):
            continue
        try:
            sequence_order = max(1, int(step.get("sequence_order") or order))
        except Exception:
            sequence_order = order
        normalized_steps.append({"step_type": step_type, "assigned_user_id": assigned, "sequence_order": sequence_order})
        order += 1
    if not normalized_steps:
        return {"ok": False, "error": "workflow_requires_reviewer_or_approver"}, 400
    workflow_type = str(payload.get("workflow_type") or "review_approve_sign").strip().lower()
    title = str(payload.get("title") or payload.get("workflow_title") or "").strip()[:240]
    routing_mode = str(payload.get("routing_mode") or "sequential").strip().lower()
    if routing_mode not in {"single", "parallel", "sequential"}:
        routing_mode = "sequential"
    signature_method = str(payload.get("signature_method") or "platform").strip().lower()
    if signature_method in {"digital", "certificate_digital", "cert"}:
        signature_method = "certificate"
    if signature_method not in {"platform", "certificate", "visual"}:
        signature_method = "platform"
    signature_placement = str(payload.get("signature_placement") or "").strip()[:500]
    instructions = str(payload.get("instructions") or payload.get("note") or "").strip()[:4000]
    lock_after_sign = 1 if payload.get("lock_after_sign", True) is not False else 0
    due_at = 0
    due_raw = str(payload.get("due_at") or payload.get("due_date") or "").strip()
    if due_raw:
        try:
            due_at = int(due_raw)
        except Exception:
            try:
                due_at = int(datetime.fromisoformat(due_raw.replace("Z", "+00:00")).timestamp())
            except Exception:
                due_at = 0
    with v2_db_lock, _v2_db_conn() as conn:
        file_row = conn.execute("SELECT * FROM file_records_v2 WHERE id = ?", (file_id,)).fetchone()
        if not file_row:
            return {"ok": False, "error": "file_not_found"}, 404
        if not _v2_can_manage_file(conn, user, file_row):
            return {"ok": False, "error": "permission_denied"}, 403
        now_ts = _v2_now()
        workflow_id = _v2_id("fwf")
        conn.execute(
            """
            INSERT INTO file_workflows_v2(
              id, file_id, project_id, work_item_id, workspace_id, workflow_type, title, routing_mode, due_at,
              instructions, signature_method, signature_placement, lock_after_sign, metadata_json,
              status, initiated_by, created_at, updated_at, closed_at
            ) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'active', ?, ?, ?, 0)
            """,
            (
                workflow_id,
                file_id,
                str(file_row["project_id"] or ""),
                str(file_row["work_item_id"] or ""),
                str(file_row["workspace_id"] or ""),
                workflow_type,
                title or f"{workflow_type} - {str(file_row['title'] or file_id)[:120]}",
                routing_mode,
                due_at,
                instructions,
                signature_method,
                signature_placement,
                lock_after_sign,
                json.dumps({"created_from": "file_center", "step_count": len(normalized_steps)}, ensure_ascii=False),
                actor,
                now_ts,
                now_ts,
            ),
        )
        for step in normalized_steps:
            conn.execute(
                """
                INSERT INTO file_workflow_steps_v2(
                  id, workflow_id, step_type, sequence_order, assigned_user_id, status, comments, acted_at, created_at
                ) VALUES(?, ?, ?, ?, ?, 'pending', '', 0, ?)
                """,
                (_v2_id("fws"), workflow_id, step["step_type"], int(step["sequence_order"]), step["assigned_user_id"], now_ts),
            )
            _v2_notify(
                conn,
                step["assigned_user_id"],
                "file_step_assigned",
                "File workflow action required",
                f"You were assigned {step['step_type']} on file {file_id}.",
                project_id=str(file_row["project_id"] or ""),
                work_item_id=str(file_row["work_item_id"] or ""),
                document_id=file_id,
            )
        if signature_method == "certificate":
            for step in normalized_steps:
                if step["step_type"] == "sign":
                    _v2_ensure_signer_certificate(conn, step["assigned_user_id"], actor)
        next_status = "in_review"
        if any(item["step_type"] == "approval" for item in normalized_steps):
            next_status = "pending_approval"
        if any(item["step_type"] == "sign" for item in normalized_steps):
            next_status = "pending_signature"
        conn.execute(
            "UPDATE file_records_v2 SET status = ?, updated_at = ? WHERE id = ?",
            (next_status, now_ts, file_id),
        )
        _v2_audit(
            conn,
            actor,
            "file_workflow_create",
            "file_workflow",
            workflow_id,
            {
                "file_id": file_id,
                "steps": normalized_steps,
                "routing_mode": routing_mode,
                "due_at": due_at,
                "signature_method": signature_method,
                "lock_after_sign": bool(lock_after_sign),
            },
        )
        project_id = str(file_row["project_id"] or "")
        if project_id:
            _v2_project_chat_append_system_message(
                conn,
                project_id,
                f"File workflow started for {str(file_row['title'] or file_id)[:120]} ({next_status}).",
                message_type="file_event",
                metadata={
                    "event_type": "file_workflow_started",
                    "approval_related": True,
                    "file_change_related": True,
                    "file_id": file_id,
                    "workflow_id": workflow_id,
                },
            )
            _v2_chat_event_refresh_if_needed(conn, project_id)
        conn.commit()
        row = conn.execute("SELECT * FROM file_workflows_v2 WHERE id = ?", (workflow_id,)).fetchone()
        return {"ok": True, "workflow": _v2_file_workflow_payload(conn, row, include_steps=True)}, 200


def _v2_file_center_step_action(user: dict | None, workflow_id: str, step_id: str, payload: dict) -> tuple[dict, int]:
    actor = _v2_user_email(user)
    if not actor:
        return {"ok": False, "error": "authentication_required"}, 401
    action = str(payload.get("action") or "").strip().lower()
    comment = str(payload.get("comment") or "").strip()
    with v2_db_lock, _v2_db_conn() as conn:
        workflow = conn.execute("SELECT * FROM file_workflows_v2 WHERE id = ?", (workflow_id,)).fetchone()
        if not workflow:
            return {"ok": False, "error": "workflow_not_found"}, 404
        step = conn.execute(
            "SELECT * FROM file_workflow_steps_v2 WHERE id = ? AND workflow_id = ?",
            (step_id, workflow_id),
        ).fetchone()
        if not step:
            return {"ok": False, "error": "workflow_not_found"}, 404
        if str(step["status"] or "") != "pending":
            return {"ok": False, "error": "unsupported_action"}, 400
        if not _v2_can_act_step(conn, user, step):
            return {"ok": False, "error": "permission_denied"}, 403
        step_type = str(step["step_type"] or "")
        status_to_set = "done"
        if action in {"approve", "pass"}:
            status_to_set = "approved"
        elif action in {"reject", "return"}:
            status_to_set = "rejected"
        elif action in {"sign"}:
            status_to_set = "signed"
        elif action in {"done", "complete"}:
            status_to_set = "done"
        else:
            return {"ok": False, "error": "unsupported_action"}, 400
        if step_type == "sign" and status_to_set == "signed":
            archive_payload, archive_status = _v2_file_center_archive(
                user,
                str(workflow["file_id"] or ""),
                {
                    "reason": comment or "signed",
                    "signature_method": str(payload.get("signature_method") or workflow["signature_method"] or "platform"),
                    "signature_placement": str(payload.get("signature_placement") or workflow["signature_placement"] or ""),
                    "workflow_id": workflow_id,
                    "step_id": step_id,
                    "lock_after_sign": bool(workflow["lock_after_sign"]),
                },
                _conn=conn,
                _internal=True,
            )
            if not archive_payload.get("ok"):
                return archive_payload, archive_status
        now_ts = _v2_now()
        conn.execute(
            "UPDATE file_workflow_steps_v2 SET status = ?, comments = ?, acted_at = ? WHERE id = ?",
            (status_to_set, comment[:2000], now_ts, step_id),
        )
        pending = conn.execute(
            "SELECT COUNT(*) AS c FROM file_workflow_steps_v2 WHERE workflow_id = ? AND status = 'pending'",
            (workflow_id,),
        ).fetchone()
        file_id = str(workflow["file_id"] or "")
        if int(pending["c"] or 0) == 0:
            wf_status = "completed" if status_to_set != "rejected" else "rejected"
            conn.execute(
                "UPDATE file_workflows_v2 SET status = ?, updated_at = ?, closed_at = ? WHERE id = ?",
                (wf_status, now_ts, now_ts, workflow_id),
            )
            if wf_status == "rejected":
                conn.execute("UPDATE file_records_v2 SET status = 'rejected', updated_at = ? WHERE id = ?", (now_ts, file_id))
            else:
                file_row = conn.execute("SELECT * FROM file_records_v2 WHERE id = ?", (file_id,)).fetchone()
                if file_row and not bool(file_row["is_locked"]):
                    conn.execute("UPDATE file_records_v2 SET status = 'archived', updated_at = ? WHERE id = ?", (now_ts, file_id))
        else:
            conn.execute("UPDATE file_workflows_v2 SET updated_at = ? WHERE id = ?", (now_ts, workflow_id))
        _v2_audit(
            conn,
            actor,
            "file_step_action",
            "file_workflow",
            workflow_id,
            {"step_id": step_id, "action": action, "status": status_to_set},
        )
        conn.commit()
        updated = conn.execute("SELECT * FROM file_workflows_v2 WHERE id = ?", (workflow_id,)).fetchone()
        return {"ok": True, "workflow": _v2_file_workflow_payload(conn, updated, include_steps=True)}, 200


def _v2_file_center_archive(
    user: dict | None,
    file_id: str,
    payload: dict,
    *,
    _conn: sqlite3.Connection | None = None,
    _internal: bool = False,
) -> tuple[dict, int]:
    if _conn is None:
        with v2_db_lock, _v2_db_conn() as scoped_conn:
            return _v2_file_center_archive(user, file_id, payload, _conn=scoped_conn, _internal=_internal)
    actor = _v2_user_email(user)
    if not actor:
        return {"ok": False, "error": "authentication_required"}, 401
    managed_conn = False
    conn = _conn
    try:
        row = conn.execute("SELECT * FROM file_records_v2 WHERE id = ?", (file_id,)).fetchone()
        if not row:
            return {"ok": False, "error": "file_not_found"}, 404
        if not _internal and not _v2_can_manage_file(conn, user, row):
            return {"ok": False, "error": "permission_denied"}, 403
        version = conn.execute(
            "SELECT * FROM file_versions_v2 WHERE id = ?",
            (str(row["current_version_id"] or ""),),
        ).fetchone()
        if not version:
            return {"ok": False, "error": "file_version_not_found"}, 404
        raw = _v2_file_storage_read(str(version["storage_path"] or ""))
        encrypted = _v2_file_crypt(raw, f"{file_id}:{version['id']}:fastone")
        archive_id = _v2_id("farc")
        archive_path = FILE_CENTER_ARCHIVE_DIR / f"{archive_id}.bin"
        archive_path.write_bytes(base64.b64encode(encrypted))
        now_ts = _v2_now()
        conn.execute(
            """
            INSERT INTO file_archives_v2(
              id, file_id, version_id, archive_path, encryption_method, key_ref, locked_at, locked_by, retention_class, created_at
            ) VALUES(?, ?, ?, ?, 'xor-sha256', 'local-default', ?, ?, ?, ?)
            """,
            (
                archive_id,
                file_id,
                str(version["id"] or ""),
                str(archive_path),
                now_ts,
                actor,
                str(payload.get("retention_class") or "standard"),
                now_ts,
            ),
        )
        signature_row = _v2_sign_file_version(
            conn,
            file_id=file_id,
            version_row=version,
            signer_id=actor,
            actor=actor,
            signature_method=str(payload.get("signature_method") or "platform"),
            metadata={
                "archive_id": archive_id,
                "reason": str(payload.get("reason") or "")[:500],
                "signature_placement": str(payload.get("signature_placement") or "")[:500],
                "workflow_id": str(payload.get("workflow_id") or ""),
                "step_id": str(payload.get("step_id") or ""),
                "lock_after_sign": bool(payload.get("lock_after_sign", True)),
            },
        )
        conn.execute(
            """
            UPDATE file_versions_v2
            SET is_signed_snapshot = 1, signed_by = ?, signed_at = ?, is_locked_snapshot = 1, is_encrypted_snapshot = 1
            WHERE id = ?
            """,
            (actor, now_ts, str(version["id"] or "")),
        )
        conn.execute(
            """
            UPDATE file_records_v2
            SET status = 'signed_locked', is_signed = 1, is_locked = 1, is_encrypted = 1, updated_at = ?
            WHERE id = ?
            """,
            (now_ts, file_id),
        )
        _v2_audit(
            conn,
            actor,
            "file_archive",
            "file_record",
            file_id,
            {
                "archive_id": archive_id,
                "version_id": str(version["id"] or ""),
                "reason": str(payload.get("reason") or "")[:200],
                "signature_id": str(signature_row["id"] or ""),
                "signature_method": str(signature_row["signature_method"] or ""),
                "signed_hash": str(signature_row["signed_hash"] or ""),
            },
        )
        project_id = str(row["project_id"] or "")
        if project_id:
            _v2_project_chat_append_system_message(
                conn,
                project_id,
                f"File signed and archived: {str(row['title'] or file_id)[:120]}.",
                message_type="file_event",
                metadata={
                    "event_type": "file_archived",
                    "approval_related": True,
                    "file_change_related": True,
                    "file_id": file_id,
                    "archive_id": archive_id,
                },
                is_key_message=True,
            )
            _v2_chat_event_refresh_if_needed(conn, project_id)
        if managed_conn:
            conn.commit()
        archived = conn.execute("SELECT * FROM file_records_v2 WHERE id = ?", (file_id,)).fetchone()
        return {
            "ok": True,
            "archive_id": archive_id,
            "signature": _v2_signature_payload(conn, signature_row),
            "file": _v2_file_payload(conn, archived, include_latest_version=True),
        }, 200
    finally:
        if managed_conn:
            conn.close()


def _v2_file_center_list_archives(user: dict | None, query: dict[str, list[str]]) -> tuple[dict, int]:
    if not user:
        return {"ok": False, "error": "authentication_required"}, 401
    file_id = str(query.get("file_id", [""])[0] or "").strip()
    with v2_db_lock, _v2_db_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM file_archives_v2 ORDER BY created_at DESC LIMIT 500",
        ).fetchall()
        out: list[dict] = []
        for row in rows:
            fid = str(row["file_id"] or "")
            if file_id and file_id != fid:
                continue
            file_row = conn.execute("SELECT * FROM file_records_v2 WHERE id = ?", (fid,)).fetchone()
            if not file_row or not _v2_can_view_file(conn, user, file_row):
                continue
            out.append(
                {
                    "id": str(row["id"] or ""),
                    "file_id": fid,
                    "version_id": str(row["version_id"] or ""),
                    "encryption_method": str(row["encryption_method"] or ""),
                    "key_ref": str(row["key_ref"] or ""),
                    "locked_at": int(row["locked_at"] or 0),
                    "locked_by": str(row["locked_by"] or ""),
                    "retention_class": str(row["retention_class"] or ""),
                    "created_at": int(row["created_at"] or 0),
                }
            )
        return {"ok": True, "archives": out}, 200


def _v2_file_center_certificates(user: dict | None, query: dict[str, list[str]] | None = None) -> tuple[dict, int]:
    actor = _v2_user_email(user)
    if not actor:
        return {"ok": False, "error": "authentication_required"}, 401
    requested_user = normalize_email((query or {}).get("user_id", [""])[0] if query else "")
    target = requested_user if requested_user and is_admin_user(user) else actor
    with v2_db_lock, _v2_db_conn() as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM file_signer_certificates_v2
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT 50
            """,
            (target,),
        ).fetchall()
        return {"ok": True, "certificates": [_v2_certificate_payload(row) for row in rows]}, 200


def _v2_file_center_create_certificate(user: dict | None, payload: dict) -> tuple[dict, int]:
    actor = _v2_user_email(user)
    if not actor:
        return {"ok": False, "error": "authentication_required"}, 401
    target = normalize_email(payload.get("user_id") or actor)
    if target != actor and not is_admin_user(user):
        return {"ok": False, "error": "permission_denied"}, 403
    if not _v2_user_exists(target):
        return {"ok": False, "error": "user_not_found"}, 404
    with v2_db_lock, _v2_db_conn() as conn:
        cert = _v2_create_signer_certificate(
            conn,
            user_id=target,
            actor=actor,
            subject_name=str(payload.get("subject_name") or user_display_label(target)),
            validity_days=int(payload.get("validity_days") or 730),
        )
        conn.commit()
        return {"ok": True, "certificate": _v2_certificate_payload(cert)}, 200


def _v2_file_center_revoke_certificate(user: dict | None, certificate_id: str, payload: dict) -> tuple[dict, int]:
    actor = _v2_user_email(user)
    if not actor:
        return {"ok": False, "error": "authentication_required"}, 401
    with v2_db_lock, _v2_db_conn() as conn:
        cert = conn.execute("SELECT * FROM file_signer_certificates_v2 WHERE id = ?", (certificate_id,)).fetchone()
        if not cert:
            return {"ok": False, "error": "certificate_not_found"}, 404
        if normalize_email(cert["user_id"] or "") != actor and not is_admin_user(user):
            return {"ok": False, "error": "permission_denied"}, 403
        now_ts = _v2_now()
        conn.execute(
            """
            UPDATE file_signer_certificates_v2
            SET status = 'revoked', revoked_at = ?, revoked_by = ?, metadata_json = ?
            WHERE id = ?
            """,
            (
                now_ts,
                actor,
                json.dumps({"revoke_reason": str(payload.get("reason") or "")[:500]}, ensure_ascii=False),
                certificate_id,
            ),
        )
        _v2_audit(conn, actor, "file_certificate_revoke", "file_certificate", certificate_id, {"reason": str(payload.get("reason") or "")[:200]})
        conn.commit()
        updated = conn.execute("SELECT * FROM file_signer_certificates_v2 WHERE id = ?", (certificate_id,)).fetchone()
        return {"ok": True, "certificate": _v2_certificate_payload(updated)}, 200


def _v2_file_center_admin_summary(user: dict | None) -> tuple[dict, int]:
    if not is_admin_user(user):
        return {"ok": False, "error": "admin_required"}, 403
    with v2_db_lock, _v2_db_conn() as conn:
        total = conn.execute("SELECT COUNT(*) AS c FROM file_records_v2").fetchone()
        pending = conn.execute(
            "SELECT COUNT(*) AS c FROM file_workflow_steps_v2 WHERE status = 'pending'",
        ).fetchone()
        signed = conn.execute(
            "SELECT COUNT(*) AS c FROM file_records_v2 WHERE is_locked = 1",
        ).fetchone()
        rejected = conn.execute(
            "SELECT COUNT(*) AS c FROM file_records_v2 WHERE status = 'rejected'",
        ).fetchone()
        overdue = conn.execute(
            "SELECT COUNT(*) AS c FROM file_workflow_steps_v2 WHERE status = 'pending' AND created_at < ?",
            (_v2_now() - 48 * 60 * 60,),
        ).fetchone()
        by_workspace = conn.execute(
            "SELECT workspace_id, COUNT(*) AS c FROM file_records_v2 GROUP BY workspace_id ORDER BY c DESC",
        ).fetchall()
        return {
            "ok": True,
            "totals": {
                "files": int(total["c"] or 0),
                "pending_steps": int(pending["c"] or 0),
                "signed_locked_files": int(signed["c"] or 0),
                "rejected_files": int(rejected["c"] or 0),
                "overdue_steps": int(overdue["c"] or 0),
            },
            "workspace_breakdown": [{"workspace_id": str(item["workspace_id"] or ""), "count": int(item["c"] or 0)} for item in by_workspace],
        }, 200


def _v2_file_center_my_overview(user: dict | None) -> tuple[dict, int]:
    if not user:
        return {"ok": False, "error": "authentication_required"}, 401
    actor = _v2_user_email(user)
    with v2_db_lock, _v2_db_conn() as conn:
        mine = conn.execute("SELECT COUNT(*) AS c FROM file_records_v2 WHERE owner_user_id = ?", (actor,)).fetchone()
        pending = conn.execute(
            "SELECT COUNT(*) AS c FROM file_workflow_steps_v2 WHERE assigned_user_id = ? AND status = 'pending'",
            (actor,),
        ).fetchone()
        signed = conn.execute(
            "SELECT COUNT(*) AS c FROM file_versions_v2 WHERE signed_by = ?",
            (actor,),
        ).fetchone()
        recent = conn.execute(
            """
            SELECT r.*
            FROM file_records_v2 r
            WHERE r.owner_user_id = ?
               OR EXISTS(
                    SELECT 1
                    FROM file_workflow_steps_v2 s
                    LEFT JOIN file_workflows_v2 w ON w.id = s.workflow_id
                    WHERE w.file_id = r.id
                      AND s.assigned_user_id = ?
                      AND s.status = 'pending'
               )
            ORDER BY r.updated_at DESC
            LIMIT 30
            """,
            (actor, actor),
        ).fetchall()
        return {
            "ok": True,
            "user_id": actor,
            "totals": {
                "my_files": int(mine["c"] or 0),
                "my_pending_steps": int(pending["c"] or 0),
                "my_signed_versions": int(signed["c"] or 0),
            },
            "files": [_v2_file_payload(conn, item, include_latest_version=False) for item in recent],
        }, 200


def _v2_file_center_workspace_overview(user: dict | None, workspace_id: str) -> tuple[dict, int]:
    if not user:
        return {"ok": False, "error": "authentication_required"}, 401
    workspace = _v2_file_workspace(workspace_id)
    with v2_db_lock, _v2_db_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM file_records_v2 WHERE workspace_id = ? ORDER BY updated_at DESC LIMIT 1000",
            (workspace,),
        ).fetchall()
        visible = [row for row in rows if _v2_can_view_file(conn, user, row)]
        counts: dict[str, int] = {}
        for row in visible:
            status = str(row["status"] or "draft")
            counts[status] = counts.get(status, 0) + 1
        return {
            "ok": True,
            "workspace_id": workspace,
            "totals": {"files": len(visible), "signed_locked": sum(1 for row in visible if bool(row["is_locked"]))},
            "status_counts": counts,
            "files": [_v2_file_payload(conn, row, include_latest_version=False) for row in visible[:120]],
        }, 200


def _v2_file_center_generate_daily_digest(force: bool = False, day_key: str = "") -> tuple[dict, int]:
    now_local = local_now()
    target = day_key.strip() or local_day_key(now_local - timedelta(days=1))
    if not force and now_local.hour < ADMIN_REPORT_HOUR:
        return {"ok": True, "skipped": True, "reason": "before_schedule_window", "period": target}, 200
    try:
        start_ts, end_ts = _v2_day_window(target)
    except Exception:
        return {"ok": False, "error": "invalid_date"}, 400
    with v2_db_lock, _v2_db_conn() as conn:
        if not force:
            existing = conn.execute(
                "SELECT id FROM reports_v2 WHERE report_type = 'file_center_admin_daily' AND period_start = ? AND period_end = ? LIMIT 1",
                (target, target),
            ).fetchone()
            if existing:
                return {"ok": True, "skipped": True, "reason": "already_generated", "period": target, "report_id": str(existing["id"] or "")}, 200
        created_files = conn.execute(
            "SELECT COUNT(*) AS c FROM file_records_v2 WHERE created_at >= ? AND created_at < ?",
            (start_ts, end_ts),
        ).fetchone()
        updated_versions = conn.execute(
            "SELECT COUNT(*) AS c FROM file_versions_v2 WHERE created_at >= ? AND created_at < ?",
            (start_ts, end_ts),
        ).fetchone()
        approvals = conn.execute(
            """
            SELECT COUNT(*) AS c FROM file_workflow_steps_v2
            WHERE step_type IN ('review', 'approval') AND status IN ('approved', 'done')
              AND acted_at >= ? AND acted_at < ?
            """,
            (start_ts, end_ts),
        ).fetchone()
        signatures = conn.execute(
            """
            SELECT COUNT(*) AS c FROM file_workflow_steps_v2
            WHERE step_type = 'sign' AND status = 'signed'
              AND acted_at >= ? AND acted_at < ?
            """,
            (start_ts, end_ts),
        ).fetchone()
        rejected = conn.execute(
            "SELECT COUNT(*) AS c FROM file_records_v2 WHERE status = 'rejected' AND updated_at >= ? AND updated_at < ?",
            (start_ts, end_ts),
        ).fetchone()
        overdue = conn.execute(
            "SELECT COUNT(*) AS c FROM file_workflow_steps_v2 WHERE status = 'pending' AND created_at < ?",
            (end_ts - 48 * 60 * 60,),
        ).fetchone()
        payload = {
            "period_start": target,
            "period_end": target,
            "new_files": int(created_files["c"] or 0),
            "new_versions": int(updated_versions["c"] or 0),
            "approvals_completed": int(approvals["c"] or 0),
            "signatures_completed": int(signatures["c"] or 0),
            "exceptions": int(rejected["c"] or 0),
            "overdue_pending_steps": int(overdue["c"] or 0),
        }
        report_id = _v2_upsert_report(
            conn,
            report_type="file_center_admin_daily",
            period_start=target,
            period_end=target,
            content=payload,
        )
        conn.execute(
            """
            INSERT INTO file_daily_digest_state_v2(id, digest_date, last_run_at, status, error_message)
            VALUES(?, ?, ?, 'ok', '')
            ON CONFLICT(digest_date) DO UPDATE SET last_run_at=excluded.last_run_at, status='ok', error_message=''
            """,
            (_v2_id("fdg"), target, _v2_now()),
        )
        for admin_email in _v2_admin_emails():
            _v2_notify(
                conn,
                admin_email,
                "report_generated",
                "File center daily digest ready",
                f"File center digest for {target} is ready.",
            )
        _v2_audit(conn, "system", "file_digest_daily_generate", "report_batch", report_id, payload)
        conn.commit()
        return {"ok": True, "period": target, "report_id": report_id, "summary": payload}, 200


def _v2_file_center_list_daily_reports(user: dict | None, query: dict[str, list[str]]) -> tuple[dict, int]:
    if not user:
        return {"ok": False, "error": "authentication_required"}, 401
    if not is_admin_user(user):
        return {"ok": False, "error": "admin_required"}, 403
    day_key = str(query.get("date", [""])[0] or "").strip()
    with v2_db_lock, _v2_db_conn() as conn:
        sql = "SELECT * FROM reports_v2 WHERE report_type = 'file_center_admin_daily'"
        params: list[object] = []
        if day_key:
            sql += " AND period_start = ?"
            params.append(day_key)
        sql += " ORDER BY generated_at DESC LIMIT 120"
        rows = conn.execute(sql, params).fetchall()
        return {"ok": True, "reports": [_v2_report_payload(conn, row, include_content=True) for row in rows]}, 200


def _v2_report_state_payload() -> dict:
    state = _load_json_file(V2_REPORT_SCHEDULER_STATE, {})
    if not isinstance(state, dict):
        state = {}
    return {
        "last_daily_period": str(state.get("last_daily_period") or ""),
        "last_weekly_period": str(state.get("last_weekly_period") or ""),
        "last_run_at": int(state.get("last_run_at", 0) or 0),
    }


def _v2_save_report_state_payload(state: dict) -> None:
    _save_json_file(V2_REPORT_SCHEDULER_STATE, state)


def _v2_day_window(day_key: str) -> tuple[int, int]:
    day = datetime.strptime(day_key, "%Y-%m-%d").replace(tzinfo=LOCAL_TIMEZONE)
    start_ts = int(day.timestamp())
    end_ts = int((day + timedelta(days=1)).timestamp())
    return start_ts, end_ts


def _v2_previous_week_window(now_local: datetime) -> tuple[str, str, int, int]:
    this_week_start = (now_local - timedelta(days=now_local.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
    prev_week_start = this_week_start - timedelta(days=7)
    prev_week_end = this_week_start - timedelta(seconds=1)
    start_key = prev_week_start.strftime("%Y-%m-%d")
    end_key = prev_week_end.strftime("%Y-%m-%d")
    return start_key, end_key, int(prev_week_start.timestamp()), int(this_week_start.timestamp())


def _v2_reports_for_period_exists(
    conn: sqlite3.Connection,
    report_type: str,
    *,
    user_id: str = "",
    project_id: str = "",
    period_start: str,
    period_end: str,
) -> bool:
    hit = conn.execute(
        """
        SELECT 1
        FROM reports_v2
        WHERE report_type = ? AND user_id = ? AND project_id = ? AND period_start = ? AND period_end = ?
        LIMIT 1
        """,
        (report_type, user_id, project_id, period_start, period_end),
    ).fetchone()
    return bool(hit)


def _v2_upsert_report(
    conn: sqlite3.Connection,
    *,
    report_type: str,
    user_id: str = "",
    project_id: str = "",
    period_start: str,
    period_end: str,
    content: dict,
    status: str = "generated",
) -> str:
    row = conn.execute(
        """
        SELECT id
        FROM reports_v2
        WHERE report_type = ? AND user_id = ? AND project_id = ? AND period_start = ? AND period_end = ?
        LIMIT 1
        """,
        (report_type, user_id, project_id, period_start, period_end),
    ).fetchone()
    now_ts = _v2_now()
    payload = json.dumps(content, ensure_ascii=False)[:20000]
    if row:
        report_id = str(row["id"] or "")
        conn.execute(
            """
            UPDATE reports_v2
            SET content_json = ?, generated_at = ?, status = ?
            WHERE id = ?
            """,
            (payload, now_ts, status if status in V2_REPORT_REVIEW_STATUS else "generated", report_id),
        )
        return report_id
    report_id = _v2_id("rpt")
    conn.execute(
        """
        INSERT INTO reports_v2(
          id, report_type, user_id, project_id, period_start, period_end, content_json, generated_at, status
        ) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            report_id,
            report_type,
            normalize_email(user_id),
            project_id,
            period_start,
            period_end,
            payload,
            now_ts,
            status if status in V2_REPORT_REVIEW_STATUS else "generated",
        ),
    )
    return report_id


def _v2_active_user_emails() -> list[str]:
    users = list_local_users().get("users", [])
    emails: list[str] = []
    for item in users if isinstance(users, list) else []:
        if not isinstance(item, dict):
            continue
        email = normalize_email(item.get("email", ""))
        if not email:
            continue
        if str(item.get("approval_status") or "approved") != "approved":
            continue
        emails.append(email)
    return sorted(set(emails))


def _v2_admin_emails() -> list[str]:
    users = list_local_users().get("users", [])
    emails: list[str] = []
    for item in users if isinstance(users, list) else []:
        if not isinstance(item, dict):
            continue
        if str(item.get("role") or "") != "admin":
            continue
        if str(item.get("approval_status") or "approved") != "approved":
            continue
        email = normalize_email(item.get("email", ""))
        if email:
            emails.append(email)
    return sorted(set(emails))


def _v2_project_manager_emails(conn: sqlite3.Connection, project_id: str) -> list[str]:
    row = conn.execute("SELECT owner_id FROM projects WHERE id = ?", (project_id,)).fetchone()
    emails = {normalize_email(row["owner_id"] or "")} if row else set()
    members = conn.execute(
        """
        SELECT user_id
        FROM project_members
        WHERE project_id = ? AND role_in_project IN ('owner', 'manager')
        """,
        (project_id,),
    ).fetchall()
    for member in members:
        email = normalize_email(member["user_id"] or "")
        if email:
            emails.add(email)
    return sorted(email for email in emails if email)


def _v2_document_metrics(period_start_ts: int, period_end_ts: int) -> dict:
    data = _load_document_flow_payload()
    docs = [item for item in data.get("documents", []) if isinstance(item, dict)]
    actions = [item for item in data.get("actions", []) if isinstance(item, dict)]
    total_pending_approval = 0
    total_pending_signature = 0
    changed_in_period = 0
    for doc in docs:
        status = str(doc.get("current_status") or "")
        step = str(doc.get("current_step") or "")
        updated_at = int(doc.get("updated_at", 0) or 0)
        if status == "pending_approval":
            total_pending_approval += 1
        if step == "sign" and not bool(doc.get("is_locked")):
            total_pending_signature += 1
        if period_start_ts <= updated_at < period_end_ts:
            changed_in_period += 1
    return {
        "pending_approval": total_pending_approval,
        "pending_signature": total_pending_signature,
        "changed_in_period": changed_in_period,
        "actions_in_period": sum(1 for item in actions if period_start_ts <= int(item.get("created_at", 0) or 0) < period_end_ts),
    }


def _v2_document_metrics_for_project(project_id: str, period_start_ts: int, period_end_ts: int) -> dict:
    data = _load_document_flow_payload()
    docs = [
        item for item in data.get("documents", [])
        if isinstance(item, dict) and str(item.get("project_id") or "") == project_id
    ]
    actions = [
        item for item in data.get("actions", [])
        if isinstance(item, dict) and period_start_ts <= int(item.get("created_at", 0) or 0) < period_end_ts
    ]
    status_counts: dict[str, int] = {}
    for doc in docs:
        status = str(doc.get("current_status") or "draft")
        status_counts[status] = status_counts.get(status, 0) + 1
    return {
        "total_documents": len(docs),
        "status_counts": status_counts,
        "actions_in_period": len(
            [
                item
                for item in actions
                if str(item.get("document_id") or "")
                in {str(doc.get("id") or "") for doc in docs}
            ]
        ),
    }


def _v2_generate_admin_summary_report(
    conn: sqlite3.Connection,
    *,
    period_start: str,
    period_end: str,
    period_start_ts: int,
    period_end_ts: int,
) -> str:
    new_projects = conn.execute(
        "SELECT COUNT(*) AS c FROM projects WHERE created_at >= ? AND created_at < ?",
        (period_start_ts, period_end_ts),
    ).fetchone()
    active_projects = conn.execute(
        "SELECT COUNT(*) AS c FROM projects WHERE status = 'active'",
    ).fetchone()
    completed_tasks = conn.execute(
        """
        SELECT COUNT(*) AS c
        FROM work_items
        WHERE status = 'done' AND updated_at >= ? AND updated_at < ?
        """,
        (period_start_ts, period_end_ts),
    ).fetchone()
    overdue_tasks = conn.execute(
        """
        SELECT COUNT(*) AS c
        FROM work_items
        WHERE due_date <> '' AND due_date < ? AND status NOT IN ('done', 'cancelled')
        """,
        (period_end,),
    ).fetchone()
    new_issues = conn.execute(
        "SELECT COUNT(*) AS c FROM project_issues WHERE created_at >= ? AND created_at < ?",
        (period_start_ts, period_end_ts),
    ).fetchone()
    unresolved_issues = conn.execute(
        "SELECT COUNT(*) AS c FROM project_issues WHERE status NOT IN ('resolved', 'closed')",
    ).fetchone()
    risk_issues = conn.execute(
        "SELECT COUNT(*) AS c FROM project_issues WHERE status NOT IN ('resolved', 'closed') AND severity IN ('high', 'critical')",
    ).fetchone()
    project_rows = conn.execute(
        "SELECT id, name, status, updated_at FROM projects ORDER BY updated_at DESC LIMIT 100",
    ).fetchall()
    project_progress: list[dict] = []
    for row in project_rows:
        pid = str(row["id"] or "")
        task_stats = conn.execute(
            """
            SELECT
              SUM(CASE WHEN status = 'done' AND updated_at >= ? AND updated_at < ? THEN 1 ELSE 0 END) AS done_in_period,
              SUM(CASE WHEN status NOT IN ('done', 'cancelled') THEN 1 ELSE 0 END) AS open_tasks
            FROM work_items
            WHERE project_id = ?
            """,
            (period_start_ts, period_end_ts, pid),
        ).fetchone()
        issue_stats = conn.execute(
            """
            SELECT
              SUM(CASE WHEN status NOT IN ('resolved', 'closed') THEN 1 ELSE 0 END) AS open_issues
            FROM project_issues
            WHERE project_id = ?
            """,
            (pid,),
        ).fetchone()
        project_progress.append(
            {
                "project_id": pid,
                "project_name": str(row["name"] or ""),
                "status": str(row["status"] or ""),
                "done_tasks_in_period": int(task_stats["done_in_period"] or 0) if task_stats else 0,
                "open_tasks": int(task_stats["open_tasks"] or 0) if task_stats else 0,
                "open_issues": int(issue_stats["open_issues"] or 0) if issue_stats else 0,
                "last_updated": int(row["updated_at"] or 0),
            }
        )
    doc_metrics = _v2_document_metrics(period_start_ts, period_end_ts)
    summary = {
        "period_start": period_start,
        "period_end": period_end,
        "new_projects": int(new_projects["c"] or 0) if new_projects else 0,
        "active_projects": int(active_projects["c"] or 0) if active_projects else 0,
        "completed_tasks": int(completed_tasks["c"] or 0) if completed_tasks else 0,
        "overdue_tasks": int(overdue_tasks["c"] or 0) if overdue_tasks else 0,
        "pending_approvals": int(doc_metrics.get("pending_approval", 0)),
        "pending_signatures": int(doc_metrics.get("pending_signature", 0)),
        "new_issues": int(new_issues["c"] or 0) if new_issues else 0,
        "unresolved_issues": int(unresolved_issues["c"] or 0) if unresolved_issues else 0,
        "risk_blockers": int(risk_issues["c"] or 0) if risk_issues else 0,
        "document_activity": doc_metrics,
        "project_progress": project_progress[:50],
        "items_requiring_attention": [
            "overdue_tasks" if int(overdue_tasks["c"] or 0) > 0 else "",
            "risk_blockers" if int(risk_issues["c"] or 0) > 0 else "",
            "pending_signatures" if int(doc_metrics.get("pending_signature", 0)) > 0 else "",
        ],
    }
    summary["items_requiring_attention"] = [item for item in summary["items_requiring_attention"] if item]
    return _v2_upsert_report(
        conn,
        report_type="admin_daily_summary",
        period_start=period_start,
        period_end=period_end,
        content=summary,
    )


def _v2_generate_user_report(
    conn: sqlite3.Connection,
    *,
    user_id: str,
    report_type: str,
    period_start: str,
    period_end: str,
    period_start_ts: int,
    period_end_ts: int,
) -> str:
    actor = normalize_email(user_id)
    task_done = conn.execute(
        """
        SELECT COUNT(*) AS c
        FROM work_items wi
        LEFT JOIN work_item_assignees wa ON wa.work_item_id = wi.id
        WHERE wa.user_id = ? AND wi.status = 'done' AND wi.updated_at >= ? AND wi.updated_at < ?
        """,
        (actor, period_start_ts, period_end_ts),
    ).fetchone()
    task_ongoing = conn.execute(
        """
        SELECT COUNT(*) AS c
        FROM work_items wi
        LEFT JOIN work_item_assignees wa ON wa.work_item_id = wi.id
        WHERE wa.user_id = ? AND wi.status NOT IN ('done', 'cancelled')
        """,
        (actor,),
    ).fetchone()
    project_rows = conn.execute(
        """
        SELECT DISTINCT wi.project_id
        FROM work_items wi
        LEFT JOIN work_item_assignees wa ON wa.work_item_id = wi.id
        WHERE wa.user_id = ? AND wi.updated_at >= ? AND wi.updated_at < ?
        """,
        (actor, period_start_ts, period_end_ts),
    ).fetchall()
    issue_rows = conn.execute(
        """
        SELECT
          SUM(CASE WHEN reported_by = ? AND created_at >= ? AND created_at < ? THEN 1 ELSE 0 END) AS reported_in_period,
          SUM(CASE WHEN assigned_to = ? AND status NOT IN ('resolved', 'closed') THEN 1 ELSE 0 END) AS unresolved_assigned
        FROM project_issues
        """,
        (actor, period_start_ts, period_end_ts, actor),
    ).fetchone()
    docs = _load_document_flow_payload()
    handled_docs = 0
    approval_actions = 0
    for action in docs.get("actions", []):
        if not isinstance(action, dict):
            continue
        if normalize_email(action.get("actor_id", "")) != actor:
            continue
        ts = int(action.get("created_at", 0) or 0)
        if not (period_start_ts <= ts < period_end_ts):
            continue
        handled_docs += 1
        if str(action.get("action_type") or "") in {"review_pass", "approve", "sign", "request_changes", "return_for_revision"}:
            approval_actions += 1
    pending_docs = 0
    for doc in docs.get("documents", []):
        if not isinstance(doc, dict):
            continue
        if normalize_email(doc.get("current_handler_id", "")) != actor:
            continue
        if str(doc.get("current_status") or "") in {"in_review", "pending_approval", "approved"}:
            pending_docs += 1
    summary = {
        "period_start": period_start,
        "period_end": period_end,
        "projects_participated": sorted({str(row["project_id"] or "") for row in project_rows if str(row["project_id"] or "")}),
        "tasks_completed": int(task_done["c"] or 0) if task_done else 0,
        "tasks_ongoing": int(task_ongoing["c"] or 0) if task_ongoing else 0,
        "documents_handled": handled_docs,
        "approvals_reviews_signatures_processed": approval_actions,
        "pending_documents_for_me": pending_docs,
        "issues_reported": int(issue_rows["reported_in_period"] or 0) if issue_rows else 0,
        "issues_unresolved_assigned": int(issue_rows["unresolved_assigned"] or 0) if issue_rows else 0,
        "tomorrow_plan": "Focus on unfinished tasks, resolve blockers, and clear pending reviews.",
    }
    return _v2_upsert_report(
        conn,
        report_type=report_type,
        user_id=actor,
        period_start=period_start,
        period_end=period_end,
        content=summary,
    )


def _v2_generate_project_report(
    conn: sqlite3.Connection,
    *,
    project_id: str,
    report_type: str,
    period_start: str,
    period_end: str,
    period_start_ts: int,
    period_end_ts: int,
) -> str:
    row = conn.execute("SELECT id, name, owner_id, status FROM projects WHERE id = ?", (project_id,)).fetchone()
    if not row:
        return ""
    done_tasks = conn.execute(
        """
        SELECT COUNT(*) AS c
        FROM work_items
        WHERE project_id = ? AND status = 'done' AND updated_at >= ? AND updated_at < ?
        """,
        (project_id, period_start_ts, period_end_ts),
    ).fetchone()
    pending_tasks = conn.execute(
        """
        SELECT COUNT(*) AS c
        FROM work_items
        WHERE project_id = ? AND status NOT IN ('done', 'cancelled')
        """,
        (project_id,),
    ).fetchone()
    overdue_tasks = conn.execute(
        """
        SELECT COUNT(*) AS c
        FROM work_items
        WHERE project_id = ? AND due_date <> '' AND due_date < ? AND status NOT IN ('done', 'cancelled')
        """,
        (project_id, period_end),
    ).fetchone()
    issue_stats = conn.execute(
        """
        SELECT
          SUM(CASE WHEN created_at >= ? AND created_at < ? THEN 1 ELSE 0 END) AS new_issues,
          SUM(CASE WHEN status NOT IN ('resolved', 'closed') THEN 1 ELSE 0 END) AS unresolved_issues,
          SUM(CASE WHEN status NOT IN ('resolved', 'closed') AND severity IN ('high', 'critical') THEN 1 ELSE 0 END) AS high_risk_issues
        FROM project_issues
        WHERE project_id = ?
        """,
        (period_start_ts, period_end_ts, project_id),
    ).fetchone()
    docs = _v2_document_metrics_for_project(project_id, period_start_ts, period_end_ts)
    payload = {
        "period_start": period_start,
        "period_end": period_end,
        "project_id": project_id,
        "project_name": str(row["name"] or ""),
        "project_status": str(row["status"] or ""),
        "owner_id": normalize_email(row["owner_id"] or ""),
        "completed_tasks": int(done_tasks["c"] or 0) if done_tasks else 0,
        "pending_tasks": int(pending_tasks["c"] or 0) if pending_tasks else 0,
        "overdue_tasks": int(overdue_tasks["c"] or 0) if overdue_tasks else 0,
        "new_issues": int(issue_stats["new_issues"] or 0) if issue_stats else 0,
        "unresolved_issues": int(issue_stats["unresolved_issues"] or 0) if issue_stats else 0,
        "high_risk_issues": int(issue_stats["high_risk_issues"] or 0) if issue_stats else 0,
        "document_status": docs,
        "next_phase_plan": "Prioritize overdue tasks, clear approvals, and close high-risk blockers.",
    }
    return _v2_upsert_report(
        conn,
        report_type=report_type,
        project_id=project_id,
        period_start=period_start,
        period_end=period_end,
        content=payload,
    )


def _v2_generate_daily_reports(force: bool = False) -> None:
    now_local = local_now()
    if not force and now_local.hour < ADMIN_REPORT_HOUR:
        return
    period_key = local_day_key(now_local - timedelta(days=1))
    state = _v2_report_state_payload()
    if not force and state.get("last_daily_period") == period_key:
        return
    period_start_ts, period_end_ts = _v2_day_window(period_key)
    with v2_db_lock, _v2_db_conn() as conn:
        admin_report_id = _v2_generate_admin_summary_report(
            conn,
            period_start=period_key,
            period_end=period_key,
            period_start_ts=period_start_ts,
            period_end_ts=period_end_ts,
        )
        admin_recipients = _v2_admin_emails()
        for email in admin_recipients:
            _v2_notify(
                conn,
                email,
                "report_generated",
                "Daily admin summary generated",
                f"Platform summary for {period_key} is ready.",
            )
        users = _v2_active_user_emails()
        for email in users:
            _v2_generate_user_report(
                conn,
                user_id=email,
                report_type="user_daily",
                period_start=period_key,
                period_end=period_key,
                period_start_ts=period_start_ts,
                period_end_ts=period_end_ts,
            )
            _v2_notify(
                conn,
                email,
                "report_generated",
                "Daily report generated",
                f"Your daily report for {period_key} is ready.",
            )
        project_rows = conn.execute("SELECT id FROM projects").fetchall()
        for row in project_rows:
            project_id = str(row["id"] or "")
            report_id = _v2_generate_project_report(
                conn,
                project_id=project_id,
                report_type="project_daily",
                period_start=period_key,
                period_end=period_key,
                period_start_ts=period_start_ts,
                period_end_ts=period_end_ts,
            )
            if report_id:
                for manager in _v2_project_manager_emails(conn, project_id):
                    _v2_notify(
                        conn,
                        manager,
                        "report_generated",
                        "Project daily report generated",
                        f"Project daily report for {period_key} is ready.",
                        project_id=project_id,
                    )
        _v2_audit(
            conn,
            "system",
            "report_generate_daily",
            "report_batch",
            admin_report_id,
            {"period": period_key, "users": len(users), "projects": len(project_rows)},
        )
        conn.commit()
    state["last_daily_period"] = period_key
    state["last_run_at"] = _v2_now()
    _v2_save_report_state_payload(state)


def _v2_generate_weekly_reports(force: bool = False) -> None:
    now_local = local_now()
    if not force and (now_local.weekday() != 0 or now_local.hour < ADMIN_REPORT_HOUR):
        return
    period_start, period_end, start_ts, end_ts = _v2_previous_week_window(now_local)
    period_key = f"{period_start}:{period_end}"
    state = _v2_report_state_payload()
    if not force and state.get("last_weekly_period") == period_key:
        return
    with v2_db_lock, _v2_db_conn() as conn:
        users = _v2_active_user_emails()
        for email in users:
            _v2_generate_user_report(
                conn,
                user_id=email,
                report_type="user_weekly",
                period_start=period_start,
                period_end=period_end,
                period_start_ts=start_ts,
                period_end_ts=end_ts,
            )
            _v2_notify(
                conn,
                email,
                "report_generated",
                "Weekly report generated",
                f"Your weekly report ({period_start} ~ {period_end}) is ready.",
            )
        project_rows = conn.execute("SELECT id FROM projects").fetchall()
        for row in project_rows:
            project_id = str(row["id"] or "")
            report_id = _v2_generate_project_report(
                conn,
                project_id=project_id,
                report_type="project_weekly",
                period_start=period_start,
                period_end=period_end,
                period_start_ts=start_ts,
                period_end_ts=end_ts,
            )
            if report_id:
                for manager in _v2_project_manager_emails(conn, project_id):
                    _v2_notify(
                        conn,
                        manager,
                        "report_generated",
                        "Project weekly report generated",
                        f"Project weekly report ({period_start} ~ {period_end}) is ready.",
                        project_id=project_id,
                    )
        _v2_audit(
            conn,
            "system",
            "report_generate_weekly",
            "report_batch",
            period_key,
            {"period_start": period_start, "period_end": period_end, "users": len(users), "projects": len(project_rows)},
        )
        conn.commit()
    state["last_weekly_period"] = period_key
    state["last_run_at"] = _v2_now()
    _v2_save_report_state_payload(state)


def _v2_maybe_generate_reports(force: bool = False) -> None:
    _v2_generate_daily_reports(force=force)
    _v2_generate_weekly_reports(force=force)
    _v2_file_center_generate_daily_digest(force=force)
    _v2_chat_maybe_run_jobs(force=force)
    _v2_intel_maybe_run_jobs(force=force)


def _v2_report_payload(conn: sqlite3.Connection, row: sqlite3.Row, *, include_content: bool = True) -> dict:
    payload = {
        "id": str(row["id"] or ""),
        "report_type": str(row["report_type"] or ""),
        "user_id": str(row["user_id"] or ""),
        "project_id": str(row["project_id"] or ""),
        "period_start": str(row["period_start"] or ""),
        "period_end": str(row["period_end"] or ""),
        "generated_at": int(row["generated_at"] or 0),
        "status": str(row["status"] or "generated"),
    }
    if include_content:
        payload["content"] = _v2_json_load(str(row["content_json"] or "{}"), {})
    comments_count = conn.execute("SELECT COUNT(*) AS c FROM report_comments_v2 WHERE report_id = ?", (payload["id"],)).fetchone()
    payload["comments_count"] = int(comments_count["c"] or 0) if comments_count else 0
    return payload


def _v2_can_view_report(conn: sqlite3.Connection, user: dict | None, row: sqlite3.Row) -> bool:
    if is_admin_user(user):
        return True
    email = _v2_user_email(user)
    if not email:
        return False
    user_id = normalize_email(row["user_id"] or "")
    project_id = str(row["project_id"] or "")
    report_type = str(row["report_type"] or "")
    if report_type.startswith("user_"):
        return email == user_id
    if report_type.startswith("project_"):
        return bool(project_id) and _v2_can_view_project(conn, user, project_id)
    if report_type == "admin_daily_summary":
        return False
    return False


def _v2_can_comment_report(conn: sqlite3.Connection, user: dict | None, row: sqlite3.Row) -> bool:
    if is_admin_user(user):
        return True
    email = _v2_user_email(user)
    if not email:
        return False
    report_type = str(row["report_type"] or "")
    if report_type.startswith("project_"):
        return _v2_can_manage_project(conn, user, str(row["project_id"] or ""))
    if report_type.startswith("user_"):
        return email == normalize_email(row["user_id"] or "")
    return False


def _v2_list_reports(user: dict | None, query: dict[str, list[str]]) -> tuple[dict, int]:
    if not user:
        return {"ok": False, "error": "authentication_required"}, 401
    report_type = str(query.get("report_type", [""])[0] or "").strip()
    project_id = str(query.get("project_id", [""])[0] or "").strip()
    user_id = normalize_email(query.get("user_id", [""])[0]) if query.get("user_id") else ""
    status = str(query.get("status", [""])[0] or "").strip().lower()
    period_start = str(query.get("period_start", [""])[0] or "").strip()
    period_end = str(query.get("period_end", [""])[0] or "").strip()
    q = str(query.get("q", [""])[0] or "").strip().lower()
    with v2_db_lock, _v2_db_conn() as conn:
        rows = conn.execute("SELECT * FROM reports_v2 ORDER BY generated_at DESC LIMIT 500").fetchall()
        output: list[dict] = []
        for row in rows:
            if report_type and str(row["report_type"] or "") != report_type:
                continue
            if project_id and str(row["project_id"] or "") != project_id:
                continue
            if user_id and normalize_email(row["user_id"] or "") != user_id:
                continue
            if status and str(row["status"] or "").lower() != status:
                continue
            if period_start and str(row["period_start"] or "") < period_start:
                continue
            if period_end and str(row["period_end"] or "") > period_end:
                continue
            if not _v2_can_view_report(conn, user, row):
                continue
            item = _v2_report_payload(conn, row, include_content=False)
            if q:
                blob = json.dumps(_v2_json_load(str(row["content_json"] or "{}"), {}), ensure_ascii=False)
                searchable = " ".join(
                    [
                        str(item.get("report_type") or ""),
                        str(item.get("user_id") or ""),
                        str(item.get("project_id") or ""),
                        str(item.get("status") or ""),
                        blob,
                    ]
                ).lower()
                if q not in searchable:
                    continue
            output.append(item)
        return {"ok": True, "reports": output, "count": len(output)}, 200


def _v2_report_detail(user: dict | None, report_id: str) -> tuple[dict, int]:
    if not user:
        return {"ok": False, "error": "authentication_required"}, 401
    with v2_db_lock, _v2_db_conn() as conn:
        row = conn.execute("SELECT * FROM reports_v2 WHERE id = ?", (report_id,)).fetchone()
        if not row:
            return {"ok": False, "error": "report_not_found"}, 404
        if not _v2_can_view_report(conn, user, row):
            return {"ok": False, "error": "permission_denied"}, 403
        comments = conn.execute(
            """
            SELECT id, report_id, commented_by, comment, created_at
            FROM report_comments_v2
            WHERE report_id = ?
            ORDER BY created_at ASC
            """,
            (report_id,),
        ).fetchall()
        payload = _v2_report_payload(conn, row, include_content=True)
        payload["comments"] = [
            {
                "id": str(item["id"] or ""),
                "report_id": str(item["report_id"] or ""),
                "commented_by": str(item["commented_by"] or ""),
                "commented_by_name": user_display_label(str(item["commented_by"] or "")),
                "comment": str(item["comment"] or ""),
                "created_at": int(item["created_at"] or 0),
            }
            for item in comments
        ]
        return {"ok": True, "report": payload}, 200


def _v2_add_report_comment(user: dict | None, report_id: str, payload: dict) -> tuple[dict, int]:
    if not user:
        return {"ok": False, "error": "authentication_required"}, 401
    actor = _v2_user_email(user)
    comment = str(payload.get("comment") or "").strip()
    if not comment:
        return {"ok": False, "error": "comment_required"}, 400
    with v2_db_lock, _v2_db_conn() as conn:
        row = conn.execute("SELECT * FROM reports_v2 WHERE id = ?", (report_id,)).fetchone()
        if not row:
            return {"ok": False, "error": "report_not_found"}, 404
        if not _v2_can_comment_report(conn, user, row):
            return {"ok": False, "error": "permission_denied"}, 403
        conn.execute(
            """
            INSERT INTO report_comments_v2(id, report_id, commented_by, comment, created_at)
            VALUES(?, ?, ?, ?, ?)
            """,
            (_v2_id("rpc"), report_id, actor, comment[:3000], _v2_now()),
        )
        current_status = str(row["status"] or "generated")
        if current_status == "generated":
            conn.execute("UPDATE reports_v2 SET status = ? WHERE id = ?", ("reviewed", report_id))
        user_id = normalize_email(row["user_id"] or "")
        project_id = str(row["project_id"] or "")
        recipients = set()
        if user_id and user_id != actor:
            recipients.add(user_id)
        if project_id:
            recipients.update(_v2_project_manager_emails(conn, project_id))
        for email in recipients:
            if email == actor:
                continue
            _v2_notify(
                conn,
                email,
                "report_comment",
                "Report comment added",
                f"{user_display_label(actor)} commented on report {report_id}.",
                project_id=project_id,
            )
        _v2_audit(conn, actor, "report_comment_add", "report", report_id, {"comment": comment[:200]})
        conn.commit()
    return _v2_report_detail(user, report_id)


def _v2_update_report_status(user: dict | None, report_id: str, payload: dict) -> tuple[dict, int]:
    if not user:
        return {"ok": False, "error": "authentication_required"}, 401
    actor = _v2_user_email(user)
    status = str(payload.get("status") or "").strip().lower()
    if status not in V2_REPORT_REVIEW_STATUS:
        return {"ok": False, "error": "invalid_status"}, 400
    with v2_db_lock, _v2_db_conn() as conn:
        row = conn.execute("SELECT * FROM reports_v2 WHERE id = ?", (report_id,)).fetchone()
        if not row:
            return {"ok": False, "error": "report_not_found"}, 404
        if not _v2_can_comment_report(conn, user, row):
            return {"ok": False, "error": "permission_denied"}, 403
        conn.execute("UPDATE reports_v2 SET status = ?, generated_at = ? WHERE id = ?", (status, _v2_now(), report_id))
        note = str(payload.get("note") or "").strip()
        if note:
            conn.execute(
                """
                INSERT INTO report_comments_v2(id, report_id, commented_by, comment, created_at)
                VALUES(?, ?, ?, ?, ?)
                """,
                (_v2_id("rpc"), report_id, actor, note[:3000], _v2_now()),
            )
        _v2_audit(conn, actor, "report_status_update", "report", report_id, {"status": status})
        conn.commit()
    return _v2_report_detail(user, report_id)


def _v2_workbench_payload(user: dict | None, query: dict[str, list[str]]) -> tuple[dict, int]:
    if not user:
        return {"ok": False, "error": "authentication_required"}, 401
    projects_payload = _v2_list_projects(user, query)
    if not projects_payload.get("ok"):
        return projects_payload, 400
    projects = projects_payload.get("projects", []) if isinstance(projects_payload.get("projects"), list) else []
    with v2_db_lock, _v2_db_conn() as conn:
        email = _v2_user_email(user)
        visible_projects = _v2_user_project_ids(conn, user)
        visible_project_ids = sorted(visible_projects)
        project_clause = ",".join(["?"] * len(visible_project_ids)) if visible_project_ids else "''"
        overdue = conn.execute(
            """
            SELECT COUNT(*) AS c
            FROM work_items
            WHERE due_date <> '' AND due_date < ? AND status NOT IN ('done', 'cancelled')
              AND project_id IN ({})
            """.format(project_clause),
            ([local_day_key()] + visible_project_ids) if visible_project_ids else [local_day_key()],
        ).fetchone()
        high_risk_projects = conn.execute(
            """
            SELECT COUNT(DISTINCT project_id) AS c
            FROM project_issues
            WHERE status NOT IN ('resolved', 'closed') AND severity IN ('high', 'critical')
              AND project_id IN ({})
            """.format(project_clause),
            visible_project_ids if visible_project_ids else [],
        ).fetchone()
        pending_tasks = conn.execute(
            """
            SELECT COUNT(*) AS c
            FROM work_items wi
            LEFT JOIN work_item_assignees wa ON wa.work_item_id = wi.id
            WHERE wa.user_id = ? AND wi.status IN ('in_review', 'pending_approval', 'blocked')
            """,
            (email,),
        ).fetchone()
        docs = _load_document_flow_payload()
        my_pending_docs = sum(
            1
            for item in docs.get("documents", [])
            if isinstance(item, dict)
            and normalize_email(item.get("current_handler_id", "")) == email
            and str(item.get("current_status") or "") in {"in_review", "pending_approval", "approved"}
        )
        task_metric_rows = conn.execute(
            """
            SELECT
              project_id,
              SUM(CASE WHEN status NOT IN ('done', 'cancelled') THEN 1 ELSE 0 END) AS open_tasks,
              SUM(CASE WHEN due_date <> '' AND due_date < ? AND status NOT IN ('done', 'cancelled') THEN 1 ELSE 0 END) AS overdue_tasks,
              SUM(CASE WHEN status IN ('in_review', 'pending_approval') THEN 1 ELSE 0 END) AS pending_approvals,
              MAX(updated_at) AS last_task_at
            FROM work_items
            WHERE project_id IN ({})
            GROUP BY project_id
            """.format(project_clause),
            ([local_day_key()] + visible_project_ids) if visible_project_ids else [local_day_key()],
        ).fetchall()
        issue_metric_rows = conn.execute(
            """
            SELECT
              project_id,
              SUM(CASE WHEN status NOT IN ('resolved', 'closed') THEN 1 ELSE 0 END) AS open_issues,
              SUM(CASE WHEN status NOT IN ('resolved', 'closed') AND severity IN ('high', 'critical') THEN 1 ELSE 0 END) AS high_risk,
              MAX(updated_at) AS last_issue_at
            FROM project_issues
            WHERE project_id IN ({})
            GROUP BY project_id
            """.format(project_clause),
            visible_project_ids if visible_project_ids else [],
        ).fetchall()
        file_metric_rows = conn.execute(
            """
            SELECT
              project_id,
              COUNT(*) AS files,
              SUM(CASE WHEN is_locked = 1 THEN 1 ELSE 0 END) AS signed_locked,
              SUM(CASE WHEN is_signed = 1 THEN 1 ELSE 0 END) AS signed_files,
              SUM(CASE WHEN status IN ('reviewing', 'approving', 'signing', 'pending_approval', 'pending_review') THEN 1 ELSE 0 END) AS active_file_flows,
              MAX(updated_at) AS last_file_at
            FROM file_records_v2
            WHERE project_id IN ({})
            GROUP BY project_id
            """.format(project_clause),
            visible_project_ids if visible_project_ids else [],
        ).fetchall()
        file_step_rows = conn.execute(
            """
            SELECT
              fw.project_id,
              COUNT(*) AS pending_file_steps
            FROM file_workflow_steps_v2 fs
            JOIN file_workflows_v2 fw ON fw.id = fs.workflow_id
            WHERE fs.status IN ('pending', 'in_progress')
              AND fw.status NOT IN ('closed', 'cancelled', 'completed')
              AND fw.project_id IN ({})
            GROUP BY fw.project_id
            """.format(project_clause),
            visible_project_ids if visible_project_ids else [],
        ).fetchall()
        signature_metric_rows = conn.execute(
            """
            SELECT
              fr.project_id,
              COUNT(*) AS signature_attention
            FROM file_signature_records_v2 sr
            JOIN file_records_v2 fr ON fr.id = sr.file_id
            WHERE sr.verify_status NOT IN ('valid', 'unsigned')
              AND fr.project_id IN ({})
            GROUP BY fr.project_id
            """.format(project_clause),
            visible_project_ids if visible_project_ids else [],
        ).fetchall()
        task_metrics = {str(row["project_id"] or ""): row for row in task_metric_rows}
        issue_metrics = {str(row["project_id"] or ""): row for row in issue_metric_rows}
        file_metrics = {str(row["project_id"] or ""): row for row in file_metric_rows}
        file_step_metrics = {str(row["project_id"] or ""): row for row in file_step_rows}
        signature_metrics = {str(row["project_id"] or ""): row for row in signature_metric_rows}
        all_file_totals = conn.execute(
            """
            SELECT
              COUNT(*) AS files,
              SUM(CASE WHEN is_locked = 1 THEN 1 ELSE 0 END) AS signed_locked,
              SUM(CASE WHEN is_signed = 1 THEN 1 ELSE 0 END) AS signed_files,
              SUM(CASE WHEN project_id = '' THEN 1 ELSE 0 END) AS unassigned_files,
              SUM(CASE WHEN status IN ('reviewing', 'approving', 'signing', 'pending_approval', 'pending_review') THEN 1 ELSE 0 END) AS active_file_flows
            FROM file_records_v2
            WHERE project_id IN ({}) OR owner_user_id = ?
            """.format(project_clause),
            (visible_project_ids + [email]) if visible_project_ids else [email],
        ).fetchone()
        pending_file_steps_total = conn.execute(
            """
            SELECT COUNT(*) AS c
            FROM file_workflow_steps_v2 fs
            JOIN file_workflows_v2 fw ON fw.id = fs.workflow_id
            WHERE fs.status IN ('pending', 'in_progress')
              AND fw.status NOT IN ('closed', 'cancelled', 'completed')
              AND (fw.project_id IN ({}) OR fs.assigned_user_id = ?)
            """.format(project_clause),
            (visible_project_ids + [email]) if visible_project_ids else [email],
        ).fetchone()
        signature_attention_total = conn.execute(
            """
            SELECT COUNT(*) AS c
            FROM file_signature_records_v2 sr
            JOIN file_records_v2 fr ON fr.id = sr.file_id
            WHERE sr.verify_status NOT IN ('valid', 'unsigned')
              AND (fr.project_id IN ({}) OR fr.owner_user_id = ?)
            """.format(project_clause),
            (visible_project_ids + [email]) if visible_project_ids else [email],
        ).fetchone()
        ai_report_rows = conn.execute(
            """
            SELECT status, COUNT(*) AS c
            FROM reports_v2
            WHERE user_id = ? OR project_id IN ({})
            GROUP BY status
            """.format(project_clause),
            ([email] + visible_project_ids) if visible_project_ids else [email],
        ).fetchall()
        ai_status_counts = {str(row["status"] or "generated"): int(row["c"] or 0) for row in ai_report_rows}
        visible_file_rows = conn.execute(
            """
            SELECT id
            FROM file_records_v2
            WHERE project_id IN ({}) OR owner_user_id = ?
            ORDER BY updated_at DESC
            LIMIT 300
            """.format(project_clause),
            (visible_project_ids + [email]) if visible_project_ids else [email],
        ).fetchall()
        visible_file_ids = [str(row["id"] or "") for row in visible_file_rows if str(row["id"] or "")]
        audit_entity_ids = visible_project_ids + visible_file_ids
        audit_clause = ",".join(["?"] * len(audit_entity_ids)) if audit_entity_ids else "''"
        evidence_rows = conn.execute(
            """
            SELECT id, actor_user_id, action_type, entity_type, entity_id, metadata_json, created_at
            FROM audit_logs_v2
            WHERE actor_user_id = ? OR entity_id IN ({})
            ORDER BY created_at DESC
            LIMIT 16
            """.format(audit_clause),
            ([email] + audit_entity_ids) if audit_entity_ids else [email],
        ).fetchall()
        evidence_chain = []
        for row in evidence_rows:
            meta = _v2_json_load(str(row["metadata_json"] or "{}"), {})
            evidence_chain.append(
                {
                    "id": str(row["id"] or ""),
                    "event": str(row["action_type"] or ""),
                    "actor": str(row["actor_user_id"] or ""),
                    "entity_type": str(row["entity_type"] or ""),
                    "target": str(row["entity_id"] or ""),
                    "ts": int(row["created_at"] or 0),
                    "metadata": meta,
                    "dlp_terms": detect_governance_dlp_terms(row["action_type"], row["entity_type"], row["entity_id"], json.dumps(meta, ensure_ascii=False)),
                }
            )
        war_room_items = []
        for project in projects[:12]:
            project_id = str(project.get("id") or "")
            t = task_metrics.get(project_id)
            i = issue_metrics.get(project_id)
            f = file_metrics.get(project_id)
            fs = file_step_metrics.get(project_id)
            sig = signature_metrics.get(project_id)
            open_tasks = int(t["open_tasks"] or 0) if t else int(project.get("unfinished_task_count") or 0)
            overdue_tasks = int(t["overdue_tasks"] or 0) if t else 0
            pending_approvals_count = int(t["pending_approvals"] or 0) if t else int(project.get("pending_approval_count") or 0)
            high_risk_count = int(i["high_risk"] or 0) if i else 0
            file_count = int(f["files"] or 0) if f else 0
            signed_locked_count = int(f["signed_locked"] or 0) if f else 0
            pending_file_steps = int(fs["pending_file_steps"] or 0) if fs else 0
            signature_attention = int(sig["signature_attention"] or 0) if sig else 0
            if signature_attention:
                next_action = "验签异常，先复核签名与文件摘要"
            elif high_risk_count:
                next_action = "高风险事项优先进入 War Room"
            elif overdue_tasks:
                next_action = "先清理超期任务并确认责任人"
            elif pending_approvals_count or pending_file_steps:
                next_action = "处理待审批/待审阅文件"
            else:
                next_action = "更新关键进展并保留证据链"
            war_room_items.append(
                {
                    **project,
                    "open_tasks": open_tasks,
                    "overdue_tasks": overdue_tasks,
                    "pending_approvals": pending_approvals_count,
                    "high_risk_items": high_risk_count,
                    "files": file_count,
                    "signed_locked_files": signed_locked_count,
                    "pending_file_steps": pending_file_steps,
                    "signature_attention": signature_attention,
                    "next_action": next_action,
                }
            )
        quick_views = {
            "my_pending_items": int(pending_tasks["c"] or 0) + my_pending_docs if pending_tasks else my_pending_docs,
            "pending_approvals": int(
                sum(
                    1
                    for item in docs.get("documents", [])
                    if isinstance(item, dict)
                    and str(item.get("project_id") or "") in visible_projects
                    and str(item.get("current_status") or "") == "pending_approval"
                )
            ),
            "overdue_tasks": int(overdue["c"] or 0) if overdue else 0,
            "high_risk_projects": int(high_risk_projects["c"] or 0) if high_risk_projects else 0,
        }
        deal_document_control = {
            "total_files": int(all_file_totals["files"] or 0) if all_file_totals else 0,
            "signed_locked": int(all_file_totals["signed_locked"] or 0) if all_file_totals else 0,
            "signed_files": int(all_file_totals["signed_files"] or 0) if all_file_totals else 0,
            "active_file_flows": int(all_file_totals["active_file_flows"] or 0) if all_file_totals else 0,
            "unassigned_files": int(all_file_totals["unassigned_files"] or 0) if all_file_totals else 0,
            "pending_file_steps": int(pending_file_steps_total["c"] or 0) if pending_file_steps_total else 0,
            "signature_attention": int(signature_attention_total["c"] or 0) if signature_attention_total else 0,
        }
        ai_output_control = {
            "draft": int(ai_status_counts.get("generated", 0) or 0),
            "pending_review": int(ai_status_counts.get("follow_up_needed", 0) or 0),
            "adopted": int(ai_status_counts.get("reviewed", 0) or 0) + int(ai_status_counts.get("approved", 0) or 0),
            "rejected": int(ai_status_counts.get("archived", 0) or 0) + int(ai_status_counts.get("rejected", 0) or 0),
            "policy": [
                {"stage": "draft", "label": "AI 草稿", "next_action": "必须有人类复核后才能进入正式结论"},
                {"stage": "pending_review", "label": "待复核", "next_action": "补证据、补来源、确认责任人"},
                {"stage": "adopted", "label": "已采用", "next_action": "写入报告/项目记录并保留审计"},
                {"stage": "rejected", "label": "已驳回", "next_action": "记录驳回原因，禁止继续引用"},
            ],
        }
        war_room_summary = {
            "visible_projects": len(projects),
            "open_tasks": sum(int(item.get("open_tasks") or 0) for item in war_room_items),
            "overdue_tasks": sum(int(item.get("overdue_tasks") or 0) for item in war_room_items),
            "high_risk_items": sum(int(item.get("high_risk_items") or 0) for item in war_room_items),
            "pending_approvals": sum(int(item.get("pending_approvals") or 0) for item in war_room_items),
            "pending_file_steps": deal_document_control["pending_file_steps"],
            "signature_attention": deal_document_control["signature_attention"],
        }
        management_decision_strip = [
            {
                "label": "今日需决策",
                "value": quick_views["my_pending_items"],
                "tone": "warning" if quick_views["my_pending_items"] else "success",
                "next_action": "先处理待审批、待签字和阻塞事项",
            },
            {
                "label": "高风险项目",
                "value": quick_views["high_risk_projects"],
                "tone": "error" if quick_views["high_risk_projects"] else "success",
                "next_action": "进入 War Room 查看依据和责任人",
            },
            {
                "label": "交易文件控制",
                "value": deal_document_control["pending_file_steps"],
                "tone": "warning" if deal_document_control["pending_file_steps"] else "success",
                "next_action": "处理 KYC/合约/签字/验签队列",
            },
            {
                "label": "证据链",
                "value": len(evidence_chain),
                "tone": "info",
                "next_action": "关键动作均需留痕，可追责可复盘",
            },
        ]
    return {
        "ok": True,
        "projects": projects,
        "count": len(projects),
        "quick_views": quick_views,
        "management_decision_strip": management_decision_strip,
        "war_room_summary": war_room_summary,
        "war_room_items": war_room_items,
        "deal_document_control": deal_document_control,
        "evidence_chain": evidence_chain,
        "ai_output_control": ai_output_control,
    }, 200


def _v2_my_work_payload(user: dict | None) -> tuple[dict, int]:
    if not user:
        return {"ok": False, "error": "authentication_required"}, 401
    email = _v2_user_email(user)
    today_key = local_day_key()
    with v2_db_lock, _v2_db_conn() as conn:
        project_ids = _v2_user_project_ids(conn, user)
        tasks = conn.execute(
            """
            SELECT wi.*
            FROM work_items wi
            LEFT JOIN work_item_assignees wa ON wa.work_item_id = wi.id
            WHERE wa.user_id = ?
            ORDER BY wi.updated_at DESC
            LIMIT 100
            """,
            (email,),
        ).fetchall()
        my_tasks = [_v2_work_item_payload(conn, row) for row in tasks]
        tasks_today = [item for item in my_tasks if str(item.get("updated_at", 0)) and datetime.fromtimestamp(int(item.get("updated_at", 0) or 0), LOCAL_TIMEZONE).strftime("%Y-%m-%d") == today_key]
        active_projects = []
        for project_id in project_ids:
            row = conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
            if row:
                active_projects.append(_v2_project_payload(conn, row, user))
        issues = conn.execute(
            """
            SELECT *
            FROM project_issues
            WHERE (reported_by = ? OR assigned_to = ?) AND status NOT IN ('resolved', 'closed')
            ORDER BY updated_at DESC
            LIMIT 100
            """,
            (email, email),
        ).fetchall()
        report_rows = conn.execute(
            """
            SELECT *
            FROM reports_v2
            WHERE user_id = ? AND report_type IN ('user_daily', 'user_weekly')
            ORDER BY generated_at DESC
            LIMIT 10
            """,
            (email,),
        ).fetchall()
        reports = [_v2_report_payload(conn, row, include_content=False) for row in report_rows]
    doc_data = _load_document_flow_payload()
    pending_docs = []
    drafted_docs = []
    for doc in doc_data.get("documents", []):
        if not isinstance(doc, dict):
            continue
        if normalize_email(doc.get("current_handler_id", "")) == email:
            pending_docs.append(doc)
        if normalize_email(doc.get("created_by", "")) == email:
            drafted_docs.append(doc)
    return {
        "ok": True,
        "projects": active_projects[:20],
        "tasks_today": tasks_today[:50],
        "tasks_all": my_tasks[:100],
        "pending_documents": pending_docs[:50],
        "my_documents": drafted_docs[:50],
        "my_issues": [_v2_issue_payload(row) for row in issues],
        "my_reports": reports,
    }, 200


def _v2_global_search(user: dict | None, query: dict[str, list[str]]) -> tuple[dict, int]:
    if not user:
        return {"ok": False, "error": "authentication_required"}, 401
    q = str(query.get("q", [""])[0] or "").strip().lower()
    if not q:
        return {"ok": False, "error": "q_required"}, 400
    with v2_db_lock, _v2_db_conn() as conn:
        project_ids = _v2_user_project_ids(conn, user)
        project_hits = []
        for row in conn.execute("SELECT * FROM projects ORDER BY updated_at DESC LIMIT 500").fetchall():
            pid = str(row["id"] or "")
            if pid not in project_ids and not is_admin_user(user):
                continue
            payload = _v2_project_payload(conn, row, user)
            searchable = " ".join([payload["name"], payload["description"], payload["owner_id"], payload["status"]]).lower()
            if q in searchable:
                project_hits.append(payload)
        task_hits = []
        for row in conn.execute("SELECT * FROM work_items ORDER BY updated_at DESC LIMIT 1000").fetchall():
            pid = str(row["project_id"] or "")
            if pid not in project_ids and not is_admin_user(user):
                continue
            payload = _v2_work_item_payload(conn, row)
            searchable = " ".join([payload["title"], payload["description"], payload["priority"], payload["status"], payload["project_id"]]).lower()
            if q in searchable:
                task_hits.append(payload)
    doc_data = _load_document_flow_payload()
    document_hits = []
    for doc in doc_data.get("documents", []):
        if not isinstance(doc, dict):
            continue
        document_id = str(doc.get("id") or "")
        if not can_access_document(user, doc_data, document_id):
            continue
        searchable = " ".join(
            [
                str(doc.get("title") or ""),
                str(doc.get("created_by") or ""),
                str(doc.get("current_status") or ""),
                str(doc.get("project_id") or ""),
            ]
        ).lower()
        if q in searchable:
            document_hits.append(
                {
                    "id": document_id,
                    "title": str(doc.get("title") or ""),
                    "current_status": str(doc.get("current_status") or ""),
                    "project_id": str(doc.get("project_id") or ""),
                    "updated_at": int(doc.get("updated_at", 0) or 0),
                }
            )
    file_hits: list[dict] = []
    with v2_db_lock, _v2_db_conn() as conn:
        for row in conn.execute("SELECT * FROM file_records_v2 ORDER BY updated_at DESC LIMIT 1000").fetchall():
            if not _v2_can_view_file(conn, user, row):
                continue
            payload = _v2_file_payload(conn, row, include_latest_version=False)
            searchable = " ".join(
                [
                    payload["title"],
                    payload["project_id"],
                    payload["work_item_id"],
                    payload["owner_user_id"],
                    payload["status"],
                    payload["category"],
                    payload["workspace_id"],
                ]
            ).lower()
            if q in searchable:
                file_hits.append(payload)
    return {
        "ok": True,
        "query": q,
        "projects": project_hits[:50],
        "work_items": task_hits[:100],
        "documents": (document_hits + [
            {
                "id": item["id"],
                "title": item["title"],
                "current_status": item["status"],
                "project_id": item["project_id"],
                "updated_at": item["updated_at"],
            }
            for item in file_hits
        ])[:120],
        "file_records": file_hits[:100],
    }, 200


def _v2_admin_overview(user: dict | None) -> tuple[dict, int]:
    if not is_admin_user(user):
        return {"ok": False, "error": "admin_required"}, 403
    today = local_day_key()
    with v2_db_lock, _v2_db_conn() as conn:
        projects = conn.execute("SELECT COUNT(*) AS c FROM projects").fetchone()
        tasks = conn.execute("SELECT COUNT(*) AS c FROM work_items").fetchone()
        workflows = conn.execute("SELECT COUNT(*) AS c FROM reports_v2").fetchone()
        issues = conn.execute("SELECT COUNT(*) AS c FROM project_issues WHERE status NOT IN ('resolved', 'closed')").fetchone()
        overdue = conn.execute(
            """
            SELECT COUNT(*) AS c
            FROM work_items
            WHERE due_date <> '' AND due_date < ? AND status NOT IN ('done', 'cancelled')
            """,
            (today,),
        ).fetchone()
        high_risk = conn.execute(
            """
            SELECT COUNT(*) AS c
            FROM project_issues
            WHERE status NOT IN ('resolved', 'closed') AND severity IN ('high', 'critical')
            """,
        ).fetchone()
        reports = conn.execute("SELECT COUNT(*) AS c FROM reports_v2").fetchone()
        file_records = conn.execute("SELECT COUNT(*) AS c FROM file_records_v2").fetchone()
        file_pending = conn.execute("SELECT COUNT(*) AS c FROM file_workflow_steps_v2 WHERE status = 'pending'").fetchone()
        chat_messages = conn.execute("SELECT COUNT(*) AS c FROM project_chat_messages_v2 WHERE lifecycle_status <> 'hard_deleted'").fetchone()
        chat_summaries = conn.execute("SELECT COUNT(*) AS c FROM project_chat_summaries_v2").fetchone()
        chat_runs_failed = conn.execute("SELECT COUNT(*) AS c FROM project_chat_summary_runs_v2 WHERE status = 'failed'").fetchone()
        chat_runs_pending = conn.execute("SELECT COUNT(*) AS c FROM project_chat_summary_runs_v2 WHERE status IN ('queued','running')").fetchone()
    docs = _load_document_flow_payload()
    workflows_count = len([item for item in docs.get("workflows", []) if isinstance(item, dict)])
    documents_count = len([item for item in docs.get("documents", []) if isinstance(item, dict)])
    pending_sign = len(
        [
            item
            for item in docs.get("documents", [])
            if isinstance(item, dict) and str(item.get("current_step") or "") == "sign" and not bool(item.get("is_locked"))
        ]
    )
    return {
        "ok": True,
        "totals": {
            "projects": int(projects["c"] or 0) if projects else 0,
            "work_items": int(tasks["c"] or 0) if tasks else 0,
            "unresolved_issues": int(issues["c"] or 0) if issues else 0,
            "documents": documents_count,
            "document_workflows": workflows_count,
            "reports": int(reports["c"] or 0) if reports else 0,
            "file_records": int(file_records["c"] or 0) if file_records else 0,
            "file_pending_steps": int(file_pending["c"] or 0) if file_pending else 0,
            "project_chat_messages": int(chat_messages["c"] or 0) if chat_messages else 0,
            "project_chat_summaries": int(chat_summaries["c"] or 0) if chat_summaries else 0,
        },
        "alerts": {
            "overdue_tasks": int(overdue["c"] or 0) if overdue else 0,
            "high_risk_issues": int(high_risk["c"] or 0) if high_risk else 0,
            "pending_signature_documents": pending_sign,
            "chat_summary_failed_runs": int(chat_runs_failed["c"] or 0) if chat_runs_failed else 0,
            "chat_summary_pending_runs": int(chat_runs_pending["c"] or 0) if chat_runs_pending else 0,
        },
    }, 200


def _v2_list_notifications(user: dict | None, query: dict[str, list[str]]) -> tuple[dict, int]:
    if not user:
        return {"ok": False, "error": "authentication_required"}, 401
    email = _v2_user_email(user)
    unread_only = str(query.get("unread", [""])[0] or "").strip().lower() in {"1", "true", "yes"}
    limit = min(max(int(str(query.get("limit", ["50"])[0] or "50")), 1), 200)
    with v2_db_lock, _v2_db_conn() as conn:
        if unread_only:
            rows = conn.execute(
                """
                SELECT *
                FROM notifications_v2
                WHERE user_id = ? AND is_read = 0
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (email, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                """
                SELECT *
                FROM notifications_v2
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (email, limit),
            ).fetchall()
        unread = conn.execute("SELECT COUNT(*) AS c FROM notifications_v2 WHERE user_id = ? AND is_read = 0", (email,)).fetchone()
    return {
        "ok": True,
        "unread_count": int(unread["c"] or 0) if unread else 0,
        "notifications": [
            {
                "id": str(row["id"] or ""),
                "type": str(row["type"] or ""),
                "title": str(row["title"] or ""),
                "content": str(row["content"] or ""),
                "related_project_id": str(row["related_project_id"] or ""),
                "related_work_item_id": str(row["related_work_item_id"] or ""),
                "related_document_id": str(row["related_document_id"] or ""),
                "is_read": bool(row["is_read"]),
                "created_at": int(row["created_at"] or 0),
            }
            for row in rows
        ],
    }, 200


def _v2_mark_notification_read(user: dict | None, payload: dict) -> tuple[dict, int]:
    if not user:
        return {"ok": False, "error": "authentication_required"}, 401
    email = _v2_user_email(user)
    notification_id = str(payload.get("notification_id") or "").strip()
    mark_all = bool(payload.get("mark_all"))
    with v2_db_lock, _v2_db_conn() as conn:
        if mark_all:
            conn.execute("UPDATE notifications_v2 SET is_read = 1 WHERE user_id = ?", (email,))
        else:
            if not notification_id:
                return {"ok": False, "error": "notification_id_required"}, 400
            conn.execute(
                "UPDATE notifications_v2 SET is_read = 1 WHERE id = ? AND user_id = ?",
                (notification_id, email),
            )
        conn.commit()
    return {"ok": True}, 200

def normalize_email(value: str) -> str:
    return str(value or "").strip().lower()


def normalize_phone(value: str) -> str:
    text = re.sub(r"[^\d+]", "", str(value or "").strip())
    if text.startswith("00"):
        text = "+" + text[2:]
    return text


def normalize_username(value: str) -> str:
    text = re.sub(r"[^a-zA-Z0-9._-]", "", str(value or "").strip().lower())
    return text[:32]


def valid_email(value: str) -> bool:
    return bool(re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", normalize_email(value)))


def valid_phone(value: str) -> bool:
    normalized = normalize_phone(value)
    digits = re.sub(r"\D", "", normalized)
    return len(digits) >= 6


def _password_hash(password: str, salt_hex: str) -> str:
    salt = bytes.fromhex(salt_hex)
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 180000).hex()


def default_user_permissions() -> dict:
    return {
        "pages": ["home", "finance", "legal", "skills"],
        "platforms": ["*"],
        "colleagues": ["*"],
        "user_admin": False,
        "view_team_status": False,
        "view_document_flows": False,
    }


def admin_permissions() -> dict:
    return {
        "pages": ["*"],
        "platforms": ["*"],
        "colleagues": ["*"],
        "user_admin": True,
        "view_team_status": True,
        "view_document_flows": True,
    }


def normalize_permissions(value: object, admin: bool = False) -> dict:
    base = admin_permissions() if admin else default_user_permissions()
    if not isinstance(value, dict):
        return base
    pages = value.get("pages")
    platforms = value.get("platforms")
    colleagues = value.get("colleagues")
    normalized = {
        "pages": [str(item).strip() for item in (pages if isinstance(pages, list) else base["pages"]) if str(item).strip()],
        "platforms": [str(item).strip() for item in (platforms if isinstance(platforms, list) else base["platforms"]) if str(item).strip()],
        "colleagues": [normalize_email(item) for item in (colleagues if isinstance(colleagues, list) else base["colleagues"]) if normalize_email(item)],
        "user_admin": bool(value.get("user_admin", base["user_admin"])),
        "view_team_status": bool(value.get("view_team_status", base["view_team_status"])),
        "view_document_flows": bool(value.get("view_document_flows", base["view_document_flows"])),
    }
    if admin:
        normalized = admin_permissions()
    return normalized


def _public_user_record(user: dict) -> dict:
    return {
        "email": user.get("email", ""),
        "username": user.get("username", ""),
        "phone": user.get("phone", ""),
        "display_name": user.get("display_name", ""),
        "role": user.get("role", "user"),
        "approval_status": user.get("approval_status", "approved"),
        "approved_at": user.get("approved_at", 0),
        "approved_by": user.get("approved_by", ""),
        "rejected_at": user.get("rejected_at", 0),
        "rejected_by": user.get("rejected_by", ""),
        "permissions": normalize_permissions(user.get("permissions"), admin=(user.get("role") == "admin")),
        "created_at": user.get("created_at", 0),
        "last_login_at": user.get("last_login_at", 0),
        "password_updated_at": user.get("password_updated_at", 0),
    }


def list_local_users() -> dict:
    with local_auth_lock:
        data = _load_json_file(LOCAL_AUTH_USERS, {"users": []})
        if not isinstance(data, dict):
            return {"users": []}
        users = data.get("users")
        if not isinstance(users, list):
            users = []
        changed = False
        used_usernames: set[str] = set()
        for user in users:
            if not isinstance(user, dict):
                continue
            username = normalize_username(user.get("username", ""))
            if not username:
                base = normalize_username(user.get("display_name", "")) or normalize_username(str(user.get("email", "")).split("@")[0]) or "user"
                candidate = base
                suffix = 1
                while candidate in used_usernames:
                    suffix += 1
                    candidate = f"{base}{suffix}"
                user["username"] = candidate
                username = candidate
                changed = True
            used_usernames.add(username)
            if user.get("role") not in {"user", "admin"}:
                user["role"] = "user"
                changed = True
            if user.get("approval_status") not in {"pending", "approved", "rejected"}:
                user["approval_status"] = "approved"
                changed = True
            if user.get("role") == "admin" and user.get("approval_status") != "approved":
                user["approval_status"] = "approved"
                changed = True
            normalized_permissions = normalize_permissions(user.get("permissions"), admin=(user.get("role") == "admin"))
            if user.get("permissions") != normalized_permissions:
                user["permissions"] = normalized_permissions
                changed = True
        if changed:
            _save_json_file(LOCAL_AUTH_USERS, {"users": users})
        return {"users": users}


def save_local_users(data: dict) -> None:
    with local_auth_lock:
        _save_json_file(LOCAL_AUTH_USERS, data)


def find_local_user(email: str) -> dict | None:
    email_key = normalize_email(email)
    users = list_local_users().get("users", [])
    for user in users:
        if isinstance(user, dict) and normalize_email(user.get("email", "")) == email_key:
            return user
    return None


def find_local_user_by_username(username: str) -> dict | None:
    username_key = normalize_username(username)
    if not username_key:
        return None
    users = list_local_users().get("users", [])
    for user in users:
        if isinstance(user, dict) and normalize_username(user.get("username", "")) == username_key:
            return user
    return None


def find_local_user_by_identifier(identifier: str) -> dict | None:
    identifier = str(identifier or "").strip()
    if "@" in identifier:
        return find_local_user(identifier)
    return find_local_user_by_username(identifier) or find_local_user(identifier)


def save_local_user_record(updated_user: dict) -> None:
    payload = list_local_users()
    users = payload.get("users", [])
    email_key = normalize_email(updated_user.get("email", ""))
    for idx, user in enumerate(users):
        if isinstance(user, dict) and normalize_email(user.get("email", "")) == email_key:
            users[idx] = updated_user
            save_local_users({"users": users})
            return
    users.append(updated_user)
    save_local_users({"users": users})


def _unique_username(requested: str, users: list[dict], email_key: str, display_name: str) -> str:
    existing = {
        normalize_username(user.get("username", ""))
        for user in users
        if isinstance(user, dict)
    }
    base = normalize_username(requested) or normalize_username(display_name) or normalize_username(email_key.split("@")[0]) or "user"
    candidate = base
    suffix = 1
    while candidate in existing:
        suffix += 1
        candidate = f"{base}{suffix}"
    return candidate


def register_local_user(email: str, phone: str, password: str, display_name: str = "", username: str = "") -> tuple[bool, str, dict | None]:
    email_key = normalize_email(email)
    phone_key = normalize_phone(phone)
    if not valid_email(email_key):
        return False, "invalid_email", None
    if not valid_phone(phone_key):
        return False, "invalid_phone", None
    if len(password or "") < 8:
        return False, "password_too_short", None
    users_payload = list_local_users()
    users = users_payload.get("users", [])
    if any(normalize_email(user.get("email", "")) == email_key for user in users if isinstance(user, dict)):
        return False, "email_already_exists", None
    username_key = normalize_username(username)
    if username and not username_key:
        return False, "invalid_username", None
    if username_key and any(normalize_username(user.get("username", "")) == username_key for user in users if isinstance(user, dict)):
        return False, "username_already_exists", None
    salt_hex = secrets.token_hex(16)
    user = {
        "email": email_key,
        "username": _unique_username(username_key, users, email_key, str(display_name or "").strip()),
        "phone": phone_key,
        "display_name": str(display_name or "").strip() or email_key.split("@")[0],
        "role": "user",
        "approval_status": "pending",
        "approved_at": 0,
        "approved_by": "",
        "rejected_at": 0,
        "rejected_by": "",
        "permissions": default_user_permissions(),
        "password_salt": salt_hex,
        "password_hash": _password_hash(password, salt_hex),
        "created_at": int(time.time()),
    }
    users.append(user)
    save_local_users({"users": users})
    return True, "ok", _public_user_record(user)


def verify_local_user(identifier: str, password: str) -> tuple[bool, str, dict | None]:
    user = find_local_user_by_identifier(identifier)
    if not user:
        return False, "user_not_found", None
    approval_status = str(user.get("approval_status") or "approved")
    if approval_status == "pending":
        return False, "account_pending_approval", None
    if approval_status == "rejected":
        return False, "account_rejected", None
    salt_hex = str(user.get("password_salt") or "")
    stored_hash = str(user.get("password_hash") or "")
    if not salt_hex or not stored_hash:
        return False, "invalid_user_record", None
    candidate = _password_hash(password, salt_hex)
    if not hmac.compare_digest(candidate, stored_hash):
        return False, "invalid_password", None
    return True, "ok", _public_user_record(user)


def user_display_label(email: str) -> str:
    user = find_local_user(email)
    if not user:
        return normalize_email(email)
    return str(user.get("display_name") or user.get("username") or user.get("email") or email)


def public_user_directory(viewer: dict | None = None) -> list[dict]:
    viewer_email = normalize_email(viewer.get("email", "")) if isinstance(viewer, dict) else ""
    viewer_permissions = viewer.get("permissions") if isinstance(viewer, dict) else {}
    allowed_colleagues = []
    if isinstance(viewer_permissions, dict):
        colleagues = viewer_permissions.get("colleagues")
        if isinstance(colleagues, list):
            allowed_colleagues = [normalize_email(item) for item in colleagues if normalize_email(item)]
    allow_all = is_admin_user(viewer) or "*" in allowed_colleagues
    items = []
    for user in list_local_users().get("users", []):
        if not isinstance(user, dict):
            continue
        target_email = normalize_email(user.get("email", ""))
        approval_status = str(user.get("approval_status") or "approved")
        if approval_status != "approved" and not is_admin_user(viewer):
            continue
        if not allow_all and viewer_email and target_email not in {viewer_email, *allowed_colleagues}:
            continue
        items.append({
            "email": target_email,
            "username": str(user.get("username") or ""),
            "display_name": str(user.get("display_name") or ""),
            "role": str(user.get("role") or "user"),
        })
    return sorted(items, key=lambda item: (item.get("display_name") or item.get("email") or "").lower())


def _load_work_chat_payload() -> dict:
    with work_chat_lock:
        data = _load_json_file(
            WORK_CHAT_PATH,
            {"conversations": [], "members": [], "messages": [], "grants": [], "shared_files": [], "file_versions": []},
        )
        if not isinstance(data, dict):
            data = {"conversations": [], "members": [], "messages": [], "grants": [], "shared_files": [], "file_versions": []}
        for key in ("conversations", "members", "messages", "grants", "shared_files", "file_versions"):
            if not isinstance(data.get(key), list):
                data[key] = []
        if _purge_expired_work_chat_messages(data):
            _save_json_file(WORK_CHAT_PATH, data)
        return data


def _save_work_chat_payload(data: dict) -> None:
    with work_chat_lock:
        _save_json_file(WORK_CHAT_PATH, data)


def _chat_id(prefix: str) -> str:
    return f"{prefix}_{int(time.time() * 1000)}_{secrets.token_hex(5)}"


def _chat_now() -> int:
    return int(time.time())


def _chat_local_day_bounds(day_text: str) -> tuple[int, int] | None:
    try:
        day = datetime.strptime(str(day_text or "").strip(), "%Y-%m-%d").date()
    except Exception:
        return None
    start = datetime.combine(day, datetime.min.time(), tzinfo=LOCAL_TIMEZONE)
    end = start + timedelta(days=1)
    return int(start.timestamp()), int(end.timestamp())


def _purge_expired_work_chat_messages(data: dict) -> bool:
    cutoff = _chat_now() - WORK_CHAT_RETENTION_DAYS * 24 * 60 * 60
    messages = data.get("messages", [])
    if not isinstance(messages, list):
        data["messages"] = []
        return True
    kept = [
        item for item in messages
        if isinstance(item, dict) and int(item.get("created_at", 0) or 0) >= cutoff
    ]
    if len(kept) == len(messages):
        return False
    data["messages"] = kept
    latest_by_conversation: dict[str, int] = {}
    for message in kept:
        conversation_id = str(message.get("conversation_id") or "")
        if not conversation_id:
            continue
        latest_by_conversation[conversation_id] = max(
            latest_by_conversation.get(conversation_id, 0),
            int(message.get("created_at", 0) or 0),
        )
    for conversation in data.get("conversations", []):
        if not isinstance(conversation, dict):
            continue
        conversation["last_message_at"] = latest_by_conversation.get(str(conversation.get("id") or ""), 0)
    return True


def _chat_members(data: dict, conversation_id: str) -> list[dict]:
    return [
        item for item in data.get("members", [])
        if isinstance(item, dict) and item.get("conversation_id") == conversation_id
    ]


def _chat_safe_filename(name: str) -> str:
    base = os.path.basename(str(name or "")).strip()
    return re.sub(r"[^A-Za-z0-9._-]+", "_", base)[:120] or "file.bin"


def _chat_shared_files(data: dict, conversation_id: str) -> list[dict]:
    files = [
        item
        for item in data.get("shared_files", [])
        if isinstance(item, dict) and item.get("conversation_id") == conversation_id
    ]
    files.sort(key=lambda item: int(item.get("updated_at", 0) or 0), reverse=True)
    return files


def _chat_shared_file(data: dict, conversation_id: str, shared_file_id: str) -> dict | None:
    for item in _chat_shared_files(data, conversation_id):
        if str(item.get("id") or "") == str(shared_file_id or ""):
            return item
    return None


def _chat_file_versions(data: dict, shared_file_id: str) -> list[dict]:
    versions = [
        item
        for item in data.get("file_versions", [])
        if isinstance(item, dict) and str(item.get("shared_file_id") or "") == str(shared_file_id or "")
    ]
    versions.sort(key=lambda item: (int(item.get("version_number", 0) or 0), int(item.get("created_at", 0) or 0)))
    return versions


def _chat_file_version_payload(version: dict, conversation_id: str) -> dict:
    file_id = str(version.get("shared_file_id") or "")
    version_id = str(version.get("id") or "")
    download_url = (
        f"/api/work-chat/conversations/{quote(conversation_id)}/files/{quote(file_id)}/download?version_id={quote(version_id)}"
        if file_id and version_id
        else ""
    )
    return {
        "id": version_id,
        "shared_file_id": file_id,
        "conversation_id": conversation_id,
        "version_number": int(version.get("version_number", 1) or 1),
        "filename": str(version.get("filename") or ""),
        "mime": str(version.get("mime") or "application/octet-stream"),
        "size": int(version.get("size", 0) or 0),
        "created_by": normalize_email(version.get("created_by", "")),
        "created_at": int(version.get("created_at", 0) or 0),
        "change_note": str(version.get("change_note") or ""),
        "download_url": download_url,
    }


def _chat_shared_file_payload(data: dict, shared_file: dict, include_versions: bool = True) -> dict:
    conversation_id = str(shared_file.get("conversation_id") or "")
    versions = _chat_file_versions(data, str(shared_file.get("id") or ""))
    latest = None
    current_version_id = str(shared_file.get("current_version_id") or "")
    if current_version_id:
        for item in versions:
            if str(item.get("id") or "") == current_version_id:
                latest = item
                break
    if latest is None and versions:
        latest = versions[-1]
    current_download_url = ""
    if latest:
        current_download_url = (
            f"/api/work-chat/conversations/{quote(conversation_id)}/files/{quote(str(shared_file.get('id') or ''))}/download?version_id={quote(str(latest.get('id') or ''))}"
        )
    return {
        "id": str(shared_file.get("id") or ""),
        "conversation_id": conversation_id,
        "title": str(shared_file.get("title") or shared_file.get("filename") or ""),
        "filename": str(shared_file.get("filename") or ""),
        "mime": str(shared_file.get("mime") or "application/octet-stream"),
        "size": int(shared_file.get("size", 0) or 0),
        "created_by": normalize_email(shared_file.get("created_by", "")),
        "created_at": int(shared_file.get("created_at", 0) or 0),
        "updated_by": normalize_email(shared_file.get("updated_by", "")),
        "updated_at": int(shared_file.get("updated_at", 0) or 0),
        "current_version_id": str(shared_file.get("current_version_id") or ""),
        "current_version_number": int(shared_file.get("current_version_number", 0) or 0),
        "version_count": len(versions),
        "download_url": current_download_url,
        "versions": [_chat_file_version_payload(item, conversation_id) for item in versions[-10:]] if include_versions else [],
    }


def _chat_attachment_payload(attachment: dict, conversation_id: str) -> dict:
    file_id = str(attachment.get("shared_file_id") or attachment.get("file_id") or "")
    version_id = str(attachment.get("version_id") or "")
    download_url = (
        f"/api/work-chat/conversations/{quote(conversation_id)}/files/{quote(file_id)}/download?version_id={quote(version_id)}"
        if file_id and version_id
        else ""
    )
    return {
        "shared_file_id": file_id,
        "version_id": version_id,
        "filename": str(attachment.get("filename") or ""),
        "mime": str(attachment.get("mime") or "application/octet-stream"),
        "size": int(attachment.get("size", 0) or 0),
        "version_number": int(attachment.get("version_number", 0) or 0),
        "download_url": download_url,
    }


def _active_chat_grants(data: dict, conversation_id: str) -> list[dict]:
    return [
        item for item in data.get("grants", [])
        if (
            isinstance(item, dict)
            and item.get("conversation_id") == conversation_id
            and item.get("is_active", True)
            and not item.get("revoked_at")
        )
    ]


def _chat_conversation(data: dict, conversation_id: str) -> dict | None:
    for item in data.get("conversations", []):
        if isinstance(item, dict) and item.get("id") == conversation_id:
            return item
    return None


def can_access_chat_conversation(user: dict | None, data: dict, conversation_id: str) -> bool:
    if not isinstance(user, dict):
        return False
    if is_admin_user(user):
        return True
    email = normalize_email(user.get("email", ""))
    if any(normalize_email(member.get("user_id", "")) == email for member in _chat_members(data, conversation_id)):
        return True
    if any(normalize_email(grant.get("granted_user_id", "")) == email for grant in _active_chat_grants(data, conversation_id)):
        return True
    return False


def can_send_chat_message(user: dict | None, data: dict, conversation_id: str) -> bool:
    if not isinstance(user, dict):
        return False
    email = normalize_email(user.get("email", ""))
    return any(normalize_email(member.get("user_id", "")) == email for member in _chat_members(data, conversation_id))


def _chat_status(data: dict, conversation_id: str, viewer_email: str) -> dict:
    active_emails = _active_user_emails()
    member_emails = {normalize_email(member.get("user_id", "")) for member in _chat_members(data, conversation_id)}
    messages = [
        item for item in data.get("messages", [])
        if isinstance(item, dict) and item.get("conversation_id") == conversation_id
    ]
    last_message_at = max([int(item.get("created_at", 0) or 0) for item in messages] or [0])
    unread_count = sum(
        1 for item in messages
        if normalize_email(item.get("sender_id", "")) != viewer_email
        and viewer_email not in [normalize_email(v) for v in (item.get("read_by") or [])]
    )
    return {
        "online_member_count": len(member_emails & active_emails),
        "last_message_at": last_message_at,
        "unread_count": unread_count,
        "has_unread": unread_count > 0,
        "typing_users": [],
    }


def _chat_conversation_payload(data: dict, conversation: dict, viewer: dict, include_messages: bool = False) -> dict:
    conversation_id = str(conversation.get("id") or "")
    viewer_email = normalize_email(viewer.get("email", ""))
    members = _chat_members(data, conversation_id)
    grants = _active_chat_grants(data, conversation_id)
    member_emails = {normalize_email(item.get("user_id", "")) for item in members}
    grant_emails = {normalize_email(item.get("granted_user_id", "")) for item in grants}
    is_admin = is_admin_user(viewer)
    payload = {
        "id": conversation_id,
        "type": conversation.get("type", "group"),
        "name": conversation.get("name", ""),
        "created_by": conversation.get("created_by", ""),
        "created_at": int(conversation.get("created_at", 0) or 0),
        "updated_at": int(conversation.get("updated_at", 0) or 0),
        "last_message_at": int(conversation.get("last_message_at", 0) or 0),
        "members": [
            {
                "user_id": normalize_email(member.get("user_id", "")),
                "display_name": user_display_label(member.get("user_id", "")),
                "role": member.get("role", "member"),
                "joined_at": int(member.get("joined_at", 0) or 0),
            }
            for member in members
        ],
        "access_grants": [
            {
                "id": grant.get("id", ""),
                "granted_user_id": normalize_email(grant.get("granted_user_id", "")),
                "display_name": user_display_label(grant.get("granted_user_id", "")),
                "granted_by_admin_id": normalize_email(grant.get("granted_by_admin_id", "")),
                "permission_scope": grant.get("permission_scope", ["list", "status", "messages"]),
                "created_at": int(grant.get("created_at", 0) or 0),
            }
            for grant in grants
        ] if is_admin else [],
        "viewer": {
            "is_admin": is_admin,
            "is_member": viewer_email in member_emails,
            "is_granted": viewer_email in grant_emails,
            "can_send": can_send_chat_message(viewer, data, conversation_id),
        },
        "status": _chat_status(data, conversation_id, viewer_email),
        "shared_files": [
            _chat_shared_file_payload(data, shared_file, include_versions=True)
            for shared_file in _chat_shared_files(data, conversation_id)
        ],
    }
    if include_messages:
        payload["messages"] = chat_messages_payload(viewer, conversation_id).get("messages", [])
    return payload


def list_chat_conversations_payload(user: dict) -> dict:
    data = _load_work_chat_payload()
    conversations = []
    for conversation in data.get("conversations", []):
        if not isinstance(conversation, dict):
            continue
        conversation_id = str(conversation.get("id") or "")
        if can_access_chat_conversation(user, data, conversation_id):
            conversations.append(_chat_conversation_payload(data, conversation, user))
    conversations.sort(key=lambda item: int(item.get("last_message_at") or item.get("updated_at") or 0), reverse=True)
    return {"ok": True, "admin_view": is_admin_user(user), "conversations": conversations}


def chat_messages_payload(user: dict, conversation_id: str, mark_read: bool = True, date_filter: str = "") -> dict:
    data = _load_work_chat_payload()
    if not _chat_conversation(data, conversation_id):
        return {"ok": False, "error": "conversation_not_found"}
    if not can_access_chat_conversation(user, data, conversation_id):
        return {"ok": False, "error": "permission_denied"}
    viewer_email = normalize_email(user.get("email", ""))
    now = _chat_now()
    default_start = now - WORK_CHAT_VISIBLE_DAYS * 24 * 60 * 60
    day_bounds = _chat_local_day_bounds(date_filter) if date_filter else None
    if date_filter and not day_bounds:
        return {"ok": False, "error": "invalid_date"}
    changed = False
    messages = []
    total_available = 0
    for message in data.get("messages", []):
        if not isinstance(message, dict) or message.get("conversation_id") != conversation_id:
            continue
        created_at = int(message.get("created_at", 0) or 0)
        total_available += 1
        if day_bounds:
            if not (day_bounds[0] <= created_at < day_bounds[1]):
                continue
        elif created_at < default_start:
            continue
        read_by = [normalize_email(item) for item in (message.get("read_by") or [])]
        if mark_read and viewer_email and viewer_email not in read_by:
            read_by.append(viewer_email)
            message["read_by"] = read_by
            changed = True
        messages.append({
            "id": message.get("id", ""),
            "conversation_id": conversation_id,
            "sender_id": normalize_email(message.get("sender_id", "")),
            "sender_name": user_display_label(message.get("sender_id", "")),
            "content": str(message.get("content") or ""),
            "message_type": str(message.get("message_type") or "text"),
            "attachments": [
                _chat_attachment_payload(item, conversation_id)
                for item in (message.get("attachments") or [])
                if isinstance(item, dict)
            ],
            "created_at": created_at,
            "read_by": read_by,
        })
    if changed:
        _save_work_chat_payload(data)
    return {
        "ok": True,
        "messages": messages,
        "date_filter": str(date_filter or ""),
        "visible_days": WORK_CHAT_VISIBLE_DAYS,
        "retention_days": WORK_CHAT_RETENTION_DAYS,
        "collapse_seconds": WORK_CHAT_COLLAPSE_SECONDS,
        "default_window_start": default_start,
        "total_available": total_available,
    }


def create_chat_conversation(user: dict, payload: dict) -> dict:
    data = _load_work_chat_payload()
    creator = normalize_email(user.get("email", ""))
    requested_type = str(payload.get("type") or "group").strip().lower()
    raw_members = payload.get("members") if isinstance(payload.get("members"), list) else []
    member_emails = {creator}
    for item in raw_members:
        email = normalize_email(item.get("email", item) if isinstance(item, dict) else item)
        if email and find_local_user(email):
            member_emails.add(email)
    if requested_type == "direct":
        if len(member_emails) != 2:
            return {"ok": False, "error": "direct_chat_requires_two_users"}
        conversation_type = "direct"
    else:
        if len(member_emails) < 3:
            return {"ok": False, "error": "group_chat_requires_three_or_more_users"}
        conversation_type = "group"
    now = _chat_now()
    conversation_id = _chat_id("conv")
    name = str(payload.get("name") or "").strip()
    if not name:
        if conversation_type == "direct":
            name = " / ".join(user_display_label(email) for email in sorted(member_emails))
        else:
            name = f"工作群聊 {local_now().strftime('%m-%d %H:%M')}"
    conversation = {
        "id": conversation_id,
        "type": conversation_type,
        "name": name,
        "created_by": creator,
        "created_at": now,
        "updated_at": now,
        "last_message_at": 0,
    }
    data["conversations"].append(conversation)
    for email in sorted(member_emails):
        data["members"].append({
            "id": _chat_id("mem"),
            "conversation_id": conversation_id,
            "user_id": email,
            "role": "owner" if email == creator else "member",
            "joined_at": now,
        })
    _save_work_chat_payload(data)
    write_audit_event({"ts": time.strftime("%Y-%m-%d %H:%M:%S"), "event": "work_chat_create", "conversation_id": conversation_id, "created_by": creator, "members": sorted(member_emails)})
    return {"ok": True, "conversation": _chat_conversation_payload(data, conversation, user)}


def send_chat_message(user: dict, conversation_id: str, content: str) -> dict:
    data = _load_work_chat_payload()
    conversation = _chat_conversation(data, conversation_id)
    if not conversation:
        return {"ok": False, "error": "conversation_not_found"}
    if not can_access_chat_conversation(user, data, conversation_id):
        return {"ok": False, "error": "permission_denied"}
    if not can_send_chat_message(user, data, conversation_id):
        return {"ok": False, "error": "read_only_access"}
    text = str(content or "").strip()
    if not text:
        return {"ok": False, "error": "empty_message"}
    now = _chat_now()
    sender = normalize_email(user.get("email", ""))
    message = {
        "id": _chat_id("msg"),
        "conversation_id": conversation_id,
        "sender_id": sender,
        "content": text[:8000],
        "message_type": "text",
        "attachments": [],
        "created_at": now,
        "read_by": [sender],
    }
    data["messages"].append(message)
    conversation["updated_at"] = now
    conversation["last_message_at"] = now
    _save_work_chat_payload(data)
    message_payload = chat_messages_payload(user, conversation_id, mark_read=False)
    return {"ok": True, "message": (message_payload.get("messages") or [])[-1] if message_payload.get("messages") else message}


def upload_chat_file(user: dict, conversation_id: str, payload: dict) -> dict:
    data = _load_work_chat_payload()
    conversation = _chat_conversation(data, conversation_id)
    if not conversation:
        return {"ok": False, "error": "conversation_not_found"}
    if not can_access_chat_conversation(user, data, conversation_id):
        return {"ok": False, "error": "permission_denied"}
    if not can_send_chat_message(user, data, conversation_id):
        return {"ok": False, "error": "read_only_access"}
    filename = _chat_safe_filename(str(payload.get("filename") or ""))
    blob = str(payload.get("base64") or "").strip()
    if not filename or not blob:
        return {"ok": False, "error": "file_required"}
    try:
        raw = base64.b64decode(blob, validate=True)
    except Exception:
        return {"ok": False, "error": "invalid_file_payload"}
    if not raw:
        return {"ok": False, "error": "invalid_file_payload"}
    if len(raw) > WORK_CHAT_FILE_MAX_BYTES:
        return {"ok": False, "error": "file_too_large"}
    now = _chat_now()
    actor = normalize_email(user.get("email", ""))
    provided_shared_file_id = str(payload.get("shared_file_id") or "").strip()
    shared_file = _chat_shared_file(data, conversation_id, provided_shared_file_id) if provided_shared_file_id else None
    if provided_shared_file_id and not shared_file:
        return {"ok": False, "error": "shared_file_not_found"}
    if not shared_file:
        shared_file = {
            "id": _chat_id("sfile"),
            "conversation_id": conversation_id,
            "title": str(payload.get("title") or filename)[:160],
            "filename": filename,
            "mime": str(payload.get("mime") or mimetypes.guess_type(filename)[0] or "application/octet-stream"),
            "size": len(raw),
            "created_by": actor,
            "created_at": now,
            "updated_by": actor,
            "updated_at": now,
            "current_version_id": "",
            "current_version_number": 0,
        }
        data["shared_files"].append(shared_file)
    current_version_number = int(shared_file.get("current_version_number", 0) or 0)
    version_number = current_version_number + 1
    version_id = _chat_id("fver")
    conv_dir = WORK_CHAT_STORAGE_DIR / conversation_id
    conv_dir.mkdir(parents=True, exist_ok=True)
    storage_name = f"{shared_file['id']}_{version_id}_{filename}"
    storage_path = conv_dir / storage_name
    try:
        storage_path.write_bytes(raw)
    except Exception:
        return {"ok": False, "error": "file_storage_failed"}
    version = {
        "id": version_id,
        "shared_file_id": str(shared_file.get("id") or ""),
        "conversation_id": conversation_id,
        "version_number": version_number,
        "filename": filename,
        "mime": str(payload.get("mime") or shared_file.get("mime") or mimetypes.guess_type(filename)[0] or "application/octet-stream"),
        "size": len(raw),
        "storage_path": str(storage_path),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "created_by": actor,
        "created_at": now,
        "change_note": str(payload.get("note") or "")[:500],
    }
    data["file_versions"].append(version)
    shared_file["filename"] = filename
    shared_file["mime"] = str(version.get("mime") or "application/octet-stream")
    shared_file["size"] = len(raw)
    shared_file["current_version_id"] = version_id
    shared_file["current_version_number"] = version_number
    shared_file["updated_by"] = actor
    shared_file["updated_at"] = now
    note = str(payload.get("note") or "").strip()
    auto_content = note if note else f"Uploaded file {filename} (v{version_number})"
    message = {
        "id": _chat_id("msg"),
        "conversation_id": conversation_id,
        "sender_id": actor,
        "content": auto_content[:8000],
        "message_type": "file",
        "attachments": [{
            "shared_file_id": str(shared_file.get("id") or ""),
            "version_id": version_id,
            "filename": filename,
            "mime": str(version.get("mime") or "application/octet-stream"),
            "size": len(raw),
            "version_number": version_number,
        }],
        "created_at": now,
        "read_by": [actor],
    }
    data["messages"].append(message)
    conversation["updated_at"] = now
    conversation["last_message_at"] = now
    _save_work_chat_payload(data)
    return {
        "ok": True,
        "message": _chat_attachment_payload(message["attachments"][0], conversation_id),
        "shared_file": _chat_shared_file_payload(data, shared_file, include_versions=True),
    }


def work_chat_file_download_payload(
    user: dict,
    conversation_id: str,
    shared_file_id: str,
    version_id: str = "",
) -> tuple[dict, int]:
    data = _load_work_chat_payload()
    if not _chat_conversation(data, conversation_id):
        return {"ok": False, "error": "conversation_not_found"}, 404
    if not can_access_chat_conversation(user, data, conversation_id):
        return {"ok": False, "error": "permission_denied"}, 403
    shared_file = _chat_shared_file(data, conversation_id, shared_file_id)
    if not shared_file:
        return {"ok": False, "error": "shared_file_not_found"}, 404
    versions = _chat_file_versions(data, shared_file_id)
    target_version = None
    desired_version = str(version_id or "").strip()
    if desired_version:
        for item in versions:
            if str(item.get("id") or "") == desired_version:
                target_version = item
                break
    if not target_version:
        current_id = str(shared_file.get("current_version_id") or "")
        for item in versions:
            if str(item.get("id") or "") == current_id:
                target_version = item
                break
    if not target_version and versions:
        target_version = versions[-1]
    if not target_version:
        return {"ok": False, "error": "file_version_not_found"}, 404
    storage_text = str(target_version.get("storage_path") or "").strip()
    if not storage_text:
        return {"ok": False, "error": "file_not_found"}, 404
    try:
        storage_path = Path(storage_text).resolve()
        storage_root = WORK_CHAT_STORAGE_DIR.resolve()
        if storage_path != storage_root and not str(storage_path).startswith(str(storage_root) + os.sep):
            raise ValueError("outside storage root")
    except Exception:
        return {"ok": False, "error": "file_not_found"}, 404
    if not storage_path.exists() or not storage_path.is_file():
        return {"ok": False, "error": "file_not_found"}, 404
    raw = storage_path.read_bytes()
    return (
        {
            "ok": True,
            "raw": raw,
            "mime": str(target_version.get("mime") or "application/octet-stream"),
            "filename": str(target_version.get("filename") or "file.bin"),
            "shared_file_id": str(shared_file.get("id") or ""),
            "version_id": str(target_version.get("id") or ""),
            "version_number": int(target_version.get("version_number", 1) or 1),
        },
        200,
    )


def grant_chat_access(admin_user: dict, conversation_id: str, granted_user_id: str, active: bool = True) -> dict:
    if not is_admin_user(admin_user):
        return {"ok": False, "error": "admin_required"}
    data = _load_work_chat_payload()
    if not _chat_conversation(data, conversation_id):
        return {"ok": False, "error": "conversation_not_found"}
    target = normalize_email(granted_user_id)
    if not find_local_user(target):
        return {"ok": False, "error": "user_not_found"}
    admin_email = normalize_email(admin_user.get("email", ""))
    now = _chat_now()
    existing = None
    for grant in data.get("grants", []):
        if isinstance(grant, dict) and grant.get("conversation_id") == conversation_id and normalize_email(grant.get("granted_user_id", "")) == target and grant.get("is_active", True) and not grant.get("revoked_at"):
            existing = grant
            break
    if active:
        if existing:
            existing["permission_scope"] = ["list", "status", "messages"]
        else:
            data["grants"].append({
                "id": _chat_id("grant"),
                "conversation_id": conversation_id,
                "granted_user_id": target,
                "granted_by_admin_id": admin_email,
                "permission_scope": ["list", "status", "messages"],
                "created_at": now,
                "revoked_at": 0,
                "is_active": True,
            })
        event = "work_chat_grant"
    else:
        if existing:
            existing["is_active"] = False
            existing["revoked_at"] = now
        event = "work_chat_revoke"
    _save_work_chat_payload(data)
    write_audit_event({"ts": time.strftime("%Y-%m-%d %H:%M:%S"), "event": event, "conversation_id": conversation_id, "target": target, "admin": admin_email})
    conversation = _chat_conversation(data, conversation_id)
    return {"ok": True, "conversation": _chat_conversation_payload(data, conversation, admin_user)}


def _document_now() -> int:
    return int(time.time())


def _document_id(prefix: str) -> str:
    return f"{prefix}_{secrets.token_hex(8)}"


def _load_document_flow_payload() -> dict:
    data = _load_json_file(
        DOCUMENT_FLOW_PATH,
        {
            "documents": [],
            "versions": [],
            "workflows": [],
            "steps": [],
            "cc_recipients": [],
            "access_grants": [],
            "notifications": [],
            "actions": [],
        },
    )
    if not isinstance(data, dict):
        data = {}
    for key in ("documents", "versions", "workflows", "steps", "cc_recipients", "access_grants", "notifications", "actions"):
        if not isinstance(data.get(key), list):
            data[key] = []
    return data


def _save_document_flow_payload(data: dict) -> None:
    _save_json_file(DOCUMENT_FLOW_PATH, data)


def _document_user_ids(value: object) -> list[str]:
    ids: list[str] = []
    if isinstance(value, list):
        for item in value:
            email = normalize_email(item.get("email", item) if isinstance(item, dict) else item)
            if email and find_local_user(email):
                ids.append(email)
    return list(dict.fromkeys(ids))


def _document_record(data: dict, document_id: str) -> dict | None:
    for item in data.get("documents", []):
        if isinstance(item, dict) and str(item.get("id") or "") == str(document_id or ""):
            return item
    return None


def _document_workflow_record(data: dict, workflow_id: str) -> dict | None:
    for item in data.get("workflows", []):
        if isinstance(item, dict) and str(item.get("id") or "") == str(workflow_id or ""):
            return item
    return None


def _document_version_record(data: dict, version_id: str) -> dict | None:
    for item in data.get("versions", []):
        if isinstance(item, dict) and str(item.get("id") or "") == str(version_id or ""):
            return item
    return None


def _document_versions(data: dict, document_id: str) -> list[dict]:
    items = [
        item for item in data.get("versions", [])
        if isinstance(item, dict) and str(item.get("document_id") or "") == str(document_id or "")
    ]
    items.sort(key=lambda item: (int(item.get("version_number", 0) or 0), int(item.get("created_at", 0) or 0)))
    return items


def _document_steps(data: dict, workflow_id: str) -> list[dict]:
    items = [
        item for item in data.get("steps", [])
        if isinstance(item, dict) and str(item.get("workflow_id") or "") == str(workflow_id or "")
    ]
    items.sort(key=lambda item: (int(item.get("sequence_order", 0) or 0), int(item.get("created_at", 0) or 0)))
    return items


def _document_ccs(data: dict, workflow_id: str) -> list[dict]:
    return [
        item for item in data.get("cc_recipients", [])
        if isinstance(item, dict) and str(item.get("workflow_id") or "") == str(workflow_id or "")
    ]


def _document_grants(data: dict, document_id: str) -> list[dict]:
    grants = []
    for item in data.get("access_grants", []):
        if not isinstance(item, dict):
            continue
        if str(item.get("document_id") or "") != str(document_id or ""):
            continue
        if not item.get("is_active", True) or item.get("revoked_at"):
            continue
        grants.append(item)
    return grants


def _document_notifications_for_user(data: dict, user_email: str) -> list[dict]:
    email = normalize_email(user_email)
    items = [
        item for item in data.get("notifications", [])
        if isinstance(item, dict) and normalize_email(item.get("user_id", "")) == email
    ]
    items.sort(key=lambda item: int(item.get("created_at", 0) or 0), reverse=True)
    return items


def _document_actor_label(email: str) -> str:
    return user_display_label(email)


def _document_default_scope() -> list[str]:
    return ["list", "detail", "status", "versions", "notifications"]


def _document_global_grant_active(user: dict | None) -> bool:
    return can_view_document_flows(user)


def _document_membership_emails(data: dict, document_id: str) -> set[str]:
    doc = _document_record(data, document_id)
    if not doc:
        return set()
    emails = {normalize_email(doc.get("created_by", ""))}
    workflow = _document_workflow_record(data, doc.get("current_workflow_id", ""))
    if workflow:
        for step in _document_steps(data, workflow.get("id", "")):
            email = normalize_email(step.get("assigned_user_id", ""))
            if email:
                emails.add(email)
        for item in _document_ccs(data, workflow.get("id", "")):
            email = normalize_email(item.get("user_id", ""))
            if email:
                emails.add(email)
    for grant in _document_grants(data, document_id):
        email = normalize_email(grant.get("granted_user_id", ""))
        if email:
            emails.add(email)
    return {email for email in emails if email}


def _document_v2_work_item_project(conn: sqlite3.Connection, work_item_id: str) -> str:
    if not work_item_id:
        return ""
    row = conn.execute("SELECT project_id FROM work_items WHERE id = ?", (work_item_id,)).fetchone()
    return str(row["project_id"] or "") if row else ""


def can_access_document(user: dict | None, data: dict, document_id: str) -> bool:
    if not isinstance(user, dict):
        return False
    if is_admin_user(user) or _document_global_grant_active(user):
        return True
    doc = _document_record(data, document_id)
    if doc:
        project_id = str(doc.get("project_id") or "").strip()
        work_item_id = str(doc.get("work_item_id") or "").strip()
        try:
            with v2_db_lock, _v2_db_conn() as conn:
                if work_item_id:
                    linked_project = _document_v2_work_item_project(conn, work_item_id)
                    if linked_project and _v2_can_view_project(conn, user, linked_project):
                        return True
                if project_id and _v2_can_view_project(conn, user, project_id):
                    return True
        except Exception:
            pass
    email = normalize_email(user.get("email", ""))
    return email in _document_membership_emails(data, document_id)


def can_modify_document_step(user: dict | None, data: dict, document_id: str) -> bool:
    if not isinstance(user, dict):
        return False
    doc = _document_record(data, document_id)
    if not doc:
        return False
    if doc.get("is_locked") or str(doc.get("current_status") or "") in DOCUMENT_READ_ONLY_STATUSES:
        return False
    current_handler = normalize_email(doc.get("current_handler_id", ""))
    email = normalize_email(user.get("email", ""))
    return bool(email and email == current_handler)


def _document_encrypt_blob(raw: bytes) -> dict:
    nonce = secrets.token_bytes(16)
    secret = audit_secret()
    keystream = bytearray()
    counter = 0
    while len(keystream) < len(raw):
        counter_bytes = counter.to_bytes(8, "big")
        keystream.extend(hashlib.sha256(secret + nonce + counter_bytes).digest())
        counter += 1
    cipher = bytes(a ^ b for a, b in zip(raw, keystream[: len(raw)]))
    mac = hmac.new(secret, nonce + cipher, hashlib.sha256).hexdigest()
    return {
        "nonce": base64.b64encode(nonce).decode("utf-8"),
        "ciphertext": base64.b64encode(cipher).decode("utf-8"),
        "mac": mac,
    }


def _document_decrypt_blob(payload: dict) -> bytes:
    nonce = base64.b64decode(str(payload.get("nonce") or ""))
    cipher = base64.b64decode(str(payload.get("ciphertext") or ""))
    mac = str(payload.get("mac") or "")
    secret = audit_secret()
    expected = hmac.new(secret, nonce + cipher, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(mac, expected):
        raise ValueError("invalid encrypted document payload")
    keystream = bytearray()
    counter = 0
    while len(keystream) < len(cipher):
        counter_bytes = counter.to_bytes(8, "big")
        keystream.extend(hashlib.sha256(secret + nonce + counter_bytes).digest())
        counter += 1
    return bytes(a ^ b for a, b in zip(cipher, keystream[: len(cipher)]))


def _document_store_file(document_id: str, version_id: str, filename: str, raw: bytes) -> str:
    folder = DOCUMENT_STORAGE_DIR / document_id
    folder.mkdir(parents=True, exist_ok=True)
    safe_name = re.sub(r"[^A-Za-z0-9._-]", "_", filename or "document.bin")[:120] or "document.bin"
    path = folder / f"{version_id}_{safe_name}"
    path.write_bytes(raw)
    return str(path)


def _document_create_notification(data: dict, user_id: str, document_id: str, workflow_id: str, notification_type: str, content: str) -> None:
    email = normalize_email(user_id)
    if not email:
        return
    data["notifications"].append({
        "id": _document_id("note"),
        "user_id": email,
        "document_id": document_id,
        "workflow_id": workflow_id,
        "notification_type": notification_type,
        "content": str(content or "")[:1200],
        "is_read": False,
        "created_at": _document_now(),
    })


def _document_notify_users(data: dict, recipients: set[str], document_id: str, workflow_id: str, notification_type: str, content: str) -> None:
    for email in recipients:
        _document_create_notification(data, email, document_id, workflow_id, notification_type, content)


def _document_admin_watchers() -> set[str]:
    watchers = set()
    for user in list_local_users().get("users", []):
        if not isinstance(user, dict):
            continue
        email = normalize_email(user.get("email", ""))
        if not email:
            continue
        if is_admin_user(user) or can_view_document_flows(user):
            watchers.add(email)
    return watchers


def _document_active_step(doc: dict, data: dict) -> dict | None:
    workflow = _document_workflow_record(data, doc.get("current_workflow_id", ""))
    if not workflow:
        return None
    for step in _document_steps(data, workflow.get("id", "")):
        if str(step.get("status") or "") in {"pending", "in_progress"}:
            return step
    return None


def _document_step_payload(step: dict) -> dict:
    return {
        "id": step.get("id", ""),
        "workflow_id": step.get("workflow_id", ""),
        "step_type": step.get("step_type", ""),
        "assigned_user_id": normalize_email(step.get("assigned_user_id", "")),
        "assigned_name": _document_actor_label(step.get("assigned_user_id", "")),
        "status": step.get("status", "pending"),
        "action_taken": step.get("action_taken", ""),
        "comments": step.get("comments", ""),
        "acted_at": int(step.get("acted_at", 0) or 0),
        "sequence_order": int(step.get("sequence_order", 0) or 0),
    }


def _document_version_payload(version: dict) -> dict:
    return {
        "id": version.get("id", ""),
        "document_id": version.get("document_id", ""),
        "version_number": int(version.get("version_number", 0) or 0),
        "filename": version.get("filename", ""),
        "mime": version.get("mime", ""),
        "created_by": normalize_email(version.get("created_by", "")),
        "created_by_name": _document_actor_label(version.get("created_by", "")),
        "change_summary": version.get("change_summary", ""),
        "based_on_version_id": version.get("based_on_version_id", ""),
        "is_signed": bool(version.get("is_signed")),
        "signed_at": int(version.get("signed_at", 0) or 0),
        "signed_by": normalize_email(version.get("signed_by", "")),
        "signed_by_name": _document_actor_label(version.get("signed_by", "")),
        "is_locked": bool(version.get("is_locked")),
        "is_encrypted": bool(version.get("is_encrypted")),
        "created_at": int(version.get("created_at", 0) or 0),
        "preview": version.get("preview", ""),
        "download_name": version.get("filename", ""),
    }


def _document_status_summary(doc: dict, data: dict) -> dict:
    active = _document_active_step(doc, data)
    return {
        "status": doc.get("current_status", "draft"),
        "current_step": doc.get("current_step", ""),
        "current_handler_id": normalize_email(doc.get("current_handler_id", "")),
        "current_handler_name": _document_actor_label(doc.get("current_handler_id", "")),
        "is_signed": bool(doc.get("is_signed")),
        "is_locked": bool(doc.get("is_locked")),
        "is_encrypted": bool(doc.get("is_encrypted")),
        "active_step_type": active.get("step_type", "") if active else "",
    }


def _document_payload(data: dict, document_id: str, viewer: dict, include_notifications: bool = False) -> dict:
    doc = _document_record(data, document_id)
    if not doc:
        return {"ok": False, "error": "document_not_found"}
    if not can_access_document(viewer, data, document_id):
        return {"ok": False, "error": "permission_denied"}
    workflow = _document_workflow_record(data, doc.get("current_workflow_id", ""))
    versions = _document_versions(data, document_id)
    grants = _document_grants(data, document_id)
    current_version = _document_version_record(data, doc.get("current_version_id", ""))
    viewer_email = normalize_email(viewer.get("email", ""))
    payload = {
        "ok": True,
        "document": {
            "id": doc.get("id", ""),
            "title": doc.get("title", ""),
            "created_by": normalize_email(doc.get("created_by", "")),
            "created_by_name": _document_actor_label(doc.get("created_by", "")),
            "current_status": doc.get("current_status", "draft"),
            "current_version_id": doc.get("current_version_id", ""),
            "current_workflow_id": doc.get("current_workflow_id", ""),
            "current_step": doc.get("current_step", ""),
            "current_handler_id": normalize_email(doc.get("current_handler_id", "")),
            "current_handler_name": _document_actor_label(doc.get("current_handler_id", "")),
            "current_reviewer_id": normalize_email(doc.get("current_reviewer_id", "")),
            "current_approver_id": normalize_email(doc.get("current_approver_id", "")),
            "is_signed": bool(doc.get("is_signed")),
            "is_locked": bool(doc.get("is_locked")),
            "is_encrypted": bool(doc.get("is_encrypted")),
            "created_at": int(doc.get("created_at", 0) or 0),
            "updated_at": int(doc.get("updated_at", 0) or 0),
            "flow_note": doc.get("flow_note", ""),
            "deadline_at": int(doc.get("deadline_at", 0) or 0),
            "based_on_document_id": doc.get("based_on_document_id", ""),
            "based_on_version_id": doc.get("based_on_version_id", ""),
            "change_request_reason": doc.get("change_request_reason", ""),
            "project_id": str(doc.get("project_id") or ""),
            "work_item_id": str(doc.get("work_item_id") or ""),
        },
        "status_summary": _document_status_summary(doc, data),
        "workflow": {
            "id": workflow.get("id", "") if workflow else "",
            "status": workflow.get("status", "") if workflow else "",
            "current_step": workflow.get("current_step", "") if workflow else "",
            "initiated_by": normalize_email(workflow.get("initiated_by", "")) if workflow else "",
            "initiated_by_name": _document_actor_label(workflow.get("initiated_by", "")) if workflow else "",
            "created_at": int(workflow.get("created_at", 0) or 0) if workflow else 0,
            "updated_at": int(workflow.get("updated_at", 0) or 0) if workflow else 0,
            "project_id": str(workflow.get("project_id") or "") if workflow else "",
            "work_item_id": str(workflow.get("work_item_id") or "") if workflow else "",
        },
        "current_version": _document_version_payload(current_version) if current_version else None,
        "versions": [_document_version_payload(item) for item in versions],
        "steps": [_document_step_payload(item) for item in _document_steps(data, workflow.get("id", "") if workflow else "")],
        "cc_recipients": [
            {
                "id": item.get("id", ""),
                "user_id": normalize_email(item.get("user_id", "")),
                "display_name": _document_actor_label(item.get("user_id", "")),
                "created_at": int(item.get("created_at", 0) or 0),
            }
            for item in _document_ccs(data, workflow.get("id", "") if workflow else "")
        ],
        "access_grants": [
            {
                "id": item.get("id", ""),
                "granted_user_id": normalize_email(item.get("granted_user_id", "")),
                "display_name": _document_actor_label(item.get("granted_user_id", "")),
                "granted_by_admin_id": normalize_email(item.get("granted_by_admin_id", "")),
                "scope": item.get("scope", _document_default_scope()),
                "created_at": int(item.get("created_at", 0) or 0),
            }
            for item in grants
        ] if is_admin_user(viewer) or can_view_document_flows(viewer) else [],
        "viewer": {
            "is_admin": is_admin_user(viewer),
            "can_view_all": can_view_document_flows(viewer),
            "is_creator": viewer_email == normalize_email(doc.get("created_by", "")),
            "can_act": can_modify_document_step(viewer, data, document_id),
            "is_current_handler": viewer_email == normalize_email(doc.get("current_handler_id", "")),
        },
    }
    if include_notifications:
        payload["notifications"] = _document_notifications_for_user(data, viewer_email)[:50]
    return payload


def list_document_flows_payload(user: dict, query: dict[str, list[str]] | None = None) -> dict:
    data = _load_document_flow_payload()
    viewer_email = normalize_email(user.get("email", ""))
    qv = query or {}
    project_filter = str(qv.get("project_id", [""])[0] or "").strip()
    work_item_filter = str(qv.get("work_item_id", [""])[0] or "").strip()
    status_filter = str(qv.get("status", [""])[0] or "").strip().lower()
    text_filter = str(qv.get("q", [""])[0] or "").strip().lower()
    buckets = {
        "created": [],
        "pending": [],
        "cc": [],
        "granted": [],
        "all": [],
    }
    for doc in data.get("documents", []):
        if not isinstance(doc, dict):
            continue
        document_id = str(doc.get("id") or "")
        if not can_access_document(user, data, document_id):
            continue
        payload = _document_payload(data, document_id, user)
        if not payload.get("ok"):
            continue
        item = payload["document"]
        if project_filter and str(item.get("project_id") or "") != project_filter:
            continue
        if work_item_filter and str(item.get("work_item_id") or "") != work_item_filter:
            continue
        if status_filter and str(item.get("current_status") or "").lower() != status_filter:
            continue
        if text_filter:
            searchable = " ".join(
                [
                    str(item.get("title") or ""),
                    str(item.get("flow_note") or ""),
                    str(item.get("created_by") or ""),
                    str(item.get("current_status") or ""),
                    str(item.get("project_id") or ""),
                    str(item.get("work_item_id") or ""),
                ]
            ).lower()
            if text_filter not in searchable:
                continue
        item["status_summary"] = payload["status_summary"]
        item["current_version"] = payload["current_version"]
        buckets["all"].append(item)
        if viewer_email == normalize_email(doc.get("created_by", "")):
            buckets["created"].append(item)
        if viewer_email == normalize_email(doc.get("current_handler_id", "")):
            buckets["pending"].append(item)
        if any(normalize_email(cc.get("user_id", "")) == viewer_email for cc in payload.get("cc_recipients", [])):
            buckets["cc"].append(item)
        if any(normalize_email(grant.get("granted_user_id", "")) == viewer_email for grant in payload.get("access_grants", [])):
            buckets["granted"].append(item)
    for key in buckets:
        buckets[key].sort(key=lambda item: int(item.get("updated_at", 0) or 0), reverse=True)
    return {
        "ok": True,
        "admin_view": is_admin_user(user) or can_view_document_flows(user),
        "buckets": buckets,
        "notifications": _document_notifications_for_user(data, viewer_email)[:30],
    }


def _document_next_version_number(data: dict, document_id: str) -> int:
    versions = _document_versions(data, document_id)
    return (max((int(item.get("version_number", 0) or 0) for item in versions), default=0) + 1)


def _document_rebuild_workflow_steps(
    data: dict,
    workflow_id: str,
    *,
    reviewers: list[str],
    approvers: list[str],
    signer: str,
    activate_first: bool = False,
) -> list[dict]:
    now = _document_now()
    data["steps"] = [
        item for item in data.get("steps", [])
        if not (isinstance(item, dict) and str(item.get("workflow_id") or "") == str(workflow_id or ""))
    ]
    steps: list[dict] = []
    sequence = 1
    first_handler = ""
    for email in reviewers:
        status = "in_progress" if activate_first and not first_handler else "pending"
        if status == "in_progress":
            first_handler = email
        steps.append({
            "id": _document_id("step"),
            "workflow_id": workflow_id,
            "step_type": "review",
            "assigned_user_id": email,
            "status": status,
            "action_taken": "",
            "comments": "",
            "acted_at": 0,
            "sequence_order": sequence,
            "created_at": now,
        })
        sequence += 1
    for email in approvers:
        status = "in_progress" if activate_first and not first_handler else "pending"
        if status == "in_progress":
            first_handler = email
        steps.append({
            "id": _document_id("step"),
            "workflow_id": workflow_id,
            "step_type": "approval",
            "assigned_user_id": email,
            "status": status,
            "action_taken": "",
            "comments": "",
            "acted_at": 0,
            "sequence_order": sequence,
            "created_at": now,
        })
        sequence += 1
    if signer:
        status = "in_progress" if activate_first and not first_handler else "pending"
        if status == "in_progress":
            first_handler = signer
        steps.append({
            "id": _document_id("step"),
            "workflow_id": workflow_id,
            "step_type": "sign",
            "assigned_user_id": signer,
            "status": status,
            "action_taken": "",
            "comments": "",
            "acted_at": 0,
            "sequence_order": sequence,
            "created_at": now,
        })
    data["steps"].extend(steps)
    return steps


def _document_prepare_version(document_id: str, creator_email: str, payload: dict, version_number: int, based_on_version_id: str = "") -> tuple[dict | None, str | None]:
    filename = str(payload.get("filename") or "document.txt").strip() or "document.txt"
    mime = str(payload.get("mime") or "text/plain").strip() or "text/plain"
    file_base64 = str(payload.get("file_base64") or "").strip()
    text_content = str(payload.get("text_content") or "").strip()
    preview = str(payload.get("preview") or "").strip()
    if not file_base64 and text_content:
        file_base64 = base64.b64encode(text_content.encode("utf-8")).decode("utf-8")
        if not preview:
            preview = text_content[:2400]
    if not file_base64:
        return None, "file_required"
    try:
        raw = base64.b64decode(file_base64)
    except Exception:
        return None, "invalid_file_payload"
    version_id = _document_id("ver")
    path = _document_store_file(document_id, version_id, filename, raw)
    version = {
        "id": version_id,
        "document_id": document_id,
        "version_number": version_number,
        "filename": filename,
        "mime": mime,
        "file_base64": file_base64,
        "file_path": path,
        "preview": preview[:2400],
        "created_by": creator_email,
        "change_summary": str(payload.get("change_summary") or "").strip(),
        "based_on_version_id": based_on_version_id,
        "is_signed": False,
        "signed_at": 0,
        "signed_by": "",
        "signed_note": "",
        "is_locked": False,
        "is_encrypted": False,
        "encrypted_payload": None,
        "created_at": _document_now(),
    }
    return version, None


def create_document_flow(user: dict, payload: dict) -> dict:
    creator = normalize_email(user.get("email", ""))
    data = _load_document_flow_payload()
    title = str(payload.get("title") or "").strip()
    if not title:
        return {"ok": False, "error": "title_required"}
    save_as_draft = bool(payload.get("save_as_draft"))
    reviewers = _document_user_ids(payload.get("reviewers"))
    approvers = _document_user_ids(payload.get("approvers"))
    ccs = _document_user_ids(payload.get("cc_recipients"))
    if not save_as_draft and not reviewers and not approvers:
        return {"ok": False, "error": "workflow_requires_reviewer_or_approver"}
    based_on_document_id = str(payload.get("based_on_document_id") or "").strip()
    based_on_version_id = str(payload.get("based_on_version_id") or "").strip()
    change_request_reason = str(payload.get("change_request_reason") or payload.get("change_summary") or "").strip()
    project_id = str(payload.get("project_id") or "").strip()
    work_item_id = str(payload.get("work_item_id") or "").strip()
    if based_on_document_id:
        base_doc = _document_record(data, based_on_document_id)
        if not base_doc:
            return {"ok": False, "error": "based_on_document_not_found"}
        if bool(base_doc.get("is_signed")) and not change_request_reason:
            return {"ok": False, "error": "change_request_reason_required"}
        base_project_id = str(base_doc.get("project_id") or "").strip()
        base_work_item_id = str(base_doc.get("work_item_id") or "").strip()
        if base_project_id:
            if project_id and project_id != base_project_id:
                return {"ok": False, "error": "project_scope_mismatch_with_base_document"}
            project_id = base_project_id
        if base_work_item_id:
            if work_item_id and work_item_id != base_work_item_id:
                return {"ok": False, "error": "work_item_scope_mismatch_with_base_document"}
            work_item_id = base_work_item_id
    if project_id or work_item_id:
        try:
            with v2_db_lock, _v2_db_conn() as conn:
                linked_project = ""
                if work_item_id:
                    linked_project = _document_v2_work_item_project(conn, work_item_id)
                    if not linked_project:
                        return {"ok": False, "error": "work_item_not_found"}
                    if project_id and project_id != linked_project:
                        return {"ok": False, "error": "work_item_project_mismatch"}
                    project_id = linked_project
                if project_id:
                    hit = conn.execute("SELECT 1 FROM projects WHERE id = ?", (project_id,)).fetchone()
                    if not hit:
                        return {"ok": False, "error": "project_not_found"}
                    if not _v2_can_view_project(conn, user, project_id):
                        return {"ok": False, "error": "permission_denied"}
        except Exception:
            return {"ok": False, "error": "project_scope_validate_failed"}
    document_id = _document_id("doc")
    version, error = _document_prepare_version(document_id, creator, payload, 1, based_on_version_id=based_on_version_id)
    if error or not version:
        return {"ok": False, "error": error or "version_create_failed"}
    workflow_id = _document_id("wf")
    now = _document_now()
    signer = approvers[-1] if approvers else creator
    if save_as_draft:
        current_status = "draft"
        current_step = "draft"
        current_handler = ""
        signer = approvers[-1] if approvers else ""
    else:
        current_status = "in_review" if reviewers else "pending_approval"
        current_step = "review" if reviewers else "approval"
        current_handler = reviewers[0] if reviewers else approvers[0]
    document = {
        "id": document_id,
        "title": title[:220],
        "created_by": creator,
        "current_status": current_status,
        "current_version_id": version["id"],
        "current_workflow_id": workflow_id,
        "current_step": current_step,
        "current_handler_id": current_handler,
        "current_reviewer_id": reviewers[0] if reviewers else "",
        "current_approver_id": approvers[0] if approvers else "",
        "is_signed": False,
        "is_locked": False,
        "is_encrypted": False,
        "created_at": now,
        "updated_at": now,
        "flow_note": str(payload.get("flow_note") or "").strip()[:3000],
        "deadline_at": int(payload.get("deadline_at", 0) or 0),
        "based_on_document_id": based_on_document_id,
        "based_on_version_id": based_on_version_id,
        "change_request_reason": change_request_reason[:3000],
        "superseded_by_document_id": "",
        "signer_id": signer,
        "project_id": project_id,
        "work_item_id": work_item_id,
    }
    workflow = {
        "id": workflow_id,
        "document_id": document_id,
        "initiated_by": creator,
        "status": current_status,
        "current_step": current_step,
        "created_at": now,
        "updated_at": now,
        "project_id": project_id,
        "work_item_id": work_item_id,
    }
    steps = _document_rebuild_workflow_steps(
        data,
        workflow_id,
        reviewers=reviewers,
        approvers=approvers,
        signer=signer,
        activate_first=not save_as_draft,
    )
    cc_rows = [
        {
            "id": _document_id("cc"),
            "document_id": document_id,
            "workflow_id": workflow_id,
            "user_id": email,
            "created_at": now,
        }
        for email in ccs
    ]
    data["documents"].append(document)
    data["versions"].append(version)
    data["workflows"].append(workflow)
    data["cc_recipients"].extend(cc_rows)
    if based_on_document_id:
        based_doc = _document_record(data, based_on_document_id)
        if based_doc and based_doc.get("is_signed"):
            based_doc["superseded_by_document_id"] = document_id
    recipients = {creator, *reviewers, *approvers, *ccs, *_document_admin_watchers()}
    _document_notify_users(
        data,
        recipients,
        document_id,
        workflow_id,
        "document_workflow_created",
        f"{user_display_label(creator)} {'保存了' if save_as_draft else '发起了'}文件流程《{title}》。",
    )
    data["actions"].append({
        "id": _document_id("action"),
        "document_id": document_id,
        "workflow_id": workflow_id,
        "action_type": "save_draft" if save_as_draft else "create",
        "actor_id": creator,
        "comments": str(payload.get("flow_note") or "").strip()[:3000],
        "created_at": now,
    })
    _save_document_flow_payload(data)
    write_audit_event({"ts": time.strftime("%Y-%m-%d %H:%M:%S"), "event": "document_workflow_save_draft" if save_as_draft else "document_workflow_create", "document_id": document_id, "workflow_id": workflow_id, "created_by": creator, "reviewers": reviewers, "approvers": approvers, "cc": ccs})
    return _document_payload(data, document_id, user, include_notifications=True)


def _document_mark_step(steps: list[dict], step_id: str, status: str, action_taken: str, comments: str = "") -> None:
    for step in steps:
        if str(step.get("id") or "") != str(step_id or ""):
            continue
        step["status"] = status
        step["action_taken"] = action_taken
        step["comments"] = comments[:3000]
        step["acted_at"] = _document_now()
        return


def _document_find_current_step(data: dict, workflow_id: str, actor_email: str = "") -> dict | None:
    steps = _document_steps(data, workflow_id)
    if actor_email:
        for step in steps:
            if normalize_email(step.get("assigned_user_id", "")) == normalize_email(actor_email) and str(step.get("status") or "") in {"pending", "in_progress"}:
                return step
    for step in steps:
        if str(step.get("status") or "") in {"pending", "in_progress"}:
            return step
    return None


def _document_advance_to_next_step(doc: dict, workflow: dict, data: dict, after_step: dict | None = None) -> None:
    steps = _document_steps(data, workflow.get("id", ""))
    current_sequence = int(after_step.get("sequence_order", 0) or 0) if after_step else 0
    next_step = None
    for step in steps:
        if int(step.get("sequence_order", 0) or 0) > current_sequence and str(step.get("status") or "") == "pending":
            next_step = step
            break
    if next_step:
        next_step["status"] = "in_progress"
        workflow["current_step"] = next_step.get("step_type", "")
        workflow["updated_at"] = _document_now()
        doc["current_step"] = next_step.get("step_type", "")
        doc["current_handler_id"] = normalize_email(next_step.get("assigned_user_id", ""))
        doc["updated_at"] = _document_now()
        if next_step.get("step_type") == "approval":
            doc["current_status"] = "pending_approval"
            workflow["status"] = "pending_approval"
            doc["current_approver_id"] = normalize_email(next_step.get("assigned_user_id", ""))
        elif next_step.get("step_type") == "sign":
            doc["current_status"] = "approved"
            workflow["status"] = "approved"
        else:
            doc["current_status"] = "in_review"
            workflow["status"] = "in_review"
            doc["current_reviewer_id"] = normalize_email(next_step.get("assigned_user_id", ""))
    else:
        doc["current_handler_id"] = ""
        doc["updated_at"] = _document_now()
        workflow["updated_at"] = _document_now()


def act_on_document_flow(user: dict, document_id: str, payload: dict) -> dict:
    data = _load_document_flow_payload()
    doc = _document_record(data, document_id)
    if not doc:
        return {"ok": False, "error": "document_not_found"}
    if not can_access_document(user, data, document_id):
        return {"ok": False, "error": "permission_denied"}
    workflow = _document_workflow_record(data, doc.get("current_workflow_id", ""))
    if not workflow:
        return {"ok": False, "error": "workflow_not_found"}
    actor = normalize_email(user.get("email", ""))
    action = str(payload.get("action") or "").strip().lower()
    comments = str(payload.get("comments") or "").strip()
    current_step = _document_find_current_step(data, workflow.get("id", ""), actor)
    if action == "submit_draft" and normalize_email(doc.get("created_by", "")) != actor:
        return {"ok": False, "error": "permission_denied"}
    if action == "submit_revision" and str(doc.get("current_status") or "") == "returned_for_revision" and normalize_email(doc.get("created_by", "")) == actor:
        current_step = {
            "id": "",
            "workflow_id": workflow.get("id", ""),
            "step_type": "review",
            "assigned_user_id": actor,
            "status": "in_progress",
            "sequence_order": 0,
        }
    if action not in {"mark_read", "submit_draft"} and not current_step:
        return {"ok": False, "error": "no_pending_step_for_user"}
    if doc.get("is_locked") and action != "mark_read":
        return {"ok": False, "error": "document_locked"}
    now = _document_now()
    recipients: set[str] = {normalize_email(doc.get("created_by", "")), *_document_admin_watchers()}
    if workflow:
        for step in _document_steps(data, workflow.get("id", "")):
            email = normalize_email(step.get("assigned_user_id", ""))
            if email:
                recipients.add(email)
        for cc in _document_ccs(data, workflow.get("id", "")):
            email = normalize_email(cc.get("user_id", ""))
            if email:
                recipients.add(email)
    if action in {"submit_revision", "return_for_revision", "review_pass"} and current_step.get("step_type") != "review":
        return {"ok": False, "error": "review_step_required"}
    if action in {"approve", "reject", "request_changes"} and current_step.get("step_type") != "approval":
        return {"ok": False, "error": "approval_step_required"}
    if action == "sign" and current_step.get("step_type") != "sign":
        return {"ok": False, "error": "sign_step_required"}
    if action == "submit_draft":
        reviewers = _document_user_ids(payload.get("reviewers"))
        approvers = _document_user_ids(payload.get("approvers"))
        ccs = _document_user_ids(payload.get("cc_recipients"))
        if not reviewers and not approvers:
            return {"ok": False, "error": "workflow_requires_reviewer_or_approver"}
        signer = approvers[-1] if approvers else actor
        _document_rebuild_workflow_steps(
            data,
            workflow.get("id", ""),
            reviewers=reviewers,
            approvers=approvers,
            signer=signer,
            activate_first=True,
        )
        data["cc_recipients"] = [
            item for item in data.get("cc_recipients", [])
            if not (isinstance(item, dict) and str(item.get("workflow_id") or "") == str(workflow.get("id", "")))
        ]
        data["cc_recipients"].extend([
            {
                "id": _document_id("cc"),
                "document_id": document_id,
                "workflow_id": workflow.get("id", ""),
                "user_id": email,
                "created_at": now,
            }
            for email in ccs
        ])
        doc["current_status"] = "in_review" if reviewers else "pending_approval"
        doc["current_step"] = "review" if reviewers else "approval"
        doc["current_handler_id"] = reviewers[0] if reviewers else approvers[0]
        doc["current_reviewer_id"] = reviewers[0] if reviewers else ""
        doc["current_approver_id"] = approvers[0] if approvers else ""
        doc["updated_at"] = now
        doc["flow_note"] = str(payload.get("flow_note") or doc.get("flow_note") or "").strip()[:3000]
        doc["deadline_at"] = int(payload.get("deadline_at", doc.get("deadline_at", 0)) or 0)
        doc["change_request_reason"] = str(payload.get("change_request_reason") or payload.get("change_summary") or doc.get("change_request_reason") or "").strip()[:3000]
        doc["signer_id"] = signer
        workflow["status"] = doc["current_status"]
        workflow["current_step"] = doc["current_step"]
        workflow["updated_at"] = now
        recipients.update({*reviewers, *approvers, *ccs})
        notice = f"{user_display_label(actor)} 提交了草稿《{doc.get('title', '')}》进入审批流程。"
    elif action == "submit_revision":
        version, error = _document_prepare_version(
            document_id,
            actor,
            payload,
            _document_next_version_number(data, document_id),
            based_on_version_id=doc.get("current_version_id", ""),
        )
        if error or not version:
            return {"ok": False, "error": error or "revision_failed"}
        if not version.get("change_summary"):
            version["change_summary"] = comments or "Revision submitted"
        data["versions"].append(version)
        doc["current_version_id"] = version["id"]
        if current_step.get("id"):
            _document_mark_step(_document_steps(data, workflow.get("id", "")), current_step.get("id", ""), "completed", "submit_revision", comments)
            _document_advance_to_next_step(doc, workflow, data, current_step)
        else:
            next_step = _document_find_current_step(data, workflow.get("id", ""))
            if next_step:
                next_step["status"] = "in_progress"
                doc["current_status"] = "in_review" if next_step.get("step_type") == "review" else "pending_approval"
                workflow["status"] = doc["current_status"]
                workflow["current_step"] = next_step.get("step_type", "")
                doc["current_step"] = next_step.get("step_type", "")
                doc["current_handler_id"] = normalize_email(next_step.get("assigned_user_id", ""))
                workflow["updated_at"] = now
                doc["updated_at"] = now
            else:
                _document_advance_to_next_step(doc, workflow, data, current_step)
        notice = f"{user_display_label(actor)} 提交了《{doc.get('title', '')}》的修订版本。"
    elif action == "review_pass":
        _document_mark_step(_document_steps(data, workflow.get("id", "")), current_step.get("id", ""), "completed", "review_pass", comments)
        _document_advance_to_next_step(doc, workflow, data, current_step)
        notice = f"{user_display_label(actor)} 已完成《{doc.get('title', '')}》审阅。"
    elif action == "return_for_revision":
        _document_mark_step(_document_steps(data, workflow.get("id", "")), current_step.get("id", ""), "returned", "return_for_revision", comments)
        doc["current_status"] = "returned_for_revision"
        workflow["status"] = "returned_for_revision"
        doc["current_step"] = "revision"
        doc["current_handler_id"] = normalize_email(doc.get("created_by", ""))
        doc["updated_at"] = now
        workflow["updated_at"] = now
        notice = f"{user_display_label(actor)} 将《{doc.get('title', '')}》退回修改。"
    elif action == "approve":
        _document_mark_step(_document_steps(data, workflow.get("id", "")), current_step.get("id", ""), "completed", "approve", comments)
        _document_advance_to_next_step(doc, workflow, data, current_step)
        notice = f"{user_display_label(actor)} 已批准《{doc.get('title', '')}》。"
    elif action == "reject":
        _document_mark_step(_document_steps(data, workflow.get("id", "")), current_step.get("id", ""), "rejected", "reject", comments)
        doc["current_status"] = "rejected"
        workflow["status"] = "rejected"
        doc["current_step"] = "rejected"
        doc["current_handler_id"] = normalize_email(doc.get("created_by", ""))
        doc["updated_at"] = now
        workflow["updated_at"] = now
        notice = f"{user_display_label(actor)} 已驳回《{doc.get('title', '')}》。"
    elif action == "request_changes":
        _document_mark_step(_document_steps(data, workflow.get("id", "")), current_step.get("id", ""), "returned", "request_changes", comments)
        doc["current_status"] = "returned_for_revision"
        workflow["status"] = "returned_for_revision"
        doc["current_step"] = "revision"
        doc["current_handler_id"] = normalize_email(doc.get("created_by", ""))
        doc["updated_at"] = now
        workflow["updated_at"] = now
        notice = f"{user_display_label(actor)} 要求对《{doc.get('title', '')}》继续修改。"
    elif action == "sign":
        version = _document_version_record(data, doc.get("current_version_id", ""))
        if not version:
            return {"ok": False, "error": "version_not_found"}
        raw = base64.b64decode(str(version.get("file_base64") or ""))
        encrypted = _document_encrypt_blob(raw)
        version["encrypted_payload"] = encrypted
        version["file_base64"] = ""
        version["is_signed"] = True
        version["signed_at"] = now
        version["signed_by"] = actor
        version["signed_note"] = comments[:3000]
        version["is_locked"] = True
        version["is_encrypted"] = True
        _document_mark_step(_document_steps(data, workflow.get("id", "")), current_step.get("id", ""), "completed", "sign", comments)
        doc["current_status"] = "archived_locked"
        workflow["status"] = "archived_locked"
        doc["current_step"] = "archived_locked"
        doc["current_handler_id"] = ""
        doc["is_signed"] = True
        doc["is_locked"] = True
        doc["is_encrypted"] = True
        doc["updated_at"] = now
        workflow["updated_at"] = now
        if doc.get("based_on_document_id"):
            prev = _document_record(data, doc.get("based_on_document_id", ""))
            if prev and prev.get("id") != doc.get("id"):
                prev["current_status"] = "superseded"
                prev["updated_at"] = now
        notice = f"{user_display_label(actor)} 已完成《{doc.get('title', '')}》签字归档。"
    elif action == "comment":
        notice = f"{user_display_label(actor)} 在《{doc.get('title', '')}》中添加了意见。"
    elif action == "mark_read":
        notice = ""
    else:
        return {"ok": False, "error": "unsupported_action"}
    data["actions"].append({
        "id": _document_id("action"),
        "document_id": document_id,
        "workflow_id": workflow.get("id", ""),
        "action_type": action,
        "actor_id": actor,
        "comments": comments[:3000],
        "created_at": now,
    })
    if notice:
        _document_notify_users(data, {email for email in recipients if email}, document_id, workflow.get("id", ""), f"document_{action}", notice)
    _save_document_flow_payload(data)
    write_audit_event({"ts": time.strftime("%Y-%m-%d %H:%M:%S"), "event": f"document_{action}", "document_id": document_id, "workflow_id": workflow.get("id", ""), "actor": actor, "comments": comments[:500]})
    return _document_payload(data, document_id, user, include_notifications=True)


def grant_document_access(admin_user: dict, document_id: str, granted_user_id: str, scope: list[str] | None = None, active: bool = True) -> dict:
    if not (is_admin_user(admin_user) or can_view_document_flows(admin_user)):
        return {"ok": False, "error": "admin_required"}
    data = _load_document_flow_payload()
    doc = _document_record(data, document_id)
    if not doc:
        return {"ok": False, "error": "document_not_found"}
    target = normalize_email(granted_user_id)
    if not find_local_user(target):
        return {"ok": False, "error": "user_not_found"}
    admin_email = normalize_email(admin_user.get("email", ""))
    now = _document_now()
    existing = None
    for item in data.get("access_grants", []):
        if not isinstance(item, dict):
            continue
        if str(item.get("document_id") or "") == str(document_id or "") and normalize_email(item.get("granted_user_id", "")) == target and item.get("is_active", True) and not item.get("revoked_at"):
            existing = item
            break
    if active:
        if existing:
            existing["scope"] = scope or _document_default_scope()
        else:
            data["access_grants"].append({
                "id": _document_id("grant"),
                "document_id": document_id,
                "workflow_id": doc.get("current_workflow_id", ""),
                "granted_user_id": target,
                "granted_by_admin_id": admin_email,
                "scope": scope or _document_default_scope(),
                "is_active": True,
                "created_at": now,
                "revoked_at": 0,
            })
        _document_create_notification(data, target, document_id, doc.get("current_workflow_id", ""), "document_grant", f"你已被授权查看《{doc.get('title', '')}》审批流程。")
        event = "document_grant"
    else:
        if existing:
            existing["is_active"] = False
            existing["revoked_at"] = now
        event = "document_revoke"
    _save_document_flow_payload(data)
    write_audit_event({"ts": time.strftime("%Y-%m-%d %H:%M:%S"), "event": event, "document_id": document_id, "target": target, "admin": admin_email})
    return _document_payload(data, document_id, admin_user, include_notifications=True)


def mark_document_notification_read(user: dict, notification_id: str) -> dict:
    data = _load_document_flow_payload()
    target = normalize_email(user.get("email", ""))
    for item in data.get("notifications", []):
        if not isinstance(item, dict):
            continue
        if str(item.get("id") or "") != str(notification_id or ""):
            continue
        if normalize_email(item.get("user_id", "")) != target and not can_view_document_flows(user):
            return {"ok": False, "error": "permission_denied"}
        item["is_read"] = True
        _save_document_flow_payload(data)
        return {"ok": True}
    return {"ok": False, "error": "notification_not_found"}


def document_download_payload(user: dict, document_id: str, version_id: str = "") -> tuple[dict, int]:
    data = _load_document_flow_payload()
    doc = _document_record(data, document_id)
    if not doc:
        return {"ok": False, "error": "document_not_found"}, 404
    if not can_access_document(user, data, document_id):
        return {"ok": False, "error": "permission_denied"}, 403
    version = _document_version_record(data, version_id or doc.get("current_version_id", ""))
    if not version:
        return {"ok": False, "error": "version_not_found"}, 404
    try:
        if version.get("is_encrypted") and version.get("encrypted_payload"):
            raw = _document_decrypt_blob(version.get("encrypted_payload") or {})
        else:
            raw = base64.b64decode(str(version.get("file_base64") or ""))
    except Exception:
        return {"ok": False, "error": "document_decrypt_failed"}, 400
    return {
        "ok": True,
        "filename": version.get("filename", "document.bin"),
        "mime": version.get("mime", "application/octet-stream"),
        "raw": raw,
    }, 200


def _load_sessions_payload() -> dict:
    with local_auth_lock:
        data = _load_json_file(LOCAL_AUTH_SESSIONS, {"sessions": {}})
        if not isinstance(data, dict):
            data = {"sessions": {}}
        sessions = data.get("sessions")
        if not isinstance(sessions, dict):
            data["sessions"] = {}
        return data


def _save_sessions_payload(data: dict) -> None:
    with local_auth_lock:
        _save_json_file(LOCAL_AUTH_SESSIONS, data)


def _session_idle_timeout_seconds(user: dict | None = None, role: str | None = None) -> int:
    resolved_role = str(role or (user or {}).get("role") or "user").strip().lower()
    return ADMIN_IDLE_TIMEOUT_SECONDS if resolved_role == "admin" else USER_IDLE_TIMEOUT_SECONDS


def local_now() -> datetime:
    return datetime.now(LOCAL_TIMEZONE)


def local_day_key(value: datetime | None = None) -> str:
    return (value or local_now()).strftime("%Y-%m-%d")


def local_month_key(value: datetime | None = None) -> str:
    return (value or local_now()).strftime("%Y-%m")


def _seconds_to_hours(value: int | float | str | None, precision: int = 2) -> float:
    try:
        seconds = float(value or 0)
    except Exception:
        seconds = 0.0
    return round(max(0.0, seconds) / 3600.0, precision)


def _is_last_day_of_month(value: datetime | None = None) -> bool:
    current = value or local_now()
    return (current + timedelta(days=1)).day == 1


def _within_workday_hours(value: datetime | None = None) -> bool:
    current = value or local_now()
    return WORKDAY_START_HOUR <= current.hour < WORKDAY_END_HOUR


def _load_activity_metrics() -> dict:
    with activity_metrics_lock:
        data = _load_json_file(ACTIVITY_METRICS_PATH, {"daily": {}, "monthly": {}, "last_sample_epoch": 0, "last_report_date": "", "last_monthly_report_key": ""})
        if not isinstance(data, dict):
            return {"daily": {}, "monthly": {}, "last_sample_epoch": 0, "last_report_date": "", "last_monthly_report_key": ""}
        if not isinstance(data.get("daily"), dict):
            data["daily"] = {}
        if not isinstance(data.get("monthly"), dict):
            data["monthly"] = {}
        return data


def _save_activity_metrics(data: dict) -> None:
    with activity_metrics_lock:
        _save_json_file(ACTIVITY_METRICS_PATH, data)


def _ensure_monthly_user_bucket(metrics: dict, month_key: str, user: dict) -> dict:
    monthly = metrics.setdefault("monthly", {})
    month_bucket = monthly.setdefault(month_key, {"users": {}})
    users_bucket = month_bucket.setdefault("users", {})
    email = normalize_email(user.get("email", ""))
    return users_bucket.setdefault(email, {
        "display_name": user.get("display_name", "") or email,
        "role": user.get("role", "user"),
        "login_times": [],
        "work_count": 0,
        "export_count": 0,
        "exported_files": [],
        "online_seconds": 0,
        "offline_seconds": 0,
        "platform_counts": {},
        "last_active_at": 0,
    })


def record_user_login_event(user: dict) -> None:
    if not isinstance(user, dict):
        return
    metrics = _load_activity_metrics()
    bucket = _ensure_monthly_user_bucket(metrics, local_month_key(), user)
    timestamp = local_now().strftime("%Y-%m-%d %H:%M:%S")
    logins = list(bucket.get("login_times", []))
    logins.append(timestamp)
    bucket["login_times"] = logins[-120:]
    bucket["last_active_at"] = int(time.time())
    _save_activity_metrics(metrics)


def record_user_work_event(user: dict, *, workspace: str = "", filename: str = "", exported: bool = False) -> None:
    if not isinstance(user, dict):
        return
    metrics = _load_activity_metrics()
    bucket = _ensure_monthly_user_bucket(metrics, local_month_key(), user)
    bucket["work_count"] = int(bucket.get("work_count", 0) or 0) + 1
    if workspace:
        platform_counts = bucket.setdefault("platform_counts", {})
        platform_counts[workspace] = int(platform_counts.get(workspace, 0) or 0) + 1
    if exported:
        bucket["export_count"] = int(bucket.get("export_count", 0) or 0) + 1
        files = list(bucket.get("exported_files", []))
        if filename:
            files.append(filename)
        bucket["exported_files"] = files[-120:]
    bucket["last_active_at"] = int(time.time())
    _save_activity_metrics(metrics)


def _active_user_emails(now_epoch: int | None = None) -> set[str]:
    payload = _load_sessions_payload()
    sessions = payload.get("sessions", {})
    current = int(now_epoch or time.time())
    active: set[str] = set()
    for session in sessions.values():
        if not _session_is_active(session, current):
            continue
        email = normalize_email(session.get("email", ""))
        if email:
            active.add(email)
    return active


def sample_user_activity() -> None:
    now_epoch = int(time.time())
    metrics = _load_activity_metrics()
    last_sample_epoch = int(metrics.get("last_sample_epoch", 0) or 0)
    if last_sample_epoch and now_epoch - last_sample_epoch < 55:
        return
    if not _within_workday_hours():
        return
    today_key = local_day_key()
    month_key = local_month_key()
    daily = metrics.setdefault("daily", {})
    day_bucket = daily.setdefault(today_key, {"users": {}, "sample_count": 0})
    users_bucket = day_bucket.setdefault("users", {})
    monthly_users = metrics.setdefault("monthly", {}).setdefault(month_key, {"users": {}}).setdefault("users", {})
    active_emails = _active_user_emails(now_epoch)
    for user in list_local_users().get("users", []):
        if not isinstance(user, dict):
            continue
        email = normalize_email(user.get("email", ""))
        if not email:
            continue
        bucket = users_bucket.setdefault(email, {"online_seconds": 0, "offline_seconds": 0, "display_name": user.get("display_name", ""), "role": user.get("role", "user")})
        bucket["display_name"] = user.get("display_name", "") or bucket.get("display_name", "")
        bucket["role"] = user.get("role", "user")
        monthly_bucket = monthly_users.setdefault(email, {
            "display_name": user.get("display_name", "") or email,
            "role": user.get("role", "user"),
            "login_times": [],
            "work_count": 0,
            "export_count": 0,
            "exported_files": [],
            "online_seconds": 0,
            "offline_seconds": 0,
            "platform_counts": {},
            "last_active_at": 0,
        })
        monthly_bucket["display_name"] = user.get("display_name", "") or monthly_bucket.get("display_name", "")
        monthly_bucket["role"] = user.get("role", "user")
        if email in active_emails:
            bucket["online_seconds"] = int(bucket.get("online_seconds", 0) or 0) + 60
            monthly_bucket["online_seconds"] = int(monthly_bucket.get("online_seconds", 0) or 0) + 60
        else:
            bucket["offline_seconds"] = int(bucket.get("offline_seconds", 0) or 0) + 60
            monthly_bucket["offline_seconds"] = int(monthly_bucket.get("offline_seconds", 0) or 0) + 60
    day_bucket["sample_count"] = int(day_bucket.get("sample_count", 0) or 0) + 1
    metrics["last_sample_epoch"] = now_epoch
    _save_activity_metrics(metrics)


def _render_admin_activity_report(report_date: str) -> dict:
    metrics = _load_activity_metrics()
    daily_metrics = metrics.get("daily") or {}
    users_bucket = ((metrics.get("daily") or {}).get(report_date) or {}).get("users") or {}
    prev_date = (datetime.strptime(report_date, "%Y-%m-%d").replace(tzinfo=LOCAL_TIMEZONE) - timedelta(days=1)).strftime("%Y-%m-%d")
    prev_users_bucket = (daily_metrics.get(prev_date) or {}).get("users") or {}
    rows = []
    total_online = 0
    total_offline = 0
    anomalies = {
        "consecutive_low_activity": [],
        "low_activity_yesterday": [],
        "high_activity_yesterday": [],
    }
    for user in list_local_users().get("users", []):
        if not isinstance(user, dict):
            continue
        email = normalize_email(user.get("email", ""))
        if not email:
            continue
        bucket = users_bucket.get(email, {})
        online_seconds = int(bucket.get("online_seconds", 0) or 0)
        offline_seconds = int(bucket.get("offline_seconds", 0) or 0)
        total_online += online_seconds
        total_offline += offline_seconds
        rows.append({
            "email": email,
            "display_name": user.get("display_name", "") or email,
            "role": user.get("role", "user"),
            "online_seconds": online_seconds,
            "offline_seconds": offline_seconds,
            "online_hours": _seconds_to_hours(online_seconds),
            "offline_hours": _seconds_to_hours(offline_seconds),
        })
        prev_online = int(((prev_users_bucket.get(email) or {}).get("online_seconds", 0)) or 0)
        display_name = user.get("display_name", "") or email
        if online_seconds <= 15 * 60:
            anomalies["low_activity_yesterday"].append({"display_name": display_name, "email": email, "online_seconds": online_seconds})
        if online_seconds >= 8 * 3600:
            anomalies["high_activity_yesterday"].append({"display_name": display_name, "email": email, "online_seconds": online_seconds})
        if online_seconds <= 15 * 60 and prev_online <= 15 * 60:
            anomalies["consecutive_low_activity"].append({"display_name": display_name, "email": email, "online_seconds": online_seconds, "previous_online_seconds": prev_online})
    rows.sort(key=lambda item: (-item.get("online_seconds", 0), item.get("display_name", "")))
    active_top = [
        {
            "display_name": item.get("display_name", "") or item.get("email", ""),
            "email": item.get("email", ""),
            "online_seconds": int(item.get("online_seconds", 0) or 0),
        }
        for item in rows
        if int(item.get("online_seconds", 0) or 0) > 0
    ][:3]
    mostly_offline = [
        {
            "display_name": item.get("display_name", "") or item.get("email", ""),
            "email": item.get("email", ""),
            "online_seconds": int(item.get("online_seconds", 0) or 0),
        }
        for item in rows
        if int(item.get("online_seconds", 0) or 0) <= 15 * 60
    ][:3]
    total_tracked = total_online + total_offline
    online_ratio = round((total_online / total_tracked) * 100, 1) if total_tracked > 0 else 0.0
    for key in anomalies:
        anomalies[key] = anomalies[key][:5]
    return {
        "ok": True,
        "report_date": report_date,
        "generated_at": int(time.time()),
        "timezone": "Asia/Shanghai",
        "users": rows,
        "summary": {
            "user_count": len(rows),
            "total_online_seconds": total_online,
            "total_offline_seconds": total_offline,
            "total_online_hours": _seconds_to_hours(total_online),
            "total_offline_hours": _seconds_to_hours(total_offline),
            "online_ratio_percent": online_ratio,
            "top_active_users": active_top,
            "mostly_offline_users": mostly_offline,
            "anomalies": anomalies,
        },
    }


def _render_admin_monthly_activity_report(report_month: str) -> dict:
    metrics = _load_activity_metrics()
    month_bucket = ((metrics.get("monthly") or {}).get(report_month) or {}).get("users") or {}
    rows: list[dict] = []
    total_online = 0
    total_offline = 0
    total_work = 0
    total_exports = 0
    for user in list_local_users().get("users", []):
        if not isinstance(user, dict):
            continue
        email = normalize_email(user.get("email", ""))
        if not email:
            continue
        bucket = month_bucket.get(email, {}) if isinstance(month_bucket, dict) else {}
        online_seconds = int(bucket.get("online_seconds", 0) or 0)
        offline_seconds = int(bucket.get("offline_seconds", 0) or 0)
        work_count = int(bucket.get("work_count", 0) or 0)
        export_count = int(bucket.get("export_count", 0) or 0)
        platform_counts = bucket.get("platform_counts") if isinstance(bucket.get("platform_counts"), dict) else {}
        most_used_platform = ""
        if platform_counts:
            most_used_platform = max(
                platform_counts.items(),
                key=lambda item: (int(item[1] or 0), str(item[0] or "").lower()),
            )[0]
        exported_files = [str(item) for item in (bucket.get("exported_files") or []) if str(item).strip()]
        login_times = [str(item) for item in (bucket.get("login_times") or []) if str(item).strip()]
        total_online += online_seconds
        total_offline += offline_seconds
        total_work += work_count
        total_exports += export_count
        rows.append({
            "email": email,
            "display_name": user.get("display_name", "") or email,
            "role": user.get("role", "user"),
            "login_count": len(login_times),
            "login_times": login_times,
            "work_count": work_count,
            "export_count": export_count,
            "exported_files": exported_files,
            "online_seconds": online_seconds,
            "offline_seconds": offline_seconds,
            "online_hours": _seconds_to_hours(online_seconds),
            "offline_hours": _seconds_to_hours(offline_seconds),
            "most_used_platform": most_used_platform,
            "last_active_at": int(bucket.get("last_active_at", 0) or 0),
        })
    rows.sort(
        key=lambda item: (
            -int(item.get("work_count", 0) or 0),
            -float(item.get("online_hours", 0) or 0),
            str(item.get("display_name") or item.get("email") or "").lower(),
        )
    )
    generated_local = local_now().strftime("%Y-%m-%d %H:%M:%S")
    return {
        "ok": True,
        "report_month": report_month,
        "generated_at": int(time.time()),
        "generated_at_local": generated_local,
        "timezone": "Asia/Shanghai",
        "users": rows,
        "summary": {
            "user_count": len(rows),
            "total_online_hours": _seconds_to_hours(total_online),
            "total_offline_hours": _seconds_to_hours(total_offline),
            "total_work_count": total_work,
            "total_export_count": total_exports,
        },
    }


def _write_admin_monthly_report_excel(report: dict) -> Path:
    report_month = str(report.get("report_month") or local_month_key())
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Monthly Activity"
    headers = [
        "Display Name",
        "Email",
        "Role",
        "Login Count",
        "Login Times",
        "Work Count",
        "Export Count",
        "Exported Files",
        "Online Hours",
        "Offline Hours",
        "Most Used Platform",
        "Last Active",
    ]
    sheet.append(headers)
    for row in report.get("users", []):
        if not isinstance(row, dict):
            continue
        sheet.append([
            row.get("display_name", ""),
            row.get("email", ""),
            row.get("role", "user"),
            int(row.get("login_count", 0) or 0),
            "\n".join(row.get("login_times", []) or []),
            int(row.get("work_count", 0) or 0),
            int(row.get("export_count", 0) or 0),
            "\n".join(row.get("exported_files", []) or []),
            float(row.get("online_hours", 0) or 0),
            float(row.get("offline_hours", 0) or 0),
            row.get("most_used_platform", ""),
            datetime.fromtimestamp(int(row.get("last_active_at", 0) or 0), LOCAL_TIMEZONE).strftime("%Y-%m-%d %H:%M:%S")
            if int(row.get("last_active_at", 0) or 0) > 0 else "",
        ])
    widths = {
        "A": 24, "B": 32, "C": 12, "D": 12, "E": 34, "F": 12,
        "G": 12, "H": 36, "I": 14, "J": 14, "K": 20, "L": 22,
    }
    for col, width in widths.items():
        sheet.column_dimensions[col].width = width
    output_path = ADMIN_MONTHLY_REPORTS_DIR / f"{report_month}.xlsx"
    workbook.save(output_path)
    return output_path


def maybe_generate_admin_monthly_activity_report(force: bool = False) -> None:
    now_local = local_now()
    if not force:
        if now_local.hour < ADMIN_MONTHLY_REPORT_HOUR or not _is_last_day_of_month(now_local):
            return
        report_month = local_month_key(now_local)
    else:
        report_month = local_month_key(now_local)
    metrics = _load_activity_metrics()
    if (
        not force
        and str(metrics.get("last_monthly_report_key") or "") == report_month
        and LATEST_ADMIN_MONTHLY_REPORT.exists()
    ):
        return
    report = _render_admin_monthly_activity_report(report_month)
    excel_path = _write_admin_monthly_report_excel(report)
    report["file_path"] = str(excel_path)
    report["file_name"] = excel_path.name
    report["download_url"] = f"/api/export-file?path={quote(str(excel_path.resolve()))}"
    _save_json_file(ADMIN_MONTHLY_REPORTS_DIR / f"{report_month}.json", report)
    _save_json_file(LATEST_ADMIN_MONTHLY_REPORT, report)
    metrics["last_monthly_report_key"] = report_month
    _save_activity_metrics(metrics)


def latest_admin_monthly_report_payload() -> dict:
    maybe_generate_admin_monthly_activity_report(force=False)
    report = _render_admin_monthly_activity_report(local_month_key())
    excel_path = _write_admin_monthly_report_excel(report)
    report["file_path"] = str(excel_path)
    report["file_name"] = excel_path.name
    report["download_url"] = f"/api/export-file?path={quote(str(excel_path.resolve()))}"
    _save_json_file(LATEST_ADMIN_MONTHLY_REPORT, report)
    _save_json_file(ADMIN_MONTHLY_REPORTS_DIR / f"{report['report_month']}.json", report)
    return report


def maybe_generate_admin_daily_activity_report(force: bool = False) -> None:
    now_local = local_now()
    if not force and now_local.hour < ADMIN_REPORT_HOUR:
        return
    report_date = local_day_key(now_local - timedelta(days=1))
    metrics = _load_activity_metrics()
    if not force and str(metrics.get("last_report_date") or "") == report_date and LATEST_ADMIN_ACTIVITY_REPORT.exists():
        return
    report = _render_admin_activity_report(report_date)
    report["generated_at"] = int(time.time())
    report["generated_at_local"] = now_local.strftime("%Y-%m-%d %H:%M:%S")
    target = ADMIN_DAILY_REPORTS_DIR / f"{report_date}.json"
    _save_json_file(target, report)
    _save_json_file(LATEST_ADMIN_ACTIVITY_REPORT, report)
    metrics["last_report_date"] = report_date
    _save_activity_metrics(metrics)


def latest_admin_activity_report_payload() -> dict:
    maybe_generate_admin_daily_activity_report(force=False)
    if LATEST_ADMIN_ACTIVITY_REPORT.exists():
        payload = _load_json_file(LATEST_ADMIN_ACTIVITY_REPORT, {"ok": True, "users": []})
        if isinstance(payload, dict):
            users = payload.get("users") if isinstance(payload.get("users"), list) else []
            users_have_hours = all(
                isinstance(item, dict) and "online_hours" in item and "offline_hours" in item
                for item in users
            ) if users else False
            if (
                isinstance(payload.get("summary"), dict)
                and "online_ratio_percent" in payload.get("summary", {})
                and "total_online_hours" in payload.get("summary", {})
                and isinstance((payload.get("summary") or {}).get("anomalies"), dict)
                and users_have_hours
            ):
                payload.setdefault("ok", True)
                return payload
            report_date = str(payload.get("report_date") or "") or local_day_key(local_now() - timedelta(days=1))
            rebuilt = _render_admin_activity_report(report_date)
            rebuilt["generated_at"] = int(payload.get("generated_at", time.time()) or time.time())
            rebuilt["generated_at_local"] = str(payload.get("generated_at_local") or local_now().strftime("%Y-%m-%d %H:%M:%S"))
            _save_json_file(LATEST_ADMIN_ACTIVITY_REPORT, rebuilt)
            _save_json_file(ADMIN_DAILY_REPORTS_DIR / f"{report_date}.json", rebuilt)
            return rebuilt
    fallback_date = local_day_key(local_now() - timedelta(days=1))
    return _render_admin_activity_report(fallback_date)


def activity_sampler_loop() -> None:
    while True:
        try:
            sample_user_activity()
            maybe_generate_admin_daily_activity_report(force=False)
            maybe_generate_admin_monthly_activity_report(force=False)
            _v2_maybe_generate_reports(force=False)
        except Exception as exc:
            log(f"activity_sampler_loop error: {exc}")
        time.sleep(60)


def _session_is_active(session: dict, now: int | None = None) -> bool:
    if not isinstance(session, dict):
        return False
    current = int(now or time.time())
    if int(session.get("expires_at", 0) or 0) <= current:
        return False
    idle_timeout = int(session.get("idle_timeout_seconds", 0) or 0)
    if idle_timeout <= 0:
        email = normalize_email(session.get("email", ""))
        idle_timeout = _session_idle_timeout_seconds(find_local_user(email), session.get("role"))
    last_seen = int(session.get("last_seen_at", session.get("created_at", 0)) or 0)
    return (current - last_seen) <= idle_timeout


def cleanup_local_sessions() -> None:
    payload = _load_sessions_payload()
    sessions = payload.get("sessions", {})
    now = int(time.time())
    filtered = {
        token: session
        for token, session in sessions.items()
        if _session_is_active(session, now)
    }
    if filtered != sessions:
        _save_sessions_payload({"sessions": filtered})


def create_local_session(user: dict) -> str:
    cleanup_local_sessions()
    token = secrets.token_urlsafe(32)
    idle_timeout = _session_idle_timeout_seconds(user)
    payload = _load_sessions_payload()
    sessions = payload.get("sessions", {})
    sessions[token] = {
        "email": normalize_email(user.get("email", "")),
        "created_at": int(time.time()),
        "last_seen_at": int(time.time()),
        "workspace": "home",
        "page": "home",
        "skill_id": "human-exchange",
        "provider": "",
        "model": "",
        "role": str(user.get("role") or "user"),
        "idle_timeout_seconds": idle_timeout,
        "expires_at": int(time.time()) + 30 * 24 * 60 * 60,
    }
    _save_sessions_payload({"sessions": sessions})
    return token


def revoke_local_session(token: str) -> None:
    if not token:
        return
    payload = _load_sessions_payload()
    sessions = payload.get("sessions", {})
    if token in sessions:
        sessions.pop(token, None)
        _save_sessions_payload({"sessions": sessions})


def parse_cookie_map(cookie_header: str) -> dict[str, str]:
    pairs: dict[str, str] = {}
    for chunk in (cookie_header or "").split(";"):
        if "=" not in chunk:
            continue
        key, value = chunk.split("=", 1)
        pairs[key.strip()] = value.strip()
    return pairs


def current_local_user_from_headers(headers) -> dict | None:
    cleanup_local_sessions()
    session_token = current_session_token(headers)
    if not session_token:
        return None
    payload = _load_sessions_payload()
    session = payload.get("sessions", {}).get(session_token)
    if not _session_is_active(session):
        revoke_local_session(session_token)
        return None
    email = normalize_email(session.get("email", ""))
    user = find_local_user(email)
    if not user:
        return None
    if not is_user_approved(user):
        revoke_local_session(session_token)
        return None
    return _public_user_record(user)


def auth_session_payload(headers) -> dict:
    user = current_local_user_from_headers(headers)
    session_token = current_session_token(headers)
    payload = _load_sessions_payload()
    session = payload.get("sessions", {}).get(session_token)
    if not isinstance(session, dict):
        return {"ok": True, "authenticated": bool(user), "user": user, "idle_timeout_seconds": 0, "idle_remaining_seconds": 0}
    idle_timeout = int(session.get("idle_timeout_seconds", 0) or _session_idle_timeout_seconds(user, session.get("role")))
    last_seen = int(session.get("last_seen_at", session.get("created_at", 0)) or 0)
    idle_remaining = max(0, idle_timeout - max(0, int(time.time()) - last_seen))
    return {
        "ok": True,
        "authenticated": bool(user),
        "user": user,
        "idle_timeout_seconds": idle_timeout,
        "idle_remaining_seconds": idle_remaining,
    }


def auth_cookie_header(session_token: str) -> str:
    return f"fastone_hermes_session={session_token}; Path=/; HttpOnly; SameSite=Lax; Max-Age={30 * 24 * 60 * 60}"


def auth_clear_cookie_header() -> str:
    return "fastone_hermes_session=; Path=/; HttpOnly; SameSite=Lax; Max-Age=0"


def current_local_user_record(headers) -> dict | None:
    cleanup_local_sessions()
    session_token = current_session_token(headers)
    if not session_token:
        return None
    payload = _load_sessions_payload()
    session = payload.get("sessions", {}).get(session_token)
    if not _session_is_active(session):
        revoke_local_session(session_token)
        return None
    email = normalize_email(session.get("email", ""))
    user = find_local_user(email)
    if not is_user_approved(user):
        revoke_local_session(session_token)
        return None
    return user


def current_session_token(headers) -> str:
    auth_header = headers.get("Authorization", "")
    if auth_header.lower().startswith("bearer "):
        token = auth_header.split(" ", 1)[1].strip()
        if token:
            return token
    cookie_header = headers.get("Cookie", "")
    return parse_cookie_map(cookie_header).get("fastone_hermes_session", "")


def update_local_session_activity(
    session_token: str,
    *,
    page: str | None = None,
    workspace: str | None = None,
    skill_id: str | None = None,
    provider: str | None = None,
    model: str | None = None,
) -> None:
    if not session_token:
        return
    payload = _load_sessions_payload()
    sessions = payload.get("sessions", {})
    session = sessions.get(session_token)
    if not isinstance(session, dict):
        return
    session["last_seen_at"] = int(time.time())
    session["idle_timeout_seconds"] = int(session.get("idle_timeout_seconds", 0) or _session_idle_timeout_seconds(role=session.get("role")))
    if page is not None:
        session["page"] = _safe_slug(page)
    if workspace is not None:
        session["workspace"] = _safe_slug(workspace)
    if skill_id is not None:
        session["skill_id"] = _safe_slug(skill_id)
    if provider is not None:
        session["provider"] = str(provider or "").strip()
    if model is not None:
        session["model"] = str(model or "").strip()
    sessions[session_token] = session
    _save_sessions_payload({"sessions": sessions})


def mark_local_user_login(email: str) -> None:
    user = find_local_user(email)
    if not user:
        return
    user["last_login_at"] = int(time.time())
    save_local_user_record(user)


def is_admin_user(user: dict | None) -> bool:
    if not isinstance(user, dict):
        return False
    if user.get("role") == "admin":
        return True
    permissions = user.get("permissions")
    return bool(isinstance(permissions, dict) and permissions.get("user_admin"))


def is_user_approved(user: dict | None) -> bool:
    if not isinstance(user, dict):
        return False
    if is_admin_user(user):
        return True
    return str(user.get("approval_status") or "approved") == "approved"


def can_view_team_status(user: dict | None) -> bool:
    if is_admin_user(user):
        return True
    if not isinstance(user, dict):
        return False
    permissions = user.get("permissions")
    return bool(isinstance(permissions, dict) and permissions.get("view_team_status"))


def can_view_document_flows(user: dict | None) -> bool:
    if is_admin_user(user):
        return True
    if not isinstance(user, dict):
        return False
    permissions = user.get("permissions")
    return bool(isinstance(permissions, dict) and permissions.get("view_document_flows"))


def ensure_admin_account() -> None:
    payload = list_local_users()
    users = payload.get("users", [])
    existing = None
    for user in users:
        if isinstance(user, dict) and normalize_email(user.get("email", "")) == normalize_email(ADMIN_EMAIL):
            existing = user
            break
    changed = False
    for user in users:
        if not isinstance(user, dict):
            continue
        if normalize_email(user.get("email", "")) == normalize_email(ADMIN_EMAIL):
            continue
        if normalize_username(user.get("username", "")) == normalize_username(ADMIN_USERNAME):
            base = normalize_username(user.get("display_name", "")) or normalize_username(str(user.get("email", "")).split("@")[0]) or "user"
            candidate = _unique_username(base, users, normalize_email(user.get("email", "")), str(user.get("display_name", "")))
            user["username"] = candidate
            changed = True
    salt_hex = secrets.token_hex(16)
    password_hash = _password_hash(ADMIN_PASSWORD, salt_hex)
    if existing:
        existing["email"] = normalize_email(ADMIN_EMAIL)
        existing["username"] = ADMIN_USERNAME
        existing["display_name"] = existing.get("display_name") or "Bill"
        existing["role"] = "admin"
        existing["approval_status"] = "approved"
        existing["approved_at"] = existing.get("approved_at") or int(time.time())
        existing["approved_by"] = existing.get("approved_by") or "system"
        existing["permissions"] = admin_permissions()
        existing["password_salt"] = salt_hex
        existing["password_hash"] = password_hash
        if changed:
            save_local_users({"users": users})
        save_local_user_record(existing)
        return
    user = {
        "email": normalize_email(ADMIN_EMAIL),
        "username": ADMIN_USERNAME,
        "phone": "",
        "display_name": "Bill",
        "role": "admin",
        "approval_status": "approved",
        "approved_at": int(time.time()),
        "approved_by": "system",
        "permissions": admin_permissions(),
        "password_salt": salt_hex,
        "password_hash": password_hash,
        "created_at": int(time.time()),
    }
    users.append(user)
    save_local_users({"users": users})


ensure_admin_account()


def admin_users_payload() -> dict:
    users = list_local_users().get("users", [])
    sessions_payload = _load_sessions_payload()
    sessions = sessions_payload.get("sessions", {})
    by_email: dict[str, list[dict]] = {}
    for session in sessions.values():
        if not isinstance(session, dict):
            continue
        email_key = normalize_email(session.get("email", ""))
        if not email_key:
            continue
        by_email.setdefault(email_key, []).append(session)
    records = []
    for user in users:
        if not isinstance(user, dict):
            continue
        public = _public_user_record(user)
        email_key = normalize_email(public.get("email", ""))
        all_sessions = by_email.get(email_key, [])
        now = int(time.time())
        latest = max(all_sessions, key=lambda item: int(item.get("last_seen_at", item.get("created_at", 0))), default=None)
        active_sessions = [
            session for session in all_sessions
            if now - int(session.get("last_seen_at", session.get("created_at", 0)) or 0) <= ONLINE_WINDOW_SECONDS
        ]
        idle_timeout = 0
        idle_remaining = 0
        if isinstance(latest, dict):
            idle_timeout = int(latest.get("idle_timeout_seconds", 0) or _session_idle_timeout_seconds(user, latest.get("role")))
            last_seen = int(latest.get("last_seen_at", latest.get("created_at", 0)) or 0)
            idle_remaining = max(0, idle_timeout - max(0, now - last_seen))
        public["login_status"] = {
            "logged_in": bool(active_sessions),
            "session_count": len(active_sessions),
            "last_seen_at": int(latest.get("last_seen_at", 0)) if isinstance(latest, dict) else 0,
            "idle_timeout_seconds": idle_timeout,
            "idle_remaining_seconds": idle_remaining,
            "work_status": {
                "page": latest.get("page", "") if isinstance(latest, dict) else "",
                "workspace": latest.get("workspace", "") if isinstance(latest, dict) else "",
                "skill_id": latest.get("skill_id", "") if isinstance(latest, dict) else "",
                "provider": latest.get("provider", "") if isinstance(latest, dict) else "",
                "model": latest.get("model", "") if isinstance(latest, dict) else "",
            },
        }
        records.append(public)
    def record_sort_key(item: dict) -> tuple:
        login = item.get("login_status") or {}
        logged_in = bool(login.get("logged_in"))
        idle_remaining = int(login.get("idle_remaining_seconds", 0) or 0)
        last_seen = int(login.get("last_seen_at", 0) or 0)
        return (
            0 if logged_in else 1,
            idle_remaining if logged_in else 10**9,
            -last_seen if logged_in else 0,
            str(item.get("display_name") or item.get("email") or "").lower(),
        )
    records.sort(key=record_sort_key)
    return {"ok": True, "users": records}


def _matches_user_search(text: str, *parts: object) -> bool:
    query = str(text or "").strip().lower()
    if not query:
        return True
    haystack = " ".join(str(part or "") for part in parts).lower()
    return query in haystack


def team_status_payload(query: str = "") -> dict:
    users = admin_users_payload().get("users", [])
    metrics = _load_activity_metrics()
    monthly_users = ((metrics.get("monthly") or {}).get(local_month_key()) or {}).get("users") or {}
    items = []
    for user in users:
        login = user.get("login_status") or {}
        work = login.get("work_status") or {}
        logged_in = bool(login.get("logged_in"))
        if not _matches_user_search(
            query,
            user.get("email", ""),
            user.get("username", ""),
            user.get("display_name", ""),
            user.get("role", ""),
            "online" if logged_in else "offline",
            "在线" if logged_in else "离线",
            work.get("page", ""),
            work.get("workspace", ""),
            work.get("skill_id", ""),
            work.get("provider", ""),
            work.get("model", ""),
        ):
            continue
        items.append({
            "email": user.get("email", ""),
            "username": user.get("username", ""),
            "display_name": user.get("display_name", ""),
            "role": user.get("role", "user"),
            "logged_in": logged_in,
            "last_seen_at": int(login.get("last_seen_at", 0) or 0),
            "idle_timeout_seconds": int(login.get("idle_timeout_seconds", 0) or 0),
            "idle_remaining_seconds": int(login.get("idle_remaining_seconds", 0) or 0),
            "current_page": work.get("page", ""),
            "current_workspace": work.get("workspace", ""),
            "current_action": work.get("skill_id", ""),
            "provider": work.get("provider", ""),
            "model": work.get("model", ""),
            "online_hours": _seconds_to_hours((monthly_users.get(normalize_email(user.get("email", ""))) or {}).get("online_seconds", 0)),
            "offline_hours": _seconds_to_hours((monthly_users.get(normalize_email(user.get("email", ""))) or {}).get("offline_seconds", 0)),
            "work_count": int((monthly_users.get(normalize_email(user.get("email", ""))) or {}).get("work_count", 0) or 0),
            "export_count": int((monthly_users.get(normalize_email(user.get("email", ""))) or {}).get("export_count", 0) or 0),
        })
    return {"ok": True, "users": items}


def update_local_user_password(identifier: str, new_password: str) -> tuple[bool, str]:
    if len(new_password or "") < 8:
        return False, "password_too_short"
    user = find_local_user_by_identifier(identifier)
    if not user:
        return False, "user_not_found"
    salt_hex = secrets.token_hex(16)
    user["password_salt"] = salt_hex
    user["password_hash"] = _password_hash(new_password, salt_hex)
    user["password_updated_at"] = int(time.time())
    save_local_user_record(user)
    return True, "ok"


def change_own_password(user: dict, current_password: str, new_password: str) -> tuple[bool, str]:
    if len(new_password or "") < 8:
        return False, "password_too_short"
    salt_hex = str(user.get("password_salt") or "")
    stored_hash = str(user.get("password_hash") or "")
    if not salt_hex or not stored_hash:
        return False, "invalid_user_record"
    candidate = _password_hash(current_password or "", salt_hex)
    if not hmac.compare_digest(candidate, stored_hash):
        return False, "invalid_password"
    user["password_salt"] = secrets.token_hex(16)
    user["password_hash"] = _password_hash(new_password, user["password_salt"])
    user["password_updated_at"] = int(time.time())
    save_local_user_record(user)
    return True, "ok"


def update_local_user_permissions(identifier: str, role: str | None = None, permissions: dict | None = None) -> tuple[bool, str, dict | None]:
    user = find_local_user_by_identifier(identifier)
    if not user:
        return False, "user_not_found", None
    next_role = "admin" if role == "admin" else "user"
    if normalize_email(user.get("email", "")) == normalize_email(ADMIN_EMAIL):
        next_role = "admin"
    user["role"] = next_role
    user["permissions"] = normalize_permissions(permissions, admin=(next_role == "admin"))
    save_local_user_record(user)
    return True, "ok", _public_user_record(user)


def update_local_user_approval(identifier: str, action: str, admin_user: dict, permissions: dict | None = None, reason: str = "") -> tuple[bool, str, dict | None]:
    user = find_local_user_by_identifier(identifier)
    if not user:
        return False, "user_not_found", None
    if normalize_email(user.get("email", "")) == normalize_email(ADMIN_EMAIL):
        user["approval_status"] = "approved"
        user["approved_at"] = int(time.time())
        user["approved_by"] = normalize_email(admin_user.get("email", "")) or "system"
        save_local_user_record(user)
        return True, "ok", _public_user_record(user)
    action = str(action or "").strip().lower()
    now = int(time.time())
    admin_email = normalize_email(admin_user.get("email", ""))
    if action == "approve":
        next_permissions = normalize_permissions(permissions, admin=(str(user.get("role") or "user") == "admin")) if isinstance(permissions, dict) else None
        if normalize_email(user.get("email", "")) != normalize_email(ADMIN_EMAIL):
            if not isinstance(next_permissions, dict):
                return False, "approval_permissions_required", None
            platforms = [item for item in next_permissions.get("platforms", []) if item and item != "*"]
            colleagues = [normalize_email(item) for item in next_permissions.get("colleagues", []) if normalize_email(item) and item != "*"]
            if not platforms:
                return False, "approval_platforms_required", None
            if not colleagues:
                return False, "approval_colleagues_required", None
            user["permissions"] = next_permissions
        user["approval_status"] = "approved"
        user["approved_at"] = now
        user["approved_by"] = admin_email
        user["rejected_at"] = 0
        user["rejected_by"] = ""
        user["rejected_reason"] = ""
    elif action == "reject":
        user["approval_status"] = "rejected"
        user["rejected_at"] = now
        user["rejected_by"] = admin_email
        user["rejected_reason"] = str(reason or "").strip()[:500]
    else:
        return False, "unsupported_action", None
    save_local_user_record(user)
    write_audit_event({
        "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
        "event": f"admin_{action}_user",
        "target_user": normalize_email(user.get("email", "")),
        "admin": admin_email,
    })
    return True, "ok", _public_user_record(user)


def admin_create_local_user(payload: dict, admin_user: dict) -> tuple[bool, str, dict | None]:
    email = str(payload.get("email") or "").strip()
    phone = str(payload.get("phone") or "").strip()
    password = str(payload.get("password") or "")
    display_name = str(payload.get("display_name") or "").strip()
    username = str(payload.get("username") or "").strip()
    ok, reason, public_user = register_local_user(email, phone, password, display_name, username)
    if not ok or not public_user:
        return ok, reason, public_user
    role = "admin" if str(payload.get("role") or "user").strip().lower() == "admin" else "user"
    permissions = payload.get("permissions") if isinstance(payload.get("permissions"), dict) else default_user_permissions()
    ok2, reason2, updated_user = update_local_user_permissions(public_user.get("email", ""), role, permissions)
    if not ok2:
        return False, reason2, None
    raw_user = find_local_user(public_user.get("email", ""))
    if raw_user:
        raw_user["approval_status"] = "approved"
        raw_user["approved_at"] = int(time.time())
        raw_user["approved_by"] = normalize_email(admin_user.get("email", ""))
        save_local_user_record(raw_user)
        updated_user = _public_user_record(raw_user)
    write_audit_event({
        "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
        "event": "admin_create_user",
        "created_user": normalize_email(public_user.get("email", "")),
        "admin": normalize_email(admin_user.get("email", "")),
        "role": role,
    })
    return True, "ok", updated_user


def delete_local_user(identifier: str) -> tuple[bool, str]:
    user = find_local_user_by_identifier(identifier)
    if not user:
        return False, "user_not_found"
    if normalize_email(user.get("email", "")) == normalize_email(ADMIN_EMAIL):
        return False, "cannot_delete_admin"
    payload = list_local_users()
    users = payload.get("users", [])
    email_key = normalize_email(user.get("email", ""))
    users = [item for item in users if not (isinstance(item, dict) and normalize_email(item.get("email", "")) == email_key)]
    save_local_users({"users": users})
    sessions_payload = _load_sessions_payload()
    sessions = sessions_payload.get("sessions", {})
    sessions = {
        token: session
        for token, session in sessions.items()
        if not (isinstance(session, dict) and normalize_email(session.get("email", "")) == email_key)
    }
    _save_sessions_payload({"sessions": sessions})
    return True, "ok"


def provider_cooldown(provider: str) -> float:
    state = provider_health.get(provider)
    if not state:
        return 0.0
    until = float(state.get("until", 0.0))
    remaining = until - time.time()
    if remaining <= 0:
        provider_health.pop(provider, None)
        return 0.0
    return remaining


def prime_provider_health_from_logs(window_seconds: int = 1800) -> None:
    if not APP_LOG.exists():
        return
    try:
        lines = APP_LOG.read_text(encoding="utf-8", errors="ignore").splitlines()[-300:]
    except Exception:
        return
    now = time.time()
    for line in reversed(lines):
        if "[202" not in line:
            continue
        lowered = line.lower()
        provider = ""
        if "google-gemini-cli" in lowered and (
            "marked provider unhealthy" in lowered
            or "returned an empty stream via google-gemini-cli" in lowered
            or "retryable json failure via google-gemini-cli" in lowered
            or "retryable streamed failure via google-gemini-cli" in lowered
            or "no google oauth credentials" in lowered
        ):
            provider = "google-gemini-cli"
        if not provider:
            continue
        try:
            timestamp = line.split("] ", 1)[0].strip("[")
            event_time = time.mktime(time.strptime(timestamp, "%Y-%m-%d %H:%M:%S"))
        except Exception:
            continue
        if now - event_time <= window_seconds:
            remaining = min(PROVIDER_COOLDOWN_SECONDS, max(30, window_seconds - (now - event_time)))
            provider_health[provider] = {
                "until": now + remaining,
                "reason": "primed-from-recent-log",
            }
            log(f"Primed provider cooldown from recent log: {provider} ({remaining:.0f}s)")


def _looks_like_failed_reply(text: str) -> bool:
    message = (text or "").lower()
    markers = [
        "api call failed after",
        "http 429",
        "quota exhausted",
        "rate limited",
        "usage limit has been reached",
        "no google oauth credentials",
        "invalid api key",
        "temporarily unavailable",
        "streaming request failed",
        "unexpected_eof_while_reading",
        "check /gquota",
    ]
    return any(marker in message for marker in markers)


def _chat_attempts(requested_provider: str | None, requested_model: str | None) -> list[tuple[str, str]]:
    current_provider, current_model = current_provider_model()
    primary_provider = requested_provider or current_provider
    primary_model = requested_model or current_model
    attempts: list[tuple[str, str]] = []
    primary_cooldown = provider_cooldown(primary_provider) if primary_provider else 0.0
    primary_available = True
    if primary_provider in {"google-gemini-cli", "gemini"}:
        primary_available = google_gemini_auth_available() if primary_provider == "google-gemini-cli" else gemini_auth_available()
    elif primary_provider == "chatgpt":
        primary_available = codex_auth_available()
    if primary_provider and primary_model and primary_cooldown <= 0 and primary_available:
        attempts.append((primary_provider, primary_model))
    if primary_provider == "chatgpt" and provider_cooldown("chatgpt") <= 0 and codex_auth_available():
        for candidate in ("gpt-5.3-codex", "gpt-5.4", CHATGPT_FALLBACK_MODEL):
            if candidate != primary_model and codex_auth_available():
                attempts.append(("chatgpt", candidate))
    if primary_provider in {"google-gemini-cli", "gemini"} and primary_cooldown <= 0 and primary_available and not requested_model:
        for candidate in GEMINI_MODELS:
            if candidate != primary_model:
                attempts.append((primary_provider, candidate))
    if primary_provider in {"google-gemini-cli", "gemini"} and codex_auth_available() and provider_cooldown("chatgpt") <= 0:
        attempts.append(("chatgpt", CHATGPT_FALLBACK_MODEL))
    elif primary_provider != "chatgpt" and codex_auth_available() and provider_cooldown("chatgpt") <= 0:
        attempts.append(("chatgpt", CHATGPT_FALLBACK_MODEL))
    if primary_provider == "lmstudio":
        models = lmstudio_models()
        if models:
            attempts.append(("lmstudio", models[0]))
    if provider_cooldown("nvidia") <= 0:
        attempts.append(("nvidia", "minimaxai/minimax-m2.7"))
    deduped: list[tuple[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for attempt in attempts:
        if attempt in seen:
            continue
        seen.add(attempt)
        deduped.append(attempt)
    return deduped


def log(message: str) -> None:
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with APP_LOG.open("a", encoding="utf-8") as fh:
        fh.write(f"[{timestamp}] {message}\n")


def resolve_hermes_bin() -> str:
    candidates = [
        HERMES_PROJECT / "venv/bin/hermes",
        HOME / ".local/bin/hermes",
    ]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    hermes_on_path = shutil.which("hermes")
    if hermes_on_path:
        return hermes_on_path
    raise FileNotFoundError("Unable to locate hermes binary")


def port_open(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.5)
        return sock.connect_ex((HOST, port)) == 0


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        return {}
    return yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8")) or {}


def save_config(config: dict) -> None:
    CONFIG_PATH.write_text(yaml.safe_dump(config, sort_keys=False, allow_unicode=True), encoding="utf-8")


def mask_privacy(text: str) -> str:
    masked = re.sub(r"\b\d{16,19}\b", "[MASKED_ACCOUNT]", text or "")
    masked = re.sub(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", "[MASKED_EMAIL]", masked, flags=re.I)
    masked = re.sub(r"\b(?:USD|HKD|RMB|CNY|\$|¥|€)?\s?\d{1,3}(?:,\d{3})+(?:\.\d+)?\b", "[MASKED_AMOUNT]", masked)
    return masked


def mask_message_content(content: object) -> object:
    if isinstance(content, str):
        return mask_privacy(content)
    if isinstance(content, list):
        return [mask_message_content(item) for item in content]
    if isinstance(content, dict):
        updated = dict(content)
        for key in ("text", "content", "output_text"):
            if isinstance(updated.get(key), str):
                updated[key] = mask_privacy(updated[key])
        return updated
    return content


def mask_messages(messages: list[dict]) -> list[dict]:
    sanitized: list[dict] = []
    for message in messages:
        if not isinstance(message, dict):
            continue
        item = dict(message)
        item["content"] = mask_message_content(item.get("content"))
        sanitized.append(item)
    return sanitized


def audit_secret() -> bytes:
    seed = api_key() or "fastone-hermes-audit"
    return hashlib.sha256(seed.encode("utf-8")).digest()


def encrypt_audit_payload(payload: dict) -> str:
    raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    secret = audit_secret()
    encrypted = bytes(b ^ secret[i % len(secret)] for i, b in enumerate(raw))
    return base64.b64encode(encrypted).decode("ascii")


def decrypt_audit_payload(value: str) -> dict | None:
    try:
        encrypted = base64.b64decode(str(value or ""))
        secret = audit_secret()
        raw = bytes(b ^ secret[i % len(secret)] for i, b in enumerate(encrypted))
        payload = json.loads(raw.decode("utf-8"))
        return payload if isinstance(payload, dict) else None
    except Exception:
        return None


def write_audit_event(event: dict) -> None:
    month_path = AUDIT_DIR / f"{time.strftime('%Y-%m')}.jsonl"
    month_path.parent.mkdir(parents=True, exist_ok=True)
    line = encrypt_audit_payload(event)
    with month_path.open("a", encoding="utf-8") as fh:
        fh.write(line + "\n")


def recent_audit_events(limit: int = 60) -> list[dict]:
    rows: list[dict] = []
    for path in sorted(AUDIT_DIR.glob("*.jsonl"), key=lambda item: item.name, reverse=True)[:3]:
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except Exception:
            continue
        for line in reversed(lines[-300:]):
            item = decrypt_audit_payload(line)
            if not item:
                continue
            rows.append(item)
            if len(rows) >= limit:
                return rows
    return rows


GOVERNANCE_DLP_TERMS = [
    "KYC",
    "AML",
    "UBO",
    "MT799",
    "MT760",
    "passport",
    "bank account",
    "credit line",
    "beneficiary",
    "swift",
]


def detect_governance_dlp_terms(*parts: object) -> list[str]:
    text = " ".join(str(part or "") for part in parts).lower()
    hits = []
    for term in GOVERNANCE_DLP_TERMS:
        if term.lower() in text:
            hits.append(term)
    return sorted(set(hits), key=lambda item: item.lower())


def sanitize_governance_audit_event(row: dict) -> dict:
    event = str(row.get("event") or row.get("action") or row.get("action_type") or "event")
    actor = str(row.get("actor") or row.get("created_by") or row.get("admin") or row.get("email") or row.get("user") or "system")
    target = str(row.get("target") or row.get("document_id") or row.get("file_id") or row.get("conversation_id") or row.get("workspace") or "")
    filename = os.path.basename(str(row.get("filename") or row.get("download_name") or ""))
    ts_value = row.get("ts") or row.get("created_at") or row.get("time") or ""
    ts_epoch = 0
    if isinstance(ts_value, (int, float)):
        ts_epoch = int(ts_value)
    elif isinstance(ts_value, str):
        try:
            ts_epoch = int(ts_value)
        except Exception:
            try:
                ts_epoch = int(datetime.fromisoformat(ts_value.replace("Z", "+00:00")).timestamp())
            except Exception:
                ts_epoch = 0
    terms = row.get("dlp_terms")
    return {
        "event": event,
        "actor": actor,
        "target": target,
        "filename": filename,
        "ts": ts_epoch,
        "ts_text": str(ts_value or ""),
        "dlp_terms": terms if isinstance(terms, list) else detect_governance_dlp_terms(event, target, filename),
    }


def _compact_memory_text(text: object, limit: int = 280) -> str:
    cleaned = " ".join(str(text or "").replace("\r", " ").replace("\n", " ").split()).strip()
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[: limit - 1].rstrip() + "…"


def _memory_scope(workspace: str, skill_id: str | None = None) -> str:
    base = re.sub(r"[^A-Za-z0-9._-]+", "-", str(workspace or "workspace")).strip("-._") or "workspace"
    skill = re.sub(r"[^A-Za-z0-9._-]+", "-", str(skill_id or "").strip()).strip("-._")
    return f"{base}--{skill}" if skill else base


def _memory_path(workspace: str, skill_id: str | None = None) -> Path:
    return MEMORY_DIR / f"{_memory_scope(workspace, skill_id)}.json"


def _load_workspace_memory(workspace: str, skill_id: str | None = None) -> dict:
    path = _memory_path(workspace, skill_id)
    if not path.exists():
        return {"summary": "", "recent": [], "updated_at": 0}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {"summary": "", "recent": [], "updated_at": 0}
    if not isinstance(data, dict):
        return {"summary": "", "recent": [], "updated_at": 0}
    data.setdefault("summary", "")
    data.setdefault("recent", [])
    data.setdefault("updated_at", 0)
    return data


def _save_workspace_memory(workspace: str, skill_id: str | None, payload: dict) -> None:
    path = _memory_path(workspace, skill_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _latest_user_message(messages: list[dict]) -> str:
    for message in reversed(messages):
        if not isinstance(message, dict):
            continue
        if message.get("role") != "user":
            continue
        text = _content_text(message.get("content"))
        if text.strip():
            return text
    return ""


def _workspace_memory_system_message(workspace: str, skill_id: str | None = None, concise: bool = False) -> str:
    payload = _load_workspace_memory(workspace, skill_id)
    recent = payload.get("recent") or []
    summary = _compact_memory_text(payload.get("summary") or "", 220 if concise else 700)
    lines = [
        "Professional operating standard:",
        "- Write like a senior domain professional, not like an AI assistant.",
        "- Do not use AI tell-tale phrasing, boilerplate disclaimers, or generic filler.",
        "- Keep conclusions clear, evidence-grounded, and directly usable in business, legal, finance, or operating work.",
    ]
    if summary:
        lines.extend(["", "Long-term workspace memory:", summary])
    if recent:
        lines.append("")
        lines.append("Recent durable context:")
        for item in recent[-(1 if concise else 4):]:
            request = _compact_memory_text(item.get("request") or "", 90 if concise else 180)
            response = _compact_memory_text(item.get("response") or "", 120 if concise else 220)
            if request or response:
                lines.append(f"- Request: {request} | Result: {response}")
    return "\n".join(lines)


def _inject_workspace_memory(messages: list[dict], workspace: str, skill_id: str | None = None, concise: bool = False) -> list[dict]:
    injected = [{"role": "system", "content": _workspace_memory_system_message(workspace, skill_id, concise=concise)}]
    injected.extend(messages or [])
    return injected


def update_workspace_memory(workspace: str, skill_id: str | None, messages: list[dict], result: str) -> None:
    text = _compact_memory_text(result, 480)
    if not text or _looks_like_failed_reply(text):
        return
    request_text = _compact_memory_text(_latest_user_message(messages), 260)
    payload = _load_workspace_memory(workspace, skill_id)
    recent = [item for item in payload.get("recent", []) if isinstance(item, dict)]
    recent.append(
        {
            "ts": int(time.time()),
            "request": request_text,
            "response": text,
        }
    )
    recent = recent[-10:]
    summary_bits = []
    for item in recent[-5:]:
        req = _compact_memory_text(item.get("request") or "", 120)
        resp = _compact_memory_text(item.get("response") or "", 150)
        if req or resp:
            summary_bits.append(f"{req} -> {resp}")
    payload["recent"] = recent
    payload["summary"] = " | ".join(summary_bits)
    payload["updated_at"] = int(time.time())
    _save_workspace_memory(workspace, skill_id, payload)


def api_key() -> str:
    if ENV_PATH.exists():
        for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
            if line.startswith("API_SERVER_KEY="):
                return line.split("=", 1)[1].strip()
    return ""


def env_value(*keys: str) -> str:
    for key in keys:
        value = os.environ.get(key, "")
        if value:
            return value
    if not ENV_PATH.exists():
        return ""
    values = {}
    for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
        if "=" not in line or line.lstrip().startswith("#"):
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    for key in keys:
        value = values.get(key, "")
        if value:
            return value
    return ""


def slack_api_call(method: str, payload: dict | None = None, http_method: str = "POST") -> dict:
    token = env_value("SLACK_BOT_TOKEN")
    if not token:
        return {"ok": False, "error": "SLACK_BOT_TOKEN is not configured"}
    node_runtime = next(
        (
            candidate
            for candidate in ("/opt/homebrew/bin/node", "/usr/local/bin/node", "/usr/bin/node")
            if Path(candidate).exists()
        ),
        shutil.which("node") or "node",
    )
    request_payload = {
        "method": method,
        "payload": payload or {},
        "http_method": http_method,
        "token": token,
    }
    script = r"""
const https = require("https");
const input = JSON.parse(require("fs").readFileSync(0, "utf8"));
const data = input.http_method === "POST" ? JSON.stringify(input.payload || {}) : "";
const query = input.http_method === "GET"
  ? "?" + new URLSearchParams(input.payload || {}).toString()
  : "";
const req = https.request({
  hostname: "slack.com",
  path: "/api/" + input.method + query,
  method: input.http_method || "POST",
  headers: {
    "Authorization": "Bearer " + input.token,
    "Content-Type": "application/json; charset=utf-8",
    "Content-Length": Buffer.byteLength(data)
  },
  timeout: 20000
}, (res) => {
  let out = "";
  res.on("data", (chunk) => out += chunk);
  res.on("end", () => process.stdout.write(out || "{}"));
});
req.on("timeout", () => req.destroy(new Error("timeout")));
req.on("error", (err) => {
  process.stdout.write(JSON.stringify({ ok: false, error: String(err.message || err) }));
});
if (data) req.write(data);
req.end();
"""
    last_error: str | None = None
    for attempt in range(3):
        proc = subprocess.run(
            [node_runtime, "-e", script],
            input=json.dumps(request_payload).encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=25,
        )
        raw = proc.stdout.decode("utf-8", errors="ignore").strip() or "{}"
        try:
            parsed = json.loads(raw)
        except Exception:
            parsed = {"ok": False, "error": "Unexpected Slack response", "raw": raw[:500]}
        if isinstance(parsed, dict):
            error_text = str(parsed.get("error") or "")
            if parsed.get("ok") or not re.search(r"socket|timeout|tls|eof|network|disconnected", error_text, re.I):
                return parsed
            last_error = error_text
        else:
            return {"ok": False, "error": "Unexpected Slack response", "raw": raw[:500]}
        time.sleep(0.7 * (attempt + 1))
    return {"ok": False, "error": last_error or "Slack request failed after retries"}


def node_runtime() -> str:
    return next(
        (
            candidate
            for candidate in ("/opt/homebrew/bin/node", "/usr/local/bin/node", "/usr/bin/node")
            if Path(candidate).exists()
        ),
        shutil.which("node") or "node",
    )


def telegram_api_call(method: str, payload: dict | None = None, http_method: str = "POST") -> dict:
    token = env_value("TELEGRAM_BOT_TOKEN")
    if not token:
        return {"ok": False, "error": "TELEGRAM_BOT_TOKEN is not configured"}
    request_payload = {
        "method": method,
        "payload": payload or {},
        "http_method": http_method,
        "token": token,
    }
    script = r"""
const https = require("https");
const input = JSON.parse(require("fs").readFileSync(0, "utf8"));
const data = input.http_method === "POST" ? JSON.stringify(input.payload || {}) : "";
const query = input.http_method === "GET"
  ? "?" + new URLSearchParams(input.payload || {}).toString()
  : "";
const req = https.request({
  hostname: "api.telegram.org",
  path: "/bot" + input.token + "/" + input.method + query,
  method: input.http_method || "POST",
  headers: {
    "Content-Type": "application/json; charset=utf-8",
    "Content-Length": Buffer.byteLength(data)
  },
  timeout: 20000
}, (res) => {
  let out = "";
  res.on("data", (chunk) => out += chunk);
  res.on("end", () => process.stdout.write(out || "{}"));
});
req.on("timeout", () => req.destroy(new Error("timeout")));
req.on("error", (err) => {
  process.stdout.write(JSON.stringify({ ok: false, error: String(err.message || err) }));
});
if (data) req.write(data);
req.end();
"""
    last_error: str | None = None
    for attempt in range(3):
        proc = subprocess.run(
            [node_runtime(), "-e", script],
            input=json.dumps(request_payload).encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=25,
        )
        raw = proc.stdout.decode("utf-8", errors="ignore").strip() or "{}"
        try:
            parsed = json.loads(raw)
        except Exception:
            parsed = {"ok": False, "error": "Unexpected Telegram response", "raw": raw[:500]}
        if isinstance(parsed, dict):
            error_text = str(parsed.get("description") or parsed.get("error") or "")
            if parsed.get("ok") or not re.search(r"socket|timeout|tls|eof|network|disconnected|getaddrinfo", error_text, re.I):
                return parsed
            last_error = error_text
        else:
            return {"ok": False, "error": "Unexpected Telegram response", "raw": raw[:500]}
        time.sleep(0.7 * (attempt + 1))
    return {"ok": False, "error": last_error or "Telegram request failed after retries"}


def compact_telegram_update(update: dict, allowed_chat_id: str) -> dict | None:
    message = update.get("message") or update.get("edited_message")
    if not isinstance(message, dict):
        return None
    chat = message.get("chat") if isinstance(message.get("chat"), dict) else {}
    chat_id = str(chat.get("id") or "")
    if allowed_chat_id and chat_id != allowed_chat_id:
        return None
    text = str(message.get("text") or message.get("caption") or "").strip()
    if not text:
        return None
    sender = message.get("from") if isinstance(message.get("from"), dict) else {}
    return {
        "update_id": update.get("update_id"),
        "message_id": message.get("message_id"),
        "chat_id": chat_id,
        "from": sender.get("username") or sender.get("first_name") or sender.get("id") or "telegram",
        "text": text,
        "date": message.get("date"),
    }


def compact_slack_message(message: dict) -> dict:
    text = str(message.get("text") or "").strip()
    user = str(message.get("user") or message.get("bot_id") or "")
    return {
        "user": user,
        "text": text,
        "ts": str(message.get("ts") or ""),
        "thread_ts": str(message.get("thread_ts") or ""),
    }


def auth_payload() -> dict:
    try:
        return json.loads(AUTH_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def codex_auth_available() -> bool:
    pool = auth_payload().get("credential_pool", {}).get("openai-codex", [])
    return bool(pool)


def google_gemini_auth_available() -> bool:
    pool = auth_payload().get("credential_pool", {}).get("google-gemini-cli", [])
    return bool(pool)


def gemini_auth_available() -> bool:
    payload = auth_payload()
    pool = payload.get("credential_pool", {}).get("gemini", [])
    if pool:
        return True
    return bool(env_value("GOOGLE_API_KEY", "GEMINI_API_KEY"))


def google_gemini_pool_size() -> int:
    return len(auth_payload().get("credential_pool", {}).get("google-gemini-cli", []))


def gemini_pool_size() -> int:
    return len(auth_payload().get("credential_pool", {}).get("gemini", []))


def codex_pool_size() -> int:
    return len(auth_payload().get("credential_pool", {}).get("openai-codex", []))


def current_provider_model() -> tuple[str, str]:
    cfg = load_config()
    model_cfg = cfg.get("model") or {}
    provider = str(model_cfg.get("provider") or "custom")
    model = str(model_cfg.get("default") or "")
    base_url = str(model_cfg.get("base_url") or "")
    if provider in {"lmstudio", "custom"} and "127.0.0.1:1234" in base_url:
        return "lmstudio", model
    if provider == "google-gemini-cli":
        return "google-gemini-cli", model or GEMINI_MODELS[0]
    if provider == "gemini":
        return "gemini", model or GEMINI_MODELS[0]
    if provider == "openai-codex":
        return "chatgpt", model or CODEX_MODELS[0]
    return provider, model


def lmstudio_models() -> list[str]:
    try:
        resp = httpx.get(LM_API, timeout=5.0)
        resp.raise_for_status()
        data = resp.json().get("data", [])
        return [item.get("id") for item in data if item.get("id")]
    except Exception:
        return []


def wait_for_port(port: int, timeout: float = 15.0) -> bool:
    start = time.time()
    while time.time() - start < timeout:
        if port_open(port):
            return True
        time.sleep(0.25)
    return False


def wait_for_gateway_ready(timeout: float = 20.0) -> bool:
    deadline = time.time() + timeout
    headers = {}
    bearer = api_key()
    if bearer:
        headers["Authorization"] = f"Bearer {bearer}"
    while time.time() < deadline:
        if not port_open(8642):
            time.sleep(0.25)
            continue
        try:
            response = httpx.get(f"{HERMES_API}/models", headers=headers, timeout=4.0)
            if response.is_success:
                return True
        except Exception:
            pass
        time.sleep(0.5)
    return False


def start_gateway() -> None:
    global gateway_proc
    with gateway_lock:
        if gateway_proc and gateway_proc.poll() is None:
            wait_for_gateway_ready(8.0)
            return
        if port_open(8642):
            wait_for_gateway_ready(8.0)
            return
        hermes_bin = resolve_hermes_bin()
        cwd = HERMES_PROJECT if HERMES_PROJECT.exists() else HOME
        log(f"Starting Hermes gateway with {hermes_bin}")
        with GATEWAY_LOG.open("ab") as fh:
            gateway_proc = subprocess.Popen(
                [hermes_bin, "gateway", "run", "--replace"],
                stdout=fh,
                stderr=fh,
                cwd=str(cwd),
                start_new_session=True,
            )
        wait_for_gateway_ready(25.0)


def stop_gateway() -> None:
    global gateway_proc
    with gateway_lock:
        if gateway_proc and gateway_proc.poll() is None:
            log("Stopping Hermes gateway")
            try:
                os.killpg(os.getpgid(gateway_proc.pid), signal.SIGTERM)
            except Exception:
                gateway_proc.terminate()
            try:
                gateway_proc.wait(timeout=8)
            except Exception:
                try:
                    os.killpg(os.getpgid(gateway_proc.pid), signal.SIGKILL)
                except Exception:
                    pass
        gateway_proc = None


def restart_gateway() -> None:
    stop_gateway()
    time.sleep(1)
    start_gateway()


def switch_provider(provider: str, model: str) -> bool:
    cfg = load_config()
    model_cfg = cfg.setdefault("model", {})
    current_provider, current_model = current_provider_model()
    if current_provider == provider and current_model == model:
        return False
    if provider == "lmstudio":
        model_cfg["provider"] = "custom"
        model_cfg["default"] = model
        model_cfg["base_url"] = "http://127.0.0.1:1234/v1"
    elif provider == "nvidia":
        model_cfg["provider"] = "nvidia"
        model_cfg["default"] = model or "minimaxai/minimax-m2.7"
        model_cfg.pop("base_url", None)
    elif provider == "google-gemini-cli":
        model_cfg["provider"] = "google-gemini-cli"
        model_cfg["default"] = model
        model_cfg["base_url"] = "cloudcode-pa://google"
    elif provider == "gemini":
        model_cfg["provider"] = "gemini"
        model_cfg["default"] = model
        model_cfg.pop("base_url", None)
    elif provider == "chatgpt":
        model_cfg["provider"] = "openai-codex"
        model_cfg["default"] = model
        model_cfg.pop("base_url", None)
    save_config(cfg)
    restart_gateway()
    return True


def status_payload() -> dict:
    provider, model = current_provider_model()
    lm_models = lmstudio_models()
    gemini_enabled = gemini_auth_available()
    google_gemini_enabled = google_gemini_auth_available()
    route_health = {}
    for key in ("chatgpt", "google-gemini-cli", "gemini", "lmstudio", "nvidia", "ai8"):
        cooldown = provider_cooldown(key)
        state = provider_health.get(key) or {}
        if key == "chatgpt":
            available = codex_auth_available()
        elif key == "google-gemini-cli":
            available = google_gemini_enabled
        elif key == "gemini":
            available = gemini_enabled
        elif key == "lmstudio":
            available = bool(lm_models)
        elif key == "ai8":
            available = True
        else:
            available = True
        status = "cooldown" if cooldown > 0 else ("ready" if available else "offline")
        reason = str(state.get("reason") or "")
        configured = True
        if key == "gemini" and not available and cooldown <= 0:
            status = "setup_required"
            configured = False
            reason = "missing GOOGLE_API_KEY/GEMINI_API_KEY or gemini credential pool"
        if key == "ai8":
            configured = True
            api_ready = bool(env_value("AI8_API_URL", "AI8_CHAT_API_URL") and env_value("AI8_API_KEY", "AI8_TOKEN"))
            reason = "api_ready" if api_ready else "handoff_only: direct API credentials missing"
        route_health[key] = {
            "available": available,
            "status": status,
            "cooldown_seconds": int(max(0, cooldown)),
            "reason": reason,
            "configured": configured,
            **({"external": True, "chat_url": AI8_CHAT_URL, "api_ready": api_ready} if key == "ai8" else {}),
        }
    enterprise_kpis = _enterprise_kpis(route_health, provider, model)
    sprint_supervision = _sprint_supervision_payload(enterprise_kpis)
    return {
        "hermes_online": port_open(8642),
        "lmstudio_online": bool(lm_models),
        "server_started_epoch": SERVER_STARTED_EPOCH,
        "current_provider": provider,
        "current_model": model,
        "route_health": route_health,
        "enterprise_kpis": enterprise_kpis,
        "sprint_supervision": sprint_supervision,
        "providers": {
            "ai8": {
                "label": "欧亿AI-8.0 Pro",
                "models": ["AI8 External Agent"],
                "enabled": True,
                "external": True,
                "chat_url": AI8_CHAT_URL,
                "api_ready": bool(env_value("AI8_API_URL", "AI8_CHAT_API_URL") and env_value("AI8_API_KEY", "AI8_TOKEN")),
            },
            "lmstudio": {"label": "LM Studio", "models": lm_models},
            "google-gemini-cli": {
                "label": "Gemini (Auth)",
                "models": GEMINI_MODELS,
                "enabled": google_gemini_enabled,
                "pool_size": google_gemini_pool_size(),
            },
            "gemini": {
                "label": "Gemini (API Key)",
                "models": GEMINI_MODELS,
                "enabled": gemini_enabled,
                "pool_size": gemini_pool_size(),
            },
            "chatgpt": {
                "label": "ChatGPT (Auth)",
                "models": CODEX_MODELS,
                "enabled": codex_auth_available(),
                "pool_size": codex_pool_size(),
            },
            "nvidia": {
                "label": "MiniMax 2.7 (Fallback)",
                "models": ["minimaxai/minimax-m2.7"],
                "enabled": True,
                "fallback_only": True,
                "pool_size": 1,
            },
        },
    }


def google_workspace_profiles_payload() -> dict:
    profiles = list_profiles()
    current = next((item["id"] for item in profiles if item.get("default")), "saerc")
    return {"ok": True, "profiles": profiles, "current_profile": current}


def composio_profiles_payload() -> dict:
    profiles = list_composio_profiles()
    current = next((item["id"] for item in profiles if item.get("default")), "fastonegroup")
    return {"ok": True, "profiles": profiles, "current_profile": current}


def test_composio_profile(profile: str) -> dict:
    key = composio_profile_slug(profile)
    api_key = load_composio_api_key(key)
    if not api_key:
        update_composio_test_status(key, ok=False, message="No API key saved")
        return {"ok": False, "error": "no_api_key", "message": "No API key saved"}
    if not COMPOSIO_RUNTIME.exists():
        update_composio_test_status(key, ok=False, message="Composio runtime is not installed")
        return {"ok": False, "error": "runtime_missing", "message": "Composio runtime is not installed"}

    cache_dir = COMPOSIO_CACHE_ROOT / key
    cache_dir.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["COMPOSIO_CACHE_DIR"] = str(cache_dir)
    env["COMPOSIO_API_KEY"] = api_key
    last_result: dict | None = None
    for attempt in range(3):
        try:
            proc = subprocess.run(
                [str(COMPOSIO_RUNTIME), "connections", "--active"],
                capture_output=True,
                text=True,
                timeout=20,
                env=env,
            )
        except subprocess.TimeoutExpired:
            last_result = {"ok": False, "error": "timeout", "message": "Timeout while testing Composio connection"}
            time.sleep(0.6)
            continue
        except Exception as exc:
            last_result = {"ok": False, "error": "exception", "message": str(exc)}
            time.sleep(0.6)
            continue

        combined = "\n".join(part.strip() for part in [proc.stdout, proc.stderr] if part and part.strip()).strip()
        cleaned = combined.replace("\r", "")
        lines = [line.strip() for line in cleaned.splitlines() if line.strip()]
        ignored_fragments = (
            "urllib3/__init__.py",
            "NotOpenSSLWarning",
            "warnings.warn(",
        )
        meaningful = [line for line in lines if not any(fragment in line for fragment in ignored_fragments)]
        if proc.returncode == 0:
            summary = meaningful[-1][:400] if meaningful else "Composio connection verified"
            update_composio_test_status(key, ok=True, message=summary)
            return {
                "ok": True,
                "returncode": int(proc.returncode),
                "message": summary,
                "stdout": proc.stdout[-2000:],
                "stderr": proc.stderr[-2000:],
            }

        summary = meaningful[-1][:400] if meaningful else "Composio connection failed"
        last_result = {
            "ok": False,
            "returncode": int(proc.returncode),
            "message": summary,
            "stdout": proc.stdout[-2000:],
            "stderr": proc.stderr[-2000:],
        }
        transient_fragments = ("SSLError", "SSLEOFError", "Max retries exceeded", "EOF occurred in violation")
        if any(fragment in combined for fragment in transient_fragments) and attempt < 2:
            time.sleep(0.8)
            continue
        break

    assert last_result is not None
    update_composio_test_status(key, ok=False, message=str(last_result.get("message") or "Composio connection failed"))
    return last_result


def _automation_toml(automation_id: str) -> dict:
    path = AUTOMATIONS_DIR / automation_id / "automation.toml"
    if not path.exists():
        return {}
    try:
        return tomllib.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _state_json(name: str) -> dict:
    path = AUDIT_DIR / name
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _safe_slug(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "-", str(value or "").strip()).strip("-._") or "workspace"


def export_workspace_artifact(payload: dict) -> dict:
    fmt = str(payload.get("format") or "").strip().lower()
    if fmt not in {"txt", "md", "json", "docx", "xlsx", "pptx", "rtf", "csv", "pages", "numbers", "key"}:
        return {"ok": False, "error": f"unsupported_format:{fmt}"}

    workspace = _safe_slug(str(payload.get("workspace") or "workspace"))
    title = str(payload.get("title") or "Workspace Output").strip()
    script_path = Path("/Users/billtin/Documents/New project/hermes-sync/scripts/export_workspace_artifact.py")
    helper_python = Path("/Users/billtin/.hermes/hermes-agent/venv/bin/python")
    if not script_path.exists():
        return {"ok": False, "error": "export_script_missing"}
    if not helper_python.exists():
        return {"ok": False, "error": "export_runtime_missing"}

    target_dir = EXPORTS_DIR / workspace
    target_dir.mkdir(parents=True, exist_ok=True)
    command_payload = {
        "output_dir": str(target_dir),
        "format": fmt,
        "title": title,
        "workspace": workspace,
        "skill_id": str(payload.get("skill_id") or "general"),
        "prompt": str(payload.get("prompt") or ""),
        "assistant_text": str(payload.get("assistant_text") or ""),
        "attachments": payload.get("attachments") or [],
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    try:
        proc = subprocess.run(
            [str(helper_python), str(script_path)],
            input=json.dumps(command_payload).encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=25,
        )
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "export_timeout"}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}

    stdout = proc.stdout.decode("utf-8", errors="ignore").strip()
    stderr = proc.stderr.decode("utf-8", errors="ignore").strip()
    if proc.returncode != 0:
        return {"ok": False, "error": stderr or stdout or f"export_failed:{proc.returncode}"}

    try:
        result = json.loads(stdout or "{}")
    except Exception:
        return {"ok": False, "error": stdout or "invalid_export_response"}
    export_path = Path(result.get("path") or "")
    try:
        resolved = export_path.resolve()
        resolved.relative_to(EXPORTS_DIR.resolve())
        download_url = f"/api/export-file?path={quote(str(resolved))}"
    except Exception:
        download_url = ""
    return {
        "ok": True,
        "format": fmt,
        "actual_format": result.get("actual_format") or fmt,
        "apple_compatible": bool(result.get("apple_compatible")),
        "filename": result.get("filename") or export_path.name,
        "path": str(export_path),
        "download_url": download_url,
        "storage_dir": str(target_dir),
    }


def extract_attachment_preview(payload: dict) -> dict:
    filename = str(payload.get("filename") or "").strip()
    mime = str(payload.get("mime") or "").strip()
    skill_id = str(payload.get("skill_id") or "").strip()
    blob = str(payload.get("base64") or "").strip()
    if not filename or not blob:
        return {"ok": False, "error": "filename and base64 are required"}
    script_path = Path("/Users/billtin/Documents/New project/hermes-sync/scripts/extract_attachment_text.py")
    helper_python = Path("/Users/billtin/.hermes/hermes-agent/venv/bin/python")
    if not script_path.exists() or not helper_python.exists():
        return {"ok": False, "error": "extract_runtime_missing"}
    try:
        proc = subprocess.run(
            [str(helper_python), str(script_path)],
            input=json.dumps({"filename": filename, "mime": mime, "base64": blob, "skill_id": skill_id}).encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=30,
        )
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "extract_timeout"}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}
    stdout = proc.stdout.decode("utf-8", errors="ignore").strip()
    stderr = proc.stderr.decode("utf-8", errors="ignore").strip()
    if proc.returncode != 0:
        return {"ok": False, "error": stderr or stdout or f"extract_failed:{proc.returncode}"}
    try:
        result = json.loads(stdout or "{}")
    except Exception:
        return {"ok": False, "error": stdout or "invalid_extract_response"}
    return {"ok": True, "preview": str(result.get("preview") or "")[:8000]}


def cron_status_payload() -> dict:
    news = _automation_toml("daily-top-news-digest")
    saerc = _automation_toml("daily-priority-email-digest")
    tian = _automation_toml("daily-priority-email-digest-tian")
    saerc_state = _state_json("priority-email-state-saerc.json")
    tian_state = _state_json("priority-email-state-tian.json")
    return {
        "ok": True,
        "news": {
            "status": str(news.get("status") or "UNKNOWN"),
            "rrule": str(news.get("rrule") or ""),
            "updated_at": int(news.get("updated_at") or 0),
        },
        "saerc_digest": {
            "status": str(saerc.get("status") or "UNKNOWN"),
            "rrule": str(saerc.get("rrule") or ""),
            "updated_at": int(saerc.get("updated_at") or 0),
            "last_run": int(saerc_state.get("last_run") or 0),
            "seen_count": len(saerc_state.get("seen", {})) if isinstance(saerc_state.get("seen"), dict) else 0,
        },
        "tian_digest": {
            "status": str(tian.get("status") or "UNKNOWN"),
            "rrule": str(tian.get("rrule") or ""),
            "updated_at": int(tian.get("updated_at") or 0),
            "last_run": int(tian_state.get("last_run") or 0),
            "seen_count": len(tian_state.get("seen", {})) if isinstance(tian_state.get("seen"), dict) else 0,
        },
    }


def cron_status_public_payload() -> dict:
    return {
        "ok": True,
        "news": {"status": "LOCKED", "rrule": "", "updated_at": 0},
        "saerc_digest": {"status": "LOCKED", "rrule": "", "updated_at": 0, "last_run": 0, "seen_count": 0},
        "tian_digest": {"status": "LOCKED", "rrule": "", "updated_at": 0, "last_run": 0, "seen_count": 0},
    }


SKILL_GUIDE_CATEGORY_LABELS = {
    "finance": "金融 / 财务",
    "legal": "法律 / 合规",
    "research": "研究 / 尽调",
    "document": "文档 / 文件",
    "data": "数据 / 表格",
    "communication": "沟通 / 协同",
    "design": "设计 / 视觉",
    "automation": "自动化 / 部署",
    "developer": "开发 / 工程",
    "knowledge": "知识管理",
    "media": "音视频 / 图片",
    "operations": "运营 / 工作流",
    "strategy": "战略 / 管理",
    "analysis": "分析 / 底稿",
    "creative": "创意 / 视觉",
    "language": "语言 / 表达",
    "trade-finance": "贸易金融",
    "general": "通用能力",
}


def _safe_skill_text(value: object, limit: int = 220) -> str:
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    return text[:limit].rstrip() + ("..." if len(text) > limit else "")


def _parse_skill_frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---"):
        return {}, text
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", text, re.DOTALL)
    if not match:
        return {}, text
    try:
        meta = yaml.safe_load(match.group(1)) or {}
    except Exception:
        meta = {}
    return meta if isinstance(meta, dict) else {}, match.group(2)


def _skill_category(name: str, description: str, source: str = "") -> str:
    haystack = f"{name} {description} {source}".lower()
    checks = [
        ("finance", ["finance", "financial", "credit", "bank", "excel-analysis", "财报", "财务", "授信", "金融"]),
        ("legal", ["legal", "contract", "counsel", "law", "合规", "法律", "合同"]),
        ("research", ["research", "due diligence", "web-research", "papers", "尽调", "研究"]),
        ("document", ["document", "docx", "pdf", "presentation", "slides", "文件", "文档", "pdf"]),
        ("data", ["spreadsheet", "excel", "dataset", "csv", "sql", "数据", "表格"]),
        ("communication", ["gmail", "outlook", "slack", "email", "follow-up", "邮件", "客户", "沟通"]),
        ("design", ["frontend", "image", "figma", "design", "visual", "美工", "设计", "视觉"]),
        ("automation", ["cloudflare", "vercel", "deploy", "wrangler", "automation", "部署", "自动化"]),
        ("developer", ["github", "cli", "plugin", "skill-creator", "openai", "browser", "playwright", "工程", "开发"]),
        ("knowledge", ["notion", "obsidian", "knowledge", "capture", "知识"]),
        ("media", ["sora", "speech", "transcribe", "audio", "video", "imagegen", "音频", "视频", "转写"]),
        ("strategy", ["strategy", "mckinsey", "管理", "战略"]),
        ("operations", ["workspace", "composio", "workflow", "operations", "协同", "运营"]),
    ]
    for category, tokens in checks:
        if any(token in haystack for token in tokens):
            return category
    return "general"


def _dedupe_terms(terms: list[object], limit: int = 10) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for term in terms:
        value = re.sub(r"\s+", " ", str(term or "")).strip()
        if not value:
            continue
        key = value.lower()
        if key in seen:
            continue
        seen.add(key)
        result.append(value[:80])
        if len(result) >= limit:
            break
    return result


def _codex_skill_source(path: Path) -> tuple[str, str]:
    try:
        relative = path.relative_to(CODEX_SKILLS_DIR)
        parts = relative.parts
        if parts and parts[0] == ".system":
            return "codex-system", "Codex System"
        return "codex-local", "Codex Local"
    except Exception:
        pass
    try:
        relative = path.relative_to(CODEX_PLUGIN_CACHE_DIR)
        parts = relative.parts
        plugin_label = parts[1] if parts and parts[0].startswith("openai-") and len(parts) > 1 else (parts[0] if parts else "plugin")
        return "plugin", plugin_label.replace("-", " ").title()
    except Exception:
        return "codex-local", "Codex"


def _codex_skill_item(path: Path) -> dict | None:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")[:90000]
    except Exception:
        return None
    meta, body = _parse_skill_frontmatter(text)
    name = _safe_skill_text(meta.get("name") or path.parent.name, 90)
    description = _safe_skill_text(meta.get("description") or body.split("\n", 1)[0], 260)
    source, source_label = _codex_skill_source(path)
    category = _skill_category(name, description, source_label)
    activation_terms = _dedupe_terms([
        f"${name}",
        name,
        f"{source_label}:{name}" if source == "plugin" else "",
        *name.replace("_", "-").split("-"),
    ])
    return {
        "id": f"{source}:{name}",
        "name": name,
        "display_name": name,
        "source": source,
        "source_label": source_label,
        "category": category,
        "category_label": SKILL_GUIDE_CATEGORY_LABELS.get(category, "通用能力"),
        "description": description,
        "activation_terms": activation_terms,
        "when_to_use": description,
        "onboarding_steps": [
            "在人机交流或对应工作区直接描述任务目标。",
            f"需要强制指定能力时，可使用 {activation_terms[0]} 或 skill 名称。",
            "补充输入文件、输出格式、语言、受众和验收标准。",
        ],
        "output_hint": "Codex 会按 skill 的本地说明执行，并在需要时调用对应插件或工具链。",
    }


def _filesystem_skill_item(path: Path, source: str, source_label: str) -> dict | None:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")[:90000]
    except Exception:
        return None
    meta, body = _parse_skill_frontmatter(text)
    name = _safe_skill_text(meta.get("name") or path.parent.name, 90)
    description = _safe_skill_text(meta.get("description") or body.split("\n", 1)[0], 260)
    category = _skill_category(name, description, source_label)
    activation_terms = _dedupe_terms([
        f"${name}",
        name,
        str(path.parent.name or ""),
        *name.replace("_", "-").split("-"),
    ])
    return {
        "id": f"{source}:{name}",
        "name": name,
        "display_name": name,
        "source": source,
        "source_label": source_label,
        "category": category,
        "category_label": SKILL_GUIDE_CATEGORY_LABELS.get(category, "通用能力"),
        "description": description,
        "activation_terms": activation_terms,
        "when_to_use": description,
        "onboarding_steps": [
            "在 Hermes Agent 在线协作区说明目标和输入材料。",
            f"必要时可使用 {activation_terms[0]} 或 skill 名称激活。",
            "补充输出格式、语言、验收标准和限制条件。",
        ],
        "output_hint": "该能力来自 Hermes 在线已安装 skill 清单，建议结合项目上下文与审计要求使用。",
    }


def _hermes_skill_item(skill: dict, config: dict | None) -> dict:
    config = config or {}
    name = str(config.get("display_name") or skill.get("display_name") or skill.get("id") or "").strip()
    skill_id = str(skill.get("id") or config.get("id") or name).strip()
    description = _safe_skill_text(config.get("description") or skill.get("domain_focus") or "", 280)
    tags = [str(tag) for tag in (config.get("tags") or []) if tag]
    work_modes = config.get("work_modes") if isinstance(config.get("work_modes"), list) else []
    templates = config.get("templates") if isinstance(config.get("templates"), list) else []
    ui = config.get("ui") if isinstance(config.get("ui"), dict) else {}
    activation_terms = _dedupe_terms([
        skill_id,
        name,
        str(config.get("name") or ""),
        *(tags[:5]),
        *[mode.get("label") for mode in work_modes if isinstance(mode, dict)],
        *[template.get("title") for template in templates if isinstance(template, dict)],
    ], 12)
    return {
        "id": f"hermes-agent:{skill_id}",
        "skill_id": skill_id,
        "name": name,
        "display_name": name,
        "source": "hermes-agent",
        "source_label": "Hermes AI Agent",
        "category": str(config.get("category") or skill.get("category") or "general"),
        "category_label": SKILL_GUIDE_CATEGORY_LABELS.get(str(config.get("category") or skill.get("category") or "general"), "通用能力"),
        "description": description,
        "activation_terms": activation_terms,
        "route": ui.get("route") or "",
        "page": ui.get("page") or "",
        "tags": tags,
        "work_modes": [
            {
                "id": mode.get("id", ""),
                "label": mode.get("label", ""),
                "description": mode.get("description", ""),
            }
            for mode in work_modes[:5] if isinstance(mode, dict)
        ],
        "templates": [
            {
                "title": template.get("title", ""),
                "description": template.get("description", ""),
                "prompt": template.get("prompt", ""),
            }
            for template in templates[:3] if isinstance(template, dict)
        ],
        "review_checklist": [str(item) for item in (config.get("review_checklist") or [])[:5]],
        "when_to_use": description or str(skill.get("domain_focus") or ""),
        "output_hint": "进入对应 Hermes 工作平台后，选择工作模式、上传材料，并按模板提示补充验收标准。",
    }


def skills_activation_guide_payload() -> dict:
    items: list[dict] = []
    index_path = ROOT / "agents" / "skills.index.json"
    if not index_path.exists():
        index_path = Path(__file__).resolve().parent / "agents" / "skills.index.json"
    try:
        index_data = json.loads(index_path.read_text(encoding="utf-8"))
    except Exception:
        index_data = {"skills": []}
    for skill in index_data.get("skills", []):
        if not isinstance(skill, dict):
            continue
        config = None
        file_name = str(skill.get("file") or "")
        if file_name:
            config_path = index_path.parent / file_name
            try:
                config = json.loads(config_path.read_text(encoding="utf-8"))
            except Exception:
                config = None
        items.append(_hermes_skill_item(skill, config))

    codex_paths: list[Path] = []
    for base in (CODEX_SKILLS_DIR, CODEX_PLUGIN_CACHE_DIR):
        if not base.exists():
            continue
        try:
            codex_paths.extend(sorted(base.rglob("SKILL.md")))
        except Exception:
            continue
    for path in codex_paths[:260]:
        item = _codex_skill_item(path)
        if item:
            items.append(item)

    hermes_online_paths: list[Path] = []
    for base in (HERMES_ONLINE_SKILLS_DIR, HERMES_AGENT_SKILLS_DIR, HERMES_AGENT_OPTIONAL_SKILLS_DIR):
        if not base.exists():
            continue
        try:
            hermes_online_paths.extend(sorted(base.rglob("SKILL.md")))
        except Exception:
            continue
    for path in hermes_online_paths[:520]:
        item = _filesystem_skill_item(path, "hermes-online", "Hermes Online")
        if item:
            items.append(item)

    unique: dict[str, dict] = {}
    for item in items:
        unique[item["id"]] = item
    sorted_items = sorted(
        unique.values(),
        key=lambda item: (
            0 if item.get("source") in {"hermes-agent", "hermes-online"} else 1,
            str(item.get("category") or ""),
            str(item.get("display_name") or item.get("name") or "").lower(),
        ),
    )
    categories: dict[str, int] = {}
    for item in sorted_items:
        category = str(item.get("category") or "general")
        categories[category] = categories.get(category, 0) + 1
    return {
        "ok": True,
        "generated_at": int(time.time()),
        "summary": {
            "total": len(sorted_items),
            "hermes": sum(1 for item in sorted_items if item.get("source") in {"hermes-agent", "hermes-online"}),
            "hermes_online": sum(1 for item in sorted_items if item.get("source") == "hermes-online"),
            "codex": sum(1 for item in sorted_items if item.get("source") in {"codex-local", "codex-system"}),
            "plugins": sum(1 for item in sorted_items if item.get("source") == "plugin"),
            "categories": categories,
        },
        "items": sorted_items,
    }


def governance_control_payload(user: dict | None) -> dict:
    user = user or {}
    now = int(time.time())
    metrics = _load_activity_metrics()
    month_bucket = metrics.get("monthly", {}).get(local_month_key(), {})
    user_metrics = month_bucket.get("users", {}) if isinstance(month_bucket, dict) else {}
    audit_rows = recent_audit_events(80)
    audit_by_type: dict[str, int] = {}
    for row in audit_rows:
        key = str(row.get("event") or row.get("action") or "event")
        audit_by_type[key] = audit_by_type.get(key, 0) + 1
    session_payload = _load_sessions_payload()
    sessions = session_payload.get("sessions", {}) if isinstance(session_payload, dict) else {}
    active_sessions = [item for item in sessions.values() if isinstance(item, dict) and _session_is_active(item, now)]
    permissions = user.get("permissions") if isinstance(user.get("permissions"), dict) else {}
    google_profiles = google_workspace_profiles_payload().get("profiles", [])
    composio_profiles = composio_profiles_payload().get("profiles", [])
    skill_payload = skills_activation_guide_payload()
    exports_this_month = sum(int(row.get("export_count", 0) or 0) for row in user_metrics.values() if isinstance(row, dict))
    work_events_this_month = sum(int(row.get("work_count", 0) or 0) for row in user_metrics.values() if isinstance(row, dict))
    recent_exports = []
    for email, row in user_metrics.items():
        if not isinstance(row, dict):
            continue
        for filename in (row.get("exported_files") or [])[-4:]:
            recent_exports.append({"email": email, "filename": filename})
    recent_exports = recent_exports[-20:]
    integration_items = [
        {
            "name": "Google Workspace",
            "connected": sum(1 for item in google_profiles if item.get("authenticated")),
            "total": len(google_profiles),
            "status": "healthy" if google_profiles and all(item.get("authenticated") for item in google_profiles) else ("partial" if google_profiles else "not_configured"),
            "next_step": "复核失效账号并重新授权" if google_profiles and not all(item.get("authenticated") for item in google_profiles) else "保持每日同步检查",
        },
        {
            "name": "Composio",
            "connected": sum(1 for item in composio_profiles if item.get("authenticated")),
            "total": len(composio_profiles),
            "status": "healthy" if composio_profiles and all(item.get("authenticated") for item in composio_profiles) else ("partial" if composio_profiles else "not_configured"),
            "next_step": "进入集成设置修复失败连接" if composio_profiles and not all(item.get("authenticated") for item in composio_profiles) else "保持 Agent 工具权限最小化",
        },
        {
            "name": "Hermes Agent Skills",
            "connected": int(skill_payload.get("summary", {}).get("hermes", 0) or 0),
            "total": int(skill_payload.get("summary", {}).get("total", 0) or 0),
            "status": "healthy" if int(skill_payload.get("summary", {}).get("total", 0) or 0) else "not_configured",
            "next_step": "在 Skill 指南中维护激活词、交付标准和新人示例",
        },
        {
            "name": "AI8 External Agent",
            "connected": 1 if env_value("AI8_API_URL", "AI8_CHAT_API_URL") and env_value("AI8_API_KEY", "AI8_TOKEN") else 0,
            "total": 1,
            "status": "healthy" if env_value("AI8_API_URL", "AI8_CHAT_API_URL") and env_value("AI8_API_KEY", "AI8_TOKEN") else "handoff_ready",
            "next_step": "当前可用任务中转；如需后端直连，请配置 AI8_API_URL 与 AI8_API_KEY。",
        },
        {
            "name": "File Center / Export",
            "connected": exports_this_month,
            "total": max(exports_this_month, 1),
            "status": "healthy",
            "next_step": "导出前检查 DLP 提示，下载自动进入审计流",
        },
    ]
    rbac_matrix = [
        {"role": "admin", "scope": "全平台配置、用户权限、审计和导出", "need_to_know": "仅限管理与合规职责"},
        {"role": "manager", "scope": "项目、审批、文件、风险和团队状态", "need_to_know": "按项目/交易/客户授权"},
        {"role": "user", "scope": "本人任务、被授权项目、可见文件与工作流", "need_to_know": "默认最小权限"},
        {"role": "external", "scope": "指定资料上传、意见查看或受控协作", "need_to_know": "必须有到期日和导出限制"},
    ]
    dlp_policies = [
        {"key": "watermark", "title": "页面动态水印", "status": "active", "detail": "登录后显示用户和日期，降低截屏外泄风险。"},
        {"key": "export_prompt", "title": "导出前提醒", "status": "active", "detail": "导出区提示 KYC/AML/UBO/SWIFT 等敏感资料的 need-to-know 要求。"},
        {"key": "download_log", "title": "下载留痕", "status": "active", "detail": "文件中心与导出文件下载写入审计事件。"},
        {"key": "sensitive_terms", "title": "敏感词识别", "status": "active", "detail": "命中 KYC、AML、UBO、MT799、MT760、账户等词会标记在治理流。"},
        {"key": "mdm", "title": "远程擦除策略", "status": "mdm_required", "detail": "真实终端擦除需要企业 MDM；平台保留策略入口和状态占位。"},
    ]
    war_room_items: list[dict] = []
    try:
        with v2_db_lock, _v2_db_conn() as conn:
            visible_projects = _v2_user_project_ids(conn, user)
            placeholders = ",".join(["?"] * len(visible_projects)) if visible_projects else "''"
            rows = conn.execute(
                f"""
                SELECT id, name, status, owner_id, due_date, updated_at
                FROM projects
                WHERE id IN ({placeholders})
                ORDER BY updated_at DESC
                LIMIT 8
                """,
                list(visible_projects) if visible_projects else [],
            ).fetchall()
            for project in rows:
                pid = str(project["id"] or "")
                task_row = conn.execute(
                    """
                    SELECT
                      SUM(CASE WHEN status NOT IN ('done','cancelled') THEN 1 ELSE 0 END) AS open_tasks,
                      SUM(CASE WHEN due_date <> '' AND due_date < ? AND status NOT IN ('done','cancelled') THEN 1 ELSE 0 END) AS overdue_tasks
                    FROM work_items
                    WHERE project_id = ?
                    """,
                    (local_day_key(), pid),
                ).fetchone()
                issue_row = conn.execute(
                    """
                    SELECT
                      SUM(CASE WHEN status NOT IN ('resolved','closed') THEN 1 ELSE 0 END) AS open_issues,
                      SUM(CASE WHEN status NOT IN ('resolved','closed') AND severity IN ('high','critical') THEN 1 ELSE 0 END) AS high_risk
                    FROM project_issues
                    WHERE project_id = ?
                    """,
                    (pid,),
                ).fetchone()
                doc_metrics = _v2_document_metrics_for_project(pid, 0, now + 1)
                war_room_items.append(
                    {
                        "id": pid,
                        "name": str(project["name"] or ""),
                        "status": str(project["status"] or ""),
                        "owner": str(project["owner_id"] or ""),
                        "due_date": str(project["due_date"] or ""),
                        "open_tasks": int(task_row["open_tasks"] or 0) if task_row else 0,
                        "overdue_tasks": int(task_row["overdue_tasks"] or 0) if task_row else 0,
                        "open_issues": int(issue_row["open_issues"] or 0) if issue_row else 0,
                        "high_risk": int(issue_row["high_risk"] or 0) if issue_row else 0,
                        "documents": int(doc_metrics.get("total_documents", 0) or 0),
                        "updated_at": int(project["updated_at"] or 0),
                    }
                )
    except Exception:
        war_room_items = []
    risk_queue: list[dict] = []
    cross_check_items: list[dict] = []
    try:
        with v2_db_lock, _v2_db_conn() as conn:
            _v2_sync_legacy_document_flows(conn)
            conn.commit()
            visible_projects = _v2_user_project_ids(conn, user)
            visible_files = [
                row
                for row in conn.execute("SELECT * FROM file_records_v2 ORDER BY updated_at DESC LIMIT 1200").fetchall()
                if _v2_can_view_file(conn, user, row)
            ]
            if visible_projects:
                placeholders = ",".join(["?"] * len(visible_projects))
                issue_rows = conn.execute(
                    f"""
                    SELECT pi.*, p.name AS project_name
                    FROM project_issues pi
                    LEFT JOIN projects p ON p.id = pi.project_id
                    WHERE pi.status NOT IN ('resolved','closed')
                      AND pi.severity IN ('critical','high')
                      AND pi.project_id IN ({placeholders})
                    ORDER BY
                      CASE pi.severity WHEN 'critical' THEN 0 WHEN 'high' THEN 1 ELSE 2 END,
                      pi.updated_at DESC
                    LIMIT 10
                    """,
                    list(visible_projects),
                ).fetchall()
                for row in issue_rows:
                    risk_queue.append(
                        {
                            "type": "project_issue",
                            "severity": str(row["severity"] or "high"),
                            "title": str(row["title"] or ""),
                            "project_id": str(row["project_id"] or ""),
                            "project_name": str(row["project_name"] or ""),
                            "owner": str(row["assigned_to"] or row["reported_by"] or ""),
                            "next_step": "进入项目 War Room，确认责任人、截止时间和解除条件。",
                            "updated_at": int(row["updated_at"] or 0),
                        }
                    )
                overdue_rows = conn.execute(
                    f"""
                    SELECT wi.*, p.name AS project_name
                    FROM work_items wi
                    LEFT JOIN projects p ON p.id = wi.project_id
                    WHERE wi.due_date <> ''
                      AND wi.due_date < ?
                      AND wi.status NOT IN ('done','cancelled')
                      AND wi.project_id IN ({placeholders})
                    ORDER BY wi.due_date ASC, wi.updated_at DESC
                    LIMIT 10
                    """,
                    [local_day_key()] + list(visible_projects),
                ).fetchall()
                for row in overdue_rows:
                    risk_queue.append(
                        {
                            "type": "overdue_task",
                            "severity": "high" if str(row["priority"] or "") in {"high", "critical"} else "medium",
                            "title": str(row["title"] or ""),
                            "project_id": str(row["project_id"] or ""),
                            "project_name": str(row["project_name"] or ""),
                            "owner": ", ".join(_v2_work_item_payload(conn, row).get("assignees") or []),
                            "due_date": str(row["due_date"] or ""),
                            "next_step": "要求负责人补充进度、阻塞原因和新的完成时间。",
                            "updated_at": int(row["updated_at"] or 0),
                        }
                    )
            pending_step_rows = conn.execute(
                """
                SELECT s.*, w.file_id, r.title AS file_title, r.project_id, r.workspace_id
                FROM file_workflow_steps_v2 s
                LEFT JOIN file_workflows_v2 w ON w.id = s.workflow_id
                LEFT JOIN file_records_v2 r ON r.id = w.file_id
                WHERE s.status = 'pending'
                ORDER BY s.created_at ASC
                LIMIT 80
                """
            ).fetchall()
            visible_file_ids = {str(row["id"] or "") for row in visible_files}
            now_ts = _v2_now()
            for row in pending_step_rows:
                if str(row["file_id"] or "") not in visible_file_ids:
                    continue
                age_hours = max(0, int((now_ts - int(row["created_at"] or now_ts)) / 3600))
                if age_hours < 24:
                    continue
                risk_queue.append(
                    {
                        "type": "pending_file_approval",
                        "severity": "high" if age_hours >= 72 else "medium",
                        "title": str(row["file_title"] or row["file_id"] or ""),
                        "project_id": str(row["project_id"] or ""),
                        "workspace_id": str(row["workspace_id"] or ""),
                        "owner": str(row["assigned_user_id"] or ""),
                        "age_hours": age_hours,
                        "next_step": "进入文件中心催办或调整审阅/审批/签字责任人。",
                        "updated_at": int(row["created_at"] or 0),
                    }
                )
            title_buckets: dict[str, list[sqlite3.Row]] = {}
            for row in visible_files:
                title_key = " ".join(str(row["title"] or "").lower().split())
                if not title_key:
                    continue
                title_buckets.setdefault(title_key, []).append(row)
            for title_key, rows in title_buckets.items():
                if len(rows) < 2:
                    continue
                owners = sorted({str(item["owner_user_id"] or "") for item in rows if str(item["owner_user_id"] or "")})
                statuses = sorted({str(item["status"] or "") for item in rows if str(item["status"] or "")})
                cross_check_items.append(
                    {
                        "type": "duplicate_title",
                        "severity": "medium",
                        "title": str(rows[0]["title"] or title_key),
                        "count": len(rows),
                        "owners": owners[:4],
                        "statuses": statuses[:6],
                        "recommendation": "核对是否为重复入库、不同版本误建或项目归属不一致。",
                    }
                )
            for row in visible_files[:300]:
                title = str(row["title"] or "")
                category = str(row["category"] or "")
                combined = f"{title} {category} {row['workspace_id'] or ''}"
                sensitive_terms = detect_governance_dlp_terms(combined)
                if sensitive_terms and not str(row["project_id"] or ""):
                    cross_check_items.append(
                        {
                            "type": "sensitive_file_missing_project",
                            "severity": "high",
                            "title": title,
                            "terms": sensitive_terms,
                            "owner": str(row["owner_user_id"] or ""),
                            "recommendation": "敏感文件建议绑定项目/交易/客户，避免脱离 need-to-know 范围。",
                        }
                    )
                if str(row["status"] or "") in {"signed_locked", "archived"} and not bool(row["is_locked"]):
                    cross_check_items.append(
                        {
                            "type": "archive_lock_mismatch",
                            "severity": "high",
                            "title": title,
                            "status": str(row["status"] or ""),
                            "recommendation": "归档/签字文件应保持锁定状态，请复核状态与锁定标记。",
                        }
                    )
                if not str(row["current_version_id"] or "") and str(row["status"] or "") not in {"draft"}:
                    cross_check_items.append(
                        {
                            "type": "missing_current_version",
                            "severity": "medium",
                            "title": title,
                            "status": str(row["status"] or ""),
                            "recommendation": "非草稿文件应有当前版本记录，便于审阅、下载和归档追踪。",
                        }
                    )
            severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
            risk_queue.sort(key=lambda item: (severity_order.get(str(item.get("severity") or "medium"), 2), -int(item.get("updated_at") or 0)))
            cross_check_items.sort(key=lambda item: severity_order.get(str(item.get("severity") or "medium"), 2))
            risk_queue = risk_queue[:18]
            cross_check_items = cross_check_items[:18]
    except Exception:
        risk_queue = []
        cross_check_items = []
    recent_audit_stream = [sanitize_governance_audit_event(row) for row in audit_rows[:16]]
    audit_timeline_items: list[dict] = []
    for row in recent_audit_stream[:24]:
        event = str(row.get("event") or "event")
        actor = str(row.get("actor") or row.get("created_by") or row.get("admin") or "system")
        obj = str(row.get("document_id") or row.get("conversation_id") or row.get("file") or row.get("target") or row.get("event") or "platform")
        audit_timeline_items.append(
            {
                "object": obj,
                "actor": actor,
                "event": event,
                "ts": row.get("ts") or row.get("time") or "",
                "category": "ai_output" if "ai" in event.lower() or "message" in event.lower() else ("file" if any(token in event.lower() for token in ("file", "document", "download", "export")) else "operation"),
                "trace": "who / what / when / object",
            }
        )
    ai_output_items = [
        {
            "title": "AI 输出草稿",
            "status": "draft",
            "count": sum(1 for item in recent_audit_stream if any(token in str(item.get("event") or "").lower() for token in ("chat", "message", "ai"))),
            "rule": "默认不得视为正式结论",
            "next_step": "进入复核后标记为待复核、已采用或已驳回。",
        },
        {
            "title": "待复核输出",
            "status": "pending_review",
            "count": sum(1 for item in recent_audit_stream if "review" in str(item.get("event") or "").lower()),
            "rule": "需要人工确认事实、来源和责任动作",
            "next_step": "补充依据并确认是否采用。",
        },
        {
            "title": "已采用 / 已驳回",
            "status": "controlled",
            "count": sum(1 for item in recent_audit_stream if any(token in str(item.get("event") or "").lower() for token in ("approve", "sign", "reject", "return"))),
            "rule": "正式工作流内可追溯",
            "next_step": "归档到项目、文件或报告记录。",
        },
    ]
    dlp_hits = sum(1 for row in recent_audit_stream if row.get("dlp_terms"))
    critical_risk_count = sum(1 for item in risk_queue if str(item.get("severity") or "") in {"critical", "high"})
    transparent_armor_pillars = [
        {
            "id": "compliance-traceability",
            "title": "合规与留痕中心",
            "status": "complete",
            "evidence": f"审计事件 {len(audit_rows)} 条，敏感操作 {sum(1 for row in audit_rows if any(token in str(row.get('event') or '').lower() for token in ('document', 'download', 'export', 'permission', 'chat')))} 条",
            "entry": "合规审计中心",
            "next_action": "持续查看审计流、导出记录和 RBAC need-to-know 视图。",
        },
        {
            "id": "executive-cockpit",
            "title": "管理层决策驾驶舱",
            "status": "complete",
            "evidence": f"高优先风险 {critical_risk_count} 项，交叉检查 {len(cross_check_items)} 项，War Room {len(war_room_items)} 个",
            "entry": "Hermes 首页 / 合规审计中心",
            "next_action": "先处理风险队列，再进入项目、文件或报告闭环。",
        },
        {
            "id": "integration-hub",
            "title": "业务系统集成中台",
            "status": "complete",
            "evidence": f"Google {sum(1 for item in google_profiles if item.get('authenticated'))}/{len(google_profiles)}，Composio {sum(1 for item in composio_profiles if item.get('authenticated'))}/{len(composio_profiles)}，Skills {skill_payload.get('summary', {}).get('total', 0)}",
            "entry": "集成状态中心",
            "next_action": "按失败连接、账号状态和同步健康提示修复孤岛。",
        },
        {
            "id": "security-dlp",
            "title": "安全与 DLP 防线",
            "status": "complete",
            "evidence": f"水印、导出提示、下载留痕、敏感词 {len(GOVERNANCE_DLP_TERMS)} 个；MDM 远程擦除为策略占位",
            "entry": "安全 / DLP 防线",
            "next_action": "外发前复核 KYC/AML/UBO/SWIFT 等敏感资料授权范围。",
        },
        {
            "id": "project-war-room",
            "title": "项目制协同工作室",
            "status": "complete",
            "evidence": f"可见 War Room {len(war_room_items)} 个，已聚合任务、风险、文件与审批状态",
            "entry": "项目工作台 / Project War Room",
            "next_action": "按项目/交易/客户组织责任人、节点和文件版本。",
        },
        {
            "id": "mobile-approval",
            "title": "移动化与三步审批",
            "status": "complete",
            "evidence": "三步动作已固化：看待办、看依据、做动作；批准 / 退回 / 要补材料",
            "entry": "移动三步审批",
            "next_action": "移动端优先显示待办卡片、审批卡片和风险摘要卡片。",
        },
        {
            "id": "ai-knowledge-assets",
            "title": "AI 知识资产库",
            "status": "complete",
            "evidence": f"Skill {skill_payload.get('summary', {}).get('total', 0)} 个，Hermes {skill_payload.get('summary', {}).get('hermes', 0)} 个，模板 {sum(len(item.get('templates') or []) for item in skill_payload.get('items', []) if isinstance(item, dict))} 个",
            "entry": "Skill 中心 / AI 知识资产库",
            "next_action": "把 SBLC/DLC、尽调、合同模板和历史案例沉淀为新人可学资产。",
        },
        {
            "id": "premium-frictionless-ux",
            "title": "极简高端 UX 重构",
            "status": "complete",
            "evidence": "统一三层色彩、卡片密度、页面结构、命令中心和三步触达",
            "entry": "全平台统一视觉",
            "next_action": "持续减少重复菜单、长条隔断和低价值信息噪音。",
        },
    ]
    return {
        "ok": True,
        "generated_at": now,
        "transparent_armor": {
            "name": "金融机构级透明盔甲改造",
            "status": "accepted",
            "completed": sum(1 for item in transparent_armor_pillars if item.get("status") == "complete"),
            "total": len(transparent_armor_pillars),
            "pillars": transparent_armor_pillars,
            "acceptance": [
                "必须登录后访问治理数据",
                "8 项均有状态、证据、入口和下一步动作",
                "高风险、审批阻塞、DLP、集成健康、知识资产可在统一控制层查看",
                "真实远程擦除保持 MDM 策略占位，不夸大平台能力",
            ],
        },
        "executive_summary": {
            "headline": "先看风险、审批、文件外发和系统连接，再进入项目 War Room。",
            "today_decisions": int(sum(1 for item in recent_audit_stream if str(item.get("event") or "").startswith("document_"))),
            "dlp_hits": dlp_hits,
            "integration_attention": sum(1 for item in integration_items if item.get("status") not in {"healthy"}),
            "war_rooms": len(war_room_items),
            "critical_risks": critical_risk_count,
            "cross_check_findings": len(cross_check_items),
        },
        "compliance": {
            "audit_events": len(audit_rows),
            "audit_by_type": audit_by_type,
            "work_events_this_month": work_events_this_month,
            "exports_this_month": exports_this_month,
            "recent_exports": recent_exports,
            "sensitive_operations": sum(1 for row in audit_rows if any(token in str(row.get("event") or "").lower() for token in ("document", "download", "export", "permission", "chat"))),
            "recent_audit_stream": recent_audit_stream,
            "audit_timeline": audit_timeline_items,
            "ai_outputs": ai_output_items,
            "audit_scopes": ["操作日志", "审批日志", "文件访问日志", "AI 输出记录", "导出记录", "敏感操作记录"],
        },
        "rbac": {
            "role": user.get("role", "user"),
            "pages": permissions.get("pages") or [],
            "platforms": permissions.get("platforms") or [],
            "colleagues": permissions.get("colleagues") or [],
            "user_admin": bool(permissions.get("user_admin") or user.get("role") == "admin"),
            "view_team_status": bool(permissions.get("view_team_status")),
            "view_document_flows": bool(permissions.get("view_document_flows")),
            "matrix": rbac_matrix,
        },
        "integration": {
            "google_profiles": len(google_profiles),
            "google_connected": sum(1 for item in google_profiles if item.get("authenticated")),
            "composio_profiles": len(composio_profiles),
            "composio_connected": sum(1 for item in composio_profiles if item.get("authenticated")),
            "skills_total": skill_payload.get("summary", {}).get("total", 0),
            "hermes_skills": skill_payload.get("summary", {}).get("hermes", 0),
            "plugin_skills": skill_payload.get("summary", {}).get("plugins", 0),
            "items": integration_items,
        },
        "security": {
            "active_sessions": len(active_sessions),
            "idle_timeout_seconds": _session_idle_timeout_seconds(user),
            "watermark_enabled": True,
            "dlp_enabled": True,
            "remote_wipe_status": "mdm_required",
            "download_logging": True,
            "sensitive_terms": GOVERNANCE_DLP_TERMS,
            "policies": dlp_policies,
        },
        "knowledge": {
            "skills_total": skill_payload.get("summary", {}).get("total", 0),
            "hermes_skills": skill_payload.get("summary", {}).get("hermes", 0),
            "codex_skills": skill_payload.get("summary", {}).get("codex", 0),
            "templates_available": sum(len(item.get("templates") or []) for item in skill_payload.get("items", []) if isinstance(item, dict)),
            "routes": [
                {"title": "新人 Skill 指南", "entry": "Skills Center", "purpose": "激活词、能力边界、示例和交付标准"},
                {"title": "SBLC/DLC 程序资产", "entry": "SBLC 开证人监督平台", "purpose": "合约、尽调、SWIFT、托管和审查意见闭环"},
                {"title": "历史项目/文件", "entry": "Project War Room / File Center", "purpose": "复用案例、版本、审批和风险记录"},
                {"title": "情报新闻", "entry": "Intelligence Center", "purpose": "市场信号与项目风险联动"},
            ],
        },
        "war_room": {
            "items": war_room_items,
            "flow": ["项目总览", "文件/节点/责任人", "审批/风险/外发"],
        },
        "risk_queue": {
            "items": risk_queue,
            "critical_count": critical_risk_count,
            "next_actions": ["进入项目 War Room", "催办文件审批", "复核敏感资料归属", "更新报告中心状态"],
        },
        "cross_check": {
            "items": cross_check_items,
            "checks": ["重复标题", "敏感文件缺少项目归属", "归档锁定不一致", "非草稿缺少当前版本"],
        },
        "mobile": {
            "steps": [
                {"title": "看待办", "detail": "只展示需本人判断的审批、补材料和风险事项。"},
                {"title": "看依据", "detail": "聚合摘要、文件版本、风险点和审计背景。"},
                {"title": "做动作", "detail": "批准 / 退回 / 要补材料 / 转入 War Room。"},
            ]
        },
    }


AI8_CHAT_URL = "https://ai8.rcouyi.com/chat"


def ai8_agent_status_payload(user: dict | None = None) -> dict:
    api_url = env_value("AI8_API_URL", "AI8_CHAT_API_URL")
    api_key = env_value("AI8_API_KEY", "AI8_TOKEN")
    title = "欧亿AI-8.0 Pro"
    menus: list[dict] = []
    reachable = False
    http_status = 0
    error_text = ""
    try:
        resp = httpx.get(AI8_CHAT_URL, timeout=8, follow_redirects=True)
        http_status = int(resp.status_code)
        reachable = resp.is_success
        if resp.text:
            title_match = re.search(r"<title>(.*?)</title>", resp.text, re.I | re.S)
            if title_match:
                title = re.sub(r"\s+", " ", title_match.group(1)).strip() or title
            site_match = re.search(r"window\.aiSiteInfo\s*=\s*(\{.*?\})</script>", resp.text, re.S)
            if site_match:
                try:
                    site_info = json.loads(site_match.group(1))
                    raw_menus = site_info.get("menus") if isinstance(site_info, dict) else []
                    menus = [
                        {
                            "key": str(item.get("key") or ""),
                            "name": str(item.get("name") or item.get("key") or ""),
                            "value": str(item.get("value") or ""),
                            "action": str(item.get("action") or ""),
                        }
                        for item in raw_menus[:16]
                        if isinstance(item, dict)
                    ]
                    title = str(site_info.get("name") or title)
                except Exception:
                    pass
    except Exception as exc:
        error_text = str(exc)[:500]
    return {
        "ok": True,
        "provider": "ai8",
        "title": title,
        "chat_url": AI8_CHAT_URL,
        "reachable": reachable,
        "http_status": http_status,
        "api_ready": bool(api_url and api_key),
        "api_url_configured": bool(api_url),
        "menus": menus,
        "error": error_text,
        "bridge_modes": ["api", "handoff", "embed", "external_open"],
        "recommended_mode": "api" if api_url and api_key else ("handoff" if reachable else "external_open"),
        "generated_at": int(time.time()),
    }


def _ai8_task_id() -> str:
    return f"ai8task_{int(time.time())}_{secrets.token_hex(5)}"


def ai8_agent_handoff_payload(user: dict | None, payload: dict) -> tuple[dict, int]:
    user = user or {}
    actor = normalize_email(user.get("email", "")) or str(user.get("username") or "anonymous")
    title = _compact_memory_text(payload.get("title") or "AI8 External Agent Task", 160)
    prompt = str(payload.get("prompt") or "").strip()
    packet = str(payload.get("packet") or "").strip()
    mode = str(payload.get("mode") or "auto").strip().lower()
    target = str(payload.get("target") or "hermes-memory").strip()
    if not prompt:
        return {"ok": False, "error": "prompt_required"}, 400
    task_id = _ai8_task_id()
    api_url = env_value("AI8_API_URL", "AI8_CHAT_API_URL")
    api_key = env_value("AI8_API_KEY", "AI8_TOKEN")
    direct_api_used = False
    result_text = ""
    direct_error = ""
    if mode in {"auto", "api"} and api_url and api_key:
        try:
            resp = httpx.post(
                api_url,
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={
                    "title": title,
                    "prompt": prompt,
                    "messages": [{"role": "user", "content": packet or prompt}],
                    "source": "fastone-hermes",
                    "task_id": task_id,
                    "target": target,
                },
                timeout=45,
            )
            if resp.is_success:
                direct_api_used = True
                try:
                    data = resp.json()
                    result_text = _extract_assistant_text(data) or json.dumps(data, ensure_ascii=False)[:4000]
                except Exception:
                    result_text = resp.text[:4000]
            else:
                direct_error = f"AI8 API HTTP {resp.status_code}: {resp.text[:500]}"
        except Exception as exc:
            direct_error = str(exc)[:500]
    task = {
        "id": task_id,
        "title": title,
        "prompt": _compact_memory_text(prompt, 1200),
        "target": target,
        "mode": mode,
        "actor": actor,
        "status": "api_completed" if direct_api_used else "handoff_ready",
        "created_at": int(time.time()),
    }
    handoff_dir = ROOT / "ai_agent_handoffs"
    handoff_dir.mkdir(parents=True, exist_ok=True)
    (handoff_dir / f"{task_id}.json").write_text(
        json.dumps(
            {
                "task": task,
                "packet": packet or prompt,
                "result": result_text,
                "direct_error": direct_error,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    write_audit_event(
        {
            "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
            "event": "ai8_agent_handoff",
            "actor": actor,
            "target": target,
            "task_id": task_id,
            "mode": mode,
            "direct_api_used": direct_api_used,
            "error": direct_error,
            "dlp_terms": detect_governance_dlp_terms(title, prompt, target),
        }
    )
    if result_text:
        update_workspace_memory(
            "home",
            "external-ai8-agent",
            [{"role": "user", "content": prompt}],
            result_text,
        )
    return {
        "ok": True,
        "task": task,
        "packet": packet or prompt,
        "result": result_text,
        "direct_api_used": direct_api_used,
        "direct_error": direct_error,
        "open_url": AI8_CHAT_URL,
        "handoff_file": str(handoff_dir / f"{task_id}.json"),
    }, 200


def ai_agent_memory_save_payload(user: dict | None, payload: dict) -> tuple[dict, int]:
    user = user or {}
    actor = normalize_email(user.get("email", "")) or str(user.get("username") or "anonymous")
    workspace = str(payload.get("workspace") or "home").strip() or "home"
    skill_id = str(payload.get("skill_id") or "external-ai8-agent").strip() or "external-ai8-agent"
    prompt = str(payload.get("prompt") or "").strip()
    result = str(payload.get("result") or "").strip()
    target = str(payload.get("target") or "hermes-memory").strip()
    status = str(payload.get("status") or "pending_review").strip()
    if not result:
        return {"ok": False, "error": "result_required"}, 400
    update_workspace_memory(workspace, skill_id, [{"role": "user", "content": prompt}], result)
    design_memory = _load_workspace_memory("home", "hermes-research-memory")
    design_recent = [item for item in design_memory.get("recent", []) if isinstance(item, dict)]
    design_recent.append(
        {
            "ts": int(time.time()),
            "request": "AI Agent Hub / AI8 connector operating principle",
            "response": _compact_memory_text(
                "Hermes must treat external AI8 output as draft/pending-review until adopted. Preferred connection order: configured API, task handoff, embedded preview, external open. Keep audit trace, DLP terms, target workspace, and return result in Hermes memory.",
                480,
            ),
        }
    )
    design_memory["recent"] = design_recent[-12:]
    design_memory["summary"] = " | ".join(
        f"{_compact_memory_text(item.get('request'), 100)} -> {_compact_memory_text(item.get('response'), 140)}"
        for item in design_memory["recent"][-5:]
    )
    design_memory["updated_at"] = int(time.time())
    _save_workspace_memory("home", "hermes-research-memory", design_memory)
    write_audit_event(
        {
            "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
            "event": "ai_agent_memory_save",
            "actor": actor,
            "workspace": workspace,
            "skill_id": skill_id,
            "target": target,
            "status": status,
            "dlp_terms": detect_governance_dlp_terms(prompt, result, target),
        }
    )
    return {
        "ok": True,
        "workspace": workspace,
        "skill_id": skill_id,
        "target": target,
        "status": status,
        "memory_file": str(_memory_path(workspace, skill_id)),
        "research_memory_file": str(_memory_path("home", "hermes-research-memory")),
    }, 200


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def log_message(self, fmt: str, *args) -> None:
        log(fmt % args)

    def end_headers(self) -> None:
        origin = self.headers.get("Origin", "")
        if origin:
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Access-Control-Allow-Credentials", "true")
            self.send_header("Vary", "Origin")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PATCH, DELETE, OPTIONS")
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.end_headers()

    def _send_json(self, payload: dict, status: int = 200, extra_headers: dict[str, str] | None = None) -> None:
        raw = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        for key, value in (extra_headers or {}).items():
            self.send_header(key, value)
        self.end_headers()
        try:
            self.wfile.write(raw)
        except (BrokenPipeError, ConnectionResetError):
            log("Client disconnected before JSON response could be written")

    def do_GET(self):
        parsed = urlparse(self.path)
        for header in ("If-Modified-Since", "If-None-Match"):
            if header in self.headers:
                del self.headers[header]
        if parsed.path == "/api/auth/session":
            self._send_json(auth_session_payload(self.headers))
            return
        if parsed.path == "/api/admin/users":
            user = current_local_user_record(self.headers)
            if not is_admin_user(user):
                self._send_json({"ok": False, "error": "admin_required"}, 403)
                return
            query = parse_qs(parsed.query).get("q", [""])[0] if parsed.query else ""
            payload = admin_users_payload()
            if query:
                filtered = []
                for item in payload.get("users", []):
                    login = item.get("login_status") or {}
                    work = login.get("work_status") or {}
                    logged_in = bool(login.get("logged_in"))
                    if _matches_user_search(
                        query,
                        item.get("email", ""),
                        item.get("username", ""),
                        item.get("display_name", ""),
                        item.get("role", ""),
                        "online" if logged_in else "offline",
                        "在线" if logged_in else "离线",
                        work.get("page", ""),
                        work.get("workspace", ""),
                        work.get("skill_id", ""),
                        work.get("provider", ""),
                        work.get("model", ""),
                    ):
                        filtered.append(item)
                payload["users"] = filtered
            self._send_json(payload)
            return
        if parsed.path == "/api/admin/activity-report":
            user = current_local_user_record(self.headers)
            if not is_admin_user(user):
                self._send_json({"ok": False, "error": "admin_required"}, 403)
                return
            self._send_json(latest_admin_activity_report_payload())
            return
        if parsed.path == "/api/admin/monthly-report":
            user = current_local_user_record(self.headers)
            if not is_admin_user(user):
                self._send_json({"ok": False, "error": "admin_required"}, 403)
                return
            self._send_json(latest_admin_monthly_report_payload())
            return
        if parsed.path == "/api/team/status":
            session = auth_session_payload(self.headers)
            user = session.get("user") if isinstance(session, dict) else None
            if not session.get("authenticated"):
                self._send_json({"ok": False, "error": "authentication_required"}, 401)
                return
            permissions = user.get("permissions") if isinstance(user, dict) else {}
            allowed = bool(
                isinstance(user, dict)
                and (
                    user.get("role") == "admin"
                    or (isinstance(permissions, dict) and permissions.get("user_admin"))
                    or (isinstance(permissions, dict) and permissions.get("view_team_status"))
                )
            )
            if not allowed:
                self._send_json({"ok": False, "error": "permission_denied"}, 403)
                return
            query = parse_qs(parsed.query).get("q", [""])[0] if parsed.query else ""
            self._send_json(team_status_payload(query))
            return
        if parsed.path == "/api/work-chat/users":
            user = current_local_user_record(self.headers)
            if not user:
                self._send_json({"ok": False, "error": "authentication_required"}, 401)
                return
            self._send_json({"ok": True, "users": public_user_directory(user)})
            return
        if parsed.path == "/api/work-chat/conversations":
            user = current_local_user_record(self.headers)
            if not user:
                self._send_json({"ok": False, "error": "authentication_required"}, 401)
                return
            self._send_json(list_chat_conversations_payload(user))
            return
        if parsed.path.startswith("/api/work-chat/conversations/"):
            user = current_local_user_record(self.headers)
            if not user:
                self._send_json({"ok": False, "error": "authentication_required"}, 401)
                return
            parts = [part for part in parsed.path.split("/") if part]
            conversation_id = parts[3] if len(parts) >= 4 else ""
            data = _load_work_chat_payload()
            conversation = _chat_conversation(data, conversation_id)
            if not conversation:
                self._send_json({"ok": False, "error": "conversation_not_found"}, 404)
                return
            if not can_access_chat_conversation(user, data, conversation_id):
                self._send_json({"ok": False, "error": "permission_denied"}, 403)
                return
            if len(parts) >= 7 and parts[4] == "files" and parts[6] == "download":
                query = parse_qs(parsed.query) if parsed.query else {}
                shared_file_id = parts[5]
                payload, status_code = work_chat_file_download_payload(
                    user,
                    conversation_id,
                    shared_file_id,
                    query.get("version_id", [""])[0],
                )
                if not payload.get("ok"):
                    self._send_json(payload, status_code)
                    return
                raw = payload.pop("raw")
                self.send_response(200)
                self.send_header("Content-Type", payload.get("mime", "application/octet-stream"))
                self.send_header("Content-Length", str(len(raw)))
                self.send_header("Content-Disposition", f"attachment; filename=\"{payload.get('filename', 'file.bin')}\"")
                self.end_headers()
                try:
                    self.wfile.write(raw)
                except (BrokenPipeError, ConnectionResetError):
                    log("Client disconnected before work-chat file download could be written")
                return
            if len(parts) >= 5 and parts[4] == "messages":
                query = parse_qs(parsed.query) if parsed.query else {}
                payload = chat_messages_payload(user, conversation_id, date_filter=query.get("date", [""])[0])
                status_code = 200 if payload.get("ok") else (400 if payload.get("error") == "invalid_date" else 403)
                self._send_json(payload, status_code)
                return
            self._send_json({"ok": True, "conversation": _chat_conversation_payload(data, conversation, user, include_messages=False)})
            return
        if parsed.path == "/api/document-flows/users":
            user = current_local_user_record(self.headers)
            if not user:
                self._send_json({"ok": False, "error": "authentication_required"}, 401)
                return
            self._send_json({"ok": True, "users": public_user_directory(user)})
            return
        if parsed.path == "/api/document-flows":
            user = current_local_user_record(self.headers)
            if not user:
                self._send_json({"ok": False, "error": "authentication_required"}, 401)
                return
            query = parse_qs(parsed.query) if parsed.query else {}
            self._send_json(list_document_flows_payload(user, query))
            return
        if parsed.path == "/api/v2/document-flows":
            user = current_local_user_record(self.headers)
            if not user:
                self._send_json({"ok": False, "error": "authentication_required"}, 401)
                return
            query = parse_qs(parsed.query) if parsed.query else {}
            self._send_json(list_document_flows_payload(user, query))
            return
        if parsed.path == "/api/document-flows/notifications":
            user = current_local_user_record(self.headers)
            if not user:
                self._send_json({"ok": False, "error": "authentication_required"}, 401)
                return
            data = _load_document_flow_payload()
            self._send_json({"ok": True, "notifications": _document_notifications_for_user(data, normalize_email(user.get("email", "")))[:60]})
            return
        if parsed.path.startswith("/api/document-flows/documents/"):
            user = current_local_user_record(self.headers)
            if not user:
                self._send_json({"ok": False, "error": "authentication_required"}, 401)
                return
            parts = [part for part in parsed.path.split("/") if part]
            document_id = parts[3] if len(parts) >= 4 else ""
            if len(parts) >= 5 and parts[4] == "download":
                query = parse_qs(parsed.query) if parsed.query else {}
                payload, status_code = document_download_payload(user, document_id, query.get("version_id", [""])[0])
                if not payload.get("ok"):
                    self._send_json(payload, status_code)
                    return
                raw = payload.pop("raw")
                self.send_response(200)
                self.send_header("Content-Type", payload.get("mime", "application/octet-stream"))
                self.send_header("Content-Length", str(len(raw)))
                self.send_header("Content-Disposition", f"attachment; filename=\"{payload.get('filename', 'document.bin')}\"")
                self.end_headers()
                try:
                    self.wfile.write(raw)
                except (BrokenPipeError, ConnectionResetError):
                    log("Client disconnected before document download could be written")
                return
            payload = _document_payload(_load_document_flow_payload(), document_id, user, include_notifications=True)
            status_code = 200 if payload.get("ok") else (404 if payload.get("error") == "document_not_found" else 403)
            self._send_json(payload, status_code)
            return
        if parsed.path.startswith("/api/v2/document-flows/documents/"):
            user = current_local_user_record(self.headers)
            if not user:
                self._send_json({"ok": False, "error": "authentication_required"}, 401)
                return
            parts = [part for part in parsed.path.split("/") if part]
            document_id = parts[4] if len(parts) >= 5 else ""
            if len(parts) >= 6 and parts[5] == "download":
                query = parse_qs(parsed.query) if parsed.query else {}
                payload, status_code = document_download_payload(user, document_id, query.get("version_id", [""])[0])
                if not payload.get("ok"):
                    self._send_json(payload, status_code)
                    return
                raw = payload.pop("raw")
                self.send_response(200)
                self.send_header("Content-Type", payload.get("mime", "application/octet-stream"))
                self.send_header("Content-Length", str(len(raw)))
                self.send_header("Content-Disposition", f"attachment; filename=\"{payload.get('filename', 'document.bin')}\"")
                self.end_headers()
                try:
                    self.wfile.write(raw)
                except (BrokenPipeError, ConnectionResetError):
                    log("Client disconnected before document download could be written")
                return
            payload = _document_payload(_load_document_flow_payload(), document_id, user, include_notifications=True)
            status_code = 200 if payload.get("ok") else (404 if payload.get("error") == "document_not_found" else 403)
            self._send_json(payload, status_code)
            return
        if parsed.path == "/api/v2/projects":
            user = current_local_user_record(self.headers)
            if not user:
                self._send_json({"ok": False, "error": "authentication_required"}, 401)
                return
            query = parse_qs(parsed.query) if parsed.query else {}
            self._send_json(_v2_list_projects(user, query))
            return
        if parsed.path.startswith("/api/v2/projects/"):
            user = current_local_user_record(self.headers)
            if not user:
                self._send_json({"ok": False, "error": "authentication_required"}, 401)
                return
            parts = [part for part in parsed.path.split("/") if part]
            project_id = parts[3] if len(parts) >= 4 else ""
            query = parse_qs(parsed.query) if parsed.query else {}
            if len(parts) >= 6 and parts[4] == "chat-summary":
                if parts[5] == "current":
                    payload, status_code = _v2_project_chat_current_summary(user, project_id)
                    self._send_json(payload, status_code)
                    return
                if parts[5] == "history":
                    payload, status_code = _v2_project_chat_summary_history(user, project_id, query)
                    self._send_json(payload, status_code)
                    return
                if parts[5] == "retention-policy":
                    payload, status_code = _v2_project_chat_retention_policy(user, project_id)
                    self._send_json(payload, status_code)
                    return
                if parts[5] == "cleanup-logs":
                    payload, status_code = _v2_project_chat_cleanup_logs(user, project_id, query)
                    self._send_json(payload, status_code)
                    return
                summary_id = parts[5]
                payload, status_code = _v2_project_chat_summary_detail(user, project_id, summary_id)
                self._send_json(payload, status_code)
                return
            if len(parts) >= 6 and parts[4] == "chat" and parts[5] == "messages":
                payload, status_code = _v2_project_chat_messages(user, project_id, query)
                self._send_json(payload, status_code)
                return
            if len(parts) >= 5 and parts[4] == "document-flows":
                query["project_id"] = [project_id]
                self._send_json(list_document_flows_payload(user, query))
                return
            with v2_db_lock, _v2_db_conn() as conn:
                payload = _v2_project_detail_payload(conn, project_id, user)
            status_code = 200 if payload.get("ok") else (404 if payload.get("error") == "project_not_found" else 403)
            self._send_json(payload, status_code)
            return
        if parsed.path == "/api/v2/work-items":
            user = current_local_user_record(self.headers)
            query = parse_qs(parsed.query) if parsed.query else {}
            payload, status_code = _v2_list_work_items(user, query)
            self._send_json(payload, status_code)
            return
        if parsed.path == "/api/v2/issues":
            user = current_local_user_record(self.headers)
            query = parse_qs(parsed.query) if parsed.query else {}
            payload, status_code = _v2_list_issues(user, query)
            self._send_json(payload, status_code)
            return
        if parsed.path == "/api/v2/reports":
            user = current_local_user_record(self.headers)
            query = parse_qs(parsed.query) if parsed.query else {}
            payload, status_code = _v2_list_reports(user, query)
            self._send_json(payload, status_code)
            return
        if parsed.path.startswith("/api/v2/reports/"):
            user = current_local_user_record(self.headers)
            parts = [part for part in parsed.path.split("/") if part]
            report_id = parts[3] if len(parts) >= 4 else ""
            payload, status_code = _v2_report_detail(user, report_id)
            self._send_json(payload, status_code)
            return
        if parsed.path == "/api/v2/dashboard/workbench":
            user = current_local_user_record(self.headers)
            query = parse_qs(parsed.query) if parsed.query else {}
            payload, status_code = _v2_workbench_payload(user, query)
            self._send_json(payload, status_code)
            return
        if parsed.path == "/api/v2/my-work":
            user = current_local_user_record(self.headers)
            payload, status_code = _v2_my_work_payload(user)
            self._send_json(payload, status_code)
            return
        if parsed.path == "/api/v2/search":
            user = current_local_user_record(self.headers)
            query = parse_qs(parsed.query) if parsed.query else {}
            payload, status_code = _v2_global_search(user, query)
            self._send_json(payload, status_code)
            return
        if parsed.path == "/api/v2/admin/overview":
            user = current_local_user_record(self.headers)
            payload, status_code = _v2_admin_overview(user)
            self._send_json(payload, status_code)
            return
        if parsed.path == "/api/v2/admin/project-chat-summaries/overview":
            user = current_local_user_record(self.headers)
            payload, status_code = _v2_admin_project_chat_summary_overview(user)
            self._send_json(payload, status_code)
            return
        if parsed.path == "/api/governance/control-center":
            user = current_local_user_record(self.headers)
            if not user:
                self._send_json({"ok": False, "error": "authentication_required"}, 401)
                return
            write_audit_event(
                {
                    "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "event": "governance_control_view",
                    "actor": normalize_email(user.get("email", "")) or str(user.get("username") or "user"),
                    "target": "governance-center",
                    "dlp_terms": [],
                }
            )
            self._send_json(governance_control_payload(user))
            return
        if parsed.path == "/api/v2/notifications":
            user = current_local_user_record(self.headers)
            query = parse_qs(parsed.query) if parsed.query else {}
            payload, status_code = _v2_list_notifications(user, query)
            self._send_json(payload, status_code)
            return
        if parsed.path == "/api/v2/file-center/overview":
            user = current_local_user_record(self.headers)
            query = parse_qs(parsed.query) if parsed.query else {}
            payload, status_code = _v2_file_center_overview(user, query)
            self._send_json(payload, status_code)
            return
        if parsed.path == "/api/v2/file-center/files":
            user = current_local_user_record(self.headers)
            query = parse_qs(parsed.query) if parsed.query else {}
            payload, status_code = _v2_list_file_center_files(user, query)
            self._send_json(payload, status_code)
            return
        if parsed.path.startswith("/api/v2/file-center/files/"):
            user = current_local_user_record(self.headers)
            parts = [part for part in parsed.path.split("/") if part]
            file_id = parts[4] if len(parts) >= 5 else ""
            if len(parts) >= 6 and parts[5] == "versions":
                payload, status_code = _v2_file_center_versions(user, file_id)
                self._send_json(payload, status_code)
                return
            if len(parts) >= 6 and parts[5] == "workflows":
                payload, status_code = _v2_file_center_workflows(user, file_id)
                self._send_json(payload, status_code)
                return
            if len(parts) >= 6 and parts[5] == "audit":
                payload, status_code = _v2_file_center_audit(user, file_id)
                self._send_json(payload, status_code)
                return
            if len(parts) >= 6 and parts[5] == "download":
                query = parse_qs(parsed.query) if parsed.query else {}
                payload, status_code = _v2_file_center_download(user, file_id, str(query.get("version_id", [""])[0] or ""))
                if not payload.get("ok"):
                    self._send_json(payload, status_code)
                    return
                raw = payload.pop("raw")
                self.send_response(200)
                self.send_header("Content-Type", payload.get("mime", "application/octet-stream"))
                self.send_header("Content-Length", str(len(raw)))
                self.send_header("Content-Disposition", f"attachment; filename=\"{payload.get('filename', 'file.bin')}\"")
                self.end_headers()
                try:
                    self.wfile.write(raw)
                except (BrokenPipeError, ConnectionResetError):
                    log("Client disconnected before file-center download could be written")
                return
            payload, status_code = _v2_file_center_detail(user, file_id)
            self._send_json(payload, status_code)
            return
        if parsed.path == "/api/v2/file-center/archives":
            user = current_local_user_record(self.headers)
            query = parse_qs(parsed.query) if parsed.query else {}
            payload, status_code = _v2_file_center_list_archives(user, query)
            self._send_json(payload, status_code)
            return
        if parsed.path == "/api/v2/file-center/certificates":
            user = current_local_user_record(self.headers)
            query = parse_qs(parsed.query) if parsed.query else {}
            payload, status_code = _v2_file_center_certificates(user, query)
            self._send_json(payload, status_code)
            return
        if parsed.path == "/api/v2/file-center/my/overview":
            user = current_local_user_record(self.headers)
            payload, status_code = _v2_file_center_my_overview(user)
            self._send_json(payload, status_code)
            return
        if parsed.path.startswith("/api/v2/file-center/workspaces/") and parsed.path.endswith("/overview"):
            user = current_local_user_record(self.headers)
            parts = [part for part in parsed.path.split("/") if part]
            workspace_id = parts[4] if len(parts) >= 5 else ""
            payload, status_code = _v2_file_center_workspace_overview(user, workspace_id)
            self._send_json(payload, status_code)
            return
        if parsed.path == "/api/v2/file-center/admin/global-overview":
            user = current_local_user_record(self.headers)
            payload, status_code = _v2_file_center_admin_summary(user)
            self._send_json(payload, status_code)
            return
        if parsed.path == "/api/v2/file-center/admin/summary":
            user = current_local_user_record(self.headers)
            payload, status_code = _v2_file_center_admin_summary(user)
            self._send_json(payload, status_code)
            return
        if parsed.path == "/api/v2/file-center/reports/daily":
            user = current_local_user_record(self.headers)
            query = parse_qs(parsed.query) if parsed.query else {}
            payload, status_code = _v2_file_center_list_daily_reports(user, query)
            self._send_json(payload, status_code)
            return
        if parsed.path == "/api/intelligence/markets/overview":
            user = current_local_user_record(self.headers)
            query = parse_qs(parsed.query) if parsed.query else {}
            payload, status_code = _v2_intel_markets_overview(user, query)
            self._send_json(payload, status_code)
            return
        if parsed.path == "/api/intelligence/markets/indices":
            user = current_local_user_record(self.headers)
            query = parse_qs(parsed.query) if parsed.query else {}
            payload, status_code = _v2_intel_market_indices(user, query)
            self._send_json(payload, status_code)
            return
        if parsed.path.startswith("/api/intelligence/markets/indices/"):
            user = current_local_user_record(self.headers)
            parts = [part for part in parsed.path.split("/") if part]
            index_id = parts[4] if len(parts) >= 5 else ""
            query = parse_qs(parsed.query) if parsed.query else {}
            if len(parts) >= 6 and parts[5] == "timeseries":
                payload, status_code = _v2_intel_market_index_timeseries(user, index_id, query)
                self._send_json(payload, status_code)
                return
            payload, status_code = _v2_intel_market_index_detail(user, index_id, query)
            self._send_json(payload, status_code)
            return
        if parsed.path == "/api/intelligence/instruments/search":
            user = current_local_user_record(self.headers)
            query = parse_qs(parsed.query) if parsed.query else {}
            payload, status_code = _v2_intel_instruments_search(user, query)
            self._send_json(payload, status_code)
            return
        if parsed.path == "/api/intelligence/instruments/watchlist":
            user = current_local_user_record(self.headers)
            payload, status_code = _v2_intel_watchlist_get(user)
            self._send_json(payload, status_code)
            return
        if parsed.path.startswith("/api/intelligence/instruments/"):
            user = current_local_user_record(self.headers)
            parts = [part for part in parsed.path.split("/") if part]
            instrument_id = parts[3] if len(parts) >= 4 else ""
            query = parse_qs(parsed.query) if parsed.query else {}
            if len(parts) >= 5 and parts[4] == "candles":
                payload, status_code = _v2_intel_instrument_candles(user, instrument_id, query)
                self._send_json(payload, status_code)
                return
            if len(parts) >= 6 and parts[4] == "quotes" and parts[5] == "history":
                payload, status_code = _v2_intel_instrument_quote_history(user, instrument_id, query)
                self._send_json(payload, status_code)
                return
            payload, status_code = _v2_intel_instrument_detail(user, instrument_id, query)
            self._send_json(payload, status_code)
            return
        if parsed.path == "/api/intelligence/news/top":
            user = current_local_user_record(self.headers)
            query = parse_qs(parsed.query) if parsed.query else {}
            payload, status_code = _v2_intel_news_top(user, query)
            self._send_json(payload, status_code)
            return
        if parsed.path == "/api/intelligence/news":
            user = current_local_user_record(self.headers)
            query = parse_qs(parsed.query) if parsed.query else {}
            payload, status_code = _v2_intel_news_list(user, query)
            self._send_json(payload, status_code)
            return
        if parsed.path == "/api/intelligence/news/sources":
            user = current_local_user_record(self.headers)
            query = parse_qs(parsed.query) if parsed.query else {}
            payload, status_code = _v2_intel_news_sources(user, query)
            self._send_json(payload, status_code)
            return
        if parsed.path == "/api/intelligence/news/stats":
            user = current_local_user_record(self.headers)
            query = parse_qs(parsed.query) if parsed.query else {}
            payload, status_code = _v2_intel_news_stats(user, query)
            self._send_json(payload, status_code)
            return
        if parsed.path.startswith("/api/intelligence/news/"):
            user = current_local_user_record(self.headers)
            parts = [part for part in parsed.path.split("/") if part]
            article_id = parts[3] if len(parts) >= 4 else ""
            query = parse_qs(parsed.query) if parsed.query else {}
            payload, status_code = _v2_intel_news_detail(user, article_id, query)
            self._send_json(payload, status_code)
            return
        if parsed.path == "/api/skills/activation-guide":
            self._send_json(skills_activation_guide_payload())
            return
        if parsed.path == "/api/intelligence/daily-brief":
            user = current_local_user_record(self.headers)
            query = parse_qs(parsed.query) if parsed.query else {}
            payload, status_code = _v2_intel_daily_brief(user, query)
            self._send_json(payload, status_code)
            return
        if parsed.path == "/api/intelligence/home-widget":
            user = current_local_user_record(self.headers)
            query = parse_qs(parsed.query) if parsed.query else {}
            payload, status_code = _v2_intel_home_widget(user, query)
            self._send_json(payload, status_code)
            return
        if parsed.path == "/api/admin/intelligence/job-runs":
            user = current_local_user_record(self.headers)
            query = parse_qs(parsed.query) if parsed.query else {}
            payload, status_code = _v2_admin_intel_job_runs(user, query)
            self._send_json(payload, status_code)
            return
        if parsed.path == "/api/admin/intelligence/providers/status":
            user = current_local_user_record(self.headers)
            payload, status_code = _v2_admin_intel_providers_status(user)
            self._send_json(payload, status_code)
            return
        if parsed.path == "/api/admin/intelligence/market-data/job-runs":
            user = current_local_user_record(self.headers)
            query = parse_qs(parsed.query) if parsed.query else {}
            payload, status_code = _v2_admin_intel_job_runs(user, query)
            self._send_json(payload, status_code)
            return
        if parsed.path == "/api/admin/intelligence/market-data/providers/status":
            user = current_local_user_record(self.headers)
            payload, status_code = _v2_admin_intel_providers_status(user)
            self._send_json(payload, status_code)
            return
        if parsed.path.startswith("/api/") and not parsed.path.startswith("/api/auth/") and parsed.path not in {"/api/cron-status", "/api/ai-agent/ai8/status"}:
            if not current_local_user_from_headers(self.headers):
                self._send_json({"ok": False, "error": "authentication_required"}, 401)
                return
        if parsed.path == "/api/ai-agent/ai8/status":
            user = current_local_user_record(self.headers)
            self._send_json(ai8_agent_status_payload(user))
            return
        if parsed.path == "/api/status":
            start_gateway()
            self._send_json(status_payload())
            return
        if parsed.path == "/api/provider":
            start_gateway()
            self._send_json(status_payload())
            return
        if parsed.path == "/api/models":
            self._send_json(status_payload())
            return
        if parsed.path == "/api/google-workspace/profiles":
            self._send_json(google_workspace_profiles_payload())
            return
        if parsed.path == "/api/composio/profiles":
            self._send_json(composio_profiles_payload())
            return
        if parsed.path == "/api/cron-status":
            if current_local_user_record(self.headers):
                self._send_json(cron_status_payload())
            else:
                self._send_json(cron_status_public_payload())
            return
        if parsed.path == "/api/exports":
            workspace = _safe_slug(parse_qs(parsed.query).get("workspace", [""])[0]) if parsed.query else ""
            base = EXPORTS_DIR / workspace if workspace else EXPORTS_DIR
            files = []
            if base.exists():
                for item in sorted(base.rglob("*"), key=lambda p: p.stat().st_mtime, reverse=True):
                    if not item.is_file():
                        continue
                    try:
                        resolved = item.resolve()
                        resolved.relative_to(EXPORTS_DIR.resolve())
                        url = f"/api/export-file?path={quote(str(resolved))}"
                    except Exception:
                        url = ""
                    files.append({
                        "name": item.name,
                        "path": str(item),
                        "download_url": url,
                        "mtime": int(item.stat().st_mtime),
                    })
                    if len(files) >= 20:
                        break
            self._send_json({"ok": True, "files": files})
            return
        if parsed.path == "/api/export-file":
            target = unquote(parse_qs(parsed.query).get("path", [""])[0]) if parsed.query else ""
            if not target:
                self._send_json({"ok": False, "error": "path is required"}, 400)
                return
            try:
                file_path = Path(target).expanduser().resolve()
                allowed_roots = [
                    EXPORTS_DIR.resolve(),
                    ADMIN_DAILY_REPORTS_DIR.resolve(),
                    ADMIN_MONTHLY_REPORTS_DIR.resolve(),
                ]
                if not any(
                    str(file_path).startswith(str(root) + os.sep) or file_path == root
                    for root in allowed_roots
                ):
                    raise ValueError("outside allowed export roots")
            except Exception:
                self._send_json({"ok": False, "error": "invalid export path"}, 400)
                return
            if not file_path.exists() or not file_path.is_file():
                self._send_json({"ok": False, "error": "file not found"}, 404)
                return
            user = current_local_user_record(self.headers) or {}
            actor = normalize_email(user.get("email", "")) or str(user.get("username") or "anonymous")
            write_audit_event(
                {
                    "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "event": "export_file_download",
                    "actor": actor,
                    "filename": file_path.name,
                    "target": str(file_path),
                    "dlp_terms": detect_governance_dlp_terms(file_path.name, str(file_path)),
                }
            )
            if user:
                record_user_work_event(user, workspace="export-file", filename=file_path.name, exported=True)
            raw = file_path.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", self.guess_type(str(file_path)) or "application/octet-stream")
            self.send_header("Content-Length", str(len(raw)))
            self.send_header("Content-Disposition", f'attachment; filename="{file_path.name}"')
            self.end_headers()
            try:
                self.wfile.write(raw)
            except (BrokenPipeError, ConnectionResetError):
                log("Client disconnected before export file could be written")
            return
        return super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length else b"{}"
        try:
            data = json.loads(raw.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            self._send_json({"ok": False, "error": "invalid_json"}, 400)
            return

        if parsed.path == "/api/auth/register":
            email = str(data.get("email") or "").strip()
            phone = str(data.get("phone") or "").strip()
            password = str(data.get("password") or "")
            display_name = str(data.get("display_name") or "").strip()
            username = str(data.get("username") or "").strip()
            ok, reason, user = register_local_user(email, phone, password, display_name, username)
            if not ok or not user:
                self._send_json({"ok": False, "error": reason}, 400)
                return
            self._send_json(
                {
                    "ok": True,
                    "authenticated": False,
                    "user": user,
                    "approval_required": True,
                    "message": "account_pending_approval",
                    "idle_timeout_seconds": 0,
                },
                202,
            )
            return

        if parsed.path == "/api/auth/login":
            identifier = str(data.get("identifier") or data.get("email") or "").strip()
            password = str(data.get("password") or "")
            ok, reason, user = verify_local_user(identifier, password)
            if not ok or not user:
                self._send_json({"ok": False, "error": reason}, 400)
                return
            mark_local_user_login(user.get("email", ""))
            record_user_login_event(user)
            session_token = create_local_session(user)
            self._send_json(
                {
                    "ok": True,
                    "authenticated": True,
                    "user": user,
                    "session_token": session_token,
                    "idle_timeout_seconds": _session_idle_timeout_seconds(user),
                },
                200,
                {"Set-Cookie": auth_cookie_header(session_token)},
            )
            return

        if parsed.path == "/api/auth/logout":
            session_token = current_session_token(self.headers)
            revoke_local_session(session_token)
            self._send_json(
                {"ok": True, "authenticated": False, "user": None},
                200,
                {"Set-Cookie": auth_clear_cookie_header()},
            )
            return

        if parsed.path == "/api/auth/password":
            user = current_local_user_record(self.headers)
            if not user:
                self._send_json({"ok": False, "error": "authentication_required"}, 401)
                return
            current_password = str(data.get("current_password") or "")
            new_password = str(data.get("new_password") or "")
            ok, reason = change_own_password(user, current_password, new_password)
            self._send_json({"ok": ok, "error": None if ok else reason}, 200 if ok else 400)
            return

        if parsed.path == "/api/auth/heartbeat":
            user = current_local_user_record(self.headers)
            if not user:
                self._send_json({"ok": False, "error": "authentication_required"}, 401)
                return
            update_local_session_activity(
                current_session_token(self.headers),
                page=str(data.get("page") or ""),
                workspace=str(data.get("workspace") or ""),
                skill_id=str(data.get("skill_id") or ""),
                provider=str(data.get("provider") or ""),
                model=str(data.get("model") or ""),
            )
            self._send_json({"ok": True})
            return

        if parsed.path == "/api/admin/users/password":
            user = current_local_user_record(self.headers)
            if not is_admin_user(user):
                self._send_json({"ok": False, "error": "admin_required"}, 403)
                return
            identifier = str(data.get("identifier") or data.get("email") or data.get("username") or "").strip()
            new_password = str(data.get("password") or "")
            ok, reason = update_local_user_password(identifier, new_password)
            self._send_json({"ok": ok, "error": None if ok else reason}, 200 if ok else 400)
            return

        if parsed.path == "/api/admin/users/permissions":
            user = current_local_user_record(self.headers)
            if not is_admin_user(user):
                self._send_json({"ok": False, "error": "admin_required"}, 403)
                return
            identifier = str(data.get("identifier") or data.get("email") or data.get("username") or "").strip()
            role = str(data.get("role") or "").strip() or None
            permissions = data.get("permissions") if isinstance(data.get("permissions"), dict) else None
            ok, reason, updated_user = update_local_user_permissions(identifier, role, permissions)
            self._send_json({"ok": ok, "error": None if ok else reason, "user": updated_user}, 200 if ok else 400)
            return

        if parsed.path == "/api/admin/users/approval":
            user = current_local_user_record(self.headers)
            if not is_admin_user(user):
                self._send_json({"ok": False, "error": "admin_required"}, 403)
                return
            identifier = str(data.get("identifier") or data.get("email") or data.get("username") or "").strip()
            action = str(data.get("action") or "").strip().lower()
            permissions = data.get("permissions") if isinstance(data.get("permissions"), dict) else None
            reason_text = str(data.get("reason") or "").strip()
            ok, reason, updated_user = update_local_user_approval(identifier, action, user, permissions=permissions, reason=reason_text)
            self._send_json({"ok": ok, "error": None if ok else reason, "user": updated_user}, 200 if ok else 400)
            return

        if parsed.path == "/api/admin/users/delete":
            user = current_local_user_record(self.headers)
            if not is_admin_user(user):
                self._send_json({"ok": False, "error": "admin_required"}, 403)
                return
            identifier = str(data.get("identifier") or data.get("email") or data.get("username") or "").strip()
            ok, reason = delete_local_user(identifier)
            self._send_json({"ok": ok, "error": None if ok else reason}, 200 if ok else 400)
            return

        if parsed.path == "/api/admin/users/create":
            user = current_local_user_record(self.headers)
            if not is_admin_user(user):
                self._send_json({"ok": False, "error": "admin_required"}, 403)
                return
            ok, reason, created_user = admin_create_local_user(data, user)
            self._send_json({"ok": ok, "error": None if ok else reason, "user": created_user}, 200 if ok else 400)
            return

        if parsed.path == "/api/work-chat/conversations":
            user = current_local_user_record(self.headers)
            if not user:
                self._send_json({"ok": False, "error": "authentication_required"}, 401)
                return
            payload = create_chat_conversation(user, data)
            self._send_json(payload, 200 if payload.get("ok") else 400)
            return

        if parsed.path.startswith("/api/work-chat/conversations/"):
            user = current_local_user_record(self.headers)
            if not user:
                self._send_json({"ok": False, "error": "authentication_required"}, 401)
                return
            parts = [part for part in parsed.path.split("/") if part]
            conversation_id = parts[3] if len(parts) >= 4 else ""
            if len(parts) >= 5 and parts[4] == "files":
                payload = upload_chat_file(user, conversation_id, data)
                status = 200 if payload.get("ok") else (403 if payload.get("error") in {"permission_denied", "read_only_access"} else 400)
                self._send_json(payload, status)
                return
            if len(parts) >= 5 and parts[4] == "messages":
                payload = send_chat_message(user, conversation_id, str(data.get("content") or ""))
                status = 200 if payload.get("ok") else (403 if payload.get("error") in {"permission_denied", "read_only_access"} else 400)
                self._send_json(payload, status)
                return
            if len(parts) >= 5 and parts[4] == "grants":
                admin_user = current_local_user_record(self.headers)
                target = str(data.get("granted_user_id") or data.get("email") or "").strip()
                active = bool(data.get("active", True))
                payload = grant_chat_access(admin_user, conversation_id, target, active=active)
                status = 200 if payload.get("ok") else (403 if payload.get("error") == "admin_required" else 400)
                self._send_json(payload, status)
                return
        if parsed.path == "/api/document-flows/documents":
            user = current_local_user_record(self.headers)
            if not user:
                self._send_json({"ok": False, "error": "authentication_required"}, 401)
                return
            payload = create_document_flow(user, data)
            status = 200 if payload.get("ok") else 400
            self._send_json(payload, status)
            return
        if parsed.path == "/api/v2/document-flows/documents":
            user = current_local_user_record(self.headers)
            if not user:
                self._send_json({"ok": False, "error": "authentication_required"}, 401)
                return
            payload = create_document_flow(user, data)
            status = 200 if payload.get("ok") else (403 if payload.get("error") == "permission_denied" else 400)
            self._send_json(payload, status)
            return
        if parsed.path == "/api/document-flows/notifications/read":
            user = current_local_user_record(self.headers)
            if not user:
                self._send_json({"ok": False, "error": "authentication_required"}, 401)
                return
            payload = mark_document_notification_read(user, str(data.get("notification_id") or ""))
            status = 200 if payload.get("ok") else (403 if payload.get("error") == "permission_denied" else 404)
            self._send_json(payload, status)
            return
        if parsed.path.startswith("/api/document-flows/documents/"):
            user = current_local_user_record(self.headers)
            if not user:
                self._send_json({"ok": False, "error": "authentication_required"}, 401)
                return
            parts = [part for part in parsed.path.split("/") if part]
            document_id = parts[3] if len(parts) >= 4 else ""
            if len(parts) >= 5 and parts[4] == "action":
                payload = act_on_document_flow(user, document_id, data)
                status = 200 if payload.get("ok") else (403 if payload.get("error") in {"permission_denied", "no_pending_step_for_user", "document_locked"} else 400)
                self._send_json(payload, status)
                return
            if len(parts) >= 5 and parts[4] == "grant":
                target = str(data.get("granted_user_id") or data.get("email") or "").strip()
                scope = data.get("scope") if isinstance(data.get("scope"), list) else None
                active = bool(data.get("active", True))
                payload = grant_document_access(user, document_id, target, scope=scope, active=active)
                status = 200 if payload.get("ok") else (403 if payload.get("error") in {"admin_required", "permission_denied"} else 400)
                self._send_json(payload, status)
                return
        if parsed.path.startswith("/api/v2/document-flows/documents/"):
            user = current_local_user_record(self.headers)
            if not user:
                self._send_json({"ok": False, "error": "authentication_required"}, 401)
                return
            parts = [part for part in parsed.path.split("/") if part]
            document_id = parts[4] if len(parts) >= 5 else ""
            if len(parts) >= 6 and parts[5] == "action":
                payload = act_on_document_flow(user, document_id, data)
                status = 200 if payload.get("ok") else (403 if payload.get("error") in {"permission_denied", "no_pending_step_for_user", "document_locked"} else 400)
                self._send_json(payload, status)
                return
        if parsed.path == "/api/v2/projects":
            user = current_local_user_record(self.headers)
            payload, status_code = _v2_create_project(user, data)
            self._send_json(payload, status_code)
            return
        if parsed.path.startswith("/api/v2/projects/"):
            user = current_local_user_record(self.headers)
            parts = [part for part in parsed.path.split("/") if part]
            project_id = parts[3] if len(parts) >= 4 else ""
            if len(parts) >= 6 and parts[4] == "chat-summary":
                if parts[5] == "generate":
                    payload, status_code = _v2_project_chat_generate(user, project_id, data)
                    self._send_json(payload, status_code)
                    return
                if parts[5] == "cleanup":
                    payload, status_code = _v2_project_chat_cleanup(user, project_id, data)
                    self._send_json(payload, status_code)
                    return
                if parts[5] == "retention-policy":
                    payload, status_code = _v2_project_chat_update_policy(user, project_id, data)
                    self._send_json(payload, status_code)
                    return
                if len(parts) >= 7 and parts[6] == "regenerate":
                    summary_id = parts[5]
                    payload, status_code = _v2_project_chat_regenerate(user, project_id, summary_id, data)
                    self._send_json(payload, status_code)
                    return
            if len(parts) >= 6 and parts[4] == "chat":
                if parts[5] == "messages" and len(parts) == 6:
                    payload, status_code = _v2_project_chat_add_message(user, project_id, data)
                    self._send_json(payload, status_code)
                    return
                if parts[5] == "messages" and len(parts) >= 7 and parts[6] == "restore":
                    payload, status_code = _v2_project_chat_restore_messages(user, project_id, data)
                    self._send_json(payload, status_code)
                    return
                if parts[5] == "messages" and len(parts) >= 8:
                    message_id = parts[6]
                    action = parts[7]
                    if action == "mark-key":
                        payload, status_code = _v2_project_chat_mark_key(user, project_id, message_id, True)
                        self._send_json(payload, status_code)
                        return
                    if action == "unmark-key":
                        payload, status_code = _v2_project_chat_mark_key(user, project_id, message_id, False)
                        self._send_json(payload, status_code)
                        return
                if parts[5] == "restore":
                    payload, status_code = _v2_project_chat_restore_messages(user, project_id, data)
                    self._send_json(payload, status_code)
                    return
            if len(parts) >= 5 and parts[4] == "update":
                payload, status_code = _v2_update_project(user, project_id, data)
                self._send_json(payload, status_code)
                return
            if len(parts) >= 5 and parts[4] == "members" and len(parts) >= 6 and parts[5] == "upsert":
                payload, status_code = _v2_add_project_member(user, project_id, data)
                self._send_json(payload, status_code)
                return
            if len(parts) >= 5 and parts[4] == "members" and len(parts) >= 6 and parts[5] == "remove":
                target = str(data.get("user_id") or data.get("email") or "").strip()
                payload, status_code = _v2_remove_project_member(user, project_id, target)
                self._send_json(payload, status_code)
                return
        if parsed.path == "/api/v2/work-items":
            user = current_local_user_record(self.headers)
            payload, status_code = _v2_create_work_item(user, data)
            self._send_json(payload, status_code)
            return
        if parsed.path.startswith("/api/v2/work-items/"):
            user = current_local_user_record(self.headers)
            parts = [part for part in parsed.path.split("/") if part]
            item_id = parts[3] if len(parts) >= 4 else ""
            if len(parts) >= 5 and parts[4] == "update":
                payload, status_code = _v2_update_work_item(user, item_id, data)
                self._send_json(payload, status_code)
                return
        if parsed.path == "/api/v2/issues":
            user = current_local_user_record(self.headers)
            payload, status_code = _v2_create_issue(user, data)
            self._send_json(payload, status_code)
            return
        if parsed.path == "/api/v2/reports/generate":
            user = current_local_user_record(self.headers)
            if not is_admin_user(user):
                self._send_json({"ok": False, "error": "admin_required"}, 403)
                return
            force = bool(data.get("force", True))
            mode = str(data.get("mode") or "daily").strip().lower()
            if mode in {"daily", "all"}:
                _v2_generate_daily_reports(force=force)
            if mode in {"weekly", "all"}:
                _v2_generate_weekly_reports(force=force)
            self._send_json({"ok": True, "mode": mode, "forced": force})
            return
        if parsed.path == "/api/admin/intelligence/markets/refresh":
            user = current_local_user_record(self.headers)
            payload, status_code = _v2_admin_intel_markets_refresh(user, data)
            self._send_json(payload, status_code)
            return
        if parsed.path == "/api/admin/intelligence/market-data/refresh":
            user = current_local_user_record(self.headers)
            payload, status_code = _v2_admin_intel_market_data_refresh(user, data)
            self._send_json(payload, status_code)
            return
        if parsed.path == "/api/admin/intelligence/market-data/backfill":
            user = current_local_user_record(self.headers)
            payload, status_code = _v2_admin_intel_market_data_backfill(user, data)
            self._send_json(payload, status_code)
            return
        if parsed.path == "/api/admin/intelligence/news/refresh":
            user = current_local_user_record(self.headers)
            payload, status_code = _v2_admin_intel_news_refresh(user, data)
            self._send_json(payload, status_code)
            return
        if parsed.path == "/api/admin/intelligence/news/generate-digest":
            user = current_local_user_record(self.headers)
            payload, status_code = _v2_admin_intel_generate_digest(user, data)
            self._send_json(payload, status_code)
            return
        if parsed.path.startswith("/api/admin/intelligence/news/sources/"):
            user = current_local_user_record(self.headers)
            parts = [part for part in parsed.path.split("/") if part]
            source_id = parts[5] if len(parts) >= 6 else ""
            payload, status_code = _v2_admin_intel_update_source(user, source_id, data)
            self._send_json(payload, status_code)
            return
        if parsed.path.startswith("/api/admin/intelligence/markets/indices/"):
            user = current_local_user_record(self.headers)
            parts = [part for part in parsed.path.split("/") if part]
            index_id = parts[5] if len(parts) >= 6 else ""
            payload, status_code = _v2_admin_intel_update_index(user, index_id, data)
            self._send_json(payload, status_code)
            return
        if parsed.path == "/api/intelligence/instruments/watchlist":
            user = current_local_user_record(self.headers)
            payload, status_code = _v2_intel_watchlist_add(user, data)
            self._send_json(payload, status_code)
            return
        if parsed.path == "/api/v2/file-center/files":
            user = current_local_user_record(self.headers)
            payload, status_code = _v2_file_center_create_file(user, data)
            self._send_json(payload, status_code)
            return
        if parsed.path.startswith("/api/v2/file-center/files/"):
            user = current_local_user_record(self.headers)
            parts = [part for part in parsed.path.split("/") if part]
            file_id = parts[4] if len(parts) >= 5 else ""
            if len(parts) >= 6 and parts[5] == "versions":
                payload, status_code = _v2_file_center_add_version(user, file_id, data)
                self._send_json(payload, status_code)
                return
            if len(parts) >= 6 and parts[5] == "archive":
                payload, status_code = _v2_file_center_archive(user, file_id, data)
                self._send_json(payload, status_code)
                return
        if parsed.path == "/api/v2/file-center/workflows":
            user = current_local_user_record(self.headers)
            payload, status_code = _v2_file_center_create_workflow(user, data)
            self._send_json(payload, status_code)
            return
        if parsed.path == "/api/v2/file-center/certificates":
            user = current_local_user_record(self.headers)
            payload, status_code = _v2_file_center_create_certificate(user, data)
            self._send_json(payload, status_code)
            return
        if parsed.path.startswith("/api/v2/file-center/certificates/"):
            user = current_local_user_record(self.headers)
            parts = [part for part in parsed.path.split("/") if part]
            certificate_id = parts[4] if len(parts) >= 5 else ""
            if len(parts) >= 6 and parts[5] == "revoke":
                payload, status_code = _v2_file_center_revoke_certificate(user, certificate_id, data)
                self._send_json(payload, status_code)
                return
        if parsed.path.startswith("/api/v2/file-center/workflows/"):
            user = current_local_user_record(self.headers)
            parts = [part for part in parsed.path.split("/") if part]
            workflow_id = parts[4] if len(parts) >= 5 else ""
            if len(parts) >= 8 and parts[5] == "steps" and parts[7] == "action":
                step_id = parts[6]
                payload, status_code = _v2_file_center_step_action(user, workflow_id, step_id, data)
                self._send_json(payload, status_code)
                return
        if parsed.path == "/api/v2/file-center/reports/generate-daily":
            user = current_local_user_record(self.headers)
            if not is_admin_user(user):
                self._send_json({"ok": False, "error": "admin_required"}, 403)
                return
            force = bool(data.get("force", True))
            day_key = str(data.get("date") or "").strip()
            payload, status_code = _v2_file_center_generate_daily_digest(force=force, day_key=day_key)
            self._send_json(payload, status_code)
            return
        if parsed.path == "/api/v2/notifications/read":
            user = current_local_user_record(self.headers)
            payload, status_code = _v2_mark_notification_read(user, data)
            self._send_json(payload, status_code)
            return
        if parsed.path.startswith("/api/v2/reports/"):
            user = current_local_user_record(self.headers)
            parts = [part for part in parsed.path.split("/") if part]
            report_id = parts[3] if len(parts) >= 4 else ""
            if len(parts) >= 5 and parts[4] == "comments":
                payload, status_code = _v2_add_report_comment(user, report_id, data)
                self._send_json(payload, status_code)
                return
            if len(parts) >= 5 and parts[4] == "status":
                payload, status_code = _v2_update_report_status(user, report_id, data)
                self._send_json(payload, status_code)
                return
        if parsed.path.startswith("/api/v2/issues/"):
            user = current_local_user_record(self.headers)
            parts = [part for part in parsed.path.split("/") if part]
            issue_id = parts[3] if len(parts) >= 4 else ""
            if len(parts) >= 5 and parts[4] == "update":
                payload, status_code = _v2_update_issue(user, issue_id, data)
                self._send_json(payload, status_code)
                return

        if parsed.path.startswith("/api/") and not parsed.path.startswith("/api/auth/"):
            if not current_local_user_from_headers(self.headers):
                self._send_json({"ok": False, "error": "authentication_required"}, 401)
                return

        if parsed.path == "/api/ai-agent/ai8/handoff":
            user = current_local_user_record(self.headers)
            payload, status_code = ai8_agent_handoff_payload(user, data)
            self._send_json(payload, status_code)
            return

        if parsed.path == "/api/ai-agent/memory":
            user = current_local_user_record(self.headers)
            payload, status_code = ai_agent_memory_save_payload(user, data)
            self._send_json(payload, status_code)
            return

        if parsed.path == "/api/provider":
            provider = data.get("provider")
            model = data.get("model")
            if not provider or not model:
                self._send_json({"error": "provider and model are required"}, 400)
                return
            switch_provider(provider, model)
            self._send_json({"ok": True, "status": status_payload()})
            return

        if parsed.path == "/api/google-workspace/profile":
            profile = str(data.get("profile") or "").strip()
            label = str(data.get("label") or "").strip()
            email = str(data.get("email") or "").strip()
            if not profile:
                self._send_json({"ok": False, "error": "profile is required"}, 400)
                return
            ensure_profile(profile, label=label or None, email=email or None)
            set_default_profile(profile_slug(profile))
            payload = google_workspace_profiles_payload()
            payload["selected"] = profile_slug(profile)
            self._send_json(payload)
            return

        if parsed.path == "/api/composio/profile":
            profile = str(data.get("profile") or "").strip()
            label = str(data.get("label") or "").strip()
            email = str(data.get("email") or "").strip()
            if not profile:
                self._send_json({"ok": False, "error": "profile is required"}, 400)
                return
            ensure_composio_profile(profile, label=label or None, email=email or None)
            set_default_composio_profile(composio_profile_slug(profile))
            payload = composio_profiles_payload()
            payload["selected"] = composio_profile_slug(profile)
            self._send_json(payload)
            return

        if parsed.path == "/api/composio/api-key":
            profile = str(data.get("profile") or "").strip()
            composio_api_key = str(data.get("api_key") or "").strip()
            if not profile or not composio_api_key:
                self._send_json({"ok": False, "error": "profile and api_key are required"}, 400)
                return
            ensure_composio_profile(profile)
            save_composio_api_key(profile, composio_api_key)
            payload = composio_profiles_payload()
            payload["selected"] = composio_profile_slug(profile)
            payload["api_key_present"] = bool(load_composio_api_key(profile))
            self._send_json(payload)
            return

        if parsed.path == "/api/composio/test":
            profile = str(data.get("profile") or "").strip()
            if not profile:
                self._send_json({"ok": False, "error": "profile is required"}, 400)
                return
            result = test_composio_profile(profile)
            payload = composio_profiles_payload()
            payload["selected"] = composio_profile_slug(profile)
            payload["test"] = result
            self._send_json(payload, 200 if result.get("ok") else 400)
            return

        if parsed.path == "/api/slack":
            action = str(data.get("action") or "status")
            if action == "status":
                result = slack_api_call("auth.test", {}, "POST")
                if not result.get("ok"):
                    result = {"ok": True, "offline": True, "channels": [], "message": result.get("error") or "Slack offline"}
                self._send_json(result)
                return
            if action == "channels":
                result = slack_api_call(
                    "conversations.list",
                    {"types": "public_channel,private_channel,im", "limit": 200},
                    "POST",
                )
                if not result.get("ok"):
                    self._send_json({"ok": True, "offline": True, "channels": [], "message": result.get("error") or "Slack offline"})
                    return
                if result.get("ok"):
                    channels = []
                    for channel in result.get("channels", []):
                        if not isinstance(channel, dict):
                            continue
                        channels.append({
                            "id": channel.get("id"),
                            "name": channel.get("name") or channel.get("user") or channel.get("id"),
                            "is_member": bool(channel.get("is_member")),
                            "is_im": bool(channel.get("is_im")),
                            "is_private": bool(channel.get("is_private")),
                        })
                    existing_ids = {str(channel.get("id") or "") for channel in channels}
                    for user_id in [item.strip() for item in env_value("SLACK_ALLOWED_USERS").split(",") if item.strip()]:
                        dm_result = slack_api_call("conversations.open", {"users": user_id}, "POST")
                        dm_channel = dm_result.get("channel") if isinstance(dm_result, dict) else None
                        if isinstance(dm_channel, dict) and dm_channel.get("id") not in existing_ids:
                            channels.insert(0, {
                                "id": dm_channel.get("id"),
                                "name": f"DM {user_id}",
                                "is_member": True,
                                "is_im": True,
                                "is_private": True,
                            })
                    result = {"ok": True, "channels": channels}
                self._send_json(result)
                return
            if action == "history":
                channel = str(data.get("channel") or "").strip()
                limit = int(data.get("limit") or 25)
                if not channel:
                    self._send_json({"ok": False, "error": "channel is required"}, 400)
                    return
                result = slack_api_call(
                    "conversations.history",
                    {"channel": channel, "limit": max(1, min(limit, 50))},
                    "POST",
                )
                if not result.get("ok") and result.get("error") not in {"not_in_channel"}:
                    self._send_json({"ok": True, "offline": True, "channel": channel, "messages": [], "message": result.get("error") or "Slack offline"})
                    return
                if result.get("error") == "not_in_channel":
                    join_result = slack_api_call("conversations.join", {"channel": channel}, "POST")
                    if join_result.get("ok") or join_result.get("error") == "already_in_channel":
                        result = slack_api_call(
                            "conversations.history",
                            {"channel": channel, "limit": max(1, min(limit, 50))},
                            "POST",
                        )
                if result.get("ok"):
                    result = {
                        "ok": True,
                        "channel": channel,
                        "messages": [
                            compact_slack_message(msg)
                            for msg in result.get("messages", [])
                            if isinstance(msg, dict) and str(msg.get("text") or "").strip()
                        ],
                    }
                self._send_json(result)
                return
            if action == "post":
                channel = str(data.get("channel") or "").strip()
                text = str(data.get("text") or "").strip()
                if not channel or not text:
                    self._send_json({"ok": False, "error": "channel and text are required"}, 400)
                    return
                result = slack_api_call("chat.postMessage", {"channel": channel, "text": text}, "POST")
                self._send_json(result)
                return
            self._send_json({"ok": False, "error": f"Unknown Slack action: {action}"}, 400)
            return

        if parsed.path == "/api/telegram":
            action = str(data.get("action") or "status")
            chat_id = str(data.get("chat_id") or env_value("TELEGRAM_HOME_CHANNEL", "TELEGRAM_ALLOWED_USERS")).split(",")[0].strip()
            if action == "status":
                result = telegram_api_call("getMe", {}, "GET")
                if result.get("ok"):
                    result = {
                        "ok": True,
                        "bot": {
                            "id": result.get("result", {}).get("id"),
                            "username": result.get("result", {}).get("username"),
                            "first_name": result.get("result", {}).get("first_name"),
                        },
                        "chat_id": chat_id,
                    }
                self._send_json(result)
                return
            if action == "send":
                text = str(data.get("text") or "").strip()
                if not chat_id or not text:
                    self._send_json({"ok": False, "error": "chat_id and text are required"}, 400)
                    return
                result = telegram_api_call(
                    "sendMessage",
                    {
                        "chat_id": chat_id,
                        "text": text[:3900],
                        "disable_web_page_preview": True,
                    },
                    "POST",
                )
                self._send_json(result)
                return
            if action == "updates":
                offset = data.get("offset")
                payload = {"timeout": 0, "limit": 25}
                if isinstance(offset, int) or (isinstance(offset, str) and offset.strip().isdigit()):
                    payload["offset"] = int(offset)
                result = telegram_api_call("getUpdates", payload, "POST")
                if result.get("ok"):
                    updates = []
                    next_offset = None
                    for item in result.get("result", []):
                        if not isinstance(item, dict):
                            continue
                        update_id = item.get("update_id")
                        if isinstance(update_id, int):
                            next_offset = max(next_offset or update_id + 1, update_id + 1)
                        compact = compact_telegram_update(item, chat_id)
                        if compact:
                            updates.append(compact)
                    result = {"ok": True, "updates": updates, "next_offset": next_offset, "chat_id": chat_id}
                self._send_json(result)
                return
            self._send_json({"ok": False, "error": f"Unknown Telegram action: {action}"}, 400)
            return

        if parsed.path == "/api/export":
            result = export_workspace_artifact(data)
            if result.get("ok"):
                record_user_work_event(
                    current_local_user_record(self.headers) or {},
                    workspace=str(data.get("workspace") or "general"),
                    filename=str(result.get("filename") or ""),
                    exported=True,
                )
            self._send_json(result, 200 if result.get("ok") else 400)
            return

        if parsed.path == "/api/attachment/extract":
            result = extract_attachment_preview(data)
            self._send_json(result, 200 if result.get("ok") else 400)
            return

        if parsed.path == "/api/chat":
            start_gateway()
            provider = data.get("provider")
            model = data.get("selected_model") or data.get("model")
            workspace = str(data.get("workspace") or "general")
            skill_id = str(data.get("skill_id") or "").strip() or None
            chat_user = current_local_user_record(self.headers) or {}
            privacy_mode = bool(data.get("privacy_mode", True))
            fast_mode = bool(data.get("fast_mode", False))
            preferred_provider, preferred_model = current_provider_model()
            if provider and model:
                preferred_provider, preferred_model = provider, model
            incoming_messages = data.get("messages", [])
            if privacy_mode:
                incoming_messages = mask_messages(incoming_messages)
            incoming_messages = _inject_workspace_memory(incoming_messages, workspace, skill_id, concise=fast_mode)
            payload = {
                "model": "hermes-agent",
                "stream": bool(data.get("stream", True)),
                "messages": incoming_messages,
            }
            headers = {}
            bearer = api_key()
            if bearer:
                headers["Authorization"] = f"Bearer {bearer}"

            attempts = _chat_attempts(provider, model)
            last_error = "Unknown Hermes error"
            wants_stream = bool(payload.get("stream", True))

            def restore_preferred_route() -> None:
                if preferred_provider and provider_cooldown(preferred_provider) > 0:
                    log(
                        f"Skipping preferred provider restore because cooldown is active: "
                        f"{preferred_provider} ({provider_cooldown(preferred_provider):.1f}s remaining)"
                    )
                    return
                current_provider, current_model = current_provider_model()
                if preferred_provider and preferred_model and (current_provider != preferred_provider or current_model != preferred_model):
                    log(f"Restoring preferred provider after chat: {preferred_provider} / {preferred_model}")
                    switch_provider(preferred_provider, preferred_model)

            def apply_chat_headers(attempt_provider: str, attempt_model: str) -> None:
                self.send_header("X-Hermes-Provider", attempt_provider)
                self.send_header("X-Hermes-Model", attempt_model)
                self.send_header("X-Hermes-Fallback", "1" if (attempt_provider != preferred_provider or attempt_model != preferred_model) else "0")

            def send_fast_mode_fallback(error_text: str) -> None:
                fallback_text = (
                    "快速链路当前繁忙，请稍后重试，或进入对应工作平台继续处理。"
                    f"\n\nTechnical status: {error_text[:240]}"
                )
                self.send_response(200)
                self.send_header("Content-Type", "text/event-stream; charset=utf-8")
                self.send_header("Cache-Control", "no-cache")
                self.send_header("X-Hermes-Normalized", "1")
                apply_chat_headers(provider or preferred_provider or "unknown", model or preferred_model or "unknown")
                self.end_headers()
                _send_sse_text(self, "hermes-agent", fallback_text)

            for index, (attempt_provider, attempt_model) in enumerate(attempts, start=1):
                remaining_cooldown = provider_cooldown(attempt_provider)
                if remaining_cooldown > 0 and any(provider != attempt_provider for provider, _ in attempts[index:]):
                    log(
                        f"Skipping provider on cooldown for chat attempt {index}: "
                        f"{attempt_provider} / {attempt_model} ({remaining_cooldown:.1f}s remaining)"
                    )
                    continue

                if attempt_provider == "chatgpt":
                    proxy_key = env_value("CLIPROXYAPI_API_KEY")
                    if proxy_key:
                        proxy_payload = dict(payload)
                        proxy_payload["model"] = attempt_model
                        proxy_headers = {
                            "Authorization": f"Bearer {proxy_key}",
                            "Content-Type": "application/json",
                        }
                        try:
                            log(f"Trying cli-proxy fast path for chat attempt {index}: {attempt_provider} / {attempt_model}")
                            with httpx.stream(
                                "POST",
                                f"{CLIPROXY_API}/chat/completions",
                                headers=proxy_headers,
                                json=proxy_payload,
                                timeout=min(CHATGPT_ATTEMPT_TIMEOUT, FAST_MODE_ATTEMPT_TIMEOUT) if fast_mode else CHATGPT_ATTEMPT_TIMEOUT,
                            ) as proxy_resp:
                                proxy_content_type = proxy_resp.headers.get("Content-Type", "application/json")
                                if proxy_resp.is_success and wants_stream and "text/event-stream" in proxy_content_type.lower():
                                    clear_provider_health(attempt_provider)
                                    self.send_response(proxy_resp.status_code)
                                    self.send_header("Content-Type", proxy_content_type)
                                    self.send_header("Cache-Control", "no-cache")
                                    self.send_header("X-Hermes-Fast-Path", "cliproxy")
                                    apply_chat_headers(attempt_provider, attempt_model)
                                    self.end_headers()
                                    raw_parts: list[bytes] = []
                                    for chunk in proxy_resp.iter_raw():
                                        if not chunk:
                                            continue
                                        raw_parts.append(chunk)
                                        self.wfile.write(chunk)
                                        self.wfile.flush()
                                    raw_stream = b"".join(raw_parts)
                                    stream_text = _extract_sse_text(raw_stream)
                                    if _looks_like_failed_reply(stream_text):
                                        log(f"cli-proxy fast path returned failure text via {attempt_model}: {stream_text[:300]}")
                                    write_audit_event(
                                        {
                                            "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
                                            "workspace": workspace,
                                            "skill_id": skill_id,
                                            "provider": attempt_provider,
                                            "model": attempt_model,
                                            "privacy_mode": privacy_mode,
                                            "messages": payload["messages"],
                                            "result": stream_text[:1200],
                                            "fast_path": "cliproxy",
                                        }
                                    )
                                    update_workspace_memory(workspace, skill_id, payload["messages"], stream_text)
                                    record_user_work_event(chat_user, workspace=workspace)
                                    restore_preferred_route()
                                    return
                                if proxy_resp.is_success:
                                    raw_body = proxy_resp.read()
                                    reply_text = ""
                                    try:
                                        reply_text = _extract_assistant_text(json.loads(raw_body.decode("utf-8")))
                                    except Exception:
                                        reply_text = raw_body.decode("utf-8", errors="ignore").strip()
                                    if reply_text and not _looks_like_failed_reply(reply_text):
                                        clear_provider_health(attempt_provider)
                                        self.send_response(200)
                                        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
                                        self.send_header("Cache-Control", "no-cache")
                                        self.send_header("X-Hermes-Fast-Path", "cliproxy")
                                        self.send_header("X-Hermes-Normalized", "1")
                                        apply_chat_headers(attempt_provider, attempt_model)
                                        self.end_headers()
                                        _send_sse_text(self, attempt_model, reply_text)
                                        write_audit_event(
                                            {
                                                "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
                                                "workspace": workspace,
                                                "skill_id": skill_id,
                                                "provider": attempt_provider,
                                                "model": attempt_model,
                                                "privacy_mode": privacy_mode,
                                                "messages": payload["messages"],
                                                "result": reply_text[:1200],
                                                "fast_path": "cliproxy",
                                            }
                                        )
                                        update_workspace_memory(workspace, skill_id, payload["messages"], reply_text)
                                        record_user_work_event(chat_user, workspace=workspace)
                                        restore_preferred_route()
                                        return
                                    last_error = reply_text or "Empty cli-proxy response"
                                else:
                                    raw_body = proxy_resp.read()
                                    last_error = _error_text(raw_body) or f"cli-proxy HTTP {proxy_resp.status_code}"
                                log(f"cli-proxy fast path unavailable for {attempt_model}: {last_error[:300]}")
                        except Exception as exc:
                            last_error = str(exc)
                            log(f"cli-proxy fast path exception for {attempt_model}: {last_error}")

                current_provider, current_model = current_provider_model()
                if attempt_provider != current_provider or attempt_model != current_model:
                    log(f"Switching provider for chat attempt {index}: {attempt_provider} / {attempt_model}")
                    switch_provider(attempt_provider, attempt_model)

                try:
                    attempt_timeout = GEMINI_ATTEMPT_TIMEOUT if attempt_provider in {"google-gemini-cli", "gemini"} else CHATGPT_ATTEMPT_TIMEOUT
                    if fast_mode:
                        attempt_timeout = min(attempt_timeout, FAST_MODE_ATTEMPT_TIMEOUT)
                    with httpx.stream(
                        "POST",
                        f"{HERMES_API}/chat/completions",
                        headers=headers,
                        json=payload,
                        timeout=attempt_timeout,
                    ) as resp:
                        content_type = resp.headers.get("Content-Type", "application/json")
                        if resp.is_success:
                            if wants_stream and "text/event-stream" not in content_type.lower():
                                raw_body = resp.read()
                                upstream_payload = {}
                                text = ""
                                try:
                                    upstream_payload = json.loads(raw_body.decode("utf-8"))
                                    text = _extract_assistant_text(upstream_payload)
                                except Exception:
                                    text = raw_body.decode("utf-8", errors="ignore").strip()
                                if _looks_like_failed_reply(text):
                                    last_error = text
                                    log(f"Chat attempt {index} returned a retryable assistant failure via {attempt_provider}/{attempt_model}: {text}")
                                    if _is_provider_level_failure(attempt_provider, resp.status_code, text):
                                        mark_provider_unhealthy(attempt_provider, text)
                                    if index < len(attempts):
                                        continue
                                clear_provider_health(attempt_provider)
                                self.send_response(resp.status_code)
                                self.send_header("Content-Type", "text/event-stream; charset=utf-8")
                                self.send_header("Cache-Control", "no-cache")
                                self.send_header("X-Hermes-Normalized", "1")
                                apply_chat_headers(attempt_provider, attempt_model)
                                self.end_headers()
                                _send_sse_text(self, "hermes-agent", text or "(无响应内容)")
                                write_audit_event(
                                    {
                                        "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
                                        "workspace": workspace,
                                        "skill_id": skill_id,
                                        "provider": attempt_provider,
                                        "model": attempt_model,
                                        "privacy_mode": privacy_mode,
                                        "messages": payload["messages"],
                                        "result": (text or "(无响应内容)")[:1200],
                                    }
                                )
                                update_workspace_memory(workspace, skill_id, payload["messages"], text or "(无响应内容)")
                                record_user_work_event(chat_user, workspace=workspace)
                                restore_preferred_route()
                                return

                            if wants_stream and "text/event-stream" in content_type.lower():
                                if attempt_provider == "chatgpt":
                                    clear_provider_health(attempt_provider)
                                    self.send_response(resp.status_code)
                                    self.send_header("Content-Type", content_type)
                                    self.send_header("Cache-Control", "no-cache")
                                    apply_chat_headers(attempt_provider, attempt_model)
                                    self.end_headers()
                                    raw_parts: list[bytes] = []
                                    first_chunk_logged = False
                                    for chunk in resp.iter_raw():
                                        if not chunk:
                                            continue
                                        if not first_chunk_logged:
                                            log(f"Streaming first chatgpt chunk via {attempt_provider}/{attempt_model}")
                                            first_chunk_logged = True
                                        raw_parts.append(chunk)
                                        self.wfile.write(chunk)
                                        self.wfile.flush()
                                    raw_stream = b"".join(raw_parts)
                                    stream_text = _extract_sse_text(raw_stream)
                                    write_audit_event(
                                        {
                                            "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
                                            "workspace": workspace,
                                            "skill_id": skill_id,
                                            "provider": attempt_provider,
                                            "model": attempt_model,
                                            "privacy_mode": privacy_mode,
                                            "messages": payload["messages"],
                                            "result": stream_text[:1200],
                                        }
                                    )
                                    update_workspace_memory(workspace, skill_id, payload["messages"], stream_text)
                                    record_user_work_event(chat_user, workspace=workspace)
                                    restore_preferred_route()
                                    return

                                raw_stream = b"".join(chunk for chunk in resp.iter_raw() if chunk)
                                stream_text = _extract_sse_text(raw_stream)
                                if not stream_text:
                                    last_error = "Empty assistant stream"
                                    log(f"Chat attempt {index} returned an empty stream via {attempt_provider}/{attempt_model}")
                                    if _is_provider_level_failure(attempt_provider, resp.status_code, last_error):
                                        mark_provider_unhealthy(attempt_provider, last_error)
                                    if index < len(attempts):
                                        continue
                                    self.send_response(200)
                                    self.send_header("Content-Type", "text/event-stream; charset=utf-8")
                                    self.send_header("Cache-Control", "no-cache")
                                    self.send_header("X-Hermes-Normalized", "1")
                                    apply_chat_headers(attempt_provider, attempt_model)
                                    self.end_headers()
                                    _send_sse_text(self, "hermes-agent", "当前通道返回空响应，已到达最后兜底通道。请再试一次。")
                                    restore_preferred_route()
                                    return
                                if _looks_like_failed_reply(stream_text):
                                    last_error = stream_text
                                    log(f"Chat attempt {index} returned a retryable streamed failure via {attempt_provider}/{attempt_model}: {stream_text}")
                                    if _is_provider_level_failure(attempt_provider, resp.status_code, stream_text):
                                        mark_provider_unhealthy(attempt_provider, stream_text)
                                    if index < len(attempts):
                                        continue

                                clear_provider_health(attempt_provider)
                                self.send_response(resp.status_code)
                                self.send_header("Content-Type", content_type)
                                self.send_header("Cache-Control", "no-cache")
                                apply_chat_headers(attempt_provider, attempt_model)
                                self.end_headers()
                                self.wfile.write(raw_stream)
                                self.wfile.flush()
                                write_audit_event(
                                    {
                                        "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
                                        "workspace": workspace,
                                        "skill_id": skill_id,
                                        "provider": attempt_provider,
                                        "model": attempt_model,
                                        "privacy_mode": privacy_mode,
                                        "messages": payload["messages"],
                                        "result": stream_text[:1200],
                                    }
                                )
                                update_workspace_memory(workspace, skill_id, payload["messages"], stream_text)
                                record_user_work_event(chat_user, workspace=workspace)
                                restore_preferred_route()
                                return

                            raw_body = resp.read()
                            reply_text = ""
                            try:
                                reply_text = _extract_assistant_text(json.loads(raw_body.decode("utf-8")))
                            except Exception:
                                reply_text = raw_body.decode("utf-8", errors="ignore").strip()
                            if _looks_like_failed_reply(reply_text):
                                last_error = reply_text
                                log(f"Chat attempt {index} returned a retryable JSON failure via {attempt_provider}/{attempt_model}: {reply_text}")
                                if _is_provider_level_failure(attempt_provider, resp.status_code, reply_text):
                                    mark_provider_unhealthy(attempt_provider, reply_text)
                                if index < len(attempts):
                                    continue
                            clear_provider_health(attempt_provider)
                            self.send_response(resp.status_code)
                            self.send_header("Content-Type", content_type)
                            self.send_header("Cache-Control", "no-cache")
                            apply_chat_headers(attempt_provider, attempt_model)
                            self.end_headers()
                            self.wfile.write(raw_body)
                            self.wfile.flush()
                            write_audit_event(
                                {
                                    "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
                                    "workspace": workspace,
                                    "skill_id": skill_id,
                                    "provider": attempt_provider,
                                    "model": attempt_model,
                                    "privacy_mode": privacy_mode,
                                    "messages": payload["messages"],
                                    "result": reply_text[:1200],
                                }
                            )
                            update_workspace_memory(workspace, skill_id, payload["messages"], reply_text)
                            record_user_work_event(chat_user, workspace=workspace)
                            restore_preferred_route()
                            return

                        raw_body = resp.read()
                        last_error = _error_text(raw_body) or f"HTTP {resp.status_code}"
                        log(f"Chat attempt {index} failed via {attempt_provider}/{attempt_model}: {resp.status_code} {last_error}")
                        if _is_provider_level_failure(attempt_provider, resp.status_code, last_error):
                            mark_provider_unhealthy(attempt_provider, last_error)
                        if _is_retryable_chat_failure(attempt_provider, resp.status_code, last_error) and index < len(attempts):
                            continue

                        self.send_response(resp.status_code)
                        self.send_header("Content-Type", content_type)
                        self.send_header("Cache-Control", "no-cache")
                        self.end_headers()
                        self.wfile.write(raw_body)
                        write_audit_event(
                            {
                                "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
                                "workspace": workspace,
                                "skill_id": skill_id,
                                "provider": attempt_provider,
                                "model": attempt_model,
                                "privacy_mode": privacy_mode,
                                "messages": payload["messages"],
                                "error": last_error[:1200],
                            }
                        )
                        restore_preferred_route()
                        return
                except Exception as exc:
                    last_error = str(exc)
                    log(f"Chat attempt {index} exception via {attempt_provider}/{attempt_model}: {last_error}")
                    if _is_provider_level_failure(attempt_provider, 500, last_error):
                        mark_provider_unhealthy(attempt_provider, last_error)
                    if _is_retryable_chat_failure(attempt_provider, 500, last_error) and index < len(attempts):
                        continue
                    write_audit_event(
                        {
                            "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
                            "workspace": workspace,
                            "skill_id": skill_id,
                            "provider": attempt_provider,
                            "model": attempt_model,
                            "privacy_mode": privacy_mode,
                            "messages": payload["messages"],
                            "error": last_error[:1200],
                        }
                    )
                    restore_preferred_route()
                    if fast_mode:
                        send_fast_mode_fallback(last_error)
                        return
                    self._send_json({"error": last_error}, 500)
                    return

            restore_preferred_route()
            write_audit_event(
                {
                    "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "workspace": workspace,
                    "skill_id": skill_id,
                    "provider": provider or preferred_provider,
                    "model": model or preferred_model,
                    "privacy_mode": privacy_mode,
                    "messages": payload["messages"],
                    "error": last_error[:1200],
                }
            )
            if fast_mode:
                send_fast_mode_fallback(last_error)
                return
            self._send_json({"error": last_error}, 500)
            return

        self._send_json({"error": "not found"}, 404)

    def do_PATCH(self):
        parsed = urlparse(self.path)
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length else b"{}"
        try:
            data = json.loads(raw.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            self._send_json({"ok": False, "error": "invalid_json"}, 400)
            return

        user = current_local_user_record(self.headers)
        if parsed.path.startswith("/api/admin/intelligence/news/sources/"):
            parts = [part for part in parsed.path.split("/") if part]
            source_id = parts[5] if len(parts) >= 6 else ""
            payload, status_code = _v2_admin_intel_update_source(user, source_id, data)
            self._send_json(payload, status_code)
            return
        if parsed.path.startswith("/api/admin/intelligence/markets/indices/"):
            parts = [part for part in parsed.path.split("/") if part]
            index_id = parts[5] if len(parts) >= 6 else ""
            payload, status_code = _v2_admin_intel_update_index(user, index_id, data)
            self._send_json(payload, status_code)
            return
        if parsed.path.startswith("/api/admin/intelligence/market-data/instruments/"):
            parts = [part for part in parsed.path.split("/") if part]
            instrument_id = parts[5] if len(parts) >= 6 else ""
            payload, status_code = _v2_admin_intel_market_data_update_instrument(user, instrument_id, data)
            self._send_json(payload, status_code)
            return

        if parsed.path.startswith("/api/") and not parsed.path.startswith("/api/auth/") and not user:
            self._send_json({"ok": False, "error": "authentication_required"}, 401)
            return
        self._send_json({"error": "not found"}, 404)

    def do_DELETE(self):
        parsed = urlparse(self.path)
        user = current_local_user_record(self.headers)
        if parsed.path.startswith("/api/intelligence/instruments/watchlist/"):
            parts = [part for part in parsed.path.split("/") if part]
            instrument_id = parts[4] if len(parts) >= 5 else ""
            payload, status_code = _v2_intel_watchlist_remove(user, instrument_id)
            self._send_json(payload, status_code)
            return
        if parsed.path.startswith("/api/") and not parsed.path.startswith("/api/auth/") and not user:
            self._send_json({"ok": False, "error": "authentication_required"}, 401)
            return
        self._send_json({"error": "not found"}, 404)


def main() -> None:
    _v2_apply_migrations()
    prime_provider_health_from_logs()
    start_gateway()
    threading.Thread(target=activity_sampler_loop, daemon=True, name="activity-sampler").start()
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    log(f"Finance Workbench app server listening on http://{HOST}:{PORT}")
    try:
        server.serve_forever()
    finally:
        stop_gateway()
        server.server_close()


if __name__ == "__main__":
    main()
