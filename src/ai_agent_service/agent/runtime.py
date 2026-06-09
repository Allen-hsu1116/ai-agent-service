from pydantic import BaseModel

from ai_agent_service.core.config import Settings
from ai_agent_service.providers.base import ChatMessage, ChatRequest, ModelProvider
from ai_agent_service.providers.factory import create_model_provider


class AgentResponse(BaseModel):
    reply: str
    model: str


class AgentRuntime:
    """Minimal runtime that hides the concrete LLM provider behind an interface."""

    HAKUNA_MATATA_TRIGGER = "哈庫拉瑪塔塔"
    HAKUNA_MATATA_DOCUMENT = "# 落地文檔\n\n真是很有意思"

    def __init__(self, provider: ModelProvider, settings: Settings | None = None):
        self.provider = provider
        self.settings = settings or Settings()

    @classmethod
    def from_settings(cls, settings: Settings) -> "AgentRuntime":
        return cls(provider=create_model_provider(settings), settings=settings)

    async def run(self, message: str) -> AgentResponse:
        if self.HAKUNA_MATATA_TRIGGER in message:
            return AgentResponse(reply=self.HAKUNA_MATATA_DOCUMENT, model="built-in-example")

        response = await self.provider.chat(
            ChatRequest(
                messages=[ChatMessage(role="user", content=message)],
                temperature=self.settings.llm_temperature,
            )
        )
        return AgentResponse(reply=response.content, model=response.model)
