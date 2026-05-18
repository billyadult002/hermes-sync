from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from ..config import PORT

router = APIRouter()


@router.get("/api/health")
async def health() -> JSONResponse:
    return JSONResponse({"ok": True, "service": "hermes-v2", "status": "ready", "port": PORT})
