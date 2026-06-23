from __future__ import annotations

from pathlib import Path
from typing import Any, TypedDict

from langgraph.graph import END, START, StateGraph

from ai_agent_service.tools.executor import ToolExecutor
from ai_agent_service.tools.registry import create_default_tool_registry


class HarnessSkillState(TypedDict, total=False):
    skill_path: str
    arguments: dict[str, Any]
    skill: dict[str, str]
    selected_tool: str
    tool_result: dict[str, Any]
    verification: dict[str, Any]
    status: str
    steps: list[str]
    errors: list[str]


def parse_skill_frontmatter(skill_path: str | Path) -> dict[str, str]:
    path = Path(skill_path)
    content = path.read_text(encoding="utf-8")
    lines = content.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError(f"Skill file must start with YAML-style frontmatter: {path}")

    metadata: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        metadata[key.strip()] = value.strip().strip('"').strip("'")

    if "name" not in metadata:
        raise ValueError(f"Skill frontmatter missing required key: name ({path})")
    if "tool" not in metadata:
        raise ValueError(f"Skill frontmatter missing required key: tool ({path})")
    return metadata


def _append_step(state: HarnessSkillState, step: str) -> list[str]:
    return [*state.get("steps", []), step]


def initialize(state: HarnessSkillState) -> HarnessSkillState:
    skill_path = Path(state["skill_path"])
    if not skill_path.exists():
        raise FileNotFoundError(f"Skill file not found: {skill_path}")
    return {"steps": _append_step(state, "initialize"), "status": "initialized"}


def load_skill(state: HarnessSkillState) -> HarnessSkillState:
    metadata = parse_skill_frontmatter(state["skill_path"])
    return {
        "skill": metadata,
        "selected_tool": metadata["tool"],
        "steps": _append_step(state, "load_skill"),
        "status": "skill_loaded",
    }


def execute_tool(state: HarnessSkillState) -> HarnessSkillState:
    registry = create_default_tool_registry()
    executor = ToolExecutor(registry)
    result = executor.run(state["selected_tool"], state.get("arguments", {}))
    return {
        "tool_result": result.model_dump(),
        "steps": _append_step(state, "execute_tool"),
        "status": "tool_executed" if result.ok else "tool_failed",
    }


def verify_result(state: HarnessSkillState) -> HarnessSkillState:
    arguments = state.get("arguments", {})
    output_path_value = arguments.get("output_path")
    marker = state.get("tool_result", {}).get("result", {}).get("marker")
    verification: dict[str, Any] = {
        "output_path_exists": False,
        "marker_present": False,
    }

    if output_path_value:
        output_path = Path(str(output_path_value)).expanduser()
        verification["output_path"] = str(output_path)
        verification["output_path_exists"] = output_path.exists()
        if output_path.exists() and marker:
            verification["marker_present"] = marker in output_path.read_text(encoding="utf-8")

    verified = bool(
        state.get("tool_result", {}).get("ok")
        and verification["output_path_exists"]
        and verification["marker_present"]
    )
    return {
        "verification": verification,
        "steps": _append_step(state, "verify"),
        "status": "verified" if verified else "needs_review",
    }


def build_harness_skill_graph():
    graph = StateGraph(HarnessSkillState)
    graph.add_node("initialize", initialize)
    graph.add_node("load_skill", load_skill)
    graph.add_node("execute_tool", execute_tool)
    graph.add_node("verify", verify_result)
    graph.add_edge(START, "initialize")
    graph.add_edge("initialize", "load_skill")
    graph.add_edge("load_skill", "execute_tool")
    graph.add_edge("execute_tool", "verify")
    graph.add_edge("verify", END)
    return graph.compile()


def run_harness_skill(skill_path: str, arguments: dict[str, Any]) -> HarnessSkillState:
    app = build_harness_skill_graph()
    return app.invoke(
        {
            "skill_path": skill_path,
            "arguments": arguments,
            "steps": [],
            "errors": [],
            "status": "pending",
        }
    )
