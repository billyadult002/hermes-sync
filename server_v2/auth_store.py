"""Auth store for server_v2.

Reads/writes the same local_users.json and local_sessions.json files as
app_server.py so both servers share auth state during the migration period.
"""
from __future__ import annotations

import hashlib
import hmac
import re
import secrets
import threading
import time
from pathlib import Path
from typing import Any

from .config import (
    ADMIN_EMAIL,
    ADMIN_PERMISSION_KEYS,
    BROWSER_SESSION_HEADER,
    DEFAULT_ADMIN_MAX_IDLE_TIMEOUT_SECONDS,
    DEFAULT_USER_IDLE_TIMEOUT_SECONDS,
    LOCAL_AUTH_SESSIONS,
    LOCAL_AUTH_USERS,
    MAX_IDLE_TIMEOUT_SECONDS,
    MIN_IDLE_TIMEOUT_SECONDS,
    PLATFORM_CONTROL_PATH,
    SESSION_COOKIE_NAME,
)
from .utils import bool_field, load_json_file, normalize_email, save_json_file

_auth_lock = threading.Lock()
_platform_lock = threading.Lock()


# ---------------------------------------------------------------------------
# Low-level helpers
# ---------------------------------------------------------------------------

def _password_hash(password: str, salt_hex: str) -> str:
    salt = bytes.fromhex(salt_hex)
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 180000).hex()


def _normalize_browser_session_id(value: str | None) -> str:
    raw = str(value or "").strip()
    safe = "".join(ch for ch in raw if ch.isalnum() or ch in "-_:.")
    return safe[:160]


def _normalize_username(value: str) -> str:
    text = re.sub(r"[^a-zA-Z0-9._-]", "", str(value or "").strip().lower())
    return text[:32]


def _normalize_inactivity_timeout_minutes(value: Any) -> int:
    try:
        minutes = int(value or 0)
    except Exception:
        return 0
    if minutes <= 0:
        return 0
    return max(1, min(minutes, 24 * 60))


def _clamp_idle_timeout(seconds: int) -> int:
    return max(MIN_IDLE_TIMEOUT_SECONDS, min(seconds, MAX_IDLE_TIMEOUT_SECONDS))


# ---------------------------------------------------------------------------
# Platform settings (for idle timeout policy)
# ---------------------------------------------------------------------------

def _platform_settings() -> dict:
    with _platform_lock:
        data = load_json_file(PLATFORM_CONTROL_PATH, {})
    if not isinstance(data, dict):
        return {}
    return data.get("settings", {})


def _session_idle_timeout_seconds(user: dict | None = None, role: str | None = None) -> int:
    settings = _platform_settings()
    admin_max_minutes = _normalize_inactivity_timeout_minutes(
        settings.get("admin_max_inactivity_timeout_minutes")
    )
    admin_max = (admin_max_minutes * 60) if admin_max_minutes > 0 else DEFAULT_ADMIN_MAX_IDLE_TIMEOUT_SECONDS
    admin_max = _clamp_idle_timeout(admin_max)

    default_user_minutes = _normalize_inactivity_timeout_minutes(
        settings.get("default_inactivity_timeout_minutes")
    )
    default_user = (default_user_minutes * 60) if default_user_minutes > 0 else DEFAULT_USER_IDLE_TIMEOUT_SECONDS
    default_user = min(_clamp_idle_timeout(default_user), admin_max)

    if isinstance(user, dict):
        custom_minutes = _normalize_inactivity_timeout_minutes(user.get("inactivity_timeout_minutes"))
        if custom_minutes > 0:
            return min(custom_minutes * 60, admin_max)

    resolved_role = str(role or (user or {}).get("role") or "user").strip().lower()
    if resolved_role == "admin":
        return admin_max
    return default_user


# ---------------------------------------------------------------------------
# Permissions
# ---------------------------------------------------------------------------

def _default_user_permissions() -> dict:
    return {
        "pages": ["home", "finance", "legal", "skills"],
        "platforms": ["*"],
        "colleagues": ["*"],
        "user_admin": False,
        "view_team_status": False,
        "view_document_flows": False,
        "admin_permissions": [],
        "can_read_files": True,
        "can_upload_files": True,
        "can_modify_files": True,
        "can_delete_files": False,
        "can_download_files": True,
    }


def _admin_permissions() -> dict:
    return {
        "pages": ["*"],
        "platforms": ["*"],
        "colleagues": ["*"],
        "user_admin": True,
        "view_team_status": True,
        "view_document_flows": True,
        "admin_permissions": sorted(ADMIN_PERMISSION_KEYS),
        "can_read_files": True,
        "can_upload_files": True,
        "can_modify_files": True,
        "can_delete_files": True,
        "can_download_files": True,
    }


def normalize_permissions(value: Any, admin: bool = False) -> dict:
    base = _admin_permissions() if admin else _default_user_permissions()
    if not isinstance(value, dict):
        return base
    if admin:
        return _admin_permissions()
    pages = value.get("pages")
    platforms = value.get("platforms")
    colleagues = value.get("colleagues")
    return {
        "pages": [str(i).strip() for i in (pages if isinstance(pages, list) else base["pages"]) if str(i).strip()],
        "platforms": [str(i).strip() for i in (platforms if isinstance(platforms, list) else base["platforms"]) if str(i).strip()],
        "colleagues": [normalize_email(i) for i in (colleagues if isinstance(colleagues, list) else base["colleagues"]) if normalize_email(i)],
        "user_admin": bool(value.get("user_admin", base["user_admin"])),
        "view_team_status": bool(value.get("view_team_status", base["view_team_status"])),
        "view_document_flows": bool(value.get("view_document_flows", base["view_document_flows"])),
        "admin_permissions": [
            str(i).strip()
            for i in (value.get("admin_permissions") if isinstance(value.get("admin_permissions"), list) else [])
            if str(i).strip() in ADMIN_PERMISSION_KEYS
        ],
        "can_read_files": bool(value.get("can_read_files", base.get("can_read_files", True))),
        "can_upload_files": bool(value.get("can_upload_files", base.get("can_upload_files", True))),
        "can_modify_files": bool(value.get("can_modify_files", base.get("can_modify_files", True))),
        "can_delete_files": bool(value.get("can_delete_files", base.get("can_delete_files", False))),
        "can_download_files": bool(value.get("can_download_files", base.get("can_download_files", True))),
    }


# ---------------------------------------------------------------------------
# User lookups
# ---------------------------------------------------------------------------

def is_super_admin_email(email: str) -> bool:
    return normalize_email(email) == normalize_email(ADMIN_EMAIL)


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


def _load_users() -> list[dict]:
    with _auth_lock:
        data = load_json_file(LOCAL_AUTH_USERS, {"users": []})
    if not isinstance(data, dict):
        return []
    users = data.get("users")
    return users if isinstance(users, list) else []


def _save_users(users: list[dict]) -> None:
    with _auth_lock:
        save_json_file(LOCAL_AUTH_USERS, {"users": users})


def find_local_user(email: str) -> dict | None:
    email_key = normalize_email(email)
    for user in _load_users():
        if isinstance(user, dict) and normalize_email(user.get("email", "")) == email_key:
            return user
    return None


def find_local_user_by_identifier(identifier: str) -> dict | None:
    identifier = str(identifier or "").strip()
    if "@" in identifier:
        return find_local_user(identifier)
    username_key = _normalize_username(identifier)
    if username_key:
        users = _load_users()
        for user in users:
            if isinstance(user, dict) and _normalize_username(user.get("username", "")) == username_key:
                return user
    return find_local_user(identifier)


def mark_local_user_login(email: str) -> None:
    users = _load_users()
    email_key = normalize_email(email)
    for idx, user in enumerate(users):
        if isinstance(user, dict) and normalize_email(user.get("email", "")) == email_key:
            users[idx]["last_login_at"] = int(time.time())
            _save_users(users)
            return


def public_user_record(user: dict) -> dict:
    email_key = normalize_email(user.get("email", ""))
    is_super = is_super_admin_email(email_key)
    inactivity_timeout = _normalize_inactivity_timeout_minutes(user.get("inactivity_timeout_minutes"))
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
        "user_id": email_key,
        "is_super_admin": is_super,
        "is_admin": is_super or user.get("role") == "admin",
        "can_login": True if is_super else bool_field(user, "can_login", True),
        "can_use_platform": True if is_super else bool_field(user, "can_use_platform", True),
        "disabled_at": user.get("disabled_at", 0),
        "permissions": normalize_permissions(user.get("permissions"), admin=is_super),
        "created_at": user.get("created_at", 0),
        "last_login_at": user.get("last_login_at", 0),
        "password_updated_at": user.get("password_updated_at", 0),
        "inactivity_timeout_minutes": inactivity_timeout,
    }


def verify_local_user(identifier: str, password: str) -> tuple[bool, str, dict | None]:
    user = find_local_user_by_identifier(identifier)
    if not user:
        return False, "user_not_found", None
    approval_status = str(user.get("approval_status") or "approved")
    if approval_status == "pending":
        return False, "account_pending_approval", None
    if approval_status == "rejected":
        return False, "account_rejected", None
    if is_super_admin_email(user.get("email", "")):
        user["can_login"] = True
        user["can_use_platform"] = True
    if not bool_field(user, "can_login", True):
        return False, "LOGIN_NOT_ALLOWED", None
    salt_hex = str(user.get("password_salt") or "")
    stored_hash = str(user.get("password_hash") or "")
    if not salt_hex or not stored_hash:
        return False, "invalid_user_record", None
    candidate = _password_hash(password, salt_hex)
    if not hmac.compare_digest(candidate, stored_hash):
        return False, "invalid_password", None
    return True, "ok", public_user_record(user)


# ---------------------------------------------------------------------------
# Session management
# ---------------------------------------------------------------------------

def _load_sessions() -> dict:
    with _auth_lock:
        data = load_json_file(LOCAL_AUTH_SESSIONS, {"sessions": {}})
    if not isinstance(data, dict):
        return {"sessions": {}}
    sessions = data.get("sessions")
    if not isinstance(sessions, dict):
        data["sessions"] = {}
    return data


def _save_sessions(data: dict) -> None:
    with _auth_lock:
        save_json_file(LOCAL_AUTH_SESSIONS, data)


def _session_is_active(session: dict, now: int | None = None) -> bool:
    if not isinstance(session, dict):
        return False
    current = int(now or time.time())
    if int(session.get("expires_at", 0) or 0) <= current:
        return False
    idle_timeout = int(session.get("idle_timeout_seconds", 0) or 0)
    if idle_timeout <= 0:
        user = find_local_user(normalize_email(session.get("email", "")))
        idle_timeout = _session_idle_timeout_seconds(user, session.get("role"))
    last_seen = int(session.get("last_seen_at", session.get("created_at", 0)) or 0)
    return (current - last_seen) <= idle_timeout


def _session_browser_matches(session: dict, browser_session_id: str) -> bool:
    stored = _normalize_browser_session_id(session.get("browser_session_id"))
    if not stored:
        return False
    return secrets.compare_digest(stored, _normalize_browser_session_id(browser_session_id))


def cleanup_sessions() -> None:
    payload = _load_sessions()
    sessions = payload.get("sessions", {})
    now = int(time.time())
    filtered = {
        token: session
        for token, session in sessions.items()
        if _session_is_active(session, now)
    }
    if filtered != sessions:
        _save_sessions({"sessions": filtered})


def create_local_session(user: dict, browser_session_id: str = "") -> str:
    cleanup_sessions()
    token = secrets.token_urlsafe(32)
    idle_timeout = _session_idle_timeout_seconds(user)
    now = int(time.time())
    payload = _load_sessions()
    sessions = payload.get("sessions", {})
    sessions[token] = {
        "email": normalize_email(user.get("email", "")),
        "created_at": now,
        "last_seen_at": now,
        "browser_session_id": _normalize_browser_session_id(browser_session_id),
        "workspace": "home",
        "page": "home",
        "skill_id": "human-exchange",
        "provider": "",
        "model": "",
        "role": str(user.get("role") or "user"),
        "idle_timeout_seconds": idle_timeout,
        "expires_at": now + idle_timeout,
    }
    _save_sessions({"sessions": sessions})
    return token


def revoke_local_session(token: str) -> None:
    if not token:
        return
    payload = _load_sessions()
    sessions = payload.get("sessions", {})
    if token in sessions:
        sessions.pop(token, None)
        _save_sessions({"sessions": sessions})


def _parse_cookie_map(cookie_header: str) -> dict[str, str]:
    pairs: dict[str, str] = {}
    for chunk in (cookie_header or "").split(";"):
        if "=" not in chunk:
            continue
        key, value = chunk.split("=", 1)
        pairs[key.strip()] = value.strip()
    return pairs


def session_token_from_request(
    authorization: str | None = None,
    cookie: str | None = None,
) -> str:
    """Extract session token from Authorization header or Cookie."""
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization.split(" ", 1)[1].strip()
        if token:
            return token
    if cookie:
        return _parse_cookie_map(cookie).get(SESSION_COOKIE_NAME, "")
    return ""


def current_user_from_token(
    token: str, browser_session_id: str = ""
) -> dict | None:
    """Validate token and return public user record, or None if invalid."""
    if not token:
        return None
    cleanup_sessions()
    payload = _load_sessions()
    session = payload.get("sessions", {}).get(token)
    if not _session_is_active(session):
        revoke_local_session(token)
        return None
    if browser_session_id and not _session_browser_matches(session, browser_session_id):
        revoke_local_session(token)
        return None
    email = normalize_email(session.get("email", ""))
    user = find_local_user(email)
    if not user:
        return None
    if not is_user_approved(user):
        revoke_local_session(token)
        return None
    if not bool_field(user, "can_login", True):
        revoke_local_session(token)
        return None
    return public_user_record(user)


def session_payload(token: str, browser_session_id: str = "") -> dict:
    """Build the /api/auth/session response payload."""
    user = current_user_from_token(token, browser_session_id)
    if not user or not token:
        return {"ok": True, "authenticated": False, "user": None, "idle_timeout_seconds": 0, "idle_remaining_seconds": 0}
    payload = _load_sessions()
    session = payload.get("sessions", {}).get(token)
    if not isinstance(session, dict):
        return {"ok": True, "authenticated": bool(user), "user": user, "idle_timeout_seconds": 0, "idle_remaining_seconds": 0}
    idle_timeout = int(session.get("idle_timeout_seconds", 0) or _session_idle_timeout_seconds(user, session.get("role")))
    last_seen = int(session.get("last_seen_at", session.get("created_at", 0)) or 0)
    idle_remaining = max(0, idle_timeout - max(0, int(time.time()) - last_seen))
    return {
        "ok": True,
        "authenticated": True,
        "user": user,
        "idle_timeout_seconds": idle_timeout,
        "idle_remaining_seconds": idle_remaining,
    }


def update_session_activity(token: str) -> None:
    """Touch last_seen_at on the session to reset idle timeout."""
    if not token:
        return
    payload = _load_sessions()
    sessions = payload.get("sessions", {})
    session = sessions.get(token)
    if not isinstance(session, dict):
        return
    session["last_seen_at"] = int(time.time())
    user = find_local_user(normalize_email(session.get("email", "")))
    idle_timeout = _session_idle_timeout_seconds(user, session.get("role"))
    session["idle_timeout_seconds"] = idle_timeout
    session["expires_at"] = int(time.time()) + idle_timeout
    sessions[token] = session
    _save_sessions({"sessions": sessions})


def auth_cookie_header(session_token: str) -> str:
    return f"{SESSION_COOKIE_NAME}={session_token}; Path=/; HttpOnly; SameSite=Lax"


def auth_clear_cookie_header() -> str:
    return f"{SESSION_COOKIE_NAME}=; Path=/; HttpOnly; SameSite=Lax; Max-Age=0; Expires=Thu, 01 Jan 1970 00:00:00 GMT"
