"""Catch-all reverse proxy: forwards unhandled /api/* requests to legacy app_server.py."""
from __future__ import annotations

import logging

import httpx
from fastapi import APIRouter, Request
from fastapi.responses import Response

from ..config import LEGACY_BACKEND_URL

log = logging.getLogger("server_v2.proxy")

router = APIRouter()

_client: httpx.AsyncClient | None = None


def _get_client() -> httpx.AsyncClient:
    global _client
    if _client is None or _client.is_closed:
        _client = httpx.AsyncClient(base_url=LEGACY_BACKEND_URL, timeout=60.0, follow_redirects=False)
    return _client


async def _forward(request: Request, url: str) -> Response:
    """Forward an arbitrary request to the legacy backend, preserving method/body/headers."""
    if request.url.query:
        url = f"{url}?{request.url.query}"
    headers = {k: v for k, v in request.headers.items() if k.lower() not in ("host", "content-length")}
    body = await request.body()
    try:
        resp = await _get_client().request(
            method=request.method,
            url=url,
            headers=headers,
            content=body,
        )
        return Response(
            content=resp.content,
            status_code=resp.status_code,
            headers=dict(resp.headers),
        )
    except httpx.ConnectError:
        log.warning("Legacy backend unavailable at %s for %s %s", LEGACY_BACKEND_URL, request.method, url)
        return Response(
            content=b'{"ok":false,"error":"legacy_backend_unavailable"}',
            status_code=503,
            media_type="application/json",
        )
    except Exception as exc:
        log.error("Proxy error forwarding %s %s: %s", request.method, url, exc)
        return Response(
            content=b'{"ok":false,"error":"proxy_error"}',
            status_code=502,
            media_type="application/json",
        )


@router.api_route(
    "/api/{path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"],
    include_in_schema=False,
)
async def proxy_api_to_legacy(request: Request, path: str) -> Response:
    """Forward unmatched /api/* requests to legacy app_server.py on port 8767."""
    return await _forward(request, f"/api/{path}")


@router.api_route(
    "/{path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"],
    include_in_schema=False,
)
async def proxy_legacy_frontend(request: Request, path: str) -> Response:
    """Strangler-fig: forward all other unhandled routes (legacy console.html,
    /assets/*, etc.) to the legacy backend during the migration period.
    server_v2's own /api routes are registered earlier and take precedence."""
    return await _forward(request, f"/{path}")
