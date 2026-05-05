"""views and audit log

Revision ID: 002
Revises: 001
Create Date: 2026-05-03

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "audit_log",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("table_name", sa.String(100), nullable=True),
        sa.Column("action", sa.String(50), nullable=False),
        sa.Column("query_text", sa.Text(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column(
            "timestamp",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_audit_log_timestamp", "audit_log", ["timestamp"])
    op.create_index("idx_audit_log_user_id", "audit_log", ["user_id"])

    op.execute("""
        CREATE OR REPLACE VIEW v_employee_safe AS
        SELECT
            e.id,
            e.employee_code,
            e.full_name,
            e.email,
            e.phone,
            CONCAT(LEFT(e.citizen_id, 3), '***', RIGHT(e.citizen_id, 3)) AS citizen_id_masked,
            e.birth_date,
            e.gender,
            e.join_date,
            e.job_title,
            e.department_id,
            e.status,
            d.name AS department_name
        FROM employees e
        JOIN departments d ON e.department_id = d.id
        WHERE e.deleted_at IS NULL
    """)

    op.execute("""
        CREATE OR REPLACE VIEW v_payroll_anonymized AS
        SELECT
            p.id,
            p.employee_id,
            p.level,
            p.effective_date,
            CASE
                WHEN p.base_salary < 15000000 THEN 'Junior band'
                WHEN p.base_salary < 30000000 THEN 'Mid band'
                WHEN p.base_salary < 50000000 THEN 'Senior band'
                ELSE 'Lead/Manager band'
            END AS salary_band,
            p.allowance
        FROM payroll p
        WHERE p.deleted_at IS NULL
    """)

    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT FROM pg_roles WHERE rolname = 'hr_chatbi_readonly'
            ) THEN
                CREATE ROLE hr_chatbi_readonly;
            END IF;
        END
        $$;
    """)
    op.execute("GRANT SELECT ON v_employee_safe TO hr_chatbi_readonly")
    op.execute("GRANT SELECT ON v_payroll_anonymized TO hr_chatbi_readonly")


def downgrade() -> None:
    op.execute("REVOKE SELECT ON v_payroll_anonymized FROM hr_chatbi_readonly")
    op.execute("REVOKE SELECT ON v_employee_safe FROM hr_chatbi_readonly")

    op.execute("DROP VIEW IF EXISTS v_payroll_anonymized")
    op.execute("DROP VIEW IF EXISTS v_employee_safe")

    op.drop_index("idx_audit_log_user_id", "audit_log")
    op.drop_index("idx_audit_log_timestamp", "audit_log")
    op.drop_table("audit_log")
