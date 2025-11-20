"""
Two-Factor Authentication (2FA) Routes
Supports: TOTP, Backup Codes, WebAuthn/FIDO2
"""
from fastapi import APIRouter, HTTPException, Depends, Body
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import List, Optional

from core.database import get_db
from core.two_factor import TwoFactorAuth, WebAuthnService, BackupCodeManager
from core.security import get_current_user
from models.user import User

router = APIRouter(prefix="/2fa", tags=["Two-Factor Authentication"])

two_factor = TwoFactorAuth()
webauthn = WebAuthnService()
backup_codes = BackupCodeManager()


class Enable2FARequest(BaseModel):
    """Request model for enabling 2FA"""
    pass


class Verify2FARequest(BaseModel):
    """Request model for verifying 2FA"""
    code: str


class WebAuthnRegisterRequest(BaseModel):
    """Request model for WebAuthn registration"""
    credential: dict


class WebAuthnAuthRequest(BaseModel):
    """Request model for WebAuthn authentication"""
    credential: dict


@router.post("/enable")
async def enable_two_factor(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Enable 2FA for user account
    
    Returns QR code and secret for authenticator app setup
    
    Args:
        current_user: Authenticated user
        db: Database session
        
    Returns:
        dict: QR code image (base64) and secret
    """
    if current_user.two_factor_enabled:
        raise HTTPException(
            status_code=400,
            detail="2FA is already enabled for this account"
        )
    
    # Generate secret and QR code
    secret = two_factor.generate_secret()
    qr_code = two_factor.generate_qr_code(
        secret=secret,
        user_email=current_user.email,
        issuer="IKODIO BugBounty"
    )
    
    # Store secret temporarily (not activated until verification)
    current_user.two_factor_secret = secret
    current_user.two_factor_enabled = False
    await db.commit()
    
    return {
        "secret": secret,
        "qr_code": qr_code,
        "message": "Scan QR code with authenticator app and verify with code"
    }


@router.post("/verify")
async def verify_two_factor(
    request: Verify2FARequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Verify 2FA code and complete setup
    
    Args:
        request: Verification request with TOTP code
        current_user: Authenticated user
        db: Database session
        
    Returns:
        dict: Backup codes for account recovery
    """
    if not current_user.two_factor_secret:
        raise HTTPException(
            status_code=400,
            detail="2FA setup not initiated. Call /2fa/enable first"
        )
    
    # Verify TOTP code
    is_valid = two_factor.verify_code(
        secret=current_user.two_factor_secret,
        code=request.code
    )
    
    if not is_valid:
        raise HTTPException(
            status_code=400,
            detail="Invalid verification code"
        )
    
    # Generate backup codes
    codes = backup_codes.generate_codes(count=10)
    hashed_codes = [backup_codes.hash_code(code) for code in codes]
    
    # Activate 2FA
    current_user.two_factor_enabled = True
    current_user.backup_codes = hashed_codes
    await db.commit()
    
    return {
        "message": "2FA successfully enabled",
        "backup_codes": codes,
        "warning": "Store backup codes securely. They will not be shown again."
    }


@router.post("/disable")
async def disable_two_factor(
    request: Verify2FARequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Disable 2FA for user account
    
    Args:
        request: Verification request with TOTP code
        current_user: Authenticated user
        db: Database session
        
    Returns:
        dict: Success message
    """
    if not current_user.two_factor_enabled:
        raise HTTPException(
            status_code=400,
            detail="2FA is not enabled for this account"
        )
    
    # Verify TOTP code
    is_valid = two_factor.verify_code(
        secret=current_user.two_factor_secret,
        code=request.code
    )
    
    if not is_valid:
        raise HTTPException(
            status_code=400,
            detail="Invalid verification code"
        )
    
    # Disable 2FA
    current_user.two_factor_enabled = False
    current_user.two_factor_secret = None
    current_user.backup_codes = []
    await db.commit()
    
    return {"message": "2FA successfully disabled"}


@router.post("/verify-login")
async def verify_login_code(
    request: Verify2FARequest,
    user_id: int = Body(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Verify 2FA code during login
    
    Args:
        request: Verification request with TOTP code
        user_id: User ID
        db: Database session
        
    Returns:
        dict: Verification result
    """
    from sqlalchemy import select
    
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user or not user.two_factor_enabled:
        raise HTTPException(status_code=400, detail="Invalid request")
    
    # Check if it's a backup code
    is_backup = backup_codes.verify_code(
        code=request.code,
        hashed_codes=user.backup_codes
    )
    
    if is_backup:
        # Remove used backup code
        hashed_code = backup_codes.hash_code(request.code)
        user.backup_codes = [
            code for code in user.backup_codes if code != hashed_code
        ]
        await db.commit()
        
        return {
            "verified": True,
            "message": "Backup code accepted",
            "backup_codes_remaining": len(user.backup_codes)
        }
    
    # Verify TOTP code
    is_valid = two_factor.verify_code(
        secret=user.two_factor_secret,
        code=request.code
    )
    
    if not is_valid:
        raise HTTPException(
            status_code=400,
            detail="Invalid verification code"
        )
    
    return {"verified": True, "message": "Code verified"}


@router.get("/backup-codes")
async def get_backup_codes_status(
    current_user: User = Depends(get_current_user)
):
    """
    Get backup codes status
    
    Args:
        current_user: Authenticated user
        
    Returns:
        dict: Number of remaining backup codes
    """
    if not current_user.two_factor_enabled:
        raise HTTPException(
            status_code=400,
            detail="2FA is not enabled"
        )
    
    return {
        "backup_codes_remaining": len(current_user.backup_codes or [])
    }


@router.post("/regenerate-backup-codes")
async def regenerate_backup_codes(
    request: Verify2FARequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Regenerate backup codes
    
    Args:
        request: Verification request with TOTP code
        current_user: Authenticated user
        db: Database session
        
    Returns:
        dict: New backup codes
    """
    if not current_user.two_factor_enabled:
        raise HTTPException(
            status_code=400,
            detail="2FA is not enabled"
        )
    
    # Verify TOTP code
    is_valid = two_factor.verify_code(
        secret=current_user.two_factor_secret,
        code=request.code
    )
    
    if not is_valid:
        raise HTTPException(
            status_code=400,
            detail="Invalid verification code"
        )
    
    # Generate new backup codes
    codes = backup_codes.generate_codes(count=10)
    hashed_codes = [backup_codes.hash_code(code) for code in codes]
    
    current_user.backup_codes = hashed_codes
    await db.commit()
    
    return {
        "message": "Backup codes regenerated",
        "backup_codes": codes,
        "warning": "Store backup codes securely. Old codes are now invalid."
    }


@router.post("/webauthn/register-begin")
async def webauthn_register_begin(
    current_user: User = Depends(get_current_user)
):
    """
    Begin WebAuthn/FIDO2 registration
    
    Args:
        current_user: Authenticated user
        
    Returns:
        dict: Registration options for client
    """
    options = await webauthn.begin_registration(
        user_id=str(current_user.id),
        username=current_user.username,
        display_name=current_user.full_name or current_user.username
    )
    
    return options


@router.post("/webauthn/register-complete")
async def webauthn_register_complete(
    request: WebAuthnRegisterRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Complete WebAuthn/FIDO2 registration
    
    Args:
        request: Registration credential from client
        current_user: Authenticated user
        db: Database session
        
    Returns:
        dict: Success message
    """
    try:
        credential = await webauthn.complete_registration(
            user_id=str(current_user.id),
            credential=request.credential
        )
        
        # Store credential (you should add webauthn_credentials field to User model)
        # For now, store in a JSON field
        if not hasattr(current_user, 'webauthn_credentials'):
            current_user.webauthn_credentials = []
        
        current_user.webauthn_credentials.append(credential)
        await db.commit()
        
        return {
            "message": "Security key registered successfully",
            "credential_id": credential["id"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/webauthn/auth-begin")
async def webauthn_auth_begin():
    """
    Begin WebAuthn/FIDO2 authentication
    
    Returns:
        dict: Authentication options for client
    """
    options = await webauthn.begin_authentication()
    return options


@router.post("/webauthn/auth-complete")
async def webauthn_auth_complete(
    request: WebAuthnAuthRequest,
    user_id: int = Body(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Complete WebAuthn/FIDO2 authentication
    
    Args:
        request: Authentication credential from client
        user_id: User ID
        db: Database session
        
    Returns:
        dict: Verification result
    """
    from sqlalchemy import select
    
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=400, detail="Invalid request")
    
    try:
        is_valid = await webauthn.complete_authentication(
            user_id=str(user.id),
            credential=request.credential,
            stored_credentials=user.webauthn_credentials or []
        )
        
        if not is_valid:
            raise HTTPException(
                status_code=400,
                detail="Invalid security key"
            )
        
        return {"verified": True, "message": "Security key verified"}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/status")
async def get_2fa_status(
    current_user: User = Depends(get_current_user)
):
    """
    Get 2FA status for current user
    
    Args:
        current_user: Authenticated user
        
    Returns:
        dict: 2FA configuration status
    """
    return {
        "two_factor_enabled": current_user.two_factor_enabled,
        "backup_codes_remaining": len(current_user.backup_codes or []),
        "webauthn_credentials": len(
            getattr(current_user, 'webauthn_credentials', [])
        )
    }
