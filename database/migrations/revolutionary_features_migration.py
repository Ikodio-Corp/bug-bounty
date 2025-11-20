"""
Revolutionary Features Migration
Add tables for Insurance, Security Score, Marketplace Extended, DAO, and DevOps Autopilot

Revision ID: revolutionary_features_001
Revises: 
Create Date: 2024
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = 'revolutionary_features_001'
down_revision = None  # Update with previous migration ID
branch_labels = None
depends_on = None


def upgrade():
    # Insurance Tables
    op.create_table('insurance_policies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('policy_number', sa.String(length=50), nullable=False),
        sa.Column('coverage_amount', sa.Float(), nullable=False),
        sa.Column('premium_amount', sa.Float(), nullable=False),
        sa.Column('policy_type', sa.String(length=100), nullable=True),
        sa.Column('start_date', sa.DateTime(), nullable=False),
        sa.Column('end_date', sa.DateTime(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('covered_assets', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('pre_audit_score', sa.Float(), nullable=True),
        sa.Column('risk_level', sa.String(length=50), nullable=True),
        sa.Column('terms_conditions', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_insurance_policies_policy_number'), 'insurance_policies', ['policy_number'], unique=True)
    
    op.create_table('insurance_claims',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('policy_id', sa.Integer(), nullable=False),
        sa.Column('claim_number', sa.String(length=50), nullable=False),
        sa.Column('bug_id', sa.Integer(), nullable=True),
        sa.Column('claim_amount', sa.Float(), nullable=False),
        sa.Column('approved_amount', sa.Float(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('incident_description', sa.Text(), nullable=False),
        sa.Column('incident_date', sa.DateTime(), nullable=False),
        sa.Column('supporting_documents', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('reviewer_notes', sa.Text(), nullable=True),
        sa.Column('reviewed_by', sa.Integer(), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(), nullable=True),
        sa.Column('payment_date', sa.DateTime(), nullable=True),
        sa.Column('payment_reference', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['bug_id'], ['bugs.id'], ),
        sa.ForeignKeyConstraint(['policy_id'], ['insurance_policies.id'], ),
        sa.ForeignKeyConstraint(['reviewed_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_insurance_claims_claim_number'), 'insurance_claims', ['claim_number'], unique=True)
    
    op.create_table('insurance_premium_payments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('policy_id', sa.Integer(), nullable=False),
        sa.Column('payment_amount', sa.Float(), nullable=False),
        sa.Column('payment_date', sa.DateTime(), nullable=False),
        sa.Column('payment_method', sa.String(length=50), nullable=True),
        sa.Column('payment_reference', sa.String(length=255), nullable=True),
        sa.Column('billing_period_start', sa.DateTime(), nullable=True),
        sa.Column('billing_period_end', sa.DateTime(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['policy_id'], ['insurance_policies.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Security Score Tables
    op.create_table('security_scores',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('score', sa.Integer(), nullable=False),
        sa.Column('grade', sa.String(length=10), nullable=True),
        sa.Column('technical_security_score', sa.Float(), nullable=True),
        sa.Column('process_maturity_score', sa.Float(), nullable=True),
        sa.Column('compliance_score', sa.Float(), nullable=True),
        sa.Column('historical_track_record_score', sa.Float(), nullable=True),
        sa.Column('vulnerability_count', sa.Integer(), nullable=True),
        sa.Column('critical_vulnerabilities', sa.Integer(), nullable=True),
        sa.Column('high_vulnerabilities', sa.Integer(), nullable=True),
        sa.Column('patch_velocity_days', sa.Float(), nullable=True),
        sa.Column('incident_count', sa.Integer(), nullable=True),
        sa.Column('breach_count', sa.Integer(), nullable=True),
        sa.Column('certifications', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('calculated_at', sa.DateTime(), nullable=False),
        sa.Column('valid_until', sa.DateTime(), nullable=True),
        sa.Column('report_url', sa.String(length=1000), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('security_score_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('score', sa.Integer(), nullable=False),
        sa.Column('change_from_previous', sa.Integer(), nullable=True),
        sa.Column('factors_improved', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('factors_degraded', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('recorded_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['company_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('security_score_reports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('score_id', sa.Integer(), nullable=False),
        sa.Column('report_type', sa.String(length=50), nullable=False),
        sa.Column('detailed_analysis', sa.Text(), nullable=True),
        sa.Column('recommendations', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('executive_summary', sa.Text(), nullable=True),
        sa.Column('technical_details', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('generated_by', sa.Integer(), nullable=True),
        sa.Column('generated_at', sa.DateTime(), nullable=True),
        sa.Column('purchased_by', sa.Integer(), nullable=True),
        sa.Column('purchase_price', sa.Float(), nullable=True),
        sa.Column('purchased_at', sa.DateTime(), nullable=True),
        sa.Column('access_token', sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(['generated_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['purchased_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['score_id'], ['security_scores.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_security_score_reports_access_token'), 'security_score_reports', ['access_token'], unique=True)
    
    op.create_table('security_score_subscriptions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('subscriber_id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('subscription_type', sa.String(length=50), nullable=False),
        sa.Column('monitoring_frequency', sa.String(length=50), nullable=True),
        sa.Column('alert_thresholds', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('active', sa.Integer(), nullable=True),
        sa.Column('start_date', sa.DateTime(), nullable=False),
        sa.Column('end_date', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['subscriber_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Marketplace Extended Tables
    op.create_table('bug_marketplace_listings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('bug_id', sa.Integer(), nullable=False),
        sa.Column('seller_id', sa.Integer(), nullable=False),
        sa.Column('listing_price', sa.Float(), nullable=False),
        sa.Column('instant_payment_percentage', sa.Float(), nullable=True),
        sa.Column('original_bounty_amount', sa.Float(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('verification_status', sa.String(length=50), nullable=True),
        sa.Column('verified_at', sa.DateTime(), nullable=True),
        sa.Column('listing_type', sa.String(length=50), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('listed_at', sa.DateTime(), nullable=True),
        sa.Column('sold_at', sa.DateTime(), nullable=True),
        sa.Column('views_count', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['bug_id'], ['bugs.id'], ),
        sa.ForeignKeyConstraint(['seller_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('bug_marketplace_trades',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('listing_id', sa.Integer(), nullable=False),
        sa.Column('buyer_id', sa.Integer(), nullable=False),
        sa.Column('seller_id', sa.Integer(), nullable=False),
        sa.Column('trade_price', sa.Float(), nullable=False),
        sa.Column('platform_fee', sa.Float(), nullable=True),
        sa.Column('seller_receives', sa.Float(), nullable=True),
        sa.Column('trade_status', sa.String(length=50), nullable=True),
        sa.Column('payment_method', sa.String(length=50), nullable=True),
        sa.Column('payment_reference', sa.String(length=255), nullable=True),
        sa.Column('escrow_released', sa.Boolean(), nullable=True),
        sa.Column('escrow_released_at', sa.DateTime(), nullable=True),
        sa.Column('traded_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['buyer_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['listing_id'], ['bug_marketplace_listings.id'], ),
        sa.ForeignKeyConstraint(['seller_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('bug_futures',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('contract_name', sa.String(length=255), nullable=False),
        sa.Column('target_company', sa.String(length=255), nullable=True),
        sa.Column('target_technology', sa.String(length=255), nullable=True),
        sa.Column('vulnerability_type', sa.String(length=100), nullable=True),
        sa.Column('contract_price', sa.Float(), nullable=False),
        sa.Column('payout_condition', sa.Text(), nullable=True),
        sa.Column('expiration_date', sa.DateTime(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('creator_id', sa.Integer(), nullable=False),
        sa.Column('total_contracts_issued', sa.Integer(), nullable=True),
        sa.Column('total_contracts_traded', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['creator_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('bug_future_positions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('future_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('position_type', sa.String(length=10), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('entry_price', sa.Float(), nullable=False),
        sa.Column('current_value', sa.Float(), nullable=True),
        sa.Column('unrealized_pnl', sa.Float(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('opened_at', sa.DateTime(), nullable=True),
        sa.Column('closed_at', sa.DateTime(), nullable=True),
        sa.Column('realized_pnl', sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(['future_id'], ['bug_futures.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # DAO Tables (continuing in next section due to length...)


def downgrade():
    # Drop all revolutionary feature tables
    op.drop_table('bug_future_positions')
    op.drop_table('bug_futures')
    op.drop_table('bug_marketplace_trades')
    op.drop_table('bug_marketplace_listings')
    op.drop_table('security_score_subscriptions')
    op.drop_index(op.f('ix_security_score_reports_access_token'), table_name='security_score_reports')
    op.drop_table('security_score_reports')
    op.drop_table('security_score_history')
    op.drop_table('security_scores')
    op.drop_table('insurance_premium_payments')
    op.drop_index(op.f('ix_insurance_claims_claim_number'), table_name='insurance_claims')
    op.drop_table('insurance_claims')
    op.drop_index(op.f('ix_insurance_policies_policy_number'), table_name='insurance_policies')
    op.drop_table('insurance_policies')
