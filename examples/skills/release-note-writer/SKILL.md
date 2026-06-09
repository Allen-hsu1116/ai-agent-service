---
name: release-note-writer
description: "Use when turning commit messages, PR summaries, or changelogs into user-facing release notes."
version: 1.0.0
author: AI Agent Service Example
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [release-notes, changelog, writing]
    related_skills: []
---

# Release Note Writer

## Overview

把工程導向的 commit / PR / changelog 轉成使用者看得懂的 release notes。

## When to Use

- 使用者貼上 commit list 或 PR list
- 需要產出版本更新公告
- 需要把技術細節轉成產品語言

## Workflow

1. 依影響分組：`New`、`Improved`、`Fixed`、`Developer`。
2. 每個項目用使用者能理解的語言重寫。
3. 合併重複或相近的項目。
4. 技術細節只保留必要部分。
5. 如果有 breaking changes，獨立標示。

## Output Format

```markdown
# Release Notes: <version or date>

## New
- ...

## Improved
- ...

## Fixed
- ...

## Developer Notes
- ...
```

## Tone Guide

- 清楚、簡短、產品導向
- 不要列出無意義的內部 refactor
- 可以保留 API / config 名稱，但要補一句影響

## Verification Checklist

- [ ] 已去除重複項目
- [ ] 使用者能看懂
- [ ] breaking changes 有標出
- [ ] 沒有誇大尚未完成的功能
