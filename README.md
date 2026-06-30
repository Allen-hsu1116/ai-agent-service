# AI Agent Service

一個漸進式 AI Agent Harness / Runtime 基礎專案。目標不是一次塞滿所有功能，而是先把可執行、可驗證、可追蹤的核心鏈路做好，再逐步加入自己的 Skills、Tools、Planner 與 Verification Gates。

## 目前可用功能

- FastAPI service：`/health`、`/agent`
- OpenAI-compatible LLM provider：呼叫 `{LLM_BASE_URL}/chat/completions`
- SQLite persistence：`sessions`、`messages`、`agent_runs`、`tool_calls`
- Read-only SQL inspection：`/sql/query`
- Tool Registry / Tool Executor：`/tools`、`/tools/{tool_name}/run`
- LangGraph + Harness skill runner CLI：`examples/langgraph_skill_runner.py`
- 範例 skill/tool：讀取文件並寫入 `Jimmy 到此一遊`

## 快速開始

完整步驟請看：[`docs/getting-started.md`](docs/getting-started.md)

### 既有 Docker container

```bash
docker exec -it ai-agent-service-dev bash
cd /workspace/ai-agent-service
git pull
cp .env.server.example .env  # 如果已經有 .env 可跳過
bash scripts/run-in-container.sh
```

### Native Python

```bash
git clone https://github.com/Allen-hsu1116/ai-agent-service.git
cd ai-agent-service
cp .env.server.example .env
bash scripts/run-local.sh
```

### 基本檢查

```bash
curl http://127.0.0.1:8020/health
curl http://127.0.0.1:8020/tools
```

## 文件入口

為避免文件無限制堆疊，之後請優先維護下面幾份 active docs：

| 文件 | 用途 |
|---|---|
| [`docs/README.md`](docs/README.md) | 文件索引與維護規則 |
| [`docs/getting-started.md`](docs/getting-started.md) | 安裝、啟動、基本測試 |
| [`docs/current-architecture-flow.md`](docs/current-architecture-flow.md) | 目前架構與流程圖 |
| [`docs/skills-and-tools.md`](docs/skills-and-tools.md) | 下一階段：新增自己的 Skill 與 Tool 教學 |
| [`docs/troubleshooting-llm-404.md`](docs/troubleshooting-llm-404.md) | LLM_BASE_URL / 404 疑難排解 |

舊版或參考型文件已移到：[`docs/archive/`](docs/archive/)

## 專案結構

```text
ai-agent-service/
├── src/ai_agent_service/
│   ├── agent/              # AgentRuntime
│   ├── api/                # request/response schemas and SQL helper
│   ├── core/               # env settings
│   ├── db/                 # SQLAlchemy models, session, repository
│   ├── harness/            # LangGraph skill workflow
│   ├── providers/          # LLM provider abstraction
│   ├── tools/              # Tool Registry / Executor / handlers
│   └── main.py             # FastAPI routes
├── docs/                   # active docs + archive
├── examples/               # runnable examples + archive
├── scripts/                # local/container startup scripts
└── tests/
```

## 測試

```bash
PYTHONPATH=src python -m pytest -q
PYTHONPATH=src python -m ruff check .
```

## Roadmap

已完成：

- [x] Agent runtime abstraction
- [x] OpenAI-compatible provider adapter
- [x] SQLite / SQLAlchemy database foundation
- [x] Session / message / agent run persistence
- [x] Read-only SQL query endpoint
- [x] Tool Registry / Tool Executor foundation
- [x] Demo write-capable document tool with `tool_calls` audit log
- [x] LangGraph + Harness skill runner CLI

下一階段：

- [ ] 新增自訂 Skill / Tool 的正式流程與範例
- [ ] `POST /skills/run`
- [ ] `agent_steps` / `run_steps` persistence
- [ ] Tool calls 關聯到 run id
- [ ] Verification gates
- [ ] LLM planner / tool-calling loop
