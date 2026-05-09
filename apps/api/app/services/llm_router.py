from __future__ import annotations

import logging
import time
import re

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.schemas import CurrentUser
from app.middleware.db_context import set_rls_context
from app.repositories.audit_repo import AuditRepository
from app.services.llm.base import LLMProvider, LLMResponse
from app.services.llm.prompts import SQL_GENERATION_PROMPT, SYSTEM_PROMPT_VN, VIEW_SCHEMA_DDL
from app.services.pii_masking import mask_response_data
from app.services.response_cache import response_cache
from app.services.sql_validator import validate as validate_sql
from app.tools.registry import get_tool, list_tools

logger = logging.getLogger(__name__)


class LLMRouter:
    def __init__(self, provider: LLMProvider):
        self.provider = provider

    async def route(
        self,
        question: str,
        user: CurrentUser,
        db: AsyncSession,
    ) -> dict:
        started = time.time()

        # 1. Cache lookup
        normalized = re.sub(r'\s+', ' ', question.strip().lower())
        cache_key = f"{user.role}:{normalized}" # add user.role because different roles may have different answers
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

        # 3. No tool match → SQL fallback
        if not llm_response.tool_call:
            return await self._sql_fallback(db, user, question, started)

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

        # 6. Format response + PII masking
        masked_data, mask_applied = mask_response_data(result.data, user.role)
        masked_list = masked_data if isinstance(masked_data, list) else ([masked_data] if masked_data else [])
        answer = await self.provider.summarize(question, masked_list)
        response = {
            "answer": answer,
            "data": masked_data,
            "rows": result.rows_returned,
            "tool": tool.name,
            "chart_type": result.chart_type,
            "mask_applied": mask_applied,
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

    async def _sql_fallback(
        self,
        db: AsyncSession,
        user: CurrentUser,
        question: str,
        started: float,
    ) -> dict:
        """Generate SQL via LLM, validate with sqlglot, execute on DB."""
        # Generate SQL
        raw_sql = await self.provider.generate_sql(question, VIEW_SCHEMA_DDL)
        if not raw_sql:
            await self._audit(
                db, user, question, None, started,
                status="no_match", reason="sql_generation_failed", mode="sql",
            )
            return {
                "answer": "Em chưa hiểu câu hỏi này. Vui lòng thử lại.",
                "data": [],
                "rows": 0,
                "tool": None,
                "mode": "sql",
            }

        # Validate SQL
        result = validate_sql(raw_sql)
        if not result.valid:
            logger.warning("SQL validation blocked: %s | SQL: %s", result.error, raw_sql)
            await self._audit(
                db, user, question, None, started,
                status="blocked", reason=result.error or "validation_failed", mode="sql",
            )
            return {
                "answer": f"Câu truy vấn không hợp lệ: {result.error}",
                "data": [],
                "rows": 0,
                "tool": None,
                "mode": "sql",
                "sql_generated": None,
                "validation_error": result.error,
            }

        safe_sql = result.sql

        # Execute with RLS context
        try:
            await set_rls_context(db, user.user_id, user.role, user.dept_id)
            rows_result = await db.execute(text(safe_sql))
            keys = list(rows_result.keys())
            data = [dict(zip(keys, row)) for row in rows_result.fetchall()]
        except Exception as exc:
            logger.error("SQL fallback execution error: %s | SQL: %s", exc, safe_sql)
            await self._audit(
                db, user, question, None, started,
                status="error", reason=str(exc), mode="sql",
            )
            return {
                "answer": f"Lỗi thực thi truy vấn: {exc}",
                "data": [],
                "rows": 0,
                "tool": None,
                "mode": "sql",
                "sql_generated": safe_sql,
            }

        masked_data, mask_applied = mask_response_data(data, user.role)
        masked_list = masked_data if isinstance(masked_data, list) else ([masked_data] if masked_data else [])
        answer = await self.provider.summarize(question, masked_list)
        response = {
            "answer": answer,
            "data": masked_data,
            "rows": len(data),
            "tool": None,
            "mode": "sql",
            "sql_generated": safe_sql,
            "mask_applied": mask_applied,
        }

        # Cache + audit
        cache_key = f"{user.role}:{question}"
        response_cache[cache_key] = response
        duration_ms = int((time.time() - started) * 1000)
        await AuditRepository(db).log_query(
            user_id=user.user_id,
            role=user.role,
            question=question,
            mode="sql",
            tool_name=None,
            args={"sql": safe_sql},
            rows_returned=len(data),
            duration_ms=duration_ms,
            status="success",
        )
        await db.commit()
        return response

    async def _audit(
        self,
        db: AsyncSession,
        user: CurrentUser,
        question: str,
        tool_name: str | None,
        started: float,
        status: str,
        reason: str,
        mode: str = "tool",
    ) -> None:
        duration_ms = int((time.time() - started) * 1000)
        await AuditRepository(db).log_query(
            user_id=user.user_id,
            role=user.role,
            question=question,
            mode=mode,
            tool_name=tool_name,
            duration_ms=duration_ms,
            status=status,
            blocked_reason=reason if status == "blocked" else None,
            error_message=reason if status == "error" else None,
        )
        await db.commit()
