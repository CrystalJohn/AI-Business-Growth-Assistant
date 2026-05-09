"""Unit tests for sql_validator — Week 5."""
import pytest

from app.services.sql_validator import DEFAULT_LIMIT, ALLOWED_VIEWS, validate


# ---------------------------------------------------------------------------
# Valid cases
# ---------------------------------------------------------------------------

def test_valid_select_single_view():
    sql = "SELECT full_name, job_title FROM v_employee_safe WHERE status = 'active' LIMIT 20"
    r = validate(sql)
    assert r.valid is True
    assert r.sql is not None
    assert r.error is None


def test_valid_select_join_two_views():
    sql = (
        "SELECT e.full_name, l.leave_type, l.total_days "
        "FROM v_employee_safe e "
        "JOIN v_leave_overview l ON e.id = l.employee_id "
        "WHERE l.status = 'approved' LIMIT 30"
    )
    r = validate(sql)
    assert r.valid is True


def test_valid_aggregate_with_group_by():
    sql = (
        "SELECT department_name, COUNT(*) AS cnt "
        "FROM v_employee_safe "
        "GROUP BY department_name "
        "ORDER BY cnt DESC LIMIT 10"
    )
    r = validate(sql)
    assert r.valid is True


def test_limit_auto_injected_when_missing():
    sql = "SELECT full_name FROM v_employee_safe"
    r = validate(sql)
    assert r.valid is True
    assert f"LIMIT {DEFAULT_LIMIT}" in r.sql


def test_limit_capped_at_max():
    sql = "SELECT full_name FROM v_employee_safe LIMIT 999"
    r = validate(sql)
    assert r.valid is True
    assert "LIMIT 100" in r.sql


def test_trailing_semicolon_stripped():
    sql = "SELECT full_name FROM v_employee_safe LIMIT 10;"
    r = validate(sql)
    assert r.valid is True


# ---------------------------------------------------------------------------
# Blocked: DML / DDL
# ---------------------------------------------------------------------------

def test_block_drop_statement():
    r = validate("DROP TABLE employees")
    assert r.valid is False
    assert "DROP" in r.error or "Select" in r.error or "Drop" in r.error


def test_block_insert_statement():
    r = validate("INSERT INTO employees (full_name) VALUES ('hacker')")
    assert r.valid is False


def test_block_update_statement():
    r = validate("UPDATE employees SET salary = 0 WHERE id = 1")
    assert r.valid is False


def test_block_delete_statement():
    r = validate("DELETE FROM employees WHERE id = 1")
    assert r.valid is False


def test_block_create_statement():
    r = validate("CREATE TABLE evil (id INT)")
    assert r.valid is False


# ---------------------------------------------------------------------------
# Blocked: base tables (not in whitelist)
# ---------------------------------------------------------------------------

def test_block_base_table_employees():
    r = validate("SELECT * FROM employees LIMIT 10")
    assert r.valid is False
    assert "employees" in r.error


def test_block_base_table_payroll():
    r = validate("SELECT base_salary FROM payroll LIMIT 10")
    assert r.valid is False
    assert "payroll" in r.error


# ---------------------------------------------------------------------------
# Blocked: multi-statement injection
# ---------------------------------------------------------------------------

def test_block_multi_statement_semicolon():
    r = validate("SELECT * FROM v_employee_safe LIMIT 1; DROP TABLE employees")
    assert r.valid is False
    assert "Multi-statement" in r.error


# ---------------------------------------------------------------------------
# Blocked: dangerous functions
# ---------------------------------------------------------------------------

def test_block_pg_sleep():
    r = validate("SELECT pg_sleep(10) FROM v_employee_safe LIMIT 1")
    assert r.valid is False


# ---------------------------------------------------------------------------
# All allowed views pass whitelist check
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("view", sorted(ALLOWED_VIEWS))
def test_all_allowed_views_pass(view):
    sql = f"SELECT * FROM {view} LIMIT 1"
    r = validate(sql)
    assert r.valid is True, f"Expected {view} to be allowed, got: {r.error}"
