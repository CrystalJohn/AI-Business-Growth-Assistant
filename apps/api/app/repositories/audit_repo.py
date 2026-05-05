from __future__ import annotations

from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.audit_log import AuditLog
from app.repositories.base import BaseRepository


class AuditRepository(BaseRepository[AuditLog]):
    model = AuditLog

    async def log_query(
        self,
        *,
        user_id: int,
        role: str,
        question: str,
        mode: str,
        sql_executed: str | None = None,
        tool_name: str | None = None,
        args: dict[str, Any] | None = None,
        rows_returned: int = 0,
        duration_ms: int = 0,
        status: str = "success",
        blocked_reason: str | None = None,
        error_message: str | None = None,
        mask_applied: bool = False,
        client_id: str | None = None,
    ) -> AuditLog:
        """Ghi 1 row vào audit_log. Trả về AuditLog instance đã flush."""
        entry = AuditLog(
            user_id=user_id,
            role=role,
            question=question,
            mode=mode,
            sql_executed=sql_executed,
            tool_name=tool_name,
            args=args,
            rows_returned=rows_returned,
            duration_ms=duration_ms,
            status=status,
            blocked_reason=blocked_reason,
            error_message=error_message,
            mask_applied=mask_applied,
            client_id=client_id,
            action="chat_query",
        )
        return await self.add(entry)
