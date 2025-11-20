"""
Unit Tests for Bug Service
"""

import pytest
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from services.bug_service import BugService
from models.bug import Bug
from models.user import User
from core.database import Base


DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(DATABASE_URL, echo=False)
async_session_maker = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


@pytest.fixture
async def db_session():
    """Create test database session"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with async_session_maker() as session:
        yield session
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def test_user(db_session: AsyncSession):
    """Create test user"""
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password="hashedpassword",
        reputation_score=100
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.mark.asyncio
async def test_create_bug(db_session: AsyncSession, test_user: User):
    """Test bug creation"""
    bug_service = BugService()
    
    bug_data = {
        "title": "XSS Vulnerability",
        "description": "Found XSS in search",
        "severity": "high",
        "bug_type": "xss",
        "target_url": "https://example.com",
        "proof_of_concept": "<script>alert(1)</script>"
    }
    
    bug = await bug_service.create_bug(db_session, test_user.id, bug_data)
    
    assert bug.id is not None
    assert bug.title == "XSS Vulnerability"
    assert bug.status == "pending"
    assert bug.reporter_id == test_user.id


@pytest.mark.asyncio
async def test_get_bug_by_id(db_session: AsyncSession, test_user: User):
    """Test retrieving bug by ID"""
    bug_service = BugService()
    
    bug = Bug(
        title="Test Bug",
        description="Test description",
        severity="medium",
        bug_type="sqli",
        status="pending",
        reporter_id=test_user.id
    )
    db_session.add(bug)
    await db_session.commit()
    await db_session.refresh(bug)
    
    retrieved_bug = await bug_service.get_bug_by_id(db_session, bug.id)
    
    assert retrieved_bug is not None
    assert retrieved_bug.id == bug.id
    assert retrieved_bug.title == "Test Bug"


@pytest.mark.asyncio
async def test_update_bug_status(db_session: AsyncSession, test_user: User):
    """Test updating bug status"""
    bug_service = BugService()
    
    bug = Bug(
        title="Test Bug",
        description="Test description",
        severity="high",
        bug_type="rce",
        status="pending",
        reporter_id=test_user.id
    )
    db_session.add(bug)
    await db_session.commit()
    await db_session.refresh(bug)
    
    updated_bug = await bug_service.update_bug_status(
        db_session,
        bug.id,
        "validated"
    )
    
    assert updated_bug.status == "validated"


@pytest.mark.asyncio
async def test_list_bugs_with_filters(db_session: AsyncSession, test_user: User):
    """Test listing bugs with filters"""
    bug_service = BugService()
    
    bugs = [
        Bug(
            title=f"Bug {i}",
            description="Description",
            severity="high" if i % 2 == 0 else "medium",
            bug_type="xss",
            status="pending" if i % 2 == 0 else "validated",
            reporter_id=test_user.id
        )
        for i in range(5)
    ]
    
    for bug in bugs:
        db_session.add(bug)
    await db_session.commit()
    
    pending_bugs = await bug_service.list_bugs(
        db_session,
        status="pending"
    )
    
    assert len(pending_bugs) == 3
    assert all(bug.status == "pending" for bug in pending_bugs)


@pytest.mark.asyncio
async def test_delete_bug(db_session: AsyncSession, test_user: User):
    """Test bug deletion"""
    bug_service = BugService()
    
    bug = Bug(
        title="Bug to Delete",
        description="Will be deleted",
        severity="low",
        bug_type="csrf",
        status="rejected",
        reporter_id=test_user.id
    )
    db_session.add(bug)
    await db_session.commit()
    await db_session.refresh(bug)
    
    success = await bug_service.delete_bug(db_session, bug.id)
    
    assert success is True
    
    deleted_bug = await bug_service.get_bug_by_id(db_session, bug.id)
    assert deleted_bug is None
