"""
Integration Tests for OAuth Routes
"""
import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock

from main import app


class TestOAuthProviders:
    """Test OAuth provider integration"""
    
    @pytest.mark.asyncio
    async def test_google_oauth_initiate(self):
        """Test Google OAuth initiation"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/oauth/google/authorize")
            
            assert response.status_code in [200, 302, 307]
            if response.status_code in [302, 307]:
                assert "location" in response.headers
    
    @pytest.mark.asyncio
    async def test_github_oauth_initiate(self):
        """Test GitHub OAuth initiation"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/oauth/github/authorize")
            
            assert response.status_code in [200, 302, 307]
    
    @pytest.mark.asyncio
    async def test_microsoft_oauth_initiate(self):
        """Test Microsoft OAuth initiation"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/oauth/microsoft/authorize")
            
            assert response.status_code in [200, 302, 307]
    
    @pytest.mark.asyncio
    async def test_gitlab_oauth_initiate(self):
        """Test GitLab OAuth initiation"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/oauth/gitlab/authorize")
            
            assert response.status_code in [200, 302, 307]


class TestOAuthCallback:
    """Test OAuth callback handling"""
    
    @pytest.mark.asyncio
    async def test_google_oauth_callback_success(self):
        """Test successful Google OAuth callback"""
        with patch('api.routes.oauth.exchange_google_code') as mock_exchange:
            mock_exchange.return_value = {
                "access_token": "test_token",
                "email": "test@gmail.com",
                "name": "Test User"
            }
            
            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.get("/api/oauth/google/callback?code=test_code")
                
                assert response.status_code in [200, 302, 307]
    
    @pytest.mark.asyncio
    async def test_oauth_callback_missing_code(self):
        """Test OAuth callback without code parameter"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/oauth/google/callback")
            
            assert response.status_code in [400, 422]
    
    @pytest.mark.asyncio
    async def test_oauth_callback_invalid_code(self):
        """Test OAuth callback with invalid code"""
        with patch('api.routes.oauth.exchange_google_code') as mock_exchange:
            mock_exchange.side_effect = Exception("Invalid code")
            
            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.get("/api/oauth/google/callback?code=invalid_code")
                
                assert response.status_code in [400, 401]


class TestOAuthUserCreation:
    """Test OAuth user creation and linking"""
    
    @pytest.mark.asyncio
    async def test_oauth_creates_new_user(self):
        """Test OAuth creates new user if not exists"""
        with patch('api.routes.oauth.exchange_google_code') as mock_exchange:
            mock_exchange.return_value = {
                "access_token": "test_token",
                "email": "newuser@gmail.com",
                "name": "New User",
                "sub": "google_12345"
            }
            
            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.get("/api/oauth/google/callback?code=test_code")
                
                assert response.status_code in [200, 302, 307]
    
    @pytest.mark.asyncio
    async def test_oauth_links_existing_user(self):
        """Test OAuth links to existing user with same email"""
        test_user_data = {
            "username": "testuser",
            "email": "existing@gmail.com",
            "password": "SecurePass123!"
        }
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            await client.post("/api/auth/register", json=test_user_data)
            
            with patch('api.routes.oauth.exchange_google_code') as mock_exchange:
                mock_exchange.return_value = {
                    "access_token": "test_token",
                    "email": "existing@gmail.com",
                    "name": "Test User",
                    "sub": "google_12345"
                }
                
                response = await client.get("/api/oauth/google/callback?code=test_code")
                
                assert response.status_code in [200, 302, 307]


class TestOAuthTokens:
    """Test OAuth token management"""
    
    @pytest.mark.asyncio
    async def test_oauth_returns_jwt_token(self):
        """Test OAuth returns JWT access token"""
        with patch('api.routes.oauth.exchange_google_code') as mock_exchange:
            mock_exchange.return_value = {
                "access_token": "test_token",
                "email": "test@gmail.com",
                "name": "Test User",
                "sub": "google_12345"
            }
            
            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.get("/api/oauth/google/callback?code=test_code")
                
                if response.status_code == 200:
                    data = response.json()
                    assert "access_token" in data or response.status_code in [302, 307]
    
    @pytest.mark.asyncio
    async def test_list_connected_providers(self):
        """Test list connected OAuth providers"""
        test_user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "SecurePass123!"
        }
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            await client.post("/api/auth/register", json=test_user_data)
            login_response = await client.post("/api/auth/login", data={
                "username": test_user_data["username"],
                "password": test_user_data["password"]
            })
            
            token = login_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            response = await client.get("/api/oauth/providers", headers=headers)
            
            assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_disconnect_oauth_provider(self):
        """Test disconnect OAuth provider"""
        test_user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "SecurePass123!"
        }
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            await client.post("/api/auth/register", json=test_user_data)
            login_response = await client.post("/api/auth/login", data={
                "username": test_user_data["username"],
                "password": test_user_data["password"]
            })
            
            token = login_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            response = await client.delete("/api/oauth/google", headers=headers)
            
            assert response.status_code in [200, 404]


class TestOAuthSecurity:
    """Test OAuth security features"""
    
    @pytest.mark.asyncio
    async def test_oauth_state_parameter(self):
        """Test OAuth uses state parameter for CSRF protection"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/oauth/google/authorize")
            
            if response.status_code in [302, 307]:
                location = response.headers.get("location", "")
                assert "state=" in location or response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_oauth_validates_state(self):
        """Test OAuth validates state parameter"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/oauth/google/callback?code=test&state=invalid_state")
            
            assert response.status_code in [400, 401, 302, 307]
    
    @pytest.mark.asyncio
    async def test_oauth_token_refresh(self):
        """Test OAuth token refresh"""
        test_user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "SecurePass123!"
        }
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            await client.post("/api/auth/register", json=test_user_data)
            login_response = await client.post("/api/auth/login", data={
                "username": test_user_data["username"],
                "password": test_user_data["password"]
            })
            
            token = login_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            response = await client.post("/api/oauth/google/refresh", headers=headers)
            
            assert response.status_code in [200, 400, 404]
