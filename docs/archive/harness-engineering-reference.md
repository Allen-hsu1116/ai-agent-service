# Harness Engineering 參考講義筆記

來源：<https://walkinglabs.github.io/learn-harness-engineering/zh-TW/>

這份文件記錄後續改善本專案時，可以參考的 Harness Engineering 課程重點。它不是目前已完成的功能清單，而是後續 roadmap / architecture review 時可回頭查的外部參考。

## 這份講義的核心觀點

Learn Harness Engineering 把 agent 可靠性問題視為「模型之外的工作系統設計」問題。重點不是單純換更強模型，而是為 agent 建立：

- 明確目標與規則
- 可初始化的工作環境
- 可持久化的狀態
- 可驗證的完成條件
- 可觀測的執行過程
- 可交接的 session 結束狀態

講義首頁用一個閉環流程描述 harness：

```text
明確目標 / AGENTS.md
→ 初始化檢查 / init.sh
→ Agent 執行任務
→ CLI / Logs 回饋
→ Test & QA 驗證
→ 清理與交接
```

這和本專案目前方向一致：我們已先做出可執行的 API、LLM provider、SQLite logs、read-only SQL、Tool Registry / Tool Executor，下一步應該逐步補上「狀態、驗證、控制、可觀測性」。

## 課程章節與可借鑑方向

### 第一講：模型能力強，不等於執行可靠

連結：<https://walkinglabs.github.io/learn-harness-engineering/zh-TW/lectures/lecture-01-why-capable-agents-still-fail/>

可借鑑方向：

- 不把 agent 失敗簡化成「模型不夠強」。
- 專案設計要把失敗原因拆成 context、state、tool、verification、handoff 等系統面問題。
- `/agent` 未來不應只回傳 reply，還應能回傳 run state / steps / verification result。

### 第二講：Harness 到底是什麼

連結：<https://walkinglabs.github.io/learn-harness-engineering/zh-TW/lectures/lecture-02-what-a-harness-actually-is/>

可借鑑方向：

- 把本專案定位成 Agent Harness / Agent Runtime，而不只是 LLM proxy。
- 將系統拆成多個子系統：環境、狀態、工具、驗證、控制。
- Tool Registry、Tool Executor、DB logs 是 harness 的一部分，不是附屬 demo。

### 第三講：讓程式碼儲存庫成為唯一的事實來源

連結：<https://walkinglabs.github.io/learn-harness-engineering/zh-TW/lectures/lecture-03-why-the-repository-must-become-the-system-of-record/>

可借鑑方向：

- 專案規則、架構、部署方式、工具格式要寫進 repo，而不是只存在聊天紀錄。
- 目前已開始把 Quick Start、troubleshooting、skills/prompts、phase 2 tool demo 寫進 `docs/`，後續應延續這個方式。
- 可考慮新增：`docs/architecture-decisions/`、`docs/runbooks/`、`docs/verification/`。

### 第四講：把指令拆分到不同檔案裡

連結：<https://walkinglabs.github.io/learn-harness-engineering/zh-TW/lectures/lecture-04-why-one-giant-instruction-file-fails/>

可借鑑方向：

- 避免把所有 agent prompt / rules 都塞進一個巨大 system prompt。
- 本專案後續的 `SkillLoader` / `PromptBuilder` 應採用分層與按需載入。
- 可以沿用目前 `docs/progressive-skills-and-prompts.md` 的方向：核心 prompt 小，細節由 references/templates 補充。

### 第五講：讓跨工作階段的任務保持脈絡連續

連結：<https://walkinglabs.github.io/learn-harness-engineering/zh-TW/lectures/lecture-05-why-long-running-tasks-lose-continuity/>

可借鑑方向：

- 目前 DB 已保存 messages 與 agent_runs，但還沒有完整 session handoff。
- 後續可加入 `session_summaries` 或 `run_handoffs` 資料表。
- 長任務不應只靠聊天紀錄，要有明確的 current state、next action、blocked reason。

### 第六講：讓 agent 每次工作前先初始化

連結：<https://walkinglabs.github.io/learn-harness-engineering/zh-TW/lectures/lecture-06-why-initialization-needs-its-own-phase/>

可借鑑方向：

- 每次 agent run 前應先做 initialization：讀 config、檢查 tools、檢查工作目錄、檢查權限、載入 relevant context。
- 可以新增 `RunInitializer`，把現在散落在 runtime / API 的前置檢查獨立出來。
- `/agent` 可以回傳初始化摘要，或寫入 `agent_runs.initialization_json`。

### 第七講：給 agent 劃清每次任務的邊界

連結：<https://walkinglabs.github.io/learn-harness-engineering/zh-TW/lectures/lecture-07-why-agents-overreach-and-under-finish/>

可借鑑方向：

- 建立 WIP=1 的任務模式：一次 run 只處理一個明確任務。
- 在 API schema 中增加 task boundary，例如 `goal`、`constraints`、`allowed_tools`、`done_criteria`。
- 避免 agent 同時做太多「順便」修改。

### 第八講：用功能清單約束 agent 該做什麼

連結：<https://walkinglabs.github.io/learn-harness-engineering/zh-TW/lectures/lecture-08-why-feature-lists-are-harness-primitives/>

可借鑑方向：

- 將 feature list 視為 agent harness primitive。
- 可在本專案新增 features/tasks 的狀態模型：`pending`、`in_progress`、`implemented`、`verified`、`blocked`。
- 完成條件要由 harness 狀態轉移控制，而不是由模型口頭宣告。

### 第九講：防止 agent 提前宣告完成

連結：<https://walkinglabs.github.io/learn-harness-engineering/zh-TW/lectures/lecture-09-why-agents-declare-victory-too-early/>

可借鑑方向：

- `/agent` 後續應支援 verification gates。
- 工具執行完成不等於任務完成，還需要測試、lint、smoke test、文件更新等 gate。
- `agent_runs.status` 不應只有 completed/error，應區分 `implemented`、`verified`、`needs_review` 等狀態。

### 第十講：跑通完整流程才算真正驗證

連結：<https://walkinglabs.github.io/learn-harness-engineering/zh-TW/lectures/lecture-10-why-end-to-end-testing-changes-results/>

可借鑑方向：

- 目前本專案已有 pytest / ruff / smoke test 習慣，後續應把這些變成 first-class verification tools。
- 增加 `/verification/run` 或內部 `Verifier`，支援針對任務執行測試命令。
- E2E 不只是測結果，也會改變 agent 的行為，因為 agent 知道最後要過完整 gate。

### 第十一講：讓 agent 的執行過程可觀測

連結：<https://walkinglabs.github.io/learn-harness-engineering/zh-TW/lectures/lecture-11-why-observability-belongs-inside-the-harness/>

可借鑑方向：

- 現在已有 `agent_runs` 與 `tool_calls`，後續可加 `agent_steps`、`observations`、`verification_results`。
- API 應能查每次 run 的 timeline，而不是只查 messages。
- Tool call logs 需要保留 input/output/error/side_effect，這與目前 Phase 2 設計一致。

### 第十二講：每次工作階段結束前都做好交接

連結：<https://walkinglabs.github.io/learn-harness-engineering/zh-TW/lectures/lecture-12-why-every-session-must-leave-a-clean-state/>

可借鑑方向：

- 每次 run 結束前應留下 clean handoff。
- 可新增 `handoff_summary`：做了什麼、還沒做什麼、如何驗證、下一步是什麼。
- 對長任務與公司內部多人接手很重要。

## 對本專案 roadmap 的建議映射

### 已完成或正在成形

- FastAPI service foundation
- OpenAI-compatible provider
- SQLite persistence
- read-only SQL inspection
- Tool Registry / Tool Executor
- `tool_calls` audit log
- user-facing docs / troubleshooting runbooks

### 建議下一批改善

1. **Run Initialization**
   - 新增 `RunInitializer`
   - 檢查設定、工具、資料庫、工作目錄、模型連線
   - 將初始化結果寫入 DB

2. **Agent Steps / Timeline**
   - 新增 `agent_steps` table
   - 紀錄 thought/action/observation/tool_result/verification_result 等執行節點
   - 提供 `GET /runs/{run_id}` 查完整 timeline

3. **Verification Gates**
   - 新增 verification tool 或 internal verifier
   - 支援 pytest、ruff、smoke test、curl endpoint checks
   - 完成狀態必須基於 gate result

4. **Task Boundary Schema**
   - 在 `/agent` request 補充 `goal`、`constraints`、`allowed_tools`、`done_criteria`
   - 避免 agent overreach / under-finish

5. **Session Handoff / Continuity**
   - 新增 run handoff summary
   - 每次任務結束保存 current state、next step、blocked reason
   - 支援跨工作階段恢復

6. **Repository as System of Record**
   - 將架構決策、runbook、troubleshooting、feature list 都保存到 repo
   - 減少只存在聊天紀錄裡的知識

## 使用這份講義時的原則

- 先把本專案做成可靠的 runnable harness，再逐步加入複雜 agent 能力。
- 每次引入新 harness 概念，都要配套：資料模型、API、測試、文件、操作範例。
- 不要只把講義內容變成抽象文件；要落到可執行功能，例如 run initializer、verification gate、timeline log。
- 任何會影響 agent 行為的規則，應該進 repo 或 DB，而不是只存在一次性 prompt。

## 相關外部資料

講義首頁列出的參考來源：

- OpenAI: Harness engineering: leveraging Codex in an agent-first world
- Anthropic: Effective harnesses for long-running agents
- Anthropic: Harness design for long-running application development
- Awesome Harness Engineering

後續如果要做較完整的架構規劃，可以再逐一閱讀這些來源並轉成專案 issue / milestone。
