"""add organization_code to organizations

Revision ID: 202602060001
Revises: 202602051730
Create Date: 2026-02-05 23:15:00

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '202602060001'
down_revision = '202602051730'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add organization_code column to organizations table."""
    # Add the column
    op.add_column(
        'organizations',
        sa.Column('organization_code', sa.String(7), nullable=True)
    )

    # Generate codes for existing organizations using Python
    connection = op.get_bind()
    from random import randint

    # Get all organizations
    result = connection.execute(sa.text("SELECT id FROM organizations"))
    org_ids = [row[0] for row in result]

    # Generate unique codes
    used_codes = set()
    for org_id in org_ids:
        while True:
            code = str(randint(1000000, 9999999))
            if code not in used_codes:
                used_codes.add(code)
                connection.execute(
                    sa.text(
                        "UPDATE organizations SET organization_code = :code WHERE id = :id"),
                    {"code": code, "id": org_id}
                )
                break

    # Make the column non-nullable and unique
    op.alter_column('organizations', 'organization_code', nullable=False)
    op.create_unique_constraint(
        'uq_organization_code', 'organizations', ['organization_code'])
    op.create_index('idx_organization_code',
                    'organizations', ['organization_code'])


def downgrade() -> None:
    """Remove organization_code column."""
    op.drop_index('idx_organization_code', 'organizations')
    op.drop_constraint('uq_organization_code', 'organizations', type_='unique')
    op.drop_column('organizations', 'organization_code')
