"""
User schemas - Pydantic models for user-related requests/responses
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from models.user import UserRole


class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=1, max_length=255)
    role: Optional[UserRole] = UserRole.HUNTER


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    bio: Optional[str] = None
    github_username: Optional[str] = None
    twitter_username: Optional[str] = None
    website: Optional[str] = None


class UserResponse(BaseModel):
    user_id: int
    email: EmailStr
    username: str
    full_name: str
    role: UserRole
    reputation_score: float
    total_bugs_found: int
    total_earnings: float
    is_active: bool
    is_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserProfileResponse(UserResponse):
    bio: Optional[str]
    github_username: Optional[str]
    twitter_username: Optional[str]
    website: Optional[str]
    rank: int
    badges: list
    
    class Config:
        from_attributes = True
