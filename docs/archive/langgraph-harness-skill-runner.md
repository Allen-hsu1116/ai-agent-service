# LangGraph + Harness Skill Runner

這份文件說明本專案新增的最小可測試範例：用 **LangGraph** 建立一個小型 Harness workflow，載入你自己的 `SKILL.md`，再透過專案內的 `ToolRegistry` / `ToolExecutor` 呼叫對應 tool。

> 使用者原本寫成 `LengGraph`，這裡採用正式套件名稱 **LangGraph**。

## 1. 設計概念：LangGraph 與 Harness 怎麼分工？

### LangGraph 負責流程控制

LangGraph 適合把 agent runtime 拆成明確節點，例如：

```text
initialize → load_skill → execute_tool → verify
```

每個節點都讀寫同一份 state，最後輸出完整執行結果。

### Harness 負責可靠性邊界

Harness Engineering 的重點不是讓模型自己「說它做完了」，而是把執行環境、狀態、工具、驗證與交接做成可控系統。

在這個範例裡：

| Harness 階段 | 對應 LangGraph node | 做什麼 |
|---|---|---|
| 初始化 | `initialize` | 檢查 skill 檔案存在 |
| 載入規則 | `load_skill` | 讀取 `SKILL.md` frontmatter，取得要呼叫的 tool |
| 受控執行 | `execute_tool` | 透過 `ToolExecutor` 執行 Tool Registry 裡的 tool |
| 驗證 | `verify` | 檢查輸出檔是否存在，並確認 marker 有寫入 |

目前這個範例**不使用 LLM 自動選工具**，而是先示範最小可控鏈路：

```text
SKILL.md → LangGraph workflow → ToolRegistry → ToolExecutor → verification
```

這符合目前專案階段：先把 harness 與 tool execution 做穩，再加入 LLM-driven tool calling。

---

## 2. 新增檔案

```text
src/ai_agent_service/harness/
├── __init__.py
└── skill_graph.py

examples/langgraph_skill_runner.py
examples/skills/jimmy-visit-skill/SKILL.md
tests/test_langgraph_harness_skill.py
```

也新增 dependency：

```toml
langgraph>=0.2.0
```

---

## 3. 安裝或更新環境

如果你已經在 container 裡，先進專案目錄：

```bash
cd /workspace/ai-agent-service
```

拉最新版本：

```bash
git pull
```

安裝專案 dependencies：

```bash
python3 -m pip install -e '.[dev]'
```

如果你的 container 只有 `python` 沒有 `python3`：

```bash
python -m pip install -e '.[dev]'
```

---

## 4. 快速測試：呼叫範例 skill

建立一份測試文件：

```bash
mkdir -p examples/runtime
printf '這是一份 LangGraph Harness skill 測試文件。\n' > examples/runtime/source.txt
```

執行範例 skill：

```bash
PYTHONPATH=src python3 examples/langgraph_skill_runner.py \
  --skill examples/skills/jimmy-visit-skill/SKILL.md \
  --input examples/runtime/source.txt \
  --output examples/runtime/visited.txt \
  --json
```

如果你的環境只有 `python`：

```bash
PYTHONPATH=src python examples/langgraph_skill_runner.py \
  --skill examples/skills/jimmy-visit-skill/SKILL.md \
  --input examples/runtime/source.txt \
  --output examples/runtime/visited.txt \
  --json
```

預期會看到類似：

```json
{
  "skill_path": "examples/skills/jimmy-visit-skill/SKILL.md",
  "arguments": {
    "input_path": "examples/runtime/source.txt",
    "output_path": "examples/runtime/visited.txt"
  },
  "skill": {
    "name": "jimmy-visit-skill",
    "description": "Read a text file and write a new file with the Jimmy visit marker.",
    "tool": "jimmy_visit_document"
  },
  "selected_tool": "jimmy_visit_document",
  "status": "verified",
  "steps": [
    "initialize",
    "load_skill",
    "execute_tool",
    "verify"
  ]
}
```

實際輸出會包含更多 `tool_result` 與 `verification` 欄位。

---

## 5. 檢查輸出文件

```bash
cat examples/runtime/visited.txt
```

預期：

```text
這是一份 LangGraph Harness skill 測試文件。

Jimmy 到此一遊
```

---

## 6. 不輸出 JSON 的簡短模式

```bash
PYTHONPATH=src python3 examples/langgraph_skill_runner.py \
  --skill examples/skills/jimmy-visit-skill/SKILL.md \
  --input examples/runtime/source.txt \
  --output examples/runtime/visited.txt
```

預期類似：

```text
status: verified
skill: jimmy-visit-skill
tool: jimmy_visit_document
steps: initialize -> load_skill -> execute_tool -> verify
verification: {"output_path_exists": true, "marker_present": true, ...}
```

---

## 7. 如何寫自己的 skill

目前最小格式如下：

```markdown
---
name: my-skill
description: My first local skill.
tool: jimmy_visit_document
---

# My Skill

這裡可以寫這個 skill 的用途、輸入、輸出與注意事項。
```

必要 frontmatter：

| 欄位 | 說明 |
|---|---|
| `name` | skill 名稱 |
| `description` | skill 說明 |
| `tool` | 要呼叫的 Tool Registry tool 名稱 |

目前可直接測的 tool 是：

```text
jimmy_visit_document
```

它需要兩個 arguments：

```text
input_path
output_path
```

建立自己的 skill：

```bash
mkdir -p examples/skills/my-skill
cat > examples/skills/my-skill/SKILL.md <<'EOF'
---
name: my-skill
description: My own skill that writes Jimmy marker into a copied document.
tool: jimmy_visit_document
---

# My Skill

讀取一份 UTF-8 文件，並輸出一份加上 Jimmy marker 的文件。
EOF
```

呼叫自己的 skill：

```bash
PYTHONPATH=src python3 examples/langgraph_skill_runner.py \
  --skill examples/skills/my-skill/SKILL.md \
  --input examples/runtime/source.txt \
  --output examples/runtime/my-skill-output.txt \
  --json
```

檢查：

```bash
cat examples/runtime/my-skill-output.txt
```

---

## 8. 使用 `--arg KEY=VALUE` 傳入自訂參數

除了 `--input` / `--output`，也可以直接用 `--arg`：

```bash
PYTHONPATH=src python3 examples/langgraph_skill_runner.py \
  --skill examples/skills/jimmy-visit-skill/SKILL.md \
  --arg input_path=examples/runtime/source.txt \
  --arg output_path=examples/runtime/visited-from-arg.txt \
  --json
```

---

## 9. 跑測試

```bash
PYTHONPATH=src python3 -m pytest tests/test_langgraph_harness_skill.py -q
```

跑完整測試：

```bash
PYTHONPATH=src python3 -m pytest -q
```

跑 lint：

```bash
PYTHONPATH=src python3 -m ruff check .
```

---

## 10. 目前限制與下一步

目前這支程式是最小可測試版本：

- skill 透過 frontmatter 的 `tool` 欄位指定要呼叫哪個 tool。
- 尚未讓 LLM 自動讀 skill 後決定 tool。
- 尚未把執行紀錄寫入 `tool_calls` DB table，CLI 目前只回傳 final graph state。
- 尚未支援多 tool chain 或 conditional routing。

建議下一步：

1. 把 `run_harness_skill` 接到 API endpoint，例如 `POST /skills/run`。
2. 將 graph 每個 node 的狀態寫入 `agent_steps` 或 `run_steps`。
3. 讓 ToolExecutor 的執行結果同步寫入 `tool_calls`。
4. 加入 LLM planner node：由模型根據 goal + skill metadata 選擇 tool。
5. 加入 verification gate：測試、lint、smoke test 必須通過才能宣告完成。
