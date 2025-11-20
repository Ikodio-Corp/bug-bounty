"""
Add OAuth, 2FA, and Payment fields to users

Revision ID: add_auth_payment_fields
Revises: revolutionary_001_initial
Create Date: 2025-11-20 14:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON

# revision identifiers
revision = 'add_auth_payment_fields'
down_revision = 'revolutionary_001_initial'
branch_labels = None
depends_on = None


def upgrade():
    """
    Add OAuth2/SSO, 2FA, and Payment fields to users table
    """
    # Add OAuth/SSO fields
    op.add_column('users', sa.Column('oauth_provider', sa.String(50), nullable=True))
    op.add_column('users', sa.Column('oauth_id', sa.String(255), nullable=True))
    
    # Add 2FA fields
    op.add_column('users', sa.Column('two_factor_enabled', sa.Boolean(), default=False))
    op.add_column('users', sa.Column('two_factor_secret', sa.String(255), nullable=True))
    op.add_column('users', sa.Column('backup_codes', JSON, nullable=True))
    op.add_column('users', sa.Column('webauthn_credentials', JSON, nullable=True))
    
    # Add Payment/Subscription fields
    op.add_column('users', sa.Column('stripe_customer_id', sa.String(255), nullable=True))
    op.add_column('users', sa.Column('stripe_subscription_id', sa.String(255), nullable=True))
    op.add_column('users', sa.Column('subscription_status', sa.String(50), nullable=True))
    op.add_column('users', sa.Column('subscription_period_end', sa.DateTime(), nullable=True))
    
    # Create indexes for performance
    op.create_index('idx_users_oauth_provider', 'users', ['oauth_provider'])
    op.create_index('idx_users_oauth_id', 'users', ['oauth_id'])
    op.create_index('idx_users_stripe_customer', 'users', ['stripe_customer_id'])
    op.create_index('idx_users_stripe_subscription', 'users', ['stripe_subscription_id'])


def downgrade():
    """
    Remove OAuth2/SSO, 2FA, and Payment fields
    """
    # Drop indexes
    op.drop_index('idx_users_stripe_subscription', 'users')
    op.drop_index('idx_users_stripe_customer', 'users')
    op.drop_index('idx_users_oauth_id', 'users')
    op.drop_index('idx_users_oauth_provider', 'users')
    
    # Drop Payment fields
    op.drop_column('users', 'subscription_period_end')
    op.drop_column('users', 'subscription_status')
    op.drop_column('users', 'stripe_subscription_id')
    op.drop_column('users', 'stripe_customer_id')
    
    # Drop 2FA fields
    op.drop_column('users', 'webauthn_credentials')
    op.drop_column('users', 'backup_codes')
    op.drop_column('users', 'two_factor_secret')
    op.drop_column('users', 'two_factor_enabled')
    
    # Drop OAuth fields
    op.drop_column('users', 'oauth_id')
    op.drop_column('users', 'oauth_provider')
