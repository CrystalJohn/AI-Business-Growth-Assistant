"""Tool integration tests — require DB with seed data."""
import os
import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.tools.registry import get_tool
from app.dependencies.mock_user import MockUser
from app.middleware.db_context import set_rls_context

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://admin:password@localhost:5432/bizgrowth",
)

engine = create_async_engine(TEST_DATABASE_URL, echo=False)
SessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture
async def manager_session():
    async with SessionLocal() as session:
        await set_rls_context(session, user_id=1, role="HR_Manager", dept_id=1)
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def staff_session():
    async with SessionLocal() as session:
        await set_rls_context(session, user_id=2, role="HR_Staff", dept_id=1)
        yield session
        await session.rollback()


MANAGER = MockUser(user_id=1, role="HR_Manager", dept_id=1)
STAFF = MockUser(user_id=2, role="HR_Staff", dept_id=1)


@pytest.mark.asyncio
async def test_headcount_manager(manager_session):
    tool = get_tool("get_headcount_by_department")
    result = await tool.execute(manager_session, MANAGER, tool.input_model())
    assert result.rows_returned == 4
    assert result.chart_type == "bar"


@pytest.mark.asyncio
async def test_headcount_staff(staff_session):
    tool = get_tool("get_headcount_by_department")
    result = await tool.execute(staff_session, STAFF, tool.input_model())
    assert result.rows_returned > 0


@pytest.mark.asyncio
async def test_search_employees(manager_session):
    tool = get_tool("search_employees")
    result = await tool.execute(manager_session, MANAGER, tool.input_model(query="Nguyễn", limit=5))
    assert result.rows_returned <= 5


@pytest.mark.asyncio
async def test_employee_detail(manager_session):
    tool = get_tool("get_employee_detail")
    result = await tool.execute(manager_session, MANAGER, tool.input_model(employee_id=1))
    assert result.rows_returned == 1
    assert "full_name" in result.data


@pytest.mark.asyncio
async def test_avg_salary_manager(manager_session):
    tool = get_tool("get_avg_salary_by_level")
    result = await tool.execute(manager_session, MANAGER, tool.input_model())
    assert result.rows_returned > 0
    assert "level" in result.data[0]


@pytest.mark.asyncio
async def test_avg_salary_staff_blocked(staff_session):
    tool = get_tool("get_avg_salary_by_level")
    with pytest.raises(PermissionError):
        tool.check_access(STAFF)


@pytest.mark.asyncio
async def test_birthdays(manager_session):
    tool = get_tool("list_birthdays_this_month")
    result = await tool.execute(manager_session, MANAGER, tool.input_model(month=5))
    assert result.rows_returned >= 0


@pytest.mark.asyncio
async def test_tenure(manager_session):
    tool = get_tool("list_tenure_top_n")
    result = await tool.execute(manager_session, MANAGER, tool.input_model(n=5))
    assert result.rows_returned == 5
    assert "years" in result.data[0]
