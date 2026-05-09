"""app_users table + seed demo accounts

Revision ID: 006
Revises: 005
Create Date: 2026-05-08

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "006"
down_revision: Union[str, None] = "005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Pre-computed bcrypt hashes (generated with bcrypt.hashpw)
# Passwords: manager123, staff123, dept123, viewer123
DEMO_USERS = [
    {"username": "hr_manager", "password_hash": "$2b$12$GltyHc9eG/yfk7sTf.fEY.6LL5xL9Cw9YLKpxSoRvyFP/74.RNDi6", "role": "HR_Manager", "dept_id": None},
    {"username": "hr_staff", "password_hash": "$2b$12$eT4oZo5j1RVYY9yNTs9NROwTJWdNzTBLPF0AdEOz6UYNlGZJfyngq", "role": "HR_Staff", "dept_id": 1},
    {"username": "dept_manager", "password_hash": "$2b$12$xN/3oZug/P6F3IOGYVHgEOs/3UbKIruGIrwIS5Ca.w0ojqTu.S1hC", "role": "Dept_Manager", "dept_id": 2},
    {"username": "viewer", "password_hash": "$2b$12$eF1A/r2.lKDgR2SI4abareOf49i44NGxS7Fvzngy3c2pQXhioKZwy", "role": "Viewer", "dept_id": None},
]


def upgrade() -> None:
    op.create_table(
        "app_users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(50), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("dept_id", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username"),
    )
    op.create_index("idx_app_users_username", "app_users", ["username"])
    op.create_index("idx_app_users_role", "app_users", ["role"])

    # Seed demo users with pre-computed hashes
    for user in DEMO_USERS:
        op.execute(
            f"INSERT INTO app_users (username, password_hash, role, dept_id) "
            f"VALUES ('{user['username']}', '{user['password_hash']}', '{user['role']}', "
            f"{user['dept_id'] if user['dept_id'] else 'NULL'})"
        )


def downgrade() -> None:
    op.drop_index("idx_app_users_role", "app_users")
    op.drop_index("idx_app_users_username", "app_users")
    op.drop_table("app_users")
