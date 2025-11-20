"""
Custom Scanner - Proprietary vulnerability detection
"""

from typing import Dict, Any, List
import httpx
import asyncio
from datetime import datetime
import re


class CustomScanner:
    """Custom scanner for proprietary vulnerability detection"""
    
    def __init__(self):
        self.timeout = httpx.Timeout(30.0)
        self.headers = {
            "User-Agent": "Ikodio-CustomScanner/1.0"
        }
    
    async def scan(
        self,
        target_url: str,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Run custom vulnerability scan"""
        
        vulnerabilities = []
        
        scan_tasks = [
            self._check_sensitive_files(target_url),
            self._check_api_exposure(target_url),
            self._check_subdomain_takeover(target_url),
            self._check_cors_misconfiguration(target_url),
            self._check_clickjacking(target_url)
        ]
        
        results = await asyncio.gather(*scan_tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, Exception):
                continue
            if result:
                vulnerabilities.extend(result)
        
        return {
            "scanner": "custom",
            "vulnerabilities": vulnerabilities,
            "scanned_at": datetime.utcnow().isoformat()
        }
    
    async def _check_sensitive_files(self, target_url: str) -> List[Dict[str, Any]]:
        """Check for exposed sensitive files"""
        
        vulnerabilities = []
        
        sensitive_paths = [
            "/.env",
            "/.git/config",
            "/config.php",
            "/admin",
            "/phpinfo.php",
            "/backup.sql",
            "/.aws/credentials"
        ]
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            for path in sensitive_paths:
                try:
                    response = await client.get(
                        f"{target_url}{path}",
                        headers=self.headers,
                        follow_redirects=False
                    )
                    
                    if response.status_code == 200:
                        vulnerabilities.append({
                            "type": "sensitive-file-exposure",
                            "name": f"Exposed Sensitive File: {path}",
                            "severity": "high",
                            "url": f"{target_url}{path}",
                            "description": f"Sensitive file {path} is publicly accessible",
                            "scanner": "custom",
                            "confidence": "high"
                        })
                
                except Exception:
                    continue
        
        return vulnerabilities
    
    async def _check_api_exposure(self, target_url: str) -> List[Dict[str, Any]]:
        """Check for exposed API endpoints"""
        
        vulnerabilities = []
        
        api_paths = [
            "/api/users",
            "/api/admin",
            "/api/config",
            "/graphql",
            "/v1/users"
        ]
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            for path in api_paths:
                try:
                    response = await client.get(
                        f"{target_url}{path}",
                        headers=self.headers
                    )
                    
                    if response.status_code == 200:
                        if self._contains_sensitive_data(response.text):
                            vulnerabilities.append({
                                "type": "api-exposure",
                                "name": f"Exposed API Endpoint: {path}",
                                "severity": "medium",
                                "url": f"{target_url}{path}",
                                "description": f"API endpoint {path} exposes sensitive data",
                                "scanner": "custom",
                                "confidence": "medium"
                            })
                
                except Exception:
                    continue
        
        return vulnerabilities
    
    async def _check_subdomain_takeover(self, target_url: str) -> List[Dict[str, Any]]:
        """Check for subdomain takeover vulnerability"""
        
        vulnerabilities = []
        
        takeover_indicators = [
            "There isn't a GitHub Pages site here",
            "NoSuchBucket",
            "No such app",
            "Project not found",
            "is not a registered application"
        ]
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(target_url, headers=self.headers)
                
                for indicator in takeover_indicators:
                    if indicator in response.text:
                        vulnerabilities.append({
                            "type": "subdomain-takeover",
                            "name": "Potential Subdomain Takeover",
                            "severity": "critical",
                            "url": target_url,
                            "description": f"Subdomain may be vulnerable to takeover: {indicator}",
                            "scanner": "custom",
                            "confidence": "high"
                        })
                        break
        
        except Exception:
            pass
        
        return vulnerabilities
    
    async def _check_cors_misconfiguration(self, target_url: str) -> List[Dict[str, Any]]:
        """Check for CORS misconfiguration"""
        
        vulnerabilities = []
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    target_url,
                    headers={
                        **self.headers,
                        "Origin": "https://evil.com"
                    }
                )
                
                acao = response.headers.get("Access-Control-Allow-Origin", "")
                acac = response.headers.get("Access-Control-Allow-Credentials", "")
                
                if acao == "https://evil.com" or acao == "*":
                    severity = "high" if acac == "true" else "medium"
                    
                    vulnerabilities.append({
                        "type": "cors-misconfiguration",
                        "name": "CORS Misconfiguration",
                        "severity": severity,
                        "url": target_url,
                        "description": f"Insecure CORS policy: {acao}",
                        "scanner": "custom",
                        "confidence": "high"
                    })
        
        except Exception:
            pass
        
        return vulnerabilities
    
    async def _check_clickjacking(self, target_url: str) -> List[Dict[str, Any]]:
        """Check for clickjacking vulnerability"""
        
        vulnerabilities = []
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(target_url, headers=self.headers)
                
                x_frame_options = response.headers.get("X-Frame-Options", "")
                csp = response.headers.get("Content-Security-Policy", "")
                
                if not x_frame_options and "frame-ancestors" not in csp:
                    vulnerabilities.append({
                        "type": "clickjacking",
                        "name": "Clickjacking Vulnerability",
                        "severity": "medium",
                        "url": target_url,
                        "description": "Missing X-Frame-Options and CSP frame-ancestors",
                        "scanner": "custom",
                        "confidence": "high"
                    })
        
        except Exception:
            pass
        
        return vulnerabilities
    
    def _contains_sensitive_data(self, response_text: str) -> bool:
        """Check if response contains sensitive data"""
        
        sensitive_patterns = [
            r'"password"\s*:\s*"[^"]+',
            r'"api_key"\s*:\s*"[^"]+',
            r'"token"\s*:\s*"[^"]+',
            r'"secret"\s*:\s*"[^"]+'
        ]
        
        for pattern in sensitive_patterns:
            if re.search(pattern, response_text, re.IGNORECASE):
                return True
        
        return False
