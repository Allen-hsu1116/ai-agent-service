import os
from functools import lru_cache

from pydantic import BaseModel, Field


class Settings(BaseModel):
    """Application settings for model-provider selection.

    The default provider is OpenAI-compatible so the service can start with an
    online API today while keeping a stable provider interface for local models
    later.
    """

    ai_provider: str = Field(default="openai-compatible")
    llm_api_key: str | None = Field(default=None)
    llm_base_url: str = Field(default="https://api.openai.com/v1")
    llm_model: str = Field(default="gpt-4o-mini")
    llm_temperature: float = Field(default=0.2)
    database_url: str = Field(default="sqlite:///./data/agent.db")
    local_model_path: str | None = Field(default=None)

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            ai_provider=os.getenv("AI_PROVIDER", "openai-compatible"),
            llm_api_key=os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY"),
            llm_base_url=os.getenv("LLM_BASE_URL", "https://api.openai.com/v1"),
            llm_model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
            llm_temperature=float(os.getenv("LLM_TEMPERATURE", "0.2")),
            database_url=os.getenv("DATABASE_URL", "sqlite:///./data/agent.db"),
            local_model_path=os.getenv("LOCAL_MODEL_PATH"),
        )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings.from_env()
