"""add_password_reset_fields

Revision ID: aa95265e1c0c
Revises: a8da5977f3ad
Create Date: 2025-11-21 09:22:49.036159

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'aa95265e1c0c'
down_revision: Union[str, None] = 'a8da5977f3ad'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add password reset fields
    op.add_column('users', sa.Column('reset_token_hash', sa.String(255), nullable=True))
    op.add_column('users', sa.Column('reset_token_expires', sa.DateTime(timezone=True), nullable=True))
    op.add_column('users', sa.Column('verification_token_hash', sa.String(255), nullable=True))


def downgrade() -> None:
    # Remove password reset fields
    op.drop_column('users', 'verification_token_hash')
    op.drop_column('users', 'reset_token_expires')
    op.drop_column('users', 'reset_token_hash')
