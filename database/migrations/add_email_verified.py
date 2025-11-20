"""add email_verified field

Revision ID: add_email_verified
Revises: 
Create Date: 2025-11-18

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_email_verified'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Add email_verified column to users table
    op.add_column('users', sa.Column('email_verified', sa.Boolean(), nullable=True, server_default='false'))


def downgrade():
    # Remove email_verified column
    op.drop_column('users', 'email_verified')
