from collections.abc import Callable
from typing import Any, Literal

from pydantic import BaseModel, Field

ToolSideEffect = Literal["read_only", "write", "external_action"]
ToolStatus = Literal["success", "error"]


class ToolResult(BaseModel):
    ok: bool
    result: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None


class ToolDefinition(BaseModel):
    name: str
    description: str
    input_schema: dict[str, Any]
    output_schema: dict[str, Any]
    permission: str
    side_effect: ToolSideEffect
    timeout_seconds: int = Field(default=30, gt=0)
    retry: int = Field(default=0, ge=0)
    requires_approval: bool = False
    owner: str | None = None
    audit_level: str = "standard"
    handler: Callable[[dict[str, Any]], ToolResult] = Field(exclude=True)

    model_config = {"arbitrary_types_allowed": True}

    def public_metadata(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema,
            "output_schema": self.output_schema,
            "permission": self.permission,
            "side_effect": self.side_effect,
            "timeout_seconds": self.timeout_seconds,
            "retry": self.retry,
            "requires_approval": self.requires_approval,
            "owner": self.owner,
            "audit_level": self.audit_level,
        }
