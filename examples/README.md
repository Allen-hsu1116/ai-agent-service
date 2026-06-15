# Examples

這個資料夾放的是 **範例資料**，供後續系統撰寫 skills 與 prompts 時參考。

目前 runtime 還不會自動載入這些檔案；它們的用途是定義風格、欄位、結構與品質標準。

## Skills Examples

```text
examples/skills/
├── local-model-connection-check/SKILL.md
├── server-container-runbook/SKILL.md
└── sqlite-readonly-inspection/SKILL.md
```

Skill 是可重複使用的操作手冊，重點是：

- 何時使用
- 前置檢查
- 操作步驟
- 常見錯誤
- 驗證方式

## Prompt Examples

```text
examples/prompts/
├── base-system.prompt.md
├── task-router.prompt.md
├── skill-writer.prompt.md
└── prompt-writer.prompt.md
```

Prompt 是模型輸入模板，重點是：

- 角色與目標
- 可用 context
- 安全規則
- 輸出格式
- 禁止事項

## Notes

- 不要把 `.env`、API key、密碼放進 examples。
- 範例可以包含 placeholder，例如 `${PROJECT_ROOT}`、`${LLM_BASE_URL}`。
- 範例應該可被 validator 檢查，不要只寫散文。
