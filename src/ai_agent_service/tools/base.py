from collections.abc import Callable
from typing import Any

from pydantic import BaseModel, Field


class ToolDefinition(BaseModel):
    """A small, JSON-schema-described function that an agent can call."""

    name: str
    description: str
    parameters: dict[str, Any] = Field(default_factory=dict)
    handler: Callable[..., Any] = Field(exclude=True)

    model_config = {"arbitrary_types_allowed": True}


class ToolResult(BaseModel):
    tool_name: str
    success: bool
    result: Any = None
    error: str | None = None
