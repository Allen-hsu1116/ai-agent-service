from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from ai_agent_service.core.config import Settings
from ai_agent_service.db.session import create_session_factory, init_database
from ai_agent_service.main import app, get_database_session
from ai_agent_service.tools.executor import ToolExecutionError, ToolExecutor
from ai_agent_service.tools.registry import create_default_tool_registry


@pytest.fixture()
def client(tmp_path: Path):
    settings = Settings(database_url=f"sqlite:///{tmp_path / 'agent.db'}")
    session_factory = create_session_factory(settings.database_url)
    init_database(session_factory)

    def override_db_session():
        with session_factory() as session:
            yield session

    app.dependency_overrides[get_database_session] = override_db_session

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def test_default_tool_registry_exposes_standardized_jimmy_visit_tool():
    registry = create_default_tool_registry()

    tool = registry.get("jimmy_visit_document")

    assert tool.name == "jimmy_visit_document"
    assert tool.side_effect == "write"
    assert tool.permission == "documents.write_demo"
    assert tool.timeout_seconds == 10
    assert tool.input_schema["required"] == ["input_path", "output_path"]
    assert "Read a UTF-8 text document" in tool.description


def test_tool_executor_reads_document_and_writes_jimmy_visit_marker(tmp_path: Path):
    input_path = tmp_path / "source.txt"
    output_path = tmp_path / "visited.txt"
    input_path.write_text("原始文件內容\n", encoding="utf-8")
    executor = ToolExecutor(create_default_tool_registry())

    result = executor.run(
        "jimmy_visit_document",
        {"input_path": str(input_path), "output_path": str(output_path)},
    )

    assert result.ok is True
    assert result.result["marker"] == "Jimmy 到此一遊"
    assert result.result["input_path"] == str(input_path)
    assert result.result["output_path"] == str(output_path)
    assert output_path.read_text(encoding="utf-8") == "原始文件內容\n\nJimmy 到此一遊\n"


def test_tool_executor_rejects_missing_required_arguments(tmp_path: Path):
    input_path = tmp_path / "source.txt"
    input_path.write_text("原始文件內容\n", encoding="utf-8")
    executor = ToolExecutor(create_default_tool_registry())

    with pytest.raises(ToolExecutionError, match="Missing required argument: output_path"):
        executor.run("jimmy_visit_document", {"input_path": str(input_path)})


def test_tools_api_lists_runs_and_logs_jimmy_visit_tool(client: TestClient, tmp_path: Path):
    input_path = tmp_path / "source.txt"
    output_path = tmp_path / "visited.txt"
    input_path.write_text("hello Jimmy\n", encoding="utf-8")

    list_response = client.get("/tools")

    assert list_response.status_code == 200
    tools = list_response.json()["tools"]
    assert any(tool["name"] == "jimmy_visit_document" for tool in tools)

    run_response = client.post(
        "/tools/jimmy_visit_document/run",
        json={"arguments": {"input_path": str(input_path), "output_path": str(output_path)}},
    )

    assert run_response.status_code == 200
    payload = run_response.json()
    assert payload["tool_name"] == "jimmy_visit_document"
    assert payload["ok"] is True
    assert payload["result"]["marker"] == "Jimmy 到此一遊"
    assert output_path.read_text(encoding="utf-8") == "hello Jimmy\n\nJimmy 到此一遊\n"

    query_response = client.post(
        "/sql/query",
        json={"query": "SELECT tool_name, status, side_effect FROM tool_calls ORDER BY id"},
    )

    assert query_response.status_code == 200
    assert query_response.json()["rows"] == [
        {"tool_name": "jimmy_visit_document", "status": "success", "side_effect": "write"}
    ]
