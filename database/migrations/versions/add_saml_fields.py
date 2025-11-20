"""Add SAML fields to users table

Revision ID: add_saml_fields
Revises: add_validation_tracking
Create Date: 2025-11-20

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'add_saml_fields'
down_revision = 'add_validation_tracking'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('saml_name_id', sa.String(length=500), nullable=True))
    op.add_column('users', sa.Column('saml_idp', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('saml_idp_configs', sa.JSON(), nullable=True))
    op.add_column('users', sa.Column('saml_session_index', sa.String(length=500), nullable=True))
    
    op.create_index('idx_users_saml_name_id', 'users', ['saml_name_id'])
    op.create_index('idx_users_saml_idp', 'users', ['saml_idp'])


def downgrade():
    op.drop_index('idx_users_saml_idp', table_name='users')
    op.drop_index('idx_users_saml_name_id', table_name='users')
    
    op.drop_column('users', 'saml_session_index')
    op.drop_column('users', 'saml_idp_configs')
    op.drop_column('users', 'saml_idp', )
    op.drop_column('users', 'saml_name_id')
