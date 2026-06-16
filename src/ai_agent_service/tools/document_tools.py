from pathlib import Path
from typing import Any

from ai_agent_service.tools.base import ToolResult

JIMMY_VISIT_MARKER = "Jimmy 到此一遊"


def jimmy_visit_document(arguments: dict[str, Any]) -> ToolResult:
    input_path = Path(str(arguments["input_path"])).expanduser()
    output_path = Path(str(arguments["output_path"])).expanduser()

    original_content = input_path.read_text(encoding="utf-8")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    normalized_content = original_content.rstrip("\n")
    visited_content = f"{normalized_content}\n\n{JIMMY_VISIT_MARKER}\n"
    output_path.write_text(visited_content, encoding="utf-8")

    return ToolResult(
        ok=True,
        result={
            "input_path": str(input_path),
            "output_path": str(output_path),
            "marker": JIMMY_VISIT_MARKER,
            "input_characters": len(original_content),
            "output_characters": len(visited_content),
        },
    )
