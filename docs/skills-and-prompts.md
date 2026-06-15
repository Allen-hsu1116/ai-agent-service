# Skills and Prompts Management

這份文件說明目前專案對 **skills** 與 **prompts** 的管理方式、尚未實作的部分，以及後續系統可以參考的範例格式。

## 1. Current Status

目前專案已完成的是 AI Agent Service 的基礎能力：

- `/agent` endpoint
- OpenAI-compatible model provider
- SQLite / SQLAlchemy persistence
- sessions / messages / agent_runs 儲存
- read-only SQL query endpoint
- Docker / server deployment 文件

目前尚未正式實作：

- `PromptBuilder`
- `SkillLoader`
- `SKILL.md` validator
- `/skills` API
- 自動挑選 skills
- 將 loaded skills 注入 model prompt

也就是說，現在的 `AgentRuntime` 還是最小版：它只把 user message 包成 chat message 後送到 model provider。

目前 runtime 邏輯概念如下：

```text
user message
  -> AgentRuntime.run(message)
  -> ChatRequest(messages=[{"role":"user", "content": message}])
  -> ModelProvider.chat(...)
  -> response
```

未來要加入 skills / prompts 時，建議改成：

```text
user message
  -> load session context
  -> select relevant skills
  -> build prompt messages
  -> ModelProvider.chat(messages=[system, developer, skill context, history, user])
  -> response
  -> persist messages / run metadata
```

## 2. Skills Management

### 2.1 Skill 的定位

Skill 是「可重複使用的操作手冊」，不是直接執行的工具程式。

Skill 應該回答：

- 什麼情境要使用這個 skill？
- 使用前要檢查什麼？
- 正確步驟是什麼？
- 常見錯誤與排查方式是什麼？
- 完成後如何驗證？

Skill 不應該保存：

- API key
- 密碼
- 一次性任務進度
- 很快會過期的 commit hash / PR number / issue number
- 大量原始資料

### 2.2 建議檔案結構

未來正式的 skill library 可以長這樣：

```text
skills/
└── local-model-connection-check/
    ├── SKILL.md
    ├── references/
    │   └── network-routing.md
    ├── scripts/
    │   └── smoke_test.sh
    └── templates/
        └── env.local-model.template
```

本 repo 目前先提供範例在：

```text
examples/skills/
```

這些範例不是 runtime 自動載入的 production skills，而是後續系統撰寫 / 驗證 skills 時可以參考的格式。

### 2.3 SKILL.md 建議格式

```markdown
---
name: local-model-connection-check
description: "Use when diagnosing connectivity between AI Agent Service and a local OpenAI-compatible model gateway."
version: 1.0.0
author: AI Agent Service Team
license: MIT
metadata:
  tags: [local-model, openai-compatible, docker, networking]
  related_skills: [server-deployment]
---

# Local Model Connection Check

## When to Use

- User reports `/agent` returns 500.
- Model health endpoint works on host but not from container.
- `LLM_BASE_URL` may include `/health` by mistake.

## Steps

1. Check service health.
2. Check model health from host.
3. Check model health from container.
4. Verify `LLM_BASE_URL`.
5. Run `/agent` smoke test.

## Verification

- `/health` returns `{"status":"ok"}`.
- `/agent` returns a model response.
```

### 2.4 Skill Loader 建議行為

未來 `SkillLoader` 建議支援：

1. 掃描 `skills/*/SKILL.md`。
2. 解析 YAML frontmatter。
3. 驗證必填欄位：`name`, `description`, `version`。
4. 建立 skill registry。
5. 根據 user request、tags、description 選出候選 skills。
6. 將選中的 skill 內容摘要或全文交給 PromptBuilder。
7. 記錄本次 run 載入了哪些 skills，方便 audit。

### 2.5 Skill 選取規則建議

最小可行版本可以先用 keyword / tag matching：

```text
user request: "container 連不到地端模型"
matched tags: docker, local-model, networking
selected skill: local-model-connection-check
```

之後可以升級成 embedding search 或 LLM router。

## 3. Prompts Management

### 3.1 Prompt 的定位

Prompt 是 runtime 實際送給模型的訊息模板與組裝規則。

Prompt 應該集中管理，不要散落在 endpoint 或 provider 裡。

建議未來結構：

```text
src/ai_agent_service/prompts/
├── __init__.py
├── system_prompt.py
├── templates.py
└── policy.py

src/ai_agent_service/agent/
└── prompt_builder.py
```

本 repo 目前先提供範例在：

```text
examples/prompts/
```

### 3.2 Prompt Builder 建議輸入

PromptBuilder 建議接收明確的 context object，而不是到處讀 global state。

```python
class PromptBuildContext(BaseModel):
    user_message: str
    session_messages: list[ChatMessage] = []
    loaded_skills: list[Skill] = []
    tool_summaries: list[ToolSummary] = []
    memory_snippets: list[str] = []
    workspace_profile: str | None = None
```

### 3.3 Prompt Builder 建議輸出

輸出應該是 provider-agnostic chat messages：

```python
messages = [
    {"role": "system", "content": base_system_prompt},
    {"role": "system", "content": safety_policy},
    {"role": "system", "content": loaded_skills_context},
    {"role": "user", "content": user_message},
]
```

### 3.4 Prompt 分層建議

建議分成以下層：

1. **Base system prompt**：Agent 身分、核心行為準則。
2. **Safety / policy prompt**：安全限制、資料隱私、危險操作確認。
3. **Workspace prompt**：目前專案、部署方式、環境資訊。
4. **Skill context**：本次任務相關 skill 的操作步驟。
5. **Tool summary**：可用工具及限制。
6. **Conversation context**：必要的歷史對話摘要。
7. **Current user message**：使用者本次需求。

### 3.5 Prompt 範例原則

好的 prompt 範例應該：

- 明確描述角色與任務。
- 用條列規則，不要寫成長篇散文。
- 區分「必須遵守」與「建議」。
- 明確指定輸出格式。
- 標明哪些資料是可信 context，哪些是 user input。
- 避免把 secret 或環境專屬絕對路徑寫死。

## 4. Example Files

本 repo 已提供以下範例：

```text
examples/
├── README.md
├── skills/
│   ├── local-model-connection-check/SKILL.md
│   ├── server-container-runbook/SKILL.md
│   └── sqlite-readonly-inspection/SKILL.md
└── prompts/
    ├── base-system.prompt.md
    ├── task-router.prompt.md
    ├── skill-writer.prompt.md
    └── prompt-writer.prompt.md
```

## 5. Suggested Next Implementation Steps

1. 建立 `src/ai_agent_service/skills/loader.py`。
2. 建立 `src/ai_agent_service/skills/schemas.py`。
3. 建立 `src/ai_agent_service/skills/validator.py`。
4. 建立 `src/ai_agent_service/prompts/templates.py`。
5. 建立 `src/ai_agent_service/agent/prompt_builder.py`。
6. 新增 tests 驗證：
   - skill frontmatter parse
   - invalid skill rejection
   - prompt builder output order
   - loaded skill 被注入 messages
7. 將 `/agent` 從直接送 user message 改成透過 PromptBuilder 組 messages。
