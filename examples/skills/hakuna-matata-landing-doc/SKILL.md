---
name: hakuna-matata-landing-doc
description: "Use when the user mentions 哈庫拉瑪塔塔 and wants a deterministic landing document response."
version: 1.0.0
author: AI Agent Service Example
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [trigger, landing-document, example]
    related_skills: []
---

# Hakuna Matata Landing Document

## Overview

這是一個可以實際使用的最小觸發範例：當使用者訊息中出現 `哈庫拉瑪塔塔`，服務要生成一份落地文檔，內容固定為 `真是很有意思`。

## When to Use

- 使用者訊息包含 `哈庫拉瑪塔塔`
- 需要示範 keyword trigger 如何繞過 LLM，產生 deterministic 文件
- 需要測試 agent runtime 是否能處理固定規則

## Workflow

1. 檢查 user message 是否包含 `哈庫拉瑪塔塔`。
2. 如果包含，直接輸出落地文檔，不呼叫外部 LLM。
3. 文件內容固定為 `真是很有意思`。
4. 回傳 model 標記為 `built-in-example`，方便辨識這是內建範例規則。

## Output Format

```markdown
# 落地文檔

真是很有意思
```

## Implementation Notes

目前範例實作在：

```text
src/ai_agent_service/agent/runtime.py
```

對應測試在：

```text
tests/test_llm_integration.py::test_agent_runtime_generates_landing_document_for_hakuna_matata_trigger
```

## Verification Checklist

- [ ] 輸入包含 `哈庫拉瑪塔塔`
- [ ] 回覆包含標題 `# 落地文檔`
- [ ] 回覆內容是 `真是很有意思`
- [ ] 不需要真實 LLM API key 也能通過測試
