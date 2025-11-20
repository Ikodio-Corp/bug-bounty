"""
Scanner Orchestrator - Coordinates multiple security scanner tools
"""

from typing import Dict, Any, List
import asyncio
from datetime import datetime

from scanners.nuclei_scanner import NucleiScanner
from scanners.zap_scanner import ZAPScanner
from scanners.burp_scanner import BurpScanner
from scanners.custom_scanner import CustomScanner


class ScannerOrchestrator:
    """Orchestrates multiple security scanners"""
    
    def __init__(self):
        self.nuclei = NucleiScanner()
        self.zap = ZAPScanner()
        self.burp = BurpScanner()
        self.custom = CustomScanner()
    
    async def run_full_scan(
        self,
        target_url: str,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Run full security scan using all available scanners"""
        
        start_time = datetime.utcnow()
        
        results = {
            "target_url": target_url,
            "start_time": start_time.isoformat(),
            "scanners_used": [],
            "vulnerabilities": [],
            "errors": []
        }
        
        scanner_tasks = []
        
        if config.get("use_nuclei", True):
            scanner_tasks.append(self._run_nuclei(target_url, config))
            results["scanners_used"].append("nuclei")
        
        if config.get("use_zap", True):
            scanner_tasks.append(self._run_zap(target_url, config))
            results["scanners_used"].append("zap")
        
        if config.get("use_burp", False):
            scanner_tasks.append(self._run_burp(target_url, config))
            results["scanners_used"].append("burp")
        
        if config.get("use_custom", True):
            scanner_tasks.append(self._run_custom(target_url, config))
            results["scanners_used"].append("custom")
        
        scanner_results = await asyncio.gather(*scanner_tasks, return_exceptions=True)
        
        for idx, result in enumerate(scanner_results):
            if isinstance(result, Exception):
                results["errors"].append({
                    "scanner": results["scanners_used"][idx],
                    "error": str(result)
                })
            elif result:
                results["vulnerabilities"].extend(result.get("vulnerabilities", []))
        
        results["vulnerabilities"] = self._deduplicate_vulnerabilities(
            results["vulnerabilities"]
        )
        
        end_time = datetime.utcnow()
        results["end_time"] = end_time.isoformat()
        results["duration_seconds"] = (end_time - start_time).total_seconds()
        results["total_vulnerabilities"] = len(results["vulnerabilities"])
        
        return results
    
    async def _run_nuclei(
        self,
        target_url: str,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Run Nuclei scanner"""
        return await self.nuclei.scan(target_url, config)
    
    async def _run_zap(
        self,
        target_url: str,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Run OWASP ZAP scanner"""
        return await self.zap.scan(target_url, config)
    
    async def _run_burp(
        self,
        target_url: str,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Run Burp Suite scanner"""
        return await self.burp.scan(target_url, config)
    
    async def _run_custom(
        self,
        target_url: str,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Run custom scanner"""
        return await self.custom.scan(target_url, config)
    
    def _deduplicate_vulnerabilities(
        self,
        vulnerabilities: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Remove duplicate vulnerabilities"""
        
        seen = set()
        unique_vulns = []
        
        for vuln in vulnerabilities:
            key = (
                vuln.get("type"),
                vuln.get("url"),
                vuln.get("parameter")
            )
            
            if key not in seen:
                seen.add(key)
                unique_vulns.append(vuln)
        
        return unique_vulns
    
    async def quick_scan(self, target_url: str) -> Dict[str, Any]:
        """Quick scan for common vulnerabilities"""
        config = {
            "use_nuclei": True,
            "use_zap": False,
            "use_burp": False,
            "use_custom": True,
            "timeout": 90,
            "severity": ["critical", "high"]
        }
        
        return await self.run_full_scan(target_url, config)
