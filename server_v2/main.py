"""server_v2 — FastAPI application entry point.

Run with:
    .venv/bin/python -m server_v2 [--host HOST] [--port PORT]

During the migration period this server runs alongside app_server.py
(default port 8766) and shares the same data files (local_users.json,
local_sessions.json, task_queue.json).
"""
from __future__ import annotations

import argparse
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import AGENT_POOL_SIZE, MAX_PARALLEL_TASKS
from .routers import auth, copilots, health, orchestrate, proxy, runtime
from .routers.runtime import get_queue
from .workflow import start_workers

log = logging.getLogger("server_v2")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    q = get_queue()
    log.info("Starting v2 worker pool: %d agents, max_parallel=%d", AGENT_POOL_SIZE, MAX_PARALLEL_TASKS)
    start_workers(q, pool_size=AGENT_POOL_SIZE, max_parallel=MAX_PARALLEL_TASKS)
    yield
    log.info("server_v2 shutdown")


app = FastAPI(
    title="Hermes Finance Workbench v2",
    description="FastAPI migration of app_server.py",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(runtime.router)
app.include_router(orchestrate.router)
app.include_router(copilots.router)
app.include_router(proxy.router)  # catch-all: must be last


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    log.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"ok": False, "error": "internal_server_error", "detail": str(exc)[:300]},
    )


def run(host: str | None = None, port: int | None = None) -> None:
    import uvicorn
    from .config import HOST, PORT
    uvicorn.run(
        "server_v2.main:app",
        host=host or HOST,
        port=port or PORT,
        log_level="info",
        access_log=True,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hermes Finance Workbench v2")
    parser.add_argument("--host", default=None)
    parser.add_argument("--port", type=int, default=None)
    args = parser.parse_args()
    run(host=args.host, port=args.port)
