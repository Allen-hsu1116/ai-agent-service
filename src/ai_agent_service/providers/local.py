from ai_agent_service.providers.base import ChatRequest, ChatResponse, ModelProvider


class LocalModelProvider(ModelProvider):
    """Future extension point for local models.

    The service can later wire this class to llama.cpp, Ollama, vLLM, MLX, or a
    local OpenAI-compatible endpoint without changing the AgentRuntime API.
    """

    provider_name = "local"

    def __init__(self, model_path: str | None = None):
        self.model_path = model_path

    async def chat(self, request: ChatRequest) -> ChatResponse:
        raise NotImplementedError(
            "Local model provider is reserved for future implementation. "
            "Use AI_PROVIDER=openai-compatible for the current online API path."
        )
