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

if [ ! -d .venv ]; then
  python3 -m venv .venv
fi

# shellcheck source=/dev/null
source .venv/bin/activate
pip install --upgrade pip
pip install -e .

set -a
# shellcheck source=/dev/null
source .env
set +a

HOST="${APP_HOST:-0.0.0.0}"
PORT="${APP_PORT:-8020}"

echo "Starting AI Agent Service on ${HOST}:${PORT}"
echo "Project root: ${PROJECT_ROOT}"
exec uvicorn ai_agent_service.main:app --host "${HOST}" --port "${PORT}"
