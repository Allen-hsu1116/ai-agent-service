# Skills and Tools Guide

這份文件是下一階段的主要教學：如何在目前架構裡加入自己的 **Skill** 和 **Tool**。

目前系統的設計原則：

```text
SKILL.md = 宣告什麼情境要用、要呼叫哪個 tool、輸入輸出說明
ToolRegistry = 真正可執行工具的 schema / 權限 / side effect / handler
ToolExecutor = 執行前驗證 arguments，然後呼叫 handler
LangGraph Harness = initialize → load_skill → execute_tool → verify
```

也就是說：

- Skill 是 declarative，不直接執行 shell 或 Python。
- Tool 是 executable，由程式碼註冊與驗證。
- Skill 可以透過 frontmatter 的 `tool` 欄位指定要呼叫哪個 Tool Registry tool。

---

## 1. 目前已可用的最小範例

目前內建一個 tool：

```text
jimmy_visit_document
```

它會：

```text
讀取 input_path → 寫出 output_path → 在最後加上 Jimmy 到此一遊
```

對應範例 skill：

```text
examples/skills/jimmy-visit-skill/SKILL.md
```

執行：

```bash
mkdir -p examples/runtime
printf '我的 skill 測試文件。\n' > examples/runtime/source.txt

PYTHONPATH=src python3 examples/langgraph_skill_runner.py \
  --skill examples/skills/jimmy-visit-skill/SKILL.md \
  --input examples/runtime/source.txt \
  --output examples/runtime/visited.txt \
  --json
```

檢查：

```bash
cat examples/runtime/visited.txt
```

---

## 2. 只新增自己的 Skill：使用既有 tool

如果你的需求只是換一個 skill 名稱、描述或使用情境，而且仍然呼叫既有 `jimmy_visit_document`，只要新增 `SKILL.md`。

### Step 1：建立資料夾

```bash
mkdir -p examples/skills/my-first-skill
```

### Step 2：建立 `SKILL.md`

```bash
cat > examples/skills/my-first-skill/SKILL.md <<'EOF'
---
name: my-first-skill
description: My first skill that calls an existing document-writing tool.
tool: jimmy_visit_document
---

# My First Skill

## When to use

當我想讀取一份文字文件，並輸出一份加上 Jimmy marker 的文件時使用。

## Inputs

- `input_path`: 要讀取的 UTF-8 文字檔。
- `output_path`: 要寫出的結果檔。

## Expected result

輸出檔會包含原始內容，最後加上：

```text
Jimmy 到此一遊
```
EOF
```

### Step 3：測試自己的 skill

```bash
PYTHONPATH=src python3 examples/langgraph_skill_runner.py \
  --skill examples/skills/my-first-skill/SKILL.md \
  --input examples/runtime/source.txt \
  --output examples/runtime/my-first-skill-output.txt \
  --json
```

如果成功，會看到：

```json
{
  "selected_tool": "jimmy_visit_document",
  "status": "verified"
}
```

---

## 3. 新增自己的 Tool：完整流程

如果你要新增真正的新能力，例如「把文字轉成大寫」、「讀 CSV」、「呼叫內部 API」，就需要新增 tool handler、註冊到 Tool Registry、補測試，再寫一個 skill 來呼叫它。

下面用 `uppercase_document` 當教學範例：

```text
讀取 input_path → 將內容轉成大寫 → 寫到 output_path
```

### Step 1：新增 handler

新增檔案：

```text
src/ai_agent_service/tools/text_tools.py
```

內容：

```python
from pathlib import Path
from typing import Any

from ai_agent_service.tools.base import ToolResult


def uppercase_document(arguments: dict[str, Any]) -> ToolResult:
    input_path = Path(str(arguments["input_path"])).expanduser()
    output_path = Path(str(arguments["output_path"])).expanduser()

    original_content = input_path.read_text(encoding="utf-8")
    transformed = original_content.upper()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(transformed, encoding="utf-8")

    return ToolResult(
        ok=True,
        result={
            "input_path": str(input_path),
            "output_path": str(output_path),
            "input_characters": len(original_content),
            "output_characters": len(transformed),
            "transform": "uppercase",
        },
    )
```

### Step 2：註冊到 Tool Registry

修改：

```text
src/ai_agent_service/tools/registry.py
```

在 import 區加入：

```python
from ai_agent_service.tools.text_tools import uppercase_document
```

在 `create_default_tool_registry()` 裡新增：

```python
registry.register(
    ToolDefinition(
        name="uppercase_document",
        description="Read a UTF-8 text document, uppercase its content, and write it to output_path.",
        input_schema={
            "type": "object",
            "properties": {
                "input_path": {
                    "type": "string",
                    "description": "Path to the UTF-8 text document to read.",
                },
                "output_path": {
                    "type": "string",
                    "description": "Path where the uppercased output document should be written.",
                },
            },
            "required": ["input_path", "output_path"],
            "additionalProperties": False,
        },
        output_schema={
            "type": "object",
            "properties": {
                "input_path": {"type": "string"},
                "output_path": {"type": "string"},
                "input_characters": {"type": "integer"},
                "output_characters": {"type": "integer"},
                "transform": {"type": "string"},
            },
            "required": ["input_path", "output_path", "transform"],
        },
        permission="documents.write_demo",
        side_effect="write",
        timeout_seconds=10,
        retry=0,
        requires_approval=False,
        owner="AI Agent Service Team",
        audit_level="standard",
        handler=uppercase_document,
    )
)
```

### Step 3：新增測試

新增或修改測試，例如：

```text
tests/test_tools.py
```

加入：

```python
def test_tool_executor_runs_uppercase_document(tmp_path: Path):
    input_path = tmp_path / "source.txt"
    output_path = tmp_path / "upper.txt"
    input_path.write_text("hello Jimmy\n", encoding="utf-8")
    executor = ToolExecutor(create_default_tool_registry())

    result = executor.run(
        "uppercase_document",
        {"input_path": str(input_path), "output_path": str(output_path)},
    )

    assert result.ok is True
    assert result.result["transform"] == "uppercase"
    assert output_path.read_text(encoding="utf-8") == "HELLO JIMMY\n"
```

### Step 4：新增 Skill

```bash
mkdir -p examples/skills/uppercase-document-skill
cat > examples/skills/uppercase-document-skill/SKILL.md <<'EOF'
---
name: uppercase-document-skill
description: Read a text file and write an uppercased copy.
tool: uppercase_document
---

# Uppercase Document Skill

## Inputs

- `input_path`: 要讀取的 UTF-8 文字檔。
- `output_path`: 要寫出的結果檔。

## Expected result

輸出檔內容會是原始文件的大寫版本。
EOF
```

### Step 5：用 LangGraph Skill Runner 測試

```bash
mkdir -p examples/runtime
printf 'hello Jimmy\n' > examples/runtime/lower.txt

PYTHONPATH=src python3 examples/langgraph_skill_runner.py \
  --skill examples/skills/uppercase-document-skill/SKILL.md \
  --input examples/runtime/lower.txt \
  --output examples/runtime/upper.txt \
  --json

cat examples/runtime/upper.txt
```

預期：

```text
HELLO JIMMY
```

### Step 6：用 API 測試 tool

啟動服務後：

```bash
curl -X POST http://127.0.0.1:8020/tools/uppercase_document/run \
  -H 'Content-Type: application/json' \
  -d '{
    "arguments": {
      "input_path": "examples/runtime/lower.txt",
      "output_path": "examples/runtime/upper-api.txt"
    }
  }'
```

檢查 tool call log：

```bash
curl -X POST http://127.0.0.1:8020/sql/query \
  -H 'Content-Type: application/json' \
  -d '{"query":"SELECT tool_name, status, side_effect FROM tool_calls ORDER BY id"}'
```

### Step 7：跑測試與 lint

```bash
PYTHONPATH=src python -m pytest -q
PYTHONPATH=src python -m ruff check .
git diff --check
```

---

## 4. Tool Metadata 怎麼填

| 欄位 | 目前用途 | 未來用途 |
|---|---|---|
| `name` | API / Skill 呼叫 tool 的名稱 | LLM planner 選 tool |
| `description` | `/tools` 顯示與文件說明 | 給 LLM 做工具選擇依據 |
| `input_schema` | ToolExecutor 驗證參數 | 自動產生 tool calling schema |
| `output_schema` | 說明回傳格式 | 驗證 tool result |
| `permission` | 目前是 metadata | 未來 RBAC / approval gate |
| `side_effect` | `tool_calls` 記錄 | 決定是否需要人工確認 |
| `requires_approval` | 目前是 metadata | 未來高風險 tool 需審核 |
| `handler` | 實際 Python function | 執行 tool |

建議 side effect 分類：

```text
read_only        # 只讀資料
write            # 寫本機檔案或 DB
external_action  # 發信、發文、下單、改外部系統
```

---

## 5. 目前狀態管理

| 路徑 | 狀態存在哪裡 | 說明 |
|---|---|---|
| `/agent` | `agent_runs.status` | 目前主要是 `completed` |
| `/tools/{tool}/run` | `tool_calls.status` | `success` / `error` |
| LangGraph skill runner | `HarnessSkillState.status` | `pending` → `initialized` → `skill_loaded` → `tool_executed` → `verified` |

目前 CLI skill runner 還沒有把每個 step 寫進 DB；下一階段會新增 `run_steps` / `agent_steps`。

---

## 6. 不要做的事

為了避免專案又變亂，請避免：

- 每做一個小功能就新增一份平行教學文件。
- 把 tool schema 只寫在 `SKILL.md`，卻沒註冊到 `ToolRegistry`。
- 在 skill 裡直接寫任意 shell command。
- 沒有測試就新增 tool handler。
- 把 runtime 測試輸出提交到 repo；`examples/runtime/` 已被 `.gitignore` 忽略。

新增 Skill / Tool 的 canonical 文件就是本檔案。之後請優先更新這裡。
