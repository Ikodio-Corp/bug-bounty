"""add report model

Revision ID: 10
Revises: 9
Create Date: 2025-11-20 07:10:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '10'
down_revision = '9'
branch_labels = None
depends_on = None


def upgrade():
    # Create reports table
    op.create_table(
        'reports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('type', sa.String(50), nullable=False),  # security, vulnerability, compliance, scan
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('status', sa.String(50), default='generating'),  # generating, ready, failed
        sa.Column('format', sa.String(20), default='pdf'),  # pdf, csv, json
        sa.Column('date_range_days', sa.Integer(), nullable=False),
        sa.Column('file_path', sa.String(500), nullable=True),
        sa.Column('file_size', sa.BigInteger(), nullable=True),
        sa.Column('data', postgresql.JSONB(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('download_count', sa.Integer(), default=0),
        sa.Column('generated_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), onupdate=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )
    
    # Create indexes
    op.create_index('ix_reports_user_id', 'reports', ['user_id'])
    op.create_index('ix_reports_type', 'reports', ['type'])
    op.create_index('ix_reports_status', 'reports', ['status'])
    op.create_index('ix_reports_created_at', 'reports', ['created_at'])


def downgrade():
    op.drop_index('ix_reports_created_at')
    op.drop_index('ix_reports_status')
    op.drop_index('ix_reports_type')
    op.drop_index('ix_reports_user_id')
    op.drop_table('reports')
