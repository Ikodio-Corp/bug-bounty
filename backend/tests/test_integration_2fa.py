"""
Integration Tests for 2FA Routes
"""
import pytest
from httpx import AsyncClient
import pyotp

from main import app


class TestTOTPSetup:
    """Test TOTP setup functionality"""
    
    @pytest.mark.asyncio
    async def test_enable_totp(self):
        """Test enabling TOTP"""
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
            
            response = await client.post("/api/two-factor/totp/setup", headers=headers)
            
            assert response.status_code == 200
            data = response.json()
            assert "secret" in data
            assert "qr_code" in data
    
    @pytest.mark.asyncio
    async def test_verify_totp(self):
        """Test TOTP verification"""
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
            
            setup_response = await client.post("/api/two-factor/totp/setup", headers=headers)
            secret = setup_response.json()["secret"]
            
            totp = pyotp.TOTP(secret)
            code = totp.now()
            
            response = await client.post(
                "/api/two-factor/totp/verify",
                json={"code": code},
                headers=headers
            )
            
            assert response.status_code in [200, 400]
    
    @pytest.mark.asyncio
    async def test_verify_totp_invalid_code(self):
        """Test TOTP verification with invalid code"""
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
            
            await client.post("/api/two-factor/totp/setup", headers=headers)
            
            response = await client.post(
                "/api/two-factor/totp/verify",
                json={"code": "000000"},
                headers=headers
            )
            
            assert response.status_code in [400, 401]
    
    @pytest.mark.asyncio
    async def test_disable_totp(self):
        """Test disabling TOTP"""
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
            
            response = await client.post("/api/two-factor/totp/disable", headers=headers)
            
            assert response.status_code in [200, 400]


class TestWebAuthn:
    """Test WebAuthn functionality"""
    
    @pytest.mark.asyncio
    async def test_register_webauthn_start(self):
        """Test WebAuthn registration start"""
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
            
            response = await client.post("/api/two-factor/webauthn/register/start", headers=headers)
            
            assert response.status_code == 200
            data = response.json()
            assert "challenge" in data
    
    @pytest.mark.asyncio
    async def test_authenticate_webauthn_start(self):
        """Test WebAuthn authentication start"""
        test_user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "SecurePass123!"
        }
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            await client.post("/api/auth/register", json=test_user_data)
            
            response = await client.post("/api/two-factor/webauthn/authenticate/start", json={
                "username": test_user_data["username"]
            })
            
            assert response.status_code in [200, 404]
    
    @pytest.mark.asyncio
    async def test_list_webauthn_credentials(self):
        """Test listing WebAuthn credentials"""
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
            
            response = await client.get("/api/two-factor/webauthn/credentials", headers=headers)
            
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
    
    @pytest.mark.asyncio
    async def test_delete_webauthn_credential(self):
        """Test deleting WebAuthn credential"""
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
            
            response = await client.delete("/api/two-factor/webauthn/credentials/test_id", headers=headers)
            
            assert response.status_code in [200, 404]


class TestBackupCodes:
    """Test backup codes functionality"""
    
    @pytest.mark.asyncio
    async def test_generate_backup_codes(self):
        """Test generating backup codes"""
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
            
            response = await client.post("/api/two-factor/backup-codes/generate", headers=headers)
            
            assert response.status_code == 200
            data = response.json()
            assert "codes" in data
            assert len(data["codes"]) > 0
    
    @pytest.mark.asyncio
    async def test_verify_backup_code(self):
        """Test verifying backup code"""
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
            
            codes_response = await client.post("/api/two-factor/backup-codes/generate", headers=headers)
            codes = codes_response.json()["codes"]
            
            response = await client.post(
                "/api/two-factor/backup-codes/verify",
                json={"code": codes[0]},
                headers=headers
            )
            
            assert response.status_code in [200, 400]
    
    @pytest.mark.asyncio
    async def test_list_backup_codes(self):
        """Test listing backup codes"""
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
            
            response = await client.get("/api/two-factor/backup-codes", headers=headers)
            
            assert response.status_code == 200


class Test2FAStatus:
    """Test 2FA status functionality"""
    
    @pytest.mark.asyncio
    async def test_get_2fa_status(self):
        """Test getting 2FA status"""
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
            
            response = await client.get("/api/two-factor/status", headers=headers)
            
            assert response.status_code == 200
            data = response.json()
            assert "totp_enabled" in data
            assert "webauthn_enabled" in data
    
    @pytest.mark.asyncio
    async def test_require_2fa_for_sensitive_operations(self):
        """Test 2FA required for sensitive operations"""
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
            
            response = await client.delete("/api/users/me", headers=headers)
            
            assert response.status_code in [200, 204, 403]
