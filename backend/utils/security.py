"""
Security Utilities
Encryption, hashing, and token generation
"""

import hashlib
import secrets
import jwt
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend

from core.config import settings


def encrypt_data(data: str, key: Optional[str] = None) -> str:
    """
    Encrypt data using Fernet (symmetric encryption)
    
    Args:
        data: Data to encrypt
        key: Encryption key (optional, uses settings key if not provided)
        
    Returns:
        Encrypted data (base64 encoded)
    """
    if key is None:
        key = settings.ENCRYPTION_KEY
    
    f = Fernet(key.encode() if isinstance(key, str) else key)
    encrypted = f.encrypt(data.encode())
    return encrypted.decode()


def decrypt_data(encrypted_data: str, key: Optional[str] = None) -> str:
    """
    Decrypt data using Fernet
    
    Args:
        encrypted_data: Encrypted data (base64 encoded)
        key: Encryption key (optional, uses settings key if not provided)
        
    Returns:
        Decrypted data
    """
    if key is None:
        key = settings.ENCRYPTION_KEY
    
    f = Fernet(key.encode() if isinstance(key, str) else key)
    decrypted = f.decrypt(encrypted_data.encode())
    return decrypted.decode()


def generate_api_key(prefix: str = "ik", environment: str = "live") -> str:
    """
    Generate API key
    
    Args:
        prefix: API key prefix (default: "ik" for IKODIO)
        environment: Environment (live or test)
        
    Returns:
        API key in format: ik_live_xxxxxxxxxxxxx
    """
    random_part = secrets.token_hex(16)  # 32 characters
    return f"{prefix}_{environment}_{random_part}"


def hash_sha256(data: str) -> str:
    """
    Hash data using SHA256
    
    Args:
        data: Data to hash
        
    Returns:
        SHA256 hex digest
    """
    return hashlib.sha256(data.encode()).hexdigest()


def hash_sha512(data: str) -> str:
    """
    Hash data using SHA512
    
    Args:
        data: Data to hash
        
    Returns:
        SHA512 hex digest
    """
    return hashlib.sha512(data.encode()).hexdigest()


def generate_jwt_token(
    payload: Dict[str, Any],
    expires_in: Optional[int] = None,
    secret: Optional[str] = None
) -> str:
    """
    Generate JWT token
    
    Args:
        payload: Token payload
        expires_in: Expiration time in seconds (optional)
        secret: JWT secret key (optional, uses settings if not provided)
        
    Returns:
        JWT token string
    """
    if secret is None:
        secret = settings.JWT_SECRET
    
    # Add expiration if specified
    if expires_in:
        payload["exp"] = datetime.utcnow() + timedelta(seconds=expires_in)
    
    # Add issued at timestamp
    payload["iat"] = datetime.utcnow()
    
    return jwt.encode(payload, secret, algorithm=settings.JWT_ALGORITHM)


def verify_jwt_token(
    token: str,
    secret: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Verify and decode JWT token
    
    Args:
        token: JWT token string
        secret: JWT secret key (optional, uses settings if not provided)
        
    Returns:
        Decoded payload or None if invalid
    """
    if secret is None:
        secret = settings.JWT_SECRET
    
    try:
        payload = jwt.decode(
            token,
            secret,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def generate_secure_token(length: int = 32) -> str:
    """
    Generate cryptographically secure random token
    
    Args:
        length: Length of token in bytes
        
    Returns:
        Random token (hex encoded)
    """
    return secrets.token_hex(length)


def generate_otp(length: int = 6) -> str:
    """
    Generate One-Time Password (OTP)
    
    Args:
        length: Length of OTP (default: 6 digits)
        
    Returns:
        OTP string
    """
    return ''.join(secrets.choice('0123456789') for _ in range(length))


def hash_with_salt(data: str, salt: Optional[str] = None) -> tuple:
    """
    Hash data with salt using PBKDF2
    
    Args:
        data: Data to hash
        salt: Salt (optional, generates new salt if not provided)
        
    Returns:
        Tuple of (hash, salt)
    """
    if salt is None:
        salt = secrets.token_hex(16)
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt.encode(),
        iterations=100000,
        backend=default_backend()
    )
    
    key = kdf.derive(data.encode())
    return key.hex(), salt


def verify_hash_with_salt(data: str, hash_value: str, salt: str) -> bool:
    """
    Verify data against hash with salt
    
    Args:
        data: Data to verify
        hash_value: Expected hash value
        salt: Salt used for hashing
        
    Returns:
        True if match, False otherwise
    """
    computed_hash, _ = hash_with_salt(data, salt)
    return computed_hash == hash_value


def generate_csrf_token() -> str:
    """
    Generate CSRF token
    
    Returns:
        CSRF token
    """
    return secrets.token_urlsafe(32)


def constant_time_compare(a: str, b: str) -> bool:
    """
    Compare two strings in constant time (prevents timing attacks)
    
    Args:
        a: First string
        b: Second string
        
    Returns:
        True if equal, False otherwise
    """
    return secrets.compare_digest(a.encode(), b.encode())
