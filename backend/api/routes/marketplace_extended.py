"""
Marketplace API Routes
Bug trading and futures marketplace endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.database import get_db
from core.security import get_current_user
from services.marketplace_extended_service import MarketplaceService
from models.user import User


router = APIRouter(prefix="/api/marketplace", tags=["Marketplace"])


@router.post("/listings")
async def create_listing(
    bug_id: int,
    listing_price: float,
    description: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List bug on marketplace with 80% instant payment
    """
    
    service = MarketplaceService(db)
    
    try:
        listing = await service.create_listing(
            bug_id=bug_id,
            seller_id=current_user.id,
            listing_price=listing_price,
            description=description
        )
        
        return {
            "success": True,
            "data": {
                "listing_id": listing.id,
                "bug_id": listing.bug_id,
                "listing_price": listing.listing_price,
                "instant_payment_percentage": listing.instant_payment_percentage,
                "status": listing.status
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/listings")
async def get_listings(
    status: str = "active",
    db: Session = Depends(get_db)
):
    """
    Get all marketplace listings
    """
    
    from models.marketplace_extended import BugMarketplaceListing
    
    listings = db.query(BugMarketplaceListing).filter(
        BugMarketplaceListing.status == status
    ).all()
    
    return {
        "success": True,
        "data": [
            {
                "listing_id": listing.id,
                "bug_id": listing.bug_id,
                "listing_price": listing.listing_price,
                "instant_payment_percentage": listing.instant_payment_percentage,
                "status": listing.status,
                "listed_at": listing.listed_at
            }
            for listing in listings
        ]
    }


@router.post("/listings/{listing_id}/buy")
async def buy_listing(
    listing_id: int,
    payment_method: str = "stripe",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Buy bug from marketplace with instant payment to seller
    """
    
    service = MarketplaceService(db)
    
    try:
        trade = await service.execute_trade(
            listing_id=listing_id,
            buyer_id=current_user.id,
            payment_method=payment_method
        )
        
        return {
            "success": True,
            "data": {
                "trade_id": trade.id,
                "trade_price": trade.trade_price,
                "platform_fee": trade.platform_fee,
                "seller_receives": trade.seller_receives,
                "status": trade.trade_status,
                "traded_at": trade.traded_at
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/futures")
async def create_future(
    contract_name: str,
    target_company: str,
    vulnerability_type: str,
    contract_price: float,
    payout_condition: str,
    expiration_days: int = 90,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create bug futures contract
    """
    
    service = MarketplaceService(db)
    
    try:
        future = await service.create_bug_future(
            creator_id=current_user.id,
            contract_name=contract_name,
            target_company=target_company,
            vulnerability_type=vulnerability_type,
            contract_price=contract_price,
            payout_condition=payout_condition,
            expiration_days=expiration_days
        )
        
        return {
            "success": True,
            "data": {
                "future_id": future.id,
                "contract_name": future.contract_name,
                "contract_price": future.contract_price,
                "expiration_date": future.expiration_date,
                "status": future.status
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/futures")
async def get_futures(
    status: str = "active",
    db: Session = Depends(get_db)
):
    """
    Get all bug futures contracts
    """
    
    from models.marketplace_extended import BugFuture
    
    futures = db.query(BugFuture).filter(
        BugFuture.status == status
    ).all()
    
    return {
        "success": True,
        "data": [
            {
                "future_id": future.id,
                "contract_name": future.contract_name,
                "target_company": future.target_company,
                "vulnerability_type": future.vulnerability_type,
                "contract_price": future.contract_price,
                "expiration_date": future.expiration_date,
                "total_contracts_traded": future.total_contracts_traded
            }
            for future in futures
        ]
    }


@router.post("/futures/{future_id}/buy")
async def buy_future_position(
    future_id: int,
    quantity: int,
    position_type: str = "long",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Buy futures position (long or short)
    """
    
    service = MarketplaceService(db)
    
    try:
        position = await service.buy_future_position(
            future_id=future_id,
            user_id=current_user.id,
            quantity=quantity,
            position_type=position_type
        )
        
        return {
            "success": True,
            "data": {
                "position_id": position.id,
                "future_id": position.future_id,
                "position_type": position.position_type,
                "quantity": position.quantity,
                "entry_price": position.entry_price,
                "current_value": position.current_value
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/stats")
async def get_marketplace_stats(
    db: Session = Depends(get_db)
):
    """
    Get marketplace statistics
    """
    
    service = MarketplaceService(db)
    
    try:
        stats = await service.get_marketplace_stats()
        
        return {
            "success": True,
            "data": stats
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
