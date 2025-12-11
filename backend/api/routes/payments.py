"""
Payment API Routes - Midtrans Integration
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from datetime import datetime
import json

from core.database import get_async_db
from core.security import Security
from models.user import User, SubscriptionTier
from integrations.midtrans_client import midtrans_client

router = APIRouter()
security = Security()


class PaymentRequest(BaseModel):
    tier: str
    billing_cycle: str = "monthly"
    

class PaymentResponse(BaseModel):
    payment_url: str
    invoice_number: str
    amount: float
    status: str


# Pricing in IDR
PRICING = {
    "professional": {
        "monthly": 299000,
        "yearly": 2990000
    },
    "business": {
        "monthly": 999000,
        "yearly": 9990000
    },
    "enterprise": {
        "monthly": 4990000,
        "yearly": 49900000
    },
    "government": {
        "monthly": 9990000,
        "yearly": 99900000
    }
}


@router.post("/create", response_model=PaymentResponse)
async def create_payment(
    payment_request: PaymentRequest,
    request: Request,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(security.get_current_user)
):
    """Create payment for subscription upgrade using Midtrans"""
    if payment_request.tier not in PRICING:
        raise HTTPException(status_code=400, detail=f"Invalid tier")
    
    amount = PRICING[payment_request.tier][payment_request.billing_cycle]
    order_id = f"ORDER-{current_user.id}-{int(datetime.utcnow().timestamp())}"
    
    # Map tier to item name
    tier_names = {
        "free": "IKODIO Free Plan",
        "professional": "IKODIO Professional Plan",
        "business": "IKODIO Business Plan",
        "enterprise": "IKODIO Enterprise Plan"
    }
    
    item_name = f"{tier_names.get(payment_request.tier, 'IKODIO')} - {payment_request.billing_cycle.title()}"
    
    result = midtrans_client.create_payment(
        order_id=order_id,
        amount=amount,
        customer_name=current_user.full_name or current_user.username,
        customer_email=current_user.email,
        item_name=item_name,
        item_quantity=1
    )
    
    if "error" in result:
        raise HTTPException(status_code=500, detail=f"Payment creation failed: {result['error']}")
    
    return PaymentResponse(
        payment_url=result.get("redirect_url", ""),
        invoice_number=order_id,
        amount=amount,
        status="pending"
    )


@router.get("/status/{order_id}")
async def get_payment_status(
    order_id: str,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(security.get_current_user)
):
    """Check payment status from Midtrans"""
    result = midtrans_client.check_transaction_status(order_id)
    if "error" in result:
        raise HTTPException(status_code=500, detail=f"Failed to check status")
    return result


@router.post("/midtrans/notification")
async def midtrans_notification(request: Request, db: AsyncSession = Depends(get_async_db)):
    """Webhook notification from Midtrans"""
    try:
        data = await request.json()
        
        # Extract transaction details
        order_id = data.get("order_id")
        transaction_status = data.get("transaction_status")
        fraud_status = data.get("fraud_status")
        signature_key = data.get("signature_key")
        
        # Verify signature
        status_code = data.get("status_code")
        gross_amount = data.get("gross_amount")
        
        if not midtrans_client.verify_signature(order_id, status_code, gross_amount, signature_key):
            raise HTTPException(status_code=401, detail="Invalid signature")
        
        # Extract user ID from order_id (ORDER-{user_id}-{timestamp})
        try:
            user_id = int(order_id.split('-')[1])
        except (IndexError, ValueError):
            raise HTTPException(status_code=400, detail="Invalid order format")
        
        # Get user from database
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Update subscription based on transaction status
        if transaction_status == "capture" or transaction_status == "settlement":
            if fraud_status == "accept" or fraud_status is None:
                # Payment successful - upgrade subscription
                amount = int(gross_amount)
                tier_map = {
                    299000: SubscriptionTier.PROFESSIONAL, 
                    2990000: SubscriptionTier.PROFESSIONAL,
                    799000: SubscriptionTier.BUSINESS, 
                    7990000: SubscriptionTier.BUSINESS,
                    1999000: SubscriptionTier.ENTERPRISE, 
                    19990000: SubscriptionTier.ENTERPRISE,
                }
                
                new_tier = tier_map.get(amount)
                if new_tier:
                    user.subscription_tier = new_tier
                    user.is_premium = True
                    await db.commit()
                    
                    return {"status": "success", "message": "Subscription upgraded"}
        
        elif transaction_status == "cancel" or transaction_status == "deny" or transaction_status == "expire":
            # Payment failed/cancelled
            return {"status": "failed", "message": "Payment not successful"}
        
        elif transaction_status == "pending":
            # Payment pending
            return {"status": "pending", "message": "Payment pending"}
        
        return {"status": "received"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pricing")
async def get_pricing():
    """Get pricing information"""
    return {
        "currency": "IDR",
        "tiers": {
            "professional": {
                "name": "Professional",
                "monthly": {
                    "price": 299000,
                    "price_formatted": "Rp 299.000",
                    "features": ["50 scans/month", "20 auto-fixes", "5,000 API calls", "10GB storage"]
                },
                "yearly": {
                    "price": 2990000,
                    "price_formatted": "Rp 2.990.000",
                    "save": 598000,
                    "features": ["50 scans/month", "20 auto-fixes", "5,000 API calls", "10GB storage", "Save 2 months"]
                }
            },
            "business": {
                "name": "Business",
                "monthly": {
                    "price": 999000,
                    "price_formatted": "Rp 999.000",
                    "features": ["200 scans/month", "Unlimited auto-fixes", "25,000 API calls", "50GB storage"]
                },
                "yearly": {
                    "price": 9990000,
                    "price_formatted": "Rp 9.990.000",
                    "save": 1998000,
                    "features": ["200 scans/month", "Unlimited auto-fixes", "25,000 API calls", "50GB storage", "Save 2 months"]
                }
            },
            "enterprise": {
                "name": "Enterprise",
                "monthly": {
                    "price": 4990000,
                    "price_formatted": "Rp 4.990.000",
                    "features": ["Unlimited scans", "Unlimited auto-fixes", "Unlimited API", "500GB storage"]
                },
                "yearly": {
                    "price": 49900000,
                    "price_formatted": "Rp 49.900.000",
                    "save": 9980000,
                    "features": ["Unlimited scans", "Unlimited auto-fixes", "Unlimited API", "500GB storage", "Save 2 months"]
                }
            },
            "government": {
                "name": "Government",
                "monthly": {
                    "price": 9990000,
                    "price_formatted": "Rp 9.990.000",
                    "features": ["Unlimited everything", "1000GB storage", "On-premise", "Compliance"]
                },
                "yearly": {
                    "price": 99900000,
                    "price_formatted": "Rp 99.900.000",
                    "save": 19980000,
                    "features": ["Unlimited everything", "1000GB storage", "On-premise", "Compliance", "Save 2 months"]
                }
            }
        }
    }


@router.post("/doku/token")
async def doku_token_endpoint(request: Request):
    """
    Endpoint untuk menerima access token dari Doku
    URL ini harus diisi di dashboard Doku sebagai Token URL
    """
    try:
        body = await request.json()
        
        # Log token yang diterima
        print(f"Received token from Doku: {body}")
        
        # Simpan token jika diperlukan (optional)
        # Biasanya token ini digunakan untuk komunikasi B2B dengan Doku
        
        return {
            "status": "success",
            "message": "Token received"
        }
    except Exception as e:
        print(f"Error receiving Doku token: {e}")
        return {
            "status": "error",
            "message": str(e)
        }
