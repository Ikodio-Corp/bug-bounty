"""add validation and issue tracking fields

Revision ID: add_validation_tracking
Revises: add_auth_payment_fields
Create Date: 2024-01-15 10:00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_validation_tracking'
down_revision = 'add_auth_payment_fields'
branch_labels = None
depends_on = None


def upgrade():
    # Add validation workflow fields to bugs table
    op.add_column('bugs', sa.Column('reviewer_id', sa.Integer(), nullable=True))
    op.add_column('bugs', sa.Column('validation_submitted_at', sa.DateTime(), nullable=True))
    op.add_column('bugs', sa.Column('validation_assigned_at', sa.DateTime(), nullable=True))
    op.add_column('bugs', sa.Column('validated_at', sa.DateTime(), nullable=True))
    op.add_column('bugs', sa.Column('rejected_at', sa.DateTime(), nullable=True))
    op.add_column('bugs', sa.Column('validation_comments', sa.Text(), nullable=True))
    op.add_column('bugs', sa.Column('appeal_reason', sa.Text(), nullable=True))
    op.add_column('bugs', sa.Column('appeal_submitted_at', sa.DateTime(), nullable=True))
    
    # Add duplicate detection fields to bugs table
    op.add_column('bugs', sa.Column('duplicate_of_id', sa.Integer(), nullable=True))
    op.add_column('bugs', sa.Column('duplicate_marked_at', sa.DateTime(), nullable=True))
    op.add_column('bugs', sa.Column('duplicate_reason', sa.Text(), nullable=True))
    
    # Add issue tracking integration fields to bugs table
    op.add_column('bugs', sa.Column('jira_issue_key', sa.String(255), nullable=True))
    op.add_column('bugs', sa.Column('jira_issue_id', sa.String(255), nullable=True))
    op.add_column('bugs', sa.Column('synced_to_jira_at', sa.DateTime(), nullable=True))
    op.add_column('bugs', sa.Column('linear_issue_id', sa.String(255), nullable=True))
    op.add_column('bugs', sa.Column('linear_issue_identifier', sa.String(255), nullable=True))
    op.add_column('bugs', sa.Column('synced_to_linear_at', sa.DateTime(), nullable=True))
    op.add_column('bugs', sa.Column('asana_task_id', sa.String(255), nullable=True))
    op.add_column('bugs', sa.Column('synced_to_asana_at', sa.DateTime(), nullable=True))
    op.add_column('bugs', sa.Column('monday_item_id', sa.String(255), nullable=True))
    op.add_column('bugs', sa.Column('synced_to_monday_at', sa.DateTime(), nullable=True))
    
    # Add foreign keys
    op.create_foreign_key('fk_bugs_reviewer_id', 'bugs', 'users', ['reviewer_id'], ['id'])
    op.create_foreign_key('fk_bugs_duplicate_of_id', 'bugs', 'bugs', ['duplicate_of_id'], ['id'])
    
    # Add issue tracking configuration fields to users table
    op.add_column('users', sa.Column('jira_url', sa.String(500), nullable=True))
    op.add_column('users', sa.Column('jira_token', sa.String(500), nullable=True))
    op.add_column('users', sa.Column('jira_email', sa.String(255), nullable=True))
    op.add_column('users', sa.Column('linear_token', sa.String(500), nullable=True))
    op.add_column('users', sa.Column('asana_token', sa.String(500), nullable=True))
    op.add_column('users', sa.Column('monday_token', sa.String(500), nullable=True))
    
    # Add bug bounty platform fields to users table
    op.add_column('users', sa.Column('hackerone_username', sa.String(255), nullable=True))
    op.add_column('users', sa.Column('hackerone_token', sa.String(500), nullable=True))
    op.add_column('users', sa.Column('bugcrowd_token', sa.String(500), nullable=True))
    op.add_column('users', sa.Column('intigriti_token', sa.String(500), nullable=True))
    op.add_column('users', sa.Column('yeswehack_token', sa.String(500), nullable=True))
    
    # Add cloud provider credentials to users table
    op.add_column('users', sa.Column('aws_access_key_id', sa.String(255), nullable=True))
    op.add_column('users', sa.Column('aws_secret_access_key', sa.String(500), nullable=True))
    op.add_column('users', sa.Column('aws_region', sa.String(50), nullable=True))
    op.add_column('users', sa.Column('aws_account_id', sa.String(100), nullable=True))
    op.add_column('users', sa.Column('gcp_project_id', sa.String(255), nullable=True))
    op.add_column('users', sa.Column('gcp_organization_id', sa.String(255), nullable=True))
    op.add_column('users', sa.Column('gcp_service_account_key', sa.JSON(), nullable=True))
    op.add_column('users', sa.Column('azure_tenant_id', sa.String(255), nullable=True))
    op.add_column('users', sa.Column('azure_client_id', sa.String(255), nullable=True))
    op.add_column('users', sa.Column('azure_client_secret', sa.String(500), nullable=True))
    op.add_column('users', sa.Column('azure_subscription_id', sa.String(255), nullable=True))
    
    # Add cloud provider fields to bugs table
    op.add_column('bugs', sa.Column('cloud_provider', sa.String(50), nullable=True))
    op.add_column('bugs', sa.Column('cloud_finding_id', sa.String(255), nullable=True))
    op.add_column('bugs', sa.Column('cloud_finding_arn', sa.String(500), nullable=True))
    op.add_column('bugs', sa.Column('imported_at', sa.DateTime(), nullable=True))
    op.add_column('bugs', sa.Column('exported_at', sa.DateTime(), nullable=True))
    
    # Create indexes for performance
    op.create_index('ix_bugs_reviewer_id', 'bugs', ['reviewer_id'])
    op.create_index('ix_bugs_duplicate_of_id', 'bugs', ['duplicate_of_id'])
    op.create_index('ix_bugs_jira_issue_key', 'bugs', ['jira_issue_key'])
    op.create_index('ix_bugs_linear_issue_id', 'bugs', ['linear_issue_id'])


def downgrade():
    # Drop indexes
    op.drop_index('ix_bugs_linear_issue_id', table_name='bugs')
    op.drop_index('ix_bugs_jira_issue_key', table_name='bugs')
    op.drop_index('ix_bugs_duplicate_of_id', table_name='bugs')
    op.drop_index('ix_bugs_reviewer_id', table_name='bugs')
    
    # Drop foreign keys
    op.drop_constraint('fk_bugs_duplicate_of_id', 'bugs', type_='foreignkey')
    op.drop_constraint('fk_bugs_reviewer_id', 'bugs', type_='foreignkey')
    
    # Remove cloud provider fields from bugs table
    op.drop_column('bugs', 'exported_at')
    op.drop_column('bugs', 'imported_at')
    op.drop_column('bugs', 'cloud_finding_arn')
    op.drop_column('bugs', 'cloud_finding_id')
    op.drop_column('bugs', 'cloud_provider')
    
    # Remove cloud provider credentials from users table
    op.drop_column('users', 'azure_subscription_id')
    op.drop_column('users', 'azure_client_secret')
    op.drop_column('users', 'azure_client_id')
    op.drop_column('users', 'azure_tenant_id')
    op.drop_column('users', 'gcp_service_account_key')
    op.drop_column('users', 'gcp_organization_id')
    op.drop_column('users', 'gcp_project_id')
    op.drop_column('users', 'aws_account_id')
    op.drop_column('users', 'aws_region')
    op.drop_column('users', 'aws_secret_access_key')
    op.drop_column('users', 'aws_access_key_id')
    
    # Remove bug bounty platform fields from users table
    op.drop_column('users', 'yeswehack_token')
    op.drop_column('users', 'intigriti_token')
    op.drop_column('users', 'bugcrowd_token')
    op.drop_column('users', 'hackerone_token')
    op.drop_column('users', 'hackerone_username')
    
    # Remove issue tracking configuration from users table
    op.drop_column('users', 'monday_token')
    op.drop_column('users', 'asana_token')
    op.drop_column('users', 'linear_token')
    op.drop_column('users', 'jira_email')
    op.drop_column('users', 'jira_token')
    op.drop_column('users', 'jira_url')
    
    # Remove issue tracking fields from bugs table
    op.drop_column('bugs', 'synced_to_monday_at')
    op.drop_column('bugs', 'monday_item_id')
    op.drop_column('bugs', 'synced_to_asana_at')
    op.drop_column('bugs', 'asana_task_id')
    op.drop_column('bugs', 'synced_to_linear_at')
    op.drop_column('bugs', 'linear_issue_identifier')
    op.drop_column('bugs', 'linear_issue_id')
    op.drop_column('bugs', 'synced_to_jira_at')
    op.drop_column('bugs', 'jira_issue_id')
    op.drop_column('bugs', 'jira_issue_key')
    
    # Remove duplicate detection fields from bugs table
    op.drop_column('bugs', 'duplicate_reason')
    op.drop_column('bugs', 'duplicate_marked_at')
    op.drop_column('bugs', 'duplicate_of_id')
    
    # Remove validation workflow fields from bugs table
    op.drop_column('bugs', 'appeal_submitted_at')
    op.drop_column('bugs', 'appeal_reason')
    op.drop_column('bugs', 'validation_comments')
    op.drop_column('bugs', 'rejected_at')
    op.drop_column('bugs', 'validated_at')
    op.drop_column('bugs', 'validation_assigned_at')
    op.drop_column('bugs', 'validation_submitted_at')
    op.drop_column('bugs', 'reviewer_id')
