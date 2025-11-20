"""
AI Agent Orchestrator - Coordinates multiple AI agents for vulnerability discovery
"""

from typing import Dict, Any, List
import asyncio
from datetime import datetime

from agents.scanner_agent import ScannerAgent
from agents.analyzer_agent import AnalyzerAgent
from agents.reporter_agent import ReporterAgent
from core.config import settings


class AIOrchestrator:
    """Orchestrates AI agents for 90-second vulnerability discovery"""
    
    def __init__(self):
        self.scanner = ScannerAgent()
        self.analyzer = AnalyzerAgent()
        self.reporter = ReporterAgent()
    
    async def run_discovery(
        self,
        target_url: str,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Run complete vulnerability discovery workflow
        Target: Complete within 90 seconds
        """
        start_time = datetime.utcnow()
        
        results = {
            "target_url": target_url,
            "start_time": start_time.isoformat(),
            "vulnerabilities": [],
            "metadata": {}
        }
        
        try:
            scan_results = await asyncio.wait_for(
                self.scanner.scan_target(target_url, config),
                timeout=30.0  # 30 seconds for scanning
            )
            
            results["scan_results"] = scan_results
            
            if scan_results.get("findings"):
                analysis_results = await asyncio.wait_for(
                    self.analyzer.analyze_findings(scan_results["findings"]),
                    timeout=40.0  # 40 seconds for analysis
                )
                
                results["analysis"] = analysis_results
                results["vulnerabilities"] = analysis_results.get("vulnerabilities", [])
            
            if results["vulnerabilities"]:
                report = await asyncio.wait_for(
                    self.reporter.generate_summary(results["vulnerabilities"]),
                    timeout=20.0  # 20 seconds for reporting
                )
                
                results["report"] = report
            
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            
            results["end_time"] = end_time.isoformat()
            results["duration_seconds"] = duration
            results["success"] = True
            
        except asyncio.TimeoutError:
            results["success"] = False
            results["error"] = "Discovery timeout exceeded 90 seconds"
        except Exception as e:
            results["success"] = False
            results["error"] = str(e)
        
        return results
    
    async def quick_scan(self, target_url: str) -> Dict[str, Any]:
        """Quick scan optimized for 90-second workflow"""
        config = {
            "scan_type": "quick",
            "depth": "shallow",
            "focus": ["xss", "sqli", "rce"],
            "timeout": 90
        }
        
        return await self.run_discovery(target_url, config)
    
    async def deep_scan(self, target_url: str) -> Dict[str, Any]:
        """Deep scan for comprehensive analysis"""
        config = {
            "scan_type": "deep",
            "depth": "full",
            "focus": "all",
            "timeout": 600
        }
        
        return await self.run_discovery(target_url, config)
