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

mkdir -p "${DATA_DIR:-./data}"

echo "Building and starting AI Agent Service with Docker Compose"
echo "Project root: ${PROJECT_ROOT}"
docker compose up -d --build

echo "Service status:"
docker compose ps
