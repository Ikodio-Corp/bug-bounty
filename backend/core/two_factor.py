"""
Two-Factor Authentication (2FA) Service
Supports TOTP (Time-based One-Time Password)
"""

import pyotp
import qrcode
import io
import base64
from typing import Dict, Any, Optional
from datetime import datetime, timedelta


class TwoFactorAuth:
    """Two-Factor Authentication service"""
    
    def __init__(self, issuer_name: str = "IKODIO BugBounty"):
        self.issuer_name = issuer_name
    
    def generate_secret(self) -> str:
        """Generate a new TOTP secret"""
        return pyotp.random_base32()
    
    def get_provisioning_uri(
        self,
        secret: str,
        email: str,
        issuer_name: Optional[str] = None
    ) -> str:
        """Get provisioning URI for QR code"""
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(
            name=email,
            issuer_name=issuer_name or self.issuer_name
        )
    
    def generate_qr_code(
        self,
        secret: str,
        email: str,
        issuer_name: Optional[str] = None
    ) -> str:
        """Generate QR code as base64 string"""
        uri = self.get_provisioning_uri(secret, email, issuer_name)
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        return f"data:image/png;base64,{img_base64}"
    
    def verify_token(self, secret: str, token: str, window: int = 1) -> bool:
        """
        Verify TOTP token
        
        Args:
            secret: User's TOTP secret
            token: Token to verify
            window: Number of time windows to check (default 1 = 30 seconds)
        
        Returns:
            True if token is valid
        """
        totp = pyotp.TOTP(secret)
        return totp.verify(token, valid_window=window)
    
    def get_current_token(self, secret: str) -> str:
        """Get current TOTP token (for testing)"""
        totp = pyotp.TOTP(secret)
        return totp.now()
    
    def generate_backup_codes(self, count: int = 10) -> list:
        """Generate backup codes for account recovery"""
        import secrets
        return [secrets.token_hex(4).upper() for _ in range(count)]
    
    def setup_2fa(self, email: str) -> Dict[str, Any]:
        """
        Setup 2FA for a user
        
        Returns:
            Dictionary with secret, QR code, and backup codes
        """
        secret = self.generate_secret()
        qr_code = self.generate_qr_code(secret, email)
        backup_codes = self.generate_backup_codes()
        
        return {
            "secret": secret,
            "qr_code": qr_code,
            "backup_codes": backup_codes,
            "provisioning_uri": self.get_provisioning_uri(secret, email)
        }
    
    def enable_2fa(
        self,
        secret: str,
        verification_token: str
    ) -> bool:
        """
        Enable 2FA after verifying initial token
        
        Returns:
            True if verification successful
        """
        return self.verify_token(secret, verification_token)


class WebAuthnService:
    """WebAuthn (FIDO2) service for hardware keys"""
    
    def __init__(self, rp_id: str, rp_name: str):
        """
        Initialize WebAuthn service
        
        Args:
            rp_id: Relying Party ID (domain)
            rp_name: Relying Party name
        """
        self.rp_id = rp_id
        self.rp_name = rp_name
    
    def generate_registration_options(
        self,
        user_id: str,
        user_name: str,
        user_display_name: str
    ) -> Dict[str, Any]:
        """Generate options for WebAuthn registration"""
        import secrets
        
        challenge = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')
        
        return {
            "challenge": challenge,
            "rp": {
                "id": self.rp_id,
                "name": self.rp_name
            },
            "user": {
                "id": base64.urlsafe_b64encode(user_id.encode()).decode('utf-8').rstrip('='),
                "name": user_name,
                "displayName": user_display_name
            },
            "pubKeyCredParams": [
                {"type": "public-key", "alg": -7},
                {"type": "public-key", "alg": -257}
            ],
            "timeout": 60000,
            "attestation": "direct",
            "authenticatorSelection": {
                "authenticatorAttachment": "cross-platform",
                "requireResidentKey": False,
                "userVerification": "preferred"
            }
        }
    
    def generate_authentication_options(
        self,
        credentials: list
    ) -> Dict[str, Any]:
        """Generate options for WebAuthn authentication"""
        import secrets
        
        challenge = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')
        
        return {
            "challenge": challenge,
            "timeout": 60000,
            "rpId": self.rp_id,
            "allowCredentials": [
                {
                    "type": "public-key",
                    "id": cred["credential_id"]
                }
                for cred in credentials
            ],
            "userVerification": "preferred"
        }


class BackupCodeManager:
    """Manage backup codes for 2FA recovery"""
    
    @staticmethod
    def hash_code(code: str) -> str:
        """Hash backup code for storage"""
        import hashlib
        return hashlib.sha256(code.encode()).hexdigest()
    
    @staticmethod
    def verify_code(code: str, hashed_code: str) -> bool:
        """Verify backup code against hash"""
        return BackupCodeManager.hash_code(code) == hashed_code
    
    @staticmethod
    def generate_codes(count: int = 10) -> Dict[str, Any]:
        """
        Generate backup codes
        
        Returns:
            Dictionary with plain codes and hashed codes
        """
        import secrets
        
        codes = [secrets.token_hex(4).upper() for _ in range(count)]
        hashed_codes = [BackupCodeManager.hash_code(code) for code in codes]
        
        return {
            "codes": codes,
            "hashed_codes": hashed_codes
        }
