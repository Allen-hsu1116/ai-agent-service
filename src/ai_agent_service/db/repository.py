from sqlalchemy import select
from sqlalchemy.orm import Session as SQLAlchemySession

from ai_agent_service.db.models import AgentRun, Message, Session, ToolCall


def get_or_create_session(db: SQLAlchemySession, session_id: int | None = None) -> Session:
    if session_id is not None:
        existing = db.get(Session, session_id)
        if existing is not None:
            return existing

    session = Session(title=None)
    db.add(session)
    db.flush()
    return session


def add_message(db: SQLAlchemySession, session_id: int, role: str, content: str) -> Message:
    message = Message(session_id=session_id, role=role, content=content)
    db.add(message)
    db.flush()
    return message


def add_agent_run(
    db: SQLAlchemySession,
    session_id: int,
    input_text: str,
    output_text: str | None,
    model: str | None,
    status: str = "completed",
    error: str | None = None,
) -> AgentRun:
    run = AgentRun(
        session_id=session_id,
        input_text=input_text,
        output_text=output_text,
        model=model,
        status=status,
        error=error,
    )
    db.add(run)
    db.flush()
    return run


def list_messages(db: SQLAlchemySession, session_id: int) -> list[Message]:
    return list(
        db.scalars(select(Message).where(Message.session_id == session_id).order_by(Message.id))
    )


def add_tool_call(
    db: SQLAlchemySession,
    *,
    tool_name: str,
    status: str,
    side_effect: str,
    arguments_json: str,
    result_json: str | None = None,
    error_message: str | None = None,
) -> ToolCall:
    tool_call = ToolCall(
        tool_name=tool_name,
        status=status,
        side_effect=side_effect,
        arguments_json=arguments_json,
        result_json=result_json,
        error_message=error_message,
    )
    db.add(tool_call)
    db.flush()
    return tool_call
