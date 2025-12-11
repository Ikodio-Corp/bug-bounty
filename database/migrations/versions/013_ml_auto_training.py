"""
Database Migration: ML Auto-Training and Learning Features

Revision ID: 013_ml_auto_training
Revises: 012_ml_integration
Create Date: 2025-11-25

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '013_ml_auto_training'
down_revision = '012_ml_integration'
branch_labels = None
depends_on = None


def upgrade():
    """Upgrade schema for ML auto-training features"""
    
    # Create ml_training_jobs table
    op.create_table(
        'ml_training_jobs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('job_type', sa.String(length=50), nullable=False),
        sa.Column('model_type', sa.String(length=100), nullable=False),
        sa.Column('training_data_count', sa.Integer(), nullable=True),
        sa.Column('validation_data_count', sa.Integer(), nullable=True),
        sa.Column('config', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('status', sa.Enum('PENDING', 'RUNNING', 'TRAINING', 'EVALUATING', 'COMPLETED', 'FAILED', 'CANCELLED', name='trainingjobstatus'), nullable=True),
        sa.Column('celery_task_id', sa.String(length=255), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('duration_seconds', sa.Integer(), nullable=True),
        sa.Column('result', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('triggered_by_user_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['triggered_by_user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_training_job_status', 'ml_training_jobs', ['status'])
    op.create_index('idx_training_job_type', 'ml_training_jobs', ['job_type'])
    op.create_index('idx_training_job_created', 'ml_training_jobs', ['created_at'])
    op.create_index('idx_training_job_celery', 'ml_training_jobs', ['celery_task_id'])
    
    # Create ml_model_versions table
    op.create_table(
        'ml_model_versions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('model_type', sa.String(length=100), nullable=False),
        sa.Column('version', sa.String(length=50), nullable=False),
        sa.Column('training_job_id', sa.Integer(), nullable=True),
        sa.Column('training_samples', sa.Integer(), nullable=True),
        sa.Column('validation_samples', sa.Integer(), nullable=True),
        sa.Column('training_duration_seconds', sa.Integer(), nullable=True),
        sa.Column('model_path', sa.String(length=500), nullable=True),
        sa.Column('model_size_bytes', sa.Integer(), nullable=True),
        sa.Column('metrics', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('config', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('status', sa.Enum('TRAINING', 'TRAINED', 'TESTING', 'PRODUCTION', 'ARCHIVED', 'FAILED', name='modelversionstatus'), nullable=True),
        sa.Column('is_production', sa.Boolean(), default=False, nullable=True),
        sa.Column('deployed_at', sa.DateTime(), nullable=True),
        sa.Column('replaced_by_version_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('created_by_user_id', sa.Integer(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['training_job_id'], ['ml_training_jobs.id'], ),
        sa.ForeignKeyConstraint(['replaced_by_version_id'], ['ml_model_versions.id'], ),
        sa.ForeignKeyConstraint(['created_by_user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_model_version_type', 'ml_model_versions', ['model_type'])
    op.create_index('idx_model_version_production', 'ml_model_versions', ['is_production'])
    op.create_index('idx_model_version_created', 'ml_model_versions', ['created_at'])
    
    # Create ml_ab_tests table
    op.create_table(
        'ml_ab_tests',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('model_a_version_id', sa.Integer(), nullable=False),
        sa.Column('model_b_version_id', sa.Integer(), nullable=False),
        sa.Column('traffic_split_percentage', sa.Float(), default=50.0, nullable=True),
        sa.Column('start_date', sa.DateTime(), nullable=True),
        sa.Column('end_date', sa.DateTime(), nullable=True),
        sa.Column('status', sa.Enum('DRAFT', 'RUNNING', 'PAUSED', 'COMPLETED', 'CANCELLED', name='abteststatus'), nullable=True),
        sa.Column('model_a_predictions', sa.Integer(), default=0, nullable=True),
        sa.Column('model_b_predictions', sa.Integer(), default=0, nullable=True),
        sa.Column('model_a_metrics', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('model_b_metrics', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('statistical_significance', sa.Float(), nullable=True),
        sa.Column('winner_model_version_id', sa.Integer(), nullable=True),
        sa.Column('winner_determined_at', sa.DateTime(), nullable=True),
        sa.Column('winner_reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('created_by_user_id', sa.Integer(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['model_a_version_id'], ['ml_model_versions.id'], ),
        sa.ForeignKeyConstraint(['model_b_version_id'], ['ml_model_versions.id'], ),
        sa.ForeignKeyConstraint(['winner_model_version_id'], ['ml_model_versions.id'], ),
        sa.ForeignKeyConstraint(['created_by_user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_ab_test_status', 'ml_ab_tests', ['status'])
    op.create_index('idx_ab_test_dates', 'ml_ab_tests', ['start_date', 'end_date'])
    op.create_index('idx_ab_test_created', 'ml_ab_tests', ['created_at'])
    
    # Create ml_ab_test_predictions table
    op.create_table(
        'ml_ab_test_predictions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ab_test_id', sa.Integer(), nullable=False),
        sa.Column('model_version_id', sa.Integer(), nullable=False),
        sa.Column('is_model_a', sa.Boolean(), nullable=False),
        sa.Column('bug_id', sa.Integer(), nullable=True),
        sa.Column('scan_id', sa.Integer(), nullable=True),
        sa.Column('prediction_result', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('latency_ms', sa.Integer(), nullable=True),
        sa.Column('user_feedback', sa.String(length=50), nullable=True),
        sa.Column('actual_outcome', sa.Boolean(), nullable=True),
        sa.Column('predicted_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['ab_test_id'], ['ml_ab_tests.id'], ),
        sa.ForeignKeyConstraint(['model_version_id'], ['ml_model_versions.id'], ),
        sa.ForeignKeyConstraint(['bug_id'], ['bugs.id'], ),
        sa.ForeignKeyConstraint(['scan_id'], ['scans.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_ab_prediction_test', 'ml_ab_test_predictions', ['ab_test_id'])
    op.create_index('idx_ab_prediction_model', 'ml_ab_test_predictions', ['model_version_id'])
    op.create_index('idx_ab_prediction_predicted', 'ml_ab_test_predictions', ['predicted_at'])
    
    # Create ml_model_monitoring table
    op.create_table(
        'ml_model_monitoring',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('model_version_id', sa.Integer(), nullable=False),
        sa.Column('window_start', sa.DateTime(), nullable=False),
        sa.Column('window_end', sa.DateTime(), nullable=False),
        sa.Column('window_size_minutes', sa.Integer(), default=15, nullable=True),
        sa.Column('predictions_count', sa.Integer(), default=0, nullable=True),
        sa.Column('accuracy', sa.Float(), nullable=True),
        sa.Column('precision', sa.Float(), nullable=True),
        sa.Column('recall', sa.Float(), nullable=True),
        sa.Column('f1_score', sa.Float(), nullable=True),
        sa.Column('avg_latency_ms', sa.Float(), nullable=True),
        sa.Column('p50_latency_ms', sa.Float(), nullable=True),
        sa.Column('p95_latency_ms', sa.Float(), nullable=True),
        sa.Column('p99_latency_ms', sa.Float(), nullable=True),
        sa.Column('error_count', sa.Integer(), default=0, nullable=True),
        sa.Column('error_rate', sa.Float(), nullable=True),
        sa.Column('data_drift_score', sa.Float(), nullable=True),
        sa.Column('concept_drift_score', sa.Float(), nullable=True),
        sa.Column('alert_triggered', sa.Boolean(), default=False, nullable=True),
        sa.Column('alert_type', sa.String(length=100), nullable=True),
        sa.Column('alert_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['model_version_id'], ['ml_model_versions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_monitoring_version', 'ml_model_monitoring', ['model_version_id'])
    op.create_index('idx_monitoring_window', 'ml_model_monitoring', ['window_start', 'window_end'])
    op.create_index('idx_monitoring_created', 'ml_model_monitoring', ['created_at'])
    op.create_index('idx_monitoring_alert', 'ml_model_monitoring', ['alert_triggered'])
    
    # Create ml_model_rollbacks table
    op.create_table(
        'ml_model_rollbacks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('from_version_id', sa.Integer(), nullable=False),
        sa.Column('to_version_id', sa.Integer(), nullable=False),
        sa.Column('reason', sa.String(length=100), nullable=False),
        sa.Column('trigger', sa.String(length=50), nullable=True),
        sa.Column('trigger_metrics', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('rolled_back_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('triggered_by_user_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['from_version_id'], ['ml_model_versions.id'], ),
        sa.ForeignKeyConstraint(['to_version_id'], ['ml_model_versions.id'], ),
        sa.ForeignKeyConstraint(['triggered_by_user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_rollback_from', 'ml_model_rollbacks', ['from_version_id'])
    op.create_index('idx_rollback_to', 'ml_model_rollbacks', ['to_version_id'])
    op.create_index('idx_rollback_date', 'ml_model_rollbacks', ['rolled_back_at'])
    
    # Add columns to ml_prediction_feedback for training usage tracking
    op.add_column('ml_prediction_feedback', sa.Column('used_for_training', sa.Boolean(), default=False, nullable=True))
    op.add_column('ml_prediction_feedback', sa.Column('training_processed_at', sa.DateTime(), nullable=True))
    op.create_index('idx_feedback_training', 'ml_prediction_feedback', ['used_for_training'])


def downgrade():
    """Downgrade schema"""
    
    # Drop indexes and columns from ml_prediction_feedback
    op.drop_index('idx_feedback_training', table_name='ml_prediction_feedback')
    op.drop_column('ml_prediction_feedback', 'training_processed_at')
    op.drop_column('ml_prediction_feedback', 'used_for_training')
    
    # Drop ml_model_rollbacks table
    op.drop_index('idx_rollback_date', table_name='ml_model_rollbacks')
    op.drop_index('idx_rollback_to', table_name='ml_model_rollbacks')
    op.drop_index('idx_rollback_from', table_name='ml_model_rollbacks')
    op.drop_table('ml_model_rollbacks')
    
    # Drop ml_model_monitoring table
    op.drop_index('idx_monitoring_alert', table_name='ml_model_monitoring')
    op.drop_index('idx_monitoring_created', table_name='ml_model_monitoring')
    op.drop_index('idx_monitoring_window', table_name='ml_model_monitoring')
    op.drop_index('idx_monitoring_version', table_name='ml_model_monitoring')
    op.drop_table('ml_model_monitoring')
    
    # Drop ml_ab_test_predictions table
    op.drop_index('idx_ab_prediction_predicted', table_name='ml_ab_test_predictions')
    op.drop_index('idx_ab_prediction_model', table_name='ml_ab_test_predictions')
    op.drop_index('idx_ab_prediction_test', table_name='ml_ab_test_predictions')
    op.drop_table('ml_ab_test_predictions')
    
    # Drop ml_ab_tests table
    op.drop_index('idx_ab_test_created', table_name='ml_ab_tests')
    op.drop_index('idx_ab_test_dates', table_name='ml_ab_tests')
    op.drop_index('idx_ab_test_status', table_name='ml_ab_tests')
    op.drop_table('ml_ab_tests')
    
    # Drop ml_model_versions table
    op.drop_index('idx_model_version_created', table_name='ml_model_versions')
    op.drop_index('idx_model_version_production', table_name='ml_model_versions')
    op.drop_index('idx_model_version_type', table_name='ml_model_versions')
    op.drop_table('ml_model_versions')
    
    # Drop ml_training_jobs table
    op.drop_index('idx_training_job_celery', table_name='ml_training_jobs')
    op.drop_index('idx_training_job_created', table_name='ml_training_jobs')
    op.drop_index('idx_training_job_type', table_name='ml_training_jobs')
    op.drop_index('idx_training_job_status', table_name='ml_training_jobs')
    op.drop_table('ml_training_jobs')
    
    # Drop enum types
    op.execute("DROP TYPE IF EXISTS trainingjobstatus")
    op.execute("DROP TYPE IF EXISTS modelversionstatus")
    op.execute("DROP TYPE IF EXISTS abteststatus")
