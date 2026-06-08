import pytest
from fastapi.testclient import TestClient

from ai_agent_service.agent.runtime import AgentRuntime
from ai_agent_service.core.config import Settings
from ai_agent_service.main import app
from ai_agent_service.providers.base import ChatMessage, ChatRequest, ChatResponse, ModelProvider
from ai_agent_service.providers.factory import create_model_provider
from ai_agent_service.providers.openai_compatible import OpenAICompatibleProvider


class FakeProvider(ModelProvider):
    async def chat(self, request: ChatRequest) -> ChatResponse:
        return ChatResponse(content=f"fake: {request.messages[-1].content}", model="fake-model")


def test_provider_factory_defaults_to_openai_compatible_for_online_api():
    settings = Settings(
        ai_provider="openai-compatible",
        llm_api_key="test-key",
        llm_base_url="https://api.example.com/v1",
        llm_model="example-model",
    )

    provider = create_model_provider(settings)

    assert isinstance(provider, OpenAICompatibleProvider)
    assert provider.model == "example-model"
    assert provider.base_url == "https://api.example.com/v1"


def test_provider_factory_can_select_local_placeholder_for_future_local_models():
    settings = Settings(ai_provider="local", local_model_path="/models/example.gguf")

    provider = create_model_provider(settings)

    assert provider.provider_name == "local"


@pytest.mark.asyncio
async def test_agent_runtime_uses_injected_provider():
    runtime = AgentRuntime(provider=FakeProvider())

    response = await runtime.run("hello")

    assert response.reply == "fake: hello"
    assert response.model == "fake-model"


def test_agent_endpoint_uses_configured_runtime_dependency_override():
    app.dependency_overrides.clear()

    async def override_runtime():
        return AgentRuntime(provider=FakeProvider())

    from ai_agent_service.main import get_agent_runtime

    app.dependency_overrides[get_agent_runtime] = override_runtime

    client = TestClient(app)
    response = client.post("/agent", json={"message": "hi"})

    assert response.status_code == 200
    assert response.json() == {"reply": "fake: hi", "model": "fake-model"}

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_openai_compatible_provider_posts_chat_completions(monkeypatch):
    captured = {}

    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "model": "gpt-test",
                "choices": [{"message": {"content": "hello from api"}}],
            }

    class FakeAsyncClient:
        def __init__(self, **kwargs):
            captured["client_kwargs"] = kwargs

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return None

        async def post(self, path, json):
            captured["path"] = path
            captured["json"] = json
            return FakeResponse()

    monkeypatch.setattr("ai_agent_service.providers.openai_compatible.httpx.AsyncClient", FakeAsyncClient)

    provider = OpenAICompatibleProvider(
        api_key="test-key",
        base_url="https://api.example.com/v1",
        model="gpt-test",
    )

    response = await provider.chat(
        ChatRequest(messages=[ChatMessage(role="user", content="hello")])
    )

    assert response.content == "hello from api"
    assert response.model == "gpt-test"
    assert captured["path"] == "/chat/completions"
    assert captured["json"] == {
        "model": "gpt-test",
        "messages": [{"role": "user", "content": "hello"}],
        "temperature": 0.2,
    }
    assert captured["client_kwargs"]["base_url"] == "https://api.example.com/v1"
    assert captured["client_kwargs"]["headers"]["Authorization"] == "Bearer test-key"
