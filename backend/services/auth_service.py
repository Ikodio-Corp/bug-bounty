"""
Authentication service - Business logic for user authentication
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from typing import Optional

from models.user import User, UserProfile, Subscription, UserRole, SubscriptionTier
from core.security import Security
from utils.cache import cache_result


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.security = Security()
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        result = await self.db.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()
    
    @cache_result(ttl=600, key_prefix="user")
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID with caching"""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def create_user(
        self,
        email: str,
        username: str,
        password: str,
        full_name: str,
        role: UserRole = UserRole.HUNTER,
        subscription_tier: SubscriptionTier = SubscriptionTier.FREE
    ) -> User:
        """Create new user with profile and subscription"""
        # Hash password
        hashed_password = self.security.hash_password(password)
        
        # Create user
        user = User(
            email=email,
            username=username,
            hashed_password=hashed_password,
            full_name=full_name,
            role=role,
            subscription_tier=subscription_tier,
            is_active=True,
            is_verified=True  # Auto-verify for now (SMTP not configured)
        )
        self.db.add(user)
        await self.db.flush()
        
        # Create profile (optional, continue if fails)
        try:
            profile = UserProfile(user_id=user.id)
            self.db.add(profile)
        except Exception as e:
            print(f"Warning: Could not create profile: {e}")
        
        # Create free subscription (optional, continue if fails)
        try:
            subscription = Subscription(
                user_id=user.id,
                tier=subscription_tier,
                status="active",
                price=0.0,
                billing_cycle="monthly",
                start_date=datetime.utcnow()
            )
            self.db.add(subscription)
        except Exception as e:
            print(f"Warning: Could not create subscription: {e}")
        
        # Commit user
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
    
    async def authenticate_user(
        self,
        username: str,
        password: str
    ) -> Optional[User]:
        """Authenticate user with username/password"""
        user = await self.get_user_by_username(username)
        if not user:
            # Try email
            user = await self.get_user_by_email(username)
        
        if not user:
            return None
        
        if not self.security.verify_password(password, user.hashed_password):
            return None
        
        return user
    
    async def update_last_login(self, user_id: int):
        """Update user's last login timestamp"""
        user = await self.get_user_by_id(user_id)
        if user:
            user.last_login = datetime.utcnow()
            await self.db.commit()
    
    async def update_password(self, user_id: int, new_password: str):
        """Update user password"""
        user = await self.get_user_by_id(user_id)
        if user:
            user.hashed_password = self.security.hash_password(new_password)
            await self.db.commit()
    
    async def verify_user_email(self, user_id: int):
        """Verify user email"""
        user = await self.get_user_by_id(user_id)
        if user:
            user.is_verified = True
            await self.db.commit()
    
    async def deactivate_user(self, user_id: int):
        """Deactivate user account"""
        user = await self.get_user_by_id(user_id)
        if user:
            user.is_active = False
            await self.db.commit()
    
    async def activate_user(self, user_id: int):
        """Activate user account"""
        user = await self.get_user_by_id(user_id)
        if user:
            user.is_active = True
            await self.db.commit()
