"""
Database migration for ML integration
Add tables for ML feedback and tracking
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '012_ml_integration'
down_revision = '11'
branch_labels = None
depends_on = None


def upgrade():
    # Add ML prediction fields to bugs table
    op.add_column('bugs', sa.Column('ml_prediction_id', sa.Integer(), nullable=True))
    op.add_column('bugs', sa.Column('ml_predicted_vulnerability', sa.Boolean(), nullable=True))
    op.add_column('bugs', sa.Column('ml_confidence_score', sa.Float(), nullable=True))
    op.add_column('bugs', sa.Column('ml_predicted_type', sa.String(100), nullable=True))
    op.add_column('bugs', sa.Column('ml_predicted_severity', sa.Float(), nullable=True))
    op.add_column('bugs', sa.Column('ml_prediction_feedback', sa.String(50), nullable=True))
    op.add_column('bugs', sa.Column('ml_feedback_notes', sa.Text(), nullable=True))
    op.add_column('bugs', sa.Column('ml_predicted_at', sa.DateTime(), nullable=True))
    
    # Add ML prediction fields to scans table
    op.add_column('scans', sa.Column('ml_prediction_enabled', sa.Boolean(), server_default='true'))
    op.add_column('scans', sa.Column('ml_prediction_id', sa.Integer(), nullable=True))
    op.add_column('scans', sa.Column('ml_predicted_vulnerabilities', sa.Integer(), nullable=True))
    op.add_column('scans', sa.Column('ml_confidence_average', sa.Float(), nullable=True))
    op.add_column('scans', sa.Column('ml_high_confidence_count', sa.Integer(), nullable=True))
    op.add_column('scans', sa.Column('ml_prediction_time_ms', sa.Integer(), nullable=True))
    op.add_column('scans', sa.Column('ml_predictions_data', postgresql.JSONB(), nullable=True))
    op.add_column('scans', sa.Column('ml_predicted_at', sa.DateTime(), nullable=True))
    
    # Create ml_prediction_feedback table
    op.create_table(
        'ml_prediction_feedback',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('prediction_id', sa.Integer(), nullable=False, index=True),
        sa.Column('bug_id', sa.Integer(), nullable=True, index=True),
        sa.Column('scan_id', sa.Integer(), nullable=True, index=True),
        sa.Column('user_id', sa.Integer(), nullable=False, index=True),
        
        sa.Column('predicted_vulnerability', sa.Boolean(), nullable=False),
        sa.Column('predicted_type', sa.String(100), nullable=True),
        sa.Column('predicted_severity', sa.Float(), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=False),
        
        sa.Column('is_correct', sa.Boolean(), nullable=False),
        sa.Column('actual_vulnerability', sa.Boolean(), nullable=True),
        sa.Column('actual_type', sa.String(100), nullable=True),
        sa.Column('actual_severity', sa.Float(), nullable=True),
        
        sa.Column('feedback_type', sa.String(50), nullable=False),
        sa.Column('feedback_source', sa.String(100), nullable=True),
        sa.Column('feedback_notes', sa.Text(), nullable=True),
        
        sa.Column('response_time_hours', sa.Float(), nullable=True),
        sa.Column('feedback_confidence', sa.Float(), nullable=True),
        
        sa.Column('prediction_made_at', sa.DateTime(), nullable=False),
        sa.Column('feedback_submitted_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('synced_to_ml_at', sa.DateTime(), nullable=True),
        
        sa.ForeignKeyConstraint(['bug_id'], ['bugs.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['scan_id'], ['scans.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for ml_prediction_feedback
    op.create_index('idx_ml_feedback_prediction_id', 'ml_prediction_feedback', ['prediction_id'])
    op.create_index('idx_ml_feedback_user_id', 'ml_prediction_feedback', ['user_id'])
    op.create_index('idx_ml_feedback_submitted_at', 'ml_prediction_feedback', ['feedback_submitted_at'])
    
    # Create ml_model_performance table
    op.create_table(
        'ml_model_performance',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('model_id', sa.Integer(), nullable=False, index=True),
        sa.Column('model_type', sa.String(50), nullable=False, index=True),
        sa.Column('model_version', sa.String(50), nullable=False),
        
        sa.Column('accuracy', sa.Float(), nullable=True),
        sa.Column('precision', sa.Float(), nullable=True),
        sa.Column('recall', sa.Float(), nullable=True),
        sa.Column('f1_score', sa.Float(), nullable=True),
        
        sa.Column('total_predictions', sa.Integer(), server_default='0'),
        sa.Column('correct_predictions', sa.Integer(), server_default='0'),
        sa.Column('false_positives', sa.Integer(), server_default='0'),
        sa.Column('false_negatives', sa.Integer(), server_default='0'),
        
        sa.Column('period_start', sa.DateTime(), nullable=False),
        sa.Column('period_end', sa.DateTime(), nullable=False),
        
        sa.Column('average_confidence', sa.Float(), nullable=True),
        sa.Column('average_processing_time_ms', sa.Float(), nullable=True),
        
        sa.Column('metadata', postgresql.JSONB(), nullable=True),
        
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for ml_model_performance
    op.create_index('idx_ml_performance_model_id', 'ml_model_performance', ['model_id'])
    op.create_index('idx_ml_performance_model_type', 'ml_model_performance', ['model_type'])
    op.create_index('idx_ml_performance_period', 'ml_model_performance', ['period_start', 'period_end'])
    
    # Create confidence_score_calibration table
    op.create_table(
        'confidence_score_calibration',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('model_type', sa.String(50), nullable=False, index=True),
        sa.Column('confidence_range_min', sa.Float(), nullable=False),
        sa.Column('confidence_range_max', sa.Float(), nullable=False),
        
        sa.Column('actual_accuracy', sa.Float(), nullable=False),
        sa.Column('sample_count', sa.Integer(), nullable=False),
        
        sa.Column('reliability_level', sa.String(50), nullable=True),
        sa.Column('recommended_threshold', sa.Float(), nullable=True),
        
        sa.Column('calibrated_from', sa.DateTime(), nullable=False),
        sa.Column('calibrated_to', sa.DateTime(), nullable=False),
        
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for confidence_score_calibration
    op.create_index('idx_confidence_model_type', 'confidence_score_calibration', ['model_type'])
    op.create_index('idx_confidence_range', 'confidence_score_calibration', ['confidence_range_min', 'confidence_range_max'])


def downgrade():
    # Drop tables
    op.drop_table('confidence_score_calibration')
    op.drop_table('ml_model_performance')
    op.drop_table('ml_prediction_feedback')
    
    # Remove columns from scans
    op.drop_column('scans', 'ml_predicted_at')
    op.drop_column('scans', 'ml_predictions_data')
    op.drop_column('scans', 'ml_prediction_time_ms')
    op.drop_column('scans', 'ml_high_confidence_count')
    op.drop_column('scans', 'ml_confidence_average')
    op.drop_column('scans', 'ml_predicted_vulnerabilities')
    op.drop_column('scans', 'ml_prediction_id')
    op.drop_column('scans', 'ml_prediction_enabled')
    
    # Remove columns from bugs
    op.drop_column('bugs', 'ml_predicted_at')
    op.drop_column('bugs', 'ml_feedback_notes')
    op.drop_column('bugs', 'ml_prediction_feedback')
    op.drop_column('bugs', 'ml_predicted_severity')
    op.drop_column('bugs', 'ml_predicted_type')
    op.drop_column('bugs', 'ml_confidence_score')
    op.drop_column('bugs', 'ml_predicted_vulnerability')
    op.drop_column('bugs', 'ml_prediction_id')
