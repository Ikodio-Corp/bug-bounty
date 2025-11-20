"""
Payment Processing Service
Stripe integration for subscriptions and payments
"""

import stripe
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import asyncio


class PaymentProcessor:
    """Stripe payment processor"""
    
    def __init__(self, api_key: str, webhook_secret: str):
        stripe.api_key = api_key
        self.webhook_secret = webhook_secret
        
    async def create_customer(
        self,
        email: str,
        name: str,
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Create Stripe customer"""
        
        try:
            customer = await asyncio.to_thread(
                stripe.Customer.create,
                email=email,
                name=name,
                metadata=metadata or {}
            )
            
            return {
                "customer_id": customer.id,
                "email": customer.email,
                "name": customer.name,
                "created": customer.created
            }
        except stripe.error.StripeError as e:
            return {"error": str(e)}
    
    async def create_subscription(
        self,
        customer_id: str,
        price_id: str,
        trial_days: int = 0
    ) -> Dict[str, Any]:
        """Create subscription"""
        
        try:
            subscription_params = {
                "customer": customer_id,
                "items": [{"price": price_id}]
            }
            
            if trial_days > 0:
                subscription_params["trial_period_days"] = trial_days
            
            subscription = await asyncio.to_thread(
                stripe.Subscription.create,
                **subscription_params
            )
            
            return {
                "subscription_id": subscription.id,
                "status": subscription.status,
                "current_period_end": subscription.current_period_end,
                "trial_end": subscription.trial_end if subscription.trial_end else None
            }
        except stripe.error.StripeError as e:
            return {"error": str(e)}
    
    async def cancel_subscription(
        self,
        subscription_id: str,
        cancel_at_period_end: bool = True
    ) -> Dict[str, Any]:
        """Cancel subscription"""
        
        try:
            if cancel_at_period_end:
                subscription = await asyncio.to_thread(
                    stripe.Subscription.modify,
                    subscription_id,
                    cancel_at_period_end=True
                )
            else:
                subscription = await asyncio.to_thread(
                    stripe.Subscription.cancel,
                    subscription_id
                )
            
            return {
                "subscription_id": subscription.id,
                "status": subscription.status,
                "canceled_at": subscription.canceled_at
            }
        except stripe.error.StripeError as e:
            return {"error": str(e)}
    
    async def create_payment_intent(
        self,
        amount: int,
        currency: str = "usd",
        customer_id: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Create payment intent"""
        
        try:
            params = {
                "amount": amount,
                "currency": currency,
                "metadata": metadata or {}
            }
            
            if customer_id:
                params["customer"] = customer_id
            
            intent = await asyncio.to_thread(
                stripe.PaymentIntent.create,
                **params
            )
            
            return {
                "payment_intent_id": intent.id,
                "client_secret": intent.client_secret,
                "status": intent.status,
                "amount": intent.amount
            }
        except stripe.error.StripeError as e:
            return {"error": str(e)}
    
    async def create_checkout_session(
        self,
        price_id: str,
        success_url: str,
        cancel_url: str,
        customer_email: Optional[str] = None,
        customer_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create checkout session"""
        
        try:
            params = {
                "mode": "subscription",
                "line_items": [{"price": price_id, "quantity": 1}],
                "success_url": success_url,
                "cancel_url": cancel_url
            }
            
            if customer_id:
                params["customer"] = customer_id
            elif customer_email:
                params["customer_email"] = customer_email
            
            session = await asyncio.to_thread(
                stripe.checkout.Session.create,
                **params
            )
            
            return {
                "session_id": session.id,
                "url": session.url
            }
        except stripe.error.StripeError as e:
            return {"error": str(e)}
    
    async def create_billing_portal_session(
        self,
        customer_id: str,
        return_url: str
    ) -> Dict[str, Any]:
        """Create billing portal session"""
        
        try:
            session = await asyncio.to_thread(
                stripe.billing_portal.Session.create,
                customer=customer_id,
                return_url=return_url
            )
            
            return {
                "session_id": session.id,
                "url": session.url
            }
        except stripe.error.StripeError as e:
            return {"error": str(e)}
    
    async def get_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """Get subscription details"""
        
        try:
            subscription = await asyncio.to_thread(
                stripe.Subscription.retrieve,
                subscription_id
            )
            
            return {
                "subscription_id": subscription.id,
                "status": subscription.status,
                "current_period_start": subscription.current_period_start,
                "current_period_end": subscription.current_period_end,
                "cancel_at_period_end": subscription.cancel_at_period_end,
                "plan": {
                    "amount": subscription.plan.amount,
                    "currency": subscription.plan.currency,
                    "interval": subscription.plan.interval
                }
            }
        except stripe.error.StripeError as e:
            return {"error": str(e)}
    
    def verify_webhook_signature(
        self,
        payload: bytes,
        sig_header: str
    ) -> Dict[str, Any]:
        """Verify Stripe webhook signature"""
        
        try:
            event = stripe.Webhook.construct_event(
                payload,
                sig_header,
                self.webhook_secret
            )
            return event
        except ValueError:
            return {"error": "Invalid payload"}
        except stripe.error.SignatureVerificationError:
            return {"error": "Invalid signature"}
    
    async def handle_webhook_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle webhook events"""
        
        event_type = event.get("type")
        data = event.get("data", {}).get("object", {})
        
        result = {
            "event_type": event_type,
            "processed": True,
            "actions": []
        }
        
        if event_type == "customer.subscription.created":
            result["actions"].append("activate_subscription")
            result["subscription_id"] = data.get("id")
        
        elif event_type == "customer.subscription.updated":
            result["actions"].append("update_subscription")
            result["subscription_id"] = data.get("id")
            result["status"] = data.get("status")
        
        elif event_type == "customer.subscription.deleted":
            result["actions"].append("cancel_subscription")
            result["subscription_id"] = data.get("id")
        
        elif event_type == "invoice.payment_succeeded":
            result["actions"].append("record_payment")
            result["invoice_id"] = data.get("id")
            result["amount"] = data.get("amount_paid")
        
        elif event_type == "invoice.payment_failed":
            result["actions"].append("handle_failed_payment")
            result["invoice_id"] = data.get("id")
        
        return result


class SubscriptionManager:
    """Manage subscription tiers and features"""
    
    TIERS = {
        "free": {
            "name": "Free",
            "price": 0,
            "features": {
                "scans_per_month": 10,
                "ai_scans": False,
                "team_members": 1,
                "priority_support": False,
                "api_access": False
            }
        },
        "bronze": {
            "name": "Bronze",
            "price": 1550000,
            "features": {
                "scans_per_month": 100,
                "ai_scans": True,
                "team_members": 3,
                "priority_support": False,
                "api_access": True
            }
        },
        "silver": {
            "name": "Silver",
            "price": 7830000,
            "features": {
                "scans_per_month": 500,
                "ai_scans": True,
                "team_members": 10,
                "priority_support": True,
                "api_access": True
            }
        },
        "gold": {
            "name": "Gold",
            "price": 47080000,
            "features": {
                "scans_per_month": -1,
                "ai_scans": True,
                "team_members": -1,
                "priority_support": True,
                "api_access": True,
                "dedicated_support": True,
                "custom_integration": True
            }
        }
    }
    
    def get_tier_features(self, tier: str) -> Dict[str, Any]:
        """Get features for subscription tier"""
        return self.TIERS.get(tier, self.TIERS["free"])
    
    def can_use_feature(
        self,
        tier: str,
        feature: str,
        current_usage: int = 0
    ) -> bool:
        """Check if tier can use feature"""
        
        tier_data = self.TIERS.get(tier, self.TIERS["free"])
        features = tier_data["features"]
        
        if feature not in features:
            return False
        
        feature_value = features[feature]
        
        if isinstance(feature_value, bool):
            return feature_value
        
        if isinstance(feature_value, int):
            if feature_value == -1:
                return True
            return current_usage < feature_value
        
        return False
    
    def calculate_upgrade_cost(
        self,
        from_tier: str,
        to_tier: str,
        days_remaining: int
    ) -> int:
        """Calculate prorated upgrade cost"""
        
        from_price = self.TIERS.get(from_tier, {}).get("price", 0)
        to_price = self.TIERS.get(to_tier, {}).get("price", 0)
        
        price_diff = to_price - from_price
        
        if days_remaining > 0:
            daily_rate = price_diff / 30
            prorated_cost = int(daily_rate * days_remaining)
            return max(prorated_cost, 0)
        
        return price_diff
