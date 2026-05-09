"""LLM Router dispatch tests."""
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock

from app.services.llm.base import LLMResponse, ToolCall
from app.services.llm_router import LLMRouter
from app.auth.schemas import CurrentUser


@pytest.fixture
def mock_provider():
    provider = AsyncMock()
    provider.name = "mock"
    return provider


@pytest.fixture
def mock_db():
    db = AsyncMock()
    fake_result = MagicMock()
    fake_result.fetchall.return_value = [
        ("Kỹ thuật", 38, 22, 16),
        ("Marketing", 37, 23, 14),
    ]
    fake_result.keys.return_value = ["phong_ban", "so_nhan_vien", "nam", "nu"]
    db.execute = AsyncMock(return_value=fake_result)
    db.commit = AsyncMock()
    return db


@pytest.fixture
def manager():
    return CurrentUser(user_id=1, username="hr_manager", role="HR_Manager", dept_id=1)


@pytest.mark.asyncio
async def test_router_dispatches_tool(mock_provider, mock_db, manager):
    mock_provider.generate_with_tools.return_value = LLMResponse(
        tool_call=ToolCall(name="get_headcount_by_department", args={}),
        finish_reason="tool_call",
    )
    router = LLMRouter(mock_provider)
    result = await router.route("Headcount theo phòng ban", manager, mock_db)
    assert result["tool"] == "get_headcount_by_department"
    assert result["rows"] > 0


@pytest.mark.asyncio
async def test_router_no_match_triggers_sql_fallback(mock_provider, mock_db, manager):
    mock_provider.generate_with_tools.return_value = LLMResponse(
        tool_call=None,
        raw_text="Em chưa hiểu.",
        finish_reason="no_match",
    )
    mock_provider.generate_sql = AsyncMock(return_value=None)
    router = LLMRouter(mock_provider)
    result = await router.route("Thời tiết hôm nay", manager, mock_db)
    assert result["tool"] is None
    assert result["mode"] == "sql"
    mock_provider.generate_sql.assert_awaited_once()


@pytest.mark.asyncio
async def test_router_unknown_tool(mock_provider, mock_db, manager):
    mock_provider.generate_with_tools.return_value = LLMResponse(
        tool_call=ToolCall(name="nonexistent_tool", args={}),
        finish_reason="tool_call",
    )
    router = LLMRouter(mock_provider)
    result = await router.route("test", manager, mock_db)
    assert "Unknown tool" in result["answer"]
