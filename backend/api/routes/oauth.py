"""
OAuth2/SSO Authentication Routes
Supports: Google, GitHub, Microsoft, GitLab
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import secrets

from core.database import get_db
from core.oauth import SSOManager
from core import security
from models.user import User
from sqlalchemy import select

router = APIRouter(prefix="/oauth", tags=["OAuth2/SSO"])

sso_manager = SSOManager({
    "google": {
        "client_id": "GOOGLE_CLIENT_ID",
        "client_secret": "GOOGLE_CLIENT_SECRET",
        "redirect_uri": "http://localhost:8000/api/oauth/google/callback"
    },
    "github": {
        "client_id": "GITHUB_CLIENT_ID",
        "client_secret": "GITHUB_CLIENT_SECRET",
        "redirect_uri": "http://localhost:8000/api/oauth/github/callback"
    },
    "microsoft": {
        "client_id": "MICROSOFT_CLIENT_ID",
        "client_secret": "MICROSOFT_CLIENT_SECRET",
        "redirect_uri": "http://localhost:8000/api/oauth/microsoft/callback"
    },
    "gitlab": {
        "client_id": "GITLAB_CLIENT_ID",
        "client_secret": "GITLAB_CLIENT_SECRET",
        "redirect_uri": "http://localhost:8000/api/oauth/gitlab/callback"
    }
})


@router.get("/google/login")
async def google_login():
    """
    Initiate Google OAuth2 login
    
    Returns:
        RedirectResponse: Redirect to Google authorization page
    """
    auth_url = sso_manager.get_authorization_url("google")
    return RedirectResponse(url=auth_url)


@router.get("/google/callback")
async def google_callback(
    code: str = Query(...),
    state: str = Query(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Google OAuth2 callback handler
    
    Args:
        code: Authorization code from Google
        state: CSRF protection state
        db: Database session
        
    Returns:
        dict: Access token and user info
    """
    try:
        # Verify state for CSRF protection
        provider = sso_manager.get_provider("google")
        if not provider.verify_state(state):
            raise HTTPException(status_code=400, detail="Invalid state parameter")
        
        # Exchange code for tokens
        tokens = await provider.exchange_code(code)
        
        # Get user info
        user_info = await provider.get_user_info(tokens["access_token"])
        
        # Find or create user
        result = await db.execute(
            select(User).where(User.email == user_info["email"])
        )
        user = result.scalar_one_or_none()
        
        if not user:
            # Create new user
            user = User(
                email=user_info["email"],
                username=user_info["email"].split("@")[0],
                full_name=user_info.get("name", ""),
                is_verified=True,
                oauth_provider="google",
                oauth_id=user_info["sub"]
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
        else:
            # Update OAuth info
            user.oauth_provider = "google"
            user.oauth_id = user_info["sub"]
            user.is_verified = True
            await db.commit()
        
        # Generate JWT tokens
        access_token = security.security.create_access_token({"sub": str(user.id)})
        refresh_token = security.security.create_refresh_token({"sub": str(user.id)})
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "full_name": user.full_name
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/github/login")
async def github_login():
    """
    Initiate GitHub OAuth2 login
    
    Returns:
        RedirectResponse: Redirect to GitHub authorization page
    """
    auth_url = sso_manager.get_authorization_url("github")
    return RedirectResponse(url=auth_url)


@router.get("/github/callback")
async def github_callback(
    code: str = Query(...),
    state: str = Query(...),
    db: AsyncSession = Depends(get_db)
):
    """
    GitHub OAuth2 callback handler
    
    Args:
        code: Authorization code from GitHub
        state: CSRF protection state
        db: Database session
        
    Returns:
        dict: Access token and user info
    """
    try:
        provider = sso_manager.get_provider("github")
        if not provider.verify_state(state):
            raise HTTPException(status_code=400, detail="Invalid state parameter")
        
        tokens = await provider.exchange_code(code)
        user_info = await provider.get_user_info(tokens["access_token"])
        
        result = await db.execute(
            select(User).where(User.email == user_info["email"])
        )
        user = result.scalar_one_or_none()
        
        if not user:
            user = User(
                email=user_info["email"],
                username=user_info["login"],
                full_name=user_info.get("name", ""),
                is_verified=True,
                oauth_provider="github",
                oauth_id=str(user_info["id"])
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
        else:
            user.oauth_provider = "github"
            user.oauth_id = str(user_info["id"])
            user.is_verified = True
            await db.commit()
        
        access_token = security.create_access_token({"sub": str(user.id)})
        refresh_token = security.create_refresh_token({"sub": str(user.id)})
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "full_name": user.full_name
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/microsoft/login")
async def microsoft_login():
    """
    Initiate Microsoft OAuth2 login
    
    Returns:
        RedirectResponse: Redirect to Microsoft authorization page
    """
    auth_url = sso_manager.get_authorization_url("microsoft")
    return RedirectResponse(url=auth_url)


@router.get("/microsoft/callback")
async def microsoft_callback(
    code: str = Query(...),
    state: str = Query(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Microsoft OAuth2 callback handler
    
    Args:
        code: Authorization code from Microsoft
        state: CSRF protection state
        db: Database session
        
    Returns:
        dict: Access token and user info
    """
    try:
        provider = sso_manager.get_provider("microsoft")
        if not provider.verify_state(state):
            raise HTTPException(status_code=400, detail="Invalid state parameter")
        
        tokens = await provider.exchange_code(code)
        user_info = await provider.get_user_info(tokens["access_token"])
        
        result = await db.execute(
            select(User).where(User.email == user_info["mail"])
        )
        user = result.scalar_one_or_none()
        
        if not user:
            user = User(
                email=user_info["mail"],
                username=user_info["mail"].split("@")[0],
                full_name=user_info.get("displayName", ""),
                is_verified=True,
                oauth_provider="microsoft",
                oauth_id=user_info["id"]
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
        else:
            user.oauth_provider = "microsoft"
            user.oauth_id = user_info["id"]
            user.is_verified = True
            await db.commit()
        
        access_token = security.create_access_token({"sub": str(user.id)})
        refresh_token = security.create_refresh_token({"sub": str(user.id)})
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "full_name": user.full_name
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/gitlab/login")
async def gitlab_login():
    """
    Initiate GitLab OAuth2 login
    
    Returns:
        RedirectResponse: Redirect to GitLab authorization page
    """
    auth_url = sso_manager.get_authorization_url("gitlab")
    return RedirectResponse(url=auth_url)


@router.get("/gitlab/callback")
async def gitlab_callback(
    code: str = Query(...),
    state: str = Query(...),
    db: AsyncSession = Depends(get_db)
):
    """
    GitLab OAuth2 callback handler
    
    Args:
        code: Authorization code from GitLab
        state: CSRF protection state
        db: Database session
        
    Returns:
        dict: Access token and user info
    """
    try:
        provider = sso_manager.get_provider("gitlab")
        if not provider.verify_state(state):
            raise HTTPException(status_code=400, detail="Invalid state parameter")
        
        tokens = await provider.exchange_code(code)
        user_info = await provider.get_user_info(tokens["access_token"])
        
        result = await db.execute(
            select(User).where(User.email == user_info["email"])
        )
        user = result.scalar_one_or_none()
        
        if not user:
            user = User(
                email=user_info["email"],
                username=user_info["username"],
                full_name=user_info.get("name", ""),
                is_verified=True,
                oauth_provider="gitlab",
                oauth_id=str(user_info["id"])
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
        else:
            user.oauth_provider = "gitlab"
            user.oauth_id = str(user_info["id"])
            user.is_verified = True
            await db.commit()
        
        access_token = security.create_access_token({"sub": str(user.id)})
        refresh_token = security.create_refresh_token({"sub": str(user.id)})
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "full_name": user.full_name
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/providers")
async def get_providers():
    """
    Get list of available OAuth providers
    
    Returns:
        dict: List of configured OAuth providers
    """
    return {
        "providers": [
            {
                "id": "google",
                "name": "Google",
                "login_url": "/api/oauth/google/login"
            },
            {
                "id": "github",
                "name": "GitHub",
                "login_url": "/api/oauth/github/login"
            },
            {
                "id": "microsoft",
                "name": "Microsoft",
                "login_url": "/api/oauth/microsoft/login"
            },
            {
                "id": "gitlab",
                "name": "GitLab",
                "login_url": "/api/oauth/gitlab/login"
            }
        ]
    }
