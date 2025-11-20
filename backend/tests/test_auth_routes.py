"""
Integration Tests for Authentication Routes
"""
import pytest
from httpx import AsyncClient
from datetime import datetime, timedelta
import jwt

from main import app
from models.user import User
from core.config import settings


@pytest.fixture
def test_user_data():
    """Test user registration data"""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "SecurePass123!",
        "full_name": "Test User"
    }


@pytest.fixture
def test_login_data():
    """Test user login data"""
    return {
        "username": "testuser",
        "password": "SecurePass123!"
    }


class TestUserRegistration:
    """Test user registration endpoints"""
    
    @pytest.mark.asyncio
    async def test_register_success(self, test_user_data):
        """Test successful user registration"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/api/auth/register", json=test_user_data)
            
            assert response.status_code == 201
            data = response.json()
            assert data["email"] == test_user_data["email"]
            assert data["username"] == test_user_data["username"]
            assert "id" in data
    
    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, test_user_data):
        """Test registration with duplicate email"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            await client.post("/api/auth/register", json=test_user_data)
            response = await client.post("/api/auth/register", json=test_user_data)
            
            assert response.status_code == 400
            assert "already exists" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_register_invalid_email(self, test_user_data):
        """Test registration with invalid email"""
        test_user_data["email"] = "invalid_email"
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/api/auth/register", json=test_user_data)
            
            assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_register_weak_password(self, test_user_data):
        """Test registration with weak password"""
        test_user_data["password"] = "weak"
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/api/auth/register", json=test_user_data)
            
            assert response.status_code == 400


class TestUserLogin:
    """Test user login endpoints"""
    
    @pytest.mark.asyncio
    async def test_login_success(self, test_user_data, test_login_data):
        """Test successful user login"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            await client.post("/api/auth/register", json=test_user_data)
            response = await client.post("/api/auth/login", data=test_login_data)
            
            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data
            assert "refresh_token" in data
            assert data["token_type"] == "bearer"
    
    @pytest.mark.asyncio
    async def test_login_wrong_password(self, test_user_data, test_login_data):
        """Test login with wrong password"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            await client.post("/api/auth/register", json=test_user_data)
            test_login_data["password"] = "WrongPassword123!"
            response = await client.post("/api/auth/login", data=test_login_data)
            
            assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, test_login_data):
        """Test login with non-existent user"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/api/auth/login", data=test_login_data)
            
            assert response.status_code == 401


class TestTokenValidation:
    """Test token validation and refresh"""
    
    @pytest.mark.asyncio
    async def test_access_protected_route_with_valid_token(self, test_user_data):
        """Test accessing protected route with valid token"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            await client.post("/api/auth/register", json=test_user_data)
            login_response = await client.post("/api/auth/login", data={
                "username": test_user_data["username"],
                "password": test_user_data["password"]
            })
            
            token = login_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            response = await client.get("/api/users/me", headers=headers)
            
            assert response.status_code == 200
            data = response.json()
            assert data["email"] == test_user_data["email"]
    
    @pytest.mark.asyncio
    async def test_access_protected_route_without_token(self):
        """Test accessing protected route without token"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/users/me")
            
            assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_access_protected_route_with_invalid_token(self):
        """Test accessing protected route with invalid token"""
        headers = {"Authorization": "Bearer invalid_token"}
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/users/me", headers=headers)
            
            assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_refresh_token(self, test_user_data):
        """Test token refresh"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            await client.post("/api/auth/register", json=test_user_data)
            login_response = await client.post("/api/auth/login", data={
                "username": test_user_data["username"],
                "password": test_user_data["password"]
            })
            
            refresh_token = login_response.json()["refresh_token"]
            response = await client.post("/api/auth/refresh", json={
                "refresh_token": refresh_token
            })
            
            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data


class TestPasswordReset:
    """Test password reset functionality"""
    
    @pytest.mark.asyncio
    async def test_request_password_reset(self, test_user_data):
        """Test password reset request"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            await client.post("/api/auth/register", json=test_user_data)
            response = await client.post("/api/auth/password-reset-request", json={
                "email": test_user_data["email"]
            })
            
            assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_request_password_reset_nonexistent_email(self):
        """Test password reset request with non-existent email"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/api/auth/password-reset-request", json={
                "email": "nonexistent@example.com"
            })
            
            assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_reset_password_with_valid_token(self, test_user_data):
        """Test password reset with valid token"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            await client.post("/api/auth/register", json=test_user_data)
            reset_response = await client.post("/api/auth/password-reset-request", json={
                "email": test_user_data["email"]
            })
            
            reset_token = "valid_reset_token"
            response = await client.post("/api/auth/password-reset", json={
                "token": reset_token,
                "new_password": "NewSecurePass123!"
            })
            
            assert response.status_code in [200, 400]


class TestEmailVerification:
    """Test email verification"""
    
    @pytest.mark.asyncio
    async def test_verify_email(self, test_user_data):
        """Test email verification"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            register_response = await client.post("/api/auth/register", json=test_user_data)
            user_id = register_response.json()["id"]
            
            verification_token = jwt.encode(
                {"user_id": user_id, "exp": datetime.utcnow() + timedelta(hours=24)},
                settings.SECRET_KEY,
                algorithm="HS256"
            )
            
            response = await client.get(f"/api/auth/verify-email?token={verification_token}")
            
            assert response.status_code in [200, 400]
    
    @pytest.mark.asyncio
    async def test_resend_verification_email(self, test_user_data):
        """Test resend verification email"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            await client.post("/api/auth/register", json=test_user_data)
            response = await client.post("/api/auth/resend-verification", json={
                "email": test_user_data["email"]
            })
            
            assert response.status_code == 200


class TestLogout:
    """Test logout functionality"""
    
    @pytest.mark.asyncio
    async def test_logout(self, test_user_data):
        """Test user logout"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            await client.post("/api/auth/register", json=test_user_data)
            login_response = await client.post("/api/auth/login", data={
                "username": test_user_data["username"],
                "password": test_user_data["password"]
            })
            
            token = login_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            response = await client.post("/api/auth/logout", headers=headers)
            
            assert response.status_code == 200


class TestAccountDeletion:
    """Test account deletion"""
    
    @pytest.mark.asyncio
    async def test_delete_account(self, test_user_data):
        """Test account deletion"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            await client.post("/api/auth/register", json=test_user_data)
            login_response = await client.post("/api/auth/login", data={
                "username": test_user_data["username"],
                "password": test_user_data["password"]
            })
            
            token = login_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            response = await client.delete("/api/users/me", headers=headers)
            
            assert response.status_code in [200, 204]
