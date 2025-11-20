import pytest
from unittest.mock import Mock, patch
from backend.services.auth_service import AuthService
from backend.models.user import User
from backend.core.security import get_password_hash


@pytest.fixture
def auth_service(db):
    return AuthService(db)


@pytest.fixture
def sample_user(db):
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("testpassword123"),
        is_active=True,
        is_verified=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


class TestAuthService:
    def test_register_user(self, auth_service):
        user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "SecurePass123!",
            "full_name": "New User"
        }
        
        user = auth_service.register_user(**user_data)
        
        assert user.id is not None
        assert user.username == user_data["username"]
        assert user.email == user_data["email"]
        assert user.hashed_password != user_data["password"]
        assert user.is_active is True
        assert user.is_verified is False
    
    def test_register_duplicate_email(self, auth_service, sample_user):
        with pytest.raises(ValueError, match="Email already registered"):
            auth_service.register_user(
                username="anotheruser",
                email=sample_user.email,
                password="password123"
            )
    
    def test_register_duplicate_username(self, auth_service, sample_user):
        with pytest.raises(ValueError, match="Username already taken"):
            auth_service.register_user(
                username=sample_user.username,
                email="different@example.com",
                password="password123"
            )
    
    def test_authenticate_user_success(self, auth_service, sample_user):
        user = auth_service.authenticate_user(
            username=sample_user.username,
            password="testpassword123"
        )
        
        assert user is not None
        assert user.id == sample_user.id
    
    def test_authenticate_user_wrong_password(self, auth_service, sample_user):
        user = auth_service.authenticate_user(
            username=sample_user.username,
            password="wrongpassword"
        )
        
        assert user is None
    
    def test_authenticate_user_not_found(self, auth_service):
        user = auth_service.authenticate_user(
            username="nonexistent",
            password="password123"
        )
        
        assert user is None
    
    def test_authenticate_inactive_user(self, auth_service, db):
        inactive_user = User(
            username="inactive",
            email="inactive@example.com",
            hashed_password=get_password_hash("password123"),
            is_active=False
        )
        db.add(inactive_user)
        db.commit()
        
        user = auth_service.authenticate_user(
            username="inactive",
            password="password123"
        )
        
        assert user is None
    
    def test_create_access_token(self, auth_service, sample_user):
        token = auth_service.create_access_token(user_id=sample_user.id)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_verify_token(self, auth_service, sample_user):
        token = auth_service.create_access_token(user_id=sample_user.id)
        
        payload = auth_service.verify_token(token)
        
        assert payload is not None
        assert payload["user_id"] == sample_user.id
    
    def test_verify_invalid_token(self, auth_service):
        payload = auth_service.verify_token("invalid.token.here")
        
        assert payload is None
    
    def test_verify_expired_token(self, auth_service, sample_user):
        with patch('backend.services.auth_service.datetime') as mock_datetime:
            # Create token
            token = auth_service.create_access_token(user_id=sample_user.id)
            
            # Fast forward time
            from datetime import datetime, timedelta
            mock_datetime.utcnow.return_value = datetime.utcnow() + timedelta(hours=25)
            
            payload = auth_service.verify_token(token)
            
            # Token should be expired (default expiry is 24 hours)
            # This test needs proper JWT expiry handling
    
    def test_refresh_token(self, auth_service, sample_user):
        old_token = auth_service.create_access_token(user_id=sample_user.id)
        
        new_token = auth_service.refresh_token(old_token)
        
        assert new_token is not None
        assert new_token != old_token
    
    def test_change_password(self, auth_service, sample_user):
        new_password = "NewSecurePass123!"
        
        result = auth_service.change_password(
            user_id=sample_user.id,
            old_password="testpassword123",
            new_password=new_password
        )
        
        assert result is True
        
        # Verify new password works
        user = auth_service.authenticate_user(
            username=sample_user.username,
            password=new_password
        )
        assert user is not None
    
    def test_change_password_wrong_old_password(self, auth_service, sample_user):
        with pytest.raises(ValueError, match="Incorrect old password"):
            auth_service.change_password(
                user_id=sample_user.id,
                old_password="wrongoldpassword",
                new_password="NewPassword123!"
            )
    
    def test_reset_password_request(self, auth_service, sample_user):
        reset_token = auth_service.request_password_reset(sample_user.email)
        
        assert reset_token is not None
        assert isinstance(reset_token, str)
    
    def test_reset_password_with_token(self, auth_service, sample_user):
        reset_token = auth_service.request_password_reset(sample_user.email)
        new_password = "ResetPassword123!"
        
        result = auth_service.reset_password_with_token(
            token=reset_token,
            new_password=new_password
        )
        
        assert result is True
        
        # Verify new password works
        user = auth_service.authenticate_user(
            username=sample_user.username,
            password=new_password
        )
        assert user is not None
    
    def test_verify_email(self, auth_service, db):
        unverified_user = User(
            username="unverified",
            email="unverified@example.com",
            hashed_password=get_password_hash("password123"),
            is_verified=False
        )
        db.add(unverified_user)
        db.commit()
        db.refresh(unverified_user)
        
        verification_token = auth_service.create_verification_token(unverified_user.id)
        
        result = auth_service.verify_email(verification_token)
        
        assert result is True
        db.refresh(unverified_user)
        assert unverified_user.is_verified is True
    
    def test_enable_2fa(self, auth_service, sample_user):
        secret = auth_service.enable_2fa(sample_user.id)
        
        assert secret is not None
        assert isinstance(secret, str)
    
    def test_verify_2fa_code(self, auth_service, sample_user):
        secret = auth_service.enable_2fa(sample_user.id)
        
        # Generate valid TOTP code
        import pyotp
        totp = pyotp.TOTP(secret)
        code = totp.now()
        
        result = auth_service.verify_2fa_code(sample_user.id, code)
        
        assert result is True
    
    def test_verify_2fa_invalid_code(self, auth_service, sample_user):
        auth_service.enable_2fa(sample_user.id)
        
        result = auth_service.verify_2fa_code(sample_user.id, "000000")
        
        assert result is False
    
    def test_disable_2fa(self, auth_service, sample_user):
        auth_service.enable_2fa(sample_user.id)
        
        result = auth_service.disable_2fa(sample_user.id)
        
        assert result is True
