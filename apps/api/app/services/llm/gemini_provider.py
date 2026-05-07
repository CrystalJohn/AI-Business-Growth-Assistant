from __future__ import annotations

import json
import logging
from typing import Any

from app.config import settings
from app.services.llm.base import LLMProvider, LLMResponse, ToolCall

logger = logging.getLogger(__name__)


class GeminiFlashProvider(LLMProvider):
    name = "gemini"

    def __init__(self):
        import google.generativeai as genai

        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel("gemini-2.5-flash")
        self._genai = genai

    async def generate_with_tools(
        self,
        system_prompt: str,
        user_message: str,
        tools: list[dict],
    ) -> LLMResponse:
        try:
            function_declarations = [
                self._genai.protos.FunctionDeclaration(
                    name=t["name"],
                    description=t["description"],
                    parameters=self._json_schema_to_proto(t["input_schema"]),
                )
                for t in tools
            ]
            gemini_tools = [
                self._genai.protos.Tool(function_declarations=function_declarations)
            ]

            response = await self.model.generate_content_async(
                f"{system_prompt}\n\nNgười dùng: {user_message}",
                tools=gemini_tools,
            )

            for part in response.candidates[0].content.parts:
                if fn_call := part.function_call:
                    return LLMResponse(
                        tool_call=ToolCall(
                            name=fn_call.name,
                            args=dict(fn_call.args) if fn_call.args else {},
                        ),
                        finish_reason="tool_call",
                    )

            return LLMResponse(
                tool_call=None,
                raw_text=response.text,
                finish_reason="no_match",
            )

        except Exception as e:
            logger.error("Gemini error: %s", e)
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
            prompt = (
                f"Tóm tắt kết quả này thành 1-2 câu tiếng Việt cho HR. "
                f"Câu hỏi: {question}\nDữ liệu: {json.dumps(data, ensure_ascii=False)[:500]}"
            )
            response = await self.model.generate_content_async(prompt)
            return response.text
        except Exception:
            return f"Tìm thấy {len(data)} kết quả."

    def _json_schema_to_proto(self, schema: dict[str, Any]) -> dict[str, Any]:
        """Convert Pydantic JSON Schema → Gemini Schema proto format."""
        properties = {}
        for prop_name, prop_def in schema.get("properties", {}).items():
            prop_type = prop_def.get("type", "string")
            type_map = {
                "string": "STRING",
                "integer": "INTEGER",
                "number": "NUMBER",
                "boolean": "BOOLEAN",
                "array": "ARRAY",
                "object": "OBJECT",
            }
            gemini_type = type_map.get(prop_type, "STRING")
            prop_config: dict[str, Any] = {"type_": gemini_type}
            if "description" in prop_def:
                prop_config["description"] = prop_def["description"]
            if prop_type == "array" and "items" in prop_def:
                items_type = prop_def["items"].get("type", "string")
                prop_config["items"] = {"type_": type_map.get(items_type, "STRING")}
            properties[prop_name] = self._genai.protos.Schema(**prop_config)

        required = schema.get("required", [])
        return self._genai.protos.Schema(
            type_="OBJECT",
            properties=properties,
            required=required,
        )
