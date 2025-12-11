"""Add GDPR compliance fields to users table

Revision ID: 005_add_gdpr_fields
Revises: revolutionary_001
Create Date: 2024-01-20 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '005_add_gdpr_fields'
down_revision = 'revolutionary_001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add GDPR consent and account deletion fields"""
    
    # Add consent fields
    op.add_column('users', sa.Column('consent_marketing', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('users', sa.Column('consent_analytics', sa.Boolean(), nullable=False, server_default='true'))
    op.add_column('users', sa.Column('consent_third_party', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('users', sa.Column('consent_profiling', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('users', sa.Column('consent_automated_decision', sa.Boolean(), nullable=False, server_default='true'))
    op.add_column('users', sa.Column('consent_updated_at', sa.DateTime(), nullable=True))
    
    # Add account deletion fields
    op.add_column('users', sa.Column('deletion_requested_at', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('deletion_scheduled_at', sa.DateTime(), nullable=True))
    
    # Create indexes for frequently queried fields
    op.create_index('idx_users_deletion_scheduled', 'users', ['deletion_scheduled_at'], 
                   postgresql_where=sa.text('deletion_scheduled_at IS NOT NULL'))


def downgrade() -> None:
    """Remove GDPR fields"""
    
    # Drop indexes
    op.drop_index('idx_users_deletion_scheduled', table_name='users')
    
    # Drop columns
    op.drop_column('users', 'deletion_scheduled_at')
    op.drop_column('users', 'deletion_requested_at')
    op.drop_column('users', 'consent_updated_at')
    op.drop_column('users', 'consent_automated_decision')
    op.drop_column('users', 'consent_profiling')
    op.drop_column('users', 'consent_third_party')
    op.drop_column('users', 'consent_analytics')
    op.drop_column('users', 'consent_marketing')
