#!/usr/bin/env bash
# Start server_v2 (FastAPI, default port 8766).
# Runs alongside app_server.py during migration period.
set -euo pipefail

cd "$(dirname "$0")"

VENV=".venv"
HOST="${HERMES_V2_HOST:-127.0.0.1}"
PORT="${HERMES_V2_PORT:-8765}"
BASE_URL="http://${HOST}:${PORT}"

if [[ ! -f "${VENV}/bin/python" ]]; then
  echo "ERROR: venv not found at ${VENV}. Run: bash start.sh first to create it." >&2
  exit 1
fi

if ! "${VENV}/bin/python" -c "import fastapi" 2>/dev/null; then
  echo "Installing FastAPI stack into venv..."
  uv pip install "fastapi[standard]>=0.130" "uvicorn[standard]>=0.45" "pydantic>=2.0" --python "${VENV}/bin/python"
fi

if lsof -nP -iTCP:"${PORT}" -sTCP:LISTEN >/dev/null 2>&1; then
  if curl -fsS -m 5 "${BASE_URL}/api/health" >/dev/null 2>&1; then
    echo "server_v2 already healthy at ${BASE_URL}"
    exit 0
  fi
fi

echo "Starting server_v2 at ${BASE_URL}"
exec "${VENV}/bin/python" -m server_v2 --host "${HOST}" --port "${PORT}"
