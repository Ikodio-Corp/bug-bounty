"""
Stripe Payment Integration
"""

import stripe
from typing import Dict, Any, Optional
from datetime import datetime

from core.config import settings


stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeClient:
    """Stripe payment processing client"""
    
    def __init__(self):
        self.webhook_secret = settings.STRIPE_WEBHOOK_SECRET
    
    async def create_payment_intent(
        self,
        amount: int,
        currency: str = "usd",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a payment intent"""
        
        try:
            intent = stripe.PaymentIntent.create(
                amount=amount,
                currency=currency,
                metadata=metadata or {},
                automatic_payment_methods={"enabled": True}
            )
            
            return {
                "client_secret": intent.client_secret,
                "payment_intent_id": intent.id,
                "status": intent.status
            }
        
        except stripe.error.StripeError as e:
            return {
                "error": str(e),
                "type": "stripe_error"
            }
    
    async def create_customer(
        self,
        email: str,
        name: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a Stripe customer"""
        
        try:
            customer = stripe.Customer.create(
                email=email,
                name=name,
                metadata=metadata or {}
            )
            
            return {
                "customer_id": customer.id,
                "email": customer.email
            }
        
        except stripe.error.StripeError as e:
            return {
                "error": str(e),
                "type": "stripe_error"
            }
    
    async def create_subscription(
        self,
        customer_id: str,
        price_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a subscription"""
        
        try:
            subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[{"price": price_id}],
                metadata=metadata or {},
                expand=["latest_invoice.payment_intent"]
            )
            
            return {
                "subscription_id": subscription.id,
                "status": subscription.status,
                "current_period_end": subscription.current_period_end
            }
        
        except stripe.error.StripeError as e:
            return {
                "error": str(e),
                "type": "stripe_error"
            }
    
    async def cancel_subscription(
        self,
        subscription_id: str
    ) -> Dict[str, Any]:
        """Cancel a subscription"""
        
        try:
            subscription = stripe.Subscription.delete(subscription_id)
            
            return {
                "subscription_id": subscription.id,
                "status": subscription.status,
                "canceled_at": subscription.canceled_at
            }
        
        except stripe.error.StripeError as e:
            return {
                "error": str(e),
                "type": "stripe_error"
            }
    
    async def create_payout(
        self,
        amount: int,
        destination: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a payout to connected account"""
        
        try:
            payout = stripe.Payout.create(
                amount=amount,
                currency="usd",
                destination=destination,
                metadata=metadata or {}
            )
            
            return {
                "payout_id": payout.id,
                "status": payout.status,
                "arrival_date": payout.arrival_date
            }
        
        except stripe.error.StripeError as e:
            return {
                "error": str(e),
                "type": "stripe_error"
            }
    
    async def retrieve_payment_intent(
        self,
        payment_intent_id: str
    ) -> Dict[str, Any]:
        """Retrieve payment intent details"""
        
        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            return {
                "payment_intent_id": intent.id,
                "status": intent.status,
                "amount": intent.amount,
                "currency": intent.currency,
                "metadata": intent.metadata
            }
        
        except stripe.error.StripeError as e:
            return {
                "error": str(e),
                "type": "stripe_error"
            }
    
    def verify_webhook_signature(
        self,
        payload: bytes,
        signature: str
    ) -> Optional[Dict[str, Any]]:
        """Verify webhook signature and parse event"""
        
        try:
            event = stripe.Webhook.construct_event(
                payload,
                signature,
                self.webhook_secret
            )
            
            return {
                "event_id": event.id,
                "event_type": event.type,
                "data": event.data.object
            }
        
        except stripe.error.SignatureVerificationError as e:
            return None
        except Exception as e:
            return None
    
    async def handle_webhook_event(
        self,
        event: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle Stripe webhook events"""
        
        event_type = event.get("event_type")
        data = event.get("data", {})
        
        handlers = {
            "payment_intent.succeeded": self._handle_payment_succeeded,
            "payment_intent.payment_failed": self._handle_payment_failed,
            "customer.subscription.created": self._handle_subscription_created,
            "customer.subscription.updated": self._handle_subscription_updated,
            "customer.subscription.deleted": self._handle_subscription_deleted,
            "invoice.payment_succeeded": self._handle_invoice_paid,
            "invoice.payment_failed": self._handle_invoice_failed
        }
        
        handler = handlers.get(event_type)
        
        if handler:
            return await handler(data)
        
        return {"status": "unhandled", "event_type": event_type}
    
    async def _handle_payment_succeeded(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle successful payment"""
        return {
            "status": "success",
            "payment_intent_id": data.get("id"),
            "amount": data.get("amount")
        }
    
    async def _handle_payment_failed(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle failed payment"""
        return {
            "status": "failed",
            "payment_intent_id": data.get("id"),
            "error": data.get("last_payment_error")
        }
    
    async def _handle_subscription_created(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle subscription creation"""
        return {
            "status": "created",
            "subscription_id": data.get("id"),
            "customer_id": data.get("customer")
        }
    
    async def _handle_subscription_updated(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle subscription update"""
        return {
            "status": "updated",
            "subscription_id": data.get("id"),
            "new_status": data.get("status")
        }
    
    async def _handle_subscription_deleted(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle subscription deletion"""
        return {
            "status": "deleted",
            "subscription_id": data.get("id"),
            "canceled_at": data.get("canceled_at")
        }
    
    async def _handle_invoice_paid(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle paid invoice"""
        return {
            "status": "paid",
            "invoice_id": data.get("id"),
            "amount_paid": data.get("amount_paid")
        }
    
    async def _handle_invoice_failed(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle failed invoice"""
        return {
            "status": "failed",
            "invoice_id": data.get("id"),
            "attempt_count": data.get("attempt_count")
        }
