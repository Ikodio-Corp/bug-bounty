"""
Marketplace Service
Bug trading and futures marketplace
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from sqlalchemy.orm import Session

from models.marketplace_extended import (
    BugMarketplaceListing,
    BugMarketplaceTrade,
    BugFuture,
    BugFuturePosition,
    MarketplaceListingStatus
)
from models.bug import Bug


class MarketplaceService:
    """
    Service for bug marketplace and futures trading
    """
    
    PLATFORM_FEE_PERCENTAGE = 0.10
    INSTANT_PAYMENT_PERCENTAGE = 0.80
    
    def __init__(self, db: Session):
        self.db = db
    
    async def create_listing(
        self,
        bug_id: int,
        seller_id: int,
        listing_price: float,
        description: Optional[str] = None
    ) -> BugMarketplaceListing:
        """
        Create new marketplace listing for bug
        """
        
        bug = self.db.query(Bug).filter(Bug.id == bug_id).first()
        if not bug:
            raise ValueError("Bug not found")
        
        if bug.hunter_id != seller_id:
            raise ValueError("Only bug hunter can list their bug")
        
        listing = BugMarketplaceListing(
            bug_id=bug_id,
            seller_id=seller_id,
            listing_price=listing_price,
            instant_payment_percentage=self.INSTANT_PAYMENT_PERCENTAGE,
            original_bounty_amount=bug.bounty_amount,
            status=MarketplaceListingStatus.PENDING_VERIFICATION,
            description=description,
            listed_at=datetime.utcnow()
        )
        
        self.db.add(listing)
        self.db.commit()
        self.db.refresh(listing)
        
        return listing
    
    async def verify_listing(self, listing_id: int) -> BugMarketplaceListing:
        """
        Verify and activate marketplace listing
        """
        
        listing = self.db.query(BugMarketplaceListing).filter(
            BugMarketplaceListing.id == listing_id
        ).first()
        
        if not listing:
            raise ValueError("Listing not found")
        
        listing.status = MarketplaceListingStatus.ACTIVE
        listing.verification_status = "verified"
        listing.verified_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(listing)
        
        return listing
    
    async def execute_trade(
        self,
        listing_id: int,
        buyer_id: int,
        payment_method: str = "stripe"
    ) -> BugMarketplaceTrade:
        """
        Execute instant trade with 80% instant payment to seller
        """
        
        listing = self.db.query(BugMarketplaceListing).filter(
            BugMarketplaceListing.id == listing_id
        ).first()
        
        if not listing or listing.status != MarketplaceListingStatus.ACTIVE:
            raise ValueError("Listing not available")
        
        platform_fee = listing.listing_price * self.PLATFORM_FEE_PERCENTAGE
        seller_receives = listing.listing_price - platform_fee
        
        instant_payment = seller_receives * self.INSTANT_PAYMENT_PERCENTAGE
        
        trade = BugMarketplaceTrade(
            listing_id=listing_id,
            buyer_id=buyer_id,
            seller_id=listing.seller_id,
            trade_price=listing.listing_price,
            platform_fee=platform_fee,
            seller_receives=instant_payment,
            trade_status="completed",
            payment_method=payment_method,
            payment_reference=f"TRADE-{listing_id}-{datetime.now().timestamp()}",
            traded_at=datetime.utcnow(),
            completed_at=datetime.utcnow()
        )
        
        self.db.add(trade)
        
        listing.status = MarketplaceListingStatus.SOLD
        listing.sold_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(trade)
        
        return trade
    
    async def create_bug_future(
        self,
        creator_id: int,
        contract_name: str,
        target_company: str,
        vulnerability_type: str,
        contract_price: float,
        payout_condition: str,
        expiration_days: int = 90
    ) -> BugFuture:
        """
        Create bug futures contract
        """
        
        future = BugFuture(
            contract_name=contract_name,
            target_company=target_company,
            vulnerability_type=vulnerability_type,
            contract_price=contract_price,
            payout_condition=payout_condition,
            expiration_date=datetime.utcnow() + timedelta(days=expiration_days),
            status="active",
            creator_id=creator_id
        )
        
        self.db.add(future)
        self.db.commit()
        self.db.refresh(future)
        
        return future
    
    async def buy_future_position(
        self,
        future_id: int,
        user_id: int,
        quantity: int,
        position_type: str = "long"
    ) -> BugFuturePosition:
        """
        Buy futures position (long or short)
        """
        
        future = self.db.query(BugFuture).filter(
            BugFuture.id == future_id
        ).first()
        
        if not future or future.status != "active":
            raise ValueError("Future not available")
        
        if datetime.utcnow() >= future.expiration_date:
            raise ValueError("Future has expired")
        
        position = BugFuturePosition(
            future_id=future_id,
            user_id=user_id,
            position_type=position_type,
            quantity=quantity,
            entry_price=future.contract_price,
            current_value=future.contract_price * quantity,
            unrealized_pnl=0,
            status="open"
        )
        
        self.db.add(position)
        
        future.total_contracts_traded += quantity
        
        self.db.commit()
        self.db.refresh(position)
        
        return position
    
    async def settle_future_position(
        self,
        position_id: int,
        settlement_price: float
    ) -> BugFuturePosition:
        """
        Settle futures position at expiration
        """
        
        position = self.db.query(BugFuturePosition).filter(
            BugFuturePosition.id == position_id
        ).first()
        
        if not position or position.status != "open":
            raise ValueError("Position not available")
        
        if position.position_type == "long":
            pnl = (settlement_price - position.entry_price) * position.quantity
        else:
            pnl = (position.entry_price - settlement_price) * position.quantity
        
        position.status = "closed"
        position.closed_at = datetime.utcnow()
        position.realized_pnl = pnl
        
        self.db.commit()
        self.db.refresh(position)
        
        return position
    
    async def get_marketplace_stats(self) -> Dict:
        """
        Get marketplace statistics
        """
        
        total_listings = self.db.query(BugMarketplaceListing).count()
        active_listings = self.db.query(BugMarketplaceListing).filter(
            BugMarketplaceListing.status == MarketplaceListingStatus.ACTIVE
        ).count()
        
        total_trades = self.db.query(BugMarketplaceTrade).count()
        
        total_volume = self.db.query(
            self.db.func.sum(BugMarketplaceTrade.trade_price)
        ).scalar() or 0
        
        return {
            "total_listings": total_listings,
            "active_listings": active_listings,
            "total_trades": total_trades,
            "total_volume": total_volume,
            "platform_fees_collected": total_volume * self.PLATFORM_FEE_PERCENTAGE
        }
