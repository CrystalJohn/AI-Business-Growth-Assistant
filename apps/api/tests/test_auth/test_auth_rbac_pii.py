"""Auth + RBAC + PII masking unit tests."""
import pytest
from app.auth.security import hash_password, verify_password
from app.auth.jwt import create_access_token, decode_access_token
from app.auth.schemas import CurrentUser
from app.tools.base import ROLE_HIERARCHY
from app.tools.registry import REGISTRY, get_tool
from app.services.pii_masking import mask_response_data


# ── Password hashing ────────────────────────────────────────────────
def test_hash_password():
    hashed = hash_password("test123")
    assert hashed != "test123"
    assert verify_password("test123", hashed)


def test_verify_wrong_password():
    hashed = hash_password("test123")
    assert not verify_password("wrong", hashed)


# ── JWT ─────────────────────────────────────────────────────────────
def test_create_and_decode_token():
    token = create_access_token({"sub": "1", "username": "hr_manager", "role": "HR_Manager", "dept_id": None})
    payload = decode_access_token(token)
    assert payload is not None
    assert payload["sub"] == "1"
    assert payload["role"] == "HR_Manager"


def test_decode_invalid_token():
    payload = decode_access_token("invalid.token.here")
    assert payload is None


def test_token_contains_all_fields():
    token = create_access_token({"sub": "2", "username": "hr_staff", "role": "HR_Staff", "dept_id": "1"})
    payload = decode_access_token(token)
    assert payload["username"] == "hr_staff"
    assert payload["dept_id"] == "1"


# ── RBAC ────────────────────────────────────────────────────────────
def test_role_hierarchy():
    assert ROLE_HIERARCHY["HR_Manager"] > ROLE_HIERARCHY["HR_Staff"]
    assert ROLE_HIERARCHY["HR_Manager"] > ROLE_HIERARCHY["Dept_Manager"]
    assert ROLE_HIERARCHY["Dept_Manager"] > ROLE_HIERARCHY["Viewer"]


def test_manager_can_access_manager_only_tool():
    tool = get_tool("get_avg_salary_by_level")
    user = CurrentUser(user_id=1, username="mgr", role="HR_Manager")
    tool.check_access(user)  # should not raise


def test_staff_blocked_from_manager_tool():
    tool = get_tool("get_avg_salary_by_level")
    user = CurrentUser(user_id=2, username="staff", role="HR_Staff", dept_id=1)
    with pytest.raises(PermissionError):
        tool.check_access(user)


def test_viewer_blocked_from_manager_tool():
    tool = get_tool("get_avg_salary_by_level")
    user = CurrentUser(user_id=4, username="viewer", role="Viewer")
    with pytest.raises(PermissionError):
        tool.check_access(user)


def test_staff_can_access_any_role_tool():
    tool = get_tool("get_headcount_by_department")
    user = CurrentUser(user_id=2, username="staff", role="HR_Staff", dept_id=1)
    tool.check_access(user)  # should not raise


def test_viewer_can_access_any_role_tool():
    tool = get_tool("get_headcount_by_department")
    user = CurrentUser(user_id=4, username="viewer", role="Viewer")
    tool.check_access(user)  # should not raise


# ── PII Masking ─────────────────────────────────────────────────────
def test_manager_sees_salary():
    data = [{"name": "Test", "base_salary": 20000000, "phone": "0912345678"}]
    masked, applied = mask_response_data(data, "HR_Manager")
    assert masked[0]["base_salary"] == 20000000
    assert not applied


def test_staff_salary_masked():
    data = [{"name": "Test", "base_salary": 20000000}]
    masked, applied = mask_response_data(data, "HR_Staff")
    assert masked[0]["base_salary"] == "***"
    assert applied


def test_viewer_salary_masked():
    data = [{"name": "Test", "base_salary": 20000000}]
    masked, applied = mask_response_data(data, "Viewer")
    assert masked[0]["base_salary"] == "***"
    assert applied


def test_phone_masked_for_viewer():
    data = [{"name": "Test", "phone": "0912345678"}]
    masked, applied = mask_response_data(data, "Viewer")
    assert masked[0]["phone"] == "***678"
    assert applied


def test_citizen_id_masked_for_viewer():
    data = [{"name": "Test", "citizen_id": "123456789012"}]
    masked, applied = mask_response_data(data, "Viewer")
    assert masked[0]["citizen_id"] == "***012"
    assert applied


def test_empty_data_no_masking():
    masked, applied = mask_response_data([], "HR_Staff")
    assert masked == []
    assert not applied


def test_none_data_no_masking():
    masked, applied = mask_response_data(None, "HR_Staff")
    assert masked is None
    assert not applied
