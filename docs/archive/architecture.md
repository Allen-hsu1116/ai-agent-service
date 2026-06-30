# AI Agent Service Architecture Plan

> **Goal:** 建立一套可擴充、可部署、可接入多種工具與 MCP Server 的 AI Agent 服務基礎架構。

## 1. High-Level Architecture

```text
Client / Channel
  ├─ Web UI
  ├─ REST API
  ├─ Discord / Telegram / Slack
  └─ Internal Webhook
        │
        ▼
API Gateway / FastAPI
        │
        ▼
Agent Runtime
  ├─ Session Manager
  ├─ Prompt Builder
  ├─ Model Router
  ├─ Tool Orchestrator
  ├─ Skill Loader
  ├─ MCP Client
  ├─ Memory Manager
  └─ Safety / Permission Layer
        │
        ├─ LLM Providers
        │   ├─ OpenAI-compatible API
        │   ├─ Anthropic
        │   ├─ Gemini
        │   └─ Local / Self-hosted Models
        │
        ├─ Tools
        │   ├─ Built-in Tools
        │   ├─ Custom Python Tools
        │   └─ MCP Tools
        │
        └─ Storage
            ├─ PostgreSQL: users, sessions, messages, runs
            ├─ Redis: queues, cache, locks, streaming state
            ├─ Object Storage: files, generated artifacts
            └─ Vector DB: retrieval memory / knowledge base
```

## 2. Recommended Repository Structure

```text
ai-agent-service/
├── docs/
│   └── architecture.md
├── src/ai_agent_service/
│   ├── api/
│   │   ├── routes_agent.py
│   │   ├── routes_health.py
│   │   ├── routes_skills.py
│   │   ├── routes_mcp.py
│   │   └── routes_admin.py
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   ├── logging.py
│   │   └── errors.py
│   ├── agent/
│   │   ├── runtime.py
│   │   ├── models.py
│   │   ├── prompt_builder.py
│   │   ├── tool_orchestrator.py
│   │   ├── loop.py
│   │   └── schemas.py
│   ├── skills/
│   │   ├── loader.py
│   │   ├── registry.py
│   │   ├── validator.py
│   │   └── storage.py
│   ├── prompts/
│   │   ├── system_prompt.py
│   │   ├── templates.py
│   │   └── policy.py
│   ├── tools/
│   │   ├── base.py
│   │   ├── registry.py
│   │   ├── builtin/
│   │   └── sandbox.py
│   ├── mcp/
│   │   ├── client.py
│   │   ├── registry.py
│   │   ├── config.py
│   │   └── schemas.py
│   ├── memory/
│   │   ├── short_term.py
│   │   ├── long_term.py
│   │   ├── vector_store.py
│   │   └── summarizer.py
│   ├── providers/
│   │   ├── base.py
│   │   ├── openai_compatible.py
│   │   ├── anthropic.py
│   │   └── local.py
│   ├── jobs/
│   │   ├── queue.py
│   │   ├── worker.py
│   │   └── scheduler.py
│   ├── db/
│   │   ├── models.py
│   │   ├── migrations/
│   │   └── session.py
│   └── main.py
├── tests/
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
└── README.md
```

## 3. Core Modules

### 3.1 API Layer

FastAPI 對外提供 HTTP 介面，初期建議至少包含：

- `POST /agent/runs`：建立一個 agent run
- `GET /agent/runs/{run_id}`：查詢 run 狀態與結果
- `POST /agent/chat`：同步或串流對話
- `GET /skills`：列出可用 skills
- `POST /skills`：新增 skill
- `GET /mcp/servers`：列出 MCP servers
- `POST /mcp/servers`：註冊 MCP server
- `GET /health`：健康檢查

### 3.2 Agent Runtime

Agent Runtime 是核心執行器，負責一次完整任務生命週期：

1. 接收 user message 與 session context。
2. 載入 system prompt、developer policy、skills、memory。
3. 呼叫 model provider。
4. 如果模型要求 tool call，交給 Tool Orchestrator 執行。
5. 把 tool result 加回 context。
6. 持續迭代直到產生 final answer 或達到上限。
7. 儲存 messages、tool calls、artifacts、metrics。

### 3.3 Prompt Builder

Prompt Builder 負責組合：

- Base system prompt
- User / workspace profile
- Safety rules
- Available tools summary
- Loaded skills
- Memory snippets
- Current task context
- MCP tool descriptions

建議設計成可測試的純函式，不要把 prompt 字串散落在各處。

### 3.4 Skill System

Skill 是可重複使用的操作手冊，建議用 `SKILL.md` 作為基本格式。

```text
skills/
└── github-pr-workflow/
    ├── SKILL.md
    ├── references/
    ├── scripts/
    └── templates/
```

Skill Loader 應支援：

- 從本機資料夾讀取 skills
- 從 GitHub / URL 匯入 skills
- 驗證 frontmatter
- 搜尋與分類
- 根據 user request 自動挑選相關 skills
- 將 skill 內容注入 prompt

建議 `SKILL.md` frontmatter：

```yaml
---
name: github-pr-workflow
description: "Use when managing GitHub PR lifecycle."
version: 1.0.0
author: Team Name
license: MIT
metadata:
  tags: [github, pr, ci]
  related_skills: [github-auth]
---
```

### 3.5 Tool System

工具分兩層：

1. **Built-in Tools**：服務內建，例如檔案、HTTP request、資料庫查詢、排程。
2. **External Tools**：透過 MCP 或 plugin 連接外部系統。

每個 tool 都應有：

- JSON Schema input
- 明確 description
- 權限等級
- timeout
- audit log
- error handling
- 是否需要 approval

範例 schema：

```json
{
  "name": "web_search",
  "description": "Search the web for fresh information.",
  "parameters": {
    "type": "object",
    "properties": {
      "query": { "type": "string" }
    },
    "required": ["query"]
  }
}
```

### 3.6 MCP Client

MCP Client 讓服務可以接入外部 MCP servers，例如 GitHub、filesystem、database、internal APIs。

建議支援兩種 transport：

- `stdio`：本機啟動 MCP server process
- `http`：連遠端 MCP server

設定範例：

```yaml
mcp_servers:
  github:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "${GITHUB_TOKEN}"
    timeout: 60

  company_api:
    url: "https://mcp.company.com/mcp"
    headers:
      Authorization: "Bearer ${COMPANY_API_TOKEN}"
    timeout: 180
```

MCP 工具命名建議：

```text
mcp_{server_name}_{tool_name}
```

例如：

- `mcp_github_list_issues`
- `mcp_filesystem_read_file`
- `mcp_company_api_query_customer`

### 3.7 Memory System

記憶建議分層：

- **Short-term memory**：目前 session 的 messages 與摘要
- **Long-term memory**：使用者偏好、常用專案、穩定事實
- **Retrieval memory**：文件、知識庫、embedding search
- **Run memory**：每次 agent run 的 tool calls、結果、錯誤

初期可以先用 PostgreSQL 儲存 session 與 messages，之後再加 vector DB。

### 3.8 Model Provider Layer

不要把 OpenAI、Anthropic、Gemini API 呼叫寫死在 runtime 裡，應該抽象成 Provider interface。

```python
class ModelProvider:
    async def complete(self, messages, tools=None, model=None, **kwargs):
        raise NotImplementedError
```

好處：

- 可切換模型
- 可支援 OpenAI-compatible endpoint
- 可做 fallback
- 可記錄 token / cost
- 可做 rate limit

### 3.9 Background Jobs

AI Agent 常常需要長任務，建議一開始就預留 job queue。

可處理：

- 長時間 agent run
- scheduled task
- webhook-triggered task
- batch processing
- retry failed tool calls

建議技術：

- MVP：FastAPI BackgroundTasks 或 asyncio task
- Production：Redis Queue / Celery / Dramatiq / Arq

### 3.10 Safety and Permissions

AI Agent 服務一定要有權限層：

- Tool allowlist / denylist
- Per-user permission
- Dangerous action approval
- Secret redaction
- Audit logs
- Rate limiting
- Prompt injection 防護
- MCP server trust level

建議把 tool 分級：

| Level | Example | Behavior |
|-------|---------|----------|
| safe | read docs, search | 可直接執行 |
| sensitive | read private DB | 需要權限 |
| destructive | delete file, send email, deploy | 需要 approval |
| external_side_effect | post message, create PR | 需要確認或 policy |

## 4. Data Model Draft

### users

- `id`
- `email`
- `display_name`
- `role`
- `created_at`

### sessions

- `id`
- `user_id`
- `title`
- `metadata`
- `created_at`
- `updated_at`

### messages

- `id`
- `session_id`
- `role`
- `content`
- `tool_calls`
- `created_at`

### agent_runs

- `id`
- `session_id`
- `status`
- `input`
- `output`
- `error`
- `started_at`
- `finished_at`

### tool_calls

- `id`
- `run_id`
- `tool_name`
- `arguments`
- `result`
- `status`
- `duration_ms`
- `created_at`

### skills

- `id`
- `name`
- `description`
- `content`
- `version`
- `tags`
- `enabled`
- `created_at`
- `updated_at`

### mcp_servers

- `id`
- `name`
- `transport`
- `config`
- `enabled`
- `last_connected_at`
- `created_at`

## 5. MVP Milestones

### Phase 1: Agent Core

- [ ] 建立 config system
- [ ] 建立 ModelProvider abstraction
- [ ] 建立 AgentRuntime loop
- [ ] 支援 basic chat endpoint
- [ ] 儲存 sessions / messages

### Phase 2: Prompt and Skills

- [ ] 建立 PromptBuilder
- [ ] 建立 `SKILL.md` validator
- [ ] 建立 SkillLoader
- [ ] 新增 `/skills` API
- [ ] 讓 agent 可載入指定 skill

### Phase 3: Tools

- [ ] 建立 Tool base class
- [ ] 建立 ToolRegistry
- [ ] 支援 JSON schema tool calling
- [ ] 加入 built-in tools
- [ ] 加入 tool audit log

### Phase 4: MCP

- [ ] 建立 MCP server config model
- [ ] 支援 stdio MCP client
- [ ] 支援 HTTP MCP client
- [ ] 將 MCP tools 註冊進 ToolRegistry
- [ ] 加入 MCP health check

### Phase 5: Production Readiness

- [ ] PostgreSQL integration
- [ ] Redis queue
- [ ] auth / API keys
- [ ] rate limiting
- [ ] structured logs
- [ ] Docker Compose
- [ ] CI pipeline

## 6. Suggested Tech Stack

| Area | Recommendation |
|------|----------------|
| API | FastAPI |
| Runtime | Python asyncio |
| Database | PostgreSQL + SQLAlchemy |
| Queue | Redis + Arq / Celery |
| Vector DB | pgvector first, Qdrant later if needed |
| Config | Pydantic Settings |
| Observability | structlog + OpenTelemetry |
| Testing | pytest + httpx |
| Container | Docker + docker-compose |
| MCP | Python MCP SDK |

## 7. Design Principles

- **Provider-agnostic**：不要綁死單一 LLM provider。
- **Tool-first architecture**：所有外部能力都透過 ToolRegistry 管理。
- **Skills are documents, not code**：skill 主要是 Agent 操作知識，工具才是可執行能力。
- **MCP is integration boundary**：公司內部 API 或第三方服務優先考慮 MCP 化。
- **Audit everything**：每次 model call、tool call、MCP call 都要可追蹤。
- **Safe by default**：危險操作預設需要 approval。
- **Small core, extensible edges**：核心 runtime 保持小，provider/tools/MCP/skills 走 plugin style。

## 8. Immediate Next Steps

1. 先把目前 placeholder `/agent` endpoint 改成 `AgentRuntime` class。
2. 新增 `core/config.py`，統一管理 provider key、database url、MCP config。
3. 新增 `providers/base.py` 與 `providers/openai_compatible.py`。
4. 新增 `prompts/system_prompt.py` 與 `agent/prompt_builder.py`。
5. 新增 `skills/loader.py`，先支援本機 `skills/<name>/SKILL.md`。
6. 新增 `tools/registry.py`，先註冊一個 dummy tool。
7. 新增 `docs/skill-format.md`，定義技能格式。
8. 新增 Docker Compose，包含 app、PostgreSQL、Redis。
