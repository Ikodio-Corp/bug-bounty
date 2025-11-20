"""
Unit Tests for Scan Service
"""

import pytest
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from services.scan_service import ScanService
from models.scan import Scan
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
        username="scanuser",
        email="scan@example.com",
        hashed_password="hashedpassword",
        reputation_score=150
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.mark.asyncio
async def test_create_scan(db_session: AsyncSession, test_user: User):
    """Test scan creation"""
    scan_service = ScanService()
    
    scan_data = {
        "target_url": "https://example.com",
        "scan_type": "quick"
    }
    
    scan = await scan_service.create_scan(db_session, test_user.id, scan_data)
    
    assert scan.id is not None
    assert scan.target_url == "https://example.com"
    assert scan.status == "pending"
    assert scan.user_id == test_user.id


@pytest.mark.asyncio
async def test_update_scan_status(db_session: AsyncSession, test_user: User):
    """Test updating scan status"""
    scan_service = ScanService()
    
    scan = Scan(
        target_url="https://test.com",
        scan_type="deep",
        status="running",
        user_id=test_user.id
    )
    db_session.add(scan)
    await db_session.commit()
    await db_session.refresh(scan)
    
    updated_scan = await scan_service.update_scan_status(
        db_session,
        scan.id,
        "completed",
        vulnerabilities_found=5,
        duration_seconds=87
    )
    
    assert updated_scan.status == "completed"
    assert updated_scan.vulnerabilities_found == 5
    assert updated_scan.duration_seconds == 87


@pytest.mark.asyncio
async def test_get_active_scans(db_session: AsyncSession, test_user: User):
    """Test getting active scans"""
    scan_service = ScanService()
    
    scans = [
        Scan(
            target_url=f"https://test{i}.com",
            scan_type="quick",
            status="running" if i % 2 == 0 else "completed",
            user_id=test_user.id
        )
        for i in range(6)
    ]
    
    for scan in scans:
        db_session.add(scan)
    await db_session.commit()
    
    active_scans = await scan_service.get_active_scans(db_session)
    
    assert len(active_scans) == 3
    assert all(scan.status == "running" for scan in active_scans)


@pytest.mark.asyncio
async def test_list_user_scans(db_session: AsyncSession, test_user: User):
    """Test listing user scans"""
    scan_service = ScanService()
    
    other_user = User(
        username="otheruser",
        email="other@example.com",
        hashed_password="hashedpassword"
    )
    db_session.add(other_user)
    await db_session.commit()
    await db_session.refresh(other_user)
    
    for i in range(3):
        scan = Scan(
            target_url=f"https://test{i}.com",
            scan_type="quick",
            status="completed",
            user_id=test_user.id
        )
        db_session.add(scan)
    
    for i in range(2):
        scan = Scan(
            target_url=f"https://other{i}.com",
            scan_type="quick",
            status="completed",
            user_id=other_user.id
        )
        db_session.add(scan)
    
    await db_session.commit()
    
    user_scans = await scan_service.list_user_scans(db_session, test_user.id)
    
    assert len(user_scans) == 3
    assert all(scan.user_id == test_user.id for scan in user_scans)
