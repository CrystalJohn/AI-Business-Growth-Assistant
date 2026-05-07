"""Mock provider unit tests."""
import pytest
import pytest_asyncio
from app.services.llm.mock_provider import MockProvider
from app.services.llm.base import LLMResponse, ToolCall

MOCK = MockProvider()


@pytest.mark.asyncio
async def test_headcount_keyword():
    result = await MOCK.generate_with_tools("", "Headcount theo phòng ban?", [])
    assert result.finish_reason == "tool_call"
    assert result.tool_call is not None
    assert result.tool_call.name == "get_headcount_by_department"


@pytest.mark.asyncio
async def test_salary_keyword():
    result = await MOCK.generate_with_tools("", "Lương trung bình theo level?", [])
    assert result.tool_call.name == "get_avg_salary_by_level"


@pytest.mark.asyncio
async def test_leave_keyword():
    result = await MOCK.generate_with_tools("", "Ai chưa duyệt nghỉ phép?", [])
    assert result.tool_call.name == "get_leave_balance"


@pytest.mark.asyncio
async def test_no_match():
    result = await MOCK.generate_with_tools("", "Thời tiết hôm nay thế nào?", [])
    assert result.finish_reason == "no_match"
    assert result.tool_call is None
    assert result.raw_text is not None


@pytest.mark.asyncio
async def test_summarize():
    result = await MOCK.summarize("test", [{"a": 1}])
    assert "1" in result
