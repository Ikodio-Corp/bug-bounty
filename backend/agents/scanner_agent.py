"""
Scanner Agent - AI-powered vulnerability scanning
"""

from typing import Dict, Any, List
import httpx
import asyncio

from core.config import settings


class ScannerAgent:
    """AI agent for vulnerability scanning"""
    
    def __init__(self):
        self.timeout = httpx.Timeout(30.0)
        self.headers = {
            "User-Agent": "Ikodio-BugBounty-Scanner/1.0"
        }
    
    async def scan_target(
        self,
        target_url: str,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Scan target for vulnerabilities"""
        
        results = {
            "target_url": target_url,
            "findings": [],
            "scan_type": config.get("scan_type", "quick")
        }
        
        tasks = []
        
        if "xss" in config.get("focus", []):
            tasks.append(self._scan_xss(target_url))
        
        if "sqli" in config.get("focus", []):
            tasks.append(self._scan_sqli(target_url))
        
        if "rce" in config.get("focus", []):
            tasks.append(self._scan_rce(target_url))
        
        findings = await asyncio.gather(*tasks, return_exceptions=True)
        
        for finding in findings:
            if isinstance(finding, Exception):
                continue
            if finding:
                results["findings"].extend(finding)
        
        return results
    
    async def _scan_xss(self, target_url: str) -> List[Dict[str, Any]]:
        """Scan for XSS vulnerabilities"""
        findings = []
        
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "'\"><script>alert(1)</script>",
            "<img src=x onerror=alert(1)>"
        ]
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            for payload in xss_payloads:
                try:
                    response = await client.get(
                        target_url,
                        params={"q": payload},
                        headers=self.headers,
                        follow_redirects=True
                    )
                    
                    if payload in response.text:
                        findings.append({
                            "type": "xss",
                            "severity": "high",
                            "payload": payload,
                            "evidence": response.text[:200],
                            "confidence": 0.9
                        })
                
                except Exception:
                    continue
        
        return findings
    
    async def _scan_sqli(self, target_url: str) -> List[Dict[str, Any]]:
        """Scan for SQL injection vulnerabilities"""
        findings = []
        
        sqli_payloads = [
            "' OR '1'='1",
            "1' OR '1'='1' --",
            "admin'--"
        ]
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            for payload in sqli_payloads:
                try:
                    response = await client.get(
                        target_url,
                        params={"id": payload},
                        headers=self.headers
                    )
                    
                    sql_errors = [
                        "sql syntax",
                        "mysql_fetch",
                        "ora-01756",
                        "postgresql error"
                    ]
                    
                    response_lower = response.text.lower()
                    for error in sql_errors:
                        if error in response_lower:
                            findings.append({
                                "type": "sqli",
                                "severity": "critical",
                                "payload": payload,
                                "evidence": response.text[:200],
                                "confidence": 0.85
                            })
                            break
                
                except Exception:
                    continue
        
        return findings
    
    async def _scan_rce(self, target_url: str) -> List[Dict[str, Any]]:
        """Scan for Remote Code Execution vulnerabilities"""
        findings = []
        
        rce_payloads = [
            ";ls -la",
            "| whoami",
            "$(id)"
        ]
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            for payload in rce_payloads:
                try:
                    response = await client.post(
                        target_url,
                        data={"cmd": payload},
                        headers=self.headers
                    )
                    
                    rce_indicators = [
                        "uid=",
                        "gid=",
                        "root",
                        "total "
                    ]
                    
                    response_lower = response.text.lower()
                    for indicator in rce_indicators:
                        if indicator in response_lower:
                            findings.append({
                                "type": "rce",
                                "severity": "critical",
                                "payload": payload,
                                "evidence": response.text[:200],
                                "confidence": 0.95
                            })
                            break
                
                except Exception:
                    continue
        
        return findings
