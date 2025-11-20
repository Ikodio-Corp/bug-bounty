"""
Billing API Routes - Payment and Payout Management Endpoints

This module provides REST API endpoints for billing operations
including payouts, invoices, and financial reporting.
"""

import logging
from typing import Any, Dict, List, Optional
from decimal import Decimal
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from ...services.billing_service import (
    get_billing_service,
    BillingService,
    PaymentMethod,
    Currency
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/billing", tags=["Billing"])


# Request Models
class CreatePayoutRequest(BaseModel):
    """Request to create payout."""
    user_id: str = Field(..., description="User ID")
    bug_id: str = Field(..., description="Bug ID")
    amount: float = Field(..., description="Payout amount")
    currency: str = Field(default="usd", description="Currency")
    method: str = Field(..., description="Payment method")
    payout_details: Dict[str, Any] = Field(..., description="Payment details")
    country_code: str = Field(default="default", description="Country code for tax")


class ApprovePayoutRequest(BaseModel):
    """Request to approve payout."""
    approved_by: str = Field(..., description="Approver user ID")


class CreateInvoiceRequest(BaseModel):
    """Request to create invoice."""
    organization_id: str = Field(..., description="Organization ID")
    line_items: List[Dict[str, Any]] = Field(..., description="Line items")
    currency: str = Field(default="usd", description="Currency")
    due_days: int = Field(default=30, description="Days until due")
    tax_rate: float = Field(default=0, description="Tax rate")


# Dependency
async def get_service() -> BillingService:
    """Get billing service."""
    return get_billing_service()


# Payout Endpoints
@router.post("/payouts", response_model=Dict[str, Any])
async def create_payout(
    request: CreatePayoutRequest,
    service: BillingService = Depends(get_service)
):
    """
    Create a payout request.

    Calculates tax withholding based on country code.
    """
    try:
        payout = await service.create_payout(
            user_id=request.user_id,
            bug_id=request.bug_id,
            amount=Decimal(str(request.amount)),
            currency=Currency(request.currency),
            method=PaymentMethod(request.method),
            payout_details=request.payout_details,
            country_code=request.country_code
        )

        return {
            "success": True,
            "payout_id": payout.id,
            "amount": float(payout.amount),
            "tax_withheld": float(payout.tax_withheld),
            "net_amount": float(payout.net_amount),
            "status": payout.status.value
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Create payout failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/payouts/{payout_id}/approve", response_model=Dict[str, Any])
async def approve_payout(
    payout_id: str,
    request: ApprovePayoutRequest,
    service: BillingService = Depends(get_service)
):
    """Approve a payout request."""
    try:
        payout = await service.approve_payout(payout_id, request.approved_by)

        return {
            "success": True,
            "payout_id": payout.id,
            "status": payout.status.value,
            "approved_by": payout.approved_by,
            "approved_at": payout.approved_at.isoformat()
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Approve payout failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/payouts/{payout_id}/process", response_model=Dict[str, Any])
async def process_payout(
    payout_id: str,
    service: BillingService = Depends(get_service)
):
    """Process an approved payout."""
    try:
        payout = await service.process_payout(payout_id)

        return {
            "success": True,
            "payout_id": payout.id,
            "status": payout.status.value,
            "processed_at": payout.processed_at.isoformat() if payout.processed_at else None
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Process payout failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/payouts/user/{user_id}", response_model=Dict[str, Any])
async def get_user_payouts(
    user_id: str,
    service: BillingService = Depends(get_service)
):
    """Get payouts for a user."""
    try:
        payouts = service.get_user_payouts(user_id)

        return {
            "success": True,
            "user_id": user_id,
            "count": len(payouts),
            "payouts": [
                {
                    "id": p.id,
                    "bug_id": p.bug_id,
                    "amount": float(p.amount),
                    "net_amount": float(p.net_amount),
                    "currency": p.currency.value,
                    "status": p.status.value,
                    "method": p.method.value,
                    "created_at": p.created_at.isoformat()
                }
                for p in payouts
            ]
        }

    except Exception as e:
        logger.error(f"Get user payouts failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/balance/{user_id}", response_model=Dict[str, Any])
async def get_user_balance(
    user_id: str,
    service: BillingService = Depends(get_service)
):
    """Get user's available balance."""
    try:
        balance = service.get_user_balance(user_id)

        return {
            "success": True,
            "user_id": user_id,
            "balance": float(balance),
            "currency": "usd"
        }

    except Exception as e:
        logger.error(f"Get balance failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Invoice Endpoints
@router.post("/invoices", response_model=Dict[str, Any])
async def create_invoice(
    request: CreateInvoiceRequest,
    service: BillingService = Depends(get_service)
):
    """Create an invoice."""
    try:
        invoice = await service.create_invoice(
            organization_id=request.organization_id,
            line_items=request.line_items,
            currency=Currency(request.currency),
            due_days=request.due_days,
            tax_rate=Decimal(str(request.tax_rate))
        )

        return {
            "success": True,
            "invoice_id": invoice.id,
            "amount": float(invoice.amount),
            "tax_amount": float(invoice.tax_amount),
            "total_amount": float(invoice.total_amount),
            "due_date": invoice.due_date.isoformat(),
            "status": invoice.status
        }

    except Exception as e:
        logger.error(f"Create invoice failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Reporting Endpoints
@router.get("/summary", response_model=Dict[str, Any])
async def get_financial_summary(
    start_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format)"),
    service: BillingService = Depends(get_service)
):
    """Get financial summary report."""
    try:
        start = datetime.fromisoformat(start_date) if start_date else None
        end = datetime.fromisoformat(end_date) if end_date else None

        summary = service.get_financial_summary(start, end)

        return {
            "success": True,
            **summary
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Get financial summary failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Reference Data Endpoints
@router.get("/payment-methods", response_model=Dict[str, Any])
async def get_payment_methods():
    """Get supported payment methods."""
    return {
        "success": True,
        "methods": [
            {"id": "stripe", "name": "Stripe", "type": "card"},
            {"id": "paypal", "name": "PayPal", "type": "wallet"},
            {"id": "bank_transfer", "name": "Bank Transfer", "type": "bank"},
            {"id": "crypto", "name": "Cryptocurrency", "type": "crypto"}
        ]
    }


@router.get("/currencies", response_model=Dict[str, Any])
async def get_currencies():
    """Get supported currencies."""
    return {
        "success": True,
        "currencies": [
            {"id": "usd", "name": "US Dollar", "symbol": "$"},
            {"id": "eur", "name": "Euro", "symbol": "EUR"},
            {"id": "gbp", "name": "British Pound", "symbol": "GBP"},
            {"id": "btc", "name": "Bitcoin", "symbol": "BTC"},
            {"id": "eth", "name": "Ethereum", "symbol": "ETH"},
            {"id": "usdc", "name": "USD Coin", "symbol": "USDC"}
        ]
    }


@router.get("/health", response_model=Dict[str, Any])
async def health_check():
    """Billing service health check."""
    return {
        "status": "healthy",
        "service": "billing",
        "version": "1.0.0"
    }
