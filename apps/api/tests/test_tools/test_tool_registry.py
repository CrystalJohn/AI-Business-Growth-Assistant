"""Tool Layer unit tests — headcount, search, RBAC."""
import pytest
from app.tools.registry import get_tool, list_tools, REGISTRY
from app.tools.base import ToolResult
from app.auth.schemas import CurrentUser


def test_registry_has_15_tools():
    assert len(REGISTRY) == 15


def test_list_tools_returns_schema():
    tools = list_tools()
    assert len(tools) == 15
    for t in tools:
        assert "name" in t
        assert "description" in t
        assert "input_schema" in t
        assert "output_schema" in t


def test_get_tool_unknown_raises():
    with pytest.raises(ValueError, match="Unknown tool"):
        get_tool("nonexistent_tool")


def test_get_tool_returns_instance():
    tool = get_tool("get_headcount_by_department")
    assert tool.name == "get_headcount_by_department"
    assert tool.required_role is None


def test_manager_access_any_tool():
    tool = get_tool("get_avg_salary_by_level")
    user = CurrentUser(user_id=1, username="hr_manager", role="HR_Manager", dept_id=1)
    tool.check_access(user)  # should not raise


def test_staff_blocked_manager_only_tool():
    tool = get_tool("get_avg_salary_by_level")
    user = CurrentUser(user_id=2, username="hr_staff", role="HR_Staff", dept_id=1)
    with pytest.raises(PermissionError, match="requires"):
        tool.check_access(user)


def test_staff_can_access_any_role_tool():
    tool = get_tool("get_headcount_by_department")
    user = CurrentUser(user_id=2, username="hr_staff", role="HR_Staff", dept_id=1)
    tool.check_access(user)  # should not raise


def test_input_validation():
    tool = get_tool("search_employees")
    args = tool.input_model(query="Nguyễn", limit=10)
    assert args.query == "Nguyễn"
    assert args.limit == 10


def test_input_validation_default():
    tool = get_tool("get_age_distribution")
    args = tool.input_model()
    assert args.bucket_size == 5


def test_manager_only_tools():
    manager_only = [
        name for name, cls in REGISTRY.items()
        if cls.required_role == "HR_Manager"
    ]
    assert len(manager_only) == 4
    assert "get_avg_salary_by_level" in manager_only
    assert "get_payroll_summary_by_month" in manager_only
    assert "get_turnover_rate" in manager_only
    assert "list_contracts_expiring_soon" in manager_only
