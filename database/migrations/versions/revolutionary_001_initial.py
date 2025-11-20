"""
Alembic migration for revolutionary features
Revision ID: revolutionary_001
Create Date: 2024-01-15
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = 'revolutionary_001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Insurance tables
    op.create_table(
        'insurance_policies',
        sa.Column('policy_id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('coverage_amount', sa.Float(), nullable=False),
        sa.Column('premium_amount', sa.Float(), nullable=False),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('start_date', sa.DateTime(), nullable=False),
        sa.Column('end_date', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('policy_id'),
        sa.ForeignKeyConstraint(['company_id'], ['companies.company_id'])
    )
    op.create_index('idx_insurance_policies_company', 'insurance_policies', ['company_id'])
    op.create_index('idx_insurance_policies_status', 'insurance_policies', ['status'])

    op.create_table(
        'insurance_claims',
        sa.Column('claim_id', sa.Integer(), nullable=False),
        sa.Column('policy_id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('incident_description', sa.Text(), nullable=False),
        sa.Column('estimated_damage', sa.Float(), nullable=False),
        sa.Column('approved_amount', sa.Float(), nullable=True),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('submitted_at', sa.DateTime(), nullable=False),
        sa.Column('reviewed_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('claim_id'),
        sa.ForeignKeyConstraint(['policy_id'], ['insurance_policies.policy_id']),
        sa.ForeignKeyConstraint(['company_id'], ['companies.company_id'])
    )
    op.create_index('idx_insurance_claims_policy', 'insurance_claims', ['policy_id'])
    op.create_index('idx_insurance_claims_status', 'insurance_claims', ['status'])

    op.create_table(
        'actuarial_data',
        sa.Column('data_id', sa.Integer(), nullable=False),
        sa.Column('company_size', sa.String(50), nullable=False),
        sa.Column('industry_risk', sa.String(50), nullable=False),
        sa.Column('base_rate', sa.Float(), nullable=False),
        sa.Column('risk_multiplier', sa.Float(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('data_id')
    )

    # Security Score tables
    op.create_table(
        'security_scores',
        sa.Column('score_id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('overall_score', sa.Integer(), nullable=False),
        sa.Column('grade', sa.String(2), nullable=False),
        sa.Column('technical_component', sa.Integer(), nullable=False),
        sa.Column('process_component', sa.Integer(), nullable=False),
        sa.Column('compliance_component', sa.Integer(), nullable=False),
        sa.Column('historical_component', sa.Integer(), nullable=False),
        sa.Column('calculated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('score_id'),
        sa.ForeignKeyConstraint(['company_id'], ['companies.company_id'])
    )
    op.create_index('idx_security_scores_company', 'security_scores', ['company_id'])
    op.create_index('idx_security_scores_grade', 'security_scores', ['grade'])

    op.create_table(
        'score_history',
        sa.Column('history_id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('score', sa.Integer(), nullable=False),
        sa.Column('grade', sa.String(2), nullable=False),
        sa.Column('recorded_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('history_id'),
        sa.ForeignKeyConstraint(['company_id'], ['companies.company_id'])
    )
    op.create_index('idx_score_history_company', 'score_history', ['company_id'])

    op.create_table(
        'security_components',
        sa.Column('component_id', sa.Integer(), nullable=False),
        sa.Column('score_id', sa.Integer(), nullable=False),
        sa.Column('component_name', sa.String(100), nullable=False),
        sa.Column('score', sa.Integer(), nullable=False),
        sa.Column('weight', sa.Float(), nullable=False),
        sa.Column('recommendations', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('component_id'),
        sa.ForeignKeyConstraint(['score_id'], ['security_scores.score_id'])
    )

    op.create_table(
        'vulnerability_metrics',
        sa.Column('metric_id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('total_vulnerabilities', sa.Integer(), nullable=False),
        sa.Column('critical_count', sa.Integer(), nullable=False),
        sa.Column('high_count', sa.Integer(), nullable=False),
        sa.Column('medium_count', sa.Integer(), nullable=False),
        sa.Column('low_count', sa.Integer(), nullable=False),
        sa.Column('avg_resolution_time_hours', sa.Float(), nullable=True),
        sa.Column('recorded_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('metric_id'),
        sa.ForeignKeyConstraint(['company_id'], ['companies.company_id'])
    )

    # Marketplace Extended tables
    op.create_table(
        'bug_listings',
        sa.Column('listing_id', sa.Integer(), nullable=False),
        sa.Column('bug_id', sa.Integer(), nullable=False),
        sa.Column('seller_id', sa.Integer(), nullable=False),
        sa.Column('asking_price', sa.Float(), nullable=False),
        sa.Column('instant_payment_amount', sa.Float(), nullable=False),
        sa.Column('is_available', sa.Boolean(), nullable=False, default=True),
        sa.Column('listed_at', sa.DateTime(), nullable=False),
        sa.Column('sold_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('listing_id'),
        sa.ForeignKeyConstraint(['bug_id'], ['bugs.bug_id']),
        sa.ForeignKeyConstraint(['seller_id'], ['users.user_id'])
    )
    op.create_index('idx_bug_listings_available', 'bug_listings', ['is_available'])

    op.create_table(
        'bug_futures',
        sa.Column('future_id', sa.Integer(), nullable=False),
        sa.Column('underlying_bug_id', sa.Integer(), nullable=True),
        sa.Column('contract_type', sa.String(50), nullable=False),
        sa.Column('strike_price', sa.Float(), nullable=False),
        sa.Column('expiration_date', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('future_id'),
        sa.ForeignKeyConstraint(['underlying_bug_id'], ['bugs.bug_id'])
    )

    op.create_table(
        'future_positions',
        sa.Column('position_id', sa.Integer(), nullable=False),
        sa.Column('future_id', sa.Integer(), nullable=False),
        sa.Column('trader_id', sa.Integer(), nullable=False),
        sa.Column('position_type', sa.String(10), nullable=False),
        sa.Column('contracts', sa.Integer(), nullable=False),
        sa.Column('entry_price', sa.Float(), nullable=False),
        sa.Column('exit_price', sa.Float(), nullable=True),
        sa.Column('profit_loss', sa.Float(), nullable=True),
        sa.Column('opened_at', sa.DateTime(), nullable=False),
        sa.Column('closed_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('position_id'),
        sa.ForeignKeyConstraint(['future_id'], ['bug_futures.future_id']),
        sa.ForeignKeyConstraint(['trader_id'], ['users.user_id'])
    )

    op.create_table(
        'trade_transactions',
        sa.Column('transaction_id', sa.Integer(), nullable=False),
        sa.Column('listing_id', sa.Integer(), nullable=True),
        sa.Column('position_id', sa.Integer(), nullable=True),
        sa.Column('buyer_id', sa.Integer(), nullable=False),
        sa.Column('seller_id', sa.Integer(), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('platform_fee', sa.Float(), nullable=False),
        sa.Column('transaction_type', sa.String(50), nullable=False),
        sa.Column('completed_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('transaction_id'),
        sa.ForeignKeyConstraint(['listing_id'], ['bug_listings.listing_id']),
        sa.ForeignKeyConstraint(['position_id'], ['future_positions.position_id']),
        sa.ForeignKeyConstraint(['buyer_id'], ['users.user_id']),
        sa.ForeignKeyConstraint(['seller_id'], ['users.user_id'])
    )

    # DAO Governance tables
    op.create_table(
        'proposals',
        sa.Column('proposal_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('proposal_type', sa.String(50), nullable=False),
        sa.Column('proposer_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('votes_for', sa.Integer(), nullable=False, default=0),
        sa.Column('votes_against', sa.Integer(), nullable=False, default=0),
        sa.Column('votes_abstain', sa.Integer(), nullable=False, default=0),
        sa.Column('execution_data', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('voting_ends_at', sa.DateTime(), nullable=False),
        sa.Column('executed_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('proposal_id'),
        sa.ForeignKeyConstraint(['proposer_id'], ['users.user_id'])
    )
    op.create_index('idx_proposals_status', 'proposals', ['status'])

    op.create_table(
        'votes',
        sa.Column('vote_id', sa.Integer(), nullable=False),
        sa.Column('proposal_id', sa.Integer(), nullable=False),
        sa.Column('voter_id', sa.Integer(), nullable=False),
        sa.Column('vote_type', sa.String(10), nullable=False),
        sa.Column('voting_power', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('vote_id'),
        sa.ForeignKeyConstraint(['proposal_id'], ['proposals.proposal_id']),
        sa.ForeignKeyConstraint(['voter_id'], ['users.user_id']),
        sa.UniqueConstraint('proposal_id', 'voter_id', name='uq_vote_per_user')
    )

    op.create_table(
        'token_balances',
        sa.Column('balance_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('balance', sa.Float(), nullable=False, default=0.0),
        sa.Column('staked_balance', sa.Float(), nullable=False, default=0.0),
        sa.Column('total_earned', sa.Float(), nullable=False, default=0.0),
        sa.Column('total_spent', sa.Float(), nullable=False, default=0.0),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('balance_id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id']),
        sa.UniqueConstraint('user_id', name='uq_token_balance_per_user')
    )

    op.create_table(
        'token_stakes',
        sa.Column('stake_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('start_date', sa.DateTime(), nullable=False),
        sa.Column('end_date', sa.DateTime(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('stake_id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'])
    )

    op.create_table(
        'governance_events',
        sa.Column('event_id', sa.Integer(), nullable=False),
        sa.Column('event_type', sa.String(50), nullable=False),
        sa.Column('proposal_id', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('event_data', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('event_id'),
        sa.ForeignKeyConstraint(['proposal_id'], ['proposals.proposal_id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'])
    )

    # DevOps Autopilot tables
    op.create_table(
        'infrastructure_resources',
        sa.Column('resource_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('resource_type', sa.String(50), nullable=False),
        sa.Column('resource_name', sa.String(255), nullable=False),
        sa.Column('cloud_provider', sa.String(50), nullable=False),
        sa.Column('region', sa.String(50), nullable=False),
        sa.Column('configuration', postgresql.JSONB(), nullable=True),
        sa.Column('monthly_cost', sa.Float(), nullable=False),
        sa.Column('auto_scaling_enabled', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('resource_id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'])
    )
    op.create_index('idx_infrastructure_resources_user', 'infrastructure_resources', ['user_id'])

    op.create_table(
        'deployment_jobs',
        sa.Column('job_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('job_type', sa.String(50), nullable=False),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('target_environment', sa.String(50), nullable=False),
        sa.Column('configuration', postgresql.JSONB(), nullable=True),
        sa.Column('estimated_duration_minutes', sa.Integer(), nullable=True),
        sa.Column('actual_duration_minutes', sa.Integer(), nullable=True),
        sa.Column('triggered_by_ai', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('job_id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'])
    )
    op.create_index('idx_deployment_jobs_status', 'deployment_jobs', ['status'])

    op.create_table(
        'self_healing_events',
        sa.Column('event_id', sa.Integer(), nullable=False),
        sa.Column('resource_id', sa.Integer(), nullable=False),
        sa.Column('incident_type', sa.String(100), nullable=False),
        sa.Column('severity', sa.String(20), nullable=False),
        sa.Column('healing_action_taken', sa.Text(), nullable=False),
        sa.Column('healing_status', sa.String(50), nullable=False),
        sa.Column('resolution_time_seconds', sa.Integer(), nullable=True),
        sa.Column('ai_confidence_score', sa.Float(), nullable=True),
        sa.Column('detected_at', sa.DateTime(), nullable=False),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('event_id'),
        sa.ForeignKeyConstraint(['resource_id'], ['infrastructure_resources.resource_id'])
    )
    op.create_index('idx_self_healing_events_resource', 'self_healing_events', ['resource_id'])

    op.create_table(
        'cost_optimization_recommendations',
        sa.Column('recommendation_id', sa.Integer(), nullable=False),
        sa.Column('resource_id', sa.Integer(), nullable=False),
        sa.Column('recommendation_type', sa.String(100), nullable=False),
        sa.Column('current_cost', sa.Float(), nullable=False),
        sa.Column('projected_cost', sa.Float(), nullable=False),
        sa.Column('savings_amount', sa.Float(), nullable=False),
        sa.Column('savings_percentage', sa.Float(), nullable=False),
        sa.Column('implementation_effort', sa.String(20), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('is_applied', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('recommendation_id'),
        sa.ForeignKeyConstraint(['resource_id'], ['infrastructure_resources.resource_id'])
    )

    op.create_table(
        'auto_scaling_policies',
        sa.Column('policy_id', sa.Integer(), nullable=False),
        sa.Column('resource_id', sa.Integer(), nullable=False),
        sa.Column('metric_type', sa.String(50), nullable=False),
        sa.Column('min_instances', sa.Integer(), nullable=False),
        sa.Column('max_instances', sa.Integer(), nullable=False),
        sa.Column('target_value', sa.Float(), nullable=False),
        sa.Column('scale_up_threshold', sa.Float(), nullable=False),
        sa.Column('scale_down_threshold', sa.Float(), nullable=False),
        sa.Column('is_enabled', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('policy_id'),
        sa.ForeignKeyConstraint(['resource_id'], ['infrastructure_resources.resource_id'])
    )

    op.create_table(
        'cloud_provider_configs',
        sa.Column('config_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('provider_name', sa.String(50), nullable=False),
        sa.Column('credentials', postgresql.JSONB(), nullable=False),
        sa.Column('default_region', sa.String(50), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('config_id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'])
    )


def downgrade() -> None:
    # Drop DevOps tables
    op.drop_table('cloud_provider_configs')
    op.drop_table('auto_scaling_policies')
    op.drop_table('cost_optimization_recommendations')
    op.drop_index('idx_self_healing_events_resource')
    op.drop_table('self_healing_events')
    op.drop_index('idx_deployment_jobs_status')
    op.drop_table('deployment_jobs')
    op.drop_index('idx_infrastructure_resources_user')
    op.drop_table('infrastructure_resources')

    # Drop DAO tables
    op.drop_table('governance_events')
    op.drop_table('token_stakes')
    op.drop_table('token_balances')
    op.drop_table('votes')
    op.drop_index('idx_proposals_status')
    op.drop_table('proposals')

    # Drop Marketplace tables
    op.drop_table('trade_transactions')
    op.drop_table('future_positions')
    op.drop_table('bug_futures')
    op.drop_index('idx_bug_listings_available')
    op.drop_table('bug_listings')

    # Drop Security Score tables
    op.drop_table('vulnerability_metrics')
    op.drop_table('security_components')
    op.drop_index('idx_score_history_company')
    op.drop_table('score_history')
    op.drop_index('idx_security_scores_grade')
    op.drop_index('idx_security_scores_company')
    op.drop_table('security_scores')

    # Drop Insurance tables
    op.drop_table('actuarial_data')
    op.drop_index('idx_insurance_claims_status')
    op.drop_index('idx_insurance_claims_policy')
    op.drop_table('insurance_claims')
    op.drop_index('idx_insurance_policies_status')
    op.drop_index('idx_insurance_policies_company')
    op.drop_table('insurance_policies')
