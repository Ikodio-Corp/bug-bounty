"""
Test marketplace functionality
"""
import pytest
from services.marketplace_service import MarketplaceService
from models.marketplace import MarketplaceListing, BugNFT
from datetime import datetime


@pytest.fixture
def marketplace_service():
    return MarketplaceService()


class TestMarketplaceListing:
    """Test marketplace listing functions"""
    
    def test_create_listing(self, marketplace_service, db_session, test_user):
        """Test creating marketplace listing"""
        listing_data = {
            "seller_id": test_user.id,
            "title": "Critical XSS Vulnerability Fix",
            "description": "Professional fix for XSS vulnerability",
            "price": 500.00,
            "category": "vulnerability_fix",
            "delivery_time": 3
        }
        
        listing = marketplace_service.create_listing(db_session, listing_data)
        
        assert listing.id is not None
        assert listing.price == 500.00
        assert listing.status == "active"
    
    def test_get_marketplace_listings(self, marketplace_service, db_session, test_user):
        """Test getting marketplace listings"""
        # Create test listings
        for i in range(3):
            marketplace_service.create_listing(db_session, {
                "seller_id": test_user.id,
                "title": f"Listing {i+1}",
                "description": f"Description {i+1}",
                "price": 100.00 * (i + 1),
                "category": "vulnerability_fix",
                "delivery_time": 5
            })
        
        listings = marketplace_service.get_listings(db_session, skip=0, limit=10)
        assert len(listings) >= 3
    
    def test_purchase_listing(self, marketplace_service, db_session, test_user):
        """Test purchasing a listing"""
        listing = marketplace_service.create_listing(db_session, {
            "seller_id": test_user.id,
            "title": "Test Fix",
            "description": "Test description",
            "price": 250.00,
            "category": "vulnerability_fix",
            "delivery_time": 7
        })
        
        result = marketplace_service.purchase_listing(
            db_session,
            listing.id,
            test_user.id
        )
        
        assert result is not None
        assert result["status"] == "purchased"


class TestBugNFT:
    """Test Bug NFT functions"""
    
    def test_mint_bug_nft(self, marketplace_service, db_session, test_user):
        """Test minting bug NFT"""
        nft_data = {
            "bug_id": 1,
            "owner_id": test_user.id,
            "metadata": {
                "name": "Critical Bug #001",
                "description": "First critical bug found",
                "attributes": {
                    "severity": "critical",
                    "type": "XSS",
                    "bounty": 1000
                }
            }
        }
        
        nft = marketplace_service.mint_bug_nft(db_session, nft_data)
        
        assert nft.id is not None
        assert nft.token_id is not None
        assert nft.owner_id == test_user.id
    
    def test_transfer_nft(self, marketplace_service, db_session, test_user):
        """Test transferring NFT"""
        nft = marketplace_service.mint_bug_nft(db_session, {
            "bug_id": 1,
            "owner_id": test_user.id,
            "metadata": {"name": "Test NFT"}
        })
        
        # Create recipient user
        from models.user import User
        recipient = User(
            username="recipient",
            email="recipient@test.com",
            hashed_password="hashed"
        )
        db_session.add(recipient)
        db_session.commit()
        
        result = marketplace_service.transfer_nft(
            db_session,
            nft.id,
            test_user.id,
            recipient.id
        )
        
        assert result is True
        db_session.refresh(nft)
        assert nft.owner_id == recipient.id
    
    def test_list_nft_for_sale(self, marketplace_service, db_session, test_user):
        """Test listing NFT for sale"""
        nft = marketplace_service.mint_bug_nft(db_session, {
            "bug_id": 1,
            "owner_id": test_user.id,
            "metadata": {"name": "Sale NFT"}
        })
        
        result = marketplace_service.list_nft_for_sale(
            db_session,
            nft.id,
            price=750.00
        )
        
        assert result is True
        db_session.refresh(nft)
        assert nft.listed_price == 750.00


class TestBugFutures:
    """Test bug futures trading"""
    
    def test_create_bug_future(self, marketplace_service, db_session, test_user):
        """Test creating bug future contract"""
        future_data = {
            "bug_type": "XSS",
            "strike_price": 500.00,
            "expiry_date": "2025-12-31",
            "contract_size": 10
        }
        
        future = marketplace_service.create_bug_future(db_session, future_data)
        
        assert future.id is not None
        assert future.strike_price == 500.00
    
    def test_trade_bug_future(self, marketplace_service, db_session, test_user):
        """Test trading bug future"""
        future = marketplace_service.create_bug_future(db_session, {
            "bug_type": "SQL Injection",
            "strike_price": 1000.00,
            "expiry_date": "2025-12-31",
            "contract_size": 5
        })
        
        result = marketplace_service.trade_bug_future(
            db_session,
            future.id,
            test_user.id,
            quantity=2,
            action="buy"
        )
        
        assert result is not None
        assert result["status"] == "success"


class TestSubscriptionBox:
    """Test subscription box service"""
    
    def test_create_subscription(self, marketplace_service, db_session, test_user):
        """Test creating subscription"""
        subscription_data = {
            "user_id": test_user.id,
            "plan": "premium",
            "price": 99.00,
            "interval": "monthly",
            "features": ["Unlimited scans", "Priority support", "API access"]
        }
        
        subscription = marketplace_service.create_subscription(
            db_session,
            subscription_data
        )
        
        assert subscription.id is not None
        assert subscription.status == "active"
    
    def test_cancel_subscription(self, marketplace_service, db_session, test_user):
        """Test canceling subscription"""
        subscription = marketplace_service.create_subscription(db_session, {
            "user_id": test_user.id,
            "plan": "basic",
            "price": 49.00,
            "interval": "monthly",
            "features": ["10 scans/month"]
        })
        
        result = marketplace_service.cancel_subscription(
            db_session,
            subscription.id
        )
        
        assert result is True
        db_session.refresh(subscription)
        assert subscription.status == "canceled"


class TestFixOffers:
    """Test fix offer system"""
    
    def test_create_fix_offer(self, marketplace_service, db_session, test_user):
        """Test creating fix offer"""
        offer_data = {
            "bug_id": 1,
            "developer_id": test_user.id,
            "price": 300.00,
            "delivery_time": 5,
            "description": "I can fix this within 5 days"
        }
        
        offer = marketplace_service.create_fix_offer(db_session, offer_data)
        
        assert offer.id is not None
        assert offer.status == "pending"
    
    def test_accept_fix_offer(self, marketplace_service, db_session, test_user):
        """Test accepting fix offer"""
        offer = marketplace_service.create_fix_offer(db_session, {
            "bug_id": 1,
            "developer_id": test_user.id,
            "price": 400.00,
            "delivery_time": 3,
            "description": "Quick fix available"
        })
        
        result = marketplace_service.accept_fix_offer(
            db_session,
            offer.id,
            test_user.id
        )
        
        assert result is True
        db_session.refresh(offer)
        assert offer.status == "accepted"
    
    def test_complete_fix(self, marketplace_service, db_session, test_user):
        """Test completing fix"""
        offer = marketplace_service.create_fix_offer(db_session, {
            "bug_id": 1,
            "developer_id": test_user.id,
            "price": 350.00,
            "delivery_time": 7,
            "description": "Comprehensive fix"
        })
        
        marketplace_service.accept_fix_offer(db_session, offer.id, test_user.id)
        
        result = marketplace_service.complete_fix(
            db_session,
            offer.id,
            solution_code="Fixed code here"
        )
        
        assert result is True
        db_session.refresh(offer)
        assert offer.status == "completed"
