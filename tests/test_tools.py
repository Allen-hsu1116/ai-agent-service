import pytest

from ai_agent_service.tools import ToolRegistry, create_default_tool_registry
from ai_agent_service.tools.base import ToolDefinition


def test_default_registry_lists_example_tools():
    registry = create_default_tool_registry()

    names = {tool.name for tool in registry.list_tools()}

    assert {"count_words", "slugify", "extract_keywords"}.issubset(names)


@pytest.mark.asyncio
async def test_count_words_tool():
    registry = create_default_tool_registry()

    result = await registry.call("count_words", {"text": "Hello hello agent"})

    assert result.success is True
    assert result.result == {"characters": 17, "words": 3, "unique_words": 2}


@pytest.mark.asyncio
async def test_slugify_tool():
    registry = create_default_tool_registry()

    result = await registry.call("slugify", {"text": "Build an AI Agent Service!"})

    assert result.success is True
    assert result.result == "build-an-ai-agent-service"


@pytest.mark.asyncio
async def test_extract_keywords_tool():
    registry = create_default_tool_registry()

    result = await registry.call(
        "extract_keywords",
        {"text": "Agent tools help agents call useful tools", "limit": 2},
    )

    assert result.success is True
    assert result.result == ["tools", "agent"]


def test_duplicate_tool_registration_is_rejected():
    registry = ToolRegistry()
    tool = ToolDefinition(
        name="example",
        description="Example tool",
        parameters={"type": "object", "properties": {}},
        handler=lambda: "ok",
    )

    registry.register(tool)

    with pytest.raises(ValueError, match="already registered"):
        registry.register(tool)


@pytest.mark.asyncio
async def test_tool_errors_are_returned_as_tool_results():
    registry = ToolRegistry()
    registry.register(
        ToolDefinition(
            name="explode",
            description="Always fails",
            parameters={"type": "object", "properties": {}},
            handler=lambda: (_ for _ in ()).throw(RuntimeError("boom")),
        )
    )

    result = await registry.call("explode", {})

    assert result.success is False
    assert result.error == "boom"
