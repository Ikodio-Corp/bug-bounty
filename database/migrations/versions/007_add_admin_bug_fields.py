"""
"""Migration to add admin fields to bugs table

Revision ID: 7
Revises: 006_update_hunter_rank
Create Date: 2025-01-20
"""

from alembic import op
import sqlalchemy as sa


revision = '7'
down_revision = '006_update_hunter_rank'
branch_labels = None
depends_on = None


def upgrade():
    # Add validated column
    op.add_column('bugs', sa.Column('validated', sa.Boolean(), default=False, nullable=True))
    
    # Add paid_out column
    op.add_column('bugs', sa.Column('paid_out', sa.Boolean(), default=False, nullable=True))
    
    # Add rejection_reason column
    op.add_column('bugs', sa.Column('rejection_reason', sa.Text(), nullable=True))
    
    # Set existing bugs to validated=False and paid_out=False
    op.execute("UPDATE bugs SET validated = false WHERE validated IS NULL")
    op.execute("UPDATE bugs SET paid_out = false WHERE paid_out IS NULL")


def downgrade():
    op.drop_column('bugs', 'rejection_reason')
    op.drop_column('bugs', 'paid_out')
    op.drop_column('bugs', 'validated')
