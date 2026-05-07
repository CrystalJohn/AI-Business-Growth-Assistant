from __future__ import annotations

import logging
import time

from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.mock_user import MockUser
from app.middleware.db_context import set_rls_context
from app.repositories.audit_repo import AuditRepository
from app.services.llm.base import LLMProvider, LLMResponse
from app.services.llm.prompts import SYSTEM_PROMPT_VN
from app.services.response_cache import response_cache
from app.tools.registry import get_tool, list_tools

logger = logging.getLogger(__name__)


class LLMRouter:
    def __init__(self, provider: LLMProvider):
        self.provider = provider

    async def route(
        self,
        question: str,
        user: MockUser,
        db: AsyncSession,
    ) -> dict:
        started = time.time()

        # 1. Cache lookup
        cache_key = f"{user.role}:{question}"
        if cached := response_cache.get(cache_key):
            logger.info("Cache hit for: %s", cache_key)
            return cached

        # 2. LLM choose tool
        tools_catalog = list_tools()
        prompt = SYSTEM_PROMPT_VN.format(role=user.role, dept_id=user.dept_id)
        llm_response: LLMResponse = await self.provider.generate_with_tools(
            system_prompt=prompt,
            user_message=question,
            tools=tools_catalog,
        )

        # 3. No match → return text response
        if not llm_response.tool_call:
            await self._audit(
                db, user, question, None, started,
                status="no_match", reason="no_matching_tool",
            )
            return {
                "answer": llm_response.raw_text or "Em chưa hiểu câu hỏi này. Vui lòng thử lại.",
                "data": [],
                "rows": 0,
                "tool": None,
            }

        # 4. Validate + RBAC
        try:
            tool = get_tool(llm_response.tool_call.name)
            validated_args = tool.input_model(**llm_response.tool_call.args)
            tool.check_access(user)
        except (ValueError, PermissionError) as e:
            await self._audit(
                db, user, question, llm_response.tool_call.name, started,
                status="blocked", reason=str(e),
            )
            return {
                "answer": str(e),
                "data": [],
                "rows": 0,
                "tool": llm_response.tool_call.name,
            }

        # 5. Set RLS + execute
        try:
            await set_rls_context(db, user.user_id, user.role, user.dept_id)
            result = await tool.execute(db, user, validated_args)
        except Exception as exc:
            logger.error("Tool %s execution error: %s", tool.name, exc)
            await self._audit(
                db, user, question, tool.name, started,
                status="error", reason=str(exc),
            )
            return {
                "answer": f"Lỗi khi thực thi: {exc}",
                "data": [],
                "rows": 0,
                "tool": tool.name,
                "chart_type": None,
            }

        # 6. Format response
        data_list = result.data if isinstance(result.data, list) else ([result.data] if result.data else [])
        answer = await self.provider.summarize(question, data_list)
        response = {
            "answer": answer,
            "data": result.data,
            "rows": result.rows_returned,
            "tool": tool.name,
            "chart_type": result.chart_type,
        }

        # 7. Cache + audit
        response_cache[cache_key] = response
        duration_ms = int((time.time() - started) * 1000)
        await AuditRepository(db).log_query(
            user_id=user.user_id,
            role=user.role,
            question=question,
            mode="tool",
            tool_name=tool.name,
            args=validated_args.model_dump(),
            rows_returned=result.rows_returned,
            duration_ms=duration_ms,
            status="success",
        )
        await db.commit()
        return response

    async def _audit(
        self,
        db: AsyncSession,
        user: MockUser,
        question: str,
        tool_name: str | None,
        started: float,
        status: str,
        reason: str,
    ) -> None:
        duration_ms = int((time.time() - started) * 1000)
        await AuditRepository(db).log_query(
            user_id=user.user_id,
            role=user.role,
            question=question,
            mode="tool",
            tool_name=tool_name,
            duration_ms=duration_ms,
            status=status,
            blocked_reason=reason if status == "blocked" else None,
            error_message=reason if status == "error" else None,
        )
        await db.commit()
