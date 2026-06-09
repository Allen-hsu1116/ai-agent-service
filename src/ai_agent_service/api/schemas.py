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
