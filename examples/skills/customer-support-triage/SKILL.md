---
name: customer-support-triage
description: "Use when classifying customer support messages by urgency, category, and next action."
version: 1.0.0
author: AI Agent Service Example
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [support, triage, customer-service]
    related_skills: []
---

# Customer Support Triage

## Overview

把使用者回報的客服訊息整理成可處理的工單摘要，包含類別、緊急程度、缺少資訊與建議下一步。

## When to Use

- 使用者貼上客服信、客訴、產品問題或 bug 回報
- 需要判斷優先級與分派團隊
- 需要把非結構化訊息整理成工單

## Workflow

1. 讀完訊息，先抓出使用者真正遇到的問題。
2. 分類：`billing`、`login`、`bug`、`feature_request`、`how_to`、`other`。
3. 判斷緊急度：`low`、`medium`、`high`、`urgent`。
4. 列出已知資訊與缺少資訊。
5. 給客服人員下一步處理建議。

## Output Format

```markdown
## Triage Result

- Category: <category>
- Priority: <priority>
- Summary: <one sentence>
- Known Facts:
  - ...
- Missing Information:
  - ...
- Suggested Next Action:
  - ...
```

## Common Pitfalls

1. 不要承諾退款、賠償或 SLA，除非原始訊息明確授權。
2. 不要把不確定的推測寫成事實。
3. 如果缺少帳號、訂單號、錯誤截圖，要列為 Missing Information。

## Verification Checklist

- [ ] 有分類
- [ ] 有優先級
- [ ] 有一句話摘要
- [ ] 有下一步建議
