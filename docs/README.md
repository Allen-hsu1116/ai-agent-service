# Documentation Index

這裡是 AI Agent Service 的文件入口。為避免文件越疊越多，之後請遵守：

1. **Active docs 優先更新，不新增重複版本。**
2. 如果只是歷史參考、外部講義筆記、舊部署方式，放到 `docs/archive/`。
3. 新功能文件應先判斷能否併入既有 active docs。
4. 文件要明確標示「目前已實作」與「下一階段建議」，不要混在一起。

## Active Docs

| 文件 | 內容 |
|---|---|
| [`getting-started.md`](getting-started.md) | 安裝、啟動、基本 API / Tool / Skill Runner smoke test |
| [`current-architecture-flow.md`](current-architecture-flow.md) | 目前架構流程圖、狀態管理、分層說明 |
| [`skills-and-tools.md`](skills-and-tools.md) | 如何新增自己的 Skill 與 Tool |
| [`troubleshooting-llm-404.md`](troubleshooting-llm-404.md) | LLM_BASE_URL、OpenAI-compatible endpoint、404 排查 |

## Archived Reference Docs

舊版或參考型文件放在：

```text
docs/archive/
```

目前包含：

- 舊版 architecture / deployment docs
- skills / prompts 舊版說明
- Harness Engineering 課程參考筆記
- LangGraph skill runner 早期獨立教學

之後如果 active docs 已涵蓋內容，請不要再新增平行版本；只要更新 active docs 即可。
