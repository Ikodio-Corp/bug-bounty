"""
Helper Utilities
Common helper functions for the application
"""

import uuid
import hashlib
import secrets
import string
import re
from typing import Optional, Dict, Any
from datetime import datetime
from passlib.context import CryptContext

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def generate_uuid() -> str:
    """Generate a unique UUID"""
    return str(uuid.uuid4())


def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)


def generate_random_string(length: int = 32, include_special: bool = False) -> str:
    """
    Generate random string
    
    Args:
        length: Length of string
        include_special: Include special characters
    """
    chars = string.ascii_letters + string.digits
    if include_special:
        chars += string.punctuation
    
    return ''.join(secrets.choice(chars) for _ in range(length))


def sanitize_input(text: str) -> str:
    """
    Sanitize user input to prevent XSS
    
    Args:
        text: Input text to sanitize
        
    Returns:
        Sanitized text
    """
    if not text:
        return ""
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Remove SQL injection patterns
    dangerous_patterns = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE)\b)",
        r"(--|#|\/\*|\*\/)",
        r"(\bOR\b.*=.*)",
        r"(\bAND\b.*=.*)",
    ]
    
    for pattern in dangerous_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    return text.strip()


def parse_user_agent(user_agent: str) -> Dict[str, Any]:
    """
    Parse User-Agent string
    
    Args:
        user_agent: User-Agent header value
        
    Returns:
        Dictionary with browser, OS, device info
    """
    result = {
        "browser": "Unknown",
        "browser_version": "",
        "os": "Unknown",
        "os_version": "",
        "device": "Desktop",
        "is_mobile": False,
        "is_bot": False,
    }
    
    if not user_agent:
        return result
    
    ua = user_agent.lower()
    
    # Detect bots
    bot_patterns = ['bot', 'crawler', 'spider', 'scraper']
    result["is_bot"] = any(pattern in ua for pattern in bot_patterns)
    
    # Detect mobile
    mobile_patterns = ['mobile', 'android', 'iphone', 'ipad', 'tablet']
    result["is_mobile"] = any(pattern in ua for pattern in mobile_patterns)
    
    if result["is_mobile"]:
        result["device"] = "Mobile"
    
    # Browser detection
    if 'chrome' in ua and 'edge' not in ua:
        result["browser"] = "Chrome"
    elif 'firefox' in ua:
        result["browser"] = "Firefox"
    elif 'safari' in ua and 'chrome' not in ua:
        result["browser"] = "Safari"
    elif 'edge' in ua:
        result["browser"] = "Edge"
    
    # OS detection
    if 'windows' in ua:
        result["os"] = "Windows"
    elif 'mac' in ua:
        result["os"] = "macOS"
    elif 'linux' in ua:
        result["os"] = "Linux"
    elif 'android' in ua:
        result["os"] = "Android"
    elif 'ios' in ua or 'iphone' in ua or 'ipad' in ua:
        result["os"] = "iOS"
    
    return result


def get_client_info(ip_address: str, user_agent: str) -> Dict[str, Any]:
    """
    Get comprehensive client information
    
    Args:
        ip_address: Client IP address
        user_agent: User-Agent string
        
    Returns:
        Dictionary with client info
    """
    ua_info = parse_user_agent(user_agent)
    
    return {
        "ip_address": ip_address,
        "user_agent": user_agent,
        **ua_info,
        "timestamp": datetime.utcnow().isoformat(),
    }


def calculate_hash(data: str, algorithm: str = "sha256") -> str:
    """
    Calculate hash of data
    
    Args:
        data: Data to hash
        algorithm: Hash algorithm (md5, sha1, sha256, sha512)
        
    Returns:
        Hex digest of hash
    """
    if algorithm == "md5":
        return hashlib.md5(data.encode()).hexdigest()
    elif algorithm == "sha1":
        return hashlib.sha1(data.encode()).hexdigest()
    elif algorithm == "sha256":
        return hashlib.sha256(data.encode()).hexdigest()
    elif algorithm == "sha512":
        return hashlib.sha512(data.encode()).hexdigest()
    else:
        raise ValueError(f"Unsupported algorithm: {algorithm}")


def chunk_list(lst: list, chunk_size: int) -> list:
    """
    Split list into chunks
    
    Args:
        lst: List to chunk
        chunk_size: Size of each chunk
        
    Returns:
        List of chunks
    """
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def merge_dicts(*dicts: Dict) -> Dict:
    """
    Merge multiple dictionaries
    
    Args:
        *dicts: Dictionaries to merge
        
    Returns:
        Merged dictionary
    """
    result = {}
    for d in dicts:
        result.update(d)
    return result
