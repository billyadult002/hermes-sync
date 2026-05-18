"""Auth routes: /api/auth/* and /api/me."""
from __future__ import annotations

from fastapi import APIRouter, Cookie, Depends, Header, HTTPException, Request, Response
from fastapi.responses import JSONResponse

from ..auth_store import (
    auth_clear_cookie_header,
    auth_cookie_header,
    create_local_session,
    mark_local_user_login,
    revoke_local_session,
    session_payload,
    session_token_from_request,
    verify_local_user,
)
from ..config import BROWSER_SESSION_HEADER, SESSION_COOKIE_NAME
from ..deps import optional_auth, require_auth
from ..models import LoginRequest, LoginResponse

router = APIRouter()


def _browser_session_id(request: Request) -> str:
    return request.headers.get(BROWSER_SESSION_HEADER, "")


def _extract_token(request: Request, cookie_val: str | None) -> str:
    return session_token_from_request(
        authorization=request.headers.get("Authorization"),
        cookie=f"{SESSION_COOKIE_NAME}={cookie_val}" if cookie_val else None,
    )


@router.post("/api/auth/login")
async def login(
    body: LoginRequest,
    request: Request,
    response: Response,
) -> dict:
    browser_session_id = _browser_session_id(request)
    if not browser_session_id:
        return JSONResponse(status_code=400, content={"ok": False, "error": "browser_session_required"})
    identifier = body.resolved_identifier()
    ok, reason, user = verify_local_user(identifier, body.password)
    if not ok or not user:
        response.headers["Set-Cookie"] = auth_clear_cookie_header()
        raise HTTPException(status_code=400, detail=reason or "login_failed")
    mark_local_user_login(user.get("email", ""))
    token = create_local_session(user, browser_session_id)
    response.headers["Set-Cookie"] = auth_cookie_header(token)
    return {
        "ok": True,
        "authenticated": True,
        "user": user,
        "session_token": token,
        "idle_timeout_seconds": 1800,
    }


@router.post("/api/auth/logout")
async def logout(
    request: Request,
    response: Response,
    fastone_hermes_session: str | None = Cookie(default=None),
) -> dict:
    token = _extract_token(request, fastone_hermes_session)
    if token:
        revoke_local_session(token)
    response.headers["Set-Cookie"] = auth_clear_cookie_header()
    return {"ok": True, "authenticated": False}


@router.get("/api/auth/session")
async def get_session(
    request: Request,
    fastone_hermes_session: str | None = Cookie(default=None),
) -> dict:
    token = _extract_token(request, fastone_hermes_session)
    browser_session_id = _browser_session_id(request)
    return session_payload(token, browser_session_id)


@router.get("/api/me")
async def me(current_user: dict = Depends(require_auth)) -> dict:
    return {"ok": True, "authenticated": True, "user": current_user}


@router.get("/api/me/permissions")
async def me_permissions(current_user: dict = Depends(require_auth)) -> dict:
    return {"ok": True, "permissions": current_user.get("permissions", {})}
