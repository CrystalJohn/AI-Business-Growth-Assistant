"""rls policies on 6 HR tables

Revision ID: 004
Revises: 003
Create Date: 2026-05-05

"""
from typing import Sequence, Union

from alembic import op

revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── Enable RLS on 6 tables (departments = public, skip) ──────────────
    for table in [
        "employees",
        "payroll",
        "attendance",
        "leave_requests",
        "performance_reviews",
        "audit_log",
    ]:
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
        op.execute(f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY")

    # ── employees policies ───────────────────────────────────────────────
    op.execute("""
        CREATE POLICY mgr_all_employees ON employees
        FOR SELECT
        USING (current_setting('app.role', true) = 'HR_Manager')
    """)
    op.execute("""
        CREATE POLICY staff_same_dept_employees ON employees
        FOR SELECT
        USING (
            current_setting('app.role', true) = 'HR_Staff'
            AND department_id = current_setting('app.dept_id', true)::int
        )
    """)
    op.execute("""
        CREATE POLICY default_deny_employees ON employees
        FOR SELECT
        USING (false)
    """)

    # ── payroll policies (HR_Manager only) ───────────────────────────────
    op.execute("""
        CREATE POLICY mgr_only_payroll ON payroll
        FOR SELECT
        USING (current_setting('app.role', true) = 'HR_Manager')
    """)
    op.execute("""
        CREATE POLICY default_deny_payroll ON payroll
        FOR SELECT
        USING (false)
    """)

    # ── attendance policies ──────────────────────────────────────────────
    op.execute("""
        CREATE POLICY mgr_all_attendance ON attendance
        FOR SELECT
        USING (current_setting('app.role', true) = 'HR_Manager')
    """)
    op.execute("""
        CREATE POLICY staff_same_dept_attendance ON attendance
        FOR SELECT
        USING (
            current_setting('app.role', true) = 'HR_Staff'
            AND employee_id IN (
                SELECT id FROM employees
                WHERE department_id = current_setting('app.dept_id', true)::int
            )
        )
    """)
    op.execute("""
        CREATE POLICY default_deny_attendance ON attendance
        FOR SELECT
        USING (false)
    """)

    # ── leave_requests policies ──────────────────────────────────────────
    op.execute("""
        CREATE POLICY mgr_all_leave_requests ON leave_requests
        FOR SELECT
        USING (current_setting('app.role', true) = 'HR_Manager')
    """)
    op.execute("""
        CREATE POLICY staff_same_dept_leave_requests ON leave_requests
        FOR SELECT
        USING (
            current_setting('app.role', true) = 'HR_Staff'
            AND employee_id IN (
                SELECT id FROM employees
                WHERE department_id = current_setting('app.dept_id', true)::int
            )
        )
    """)
    op.execute("""
        CREATE POLICY default_deny_leave_requests ON leave_requests
        FOR SELECT
        USING (false)
    """)

    # ── performance_reviews policies ─────────────────────────────────────
    op.execute("""
        CREATE POLICY mgr_all_performance_reviews ON performance_reviews
        FOR SELECT
        USING (current_setting('app.role', true) = 'HR_Manager')
    """)
    op.execute("""
        CREATE POLICY staff_same_dept_performance_reviews ON performance_reviews
        FOR SELECT
        USING (
            current_setting('app.role', true) = 'HR_Staff'
            AND employee_id IN (
                SELECT id FROM employees
                WHERE department_id = current_setting('app.dept_id', true)::int
            )
        )
    """)
    op.execute("""
        CREATE POLICY default_deny_performance_reviews ON performance_reviews
        FOR SELECT
        USING (false)
    """)

    # ── audit_log policies (INSERT for everyone, SELECT for manager) ─────
    op.execute("""
        CREATE POLICY insert_audit_log ON audit_log
        FOR INSERT
        WITH CHECK (true)
    """)
    op.execute("""
        CREATE POLICY mgr_select_audit_log ON audit_log
        FOR SELECT
        USING (current_setting('app.role', true) = 'HR_Manager')
    """)
    op.execute("""
        CREATE POLICY default_deny_audit_log ON audit_log
        FOR SELECT
        USING (false)
    """)

    # ── GRANT to hr_chatbi_readonly role ─────────────────────────────────
    op.execute("GRANT USAGE ON SCHEMA public TO hr_chatbi_readonly")
    op.execute("GRANT SELECT ON v_employee_safe TO hr_chatbi_readonly")
    op.execute("GRANT SELECT ON v_payroll_anonymized TO hr_chatbi_readonly")
    op.execute("GRANT INSERT ON audit_log TO hr_chatbi_readonly")
    op.execute("REVOKE UPDATE, DELETE ON audit_log FROM hr_chatbi_readonly")

    # ── GRANT on raw tables for RLS-filtered access ──────────────────────
    for table in [
        "employees",
        "payroll",
        "attendance",
        "leave_requests",
        "performance_reviews",
    ]:
        op.execute(f"GRANT SELECT ON {table} TO hr_chatbi_readonly")


def downgrade() -> None:
    # ── REVOKE all grants ────────────────────────────────────────────────
    for table in [
        "employees",
        "payroll",
        "attendance",
        "leave_requests",
        "performance_reviews",
    ]:
        op.execute(f"REVOKE SELECT ON {table} FROM hr_chatbi_readonly")

    op.execute("REVOKE INSERT ON audit_log FROM hr_chatbi_readonly")
    op.execute("REVOKE SELECT ON v_payroll_anonymized FROM hr_chatbi_readonly")
    op.execute("REVOKE SELECT ON v_employee_safe FROM hr_chatbi_readonly")
    op.execute("REVOKE USAGE ON SCHEMA public FROM hr_chatbi_readonly")

    # ── Drop all policies ────────────────────────────────────────────────
    policies = [
        ("employees", "mgr_all_employees"),
        ("employees", "staff_same_dept_employees"),
        ("employees", "default_deny_employees"),
        ("payroll", "mgr_only_payroll"),
        ("payroll", "default_deny_payroll"),
        ("attendance", "mgr_all_attendance"),
        ("attendance", "staff_same_dept_attendance"),
        ("attendance", "default_deny_attendance"),
        ("leave_requests", "mgr_all_leave_requests"),
        ("leave_requests", "staff_same_dept_leave_requests"),
        ("leave_requests", "default_deny_leave_requests"),
        ("performance_reviews", "mgr_all_performance_reviews"),
        ("performance_reviews", "staff_same_dept_performance_reviews"),
        ("performance_reviews", "default_deny_performance_reviews"),
        ("audit_log", "insert_audit_log"),
        ("audit_log", "mgr_select_audit_log"),
        ("audit_log", "default_deny_audit_log"),
    ]
    for table, policy in policies:
        op.execute(f"DROP POLICY IF EXISTS {policy} ON {table}")

    # ── Disable RLS ──────────────────────────────────────────────────────
    for table in [
        "audit_log",
        "performance_reviews",
        "leave_requests",
        "attendance",
        "payroll",
        "employees",
    ]:
        op.execute(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY")
