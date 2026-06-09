from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from ai_agent_service.agent.runtime import AgentRuntime
from ai_agent_service.core.config import Settings
from ai_agent_service.db.session import create_session_factory, init_database
from ai_agent_service.main import app, get_agent_runtime, get_database_session
from ai_agent_service.providers.base import ChatRequest, ChatResponse, ModelProvider


class FakeProvider(ModelProvider):
    provider_name = "fake"

    async def chat(self, request: ChatRequest) -> ChatResponse:
        return ChatResponse(content=f"fake: {request.messages[-1].content}", model="fake-model")


@pytest.fixture()
def sqlite_settings(tmp_path: Path) -> Settings:
    return Settings(database_url=f"sqlite:///{tmp_path / 'agent.db'}")


@pytest.fixture()
def client(sqlite_settings: Settings):
    session_factory = create_session_factory(sqlite_settings.database_url)
    init_database(session_factory)

    def override_db_session():
        with session_factory() as session:
            yield session

    async def override_runtime():
        return AgentRuntime(provider=FakeProvider(), settings=sqlite_settings)

    app.dependency_overrides[get_database_session] = override_db_session
    app.dependency_overrides[get_agent_runtime] = override_runtime

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def test_database_initialization_creates_core_tables(sqlite_settings: Settings):
    session_factory = create_session_factory(sqlite_settings.database_url)
    init_database(session_factory)

    with session_factory() as session:
        rows = session.execute(
            text("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        ).all()

    table_names = {row[0] for row in rows}
    assert {"sessions", "messages", "agent_runs"}.issubset(table_names)


def test_agent_endpoint_calls_llm_and_persists_session_messages(client: TestClient):
    response = client.post("/agent", json={"message": "hello database"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["reply"] == "fake: hello database"
    assert payload["model"] == "fake-model"
    assert payload["session_id"]

    session_id = payload["session_id"]
    messages = client.get(f"/sessions/{session_id}/messages")

    assert messages.status_code == 200
    assert messages.json() == {
        "session_id": session_id,
        "messages": [
            {"role": "user", "content": "hello database"},
            {"role": "assistant", "content": "fake: hello database"},
        ],
    }


def test_agent_endpoint_can_continue_existing_session(client: TestClient):
    first = client.post("/agent", json={"message": "first"}).json()
    second = client.post(
        "/agent",
        json={"message": "second", "session_id": first["session_id"]},
    ).json()

    assert second["session_id"] == first["session_id"]

    messages = client.get(f"/sessions/{first['session_id']}/messages").json()["messages"]
    assert [message["role"] for message in messages] == ["user", "assistant", "user", "assistant"]


def test_read_only_sql_query_endpoint_returns_rows(client: TestClient):
    client.post("/agent", json={"message": "sql test"})

    response = client.post(
        "/sql/query",
        json={"query": "SELECT role, content FROM messages ORDER BY id"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "columns": ["role", "content"],
        "rows": [
            {"role": "user", "content": "sql test"},
            {"role": "assistant", "content": "fake: sql test"},
        ],
        "row_count": 2,
    }


def test_sql_query_endpoint_rejects_writes(client: TestClient):
    response = client.post(
        "/sql/query",
        json={"query": "DELETE FROM messages"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Only read-only SELECT, WITH, PRAGMA, or EXPLAIN queries are allowed."
