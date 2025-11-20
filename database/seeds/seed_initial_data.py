"""
Database seed script for initial data
"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.core.config import settings
from backend.core.security import get_password_hash
from backend.models.user import User, UserRole
from backend.models.bug import Bug, BugSeverity, BugStatus
from backend.models.advanced import Company


async def seed_users(session: AsyncSession):
    """Seed initial users"""
    print("Seeding users...")
    
    users = [
        User(
            email="admin@ikodio.com",
            username="admin",
            hashed_password=get_password_hash("Admin@12345"),
            full_name="System Administrator",
            role=UserRole.ADMIN,
            is_active=True,
            is_verified=True,
            reputation_score=100.0,
            created_at=datetime.utcnow()
        ),
        User(
            email="hunter@ikodio.com",
            username="hunter1",
            hashed_password=get_password_hash("Hunter@12345"),
            full_name="Elite Hunter",
            role=UserRole.HUNTER,
            is_active=True,
            is_verified=True,
            reputation_score=95.0,
            total_bugs_found=25,
            total_earnings=50000.0,
            created_at=datetime.utcnow()
        ),
        User(
            email="company@ikodio.com",
            username="company1",
            hashed_password=get_password_hash("Company@12345"),
            full_name="Test Company",
            role=UserRole.COMPANY,
            is_active=True,
            is_verified=True,
            created_at=datetime.utcnow()
        )
    ]
    
    for user in users:
        session.add(user)
    
    await session.commit()
    print(f"Created {len(users)} users")


async def seed_companies(session: AsyncSession):
    """Seed initial companies"""
    print("Seeding companies...")
    
    companies = [
        Company(
            name="TechCorp Inc",
            domain="techcorp.com",
            industry="technology",
            company_size="large",
            is_verified=True,
            created_at=datetime.utcnow()
        ),
        Company(
            name="SecureBank",
            domain="securebank.com",
            industry="finance",
            company_size="enterprise",
            is_verified=True,
            created_at=datetime.utcnow()
        ),
        Company(
            name="HealthTech Solutions",
            domain="healthtech.com",
            industry="healthcare",
            company_size="medium",
            is_verified=True,
            created_at=datetime.utcnow()
        )
    ]
    
    for company in companies:
        session.add(company)
    
    await session.commit()
    print(f"Created {len(companies)} companies")


async def seed_bugs(session: AsyncSession):
    """Seed sample bugs"""
    print("Seeding bugs...")
    
    bugs = [
        Bug(
            title="SQL Injection in Login Form",
            description="The login form is vulnerable to SQL injection attacks...",
            severity=BugSeverity.CRITICAL,
            status=BugStatus.FIXED,
            vulnerability_type="SQL Injection",
            target_url="https://example.com/login",
            proof_of_concept="' OR '1'='1' --",
            impact="Complete database compromise",
            remediation="Use parameterized queries",
            cvss_score=9.8,
            reward_amount=5000.0,
            hunter_id=2,
            company_id=1,
            created_at=datetime.utcnow() - timedelta(days=30)
        ),
        Bug(
            title="XSS in User Profile Page",
            description="Stored XSS vulnerability in user profile bio field...",
            severity=BugSeverity.HIGH,
            status=BugStatus.VERIFIED,
            vulnerability_type="Cross-Site Scripting",
            target_url="https://example.com/profile",
            proof_of_concept="<script>alert('XSS')</script>",
            impact="Session hijacking and data theft",
            remediation="Implement input sanitization",
            cvss_score=7.5,
            reward_amount=2000.0,
            hunter_id=2,
            company_id=1,
            created_at=datetime.utcnow() - timedelta(days=15)
        ),
        Bug(
            title="CSRF Token Not Validated",
            description="CSRF protection missing on critical endpoints...",
            severity=BugSeverity.MEDIUM,
            status=BugStatus.ACCEPTED,
            vulnerability_type="CSRF",
            target_url="https://example.com/api/transfer",
            proof_of_concept="POST request without CSRF token",
            impact="Unauthorized actions on behalf of users",
            remediation="Implement CSRF tokens",
            cvss_score=6.5,
            reward_amount=1000.0,
            hunter_id=2,
            company_id=2,
            created_at=datetime.utcnow() - timedelta(days=7)
        )
    ]
    
    for bug in bugs:
        session.add(bug)
    
    await session.commit()
    print(f"Created {len(bugs)} bugs")


async def main():
    """Main seeding function"""
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        try:
            await seed_users(session)
            await seed_companies(session)
            await seed_bugs(session)
            print("\nDatabase seeding completed successfully!")
        except Exception as e:
            print(f"\nError during seeding: {e}")
            await session.rollback()
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
