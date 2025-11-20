"""
2FA/MFA System - Multi-Factor Authentication Implementation

This module provides comprehensive MFA support including:
- TOTP (Time-based One-Time Password)
- SMS/Email verification codes
- Hardware security keys (WebAuthn)
- Backup codes
"""

import base64
import hashlib
import hmac
import logging
import secrets
import struct
import time
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum
from datetime import datetime, timedelta

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class MFAMethod(str, Enum):
    """Supported MFA methods."""
    TOTP = "totp"
    SMS = "sms"
    EMAIL = "email"
    WEBAUTHN = "webauthn"
    BACKUP_CODES = "backup_codes"


class TOTPConfig(BaseModel):
    """TOTP configuration."""
    secret: str
    algorithm: str = "SHA1"
    digits: int = 6
    period: int = 30
    issuer: str = "IKODIO"
    account_name: str = ""


class WebAuthnCredential(BaseModel):
    """WebAuthn credential."""
    credential_id: str
    public_key: str
    sign_count: int = 0
    device_name: str = ""
    created_at: datetime


class MFASetup(BaseModel):
    """MFA setup result."""
    method: MFAMethod
    secret: Optional[str] = None
    qr_code_url: Optional[str] = None
    backup_codes: Optional[List[str]] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None


class MFAVerification(BaseModel):
    """MFA verification result."""
    success: bool
    method: MFAMethod
    backup_code_used: bool = False
    remaining_backup_codes: Optional[int] = None


class TOTPService:
    """
    TOTP (Time-based One-Time Password) Service.

    Implements RFC 6238 TOTP algorithm.
    """

    def __init__(self, digits: int = 6, period: int = 30):
        """Initialize TOTP service."""
        self.digits = digits
        self.period = period

    def generate_secret(self, length: int = 32) -> str:
        """
        Generate a new TOTP secret.

        Args:
            length: Secret length in bytes

        Returns:
            Base32-encoded secret
        """
        random_bytes = secrets.token_bytes(length)
        return base64.b32encode(random_bytes).decode().rstrip("=")

    def generate_totp(self, secret: str, timestamp: Optional[int] = None) -> str:
        """
        Generate TOTP code.

        Args:
            secret: Base32-encoded secret
            timestamp: Unix timestamp (defaults to now)

        Returns:
            TOTP code
        """
        if timestamp is None:
            timestamp = int(time.time())

        # Decode secret
        secret_bytes = base64.b32decode(secret + "=" * (8 - len(secret) % 8))

        # Calculate counter
        counter = timestamp // self.period

        # Generate HMAC
        counter_bytes = struct.pack(">Q", counter)
        hmac_hash = hmac.new(secret_bytes, counter_bytes, hashlib.sha1).digest()

        # Dynamic truncation
        offset = hmac_hash[-1] & 0x0F
        code = struct.unpack(">I", hmac_hash[offset:offset + 4])[0]
        code = (code & 0x7FFFFFFF) % (10 ** self.digits)

        return str(code).zfill(self.digits)

    def verify_totp(
        self,
        secret: str,
        code: str,
        window: int = 1
    ) -> bool:
        """
        Verify TOTP code.

        Args:
            secret: Base32-encoded secret
            code: TOTP code to verify
            window: Number of periods to check before/after

        Returns:
            True if code is valid
        """
        timestamp = int(time.time())

        # Check current and adjacent periods
        for i in range(-window, window + 1):
            check_time = timestamp + (i * self.period)
            expected = self.generate_totp(secret, check_time)
            if hmac.compare_digest(code, expected):
                return True

        return False

    def get_provisioning_uri(
        self,
        secret: str,
        account_name: str,
        issuer: str = "IKODIO"
    ) -> str:
        """
        Generate provisioning URI for QR code.

        Args:
            secret: Base32-encoded secret
            account_name: User's account name (usually email)
            issuer: Issuer name

        Returns:
            otpauth:// URI
        """
        from urllib.parse import quote

        return (
            f"otpauth://totp/{quote(issuer)}:{quote(account_name)}"
            f"?secret={secret}"
            f"&issuer={quote(issuer)}"
            f"&algorithm=SHA1"
            f"&digits={self.digits}"
            f"&period={self.period}"
        )


class BackupCodesService:
    """Service for generating and managing backup codes."""

    def __init__(self, code_length: int = 8, num_codes: int = 10):
        """Initialize backup codes service."""
        self.code_length = code_length
        self.num_codes = num_codes

    def generate_codes(self) -> List[str]:
        """
        Generate new backup codes.

        Returns:
            List of backup codes
        """
        codes = []
        for _ in range(self.num_codes):
            code = secrets.token_hex(self.code_length // 2).upper()
            # Format: XXXX-XXXX
            formatted = f"{code[:4]}-{code[4:]}"
            codes.append(formatted)
        return codes

    def hash_code(self, code: str) -> str:
        """
        Hash a backup code for storage.

        Args:
            code: Backup code

        Returns:
            Hashed code
        """
        normalized = code.replace("-", "").upper()
        return hashlib.sha256(normalized.encode()).hexdigest()

    def verify_code(self, code: str, hashed_codes: List[str]) -> Tuple[bool, Optional[int]]:
        """
        Verify a backup code.

        Args:
            code: Backup code to verify
            hashed_codes: List of hashed valid codes

        Returns:
            Tuple of (is_valid, index of used code)
        """
        code_hash = self.hash_code(code)

        for i, hashed in enumerate(hashed_codes):
            if hmac.compare_digest(code_hash, hashed):
                return True, i

        return False, None


class SMSService:
    """SMS verification code service."""

    def __init__(self, code_length: int = 6, expiry_minutes: int = 5):
        """Initialize SMS service."""
        self.code_length = code_length
        self.expiry_minutes = expiry_minutes
        self._pending_codes: Dict[str, Dict[str, Any]] = {}

    def generate_code(self, phone_number: str, user_id: str) -> str:
        """
        Generate SMS verification code.

        Args:
            phone_number: Phone number to send to
            user_id: User ID

        Returns:
            Generated code
        """
        code = "".join(secrets.choice("0123456789") for _ in range(self.code_length))

        self._pending_codes[user_id] = {
            "code": code,
            "phone_number": phone_number,
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(minutes=self.expiry_minutes),
            "attempts": 0
        }

        return code

    def verify_code(self, user_id: str, code: str) -> bool:
        """
        Verify SMS code.

        Args:
            user_id: User ID
            code: Code to verify

        Returns:
            True if code is valid
        """
        if user_id not in self._pending_codes:
            return False

        pending = self._pending_codes[user_id]

        # Check expiry
        if pending["expires_at"] < datetime.utcnow():
            del self._pending_codes[user_id]
            return False

        # Check attempts
        pending["attempts"] += 1
        if pending["attempts"] > 3:
            del self._pending_codes[user_id]
            return False

        # Verify code
        if hmac.compare_digest(code, pending["code"]):
            del self._pending_codes[user_id]
            return True

        return False


class EmailService:
    """Email verification code service."""

    def __init__(self, code_length: int = 6, expiry_minutes: int = 10):
        """Initialize email service."""
        self.code_length = code_length
        self.expiry_minutes = expiry_minutes
        self._pending_codes: Dict[str, Dict[str, Any]] = {}

    def generate_code(self, email: str, user_id: str) -> str:
        """
        Generate email verification code.

        Args:
            email: Email address
            user_id: User ID

        Returns:
            Generated code
        """
        code = "".join(secrets.choice("0123456789") for _ in range(self.code_length))

        self._pending_codes[user_id] = {
            "code": code,
            "email": email,
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(minutes=self.expiry_minutes),
            "attempts": 0
        }

        return code

    def verify_code(self, user_id: str, code: str) -> bool:
        """
        Verify email code.

        Args:
            user_id: User ID
            code: Code to verify

        Returns:
            True if code is valid
        """
        if user_id not in self._pending_codes:
            return False

        pending = self._pending_codes[user_id]

        # Check expiry
        if pending["expires_at"] < datetime.utcnow():
            del self._pending_codes[user_id]
            return False

        # Check attempts
        pending["attempts"] += 1
        if pending["attempts"] > 5:
            del self._pending_codes[user_id]
            return False

        # Verify code
        if hmac.compare_digest(code, pending["code"]):
            del self._pending_codes[user_id]
            return True

        return False


class MFAService:
    """
    Main MFA Service.

    Orchestrates all MFA methods and provides unified interface.
    """

    def __init__(self):
        """Initialize MFA service."""
        self.totp = TOTPService()
        self.backup_codes = BackupCodesService()
        self.sms = SMSService()
        self.email = EmailService()

        # User MFA configurations
        self._user_configs: Dict[str, Dict[str, Any]] = {}

    def setup_totp(self, user_id: str, account_name: str) -> MFASetup:
        """
        Set up TOTP for user.

        Args:
            user_id: User ID
            account_name: Account name (usually email)

        Returns:
            Setup result with secret and QR code URL
        """
        secret = self.totp.generate_secret()
        qr_url = self.totp.get_provisioning_uri(secret, account_name)

        # Store pending setup
        if user_id not in self._user_configs:
            self._user_configs[user_id] = {}

        self._user_configs[user_id]["pending_totp"] = secret

        return MFASetup(
            method=MFAMethod.TOTP,
            secret=secret,
            qr_code_url=qr_url
        )

    def confirm_totp(self, user_id: str, code: str) -> bool:
        """
        Confirm TOTP setup by verifying first code.

        Args:
            user_id: User ID
            code: TOTP code

        Returns:
            True if setup confirmed
        """
        if user_id not in self._user_configs:
            return False

        pending_secret = self._user_configs[user_id].get("pending_totp")
        if not pending_secret:
            return False

        if self.totp.verify_totp(pending_secret, code):
            # Confirm setup
            self._user_configs[user_id]["totp_secret"] = pending_secret
            self._user_configs[user_id]["totp_enabled"] = True
            del self._user_configs[user_id]["pending_totp"]
            return True

        return False

    def setup_backup_codes(self, user_id: str) -> MFASetup:
        """
        Generate backup codes for user.

        Args:
            user_id: User ID

        Returns:
            Setup result with backup codes
        """
        codes = self.backup_codes.generate_codes()
        hashed_codes = [self.backup_codes.hash_code(code) for code in codes]

        if user_id not in self._user_configs:
            self._user_configs[user_id] = {}

        self._user_configs[user_id]["backup_codes"] = hashed_codes

        return MFASetup(
            method=MFAMethod.BACKUP_CODES,
            backup_codes=codes
        )

    def setup_sms(self, user_id: str, phone_number: str) -> MFASetup:
        """
        Set up SMS MFA for user.

        Args:
            user_id: User ID
            phone_number: Phone number

        Returns:
            Setup result
        """
        code = self.sms.generate_code(phone_number, user_id)

        # In production, send SMS here
        logger.info(f"SMS code for {user_id}: {code}")

        if user_id not in self._user_configs:
            self._user_configs[user_id] = {}

        self._user_configs[user_id]["pending_sms"] = phone_number

        return MFASetup(
            method=MFAMethod.SMS,
            phone_number=self._mask_phone(phone_number)
        )

    def confirm_sms(self, user_id: str, code: str) -> bool:
        """
        Confirm SMS setup.

        Args:
            user_id: User ID
            code: Verification code

        Returns:
            True if setup confirmed
        """
        if self.sms.verify_code(user_id, code):
            if user_id in self._user_configs:
                phone = self._user_configs[user_id].get("pending_sms")
                if phone:
                    self._user_configs[user_id]["sms_phone"] = phone
                    self._user_configs[user_id]["sms_enabled"] = True
                    del self._user_configs[user_id]["pending_sms"]
                    return True
        return False

    def setup_email(self, user_id: str, email: str) -> MFASetup:
        """
        Set up email MFA for user.

        Args:
            user_id: User ID
            email: Email address

        Returns:
            Setup result
        """
        code = self.email.generate_code(email, user_id)

        # In production, send email here
        logger.info(f"Email code for {user_id}: {code}")

        if user_id not in self._user_configs:
            self._user_configs[user_id] = {}

        self._user_configs[user_id]["pending_email"] = email

        return MFASetup(
            method=MFAMethod.EMAIL,
            email=self._mask_email(email)
        )

    def confirm_email(self, user_id: str, code: str) -> bool:
        """
        Confirm email setup.

        Args:
            user_id: User ID
            code: Verification code

        Returns:
            True if setup confirmed
        """
        if self.email.verify_code(user_id, code):
            if user_id in self._user_configs:
                email = self._user_configs[user_id].get("pending_email")
                if email:
                    self._user_configs[user_id]["email_address"] = email
                    self._user_configs[user_id]["email_enabled"] = True
                    del self._user_configs[user_id]["pending_email"]
                    return True
        return False

    def verify(
        self,
        user_id: str,
        method: MFAMethod,
        code: str
    ) -> MFAVerification:
        """
        Verify MFA code.

        Args:
            user_id: User ID
            method: MFA method
            code: Verification code

        Returns:
            Verification result
        """
        if user_id not in self._user_configs:
            return MFAVerification(
                success=False,
                method=method
            )

        config = self._user_configs[user_id]

        if method == MFAMethod.TOTP:
            secret = config.get("totp_secret")
            if secret and self.totp.verify_totp(secret, code):
                return MFAVerification(success=True, method=method)

        elif method == MFAMethod.SMS:
            if self.sms.verify_code(user_id, code):
                return MFAVerification(success=True, method=method)

        elif method == MFAMethod.EMAIL:
            if self.email.verify_code(user_id, code):
                return MFAVerification(success=True, method=method)

        elif method == MFAMethod.BACKUP_CODES:
            hashed_codes = config.get("backup_codes", [])
            valid, index = self.backup_codes.verify_code(code, hashed_codes)

            if valid and index is not None:
                # Remove used code
                config["backup_codes"].pop(index)
                return MFAVerification(
                    success=True,
                    method=method,
                    backup_code_used=True,
                    remaining_backup_codes=len(config["backup_codes"])
                )

        return MFAVerification(success=False, method=method)

    def send_challenge(self, user_id: str, method: MFAMethod) -> bool:
        """
        Send MFA challenge (for SMS/Email).

        Args:
            user_id: User ID
            method: MFA method

        Returns:
            True if challenge sent
        """
        if user_id not in self._user_configs:
            return False

        config = self._user_configs[user_id]

        if method == MFAMethod.SMS:
            phone = config.get("sms_phone")
            if phone:
                code = self.sms.generate_code(phone, user_id)
                # Send SMS
                logger.info(f"SMS challenge for {user_id}: {code}")
                return True

        elif method == MFAMethod.EMAIL:
            email = config.get("email_address")
            if email:
                code = self.email.generate_code(email, user_id)
                # Send email
                logger.info(f"Email challenge for {user_id}: {code}")
                return True

        return False

    def get_enabled_methods(self, user_id: str) -> List[MFAMethod]:
        """
        Get enabled MFA methods for user.

        Args:
            user_id: User ID

        Returns:
            List of enabled methods
        """
        if user_id not in self._user_configs:
            return []

        config = self._user_configs[user_id]
        methods = []

        if config.get("totp_enabled"):
            methods.append(MFAMethod.TOTP)
        if config.get("sms_enabled"):
            methods.append(MFAMethod.SMS)
        if config.get("email_enabled"):
            methods.append(MFAMethod.EMAIL)
        if config.get("backup_codes"):
            methods.append(MFAMethod.BACKUP_CODES)

        return methods

    def disable_method(self, user_id: str, method: MFAMethod) -> bool:
        """
        Disable MFA method for user.

        Args:
            user_id: User ID
            method: MFA method to disable

        Returns:
            True if disabled
        """
        if user_id not in self._user_configs:
            return False

        config = self._user_configs[user_id]

        if method == MFAMethod.TOTP:
            config.pop("totp_secret", None)
            config["totp_enabled"] = False
        elif method == MFAMethod.SMS:
            config.pop("sms_phone", None)
            config["sms_enabled"] = False
        elif method == MFAMethod.EMAIL:
            config.pop("email_address", None)
            config["email_enabled"] = False
        elif method == MFAMethod.BACKUP_CODES:
            config.pop("backup_codes", None)

        return True

    def _mask_phone(self, phone: str) -> str:
        """Mask phone number for display."""
        if len(phone) > 4:
            return "*" * (len(phone) - 4) + phone[-4:]
        return phone

    def _mask_email(self, email: str) -> str:
        """Mask email for display."""
        if "@" in email:
            local, domain = email.split("@")
            if len(local) > 2:
                return local[0] + "*" * (len(local) - 2) + local[-1] + "@" + domain
        return email


# Singleton instance
_mfa_service: Optional[MFAService] = None


def get_mfa_service() -> MFAService:
    """Get the global MFA service instance."""
    global _mfa_service
    if _mfa_service is None:
        _mfa_service = MFAService()
    return _mfa_service


__all__ = [
    "MFAService",
    "MFAMethod",
    "MFASetup",
    "MFAVerification",
    "TOTPService",
    "BackupCodesService",
    "get_mfa_service"
]
