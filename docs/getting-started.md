# Getting Started

這份文件只保留最短可用流程：啟動服務、確認 LLM、測 `/agent`、測 tool、測 skill runner。

## 1. 取得專案

### 已有 Docker container

```bash
docker exec -it ai-agent-service-dev bash
cd /workspace/ai-agent-service
git pull
```

如果 container 尚未啟動：

```bash
docker start ai-agent-service-dev
docker exec -it ai-agent-service-dev bash
cd /workspace/ai-agent-service
git pull
```

### Native Python

```bash
git clone https://github.com/Allen-hsu1116/ai-agent-service.git
cd ai-agent-service
```

## 2. 設定 `.env`

如果還沒有 `.env`：

```bash
cp .env.server.example .env
```

常見 local OpenAI-compatible gateway 設定：

```env
AI_PROVIDER=openai-compatible
LLM_BASE_URL=http://localhost:8080/v1
LLM_MODEL=Qwen3.5-35B
LLM_API_KEY=
LLM_TEMPERATURE=0.2
DATABASE_URL=sqlite:///./data/agent.db
```

注意：

- `LLM_BASE_URL` 不要包含 `/health`。
- 程式會自動呼叫 `{LLM_BASE_URL}/chat/completions`。
- 如果 AI Agent Service 在 Docker container 裡，但模型 gateway 在 host 主機上，通常要改成：

```env
LLM_BASE_URL=http://host.docker.internal:8080/v1
```

更多 404 排查看：[`troubleshooting-llm-404.md`](troubleshooting-llm-404.md)

## 3. 啟動服務

### Container 內

```bash
bash scripts/run-in-container.sh
```

### Native Python

```bash
bash scripts/run-local.sh
```

使用 `bash scripts/...` 是為了避免 `.sh` executable bit 遺失造成 `Permission denied`。

## 4. 測健康檢查

```bash
curl http://127.0.0.1:8020/health
```

預期：

```json
{"status":"ok"}
```

## 5. 測 LLM 對話 API

```bash
curl -X POST http://127.0.0.1:8020/agent \
  -H 'Content-Type: application/json' \
  -d '{"message":"請用繁體中文簡短回答：模型連線測試"}'
```

查詢對話紀錄：

```bash
curl http://127.0.0.1:8020/sessions/1/messages
```

## 6. 測 Tool Registry

查詢 tools：

```bash
curl http://127.0.0.1:8020/tools
```

建立測試文件：

```bash
mkdir -p examples/runtime
printf '這是一份測試文件。\n' > examples/runtime/source.txt
```

執行範例 tool：

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

檢查輸出：

```bash
cat examples/runtime/visited.txt
```

預期：

```text
這是一份測試文件。

Jimmy 到此一遊
```

查詢 tool log：

```bash
curl -X POST http://127.0.0.1:8020/sql/query \
  -H 'Content-Type: application/json' \
  -d '{"query":"SELECT tool_name, status, side_effect FROM tool_calls ORDER BY id"}'
```

## 7. 測 LangGraph + Skill Runner

```bash
PYTHONPATH=src python3 examples/langgraph_skill_runner.py \
  --skill examples/skills/jimmy-visit-skill/SKILL.md \
  --input examples/runtime/source.txt \
  --output examples/runtime/skill-output.txt \
  --json
```

如果只有 `python`：

```bash
PYTHONPATH=src python examples/langgraph_skill_runner.py \
  --skill examples/skills/jimmy-visit-skill/SKILL.md \
  --input examples/runtime/source.txt \
  --output examples/runtime/skill-output.txt \
  --json
```

預期重點：

```json
{
  "selected_tool": "jimmy_visit_document",
  "status": "verified",
  "steps": ["initialize", "load_skill", "execute_tool", "verify"]
}
```

## 8. 測試與 lint

```bash
PYTHONPATH=src python -m pytest -q
PYTHONPATH=src python -m ruff check .
```

## 9. 下一步：新增自己的 Skill 和 Tool

請看：[`skills-and-tools.md`](skills-and-tools.md)
