"""LLM Router dispatch tests."""
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock

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
def manager():
    return MockUser(user_id=1, role="HR_Manager", dept_id=1)


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
async def test_router_no_match(mock_provider, mock_db, manager):
    mock_provider.generate_with_tools.return_value = LLMResponse(
        tool_call=None,
        raw_text="Em chưa hiểu.",
        finish_reason="no_match",
    )
    router = LLMRouter(mock_provider)
    result = await router.route("Thời tiết hôm nay", manager, mock_db)
    assert result["tool"] is None
    assert result["rows"] == 0


@pytest.mark.asyncio
async def test_router_unknown_tool(mock_provider, mock_db, manager):
    mock_provider.generate_with_tools.return_value = LLMResponse(
        tool_call=ToolCall(name="nonexistent_tool", args={}),
        finish_reason="tool_call",
    )
    router = LLMRouter(mock_provider)
    result = await router.route("test", manager, mock_db)
    assert "Unknown tool" in result["answer"]
