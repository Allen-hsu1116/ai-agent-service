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
- Tool Registry / Tool Executor 基礎版
- `/tools` 查詢可用工具
- `/tools/{tool_name}/run` 執行受控工具並寫入 `tool_calls` log
- 範例工具：讀取文件後輸出包含 `Jimmy 到此一遊` 的新文件
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
│   ├── tools/              # Tool Registry / Executor / demo tools
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

### 已有 Docker container 的快速流程

如果你已經自己建好 container，請用這段。假設你的 container 名稱是 `ai-agent-service-dev`，先從 server 主機進入 container：

```bash
docker exec -it ai-agent-service-dev bash
```

如果 container 還沒啟動，先執行：

```bash
docker start ai-agent-service-dev
docker exec -it ai-agent-service-dev bash
```

進入 container 後，確認 Python 版本：

```bash
python3 --version || python --version
```

建議 Python 版本是 `3.11+`。如果 container 裡沒有 `git` 或 `curl`，先安裝：

```bash
apt-get update
apt-get install -y git curl
```

接著在 container 內取得專案：

```bash
mkdir -p /workspace
cd /workspace

# 如果還沒有下載 repo
git clone https://github.com/Allen-hsu1116/ai-agent-service.git
cd ai-agent-service
```

如果你的 container 已經有專案資料夾，直接切到該資料夾即可，例如：

```bash
cd /workspace/ai-agent-service
```

建立環境檔：

```bash
cp .env.server.example .env
```

如果你的模型 gateway 跑在 server 主機的 `8080`，而 container 可以連 `host.docker.internal`，保留：

```env
LLM_BASE_URL=http://host.docker.internal:8080/api/v1
```

如果你的模型 gateway 是另一個 Docker container，且兩個 container 在同一個 Docker network，請改成模型 container 名稱，例如：

```env
LLM_BASE_URL=http://model-gateway:8080/api/v1
```

如果你的 container 使用 `--network host`，請改成：

```env
LLM_BASE_URL=http://localhost:8080/api/v1
```

不要把 `/health` 放進 `LLM_BASE_URL`。

啟動服務：

```bash
bash scripts/run-in-container.sh
```

這個 script 會自動安裝 Python package、載入 `.env`，並啟動 `uvicorn`。

> 為了避免 `Permission denied`，Quick Start 預設用 `bash scripts/run-in-container.sh`，不要求 `.sh` 檔有 executable bit。如果你想用 `./scripts/run-in-container.sh`，請先執行 `chmod +x scripts/run-in-container.sh`。

> 注意：如果你希望從 server 主機用 `http://127.0.0.1:8020` 存取服務，你建立 container 時需要有 port mapping，例如 `-p 8020:8020`。如果當初沒有映射 port，可以在 container 內測 `curl http://127.0.0.1:8020/health`，或重新建立 container 加上 port mapping。

### 從零建立 Docker container 的參考流程

如果你還沒建立 container，可以在 server 主機使用：

```bash
git clone https://github.com/Allen-hsu1116/ai-agent-service.git
cd ai-agent-service

docker run -it \
  --name ai-agent-service-dev \
  -p 8020:8020 \
  --add-host=host.docker.internal:host-gateway \
  -v "$PWD:/workspace/ai-agent-service" \
  -w /workspace/ai-agent-service \
  python:3.11-slim \
  bash
```

進 container 後：

```bash
apt-get update
apt-get install -y git curl
cp .env.server.example .env
bash scripts/run-in-container.sh
```

### Native Python 快速流程

如果你不用 Docker，直接在主機跑 Python：

```bash
git clone https://github.com/Allen-hsu1116/ai-agent-service.git
cd ai-agent-service

cp .env.server.example .env
# 如果 AI Agent Service 和模型 gateway 都直接跑在主機上，把 .env 裡的 LLM_BASE_URL 改成：
# LLM_BASE_URL=http://localhost:8080/api/v1

bash scripts/run-local.sh
```

`scripts/run-local.sh` 會自動建立 `.venv`、安裝套件、載入 `.env`，再啟動服務。

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

### Phase 2 Tool Registry 範例：Jimmy 到此一遊

先查詢目前註冊的 tools：

```bash
curl http://127.0.0.1:8020/tools
```

建立一份測試文件：

```bash
mkdir -p examples/runtime
printf '這是一份測試文件。\n' > examples/runtime/source.txt
```

執行範例 tool，讀取 `source.txt` 並寫出 `visited.txt`：

```bash
curl -X POST http://127.0.0.1:8020/tools/jimmy_visit_document/run \
  -H 'Content-Type: application/json' \
  -d '{
    "arguments": {
      "input_path": "examples/runtime/source.txt",
      "output_path": "examples/runtime/visited.txt"
    }
  }'
```

檢查輸出文件：

```bash
cat examples/runtime/visited.txt
```

預期會看到：

```text
這是一份測試文件。

Jimmy 到此一遊
```

檢查 tool execution log：

```bash
curl -X POST http://127.0.0.1:8020/sql/query \
  -H 'Content-Type: application/json' \
  -d '{"query":"SELECT tool_name, status, side_effect FROM tool_calls ORDER BY id"}'
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

如果你已經有 container，先進入 container：

```bash
docker exec -it ai-agent-service-dev bash
```

Container 內執行：

```bash
mkdir -p /workspace
cd /workspace
# 如果還沒有 repo 才需要 clone
git clone https://github.com/Allen-hsu1116/ai-agent-service.git
cd ai-agent-service
cp .env.server.example .env
bash scripts/run-in-container.sh
```

如果你還沒建立 container，請看 [`docs/server-deployment.md`](docs/server-deployment.md)。

Docker Compose 快速流程：

```bash
cp .env.example .env
docker compose up -d --build
```

## Architecture Plan

完整規劃請看：[`docs/architecture.md`](docs/architecture.md)

Skills 與 prompts 管理說明請看：[`docs/skills-and-prompts.md`](docs/skills-and-prompts.md)

LLM 連線 404 / `LLM_BASE_URL` 疑難排解請看：[`docs/troubleshooting-llm-404.md`](docs/troubleshooting-llm-404.md)

Harness Engineering 課程參考筆記請看：[`docs/harness-engineering-reference.md`](docs/harness-engineering-reference.md)

目前架構流程圖與分層說明請看：[`docs/current-architecture-flow.md`](docs/current-architecture-flow.md)

LangGraph + Harness 呼叫自訂 skill 的測試程式請看：[`docs/langgraph-harness-skill-runner.md`](docs/langgraph-harness-skill-runner.md)

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
- [x] Phase 2 Tool Registry / Tool Executor foundation
- [x] Demo write-capable document tool with `tool_calls` audit log
- [ ] System prompt builder
- [ ] Skill loader / progressive skill runtime
- [ ] Tool-calling agent loop
- [ ] MCP client integration
- [ ] Background job queue
- [ ] Auth / RBAC
- [ ] Observability and admin dashboard
