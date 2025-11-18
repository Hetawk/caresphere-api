"""add organizations and sender settings

Revision ID: a8da5977f3ad
Revises: b6d8dccdae32
Create Date: 2025-11-18 12:52:05.812637

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


# revision identifiers, used by Alembic.
revision: str = 'a8da5977f3ad'
down_revision: Union[str, None] = 'b6d8dccdae32'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "organizations",
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=255), nullable=False),
        sa.Column("domain", sa.String(length=255), nullable=True),
        sa.Column("settings", sa.JSON(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column("id", mysql.CHAR(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug", name="uq_organizations_slug"),
    )

    op.add_column(
        "users",
        sa.Column("organization_id", mysql.CHAR(length=36), nullable=True),
    )
    op.create_foreign_key(
        "fk_users_organization",
        "users",
        "organizations",
        ["organization_id"],
        ["id"],
    )

    op.create_table(
        "sender_settings",
        sa.Column("scope", sa.Enum("global", "organization", "user", name="settingscope"), nullable=False),
        sa.Column("reference_id", sa.String(length=36), nullable=True),
        sa.Column("sender_name", sa.String(length=255), nullable=True),
        sa.Column("sender_email", sa.String(length=255), nullable=True),
        sa.Column("sender_phone", sa.String(length=50), nullable=True),
        sa.Column("id", mysql.CHAR(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("scope", "reference_id", name="uq_sender_settings_scope_ref"),
    )


def downgrade() -> None:
    op.drop_table("sender_settings")
    op.drop_constraint("fk_users_organization", "users", type_="foreignkey")
    op.drop_column("users", "organization_id")
    op.drop_table("organizations")
