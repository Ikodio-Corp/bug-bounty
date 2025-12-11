"""add certificate model

Revision ID: 8
Revises: 7
Create Date: 2025-11-20 07:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '8'
down_revision = '7'
branch_labels = None
depends_on = None


def upgrade():
    # Create certificates table
    op.create_table(
        'certificates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('issuer', sa.String(255), nullable=False),
        sa.Column('type', sa.String(50), nullable=False),  # course, achievement, certification
        sa.Column('issued_at', sa.DateTime(), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('credential_id', sa.String(255), nullable=False, unique=True),
        sa.Column('skills', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('verified', sa.Boolean(), default=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('metadata', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), onupdate=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )
    
    # Create indexes
    op.create_index('ix_certificates_user_id', 'certificates', ['user_id'])
    op.create_index('ix_certificates_type', 'certificates', ['type'])
    op.create_index('ix_certificates_credential_id', 'certificates', ['credential_id'])
    op.create_index('ix_certificates_issued_at', 'certificates', ['issued_at'])


def downgrade():
    op.drop_index('ix_certificates_issued_at')
    op.drop_index('ix_certificates_credential_id')
    op.drop_index('ix_certificates_type')
    op.drop_index('ix_certificates_user_id')
    op.drop_table('certificates')
