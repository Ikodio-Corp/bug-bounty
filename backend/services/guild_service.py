"""
Guild service - Business logic for guild management
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List

from models.community import GuildMembership, GuildProposal, GuildMembershipTier
from utils.cache import cache_result


class GuildService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def join_guild(
        self,
        user_id: int,
        guild_name: str,
        tier: GuildMembershipTier = GuildMembershipTier.APPRENTICE
    ) -> GuildMembership:
        """Join guild"""
        membership = GuildMembership(
            user_id=user_id,
            guild_name=guild_name,
            tier=tier,
            contribution_points=0,
            is_active=True
        )
        
        self.db.add(membership)
        await self.db.commit()
        await self.db.refresh(membership)
        
        return membership
    
    @cache_result(ttl=600, key_prefix="guild_membership")
    async def get_user_membership(
        self,
        user_id: int,
        guild_name: str
    ) -> Optional[GuildMembership]:
        """Get user guild membership with caching"""
        result = await self.db.execute(
            select(GuildMembership).where(
                GuildMembership.user_id == user_id,
                GuildMembership.guild_name == guild_name
            )
        )
        return result.scalar_one_or_none()
    
    async def upgrade_tier(
        self,
        membership_id: int,
        new_tier: GuildMembershipTier
    ) -> Optional[GuildMembership]:
        """Upgrade guild membership tier"""
        result = await self.db.execute(
            select(GuildMembership).where(GuildMembership.id == membership_id)
        )
        membership = result.scalar_one_or_none()
        
        if not membership:
            return None
        
        membership.tier = new_tier
        await self.db.commit()
        await self.db.refresh(membership)
        
        return membership
    
    async def add_contribution_points(
        self,
        membership_id: int,
        points: int
    ) -> Optional[GuildMembership]:
        """Add contribution points"""
        result = await self.db.execute(
            select(GuildMembership).where(GuildMembership.id == membership_id)
        )
        membership = result.scalar_one_or_none()
        
        if not membership:
            return None
        
        membership.contribution_points += points
        await self.db.commit()
        await self.db.refresh(membership)
        
        return membership
    
    async def create_proposal(
        self,
        guild_name: str,
        proposer_id: int,
        title: str,
        description: str,
        proposal_type: str
    ) -> GuildProposal:
        """Create guild proposal"""
        proposal = GuildProposal(
            guild_name=guild_name,
            proposer_id=proposer_id,
            title=title,
            description=description,
            proposal_type=proposal_type,
            status="voting",
            votes_for=0,
            votes_against=0
        )
        
        self.db.add(proposal)
        await self.db.commit()
        await self.db.refresh(proposal)
        
        return proposal
    
    async def vote_on_proposal(
        self,
        proposal_id: int,
        vote_for: bool
    ) -> Optional[GuildProposal]:
        """Vote on guild proposal"""
        result = await self.db.execute(
            select(GuildProposal).where(GuildProposal.id == proposal_id)
        )
        proposal = result.scalar_one_or_none()
        
        if not proposal:
            return None
        
        if vote_for:
            proposal.votes_for += 1
        else:
            proposal.votes_against += 1
        
        await self.db.commit()
        await self.db.refresh(proposal)
        
        return proposal
    
    async def list_guild_members(self, guild_name: str) -> List[GuildMembership]:
        """List guild members"""
        result = await self.db.execute(
            select(GuildMembership).where(
                GuildMembership.guild_name == guild_name,
                GuildMembership.is_active == True
            ).order_by(GuildMembership.contribution_points.desc())
        )
        return result.scalars().all()
