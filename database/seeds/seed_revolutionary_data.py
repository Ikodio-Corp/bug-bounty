"""
Seed revolutionary features test data
"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.core.config import settings
from backend.models.insurance import InsurancePolicy, InsuranceClaim, PolicyStatus, ClaimStatus
from backend.models.security_score import SecurityScore, ScoreHistory
from backend.models.marketplace import BugListing, BugFuture, FuturePosition
from backend.models.dao import Proposal, Vote, TokenBalance, TokenStake, ProposalType, ProposalStatus, VoteType
from backend.models.devops import InfrastructureResource, DeploymentJob, SelfHealingEvent


async def seed_insurance_data(session: AsyncSession):
    """Seed insurance policies and claims"""
    print("Seeding insurance data...")
    
    # Create policies
    policies = [
        InsurancePolicy(
            company_id=1,
            coverage_amount=1000000.0,
            premium_amount=25000.0,
            status=PolicyStatus.ACTIVE,
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow() + timedelta(days=365),
            created_at=datetime.utcnow()
        ),
        InsurancePolicy(
            company_id=2,
            coverage_amount=5000000.0,
            premium_amount=200000.0,
            status=PolicyStatus.ACTIVE,
            start_date=datetime.utcnow() - timedelta(days=180),
            end_date=datetime.utcnow() + timedelta(days=185),
            created_at=datetime.utcnow() - timedelta(days=180)
        )
    ]
    
    for policy in policies:
        session.add(policy)
    
    await session.flush()
    
    # Create claims
    claims = [
        InsuranceClaim(
            policy_id=policies[0].policy_id,
            company_id=1,
            incident_description="Critical vulnerability exploited causing data breach",
            estimated_damage=50000.0,
            approved_amount=50000.0,
            status=ClaimStatus.APPROVED,
            submitted_at=datetime.utcnow() - timedelta(days=10),
            reviewed_at=datetime.utcnow() - timedelta(days=5)
        )
    ]
    
    for claim in claims:
        session.add(claim)
    
    await session.commit()
    print(f"Created {len(policies)} policies and {len(claims)} claims")


async def seed_security_scores(session: AsyncSession):
    """Seed security credit scores"""
    print("Seeding security scores...")
    
    scores = [
        SecurityScore(
            company_id=1,
            overall_score=720,
            grade="B",
            technical_component=750,
            process_component=700,
            compliance_component=690,
            historical_component=740,
            calculated_at=datetime.utcnow()
        ),
        SecurityScore(
            company_id=2,
            overall_score=650,
            grade="C",
            technical_component=630,
            process_component=660,
            compliance_component=670,
            historical_component=640,
            calculated_at=datetime.utcnow()
        ),
        SecurityScore(
            company_id=3,
            overall_score=810,
            grade="A",
            technical_component=830,
            process_component=800,
            compliance_component=790,
            historical_component=820,
            calculated_at=datetime.utcnow()
        )
    ]
    
    for score in scores:
        session.add(score)
        
        # Add history
        history = ScoreHistory(
            company_id=score.company_id,
            score=score.overall_score - 20,
            grade="C" if score.grade == "B" else "D" if score.grade == "C" else "B",
            recorded_at=datetime.utcnow() - timedelta(days=30)
        )
        session.add(history)
    
    await session.commit()
    print(f"Created {len(scores)} security scores with history")


async def seed_dao_data(session: AsyncSession):
    """Seed DAO governance data"""
    print("Seeding DAO data...")
    
    # Create token balances
    balances = [
        TokenBalance(
            user_id=1,
            balance=100000.0,
            staked_balance=50000.0,
            total_earned=100000.0,
            created_at=datetime.utcnow()
        ),
        TokenBalance(
            user_id=2,
            balance=50000.0,
            staked_balance=25000.0,
            total_earned=50000.0,
            created_at=datetime.utcnow()
        ),
        TokenBalance(
            user_id=3,
            balance=25000.0,
            staked_balance=10000.0,
            total_earned=25000.0,
            created_at=datetime.utcnow()
        )
    ]
    
    for balance in balances:
        session.add(balance)
    
    await session.flush()
    
    # Create proposals
    proposals = [
        Proposal(
            title="Increase Bug Bounty Rewards by 20%",
            description="Proposal to increase all bug bounty rewards by 20% to attract more hunters",
            proposal_type=ProposalType.PARAMETER_CHANGE,
            proposer_id=1,
            status=ProposalStatus.ACTIVE,
            votes_for=75000,
            votes_against=20000,
            votes_abstain=5000,
            created_at=datetime.utcnow() - timedelta(days=3),
            voting_ends_at=datetime.utcnow() + timedelta(days=4)
        ),
        Proposal(
            title="Add Quantum Security Scanner",
            description="Proposal to add quantum-resistant cryptography scanning feature",
            proposal_type=ProposalType.FEATURE,
            proposer_id=2,
            status=ProposalStatus.ACTIVE,
            votes_for=60000,
            votes_against=10000,
            votes_abstain=2000,
            created_at=datetime.utcnow() - timedelta(days=1),
            voting_ends_at=datetime.utcnow() + timedelta(days=6)
        )
    ]
    
    for proposal in proposals:
        session.add(proposal)
    
    await session.flush()
    
    # Create votes
    votes = [
        Vote(
            proposal_id=proposals[0].proposal_id,
            voter_id=1,
            vote_type=VoteType.FOR,
            voting_power=50000,
            created_at=datetime.utcnow() - timedelta(days=2)
        ),
        Vote(
            proposal_id=proposals[0].proposal_id,
            voter_id=2,
            vote_type=VoteType.FOR,
            voting_power=25000,
            created_at=datetime.utcnow() - timedelta(days=2)
        )
    ]
    
    for vote in votes:
        session.add(vote)
    
    await session.commit()
    print(f"Created {len(balances)} token balances, {len(proposals)} proposals, {len(votes)} votes")


async def seed_devops_data(session: AsyncSession):
    """Seed DevOps autopilot data"""
    print("Seeding DevOps data...")
    
    # Create infrastructure resources
    resources = [
        InfrastructureResource(
            user_id=3,
            resource_type="compute",
            resource_name="web-server-01",
            cloud_provider="aws",
            region="us-east-1",
            monthly_cost=150.0,
            auto_scaling_enabled=True,
            created_at=datetime.utcnow() - timedelta(days=60)
        ),
        InfrastructureResource(
            user_id=3,
            resource_type="database",
            resource_name="postgres-primary",
            cloud_provider="aws",
            region="us-east-1",
            monthly_cost=350.0,
            auto_scaling_enabled=False,
            created_at=datetime.utcnow() - timedelta(days=60)
        ),
        InfrastructureResource(
            user_id=3,
            resource_type="storage",
            resource_name="s3-bucket-prod",
            cloud_provider="aws",
            region="us-east-1",
            monthly_cost=50.0,
            auto_scaling_enabled=False,
            created_at=datetime.utcnow() - timedelta(days=60)
        )
    ]
    
    for resource in resources:
        session.add(resource)
    
    await session.flush()
    
    # Create deployment jobs
    jobs = [
        DeploymentJob(
            user_id=3,
            job_type="deploy",
            status="completed",
            target_environment="production",
            estimated_duration_minutes=15,
            actual_duration_minutes=12,
            triggered_by_ai=True,
            created_at=datetime.utcnow() - timedelta(hours=2),
            completed_at=datetime.utcnow() - timedelta(hours=2) + timedelta(minutes=12)
        ),
        DeploymentJob(
            user_id=3,
            job_type="provision",
            status="completed",
            target_environment="production",
            estimated_duration_minutes=30,
            actual_duration_minutes=28,
            triggered_by_ai=True,
            created_at=datetime.utcnow() - timedelta(days=1),
            completed_at=datetime.utcnow() - timedelta(days=1) + timedelta(minutes=28)
        )
    ]
    
    for job in jobs:
        session.add(job)
    
    await session.flush()
    
    # Create self-healing events
    events = [
        SelfHealingEvent(
            resource_id=resources[0].resource_id,
            incident_type="high_cpu_usage",
            severity="high",
            healing_action_taken="Scaled up instances from 2 to 4",
            healing_status="resolved",
            resolution_time_seconds=95,
            ai_confidence_score=0.95,
            detected_at=datetime.utcnow() - timedelta(hours=5),
            resolved_at=datetime.utcnow() - timedelta(hours=5) + timedelta(seconds=95)
        ),
        SelfHealingEvent(
            resource_id=resources[1].resource_id,
            incident_type="connection_timeout",
            severity="critical",
            healing_action_taken="Restarted database service and cleared connection pool",
            healing_status="resolved",
            resolution_time_seconds=118,
            ai_confidence_score=0.92,
            detected_at=datetime.utcnow() - timedelta(hours=12),
            resolved_at=datetime.utcnow() - timedelta(hours=12) + timedelta(seconds=118)
        )
    ]
    
    for event in events:
        session.add(event)
    
    await session.commit()
    print(f"Created {len(resources)} resources, {len(jobs)} jobs, {len(events)} healing events")


async def main():
    """Main seeding function for revolutionary features"""
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        try:
            await seed_insurance_data(session)
            await seed_security_scores(session)
            await seed_dao_data(session)
            await seed_devops_data(session)
            print("\nRevolutionary features data seeding completed successfully!")
        except Exception as e:
            print(f"\nError during seeding: {e}")
            await session.rollback()
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
