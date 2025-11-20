"""
Validators
Input validation utilities
"""

import re
from typing import Optional
from urllib.parse import urlparse


def validate_email(email: str) -> bool:
    """
    Validate email address format
    
    Args:
        email: Email address to validate
        
    Returns:
        True if valid, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_url(url: str) -> bool:
    """
    Validate URL format
    
    Args:
        url: URL to validate
        
    Returns:
        True if valid, False otherwise
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def validate_ip_address(ip: str) -> bool:
    """
    Validate IPv4 address
    
    Args:
        ip: IP address to validate
        
    Returns:
        True if valid IPv4, False otherwise
    """
    pattern = r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
    return bool(re.match(pattern, ip))


def validate_domain(domain: str) -> bool:
    """
    Validate domain name
    
    Args:
        domain: Domain to validate
        
    Returns:
        True if valid, False otherwise
    """
    pattern = r'^([a-z0-9]+(-[a-z0-9]+)*\.)+[a-z]{2,}$'
    return bool(re.match(pattern, domain.lower()))


def validate_cve_id(cve_id: str) -> bool:
    """
    Validate CVE ID format
    
    Args:
        cve_id: CVE ID to validate (e.g., CVE-2024-1234)
        
    Returns:
        True if valid CVE format, False otherwise
    """
    pattern = r'^CVE-\d{4}-\d{4,}$'
    return bool(re.match(pattern, cve_id.upper()))


def validate_severity(severity: str) -> bool:
    """
    Validate bug severity level
    
    Args:
        severity: Severity level
        
    Returns:
        True if valid severity, False otherwise
    """
    valid_severities = ["low", "medium", "high", "critical", "info"]
    return severity.lower() in valid_severities


def validate_password_strength(password: str) -> dict:
    """
    Validate password strength
    
    Args:
        password: Password to validate
        
    Returns:
        Dictionary with validation results
    """
    result = {
        "valid": True,
        "score": 0,
        "feedback": []
    }
    
    # Length check
    if len(password) < 8:
        result["valid"] = False
        result["feedback"].append("Password must be at least 8 characters")
    else:
        result["score"] += 1
    
    # Uppercase check
    if not any(c.isupper() for c in password):
        result["valid"] = False
        result["feedback"].append("Password must contain uppercase letter")
    else:
        result["score"] += 1
    
    # Lowercase check
    if not any(c.islower() for c in password):
        result["valid"] = False
        result["feedback"].append("Password must contain lowercase letter")
    else:
        result["score"] += 1
    
    # Digit check
    if not any(c.isdigit() for c in password):
        result["valid"] = False
        result["feedback"].append("Password must contain digit")
    else:
        result["score"] += 1
    
    # Special character check
    if not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password):
        result["feedback"].append("Consider adding special characters for stronger password")
    else:
        result["score"] += 1
    
    # Length bonus
    if len(password) >= 12:
        result["score"] += 1
    if len(password) >= 16:
        result["score"] += 1
    
    return result


def validate_api_key_format(api_key: str) -> bool:
    """
    Validate API key format
    
    Args:
        api_key: API key to validate
        
    Returns:
        True if valid format, False otherwise
    """
    # Expected format: ik_live_xxxxxxxxxxxxx or ik_test_xxxxxxxxxxxxx
    pattern = r'^ik_(live|test)_[a-zA-Z0-9]{32}$'
    return bool(re.match(pattern, api_key))


def validate_port_number(port: int) -> bool:
    """
    Validate port number
    
    Args:
        port: Port number to validate
        
    Returns:
        True if valid port (1-65535), False otherwise
    """
    return 1 <= port <= 65535


def validate_hex_color(color: str) -> bool:
    """
    Validate hex color code
    
    Args:
        color: Hex color code (e.g., #FF5733)
        
    Returns:
        True if valid hex color, False otherwise
    """
    pattern = r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$'
    return bool(re.match(pattern, color))
