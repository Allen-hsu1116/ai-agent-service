# AI Agent Service

一套準備用來架設 AI Agent 服務的公開專案骨架。

## 目標

- 提供可擴充的 AI Agent API 服務
- 支援工具調用、任務執行、記憶與排程等能力
- 可用 Docker 部署
- 後續可接入 Discord、Telegram、Web UI 或企業內部系統

## 初始架構

```text
ai-agent-service/
├── src/ai_agent_service/
│   ├── __init__.py
│   └── main.py
├── .env.example
├── .gitignore
├── Dockerfile
├── pyproject.toml
└── README.md
```

## Local Development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
uvicorn ai_agent_service.main:app --reload
```

Open: http://127.0.0.1:8000/health

## Environment Variables

Copy `.env.example` to `.env` and fill in your provider key.

```bash
cp .env.example .env
```

## Architecture Plan

完整規劃請看：[`docs/architecture.md`](docs/architecture.md)

架構會逐步支援：

- Agent Runtime
- System Prompt Builder
- Skill Loader / Skill Registry
- Tool Registry
- MCP Client / MCP Server 管理
- Memory / Session Storage
- Model Provider Abstraction
- Background Jobs
- Safety / Permission Layer

## Roadmap

- [ ] Agent runtime abstraction
- [ ] System prompt builder
- [ ] Skill loader and skill registry
- [ ] Tool registry
- [ ] MCP client integration
- [ ] Conversation/session storage
- [ ] Provider adapters
- [ ] Background job queue
- [ ] Messaging platform integrations
- [ ] Observability and admin dashboard
