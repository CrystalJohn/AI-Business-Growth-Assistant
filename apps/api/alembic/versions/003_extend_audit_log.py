"""extend audit_log with 13 security columns

Revision ID: 003
Revises: 002
Create Date: 2026-05-05

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("audit_log", sa.Column("role", sa.String(20), nullable=True))
    op.add_column("audit_log", sa.Column("mode", sa.String(20), nullable=True))
    op.add_column("audit_log", sa.Column("tool_name", sa.String(100), nullable=True))
    op.add_column("audit_log", sa.Column("sql_executed", sa.Text(), nullable=True))
    op.add_column("audit_log", sa.Column("args", sa.JSON(), nullable=True))
    op.add_column("audit_log", sa.Column("rows_returned", sa.Integer(), nullable=True))
    op.add_column("audit_log", sa.Column("duration_ms", sa.Integer(), nullable=True))
    op.add_column("audit_log", sa.Column("status", sa.String(20), nullable=True))
    op.add_column("audit_log", sa.Column("blocked_reason", sa.Text(), nullable=True))
    op.add_column("audit_log", sa.Column("error_message", sa.Text(), nullable=True))
    op.add_column("audit_log", sa.Column("question", sa.Text(), nullable=True))
    op.add_column(
        "audit_log",
        sa.Column("mask_applied", sa.Boolean(), nullable=False, server_default="false"),
    )
    op.add_column("audit_log", sa.Column("client_id", sa.String(64), nullable=True))

    op.create_index("idx_audit_log_role", "audit_log", ["role"])
    op.create_index("idx_audit_log_status", "audit_log", ["status"])


def downgrade() -> None:
    op.drop_index("idx_audit_log_status", "audit_log")
    op.drop_index("idx_audit_log_role", "audit_log")

    op.drop_column("audit_log", "client_id")
    op.drop_column("audit_log", "mask_applied")
    op.drop_column("audit_log", "question")
    op.drop_column("audit_log", "error_message")
    op.drop_column("audit_log", "blocked_reason")
    op.drop_column("audit_log", "status")
    op.drop_column("audit_log", "duration_ms")
    op.drop_column("audit_log", "rows_returned")
    op.drop_column("audit_log", "args")
    op.drop_column("audit_log", "sql_executed")
    op.drop_column("audit_log", "tool_name")
    op.drop_column("audit_log", "mode")
    op.drop_column("audit_log", "role")
