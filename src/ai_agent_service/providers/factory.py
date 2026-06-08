from ai_agent_service.core.config import Settings
from ai_agent_service.providers.base import ModelProvider
from ai_agent_service.providers.local import LocalModelProvider
from ai_agent_service.providers.openai_compatible import OpenAICompatibleProvider


def create_model_provider(settings: Settings) -> ModelProvider:
    provider = settings.ai_provider.lower().replace("_", "-")

    if provider in {"openai", "openai-compatible", "online"}:
        return OpenAICompatibleProvider(
            api_key=settings.llm_api_key,
            base_url=settings.llm_base_url,
            model=settings.llm_model,
        )

    if provider in {"local", "local-model"}:
        return LocalModelProvider(model_path=settings.local_model_path)

    raise ValueError(
        f"Unsupported AI_PROVIDER={settings.ai_provider!r}. "
        "Supported values: openai-compatible, local."
    )
