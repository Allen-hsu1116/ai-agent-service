from contextlib import asynccontextmanager
import json

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session as SQLAlchemySession

from ai_agent_service.agent.runtime import AgentRuntime
from ai_agent_service.api.schemas import (
    AgentRequest,
    AgentResponse,
    MessageItem,
    SQLQueryRequest,
    SQLQueryResponse,
    SessionMessagesResponse,
    ToolListResponse,
    ToolMetadata,
    ToolRunRequest,
    ToolRunResponse,
)
from ai_agent_service.api.sql import run_read_only_query
from ai_agent_service.core.config import Settings, get_settings
from ai_agent_service.db.repository import (
    add_agent_run,
    add_message,
    add_tool_call,
    get_or_create_session,
    list_messages,
)
from ai_agent_service.db.session import get_database_session, init_database
from ai_agent_service.tools.executor import ToolExecutionError, ToolExecutor
from ai_agent_service.tools.registry import ToolRegistry, create_default_tool_registry

@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ARG001
    init_database()
    yield


app = FastAPI(
    title="AI Agent Service",
    description="Starter API service for hosting AI agents.",
    version="0.1.0",
    lifespan=lifespan,
)


def get_agent_runtime(settings: Settings = Depends(get_settings)) -> AgentRuntime:
    return AgentRuntime.from_settings(settings)


def get_tool_registry() -> ToolRegistry:
    return create_default_tool_registry()


def get_tool_executor(registry: ToolRegistry = Depends(get_tool_registry)) -> ToolExecutor:
    return ToolExecutor(registry)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/agent", response_model=AgentResponse)
async def run_agent(
    request: AgentRequest,
    runtime: AgentRuntime = Depends(get_agent_runtime),
    db: SQLAlchemySession = Depends(get_database_session),
) -> AgentResponse:
    session = get_or_create_session(db, request.session_id)
    add_message(db, session.id, "user", request.message)

    response = await runtime.run(request.message)

    add_message(db, session.id, "assistant", response.reply)
    add_agent_run(
        db,
        session_id=session.id,
        input_text=request.message,
        output_text=response.reply,
        model=response.model,
    )
    db.commit()

    return AgentResponse(reply=response.reply, model=response.model, session_id=session.id)


@app.get("/sessions/{session_id}/messages", response_model=SessionMessagesResponse)
def get_session_messages(
    session_id: int,
    db: SQLAlchemySession = Depends(get_database_session),
) -> SessionMessagesResponse:
    messages = list_messages(db, session_id)
    if not messages:
        raise HTTPException(status_code=404, detail="Session not found or has no messages.")

    return SessionMessagesResponse(
        session_id=session_id,
        messages=[MessageItem(role=message.role, content=message.content) for message in messages],
    )


@app.post("/sql/query", response_model=SQLQueryResponse)
def sql_query(
    request: SQLQueryRequest,
    db: SQLAlchemySession = Depends(get_database_session),
) -> SQLQueryResponse:
    columns, rows = run_read_only_query(db, request.query)
    return SQLQueryResponse(columns=columns, rows=rows, row_count=len(rows))


@app.get("/tools", response_model=ToolListResponse)
def list_tools(registry: ToolRegistry = Depends(get_tool_registry)) -> ToolListResponse:
    return ToolListResponse(
        tools=[ToolMetadata(**tool.public_metadata()) for tool in registry.list()]
    )


@app.post("/tools/{tool_name}/run", response_model=ToolRunResponse)
def run_tool(
    tool_name: str,
    request: ToolRunRequest,
    executor: ToolExecutor = Depends(get_tool_executor),
    registry: ToolRegistry = Depends(get_tool_registry),
    db: SQLAlchemySession = Depends(get_database_session),
) -> ToolRunResponse:
    try:
        tool = registry.get(tool_name)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    try:
        result = executor.run(tool_name, request.arguments)
    except ToolExecutionError as exc:
        add_tool_call(
            db,
            tool_name=tool_name,
            status="error",
            side_effect=tool.side_effect,
            arguments_json=json.dumps(request.arguments, ensure_ascii=False),
            error_message=str(exc),
        )
        db.commit()
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    add_tool_call(
        db,
        tool_name=tool_name,
        status="success" if result.ok else "error",
        side_effect=tool.side_effect,
        arguments_json=json.dumps(request.arguments, ensure_ascii=False),
        result_json=json.dumps(result.result, ensure_ascii=False),
        error_message=result.error,
    )
    db.commit()

    return ToolRunResponse(
        tool_name=tool_name,
        ok=result.ok,
        result=result.result,
        error=result.error,
    )
