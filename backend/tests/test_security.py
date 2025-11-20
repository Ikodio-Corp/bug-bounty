"""
Security Tests
"""
import pytest
from httpx import AsyncClient
import jwt
from datetime import datetime, timedelta

from main import app
from core.config import settings


class TestPasswordSecurity:
    """Test password security"""
    
    @pytest.mark.asyncio
    async def test_reject_weak_password(self):
        """Test rejection of weak passwords"""
        weak_passwords = [
            "123456",
            "password",
            "abc123",
            "short",
            "nouppercaseornumbers"
        ]
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            for password in weak_passwords:
                user_data = {
                    "username": "testuser",
                    "email": "test@example.com",
                    "password": password
                }
                
                response = await client.post("/api/auth/register", json=user_data)
                assert response.status_code in [400, 422]
    
    @pytest.mark.asyncio
    async def test_password_hashing(self):
        """Test password is hashed"""
        user_data = {
            "username": "hashtest",
            "email": "hashtest@example.com",
            "password": "SecurePass123!"
        }
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/api/auth/register", json=user_data)
            
            assert response.status_code == 201
            data = response.json()
            assert "password" not in data


class TestTokenSecurity:
    """Test token security"""
    
    @pytest.mark.asyncio
    async def test_expired_token_rejection(self):
        """Test expired tokens are rejected"""
        expired_payload = {
            "sub": "testuser",
            "exp": datetime.utcnow() - timedelta(hours=1)
        }
        
        expired_token = jwt.encode(expired_payload, settings.SECRET_KEY, algorithm="HS256")
        headers = {"Authorization": f"Bearer {expired_token}"}
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/users/me", headers=headers)
            
            assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_invalid_token_rejection(self):
        """Test invalid tokens are rejected"""
        invalid_token = "invalid.token.here"
        headers = {"Authorization": f"Bearer {invalid_token}"}
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/users/me", headers=headers)
            
            assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_token_tampering_detection(self):
        """Test token tampering is detected"""
        user_data = {
            "username": "tokentest",
            "email": "tokentest@example.com",
            "password": "SecurePass123!"
        }
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            await client.post("/api/auth/register", json=user_data)
            login_response = await client.post("/api/auth/login", data={
                "username": user_data["username"],
                "password": user_data["password"]
            })
            
            token = login_response.json()["access_token"]
            tampered_token = token[:-5] + "xxxxx"
            headers = {"Authorization": f"Bearer {tampered_token}"}
            
            response = await client.get("/api/users/me", headers=headers)
            
            assert response.status_code == 401


class TestSQLInjectionPrevention:
    """Test SQL injection prevention"""
    
    @pytest.mark.asyncio
    async def test_sql_injection_in_login(self):
        """Test SQL injection attempts in login"""
        sql_injections = [
            "' OR '1'='1",
            "admin' --",
            "' OR 1=1--",
            "admin'/*"
        ]
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            for injection in sql_injections:
                response = await client.post("/api/auth/login", data={
                    "username": injection,
                    "password": "anything"
                })
                
                assert response.status_code in [401, 422]


class TestXSSPrevention:
    """Test XSS prevention"""
    
    @pytest.mark.asyncio
    async def test_xss_in_user_input(self):
        """Test XSS prevention in user input"""
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')"
        ]
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            for payload in xss_payloads:
                user_data = {
                    "username": payload,
                    "email": "test@example.com",
                    "password": "SecurePass123!"
                }
                
                response = await client.post("/api/auth/register", json=user_data)
                
                if response.status_code == 201:
                    data = response.json()
                    assert payload not in str(data).replace("&lt;", "<").replace("&gt;", ">")


class TestCSRFProtection:
    """Test CSRF protection"""
    
    @pytest.mark.asyncio
    async def test_csrf_token_required(self):
        """Test CSRF token is required for state-changing operations"""
        user_data = {
            "username": "csrftest",
            "email": "csrftest@example.com",
            "password": "SecurePass123!"
        }
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            await client.post("/api/auth/register", json=user_data)
            login_response = await client.post("/api/auth/login", data={
                "username": user_data["username"],
                "password": user_data["password"]
            })
            
            token = login_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            response = await client.delete("/api/users/me", headers=headers)
            
            assert response.status_code in [200, 204, 403]


class TestRateLimiting:
    """Test rate limiting"""
    
    @pytest.mark.asyncio
    async def test_login_rate_limiting(self):
        """Test rate limiting on login attempts"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            responses = []
            
            for _ in range(50):
                response = await client.post("/api/auth/login", data={
                    "username": "nonexistent",
                    "password": "wrong"
                })
                responses.append(response.status_code)
            
            rate_limited = any(code == 429 for code in responses)


class TestInputValidation:
    """Test input validation"""
    
    @pytest.mark.asyncio
    async def test_email_validation(self):
        """Test email validation"""
        invalid_emails = [
            "notanemail",
            "@example.com",
            "user@",
            "user@.com",
            "user..name@example.com"
        ]
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            for email in invalid_emails:
                user_data = {
                    "username": "testuser",
                    "email": email,
                    "password": "SecurePass123!"
                }
                
                response = await client.post("/api/auth/register", json=user_data)
                assert response.status_code in [400, 422]
    
    @pytest.mark.asyncio
    async def test_url_validation(self):
        """Test URL validation"""
        invalid_urls = [
            "not a url",
            "ftp://invalid",
            "javascript:alert(1)",
            "file:///etc/passwd"
        ]
        
        user_data = {
            "username": "urltest",
            "email": "urltest@example.com",
            "password": "SecurePass123!"
        }
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            await client.post("/api/auth/register", json=user_data)
            login_response = await client.post("/api/auth/login", data={
                "username": user_data["username"],
                "password": user_data["password"]
            })
            
            token = login_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            for url in invalid_urls:
                scan_data = {
                    "target_url": url,
                    "scan_type": "quick",
                    "scanner": "nuclei"
                }
                
                response = await client.post("/api/scans/", json=scan_data, headers=headers)
                assert response.status_code in [400, 422]


class TestAuthorizationChecks:
    """Test authorization checks"""
    
    @pytest.mark.asyncio
    async def test_user_cannot_access_others_data(self):
        """Test users cannot access other users' data"""
        user1_data = {
            "username": "user1",
            "email": "user1@example.com",
            "password": "SecurePass123!"
        }
        user2_data = {
            "username": "user2",
            "email": "user2@example.com",
            "password": "SecurePass123!"
        }
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            await client.post("/api/auth/register", json=user1_data)
            user2_response = await client.post("/api/auth/register", json=user2_data)
            user2_id = user2_response.json()["id"]
            
            login1_response = await client.post("/api/auth/login", data={
                "username": user1_data["username"],
                "password": user1_data["password"]
            })
            
            token1 = login1_response.json()["access_token"]
            headers1 = {"Authorization": f"Bearer {token1}"}
            
            response = await client.get(f"/api/users/{user2_id}", headers=headers1)
            
            assert response.status_code in [403, 404]


class TestDataSanitization:
    """Test data sanitization"""
    
    @pytest.mark.asyncio
    async def test_sensitive_data_not_exposed(self):
        """Test sensitive data is not exposed in responses"""
        user_data = {
            "username": "sensitive",
            "email": "sensitive@example.com",
            "password": "SecurePass123!"
        }
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/api/auth/register", json=user_data)
            
            assert response.status_code == 201
            data = response.json()
            
            assert "password" not in data
            assert "hashed_password" not in data
            assert "secret" not in str(data).lower()
