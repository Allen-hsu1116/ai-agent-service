# AI Agent Service

一套可本機啟動、可呼叫 LLM、可保存對話資料、並提供 read-only SQL 查詢的 AI Agent Service 基礎專案。

## 目前已支援

- FastAPI HTTP API
- OpenAI-compatible LLM 呼叫
- SQLite / SQLAlchemy 基礎資料庫
- 自動建立資料表
- `/agent` 對話 API
- session / message / agent run 儲存
- `/sessions/{session_id}/messages` 查詢對話紀錄
- `/sql/query` read-only SQL 查詢
- Docker / Docker Compose 啟動

## 專案結構

```text
ai-agent-service/
├── src/ai_agent_service/
│   ├── agent/              # AgentRuntime
│   ├── api/                # API schemas and SQL helper
│   ├── core/               # Settings / config
│   ├── db/                 # SQLAlchemy models, session, repository
│   ├── providers/          # LLM provider abstraction
│   ├── __init__.py
│   └── main.py             # FastAPI app and routes
├── docs/
│   ├── architecture.md
│   ├── docker-deployment.md
│   └── getting-started.md
├── tests/
├── .dockerignore
├── .env.example
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
└── README.md
```

## Quick Start

完整流程請看：[`docs/getting-started.md`](docs/getting-started.md)

```bash
git clone https://github.com/Allen-hsu1116/ai-agent-service.git
cd ai-agent-service

python -m venv .venv
source .venv/bin/activate
pip install -e .

cp .env.example .env
# 編輯 .env，填入 LLM_API_KEY

uvicorn ai_agent_service.main:app --host 0.0.0.0 --port 8020 --reload
```

健康檢查：

```bash
curl http://127.0.0.1:8020/health
```

呼叫 Agent：

```bash
curl -X POST http://127.0.0.1:8020/agent \
  -H 'Content-Type: application/json' \
  -d '{"message":"請用繁體中文簡短介紹 AI Agent"}'
```

查詢 messages：

```bash
curl http://127.0.0.1:8020/sessions/1/messages
```

Read-only SQL 查詢：

```bash
curl -X POST http://127.0.0.1:8020/sql/query \
  -H 'Content-Type: application/json' \
  -d '{"query":"SELECT id, role, content FROM messages ORDER BY id"}'
```

## Environment Variables

Copy `.env.example` to `.env` and fill in your provider key.

```bash
cp .env.example .env
```

Current default LLM mode uses an online OpenAI-compatible API:

```bash
AI_PROVIDER=openai-compatible
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4o-mini
LLM_API_KEY=your_api_key_here
LLM_TEMPERATURE=0.2
DATABASE_URL=sqlite:///./data/agent.db
```

The provider layer is intentionally flexible. Later, a local model can be introduced by either:

1. Switching `LLM_BASE_URL` to a local OpenAI-compatible endpoint such as vLLM, Ollama, LM Studio, or llama.cpp server.
2. Switching `AI_PROVIDER=local` and implementing the reserved `LocalModelProvider` adapter.

### Local model example: qwen3.5-35b

If your local model gateway exposes OpenAI-compatible chat completions under `http://localhost:8080/api/v1`, configure `.env` like this:

```bash
AI_PROVIDER=openai-compatible
LLM_BASE_URL=http://localhost:8080/api/v1
LLM_MODEL=qwen3.5-35b
LLM_API_KEY=
LLM_TEMPERATURE=0.2
DATABASE_URL=sqlite:///./data/agent.db
```

Do not include the health-check path in `LLM_BASE_URL`. For example, use `http://localhost:8080/api/v1`, not `http://localhost:8080/api/v1/health`, because the service automatically sends requests to `{LLM_BASE_URL}/chat/completions`.

Before testing `/agent`, confirm the local model service is running:

```bash
curl http://localhost:8080/api/v1/health
```

If the AI Agent service runs inside Docker while the model gateway runs on the host machine, use:

```bash
LLM_BASE_URL=http://host.docker.internal:8080/api/v1
```

## Docker Deployment

Linux Docker 實際部署流程請看：[`docs/docker-deployment.md`](docs/docker-deployment.md)

如果你是從 GitHub 下載整個資料夾到 server 執行，尤其是會自己建立 Docker container 後進 container 跑指令，建議看：[`docs/server-deployment.md`](docs/server-deployment.md)

Manual container 快速流程：

```bash
docker run -it \
  --name ai-agent-service-dev \
  -p 8020:8020 \
  --add-host=host.docker.internal:host-gateway \
  -v "$PWD:/workspace/ai-agent-service" \
  -w /workspace/ai-agent-service \
  python:3.11-slim \
  bash

apt-get update
apt-get install -y git curl
cp .env.server.example .env
./scripts/run-in-container.sh
```

Docker Compose 快速流程：

```bash
cp .env.example .env
docker compose up -d --build
```

## Architecture Plan

完整規劃請看：[`docs/architecture.md`](docs/architecture.md)

Skills 與 prompts 管理說明請看：[`docs/skills-and-prompts.md`](docs/skills-and-prompts.md)

漸進式 skills / prompts 載入策略請看：[`docs/progressive-skills-and-prompts.md`](docs/progressive-skills-and-prompts.md)

範例資料請看：[`examples/`](examples/)

## Tests

```bash
PYTHONPATH=src python -m pytest -q
PYTHONPATH=src python -m ruff check .
```

## Roadmap

- [x] Agent runtime abstraction
- [x] OpenAI-compatible provider adapter
- [x] SQLite / SQLAlchemy database foundation
- [x] Session / message persistence
- [x] Read-only SQL query endpoint
- [ ] System prompt builder
- [ ] Tool registry
- [ ] MCP client integration
- [ ] Background job queue
- [ ] Auth / RBAC
- [ ] Observability and admin dashboard
