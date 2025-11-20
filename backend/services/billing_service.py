"""
Billing Service - Enhanced Payment Processing and Billing

This module provides comprehensive billing management including:
- Payout management for researchers
- Invoicing for organizations
- Multi-currency support
- Tax handling
- Financial reporting
"""

import logging
from typing import Any, Dict, List, Optional
from enum import Enum
from datetime import datetime, timedelta
from decimal import Decimal

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class PaymentMethod(str, Enum):
    """Payment methods."""
    STRIPE = "stripe"
    PAYPAL = "paypal"
    BANK_TRANSFER = "bank_transfer"
    CRYPTO = "crypto"


class PayoutStatus(str, Enum):
    """Payout status."""
    PENDING = "pending"
    APPROVED = "approved"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    ON_HOLD = "on_hold"


class Currency(str, Enum):
    """Supported currencies."""
    USD = "usd"
    EUR = "eur"
    GBP = "gbp"
    BTC = "btc"
    ETH = "eth"
    USDC = "usdc"


class Payout(BaseModel):
    """Payout record."""
    id: str
    user_id: str
    bug_id: str
    amount: Decimal
    currency: Currency
    status: PayoutStatus
    method: PaymentMethod
    tax_withheld: Decimal = Decimal("0")
    net_amount: Decimal
    payout_details: Dict[str, Any] = {}
    approved_by: Optional[str] = None
    created_at: datetime = datetime.utcnow()
    approved_at: Optional[datetime] = None
    processed_at: Optional[datetime] = None


class Invoice(BaseModel):
    """Invoice record."""
    id: str
    organization_id: str
    amount: Decimal
    currency: Currency
    status: str
    line_items: List[Dict[str, Any]]
    tax_amount: Decimal = Decimal("0")
    total_amount: Decimal
    due_date: datetime
    paid_at: Optional[datetime] = None
    created_at: datetime = datetime.utcnow()


class BillingService:
    """
    Billing Service for bug bounty platform.

    Provides:
    - Researcher payout management
    - Organization invoicing
    - Tax calculation
    - Multi-currency support
    - Financial reporting
    """

    def __init__(self):
        """Initialize billing service."""
        self._payouts: Dict[str, Payout] = {}
        self._invoices: Dict[str, Invoice] = {}
        self._balances: Dict[str, Decimal] = {}

        # Tax rates by country
        self._tax_rates = {
            "US": Decimal("0"),
            "default": Decimal("0.30")
        }

    async def create_payout(
        self,
        user_id: str,
        bug_id: str,
        amount: Decimal,
        currency: Currency,
        method: PaymentMethod,
        payout_details: Dict[str, Any],
        country_code: str = "default"
    ) -> Payout:
        """Create a payout request."""
        import uuid

        # Calculate tax withholding
        tax_rate = self._tax_rates.get(country_code, self._tax_rates["default"])
        tax_withheld = amount * tax_rate
        net_amount = amount - tax_withheld

        payout = Payout(
            id=str(uuid.uuid4()),
            user_id=user_id,
            bug_id=bug_id,
            amount=amount,
            currency=currency,
            status=PayoutStatus.PENDING,
            method=method,
            tax_withheld=tax_withheld,
            net_amount=net_amount,
            payout_details=payout_details
        )

        self._payouts[payout.id] = payout

        # Update user balance
        if user_id not in self._balances:
            self._balances[user_id] = Decimal("0")
        self._balances[user_id] += net_amount

        logger.info(f"Created payout {payout.id}: {amount} {currency.value}")

        return payout

    async def approve_payout(self, payout_id: str, approved_by: str) -> Payout:
        """Approve a payout request."""
        if payout_id not in self._payouts:
            raise ValueError(f"Payout {payout_id} not found")

        payout = self._payouts[payout_id]
        payout.status = PayoutStatus.APPROVED
        payout.approved_by = approved_by
        payout.approved_at = datetime.utcnow()

        return payout

    async def process_payout(self, payout_id: str) -> Payout:
        """Process an approved payout."""
        if payout_id not in self._payouts:
            raise ValueError(f"Payout {payout_id} not found")

        payout = self._payouts[payout_id]

        if payout.status != PayoutStatus.APPROVED:
            raise ValueError(f"Cannot process payout in {payout.status.value} status")

        payout.status = PayoutStatus.PROCESSING

        try:
            # Process payment (integrate with payment processor)
            payout.status = PayoutStatus.COMPLETED
            payout.processed_at = datetime.utcnow()

            # Deduct from balance
            self._balances[payout.user_id] -= payout.net_amount

        except Exception as e:
            payout.status = PayoutStatus.FAILED
            raise

        return payout

    async def create_invoice(
        self,
        organization_id: str,
        line_items: List[Dict[str, Any]],
        currency: Currency,
        due_days: int = 30,
        tax_rate: Decimal = Decimal("0")
    ) -> Invoice:
        """Create an invoice."""
        import uuid

        subtotal = sum(Decimal(str(item.get("amount", 0))) for item in line_items)
        tax_amount = subtotal * tax_rate
        total_amount = subtotal + tax_amount

        invoice = Invoice(
            id=str(uuid.uuid4()),
            organization_id=organization_id,
            amount=subtotal,
            currency=currency,
            status="draft",
            line_items=line_items,
            tax_amount=tax_amount,
            total_amount=total_amount,
            due_date=datetime.utcnow() + timedelta(days=due_days)
        )

        self._invoices[invoice.id] = invoice
        return invoice

    def get_user_balance(self, user_id: str) -> Decimal:
        """Get user's available balance."""
        return self._balances.get(user_id, Decimal("0"))

    def get_user_payouts(self, user_id: str) -> List[Payout]:
        """Get user's payouts."""
        return [p for p in self._payouts.values() if p.user_id == user_id]

    def get_financial_summary(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get financial summary report."""
        payouts = list(self._payouts.values())

        if start_date:
            payouts = [p for p in payouts if p.created_at >= start_date]
        if end_date:
            payouts = [p for p in payouts if p.created_at <= end_date]

        total_payouts = sum(
            p.amount for p in payouts
            if p.status == PayoutStatus.COMPLETED
        )

        total_tax = sum(
            p.tax_withheld for p in payouts
            if p.status == PayoutStatus.COMPLETED
        )

        pending = sum(
            p.amount for p in payouts
            if p.status in [PayoutStatus.PENDING, PayoutStatus.APPROVED]
        )

        return {
            "total_payouts": float(total_payouts),
            "total_tax_withheld": float(total_tax),
            "pending_payouts": float(pending),
            "payout_count": len([p for p in payouts if p.status == PayoutStatus.COMPLETED])
        }


# Singleton instance
_billing_service: Optional[BillingService] = None


def get_billing_service() -> BillingService:
    """Get the global billing service instance."""
    global _billing_service
    if _billing_service is None:
        _billing_service = BillingService()
    return _billing_service


__all__ = [
    "BillingService",
    "PaymentMethod",
    "PayoutStatus",
    "Currency",
    "Payout",
    "Invoice",
    "get_billing_service"
]
