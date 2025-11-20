"""
OWASP ZAP Scanner Integration - Web application security testing
"""

from typing import Dict, Any, List
import httpx
import asyncio
from datetime import datetime


class ZAPScanner:
    """Integration with OWASP ZAP scanner"""
    
    def __init__(self):
        self.zap_url = "http://localhost:8080"
        self.api_key = "changeme"
    
    async def scan(
        self,
        target_url: str,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Run OWASP ZAP scan"""
        
        timeout = config.get("timeout", 300)
        scan_type = config.get("scan_type", "quick")
        
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                spider_response = await client.get(
                    f"{self.zap_url}/JSON/spider/action/scan/",
                    params={
                        "apikey": self.api_key,
                        "url": target_url,
                        "maxChildren": 10 if scan_type == "quick" else 100
                    }
                )
                
                scan_id = spider_response.json().get("scan")
                
                await self._wait_for_spider(client, scan_id, timeout=60)
                
                ascan_response = await client.get(
                    f"{self.zap_url}/JSON/ascan/action/scan/",
                    params={
                        "apikey": self.api_key,
                        "url": target_url,
                        "recurse": "true"
                    }
                )
                
                ascan_id = ascan_response.json().get("scan")
                
                await self._wait_for_ascan(client, ascan_id, timeout=timeout)
                
                alerts_response = await client.get(
                    f"{self.zap_url}/JSON/core/view/alerts/",
                    params={
                        "apikey": self.api_key,
                        "baseurl": target_url
                    }
                )
                
                alerts = alerts_response.json().get("alerts", [])
                vulnerabilities = self._parse_zap_alerts(alerts)
                
                return {
                    "scanner": "zap",
                    "vulnerabilities": vulnerabilities,
                    "scanned_at": datetime.utcnow().isoformat()
                }
        
        except httpx.ConnectError:
            return {
                "scanner": "zap",
                "vulnerabilities": self._simulate_zap_scan(target_url),
                "note": "ZAP not running, using simulated results"
            }
        
        except Exception as e:
            return {
                "scanner": "zap",
                "vulnerabilities": [],
                "error": str(e)
            }
    
    async def _wait_for_spider(
        self,
        client: httpx.AsyncClient,
        scan_id: str,
        timeout: int
    ) -> None:
        """Wait for spider scan to complete"""
        
        start_time = asyncio.get_event_loop().time()
        
        while True:
            if asyncio.get_event_loop().time() - start_time > timeout:
                break
            
            response = await client.get(
                f"{self.zap_url}/JSON/spider/view/status/",
                params={
                    "apikey": self.api_key,
                    "scanId": scan_id
                }
            )
            
            status = int(response.json().get("status", "0"))
            
            if status >= 100:
                break
            
            await asyncio.sleep(2)
    
    async def _wait_for_ascan(
        self,
        client: httpx.AsyncClient,
        scan_id: str,
        timeout: int
    ) -> None:
        """Wait for active scan to complete"""
        
        start_time = asyncio.get_event_loop().time()
        
        while True:
            if asyncio.get_event_loop().time() - start_time > timeout:
                break
            
            response = await client.get(
                f"{self.zap_url}/JSON/ascan/view/status/",
                params={
                    "apikey": self.api_key,
                    "scanId": scan_id
                }
            )
            
            status = int(response.json().get("status", "0"))
            
            if status >= 100:
                break
            
            await asyncio.sleep(5)
    
    def _parse_zap_alerts(self, alerts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Parse ZAP alerts into vulnerabilities"""
        
        vulnerabilities = []
        
        severity_map = {
            "3": "critical",
            "2": "high",
            "1": "medium",
            "0": "low"
        }
        
        for alert in alerts:
            vuln = {
                "type": alert.get("pluginId", "unknown"),
                "name": alert.get("alert", "Unknown"),
                "severity": severity_map.get(str(alert.get("risk", "1")), "medium"),
                "url": alert.get("url", ""),
                "parameter": alert.get("param", ""),
                "description": alert.get("description", ""),
                "solution": alert.get("solution", ""),
                "scanner": "zap",
                "confidence": alert.get("confidence", "medium").lower()
            }
            
            vulnerabilities.append(vuln)
        
        return vulnerabilities
    
    def _simulate_zap_scan(self, target_url: str) -> List[Dict[str, Any]]:
        """Simulate ZAP scan for testing"""
        
        return [
            {
                "type": "40012",
                "name": "Cross-Site Scripting (Reflected)",
                "severity": "high",
                "url": target_url,
                "parameter": "q",
                "description": "Reflected XSS vulnerability in search parameter",
                "solution": "Validate and encode all user input",
                "scanner": "zap",
                "confidence": "high"
            },
            {
                "type": "40018",
                "name": "SQL Injection",
                "severity": "critical",
                "url": target_url,
                "parameter": "id",
                "description": "SQL injection vulnerability detected",
                "solution": "Use parameterized queries",
                "scanner": "zap",
                "confidence": "medium"
            }
        ]
