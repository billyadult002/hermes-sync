"""FastAPI dependency functions for server_v2."""
from __future__ import annotations

from fastapi import Cookie, Header, HTTPException, Request

from .auth_store import (
    current_user_from_token,
    session_token_from_request,
    update_session_activity,
)
from .config import BROWSER_SESSION_HEADER, SESSION_COOKIE_NAME


def _extract_token(
    authorization: str | None = None,
    fastone_hermes_session: str | None = None,
) -> str:
    return session_token_from_request(
        authorization=authorization,
        cookie=f"{SESSION_COOKIE_NAME}={fastone_hermes_session}" if fastone_hermes_session else None,
    )


async def require_auth(
    request: Request,
    authorization: str | None = Header(default=None),
    fastone_hermes_session: str | None = Cookie(default=None),
) -> dict:
    """Resolve authenticated user or raise 401."""
    token = _extract_token(authorization, fastone_hermes_session)
    browser_session_id = request.headers.get(BROWSER_SESSION_HEADER, "")
    user = current_user_from_token(token, browser_session_id)
    if not user:
        raise HTTPException(status_code=401, detail="authentication_required")
    update_session_activity(token)
    return user


async def optional_auth(
    request: Request,
    authorization: str | None = Header(default=None),
    fastone_hermes_session: str | None = Cookie(default=None),
) -> dict | None:
    """Resolve authenticated user, return None if unauthenticated."""
    token = _extract_token(authorization, fastone_hermes_session)
    if not token:
        return None
    browser_session_id = request.headers.get(BROWSER_SESSION_HEADER, "")
    return current_user_from_token(token, browser_session_id)
