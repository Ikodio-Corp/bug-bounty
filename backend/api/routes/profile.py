"""
Profile management routes
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from core.database import get_db
from middleware.auth import get_current_user
from models.user import User, UserProfile

router = APIRouter()


class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    website: Optional[str] = None
    github_username: Optional[str] = None
    twitter_username: Optional[str] = None
    linkedin_url: Optional[str] = None
    discord_username: Optional[str] = None
    specializations: Optional[str] = None
    skills: Optional[str] = None


class UserProfileUpdate(BaseModel):
    about_me: Optional[str] = None
    experience_years: Optional[int] = None
    preferred_platforms: Optional[str] = None
    preferred_vulnerabilities: Optional[str] = None
    preferred_industries: Optional[str] = None
    certifications: Optional[str] = None
    education: Optional[str] = None
    portfolio_url: Optional[str] = None
    blog_url: Optional[str] = None


@router.get("/profile")
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user profile"""
    profile = db.query(UserProfile).filter(
        UserProfile.user_id == current_user.id
    ).first()
    
    return {
        "user": {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "full_name": current_user.full_name,
            "bio": current_user.bio,
            "avatar_url": current_user.avatar_url,
            "location": current_user.location,
            "website": current_user.website,
            "github_username": current_user.github_username,
            "twitter_username": current_user.twitter_username,
            "linkedin_url": current_user.linkedin_url,
            "discord_username": current_user.discord_username,
            "total_bounties_earned": current_user.total_bounties_earned,
            "total_bugs_found": current_user.total_bugs_found,
            "reputation_score": current_user.reputation_score,
            "hunter_rank": current_user.hunter_rank,
            "specializations": current_user.specializations,
            "skills": current_user.skills,
            "subscription_tier": current_user.subscription_tier,
            "created_at": current_user.created_at.isoformat()
        },
        "profile": {
            "about_me": profile.about_me if profile else None,
            "experience_years": profile.experience_years if profile else None,
            "total_scans": profile.total_scans if profile else 0,
            "successful_reports": profile.successful_reports if profile else 0,
            "acceptance_rate": profile.acceptance_rate if profile else 0,
            "avg_severity": profile.avg_severity if profile else 0,
            "preferred_platforms": profile.preferred_platforms if profile else None,
            "preferred_vulnerabilities": profile.preferred_vulnerabilities if profile else None,
            "certifications": profile.certifications if profile else None,
            "portfolio_url": profile.portfolio_url if profile else None,
            "blog_url": profile.blog_url if profile else None
        } if profile else None
    }


@router.put("/profile")
async def update_profile(
    profile_data: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user profile"""
    update_data = profile_data.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    
    return {"message": "Profile updated successfully"}


@router.put("/profile/details")
async def update_profile_details(
    profile_data: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update detailed profile information"""
    profile = db.query(UserProfile).filter(
        UserProfile.user_id == current_user.id
    ).first()
    
    if not profile:
        profile = UserProfile(user_id=current_user.id)
        db.add(profile)
    
    update_data = profile_data.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(profile, field, value)
    
    db.commit()
    db.refresh(profile)
    
    return {"message": "Profile details updated successfully"}


@router.post("/profile/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload user avatar"""
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    if file.size > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size must be less than 5MB")
    
    import os
    import uuid
    from pathlib import Path
    
    upload_dir = Path("uploads/avatars")
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    file_extension = file.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = upload_dir / filename
    
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    current_user.avatar_url = f"/uploads/avatars/{filename}"
    db.commit()
    
    return {
        "message": "Avatar uploaded successfully",
        "avatar_url": current_user.avatar_url
    }


@router.get("/profile/{username}")
async def get_public_profile(
    username: str,
    db: Session = Depends(get_db)
):
    """Get public user profile"""
    user = db.query(User).filter(User.username == username).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    profile = db.query(UserProfile).filter(
        UserProfile.user_id == user.id
    ).first()
    
    return {
        "username": user.username,
        "full_name": user.full_name,
        "bio": user.bio,
        "avatar_url": user.avatar_url,
        "location": user.location,
        "website": user.website,
        "github_username": user.github_username,
        "twitter_username": user.twitter_username,
        "total_bounties_earned": user.total_bounties_earned,
        "total_bugs_found": user.total_bugs_found,
        "reputation_score": user.reputation_score,
        "hunter_rank": user.hunter_rank,
        "specializations": user.specializations,
        "skills": user.skills,
        "about_me": profile.about_me if profile else None,
        "experience_years": profile.experience_years if profile else None,
        "certifications": profile.certifications if profile else None,
        "portfolio_url": profile.portfolio_url if profile else None,
        "blog_url": profile.blog_url if profile else None,
        "created_at": user.created_at.isoformat()
    }


@router.get("/profile/stats")
async def get_profile_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user statistics"""
    from models.bug import Bug
    from models.community import Scan
    
    total_bugs = db.query(Bug).filter(Bug.hunter_id == current_user.id).count()
    validated_bugs = db.query(Bug).filter(
        Bug.hunter_id == current_user.id,
        Bug.validated == True
    ).count()
    
    total_scans = db.query(Scan).filter(Scan.user_id == current_user.id).count()
    
    return {
        "total_bugs": total_bugs,
        "validated_bugs": validated_bugs,
        "validation_rate": (validated_bugs / total_bugs * 100) if total_bugs > 0 else 0,
        "total_scans": total_scans,
        "total_bounties": current_user.total_bounties_earned,
        "reputation_score": current_user.reputation_score,
        "hunter_rank": current_user.hunter_rank
    }
