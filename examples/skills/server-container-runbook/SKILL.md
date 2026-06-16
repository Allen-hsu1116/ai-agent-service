---
name: server-container-runbook
description: "Use when deploying AI Agent Service by creating a Docker container manually and running commands inside it."
version: 1.0.0
author: AI Agent Service Team
license: MIT
metadata:
  tags: [docker, server, deployment, manual-container]
  related_skills: [local-model-connection-check]
---

# Server Container Runbook

## When to Use

Use this skill when the operator wants to:

- Download the repo from GitHub onto a server.
- Create their own Docker container.
- Enter the container and run commands manually.
- Keep project files and SQLite data on the server host.

## Assumptions

- The server has Docker installed.
- The repo exists on the server host.
- The operator is in the project root when creating the container.
- The model gateway runs on the server host at port `8080`.

## Recommended Container Creation

```bash
docker run -it \
  --name ai-agent-service-dev \
  -p 8020:8020 \
  --add-host=host.docker.internal:host-gateway \
  -v "$PWD:/workspace/ai-agent-service" \
  -w /workspace/ai-agent-service \
  python:3.11-slim \
  bash
```

## Inside Container Setup

```bash
apt-get update
apt-get install -y git curl
cp .env.server.example .env
bash scripts/run-in-container.sh
```

## Important Environment Values

For manual Docker container connecting to a model gateway on the host:

```env
LLM_BASE_URL=http://host.docker.internal:8080/api/v1
DATABASE_URL=sqlite:///./data/agent.db
```

For host network mode:

```env
LLM_BASE_URL=http://localhost:8080/api/v1
```

## Data Persistence

Prefer mounting the repo into the container:

```bash
-v "$PWD:/workspace/ai-agent-service"
```

Then SQLite data stays on the host at:

```text
./data/agent.db
```

## Start Service

```bash
bash scripts/run-in-container.sh
```

Manual equivalent:

```bash
mkdir -p data
python -m pip install --upgrade pip
python -m pip install -e .
set -a
source .env
set +a
python -m uvicorn ai_agent_service.main:app --host 0.0.0.0 --port 8020
```

## Smoke Tests from Host

```bash
curl http://127.0.0.1:8020/health
```

```bash
curl -X POST http://127.0.0.1:8020/agent \
  -H 'Content-Type: application/json' \
  -d '{"message":"請用繁體中文簡短回答：服務測試"}'
```

## Restart Existing Container

```bash
docker start ai-agent-service-dev
docker exec -it ai-agent-service-dev bash
cd /workspace/ai-agent-service
bash scripts/run-in-container.sh
```

## Background Run Option

```bash
nohup bash scripts/run-in-container.sh > app.log 2>&1 &
tail -f app.log
```

## Verification Checklist

- [ ] Container has repo mounted or cloned.
- [ ] `.env` exists.
- [ ] `LLM_BASE_URL` matches the network mode.
- [ ] `data/` exists.
- [ ] Service listens on `0.0.0.0:8020` inside container.
- [ ] Host can reach `http://127.0.0.1:8020/health`.
