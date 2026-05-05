"""RLS (Row-Level Security) tests.

Yêu cầu DB đã chạy migration 004 + seed data.
Test kết nối trực tiếp Postgres (không qua API).
"""
import os

import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://admin:password@localhost:5432/bizgrowth_test",
)

engine = create_async_engine(TEST_DATABASE_URL, echo=False)
SessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture
async def rls_session():
    """Session với RLS context đã set."""
    async with SessionLocal() as session:
        yield session
        await session.rollback()


async def _set_role(session: AsyncSession, role: str, dept_id: int | None = None):
    """Set RLS session vars."""
    await session.execute(text(f"SET LOCAL app.role = '{role}'"))
    if dept_id is not None:
        await session.execute(text(f"SET LOCAL app.dept_id = '{dept_id}'"))


@pytest.mark.asyncio
async def test_manager_sees_all_employees(rls_session):
    """HR_Manager thấy tất cả employees."""
    await _set_role(rls_session, "HR_Manager")
    result = await rls_session.execute(text("SELECT COUNT(*) FROM employees WHERE deleted_at IS NULL"))
    count = result.scalar_one()
    assert count == 150, f"Expected 150, got {count}"


@pytest.mark.asyncio
async def test_staff_sees_only_own_dept(rls_session):
    """HR_Staff chỉ thấy employees cùng phòng ban."""
    await _set_role(rls_session, "HR_Staff", dept_id=1)
    result = await rls_session.execute(text("SELECT COUNT(*) FROM employees WHERE deleted_at IS NULL"))
    count = result.scalar_one()
    assert 0 < count < 150, f"Expected < 150 rows for staff, got {count}"


@pytest.mark.asyncio
async def test_staff_blocked_payroll(rls_session):
    """HR_Staff KHÔNG thấy payroll (RLS block)."""
    await _set_role(rls_session, "HR_Staff", dept_id=1)
    result = await rls_session.execute(text("SELECT COUNT(*) FROM payroll WHERE deleted_at IS NULL"))
    count = result.scalar_one()
    assert count == 0, f"Expected 0 (blocked), got {count}"


@pytest.mark.asyncio
async def test_manager_sees_payroll(rls_session):
    """HR_Manager thấy tất cả payroll."""
    await _set_role(rls_session, "HR_Manager")
    result = await rls_session.execute(text("SELECT COUNT(*) FROM payroll WHERE deleted_at IS NULL"))
    count = result.scalar_one()
    assert count == 150, f"Expected 150, got {count}"


@pytest.mark.asyncio
async def test_no_role_blocked(rls_session):
    """Không SET role → RLS block mọi bảng (default deny)."""
    # Không set role — default policy = false
    result = await rls_session.execute(text("SELECT COUNT(*) FROM employees WHERE deleted_at IS NULL"))
    count = result.scalar_one()
    assert count == 0, f"Expected 0 (no role = blocked), got {count}"


@pytest.mark.asyncio
async def test_audit_inserted_on_query(rls_session):
    """INSERT vào audit_log hoạt động (RLS cho phép INSERT)."""
    await _set_role(rls_session, "HR_Manager")
    await rls_session.execute(text("""
        INSERT INTO audit_log (action, user_id, role, question, mode, status)
        VALUES ('test', 1, 'HR_Manager', 'test question', 'sql', 'success')
    """))
    result = await rls_session.execute(text("SELECT COUNT(*) FROM audit_log WHERE action = 'test'"))
    count = result.scalar_one()
    assert count >= 1


@pytest.mark.asyncio
async def test_audit_blocked_logged(rls_session):
    """Audit log có thể ghi status=blocked."""
    await _set_role(rls_session, "HR_Manager")
    await rls_session.execute(text("""
        INSERT INTO audit_log (action, user_id, role, status, blocked_reason)
        VALUES ('test_blocked', 1, 'HR_Manager', 'blocked', 'invalid role')
    """))
    result = await rls_session.execute(text(
        "SELECT blocked_reason FROM audit_log WHERE action = 'test_blocked'"
    ))
    row = result.scalar_one()
    assert row == "invalid role"


@pytest.mark.asyncio
async def test_readonly_role_cannot_update(rls_session):
    """hr_chatbi_readonly không thể UPDATE employees."""
    # Switch to readonly role
    await rls_session.execute(text("SET ROLE hr_chatbi_readonly"))
    with pytest.raises(Exception) as exc_info:
        await rls_session.execute(text("UPDATE employees SET full_name = 'hacked' WHERE id = 1"))
    assert "permission denied" in str(exc_info.value).lower() or "PermissionDenied" in str(exc_info.typename)
    await rls_session.execute(text("RESET ROLE"))
