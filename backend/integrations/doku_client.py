"""
Doku Payment Gateway Integration
"""

import base64
import hashlib
import hmac
import json
import time
from datetime import datetime
from typing import Dict, Optional
import requests
from core.config import settings


class DokuClient:
    """Doku payment gateway client"""
    
    def __init__(self):
        self.client_id = "BRN-0209-1764040821452"
        self.secret_key = "SK-gL0YlQGAWmlXM3gACacn"
        self.base_url = "https://api-sandbox.doku.com"  # Production: https://api.doku.com
        self.token_url = "https://api-sandbox.doku.com/authorization/v1/access-token/b2b"
        
        # Doku's public key (dari dashboard - untuk verifikasi signature dari Doku)
        self.doku_public_key = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA0ECAQHDOCACn8AMIIBCgKCAgEAkgn6IL6LuVQJr5v3uPj93y6scpvqQKoQejeXD4vJ2izYUq3iBSfXsjjIhOZtNAlluLUda13OPbMtHeS8FMWdvwJ5TRbC2P98zTUVYYUdK1fd83fYbKDcupeWaPw/P0nRV+aY0EU6yTE8g0pZfnDvzgT0VcsOFB15qzlWtNUv9po1J3oI+0SBy0PpJiIv71ollozu865C+scY8iqg6OU00OVuqSKAPiL2C6xfLNHqw9uDxyDL6I2PwLSuwIDAQAB
-----END PUBLIC KEY-----"""
        
        # IMPORTANT: Merchant Private Key belum di-set di dashboard Doku
        # Harus generate dulu dan upload ke "Edit Merchant Public Key"
        # Untuk sekarang, gunakan dummy key (akan error sampai di-set dengan benar)
        self.merchant_private_key = None  # Will be set when needed
    
    def _generate_signature(self, method: str, path: str, request_id: str, timestamp: str, body: str = "") -> str:
        """Generate HMAC SHA256 signature for Doku API"""
        # Calculate SHA-256 hash of body and encode to base64
        body_hash = hashlib.sha256(body.encode('utf-8')).digest()
        digest_base64 = base64.b64encode(body_hash).decode('utf-8')
        
        # Build component string according to Doku spec
        component = f"Client-Id:{self.client_id}\n"
        component += f"Request-Id:{request_id}\n"
        component += f"Request-Timestamp:{timestamp}\n"
        component += f"Request-Target:{method} {path}\n"
        component += f"Digest:SHA-256={digest_base64}"
        
        # Generate HMAC-SHA256 signature and encode to base64
        signature_bytes = hmac.new(
            self.secret_key.encode('utf-8'),
            component.encode('utf-8'),
            hashlib.sha256
        ).digest()
        
        signature_base64 = base64.b64encode(signature_bytes).decode('utf-8')
        
        return signature_base64
    
    def _get_headers(self, method: str, path: str, body: Dict = None) -> Dict[str, str]:
        """Generate headers for Doku API request"""
        timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        request_id = f"REQ-{int(time.time() * 1000)}"
        body_str = json.dumps(body) if body else ""
        
        signature = self._generate_signature(method, path, request_id, timestamp, body_str)
        
        return {
            "Client-Id": self.client_id,
            "Request-Id": request_id,
            "Request-Timestamp": timestamp,
            "Signature": f"HMACSHA256={signature}",
            "Content-Type": "application/json"
        }
    
    def create_payment(
        self,
        invoice_number: str,
        amount: float,
        customer_name: str,
        customer_email: str,
        tier: str,
        success_url: str,
        failed_url: str
    ) -> Dict:
        """
        Create payment request
        
        Args:
            invoice_number: Unique invoice number
            amount: Payment amount in IDR
            customer_name: Customer full name
            customer_email: Customer email
            tier: Subscription tier (professional, business, enterprise, government)
            success_url: URL to redirect on success
            failed_url: URL to redirect on failure
            
        Returns:
            Dict with payment_url and invoice details
        """
        path = "/checkout/v1/payment"
        
        # Map tier to description
        tier_names = {
            "professional": "IKODIO Professional Plan",
            "business": "IKODIO Business Plan",
            "enterprise": "IKODIO Enterprise Plan",
            "government": "IKODIO Government Plan"
        }
        
        payload = {
            "order": {
                "invoice_number": invoice_number,
                "amount": int(amount),
                "currency": "IDR"
            },
            "payment": {
                "payment_due_date": int(time.time()) + (24 * 60 * 60)  # 24 hours
            },
            "customer": {
                "name": customer_name,
                "email": customer_email
            },
            "item_details": [
                {
                    "name": tier_names.get(tier, f"IKODIO {tier.title()} Plan"),
                    "quantity": 1,
                    "price": int(amount)
                }
            ],
            "callback": {
                "success_redirect_url": success_url,
                "failed_redirect_url": failed_url,
                "notification_url": f"{settings.API_URL}/api/payments/doku/callback"
            }
        }
        
        headers = self._get_headers("POST", path, payload)
        
        # Debug logging
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Doku Request URL: {self.base_url}{path}")
        logger.info(f"Doku Headers: {headers}")
        logger.info(f"Doku Payload: {json.dumps(payload, indent=2)}")
        
        try:
            response = requests.post(
                f"{self.base_url}{path}",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            # Log response
            logger.info(f"Doku Response Status: {response.status_code}")
            logger.info(f"Doku Response Body: {response.text}")
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Doku Error: {str(e)}")
            logger.error(f"Response: {getattr(e.response, 'text', 'No response')}")
            return {
                "error": str(e),
                "response": getattr(e.response, 'text', 'No response'),
                "status": "failed"
            }
    
    def check_payment_status(self, invoice_number: str) -> Dict:
        """Check payment status"""
        path = f"/orders/v1/status/{invoice_number}"
        headers = self._get_headers("GET", path)
        
        try:
            response = requests.get(
                f"{self.base_url}{path}",
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "error": str(e),
                "status": "unknown"
            }
    
    def verify_callback(self, signature: str, body: str) -> bool:
        """Verify callback signature from Doku"""
        expected_signature = hmac.new(
            self.secret_key.encode('utf-8'),
            body.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected_signature)


# Singleton instance
doku_client = DokuClient()
