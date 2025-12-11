"""
Database migration: Update hunter_rank column
"""

from alembic import op
import sqlalchemy as sa


revision = '006_update_hunter_rank'
down_revision = '005_add_gdpr_fields'
branch_labels = None
depends_on = None


def upgrade():
    """Upgrade database schema"""
    # Update hunter_rank column to String
    with op.batch_alter_table('users') as batch_op:
        batch_op.alter_column(
            'hunter_rank',
            existing_type=sa.Integer(),
            type_=sa.String(50),
            existing_nullable=True
        )
    
    # Set default value for existing records
    op.execute("UPDATE users SET hunter_rank = 'bronze' WHERE hunter_rank IS NULL")


def downgrade():
    """Downgrade database schema"""
    # Revert hunter_rank column to Integer
    with op.batch_alter_table('users') as batch_op:
        batch_op.alter_column(
            'hunter_rank',
            existing_type=sa.String(50),
            type_=sa.Integer(),
            existing_nullable=True
        )

    