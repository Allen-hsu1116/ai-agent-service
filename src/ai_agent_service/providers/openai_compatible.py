import httpx

from ai_agent_service.providers.base import ChatRequest, ChatResponse, ModelProvider


class OpenAICompatibleProvider(ModelProvider):
    """Provider for online OpenAI-compatible chat-completions APIs.

    This covers OpenAI today and leaves room for compatible services such as
    OpenRouter, vLLM, Ollama OpenAI-compatible endpoints, LM Studio, or a future
    self-hosted gateway by changing only base_url/model/config.
    """

    provider_name = "openai-compatible"

    def __init__(self, api_key: str | None, base_url: str, model: str, timeout: float = 60.0):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    async def chat(self, request: ChatRequest) -> ChatResponse:
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        payload = {
            "model": self.model,
            "messages": [message.model_dump() for message in request.messages],
            "temperature": request.temperature,
        }

        async with httpx.AsyncClient(
            base_url=self.base_url,
            headers=headers,
            timeout=self.timeout,
        ) as client:
            response = await client.post("/chat/completions", json=payload)
            response.raise_for_status()
            data = response.json()

        return ChatResponse(
            content=data["choices"][0]["message"]["content"],
            model=data.get("model", self.model),
        )
