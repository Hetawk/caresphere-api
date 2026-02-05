"""Add field configuration tables

Revision ID: fc8d9e3b2a1c
Revises: aa95265e1c0c
Create Date: 2025-11-21

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'fc8d9e3b2a1c'
down_revision = 'aa95265e1c0c'
branch_labels = None
depends_on = None


def upgrade():
    # Create field_configurations table
    op.create_table('field_configurations',
                    sa.Column('id', sa.String(length=36), nullable=False),
                    sa.Column('created_at', sa.DateTime(timezone=True),
                              server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
                    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text(
                        'CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False),
                    sa.Column('organization_id', sa.String(
                        length=36), nullable=False),
                    sa.Column('entity_type', sa.Enum('MEMBER', 'MESSAGE', 'EVENT',
                                                     'DONATION', 'VOLUNTEER', name='entitytype'), nullable=False),
                    sa.Column('field_key', sa.String(
                        length=100), nullable=False),
                    sa.Column('field_label', sa.String(
                        length=200), nullable=False),
                    sa.Column('field_type', sa.Enum('TEXT', 'EMAIL', 'PHONE', 'NUMBER', 'DATE', 'SELECT',
                                                    'MULTISELECT', 'CHECKBOX', 'TEXTAREA', 'URL', 'FILE', name='fieldtype'), nullable=False),
                    sa.Column('description', sa.Text(), nullable=True),
                    sa.Column('placeholder', sa.String(
                        length=200), nullable=True),
                    sa.Column('options', sa.JSON(), nullable=True),
                    sa.Column('validation_rules', sa.JSON(), nullable=True),
                    sa.Column('is_required', sa.Boolean(),
                              nullable=True, default=False),
                    sa.Column('is_visible', sa.Boolean(),
                              nullable=True, default=True),
                    sa.Column('is_searchable', sa.Boolean(),
                              nullable=True, default=False),
                    sa.Column('display_order', sa.Integer(),
                              nullable=True, default=0),
                    sa.Column('default_value', sa.String(
                        length=500), nullable=True),
                    sa.Column('group_name', sa.String(
                        length=100), nullable=True),
                    sa.ForeignKeyConstraint(['organization_id'], [
                                            'organizations.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index(op.f('ix_field_configurations_organization_id'),
                    'field_configurations', ['organization_id'], unique=False)
    op.create_index(op.f('ix_field_configurations_entity_type'),
                    'field_configurations', ['entity_type'], unique=False)

    # Create field_values table
    op.create_table('field_values',
                    sa.Column('id', sa.String(length=36), nullable=False),
                    sa.Column('created_at', sa.DateTime(timezone=True),
                              server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
                    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text(
                        'CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False),
                    sa.Column('field_configuration_id',
                              sa.String(length=36), nullable=False),
                    sa.Column('entity_type', sa.Enum('MEMBER', 'MESSAGE', 'EVENT',
                                                     'DONATION', 'VOLUNTEER', name='entitytype'), nullable=False),
                    sa.Column('entity_id', sa.String(
                        length=36), nullable=False),
                    sa.Column('value', sa.Text(), nullable=True),
                    sa.ForeignKeyConstraint(['field_configuration_id'], [
                        'field_configurations.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index(op.f('ix_field_values_field_configuration_id'),
                    'field_values', ['field_configuration_id'], unique=False)
    op.create_index(op.f('ix_field_values_entity_type'),
                    'field_values', ['entity_type'], unique=False)
    op.create_index(op.f('ix_field_values_entity_id'),
                    'field_values', ['entity_id'], unique=False)

    # Add member CSV fields for backward compatibility
    op.add_column('members', sa.Column(
        'work_school', sa.String(length=200), nullable=True))
    op.add_column('members', sa.Column('whatsapp_number',
                  sa.String(length=20), nullable=True))
    op.add_column('members', sa.Column(
        'wechat_id', sa.String(length=100), nullable=True))
    op.add_column('members', sa.Column(
        'hear_about_us', sa.Text(), nullable=True))
    op.add_column('members', sa.Column(
        'involvement', sa.Text(), nullable=True))
    op.add_column('members', sa.Column('comments', sa.Text(), nullable=True))
    op.add_column('members', sa.Column('consent_given',
                  sa.Boolean(), nullable=True, default=False))


def downgrade():
    # Drop member CSV fields
    op.drop_column('members', 'consent_given')
    op.drop_column('members', 'comments')
    op.drop_column('members', 'involvement')
    op.drop_column('members', 'hear_about_us')
    op.drop_column('members', 'wechat_id')
    op.drop_column('members', 'whatsapp_number')
    op.drop_column('members', 'work_school')

    # Drop field_values table
    op.drop_index(op.f('ix_field_values_entity_id'), table_name='field_values')
    op.drop_index(op.f('ix_field_values_entity_type'),
                  table_name='field_values')
    op.drop_index(op.f('ix_field_values_field_configuration_id'),
                  table_name='field_values')
    op.drop_table('field_values')

    # Drop field_configurations table
    op.drop_index(op.f('ix_field_configurations_entity_type'),
                  table_name='field_configurations')
    op.drop_index(op.f('ix_field_configurations_organization_id'),
                  table_name='field_configurations')
    op.drop_table('field_configurations')
