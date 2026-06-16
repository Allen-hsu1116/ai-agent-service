# Getting Started

這份文件說明如何把 AI Agent Service 在本機或 Linux server 上跑起來，並確認 **LLM 呼叫**、**SQLite 資料庫**、**SQL 查詢** 都能使用。

## 1. Clone

```bash
git clone https://github.com/Allen-hsu1116/ai-agent-service.git
cd ai-agent-service
```

## 2. Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

如果要跑測試與 lint：

```bash
pip install -e '.[dev]'
```

## 3. Configure Environment

```bash
cp .env.example .env
```

編輯 `.env`：

```bash
nano .env
```

最小設定：

```env
AI_PROVIDER=openai-compatible
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4o-mini
LLM_API_KEY=your_api_key_here
LLM_TEMPERATURE=0.2
DATABASE_URL=sqlite:///./data/agent.db
```

### OpenAI-compatible Provider

目前預設使用 OpenAI-compatible `/chat/completions` API，所以可以接：

- OpenAI
- OpenRouter
- vLLM OpenAI-compatible server
- Ollama OpenAI-compatible endpoint
- LM Studio
- llama.cpp server
- 其他相容服務

只要調整：

```env
LLM_BASE_URL=https://your-provider.example.com/v1
LLM_MODEL=your-model-name
LLM_API_KEY=your_api_key
```

### SQLite Database

預設：

```env
DATABASE_URL=sqlite:///./data/agent.db
```

第一次啟動服務時會自動建立：

- `sessions`
- `messages`
- `agent_runs`

## 4. Start Server

建議使用內建 script 啟動，因為它會自動載入 `.env`：

```bash
./scripts/run-local.sh
```

如果你要手動啟動，請先把 `.env` 載入 shell，否則 Python process 讀不到環境變數：

```bash
set -a
source .env
set +a
uvicorn ai_agent_service.main:app --host 0.0.0.0 --port 8020 --reload
```

預設服務位置：

```text
http://127.0.0.1:8020
```

Swagger UI：

```text
http://127.0.0.1:8020/docs
```

## 5. Health Check

```bash
curl http://127.0.0.1:8020/health
```

預期：

```json
{"status":"ok"}
```

## 6. Call the Agent

```bash
curl -X POST http://127.0.0.1:8020/agent \
  -H 'Content-Type: application/json' \
  -d '{"message":"請用繁體中文簡短介紹 AI Agent"}'
```

回傳範例：

```json
{
  "reply": "AI Agent 是可以理解任務、呼叫工具並完成工作的智慧代理程式。",
  "model": "gpt-4o-mini",
  "session_id": 1
}
```

`session_id` 會自動建立，並存入 SQLite。

## 7. Continue a Session

第二次呼叫時帶入同一個 `session_id`：

```bash
curl -X POST http://127.0.0.1:8020/agent \
  -H 'Content-Type: application/json' \
  -d '{"session_id":1,"message":"請再講一個實際使用場景"}'
```

目前 runtime 會保存 session/message，但尚未把歷史訊息全部送進 LLM context。這部分後續可以接 `PromptBuilder` 與 conversation history。

## 8. Query Session Messages

```bash
curl http://127.0.0.1:8020/sessions/1/messages
```

回傳範例：

```json
{
  "session_id": 1,
  "messages": [
    {
      "role": "user",
      "content": "請用繁體中文簡短介紹 AI Agent"
    },
    {
      "role": "assistant",
      "content": "AI Agent 是可以理解任務、呼叫工具並完成工作的智慧代理程式。"
    }
  ]
}
```

## 9. Read-only SQL Query

可以用 `/sql/query` 查 SQLite 裡的資料。

```bash
curl -X POST http://127.0.0.1:8020/sql/query \
  -H 'Content-Type: application/json' \
  -d '{"query":"SELECT id, session_id, role, content FROM messages ORDER BY id"}'
```

回傳範例：

```json
{
  "columns": ["id", "session_id", "role", "content"],
  "rows": [
    {
      "id": 1,
      "session_id": 1,
      "role": "user",
      "content": "請用繁體中文簡短介紹 AI Agent"
    }
  ],
  "row_count": 1
}
```

目前只允許 read-only 查詢：

- `SELECT`
- `WITH`
- `PRAGMA`
- `EXPLAIN`

會拒絕：

- `INSERT`
- `UPDATE`
- `DELETE`
- `DROP`
- `ALTER`
- `CREATE`
- 多段 SQL statement

例如這個會被拒絕：

```bash
curl -X POST http://127.0.0.1:8020/sql/query \
  -H 'Content-Type: application/json' \
  -d '{"query":"DELETE FROM messages"}'
```

## 10. Docker Start

如果你已經自己建立好 Docker container，請優先用這個流程。更多細節請看：[`docs/server-deployment.md`](server-deployment.md)

Host 上進入既有 container：

```bash
docker exec -it ai-agent-service-dev bash
```

如果 container 還沒啟動：

```bash
docker start ai-agent-service-dev
docker exec -it ai-agent-service-dev bash
```

Container 內取得專案並啟動：

```bash
mkdir -p /workspace
cd /workspace

# 如果還沒有下載 repo
git clone https://github.com/Allen-hsu1116/ai-agent-service.git
cd ai-agent-service

cp .env.server.example .env
# 依你的 container 網路調整 LLM_BASE_URL：
# - 連 server 主機模型 gateway: http://host.docker.internal:8080/api/v1
# - 連同 network 的模型 container: http://model-gateway:8080/api/v1
# - host network: http://localhost:8080/api/v1

./scripts/run-in-container.sh
```

如果你的 container 已經有 repo，直接 `cd` 到專案根目錄後從 `cp .env.server.example .env` 開始。

如果你還沒建立 container，可以參考：

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

如果使用 Docker Compose：

```bash
cp .env.example .env
# edit .env first
docker compose up -d --build
```

確認：

```bash
curl http://127.0.0.1:8020/health
```

如果當初 container 沒有 `-p 8020:8020`，host 可能連不到 `127.0.0.1:8020`，請在 container 內測：

```bash
curl http://127.0.0.1:8020/health
```

更多 Docker 說明：[`docs/docker-deployment.md`](docker-deployment.md)

## 11. Run Tests

```bash
PYTHONPATH=src python -m pytest -q
PYTHONPATH=src python -m ruff check .
```

## 12. Current Scope

這個版本刻意先把範例功能拿掉，專注在可以實際使用的基礎功能：

- LLM 呼叫
- SQLite / SQLAlchemy
- 對話儲存
- read-only SQL 查詢
- Docker 啟動

後續再逐步加入：

- PromptBuilder
- conversation history injection
- tool calling
- MCP
- auth / RBAC
- background jobs
- observability
