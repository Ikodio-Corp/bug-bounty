"""
Tests Configuration and Fixtures
"""

import pytest
import asyncio
from typing import Generator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from httpx import AsyncClient

from core.database import Base
from models.user import User
from models.bug import Bug
from main import app


TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def anyio_backend():
    """Configure anyio backend for async tests"""
    return "asyncio"


@pytest.fixture
async def db_engine():
    """Create test database engine"""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture
async def db_session(db_engine):
    """Create test database session"""
    async_session = sessionmaker(
        db_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session


@pytest.fixture
async def client():
    """Create test HTTP client"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def test_user_data():
    """Standard test user data"""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "SecurePass123!",
        "full_name": "Test User"
    }


@pytest.fixture
async def authenticated_client(client, test_user_data):
    """Create authenticated HTTP client"""
    await client.post("/api/auth/register", json=test_user_data)
    login_response = await client.post("/api/auth/login", data={
        "username": test_user_data["username"],
        "password": test_user_data["password"]
    })
    
    token = login_response.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"
    
    return client


@pytest.fixture
def mock_stripe():
    """Mock Stripe client"""
    from unittest.mock import AsyncMock
    return AsyncMock()


@pytest.fixture
def mock_oauth():
    """Mock OAuth providers"""
    from unittest.mock import AsyncMock
    return AsyncMock()

