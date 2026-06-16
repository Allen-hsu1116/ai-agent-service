from typing import Any

from ai_agent_service.tools.base import ToolDefinition, ToolResult
from ai_agent_service.tools.registry import ToolRegistry


class ToolExecutionError(Exception):
    pass


class ToolExecutor:
    def __init__(self, registry: ToolRegistry):
        self.registry = registry

    def run(self, tool_name: str, arguments: dict[str, Any]) -> ToolResult:
        tool = self.registry.get(tool_name)
        self._validate_arguments(tool, arguments)

        try:
            return tool.handler(arguments)
        except ToolExecutionError:
            raise
        except Exception as exc:  # pragma: no cover - message is still surfaced to API/logs
            raise ToolExecutionError(str(exc)) from exc

    def _validate_arguments(self, tool: ToolDefinition, arguments: dict[str, Any]) -> None:
        schema = tool.input_schema
        if schema.get("type") != "object":
            raise ToolExecutionError(f"Tool {tool.name} input schema must be an object schema.")

        for required_name in schema.get("required", []):
            if required_name not in arguments:
                raise ToolExecutionError(f"Missing required argument: {required_name}")

        if schema.get("additionalProperties") is False:
            allowed_names = set(schema.get("properties", {}))
            for provided_name in arguments:
                if provided_name not in allowed_names:
                    raise ToolExecutionError(f"Unexpected argument: {provided_name}")

        for name, value in arguments.items():
            expected_type = schema.get("properties", {}).get(name, {}).get("type")
            if expected_type == "string" and not isinstance(value, str):
                raise ToolExecutionError(f"Argument {name} must be a string.")
            if expected_type == "integer" and not isinstance(value, int):
                raise ToolExecutionError(f"Argument {name} must be an integer.")
            if expected_type == "number" and not isinstance(value, int | float):
                raise ToolExecutionError(f"Argument {name} must be a number.")
            if expected_type == "boolean" and not isinstance(value, bool):
                raise ToolExecutionError(f"Argument {name} must be a boolean.")
