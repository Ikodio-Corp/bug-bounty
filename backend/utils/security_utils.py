from typing import Optional
from pydantic import BaseModel, validator
import re

class PasswordPolicy(BaseModel):
    min_length: int = 12
    require_uppercase: bool = True
    require_lowercase: bool = True
    require_digit: bool = True
    require_special: bool = True
    max_age_days: int = 90
    prevent_reuse: int = 5
    
    @staticmethod
    def validate_password(password: str, policy: Optional['PasswordPolicy'] = None) -> tuple[bool, Optional[str]]:
        if policy is None:
            policy = PasswordPolicy()
        
        if len(password) < policy.min_length:
            return False, f"Password must be at least {policy.min_length} characters long"
        
        if policy.require_uppercase and not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        
        if policy.require_lowercase and not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        
        if policy.require_digit and not re.search(r'\d', password):
            return False, "Password must contain at least one digit"
        
        if policy.require_special and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "Password must contain at least one special character"
        
        common_passwords = [
            "password", "123456", "password123", "admin", "letmein",
            "welcome", "monkey", "qwerty", "abc123", "password1"
        ]
        if password.lower() in common_passwords:
            return False, "Password is too common"
        
        return True, None
    
    @staticmethod
    def calculate_strength(password: str) -> dict:
        score = 0
        feedback = []
        
        if len(password) >= 8:
            score += 1
        if len(password) >= 12:
            score += 1
        if len(password) >= 16:
            score += 1
        
        if re.search(r'[a-z]', password):
            score += 1
        else:
            feedback.append("Add lowercase letters")
        
        if re.search(r'[A-Z]', password):
            score += 1
        else:
            feedback.append("Add uppercase letters")
        
        if re.search(r'\d', password):
            score += 1
        else:
            feedback.append("Add numbers")
        
        if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            score += 1
        else:
            feedback.append("Add special characters")
        
        if len(set(password)) >= len(password) * 0.7:
            score += 1
        
        if score <= 3:
            strength = "weak"
        elif score <= 5:
            strength = "fair"
        elif score <= 7:
            strength = "good"
        else:
            strength = "strong"
        
        return {
            "score": score,
            "max_score": 8,
            "strength": strength,
            "feedback": feedback
        }

class SecurityHeaders:
    @staticmethod
    def get_headers() -> dict:
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; "
                "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
                "font-src 'self' https://fonts.gstatic.com; "
                "img-src 'self' data: https:; "
                "connect-src 'self' https://api.ikodio.com wss://api.ikodio.com; "
                "frame-ancestors 'none'; "
                "base-uri 'self'; "
                "form-action 'self'"
            ),
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": (
                "accelerometer=(), "
                "camera=(), "
                "geolocation=(), "
                "gyroscope=(), "
                "magnetometer=(), "
                "microphone=(), "
                "payment=(), "
                "usb=()"
            )
        }

class InputValidator:
    @staticmethod
    def sanitize_html(text: str) -> str:
        import html
        return html.escape(text)
    
    @staticmethod
    def validate_email(email: str) -> bool:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_url(url: str) -> bool:
        pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        return bool(re.match(pattern, url))
    
    @staticmethod
    def validate_username(username: str) -> tuple[bool, Optional[str]]:
        if len(username) < 3:
            return False, "Username must be at least 3 characters"
        
        if len(username) > 32:
            return False, "Username must be at most 32 characters"
        
        if not re.match(r'^[a-zA-Z0-9_-]+$', username):
            return False, "Username can only contain letters, numbers, underscores, and hyphens"
        
        if username.startswith('-') or username.startswith('_'):
            return False, "Username cannot start with hyphen or underscore"
        
        return True, None
    
    @staticmethod
    def detect_sql_injection(text: str) -> bool:
        sql_patterns = [
            r"(\bOR\b|\bAND\b).*?=.*?",
            r"UNION.*?SELECT",
            r"DROP.*?TABLE",
            r"INSERT.*?INTO",
            r"DELETE.*?FROM",
            r"UPDATE.*?SET",
            r"--",
            r"/\*.*?\*/",
            r"xp_cmdshell",
            r"exec\s*\(",
        ]
        
        for pattern in sql_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False
    
    @staticmethod
    def detect_xss(text: str) -> bool:
        xss_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"on\w+\s*=",
            r"<iframe",
            r"<object",
            r"<embed",
            r"eval\s*\(",
        ]
        
        for pattern in xss_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False

class RateLimiter:
    def __init__(self, redis_client):
        self.redis = redis_client
    
    async def check_rate_limit(
        self,
        key: str,
        max_requests: int,
        window_seconds: int
    ) -> tuple[bool, int]:
        current = await self.redis.incr(key)
        
        if current == 1:
            await self.redis.expire(key, window_seconds)
        
        if current > max_requests:
            ttl = await self.redis.ttl(key)
            return False, ttl
        
        return True, window_seconds
    
    async def get_remaining(self, key: str, max_requests: int) -> int:
        current = await self.redis.get(key)
        if current is None:
            return max_requests
        return max(0, max_requests - int(current))

class EncryptionService:
    @staticmethod
    def encrypt_sensitive_data(data: str, key: bytes) -> str:
        from cryptography.fernet import Fernet
        f = Fernet(key)
        return f.encrypt(data.encode()).decode()
    
    @staticmethod
    def decrypt_sensitive_data(encrypted_data: str, key: bytes) -> str:
        from cryptography.fernet import Fernet
        f = Fernet(key)
        return f.decrypt(encrypted_data.encode()).decode()
    
    @staticmethod
    def generate_key() -> bytes:
        from cryptography.fernet import Fernet
        return Fernet.generate_key()
    
    @staticmethod
    def hash_data(data: str) -> str:
        import hashlib
        return hashlib.sha256(data.encode()).hexdigest()
