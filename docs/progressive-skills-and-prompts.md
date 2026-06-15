# Progressive Skills and Prompts

這份文件定義一種 **漸進式載入** 的 skills / prompts 管理方式。目標是像書一樣管理知識：先讀目錄，只有在任務需要時才載入正文章節或附錄，以減少 token 使用量。

## 1. Why Progressive Loading

傳統 skill 寫法常把所有內容塞進單一 `SKILL.md`：

```text
SKILL.md = 使用時機 + 步驟 + 範例 + 疑難排解 + 模板 + 長篇背景
```

缺點：

- 每次載入都吃掉大量 token。
- 任務只需要其中一小段時，也會載入全部內容。
- 常見流程、罕見疑難排解、模板範例混在一起，不容易管理。

漸進式寫法把 skill 拆成：

```text
SKILL.md = 書的封面 + 目錄 + 最小必要操作規則
references/*.md = 正文章節，按需求載入
templates/* = 輸出模板，只有要產出該格式才載入
scripts/* = 輔助腳本，只有要執行時才使用
appendix/* = 低頻、長篇、背景知識或疑難排解
```

## 2. Recommended Layout

```text
skills/
└── api-data-analysis-pipeline/
    ├── SKILL.md
    ├── references/
    │   ├── 01-api-retrieval.md
    │   ├── 02-validation-cleaning.md
    │   ├── 03-analysis-methods.md
    │   └── 04-reporting-audit.md
    ├── templates/
    │   ├── request-plan.json
    │   └── analysis-report.md
    └── appendix/
        └── statistical-notes.md
```

## 3. SKILL.md as Table of Contents

`SKILL.md` 應該短，通常控制在可以快速載入的大小。它負責：

- 判斷是否適用。
- 說明最小流程。
- 列出章節目錄。
- 說明何時載入哪個章節。
- 給出 context budget 規則。

它不應該包含全部長篇細節。

## 4. Module Loading Policy

建議 SkillLoader / PromptBuilder 使用這個順序：

1. **Discovery:** 只讀每個 skill 的 frontmatter 與 `SKILL.md` 摘要。
2. **Selection:** 根據 user request 選定 1 到 3 個最相關 skills。
3. **Planning:** 從 `SKILL.md` 的目錄決定要載入哪些 modules。
4. **Focused Loading:** 只載入必要的 `references/` 或 `templates/`。
5. **Appendix on demand:** 只有遇到錯誤、特殊需求或使用者要求深入說明時，才載入 `appendix/`。
6. **Audit:** 記錄本次載入了哪些 skill 與 module。

## 5. Module Metadata Convention

在 `SKILL.md` 裡可以用這種格式描述 module：

```markdown
## Module Index

| Module | Load When | Token Cost | Purpose |
|--------|-----------|------------|---------|
| `references/01-api-retrieval.md` | Need API request, auth, pagination | medium | Fetch data safely |
| `references/02-validation-cleaning.md` | Data schema or cleaning is needed | medium | Validate and normalize rows |
| `references/03-analysis-methods.md` | Need statistics / trend / anomaly analysis | high | Choose analysis method |
| `templates/analysis-report.md` | Need final Markdown report | low | Output template |
```

如果目標平台不適合 markdown table，也可以用 bullets：

```markdown
- `references/01-api-retrieval.md`
  - Load when: API request, auth, pagination.
  - Token cost: medium.
  - Purpose: Fetch data safely.
```

## 6. Prompt Strategy

Prompt 也可以漸進式管理：

```text
prompts/
├── api-data-analysis.prompt.md              # prompt 目錄與核心規則
├── modules/
│   ├── api-request-planning.prompt.md       # API request 規劃
│   ├── data-quality-check.prompt.md         # 資料品質檢查
│   └── final-report.prompt.md               # 報告輸出格式
└── appendix/
    └── json-output-schema.prompt.md         # 只有需要 JSON 才載入
```

PromptBuilder 應先載入核心 prompt，再依照任務需要追加 prompt modules。

## 7. Example Decision Flow

User request:

```text
請透過訂單 API 抓最近 30 天資料，分析營收趨勢與異常日期，最後給我 Markdown 報告。
```

Progressive loading decision:

```json
{
  "selected_skill": "api-data-analysis-pipeline",
  "loaded_modules": [
    "references/01-api-retrieval.md",
    "references/02-validation-cleaning.md",
    "references/03-analysis-methods.md",
    "references/04-reporting-audit.md",
    "templates/analysis-report.md"
  ],
  "skipped_modules": [
    "appendix/statistical-notes.md"
  ],
  "reason": "The task requires API retrieval, data validation, trend/anomaly analysis, and Markdown report output. No deep statistical appendix is needed yet."
}
```

## 8. Quality Rules

- Keep `SKILL.md` short and navigational.
- Put long explanations in `references/` or `appendix/`.
- Put output formats in `templates/`.
- Use clear load conditions for every module.
- Avoid secrets in all skill and prompt files.
- Design module names to be stable because prompts may reference them.
- Prefer deterministic file paths over vague section names.

## 9. Current Examples

Progressive example skill:

```text
examples/skills/api-data-analysis-pipeline/
```

Progressive prompt examples:

```text
examples/prompts/api-data-analysis.prompt.md
examples/prompts/progressive-skill-loader.prompt.md
```
