from abc import ABC, abstractmethod
from typing import Literal

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant", "tool"]
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    temperature: float = Field(default=0.2)


class ChatResponse(BaseModel):
    content: str
    model: str


class ModelProvider(ABC):
    provider_name: str

    @abstractmethod
    async def chat(self, request: ChatRequest) -> ChatResponse:
        """Return a chat completion for the provided messages."""
