"""
Add usage tracking tables and update subscription tiers

Revision ID: add_usage_tracking
Create Date: 2025-01-XX XX:XX:XX.XXXXXX
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic
revision = 'add_usage_tracking'
down_revision = None  # Update this with your last migration ID
branch_labels = None
depends_on = None


def upgrade():
    """
    Upgrade database schema:
    1. Update subscription tier enum
    2. Migrate existing users to new tier names
    3. Create usage tracking tables
    4. Create indexes
    """
    
    # 1. Create new subscription tier enum
    new_tier_enum = postgresql.ENUM(
        'FREE', 'PROFESSIONAL', 'BUSINESS', 'ENTERPRISE', 'GOVERNMENT',
        name='subscriptiontier_new'
    )
    new_tier_enum.create(op.get_bind(), checkfirst=False)
    
    # 2. Migrate existing users to new tier names
    op.execute("""
        UPDATE users 
        SET subscription_tier = 
            CASE subscription_tier::text
                WHEN 'BRONZE' THEN 'PROFESSIONAL'
                WHEN 'SILVER' THEN 'BUSINESS'
                WHEN 'GOLD' THEN 'ENTERPRISE'
                WHEN 'PLATINUM' THEN 'GOVERNMENT'
                ELSE subscription_tier::text
            END::subscriptiontier_new
    """)
    
    # 3. Drop old enum and rename new one
    op.execute('ALTER TABLE users ALTER COLUMN subscription_tier TYPE subscriptiontier_new USING subscription_tier::text::subscriptiontier_new')
    op.execute('DROP TYPE IF EXISTS subscriptiontier CASCADE')
    op.execute('ALTER TYPE subscriptiontier_new RENAME TO subscriptiontier')
    
    # 4. Create scan_usage table
    op.create_table(
        'scan_usage',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('month', sa.String(length=7), nullable=False),  # YYYY-MM format
        sa.Column('scan_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('limit', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'month', name='uq_scan_usage_user_month')
    )
    
    # Create indexes for scan_usage
    op.create_index('idx_scan_usage_user_id', 'scan_usage', ['user_id'])
    op.create_index('idx_scan_usage_month', 'scan_usage', ['month'])
    op.create_index('idx_scan_usage_user_month', 'scan_usage', ['user_id', 'month'])
    
    # 5. Create autofix_usage table
    op.create_table(
        'autofix_usage',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('month', sa.String(length=7), nullable=False),
        sa.Column('fix_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('limit', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'month', name='uq_autofix_usage_user_month')
    )
    
    # Create indexes for autofix_usage
    op.create_index('idx_autofix_usage_user_id', 'autofix_usage', ['user_id'])
    op.create_index('idx_autofix_usage_month', 'autofix_usage', ['month'])
    op.create_index('idx_autofix_usage_user_month', 'autofix_usage', ['user_id', 'month'])
    
    # 6. Create api_usage table
    op.create_table(
        'api_usage',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('month', sa.String(length=7), nullable=False),
        sa.Column('request_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('limit', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'month', name='uq_api_usage_user_month')
    )
    
    # Create indexes for api_usage
    op.create_index('idx_api_usage_user_id', 'api_usage', ['user_id'])
    op.create_index('idx_api_usage_month', 'api_usage', ['month'])
    op.create_index('idx_api_usage_user_month', 'api_usage', ['user_id', 'month'])
    
    # 7. Create storage_usage table
    op.create_table(
        'storage_usage',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('bytes_used', sa.BigInteger(), nullable=False, server_default='0'),
        sa.Column('bytes_limit', sa.BigInteger(), nullable=True),
        sa.Column('retention_days', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', name='uq_storage_usage_user')
    )
    
    # Create indexes for storage_usage
    op.create_index('idx_storage_usage_user_id', 'storage_usage', ['user_id'])
    
    # 8. Create trigger to auto-update updated_at timestamps
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ language 'plpgsql';
    """)
    
    # Apply triggers to all usage tables
    for table in ['scan_usage', 'autofix_usage', 'api_usage', 'storage_usage']:
        op.execute(f"""
            CREATE TRIGGER update_{table}_updated_at 
            BEFORE UPDATE ON {table}
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
        """)
    
    print(" Migration complete:")
    print("  - Updated subscription tier enum")
    print("  - Migrated existing users to new tier names")
    print("  - Created 4 usage tracking tables")
    print("  - Created indexes for performance")
    print("  - Created auto-update triggers")


def downgrade():
    """
    Downgrade database schema (rollback changes)
    """
    
    # 1. Drop triggers
    for table in ['scan_usage', 'autofix_usage', 'api_usage', 'storage_usage']:
        op.execute(f'DROP TRIGGER IF EXISTS update_{table}_updated_at ON {table}')
    
    op.execute('DROP FUNCTION IF EXISTS update_updated_at_column()')
    
    # 2. Drop usage tables (indexes will be dropped automatically)
    op.drop_table('storage_usage')
    op.drop_table('api_usage')
    op.drop_table('autofix_usage')
    op.drop_table('scan_usage')
    
    # 3. Revert subscription tier enum (optional - data loss!)
    # Note: This will fail if you have PROFESSIONAL/BUSINESS/ENTERPRISE/GOVERNMENT users
    # Only run this if you're absolutely sure you want to revert
    
    old_tier_enum = postgresql.ENUM(
        'FREE', 'BRONZE', 'SILVER', 'GOLD', 'PLATINUM',
        name='subscriptiontier_old'
    )
    old_tier_enum.create(op.get_bind(), checkfirst=False)
    
    # Revert tier names (this will LOSE data for users with new tier names!)
    op.execute("""
        UPDATE users 
        SET subscription_tier = 
            CASE subscription_tier::text
                WHEN 'PROFESSIONAL' THEN 'BRONZE'
                WHEN 'BUSINESS' THEN 'SILVER'
                WHEN 'ENTERPRISE' THEN 'GOLD'
                WHEN 'GOVERNMENT' THEN 'PLATINUM'
                ELSE subscription_tier::text
            END::subscriptiontier_old
    """)
    
    # Drop new enum and rename old one
    op.execute('ALTER TABLE users ALTER COLUMN subscription_tier TYPE subscriptiontier_old USING subscription_tier::text::subscriptiontier_old')
    op.execute('DROP TYPE IF EXISTS subscriptiontier CASCADE')
    op.execute('ALTER TYPE subscriptiontier_old RENAME TO subscriptiontier')
    
    print("  Migration rolled back:")
    print("  - Deleted usage tracking tables")
    print("  - Reverted subscription tier enum")
    print("  -   WARNING: Users with PROFESSIONAL/BUSINESS/ENTERPRISE/GOVERNMENT tiers were downgraded!")
