"""constrained t2sql additional views

Revision ID: 005
Revises: 004
Create Date: 2026-05-07

"""
from typing import Sequence, Union

from alembic import op

revision: str = "005"
down_revision: Union[str, None] = "004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        CREATE OR REPLACE VIEW v_attendance_daily AS
        SELECT
            a.id,
            a.employee_id,
            e.employee_code,
            e.full_name,
            e.job_title,
            d.name AS department_name,
            a.work_date,
            a.check_in,
            a.check_out,
            a.status
        FROM attendance a
        JOIN employees e ON e.id = a.employee_id
        JOIN departments d ON d.id = e.department_id
        WHERE a.deleted_at IS NULL
          AND e.deleted_at IS NULL
    """)

    op.execute("""
        CREATE OR REPLACE VIEW v_leave_overview AS
        SELECT
            lr.id,
            lr.employee_id,
            e.employee_code,
            e.full_name,
            e.job_title,
            d.name AS department_name,
            lr.leave_type,
            lr.start_date,
            lr.end_date,
            (lr.end_date - lr.start_date + 1) AS total_days,
            lr.status,
            lr.reason
        FROM leave_requests lr
        JOIN employees e ON e.id = lr.employee_id
        JOIN departments d ON d.id = e.department_id
        WHERE lr.deleted_at IS NULL
          AND e.deleted_at IS NULL
    """)

    op.execute("""
        CREATE OR REPLACE VIEW v_performance_summary AS
        SELECT
            pr.id,
            pr.employee_id,
            e.employee_code,
            e.full_name,
            e.job_title,
            d.name AS department_name,
            pr.period,
            pr.score,
            pr.rating,
            pr.comment
        FROM performance_reviews pr
        JOIN employees e ON e.id = pr.employee_id
        JOIN departments d ON d.id = e.department_id
        WHERE pr.deleted_at IS NULL
          AND e.deleted_at IS NULL
    """)

    op.execute("""
        CREATE OR REPLACE VIEW v_department_list AS
        SELECT
            id,
            name AS department_name,
            description
        FROM departments
        WHERE deleted_at IS NULL
    """)

    for view in [
        "v_attendance_daily",
        "v_leave_overview",
        "v_performance_summary",
        "v_department_list",
    ]:
        op.execute(f"GRANT SELECT ON {view} TO hr_chatbi_readonly")


def downgrade() -> None:
    for view in [
        "v_department_list",
        "v_performance_summary",
        "v_leave_overview",
        "v_attendance_daily",
    ]:
        op.execute(f"REVOKE SELECT ON {view} FROM hr_chatbi_readonly")
        op.execute(f"DROP VIEW IF EXISTS {view}")
