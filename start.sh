#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

HOST="${HERMES_HOST:-127.0.0.1}"
PORT="${HERMES_PORT:-8765}"              # server_v2 (FastAPI) takes the main port
LEGACY_PORT="${HERMES_LEGACY_PORT:-8767}" # app_server.py moves here
BASE_URL="http://${HOST}:${PORT}"
LEGACY_URL="http://${HOST}:${LEGACY_PORT}"

if command -v node >/dev/null 2>&1; then
  node ./scripts/check-home-entry-links.js
else
  echo "node is not available; skipping static home-entry link check"
fi

# --- venv setup ---
PYTHON_EXE="python3"
VENV_DIR="./.venv"

if [[ ! -d "${VENV_DIR}" ]]; then
  echo "Virtual environment not found. Creating one..."
  if command -v uv >/dev/null 2>&1; then
    uv venv "${VENV_DIR}"
    PYTHON_EXE="${VENV_DIR}/bin/python"
    uv pip install -r requirements.txt --python "${PYTHON_EXE}"
  else
    python3 -m venv "${VENV_DIR}"
    PYTHON_EXE="${VENV_DIR}/bin/python"
    "${PYTHON_EXE}" -m pip install -r requirements.txt
  fi
else
  PYTHON_EXE="${VENV_DIR}/bin/python"
fi

if ! "${PYTHON_EXE}" -c "import httpx" >/dev/null 2>&1; then
  echo "Dependencies missing in ${PYTHON_EXE}. Installing..."
  if command -v uv >/dev/null 2>&1; then
    uv pip install -r requirements.txt --python "${PYTHON_EXE}"
  else
    "${PYTHON_EXE}" -m pip install -r requirements.txt
  fi
fi

# --- Check if server_v2 is already running ---
if lsof -nP -iTCP:"${PORT}" -sTCP:LISTEN >/dev/null 2>&1; then
  if curl -fsS -m 5 "${BASE_URL}/api/health" >/dev/null 2>&1; then
    echo "Finance Workbench is already healthy at ${BASE_URL}; leaving existing service running."
    exit 0
  fi
  echo "Port ${PORT} is occupied but ${BASE_URL}/api/health is not healthy."
  if [[ "${HERMES_SAFE_RESTART:-0}" == "1" ]]; then
    pids="$(lsof -tiTCP:"${PORT}" -sTCP:LISTEN || true)"
    if [[ -n "${pids}" ]]; then
      echo "Stopping existing listener(s) on ${PORT}: ${pids}"
      kill ${pids}
      sleep 2
    fi
  else
    exit 1
  fi
fi

# --- Start legacy app_server.py on 8767 (background) ---
if ! lsof -nP -iTCP:"${LEGACY_PORT}" -sTCP:LISTEN >/dev/null 2>&1; then
  echo "Starting legacy app_server.py at ${LEGACY_URL} ..."
  HERMES_PORT="${LEGACY_PORT}" HERMES_HOST="${HOST}" \
    "${PYTHON_EXE}" -u ./app_server.py > /tmp/app_server_legacy.log 2>&1 &
  LEGACY_PID=$!
  echo "Legacy PID: ${LEGACY_PID}"
  for i in {1..15}; do
    sleep 1
    if curl -fsS -m 2 "${LEGACY_URL}/api/health" >/dev/null 2>&1; then
      echo "Legacy backend ready at ${LEGACY_URL}"
      break
    fi
    if [[ $i -eq 15 ]]; then
      echo "WARNING: Legacy backend did not become healthy in 15s; server_v2 proxy will return 503 for unhandled routes."
    fi
  done
else
  echo "Legacy app_server.py already listening on ${LEGACY_PORT}"
fi

# --- Start server_v2 (FastAPI/uvicorn) on 8765 (foreground) ---
echo "Starting server_v2 at ${BASE_URL}"
exec HERMES_V2_HOST="${HOST}" HERMES_V2_PORT="${PORT}" HERMES_LEGACY_PORT="${LEGACY_PORT}" \
  "${PYTHON_EXE}" -m server_v2 --host "${HOST}" --port "${PORT}"
