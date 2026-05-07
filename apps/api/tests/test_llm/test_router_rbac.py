"""LLM Router RBAC enforcement tests."""
import pytest
from unittest.mock import AsyncMock

from app.services.llm.base import LLMResponse, ToolCall
from app.services.llm_router import LLMRouter
from app.dependencies.mock_user import MockUser


@pytest.fixture
def mock_provider():
    provider = AsyncMock()
    provider.name = "mock"
    return provider


@pytest.fixture
def mock_db():
    db = AsyncMock()
    db.execute = AsyncMock()
    db.commit = AsyncMock()
    return db


@pytest.fixture
def staff():
    return MockUser(user_id=2, role="HR_Staff", dept_id=1)


@pytest.mark.asyncio
async def test_staff_blocked_manager_tool(mock_provider, mock_db, staff):
    mock_provider.generate_with_tools.return_value = LLMResponse(
        tool_call=ToolCall(name="get_avg_salary_by_level", args={}),
        finish_reason="tool_call",
    )
    router = LLMRouter(mock_provider)
    result = await router.route("Lương trung bình", staff, mock_db)
    assert result["rows"] == 0
    assert "requires role" in result["answer"]


@pytest.mark.asyncio
async def test_staff_allowed_any_role_tool(mock_provider, mock_db, staff):
    mock_provider.generate_with_tools.return_value = LLMResponse(
        tool_call=ToolCall(name="get_headcount_by_department", args={}),
        finish_reason="tool_call",
    )
    router = LLMRouter(mock_provider)
    result = await router.route("Headcount", staff, mock_db)
    assert result["tool"] == "get_headcount_by_department"
