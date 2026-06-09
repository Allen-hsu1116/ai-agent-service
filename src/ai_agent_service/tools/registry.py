from typing import Any

from ai_agent_service.tools.base import ToolDefinition, ToolResult
from ai_agent_service.tools.builtin.text_tools import build_text_tools


class ToolRegistry:
    """In-memory registry for built-in and custom tools."""

    def __init__(self) -> None:
        self._tools: dict[str, ToolDefinition] = {}

    def register(self, tool: ToolDefinition) -> None:
        if tool.name in self._tools:
            raise ValueError(f"Tool {tool.name!r} is already registered")
        self._tools[tool.name] = tool

    def list_tools(self) -> list[ToolDefinition]:
        return list(self._tools.values())

    def get(self, name: str) -> ToolDefinition:
        try:
            return self._tools[name]
        except KeyError as exc:
            raise KeyError(f"Unknown tool: {name}") from exc

    async def call(self, name: str, arguments: dict[str, Any]) -> ToolResult:
        tool = self.get(name)
        try:
            result = tool.handler(**arguments)
        except Exception as exc:  # noqa: BLE001 - tool errors should be returned, not crash the agent
            return ToolResult(tool_name=name, success=False, error=str(exc))
        return ToolResult(tool_name=name, success=True, result=result)


def create_default_tool_registry() -> ToolRegistry:
    registry = ToolRegistry()
    for tool in build_text_tools():
        registry.register(tool)
    return registry
