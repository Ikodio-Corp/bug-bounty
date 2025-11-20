"""
Marketplace service - Business logic for marketplace operations
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import Optional, List
from datetime import datetime

from models.marketplace import (
    MarketplaceListing, BugNFT, Payment, 
    PaymentStatus, BugFuture, SubscriptionBox
)
from models.bug import Bug
from utils.cache import cache_result


class MarketplaceService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_listing(
        self,
        seller_id: int,
        bug_id: int,
        price: float,
        currency: str = "USD",
        listing_type: str = "bug"
    ) -> MarketplaceListing:
        """Create marketplace listing"""
        listing = MarketplaceListing(
            seller_id=seller_id,
            bug_id=bug_id,
            price=price,
            currency=currency,
            listing_type=listing_type,
            status="active"
        )
        
        self.db.add(listing)
        await self.db.commit()
        await self.db.refresh(listing)
        
        return listing
    
    @cache_result(ttl=300, key_prefix="listing")
    async def get_listing_by_id(self, listing_id: int) -> Optional[MarketplaceListing]:
        """Get listing by ID with caching"""
        result = await self.db.execute(
            select(MarketplaceListing).where(MarketplaceListing.id == listing_id)
        )
        return result.scalar_one_or_none()
    
    async def list_active_listings(
        self,
        skip: int = 0,
        limit: int = 100,
        listing_type: Optional[str] = None
    ) -> List[MarketplaceListing]:
        """List active marketplace listings"""
        query = select(MarketplaceListing).where(
            MarketplaceListing.status == "active"
        )
        
        if listing_type:
            query = query.where(MarketplaceListing.listing_type == listing_type)
        
        query = query.order_by(MarketplaceListing.created_at.desc()).offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def purchase_listing(
        self,
        listing_id: int,
        buyer_id: int,
        payment_method: str
    ) -> Optional[Payment]:
        """Purchase marketplace listing"""
        listing = await self.get_listing_by_id(listing_id)
        if not listing or listing.status != "active":
            return None
        
        payment = Payment(
            buyer_id=buyer_id,
            seller_id=listing.seller_id,
            amount=listing.price,
            currency=listing.currency,
            payment_method=payment_method,
            status=PaymentStatus.PENDING,
            listing_id=listing_id
        )
        
        self.db.add(payment)
        listing.status = "sold"
        listing.sold_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(payment)
        
        return payment
    
    async def mint_nft(
        self,
        bug_id: int,
        owner_id: int,
        token_id: str,
        metadata_url: str,
        mint_price: float
    ) -> BugNFT:
        """Mint bug NFT"""
        nft = BugNFT(
            bug_id=bug_id,
            owner_id=owner_id,
            token_id=token_id,
            metadata_url=metadata_url,
            mint_price=mint_price,
            current_price=mint_price,
            royalty_percentage=10.0
        )
        
        self.db.add(nft)
        await self.db.commit()
        await self.db.refresh(nft)
        
        return nft
    
    async def transfer_nft(
        self,
        nft_id: int,
        new_owner_id: int,
        sale_price: float
    ) -> Optional[BugNFT]:
        """Transfer NFT ownership"""
        result = await self.db.execute(
            select(BugNFT).where(BugNFT.id == nft_id)
        )
        nft = result.scalar_one_or_none()
        
        if not nft:
            return None
        
        nft.owner_id = new_owner_id
        nft.current_price = sale_price
        nft.transfer_count = nft.transfer_count + 1
        nft.last_transfer_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(nft)
        
        return nft
    
    async def create_future(
        self,
        creator_id: int,
        bug_type: str,
        severity: str,
        pre_order_price: float,
        estimated_delivery_date: datetime
    ) -> BugFuture:
        """Create bug future"""
        future = BugFuture(
            creator_id=creator_id,
            bug_type=bug_type,
            severity=severity,
            pre_order_price=pre_order_price,
            estimated_delivery_date=estimated_delivery_date,
            status="available"
        )
        
        self.db.add(future)
        await self.db.commit()
        await self.db.refresh(future)
        
        return future
    
    async def create_subscription_box(
        self,
        creator_id: int,
        name: str,
        description: str,
        monthly_price: float,
        bugs_per_month: int
    ) -> SubscriptionBox:
        """Create subscription box"""
        box = SubscriptionBox(
            creator_id=creator_id,
            name=name,
            description=description,
            monthly_price=monthly_price,
            bugs_per_month=bugs_per_month,
            is_active=True
        )
        
        self.db.add(box)
        await self.db.commit()
        await self.db.refresh(box)
        
        return box
