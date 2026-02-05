"""add organization_id to members

Revision ID: 202602051700
Revises: fc8d9e3b2a1c
Create Date: 2026-02-05 17:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '202602051700'
down_revision: Union[str, None] = 'fc8d9e3b2a1c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add organization_id column to members table
    op.add_column('members', sa.Column(
        'organization_id', sa.String(36), nullable=True))
    op.create_foreign_key(
        'fk_members_organization_id',
        'members', 'organizations',
        ['organization_id'], ['id']
    )
    op.create_index('ix_members_organization_id',
                    'members', ['organization_id'])


def downgrade() -> None:
    op.drop_index('ix_members_organization_id', 'members')
    op.drop_constraint('fk_members_organization_id',
                       'members', type_='foreignkey')
    op.drop_column('members', 'organization_id')
