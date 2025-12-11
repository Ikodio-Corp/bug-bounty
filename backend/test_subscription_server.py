#!/usr/bin/env python3
"""
Minimal test server for subscription system
Only includes auth and usage tracking routes
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta

# Core imports
from core.database import get_async_db, init_db, close_db
from core.security import Security
from models.user import User, UserRole, SubscriptionTier
from schemas.auth import UserRegister, UserLogin, Token
from services.auth_service import AuthService
from services.usage_tracking_service import UsageTrackingService

# Create app
app = FastAPI(
    title="IKODIO BugBounty - Subscription Test Server",
    version="1.0.0",
    description="Test server for subscription system"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = Security()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# Startup/Shutdown
@app.on_event("startup")
async def startup():
    await init_db()
    print("Database initialized")

@app.on_event("shutdown")
async def shutdown():
    await close_db()

# Health endpoint
@app.get("/")
async def root():
    return {"message": "IKODIO Subscription Test Server", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy", "database": "connected"}

# Auth endpoints
@app.post("/api/auth/register", status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    db: AsyncSession = Depends(get_async_db)
):
    """Register new user with subscription tier"""
    auth_service = AuthService(db)
    
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
    
    # Create user with subscription tier
    user = await auth_service.create_user(
        email=user_data.email,
        username=user_data.username,
        password=user_data.password,
        full_name=user_data.full_name,
        role=user_data.role or UserRole.HUNTER,
        subscription_tier=user_data.subscription_tier or SubscriptionTier.FREE
    )
    
    # Generate tokens
    access_token = security.create_access_token(
        data={"sub": str(user.id), "role": user.role.value}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "subscription_tier": user.subscription_tier.value
        }
    }

@app.post("/api/auth/login")
async def login(
    user_data: UserLogin,
    db: AsyncSession = Depends(get_async_db)
):
    """Login user"""
    auth_service = AuthService(db)
    
    user = await auth_service.authenticate_user(
        username=user_data.username,
        password=user_data.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    access_token = security.create_access_token(
        data={"sub": str(user.id), "role": user.role.value}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

# Usage tracking endpoints
@app.get("/api/usage/summary")
async def get_usage_summary(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_async_db)
):
    """Get current usage summary"""
    current_user = await security.get_current_user(token, db)
    from core.database import get_db
    sync_db = next(get_db())
    usage_service = UsageTrackingService(sync_db)
    
    summary = usage_service.get_usage_summary(current_user)
    sync_db.close()
    
    return summary

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
