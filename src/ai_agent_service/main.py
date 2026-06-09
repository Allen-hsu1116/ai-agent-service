from contextlib import asynccontextmanager

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
)
from ai_agent_service.api.sql import run_read_only_query
from ai_agent_service.core.config import Settings, get_settings
from ai_agent_service.db.repository import add_agent_run, add_message, get_or_create_session, list_messages
from ai_agent_service.db.session import get_database_session, init_database

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
