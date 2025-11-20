"""
Authentication routes - Login, Register, Token Management
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta
import re

from core.database import get_async_db
from core.security import Security
from core.config import settings
from models.user import User, UserRole
from schemas.auth import (
    UserRegister, UserLogin, Token, TokenRefresh,
    PasswordChange, PasswordReset
)
from services.auth_service import AuthService
from integrations.email_client import send_verification_email

router = APIRouter()
security = Security()

# List of temporary email domains
TEMP_EMAIL_DOMAINS = [
    'tempmail.com', 'guerrillamail.com', '10minutemail.com',
    'throwaway.email', 'mailinator.com', 'maildrop.cc',
    'temp-mail.org', 'yopmail.com', 'getairmail.com',
    'trashmail.com', 'fakeinbox.com', 'dispostable.com'
]

def is_temp_email(email: str) -> bool:
    """Check if email is from a temporary email provider"""
    domain = email.split('@')[1].lower() if '@' in email else ''
    return domain in TEMP_EMAIL_DOMAINS


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_async_db)
):
    """Register new user"""
    auth_service = AuthService(db)
    
    # Check for temporary email
    if is_temp_email(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Temporary email addresses are not allowed"
        )
    
    # Check if user exists
    existing_user = await auth_service.get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    existing_username = await auth_service.get_user_by_username(user_data.username)
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Create user
    user = await auth_service.create_user(
        email=user_data.email,
        username=user_data.username,
        password=user_data.password,
        full_name=user_data.full_name,
        role=user_data.role or UserRole.HUNTER
    )
    
    # Generate verification token
    verification_token = security.create_access_token(
        data={"sub": str(user.id), "type": "email_verification"},
        expires_delta=timedelta(hours=24)
    )
    
    # Try to send verification email (don't fail if SMTP not configured)
    try:
        background_tasks.add_task(
            send_verification_email,
            email=user.email,
            token=verification_token,
            username=user.username
        )
    except Exception as e:
        print(f"Warning: Could not send verification email: {e}")
    
    # Generate tokens
    access_token = security.create_access_token(
        data={"sub": str(user.id), "role": user.role.value}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "message": "Registration successful! Please check your email to verify your account.",
        "user": {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "email_verified": user.email_verified
        }
    }


@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_async_db)
):
    """Login user"""
    auth_service = AuthService(db)
    
    # Authenticate user
    user = await auth_service.authenticate_user(
        form_data.username,
        form_data.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )
    
    # Generate access token
    access_token = security.create_access_token(
        data={"sub": str(user.id), "role": user.role.value}
    )
    
    # Update last login
    await auth_service.update_last_login(user.id)
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.post("/refresh", response_model=Token)
async def refresh_token(
    token_data: TokenRefresh,
    db: AsyncSession = Depends(get_async_db)
):
    """Refresh access token"""
    try:
        payload = security.verify_token(token_data.refresh_token)
        user_id = int(payload.get("sub"))
        
        auth_service = AuthService(db)
        user = await auth_service.get_user_by_id(user_id)
        
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Generate new tokens
        access_token = security.create_access_token(
            data={"sub": str(user.id), "role": user.role.value}
        )
        refresh_token = security.create_refresh_token(
            data={"sub": str(user.id)}
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )


@router.post("/logout")
async def logout():
    """Logout user (client should delete tokens)"""
    return {"message": "Successfully logged out"}


@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(security.get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Change user password"""
    auth_service = AuthService(db)
    
    # Verify current password
    user = await auth_service.authenticate_user(
        current_user.username,
        password_data.current_password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Update password
    await auth_service.update_password(user.id, password_data.new_password)
    
    return {"message": "Password changed successfully"}


@router.post("/request-password-reset")
async def request_password_reset(
    email: str,
    db: AsyncSession = Depends(get_async_db)
):
    """Request password reset (sends email with reset token)"""
    auth_service = AuthService(db)
    
    user = await auth_service.get_user_by_email(email)
    if not user:
        # Don't reveal if email exists
        return {"message": "If email exists, reset instructions have been sent"}
    
    # Generate reset token
    reset_token = security.create_access_token(
        data={"sub": str(user.id), "type": "password_reset"},
        expires_delta=timedelta(hours=1)
    )
    
    # TODO: Send email with reset token
    # For now, just return the token (in production, send via email)
    
    return {
        "message": "Password reset instructions sent",
        "reset_token": reset_token  # Remove this in production
    }


@router.post("/reset-password")
async def reset_password(
    reset_data: PasswordReset,
    db: AsyncSession = Depends(get_async_db)
):
    """Reset password using reset token"""
    try:
        payload = security.verify_token(reset_data.token)
        
        if payload.get("type") != "password_reset":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid reset token"
            )
        
        user_id = int(payload.get("sub"))
        
        auth_service = AuthService(db)
        await auth_service.update_password(user_id, reset_data.new_password)
        
        return {"message": "Password reset successfully"}
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )


@router.get("/verify-email")
async def verify_email(
    token: str,
    db: AsyncSession = Depends(get_async_db)
):
    """Verify user email address"""
    try:
        payload = security.verify_token(token)
        
        if payload.get("type") != "email_verification":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification token"
            )
        
        user_id = int(payload.get("sub"))
        
        auth_service = AuthService(db)
        user = await auth_service.get_user_by_id(user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if user.email_verified:
            return {"message": "Email already verified"}
        
        # Mark email as verified
        user.email_verified = True
        await db.commit()
        
        return {"message": "Email verified successfully"}
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token"
        )


@router.post("/resend-verification")
async def resend_verification(
    email_data: dict,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_async_db)
):
    """Resend verification email"""
    auth_service = AuthService(db)
    user = await auth_service.get_user_by_email(email_data.get("email"))
    
    if not user:
        # Don't reveal if email exists
        return {"message": "If account exists, verification email will be sent"}
    
    if user.email_verified:
        return {"message": "Email already verified"}
    
    # Generate new verification token
    verification_token = security.create_access_token(
        data={"sub": str(user.id), "type": "email_verification"},
        expires_delta=timedelta(hours=24)
    )
    
    # Send verification email in background
    background_tasks.add_task(
        send_verification_email,
        email=user.email,
        token=verification_token,
        username=user.username
    )
    
    return {"message": "Verification email sent"}


@router.get("/google/login")
async def google_login():
    """Redirect to Google OAuth"""
    # This would redirect to Google OAuth in production
    # For now, just redirect to dashboard (placeholder)
    return {
        "message": "Google OAuth not configured yet",
        "redirect_url": f"{settings.FRONTEND_URL}/dashboard"
    }


@router.get("/github/login")
async def github_login():
    """Redirect to GitHub OAuth"""
    # This would redirect to GitHub OAuth in production
    # For now, just redirect to dashboard (placeholder)
    return {
        "message": "GitHub OAuth not configured yet",
        "redirect_url": f"{settings.FRONTEND_URL}/dashboard"
    }
