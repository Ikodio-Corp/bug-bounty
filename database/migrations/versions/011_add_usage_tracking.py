"""add usage tracking and update subscription tiers

Revision ID: 11
Revises: 10
Create Date: 2025-11-24 14:50:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from datetime import datetime

# revision identifiers, used by Alembic.
revision = '11'
down_revision = '10'
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
    op.execute("CREATE TYPE subscriptiontier_new AS ENUM ('FREE', 'PROFESSIONAL', 'BUSINESS', 'ENTERPRISE', 'GOVERNMENT')")
    
    # 2. Add temporary column with new enum type
    op.execute("""
        ALTER TABLE users 
        ADD COLUMN subscription_tier_new subscriptiontier_new
    """)
    
    # 3. Migrate data from old to new column
    op.execute("""
        UPDATE users 
        SET subscription_tier_new = 
            CASE subscription_tier::text
                WHEN 'BRONZE' THEN 'PROFESSIONAL'::subscriptiontier_new
                WHEN 'SILVER' THEN 'BUSINESS'::subscriptiontier_new
                WHEN 'GOLD' THEN 'ENTERPRISE'::subscriptiontier_new
                WHEN 'PLATINUM' THEN 'GOVERNMENT'::subscriptiontier_new
                WHEN 'FREE' THEN 'FREE'::subscriptiontier_new
                WHEN 'PROFESSIONAL' THEN 'PROFESSIONAL'::subscriptiontier_new
                WHEN 'BUSINESS' THEN 'BUSINESS'::subscriptiontier_new
                WHEN 'ENTERPRISE' THEN 'ENTERPRISE'::subscriptiontier_new
                WHEN 'GOVERNMENT' THEN 'GOVERNMENT'::subscriptiontier_new
                ELSE 'FREE'::subscriptiontier_new
            END
    """)
    
    # 4. Drop old column and rename new column
    op.execute("ALTER TABLE users DROP COLUMN subscription_tier")
    op.execute("ALTER TABLE users RENAME COLUMN subscription_tier_new TO subscription_tier")
    
    # 5. Drop old enum type
    op.execute("DROP TYPE IF EXISTS subscriptiontier CASCADE")
    
    # 6. Rename new enum type
    op.execute("ALTER TYPE subscriptiontier_new RENAME TO subscriptiontier")
    
    # 7. Set default value
    op.execute("ALTER TABLE users ALTER COLUMN subscription_tier SET DEFAULT 'FREE'::subscriptiontier")
    
    # 8. Create scan_usage table
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
    
    # 9. Create autofix_usage table
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
    
    # 10. Create api_usage table
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
    
    # 11. Create storage_usage table
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
    
    # 12. Create trigger function to auto-update updated_at timestamps
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ language 'plpgsql';
    """)
    
    # 13. Apply triggers to all usage tables
    for table in ['scan_usage', 'autofix_usage', 'api_usage', 'storage_usage']:
        op.execute(f"""
            CREATE TRIGGER update_{table}_updated_at 
            BEFORE UPDATE ON {table}
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
        """)
    
    print(" Migration 011 complete:")
    print("  - Updated subscription tier enum (FREE, PROFESSIONAL, BUSINESS, ENTERPRISE, GOVERNMENT)")
    print("  - Migrated existing users to new tier names")
    print("  - Created 4 usage tracking tables (scan_usage, autofix_usage, api_usage, storage_usage)")
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
    
    # 3. Revert subscription tier enum (with data loss warning)
    # Create old enum
    op.execute("CREATE TYPE subscriptiontier_old AS ENUM ('FREE', 'BRONZE', 'SILVER', 'GOLD', 'PLATINUM')")
    
    # Add temporary column
    op.execute("ALTER TABLE users ADD COLUMN subscription_tier_old subscriptiontier_old")
    
    # Migrate data back (THIS WILL LOSE DATA for PROFESSIONAL/BUSINESS/ENTERPRISE/GOVERNMENT users!)
    op.execute("""
        UPDATE users 
        SET subscription_tier_old = 
            CASE subscription_tier::text
                WHEN 'PROFESSIONAL' THEN 'BRONZE'::subscriptiontier_old
                WHEN 'BUSINESS' THEN 'SILVER'::subscriptiontier_old
                WHEN 'ENTERPRISE' THEN 'GOLD'::subscriptiontier_old
                WHEN 'GOVERNMENT' THEN 'PLATINUM'::subscriptiontier_old
                WHEN 'FREE' THEN 'FREE'::subscriptiontier_old
                ELSE 'FREE'::subscriptiontier_old
            END
    """)
    
    # Drop new column and rename old column
    op.execute("ALTER TABLE users DROP COLUMN subscription_tier")
    op.execute("ALTER TABLE users RENAME COLUMN subscription_tier_old TO subscription_tier")
    
    # Drop new enum
    op.execute("DROP TYPE IF EXISTS subscriptiontier CASCADE")
    
    # Rename old enum
    op.execute("ALTER TYPE subscriptiontier_old RENAME TO subscriptiontier")
    
    # Set default
    op.execute("ALTER TABLE users ALTER COLUMN subscription_tier SET DEFAULT 'FREE'::subscriptiontier")
    
    print("  Migration 011 rolled back:")
    print("  - Deleted usage tracking tables")
    print("  - Reverted subscription tier enum")
    print("  -   WARNING: Users with PROFESSIONAL/BUSINESS/ENTERPRISE/GOVERNMENT tiers were downgraded!")
