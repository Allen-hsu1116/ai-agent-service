---
name: bug-report-debugging
description: "Use when converting a bug report into reproduction steps, hypotheses, and a debugging checklist."
version: 1.0.0
author: AI Agent Service Example
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [debugging, bug-report, qa]
    related_skills: []
---

# Bug Report Debugging

## Overview

將模糊的 bug report 轉成工程師可執行的 debugging plan。

## When to Use

- 使用者貼上 bug report、錯誤訊息或測試失敗
- 需要整理重現步驟
- 需要列出可能原因與排查順序

## Workflow

1. 摘要 bug 的實際症狀。
2. 抽出環境資訊：版本、OS、瀏覽器、帳號類型、輸入資料。
3. 寫出最小重現步驟。
4. 列出 2-4 個可能原因，依機率排序。
5. 提供 debugging checklist。

## Output Format

```markdown
## Bug Summary
<one paragraph>

## Reproduction Steps
1. ...
2. ...

## Expected vs Actual
- Expected: ...
- Actual: ...

## Hypotheses
1. ...

## Debugging Checklist
- [ ] ...
```

## Common Pitfalls

1. 不要直接跳到修法，要先確認能重現。
2. 不要忽略環境差異。
3. 如果缺少 log、版本或輸入資料，要明確列出。

## Verification Checklist

- [ ] 有重現步驟
- [ ] 有 Expected / Actual
- [ ] 有假設清單
- [ ] 有排查 checklist
