from ai_agent_service.tools.base import ToolDefinition
from ai_agent_service.tools.document_tools import jimmy_visit_document


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, ToolDefinition] = {}

    def register(self, tool: ToolDefinition) -> None:
        if tool.name in self._tools:
            raise ValueError(f"Tool already registered: {tool.name}")
        self._tools[tool.name] = tool

    def get(self, name: str) -> ToolDefinition:
        try:
            return self._tools[name]
        except KeyError as exc:
            raise KeyError(f"Unknown tool: {name}") from exc

    def list(self) -> list[ToolDefinition]:
        return sorted(self._tools.values(), key=lambda tool: tool.name)


def create_default_tool_registry() -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(
        ToolDefinition(
            name="jimmy_visit_document",
            description=(
                "Read a UTF-8 text document and write a new document containing the "
                "original content followed by the marker 'Jimmy 到此一遊'. Use this as "
                "a controlled write-capable demo tool for validating Phase 2 tool execution."
            ),
            input_schema={
                "type": "object",
                "properties": {
                    "input_path": {
                        "type": "string",
                        "description": "Path to the UTF-8 text document to read.",
                    },
                    "output_path": {
                        "type": "string",
                        "description": "Path where the marked output document should be written.",
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
                    "marker": {"type": "string"},
                    "input_characters": {"type": "integer"},
                    "output_characters": {"type": "integer"},
                },
                "required": ["input_path", "output_path", "marker"],
            },
            permission="documents.write_demo",
            side_effect="write",
            timeout_seconds=10,
            retry=0,
            requires_approval=False,
            owner="AI Agent Service Team",
            audit_level="standard",
            handler=jimmy_visit_document,
        )
    )
    return registry
