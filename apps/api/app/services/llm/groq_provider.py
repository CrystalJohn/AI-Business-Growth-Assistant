from __future__ import annotations

import json
import logging

from app.config import settings
from app.services.llm.base import LLMProvider, LLMResponse, ToolCall
from app.services.llm.prompts import SQL_GENERATION_PROMPT, VIEW_SCHEMA_DDL

logger = logging.getLogger(__name__)


class GroqProvider(LLMProvider):
    name = "groq"

    def __init__(self):
        from openai import AsyncOpenAI

        self.client = AsyncOpenAI(
            api_key=settings.groq_api_key,
            base_url="https://api.groq.com/openai/v1",
        )

    async def generate_with_tools(
        self,
        system_prompt: str,
        user_message: str,
        tools: list[dict],
    ) -> LLMResponse:
        try:
            openai_tools = [
                {
                    "type": "function",
                    "function": {
                        "name": t["name"],
                        "description": t["description"],
                        "parameters": t["input_schema"],
                    },
                }
                for t in tools
            ]

            response = await self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                tools=openai_tools,
                tool_choice="auto",
            )

            msg = response.choices[0].message
            if msg.tool_calls:
                tc = msg.tool_calls[0]
                return LLMResponse(
                    tool_call=ToolCall(
                        name=tc.function.name,
                        args=json.loads(tc.function.arguments),
                    ),
                    finish_reason="tool_call",
                )

            return LLMResponse(
                tool_call=None,
                raw_text=msg.content,
                finish_reason="no_match",
            )

        except Exception as e:
            logger.error("Groq error: %s", e)
            return LLMResponse(
                tool_call=None,
                raw_text=f"LLM error: {e}",
                finish_reason="error",
            )

    async def summarize(
        self,
        question: str,
        data: list[dict],
        max_words: int = 100,
    ) -> str:
        try:
            summary_data = data[:10]
            prompt = (
                f"Tóm tắt kết quả này thành 1-2 câu tiếng Việt cho HR. "
                f"Câu hỏi: {question}\n"
                f"Dữ liệu ({len(data)} dòng, hiển thị {len(summary_data)} dòng đầu): "
                f"{json.dumps(summary_data, ensure_ascii=False)}"
            )
            response = await self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
            )
            return response.choices[0].message.content or f"Tìm thấy {len(data)} kết quả."
        except Exception:
            return f"Tìm thấy {len(data)} kết quả."

    async def generate_sql(
        self,
        question: str,
        view_schema: str,
    ) -> str | None:
        try:
            prompt = SQL_GENERATION_PROMPT.format(
                view_schema=view_schema,
                question=question,
            )
            response = await self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
            )
            raw = (response.choices[0].message.content or "").strip()
            raw = raw.removeprefix("```sql").removeprefix("```").removesuffix("```").strip()
            return raw or None
        except Exception as e:
            logger.error("Groq generate_sql error: %s", e)
            return None
