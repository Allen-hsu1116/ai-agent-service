---
name: jimmy-visit-skill
description: Read a text file and write a new file with the Jimmy visit marker.
tool: jimmy_visit_document
---

# Jimmy Visit Skill

這是一個最小可測試 skill，用來示範 LangGraph + Harness 如何載入 `SKILL.md`，再根據 frontmatter 的 `tool` 欄位呼叫專案內已註冊的 Tool Registry 工具。

## Inputs

- `input_path`: 要讀取的 UTF-8 文字檔。
- `output_path`: 要寫出的結果檔。

## Expected Result

輸出檔會保留原始內容，並在最後加上：

```text
Jimmy 到此一遊
```

## Harness Notes

這個 skill 不直接執行 shell command，也不直接寫 Python code。它只宣告要使用的 tool：

```yaml
tool: jimmy_visit_document
```

實際執行由 `ToolRegistry` 和 `ToolExecutor` 控制，讓 skill 本身保持 declarative，方便未來加入權限、審核、verification gates 和 observability。
