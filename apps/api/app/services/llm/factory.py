from app.config import settings
from app.services.llm.base import LLMProvider
from app.services.llm.mock_provider import MockProvider


def get_provider() -> LLMProvider:
    """Factory: đọc LLM_PROVIDER env → trả về provider instance."""
    name = settings.llm_provider.lower()

    if name == "gemini":
        from app.services.llm.gemini_provider import GeminiFlashProvider

        return GeminiFlashProvider()

    if name == "groq":
        from app.services.llm.groq_provider import GroqProvider

        return GroqProvider()

    return MockProvider()
