from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolCall:
    name: str
    args: dict[str, Any]


@dataclass
class LLMResponse:
    tool_call: ToolCall | None = None
    raw_text: str | None = None
    finish_reason: str = "tool_call"  # tool_call | no_match | error


class LLMProvider(ABC):
    name: str

    @abstractmethod
    async def generate_with_tools(
        self,
        system_prompt: str,
        user_message: str,
        tools: list[dict],
    ) -> LLMResponse:
        """Gọi LLM với tool catalog, trả về LLMResponse."""
        ...

    @abstractmethod
    async def summarize(
        self,
        question: str,
        data: list[dict],
        max_words: int = 100,
    ) -> str:
        """Sinh text answer ngắn từ kết quả query."""
        ...

    @abstractmethod
    async def generate_sql(
        self,
        question: str,
        view_schema: str,
    ) -> str | None:
        """Sinh SQL SELECT dựa trên câu hỏi và schema views cho phép.

        Trả về raw SQL string hoặc None nếu không thể sinh.
        """
        ...
