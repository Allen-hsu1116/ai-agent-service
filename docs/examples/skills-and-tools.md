# Skill and Tool Examples

這份文件提供幾個簡單範例，說明 AI Agent Service 裡的 **Skill** 和 **Tool** 可以怎麼設計與使用。

## Concepts

### Skill 是什麼？

Skill 是「給 Agent 看的操作手冊」。它通常是 Markdown 文件，描述某類任務的處理流程、輸出格式、注意事項與驗證清單。

適合放在 Skill 的內容：

- 客服分類 SOP
- Release notes 寫作規則
- Bug report 整理流程
- 內部工具使用指南
- 專案固定開發流程

Skill 通常不直接執行程式，而是影響 Agent 怎麼思考與回覆。

### Tool 是什麼？

Tool 是「Agent 可以呼叫的函式」。它有明確的名稱、描述、JSON schema 參數與 handler。

適合放在 Tool 的內容：

- 查資料庫
- 呼叫內部 API
- 寫檔案或讀檔案
- 送 Slack / Discord 訊息
- 做 deterministic 文字處理
- 觸發部署或背景任務

Tool 會真的執行程式，所以需要權限、錯誤處理與 audit log。

## Example Skills

這個 repo 已提供三個簡單範例：

```text
examples/skills/
├── bug-report-debugging/
│   └── SKILL.md
├── customer-support-triage/
│   └── SKILL.md
└── release-note-writer/
    └── SKILL.md
```

### 1. Customer Support Triage

路徑：[`examples/skills/customer-support-triage/SKILL.md`](../../examples/skills/customer-support-triage/SKILL.md)

用途：把客服訊息整理成工單摘要。

適合使用者這樣問：

```text
請幫我分類這則客服訊息，判斷優先級並整理下一步。
```

預期輸出：

```markdown
## Triage Result

- Category: login
- Priority: high
- Summary: 使用者無法登入且重設密碼信未收到。
- Known Facts:
  - 使用者已嘗試重設密碼
  - 沒有收到 email
- Missing Information:
  - 帳號 email
  - 是否檢查垃圾信箱
- Suggested Next Action:
  - 請使用者提供帳號 email，並檢查 email provider delivery log。
```

### 2. Release Note Writer

路徑：[`examples/skills/release-note-writer/SKILL.md`](../../examples/skills/release-note-writer/SKILL.md)

用途：把 commit / PR list 轉成使用者看得懂的 release notes。

適合使用者這樣問：

```text
以下是這週 merged PR，請幫我寫 release notes。
```

預期輸出：

```markdown
# Release Notes: 2026-06-04

## New
- 新增 AI provider 設定，現在可以透過環境變數切換模型。

## Improved
- 改善 Agent runtime 結構，之後更容易加入不同模型供應商。

## Fixed
- 修正空訊息時 API 回傳格式不一致的問題。
```

### 3. Bug Report Debugging

路徑：[`examples/skills/bug-report-debugging/SKILL.md`](../../examples/skills/bug-report-debugging/SKILL.md)

用途：把模糊 bug report 轉成可執行 debugging plan。

適合使用者這樣問：

```text
這是使用者回報的 bug，請幫我整理重現步驟與排查清單。
```

預期輸出：

```markdown
## Bug Summary
使用者在登入後被導回首頁，而不是原本要前往的頁面。

## Reproduction Steps
1. 開啟需要登入的受保護頁面。
2. 被導到登入頁。
3. 登入成功。
4. 觀察跳轉位置。

## Expected vs Actual
- Expected: 登入後回到原本頁面。
- Actual: 登入後回到首頁。

## Hypotheses
1. `next` query parameter 沒有被保留。
2. redirect allowlist 擋掉內部路徑。
3. 前端 router 在登入後覆蓋 redirect target。

## Debugging Checklist
- [ ] 檢查登入頁是否收到 `next` 參數
- [ ] 檢查 login API response 是否包含 redirect target
- [ ] 檢查前端登入成功 callback
```

## Skill Format Quick Start

最小可用格式：

```markdown
---
name: my-skill-name
description: "Use when handling a specific repeatable task."
version: 1.0.0
author: Your Team
license: MIT
metadata:
  hermes:
    tags: [example]
    related_skills: []
---

# My Skill Name

## Overview

這個 skill 的目的。

## When to Use

- 什麼情境使用

## Workflow

1. 第一步
2. 第二步
3. 驗證結果

## Common Pitfalls

1. 常見錯誤

## Verification Checklist

- [ ] 檢查項目
```

## Example Tools

這個 repo 也提供一組簡單文字工具：

```text
src/ai_agent_service/tools/
├── base.py
├── registry.py
└── builtin/text_tools.py
```

目前內建三個 tools：

| Tool | Purpose |
|------|---------|
| `count_words` | 計算字數、字元數、unique words |
| `slugify` | 把標題轉成 URL-friendly slug |
| `extract_keywords` | 從英文文字抽常見關鍵字 |

### Tool Definition

每個 tool 都是 `ToolDefinition`：

```python
ToolDefinition(
    name="slugify",
    description="Convert a title or label into a URL-friendly slug.",
    parameters={
        "type": "object",
        "properties": {
            "text": {"type": "string"},
            "separator": {"type": "string", "default": "-"},
        },
        "required": ["text"],
    },
    handler=slugify,
)
```

重點欄位：

- `name`：模型呼叫 tool 時使用的名稱
- `description`：讓模型知道何時使用
- `parameters`：JSON Schema，用來限制參數格式
- `handler`：實際執行的 Python function

### Usage: Python

```python
import asyncio

from ai_agent_service.tools import create_default_tool_registry

async def main():
    registry = create_default_tool_registry()

    result = await registry.call(
        "slugify",
        {"text": "Build an AI Agent Service"},
    )

    print(result.model_dump())

asyncio.run(main())
```

輸出：

```python
{
    "tool_name": "slugify",
    "success": True,
    "result": "build-an-ai-agent-service",
    "error": None,
}
```

### Usage: List Available Tools

```python
from ai_agent_service.tools import create_default_tool_registry

registry = create_default_tool_registry()
for tool in registry.list_tools():
    print(tool.name, tool.description)
```

### Usage: Call Built-in Tools

```python
result = await registry.call("count_words", {"text": "hello hello agent"})
# result.result == {"characters": 17, "words": 3, "unique_words": 2}

result = await registry.call("slugify", {"text": "Hello AI Agent!"})
# result.result == "hello-ai-agent"

result = await registry.call("extract_keywords", {"text": "Agent tools help agents call tools", "limit": 2})
# result.result == ["agent", "tools"]
```

## Adding a New Tool

1. 在 `src/ai_agent_service/tools/builtin/` 新增 function。
2. 用 `ToolDefinition` 包起來。
3. 在 `build_text_tools()` 或新的 `build_x_tools()` 中回傳。
4. 在 `create_default_tool_registry()` 註冊。
5. 新增測試。

範例：

```python
def reverse_text(text: str) -> str:
    return text[::-1]

ToolDefinition(
    name="reverse_text",
    description="Reverse the input text.",
    parameters={
        "type": "object",
        "properties": {"text": {"type": "string"}},
        "required": ["text"],
    },
    handler=reverse_text,
)
```

## Skill vs Tool: How to Choose

| Need | Use Skill | Use Tool |
|------|-----------|----------|
| 告訴 Agent 怎麼整理客服訊息 | ✅ | ❌ |
| 呼叫客服系統 API 建立工單 | ❌ | ✅ |
| 定義 release note 語氣與格式 | ✅ | ❌ |
| 從 GitHub API 抓 merged PR | ❌ | ✅ |
| 定義 debugging SOP | ✅ | ❌ |
| 執行測試、讀 log、查 DB | ❌ | ✅ |

## Recommended Pattern

複雜任務通常會同時用 Skill + Tool：

```text
User asks: 幫我整理這週 release notes

Agent loads skill: release-note-writer
Agent calls tool: github_list_merged_prs
Agent applies skill workflow to tool result
Agent returns user-facing release notes
```

也就是：

- **Tool 負責拿資料 / 做動作**
- **Skill 負責決定怎麼使用資料 / 怎麼輸出**

## Tests

執行範例工具測試：

```bash
PYTHONPATH=src python -m pytest tests/test_tools.py -q
```

執行全部測試：

```bash
PYTHONPATH=src python -m pytest -q
```
