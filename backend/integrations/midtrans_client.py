"""
Midtrans Payment Gateway Integration
"""

import base64
import hashlib
import json
import time
from typing import Dict, Optional
import requests
from core.config import settings


class MidtransClient:
    """Midtrans payment gateway client"""
    
    def __init__(self):
        # Midtrans Sandbox credentials
        # Get from: https://dashboard.sandbox.midtrans.com/settings/config_info
        self.server_key = settings.MIDTRANS_SERVER_KEY if hasattr(settings, 'MIDTRANS_SERVER_KEY') else "SB-Mid-server-PLACEHOLDER"
        self.client_key = settings.MIDTRANS_CLIENT_KEY if hasattr(settings, 'MIDTRANS_CLIENT_KEY') else "SB-Mid-client-PLACEHOLDER"
        
        # Sandbox URLs
        self.api_url = "https://app.sandbox.midtrans.com/snap/v1/transactions"
        self.snap_url = "https://app.sandbox.midtrans.com/snap/snap.js"
        
        # Production URLs (uncomment for production)
        # self.api_url = "https://app.midtrans.com/snap/v1/transactions"
        # self.snap_url = "https://app.midtrans.com/snap/snap.js"
    
    def _get_headers(self) -> Dict[str, str]:
        """Generate headers for Midtrans API request"""
        # Encode server key to base64 for authorization
        auth_string = f"{self.server_key}:"
        auth_bytes = auth_string.encode('ascii')
        base64_bytes = base64.b64encode(auth_bytes)
        base64_auth = base64_bytes.decode('ascii')
        
        return {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Basic {base64_auth}"
        }
    
    def create_payment(
        self,
        order_id: str,
        amount: float,
        customer_name: str,
        customer_email: str,
        customer_phone: str = None,
        item_name: str = "Subscription",
        item_quantity: int = 1
    ) -> Dict:
        """
        Create payment transaction using Snap
        
        Args:
            order_id: Unique order ID
            amount: Payment amount in IDR (gross_amount)
            customer_name: Customer full name
            customer_email: Customer email
            customer_phone: Customer phone (optional)
            item_name: Item description
            item_quantity: Item quantity
            
        Returns:
            Dict with token and redirect_url
        """
        
        # Build transaction payload
        payload = {
            "transaction_details": {
                "order_id": order_id,
                "gross_amount": int(amount)
            },
            "customer_details": {
                "first_name": customer_name,
                "email": customer_email
            },
            "item_details": [
                {
                    "id": "item-1",
                    "price": int(amount),
                    "quantity": item_quantity,
                    "name": item_name
                }
            ],
            "enabled_payments": [
                "credit_card",
                "gopay",
                "shopeepay",
                "other_qris",
                "bca_va",
                "bni_va",
                "bri_va",
                "permata_va",
                "other_va"
            ]
        }
        
        # Add phone if provided
        if customer_phone:
            payload["customer_details"]["phone"] = customer_phone
        
        headers = self._get_headers()
        
        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 201:
                data = response.json()
                return {
                    "token": data.get("token"),
                    "redirect_url": data.get("redirect_url"),
                    "order_id": order_id,
                    "status": "pending"
                }
            else:
                return {
                    "error": f"Midtrans API error: {response.status_code}",
                    "message": response.text,
                    "status": "failed"
                }
                
        except requests.exceptions.RequestException as e:
            return {
                "error": str(e),
                "status": "failed"
            }
    
    def check_transaction_status(self, order_id: str) -> Dict:
        """
        Check transaction status
        
        Args:
            order_id: Order ID to check
            
        Returns:
            Dict with transaction status
        """
        url = f"https://api.sandbox.midtrans.com/v2/{order_id}/status"
        headers = self._get_headers()
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "error": f"Failed to check status: {response.status_code}",
                    "message": response.text
                }
                
        except requests.exceptions.RequestException as e:
            return {
                "error": str(e)
            }
    
    def verify_signature(self, order_id: str, status_code: str, gross_amount: str, signature_key: str) -> bool:
        """
        Verify notification signature from Midtrans
        
        Args:
            order_id: Order ID
            status_code: Transaction status code
            gross_amount: Gross amount
            signature_key: Signature from Midtrans
            
        Returns:
            True if signature is valid
        """
        # Create signature string
        signature_string = f"{order_id}{status_code}{gross_amount}{self.server_key}"
        
        # Calculate SHA512 hash
        calculated_signature = hashlib.sha512(signature_string.encode('utf-8')).hexdigest()
        
        return calculated_signature == signature_key


# Create singleton instance
midtrans_client = MidtransClient()
