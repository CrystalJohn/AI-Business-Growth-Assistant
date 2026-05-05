"""AuditRepository unit tests."""
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.audit_log import AuditLog
from app.repositories.audit_repo import AuditRepository


@pytest.mark.asyncio
async def test_log_query_creates_row(db_session: AsyncSession):
    """log_query() tạo 1 row trong audit_log."""
    repo = AuditRepository(db_session)
    entry = await repo.log_query(
        user_id=1,
        role="HR_Manager",
        question="Headcount theo phòng ban?",
        mode="sql",
        sql_executed="SELECT COUNT(*) FROM employees",
        rows_returned=4,
        duration_ms=120,
        status="success",
    )
    assert entry.id is not None
    assert entry.user_id == 1
    assert entry.role == "HR_Manager"
    assert entry.question == "Headcount theo phòng ban?"
    assert entry.status == "success"
    assert entry.rows_returned == 4
    assert entry.duration_ms == 120


@pytest.mark.asyncio
async def test_log_query_with_args_jsonb(db_session: AsyncSession):
    """log_query() lưu JSONB args đúng."""
    repo = AuditRepository(db_session)
    entry = await repo.log_query(
        user_id=2,
        role="HR_Staff",
        question="Test",
        mode="tool",
        tool_name="get_employees",
        args={"department_id": 1, "limit": 10},
        status="success",
    )
    assert entry.args == {"department_id": 1, "limit": 10}
    assert entry.tool_name == "get_employees"


@pytest.mark.asyncio
async def test_log_query_error_status(db_session: AsyncSession):
    """log_query() ghi status=error với error_message."""
    repo = AuditRepository(db_session)
    entry = await repo.log_query(
        user_id=1,
        role="HR_Manager",
        question="Bad query",
        mode="sql",
        status="error",
        error_message="Syntax error at line 1",
    )
    assert entry.status == "error"
    assert entry.error_message == "Syntax error at line 1"


@pytest.mark.asyncio
async def test_log_query_blocked_status(db_session: AsyncSession):
    """log_query() ghi status=blocked với blocked_reason."""
    repo = AuditRepository(db_session)
    entry = await repo.log_query(
        user_id=3,
        role="HR_Staff",
        question="SELECT * FROM payroll",
        mode="sql",
        status="blocked",
        blocked_reason="RLS policy denied access",
    )
    assert entry.status == "blocked"
    assert entry.blocked_reason == "RLS policy denied access"
