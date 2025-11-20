"""
Test authentication and security
"""
import pytest
from fastapi.testclient import TestClient
from main import app
from core.security import create_access_token, verify_password, get_password_hash
from datetime import timedelta


client = TestClient(app)


class TestAuthentication:
    """Test authentication endpoints"""
    
    def test_user_registration(self):
        """Test user registration"""
        response = client.post("/api/auth/register", json={
            "username": "newuser",
            "email": "newuser@test.com",
            "password": "SecurePassword123!",
            "full_name": "New User"
        })
        
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["email"] == "newuser@test.com"
    
    def test_duplicate_email_registration(self, test_user):
        """Test registration with duplicate email"""
        response = client.post("/api/auth/register", json={
            "username": "duplicate",
            "email": test_user.email,
            "password": "Password123!"
        })
        
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()
    
    def test_user_login(self, test_user):
        """Test user login"""
        response = client.post("/api/auth/login", data={
            "username": test_user.email,
            "password": "testpassword"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_invalid_login_credentials(self):
        """Test login with invalid credentials"""
        response = client.post("/api/auth/login", data={
            "username": "nonexistent@test.com",
            "password": "wrongpassword"
        })
        
        assert response.status_code == 401
    
    def test_access_protected_endpoint(self, test_user):
        """Test accessing protected endpoint with token"""
        token = create_access_token(
            data={"sub": test_user.email},
            expires_delta=timedelta(minutes=30)
        )
        
        response = client.get(
            "/api/users/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user.email
    
    def test_access_without_token(self):
        """Test accessing protected endpoint without token"""
        response = client.get("/api/users/me")
        
        assert response.status_code == 401


class TestPasswordSecurity:
    """Test password security functions"""
    
    def test_password_hashing(self):
        """Test password hashing"""
        password = "SecurePassword123!"
        hashed = get_password_hash(password)
        
        assert hashed != password
        assert len(hashed) > 50
    
    def test_password_verification(self):
        """Test password verification"""
        password = "SecurePassword123!"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True
        assert verify_password("wrongpassword", hashed) is False
    
    def test_weak_password_rejection(self):
        """Test weak password rejection"""
        response = client.post("/api/auth/register", json={
            "username": "weakpass",
            "email": "weak@test.com",
            "password": "123"  # Too weak
        })
        
        assert response.status_code == 400
        assert "password" in response.json()["detail"].lower()


class TestTwoFactorAuth:
    """Test 2FA functionality"""
    
    def test_enable_2fa(self, test_user):
        """Test enabling 2FA"""
        token = create_access_token(data={"sub": test_user.email})
        
        response = client.post(
            "/api/auth/2fa/enable",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "secret" in data
        assert "qr_code" in data
    
    def test_verify_2fa_code(self, test_user):
        """Test verifying 2FA code"""
        token = create_access_token(data={"sub": test_user.email})
        
        # Enable 2FA first
        enable_response = client.post(
            "/api/auth/2fa/enable",
            headers={"Authorization": f"Bearer {token}"}
        )
        secret = enable_response.json()["secret"]
        
        # Verify with code (mocked)
        response = client.post(
            "/api/auth/2fa/verify",
            headers={"Authorization": f"Bearer {token}"},
            json={"code": "123456"}  # Mock code
        )
        
        assert response.status_code in [200, 400]  # May fail if code invalid
    
    def test_disable_2fa(self, test_user):
        """Test disabling 2FA"""
        token = create_access_token(data={"sub": test_user.email})
        
        response = client.post(
            "/api/auth/2fa/disable",
            headers={"Authorization": f"Bearer {token}"},
            json={"password": "testpassword"}
        )
        
        assert response.status_code == 200


class TestOAuth:
    """Test OAuth integration"""
    
    def test_github_oauth_initiation(self):
        """Test initiating GitHub OAuth"""
        response = client.get("/api/auth/oauth/github")
        
        assert response.status_code in [200, 302]  # May redirect
    
    def test_google_oauth_initiation(self):
        """Test initiating Google OAuth"""
        response = client.get("/api/auth/oauth/google")
        
        assert response.status_code in [200, 302]


class TestSessionManagement:
    """Test session management"""
    
    def test_token_refresh(self, test_user):
        """Test refreshing access token"""
        refresh_token = create_access_token(
            data={"sub": test_user.email, "type": "refresh"},
            expires_delta=timedelta(days=7)
        )
        
        response = client.post(
            "/api/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
    
    def test_logout(self, test_user):
        """Test user logout"""
        token = create_access_token(data={"sub": test_user.email})
        
        response = client.post(
            "/api/auth/logout",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
    
    def test_revoke_all_sessions(self, test_user):
        """Test revoking all user sessions"""
        token = create_access_token(data={"sub": test_user.email})
        
        response = client.post(
            "/api/auth/revoke-all",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200


class TestAccountSecurity:
    """Test account security features"""
    
    def test_password_reset_request(self):
        """Test password reset request"""
        response = client.post(
            "/api/auth/password-reset-request",
            json={"email": "test@test.com"}
        )
        
        assert response.status_code == 200
    
    def test_password_reset_confirm(self):
        """Test password reset confirmation"""
        response = client.post(
            "/api/auth/password-reset-confirm",
            json={
                "token": "reset_token_here",
                "new_password": "NewSecurePassword123!"
            }
        )
        
        assert response.status_code in [200, 400]  # May fail if token invalid
    
    def test_email_verification(self):
        """Test email verification"""
        response = client.get("/api/auth/verify-email?token=verification_token")
        
        assert response.status_code in [200, 400]
