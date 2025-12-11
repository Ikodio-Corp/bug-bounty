"""
Core security utilities - JWT, encryption, hashing
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
import bcrypt
from cryptography.fernet import Fernet
import secrets
import hashlib
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from .config import settings

# Use bcrypt directly instead of passlib to avoid 72-byte test issues
fernet = Fernet(settings.ENCRYPTION_KEY.encode() if len(settings.ENCRYPTION_KEY) == 44 else Fernet.generate_key())

# OAuth2 scheme for token extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login", auto_error=False)

# Dependency for getting current user
async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get current user from JWT token"""
    from models.user import User
    from .database import AsyncSessionLocal
    
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    payload = Security.decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Create db session
    async with AsyncSessionLocal() as db:
        user = await db.get(User, int(user_id))
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"}
            )
        return user


class Security:
    """Security utilities for authentication and encryption"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt (max 72 bytes)"""
        # Bcrypt has a 72-byte limit, truncate if necessary
        password_bytes = password.encode('utf-8')[:72]
        # Use bcrypt directly
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against a hash"""
        # Truncate to same length for verification
        password_bytes = plain_password.encode('utf-8')[:72]
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    
    @staticmethod
    def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(seconds=settings.JWT_EXPIRATION)
        
        to_encode.update({"exp": expire, "iat": datetime.utcnow()})
        encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
        """Decode and verify JWT token"""
        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
            return payload
        except JWTError:
            return None
    
    @staticmethod
    def encrypt(data: str) -> str:
        """Encrypt data using Fernet"""
        return fernet.encrypt(data.encode()).decode()
    
    @staticmethod
    def decrypt(encrypted_data: str) -> str:
        """Decrypt data using Fernet"""
        return fernet.decrypt(encrypted_data.encode()).decode()
    
    @staticmethod
    def generate_api_key() -> str:
        """Generate secure API key"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def generate_secret() -> str:
        """Generate secure secret"""
        return secrets.token_hex(32)
    
    @staticmethod
    def hash_sha256(data: str) -> str:
        """Hash data using SHA256"""
        return hashlib.sha256(data.encode()).hexdigest()
    
    @staticmethod
    def verify_signature(data: str, signature: str) -> bool:
        """Verify data signature"""
        return Security.hash_sha256(data) == signature
    
    @staticmethod
    async def get_current_user(token: str = Depends(oauth2_scheme)):
        """Get current user from JWT token"""
        from fastapi import HTTPException, status
        from models.user import User
        from .database import AsyncSessionLocal
        
        if token is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        payload = Security.decode_access_token(token)
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Create db session using context manager
        async with AsyncSessionLocal() as db:
            user = await db.get(User, int(user_id))
            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found",
                    headers={"WWW-Authenticate": "Bearer"}
                )
            return user


class RateLimiter:
    """Rate limiting utilities"""
    
    @staticmethod
    def get_key(identifier: str, endpoint: str) -> str:
        """Generate rate limit key"""
        return f"rate_limit:{identifier}:{endpoint}"
    
    @staticmethod
    async def check_rate_limit(redis, identifier: str, endpoint: str, limit: int, window: int) -> bool:
        """
        Check if rate limit exceeded
        Returns True if allowed, False if exceeded
        """
        key = RateLimiter.get_key(identifier, endpoint)
        count = await redis.incr(key)
        
        if count == 1:
            await redis.expire(key, window)
        
        return count <= limit
    
    @staticmethod
    async def get_remaining(redis, identifier: str, endpoint: str, limit: int) -> int:
        """Get remaining requests"""
        key = RateLimiter.get_key(identifier, endpoint)
        count = await redis.get(key)
        
        if count is None:
            return limit
        
        return max(0, limit - int(count))
