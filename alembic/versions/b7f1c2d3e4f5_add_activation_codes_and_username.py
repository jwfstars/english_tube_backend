"""add activation codes and username

Revision ID: b7f1c2d3e4f5
Revises: 9d7e5c1a4f11
Create Date: 2025-12-29 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "b7f1c2d3e4f5"
down_revision: Union[str, None] = "9d7e5c1a4f11"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("username", sa.String(length=64), nullable=True))
    op.create_index("ix_users_username", "users", ["username"], unique=True)

    op.create_table(
        "activation_codes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("is_used", sa.Boolean(), nullable=True),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("used_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["used_by_user_id"], ["users.id"]),
    )
    op.create_index("ix_activation_codes_code", "activation_codes", ["code"], unique=True)

    op.create_table(
        "activation_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("token", sa.String(length=128), nullable=False),
        sa.Column("code_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("is_used", sa.Boolean(), nullable=True),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["code_id"], ["activation_codes.id"]),
    )
    op.create_index("ix_activation_sessions_token", "activation_sessions", ["token"], unique=True)
    op.create_index("ix_activation_sessions_code_id", "activation_sessions", ["code_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_activation_sessions_code_id", table_name="activation_sessions")
    op.drop_index("ix_activation_sessions_token", table_name="activation_sessions")
    op.drop_table("activation_sessions")
    op.drop_index("ix_activation_codes_code", table_name="activation_codes")
    op.drop_table("activation_codes")
    op.drop_index("ix_users_username", table_name="users")
    op.drop_column("users", "username")
