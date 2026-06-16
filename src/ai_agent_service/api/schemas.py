from typing import Any

from pydantic import BaseModel, Field


class AgentRequest(BaseModel):
    message: str = Field(min_length=1)
    session_id: int | None = None


class AgentResponse(BaseModel):
    reply: str
    model: str
    session_id: int


class MessageItem(BaseModel):
    role: str
    content: str


class SessionMessagesResponse(BaseModel):
    session_id: int
    messages: list[MessageItem]


class SQLQueryRequest(BaseModel):
    query: str = Field(min_length=1)


class SQLQueryResponse(BaseModel):
    columns: list[str]
    rows: list[dict[str, object]]
    row_count: int


class ToolMetadata(BaseModel):
    name: str
    description: str
    input_schema: dict[str, Any]
    output_schema: dict[str, Any]
    permission: str
    side_effect: str
    timeout_seconds: int
    retry: int
    requires_approval: bool
    owner: str | None = None
    audit_level: str


class ToolListResponse(BaseModel):
    tools: list[ToolMetadata]


class ToolRunRequest(BaseModel):
    arguments: dict[str, Any] = Field(default_factory=dict)


class ToolRunResponse(BaseModel):
    tool_name: str
    ok: bool
    result: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None
