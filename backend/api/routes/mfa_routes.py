"""
MFA API Routes - Multi-Factor Authentication Endpoints

This module provides REST API endpoints for 2FA/MFA operations.
"""

import logging
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from ...auth.mfa import get_mfa_service, MFAService, MFAMethod

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth/mfa", tags=["MFA"])


# Request Models
class SetupTOTPRequest(BaseModel):
    """Request to setup TOTP."""
    user_id: str = Field(..., description="User ID")
    account_name: str = Field(..., description="Account name (email)")


class ConfirmTOTPRequest(BaseModel):
    """Request to confirm TOTP setup."""
    user_id: str = Field(..., description="User ID")
    code: str = Field(..., description="TOTP code")


class SetupSMSRequest(BaseModel):
    """Request to setup SMS MFA."""
    user_id: str = Field(..., description="User ID")
    phone_number: str = Field(..., description="Phone number")


class SetupEmailRequest(BaseModel):
    """Request to setup Email MFA."""
    user_id: str = Field(..., description="User ID")
    email: str = Field(..., description="Email address")


class VerifyRequest(BaseModel):
    """Request to verify MFA code."""
    user_id: str = Field(..., description="User ID")
    method: str = Field(..., description="MFA method")
    code: str = Field(..., description="Verification code")


class ChallengeRequest(BaseModel):
    """Request to send MFA challenge."""
    user_id: str = Field(..., description="User ID")
    method: str = Field(..., description="MFA method")


# Dependency
async def get_service() -> MFAService:
    """Get MFA service."""
    return get_mfa_service()


# Endpoints
@router.post("/totp/setup", response_model=Dict[str, Any])
async def setup_totp(
    request: SetupTOTPRequest,
    service: MFAService = Depends(get_service)
):
    """
    Set up TOTP for user.

    Returns secret and QR code URL for authenticator app.
    """
    try:
        result = service.setup_totp(request.user_id, request.account_name)

        return {
            "success": True,
            "method": result.method.value,
            "secret": result.secret,
            "qr_code_url": result.qr_code_url
        }

    except Exception as e:
        logger.error(f"TOTP setup failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/totp/confirm", response_model=Dict[str, Any])
async def confirm_totp(
    request: ConfirmTOTPRequest,
    service: MFAService = Depends(get_service)
):
    """
    Confirm TOTP setup by verifying first code.
    """
    try:
        success = service.confirm_totp(request.user_id, request.code)

        if success:
            return {"success": True, "message": "TOTP enabled successfully"}
        else:
            raise HTTPException(status_code=400, detail="Invalid code")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"TOTP confirm failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sms/setup", response_model=Dict[str, Any])
async def setup_sms(
    request: SetupSMSRequest,
    service: MFAService = Depends(get_service)
):
    """
    Set up SMS MFA for user.

    Sends verification code to phone number.
    """
    try:
        result = service.setup_sms(request.user_id, request.phone_number)

        return {
            "success": True,
            "method": result.method.value,
            "phone_number": result.phone_number,
            "message": "Verification code sent"
        }

    except Exception as e:
        logger.error(f"SMS setup failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sms/confirm", response_model=Dict[str, Any])
async def confirm_sms(
    request: ConfirmTOTPRequest,
    service: MFAService = Depends(get_service)
):
    """Confirm SMS setup by verifying code."""
    try:
        success = service.confirm_sms(request.user_id, request.code)

        if success:
            return {"success": True, "message": "SMS MFA enabled successfully"}
        else:
            raise HTTPException(status_code=400, detail="Invalid code")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"SMS confirm failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/email/setup", response_model=Dict[str, Any])
async def setup_email(
    request: SetupEmailRequest,
    service: MFAService = Depends(get_service)
):
    """
    Set up Email MFA for user.

    Sends verification code to email address.
    """
    try:
        result = service.setup_email(request.user_id, request.email)

        return {
            "success": True,
            "method": result.method.value,
            "email": result.email,
            "message": "Verification code sent"
        }

    except Exception as e:
        logger.error(f"Email setup failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/email/confirm", response_model=Dict[str, Any])
async def confirm_email(
    request: ConfirmTOTPRequest,
    service: MFAService = Depends(get_service)
):
    """Confirm Email setup by verifying code."""
    try:
        success = service.confirm_email(request.user_id, request.code)

        if success:
            return {"success": True, "message": "Email MFA enabled successfully"}
        else:
            raise HTTPException(status_code=400, detail="Invalid code")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Email confirm failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/backup-codes/generate", response_model=Dict[str, Any])
async def generate_backup_codes(
    user_id: str,
    service: MFAService = Depends(get_service)
):
    """
    Generate backup codes for user.

    Returns list of one-time backup codes.
    """
    try:
        result = service.setup_backup_codes(user_id)

        return {
            "success": True,
            "method": result.method.value,
            "backup_codes": result.backup_codes,
            "message": "Save these codes securely"
        }

    except Exception as e:
        logger.error(f"Backup codes generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/verify", response_model=Dict[str, Any])
async def verify_mfa(
    request: VerifyRequest,
    service: MFAService = Depends(get_service)
):
    """
    Verify MFA code.

    Validates code for any enabled MFA method.
    """
    try:
        method = MFAMethod(request.method)
        result = service.verify(request.user_id, method, request.code)

        if result.success:
            response = {
                "success": True,
                "method": result.method.value
            }
            if result.backup_code_used:
                response["backup_code_used"] = True
                response["remaining_backup_codes"] = result.remaining_backup_codes
            return response
        else:
            raise HTTPException(status_code=401, detail="Invalid code")

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"MFA verify failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/challenge", response_model=Dict[str, Any])
async def send_challenge(
    request: ChallengeRequest,
    service: MFAService = Depends(get_service)
):
    """
    Send MFA challenge (for SMS/Email methods).

    Triggers sending of verification code.
    """
    try:
        method = MFAMethod(request.method)
        success = service.send_challenge(request.user_id, method)

        if success:
            return {"success": True, "message": "Challenge sent"}
        else:
            raise HTTPException(status_code=400, detail="Method not enabled")

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Send challenge failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/methods/{user_id}", response_model=Dict[str, Any])
async def get_enabled_methods(
    user_id: str,
    service: MFAService = Depends(get_service)
):
    """Get enabled MFA methods for user."""
    try:
        methods = service.get_enabled_methods(user_id)

        return {
            "success": True,
            "user_id": user_id,
            "enabled_methods": [m.value for m in methods],
            "mfa_enabled": len(methods) > 0
        }

    except Exception as e:
        logger.error(f"Get methods failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/method/{user_id}/{method}", response_model=Dict[str, Any])
async def disable_method(
    user_id: str,
    method: str,
    service: MFAService = Depends(get_service)
):
    """Disable MFA method for user."""
    try:
        mfa_method = MFAMethod(method)
        success = service.disable_method(user_id, mfa_method)

        if success:
            return {"success": True, "message": f"{method} disabled"}
        else:
            raise HTTPException(status_code=400, detail="Failed to disable")

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Disable method failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/supported-methods", response_model=Dict[str, Any])
async def get_supported_methods():
    """Get list of supported MFA methods."""
    return {
        "success": True,
        "methods": [
            {"id": "totp", "name": "Authenticator App", "type": "totp"},
            {"id": "sms", "name": "SMS", "type": "sms"},
            {"id": "email", "name": "Email", "type": "email"},
            {"id": "backup_codes", "name": "Backup Codes", "type": "backup"}
        ]
    }
