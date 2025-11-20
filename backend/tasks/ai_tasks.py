"""
AI-related Celery tasks
"""

from typing import Dict, Any
import asyncio

from agents.orchestrator import AIOrchestrator
from agents.analyzer import VulnerabilityAnalyzer
from agents.reporter import AIReporter


def run_async(coro):
    """Helper to run async code in sync context"""
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(coro)


def orchestrate_ai_scan(target_url: str, scan_config: Dict[str, Any]) -> Dict[str, Any]:
    """Orchestrate AI agents for vulnerability discovery"""
    async def _orchestrate():
        orchestrator = AIOrchestrator()
        results = await orchestrator.run_discovery(
            target_url=target_url,
            config=scan_config
        )
        return results
    
    return run_async(_orchestrate())


def analyze_vulnerability_pattern(bug_data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze vulnerability patterns using AI"""
    async def _analyze():
        analyzer = VulnerabilityAnalyzer()
        pattern = await analyzer.analyze_pattern(bug_data)
        return pattern
    
    return run_async(_analyze())


def generate_intelligence_report(company_name: str, scan_ids: list) -> Dict[str, Any]:
    """Generate comprehensive intelligence report"""
    async def _generate():
        reporter = AIReporter()
        report = await reporter.generate_intelligence_report(
            company_name=company_name,
            scan_ids=scan_ids
        )
        return report
    
    return run_async(_generate())


def predict_vulnerabilities(target_info: Dict[str, Any]) -> Dict[str, Any]:
    """Predict potential vulnerabilities using AI"""
    async def _predict():
        from agents.predictor import VulnerabilityPredictor
        predictor = VulnerabilityPredictor()
        
        predictions = await predictor.predict(target_info)
        return predictions
    
    return run_async(_predict())


def train_vulnerability_model(training_data: list) -> Dict[str, Any]:
    """Train vulnerability detection model"""
    async def _train():
        from agents.trainer import ModelTrainer
        trainer = ModelTrainer()
        
        results = await trainer.train(training_data)
        return results
    
    return run_async(_train())
