#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${PROJECT_ROOT}"

if [ ! -f .env ]; then
  if [ -f .env.server.example ]; then
    cp .env.server.example .env
    echo "Created .env from .env.server.example. Please review it before production use."
  else
    cp .env.example .env
    echo "Created .env from .env.example. Please review it before production use."
  fi
fi

mkdir -p data

if [ -n "${PYTHON_BIN:-}" ]; then
  PYTHON="${PYTHON_BIN}"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON="python3"
elif command -v python >/dev/null 2>&1; then
  PYTHON="python"
else
  echo "ERROR: python3 or python is required inside this container." >&2
  exit 1
fi

"${PYTHON}" -m pip install --upgrade pip
"${PYTHON}" -m pip install -e .

set -a
# shellcheck source=/dev/null
source .env
set +a

HOST="${APP_HOST:-0.0.0.0}"
PORT="${APP_PORT:-8020}"

echo "Using Python: $(${PYTHON} --version)"
echo "Starting AI Agent Service inside container on ${HOST}:${PORT}"
echo "Project root: ${PROJECT_ROOT}"
exec "${PYTHON}" -m uvicorn ai_agent_service.main:app --host "${HOST}" --port "${PORT}"
