"""Paths, environment, and constants for server_v2.

All path and config values are derived from environment variables so the server
is portable across machines. Defaults match the production layout under ~/.hermes.
"""
from __future__ import annotations

import os
from pathlib import Path


def _env(key: str, default: str = "") -> str:
    return os.getenv(key, default).strip()


def _env_int(key: str, default: int) -> int:
    try:
        return int(_env(key, str(default)))
    except ValueError:
        return default


def _load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        raw = line.strip()
        if not raw or raw.startswith("#") or "=" not in raw:
            continue
        key, value = raw.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


HOME = Path.home()
HERMES_HOME = Path(_env("HERMES_HOME", str(HOME / ".hermes")))
ROOT = Path(_env("HERMES_RUNTIME_ROOT", str(HERMES_HOME / "finance-workbench")))

_load_dotenv(HERMES_HOME / ".env")

# Server
HOST = _env("HERMES_V2_HOST", _env("HERMES_HOST", "127.0.0.1"))
PORT = _env_int("HERMES_V2_PORT", 8766)

# Auth files (shared with app_server.py during migration)
LOCAL_AUTH_USERS = ROOT / "local_users.json"
LOCAL_AUTH_SESSIONS = ROOT / "local_sessions.json"
PLATFORM_CONTROL_PATH = ROOT / "platform_control.json"

# Queue (shared with app_server.py during migration)
V2_DATA_DIR = ROOT / "data"
TASK_QUEUE_PATH = V2_DATA_DIR / "task_queue.json"
TASK_QUEUE_ARCHIVE_PATH = V2_DATA_DIR / "task_queue.archive.jsonl"
MAX_COMPLETED_TASK_HISTORY = 500
MAX_FAILED_TASK_HISTORY = 500

# Worker config
AGENT_POOL_SIZE = _env_int("AGENT_POOL_SIZE", 3)
MAX_PARALLEL_TASKS = _env_int("MAX_PARALLEL_TASKS", 3)

# AI provider endpoints (same as app_server.py)
HERMES_API = _env("HERMES_API", "http://127.0.0.1:8642/v1")
HERMES_BRIDGE_URL = _env("HERMES_BRIDGE_URL", "http://127.0.0.1:8642").rstrip("/")
CLIPROXY_API = _env("CLIPROXY_API", "http://127.0.0.1:8317/v1")

CHATGPT_TARGET_MODEL = "gpt-5.5"
CHATGPT_FALLBACK_MODEL = "gpt-5.4-mini"

# Provider call limits
MAX_PROVIDER_ATTEMPTS = _env_int("MAX_PROVIDER_ATTEMPTS", 6)
MAX_PROVIDER_TOTAL_SECONDS = float(_env("MAX_PROVIDER_TOTAL_SECONDS", "45.0"))
MAX_SINGLE_PROVIDER_SECONDS = float(_env("MAX_SINGLE_PROVIDER_SECONDS", "12.0"))

# Session defaults
DEFAULT_ADMIN_MAX_IDLE_TIMEOUT_SECONDS = 30 * 60
DEFAULT_USER_IDLE_TIMEOUT_SECONDS = 30 * 60
MIN_IDLE_TIMEOUT_SECONDS = 60
MAX_IDLE_TIMEOUT_SECONDS = 8 * 60 * 60

# Legacy app_server.py backend URL (runs on 8767 during migration, server_v2 proxies unknown routes)
LEGACY_BACKEND_PORT = _env_int("HERMES_LEGACY_PORT", 8767)
LEGACY_BACKEND_URL = _env("HERMES_LEGACY_URL", f"http://127.0.0.1:{LEGACY_BACKEND_PORT}")

ADMIN_EMAIL = _env("HERMES_ADMIN_EMAIL", "bill@fastonegroup.com")

BROWSER_SESSION_HEADER = "X-Hermes-Browser-Session"
SESSION_COOKIE_NAME = "fastone_hermes_session"

ADMIN_PERMISSION_KEYS: frozenset[str] = frozenset({
    "manage_users",
    "manage_registration",
    "approve_registration_emails",
    "manage_login_access",
    "manage_platform_access",
    "manage_file_permissions",
    "manage_admins",
    "view_audit_logs",
    "manage_system_settings",
    "manage_session_settings",
    "control_center",
    "admin/control_center",
    "full_control",
})
