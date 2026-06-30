# Examples

這裡只保留目前會直接用到的 runnable examples。舊版或較大的參考範例已移到 `examples/archive/`，避免入口太亂。

## Active Examples

```text
examples/
├── langgraph_skill_runner.py
└── skills/
    └── jimmy-visit-skill/
        └── SKILL.md
```

### `langgraph_skill_runner.py`

用 LangGraph + Harness 流程載入 `SKILL.md`，再透過 `ToolRegistry` / `ToolExecutor` 呼叫對應 tool。

### `skills/jimmy-visit-skill/SKILL.md`

最小可測試 skill：

```yaml
tool: jimmy_visit_document
```

用途：讀取一份文字文件，輸出一份加上 `Jimmy 到此一遊` 的文件。

## Runtime Files

測試時可把暫存輸入/輸出放在：

```text
examples/runtime/
```

這個資料夾已被 `.gitignore` 忽略，不應提交。

## Archived Examples

舊範例放在：

```text
examples/archive/
```

包含早期 prompts、progressive skill 範例、server runbook 等。之後若要恢復使用，請先整理進 active docs，不要直接再新增平行版本。

## 新增自己的 Skill / Tool

請看：[`../docs/skills-and-tools.md`](../docs/skills-and-tools.md)
