"""
Integration Tests for API Routes
"""

import pytest
from httpx import AsyncClient
from fastapi import status

from main import app


@pytest.fixture
async def async_client():
    """Create async HTTP client"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
async def auth_token(async_client: AsyncClient):
    """Get authentication token"""
    register_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123"
    }
    
    await async_client.post("/api/auth/register", json=register_data)
    
    login_data = {
        "username": "testuser",
        "password": "testpass123"
    }
    
    response = await async_client.post("/api/auth/login", data=login_data)
    return response.json()["access_token"]


@pytest.mark.asyncio
async def test_register_user(async_client: AsyncClient):
    """Test user registration"""
    user_data = {
        "username": "newuser",
        "email": "new@example.com",
        "password": "password123"
    }
    
    response = await async_client.post("/api/auth/register", json=user_data)
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["username"] == "newuser"
    assert data["email"] == "new@example.com"


@pytest.mark.asyncio
async def test_login_user(async_client: AsyncClient):
    """Test user login"""
    register_data = {
        "username": "loginuser",
        "email": "login@example.com",
        "password": "loginpass123"
    }
    
    await async_client.post("/api/auth/register", json=register_data)
    
    login_data = {
        "username": "loginuser",
        "password": "loginpass123"
    }
    
    response = await async_client.post("/api/auth/login", data=login_data)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_create_bug_authenticated(async_client: AsyncClient, auth_token: str):
    """Test creating bug with authentication"""
    bug_data = {
        "title": "SQL Injection",
        "description": "Found SQLi in login form",
        "severity": "critical",
        "bug_type": "sqli",
        "target_url": "https://example.com/login",
        "proof_of_concept": "admin' OR '1'='1"
    }
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = await async_client.post(
        "/api/bugs/report",
        json=bug_data,
        headers=headers
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["title"] == "SQL Injection"
    assert data["status"] == "pending"


@pytest.mark.asyncio
async def test_list_bugs(async_client: AsyncClient, auth_token: str):
    """Test listing bugs"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    for i in range(3):
        bug_data = {
            "title": f"Bug {i}",
            "description": "Description",
            "severity": "high",
            "bug_type": "xss",
            "target_url": "https://example.com"
        }
        await async_client.post("/api/bugs/report", json=bug_data, headers=headers)
    
    response = await async_client.get("/api/bugs/list", headers=headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["bugs"]) == 3


@pytest.mark.asyncio
async def test_start_scan(async_client: AsyncClient, auth_token: str):
    """Test starting a scan"""
    scan_data = {
        "target_url": "https://example.com",
        "scan_type": "quick"
    }
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = await async_client.post(
        "/api/scans/start",
        json=scan_data,
        headers=headers
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["target_url"] == "https://example.com"
    assert data["status"] == "pending"


@pytest.mark.asyncio
async def test_unauthorized_access(async_client: AsyncClient):
    """Test unauthorized access to protected endpoint"""
    response = await async_client.get("/api/bugs/list")
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
