"""
Celery tasks for security scanning
"""

from celery import Task
from typing import Dict, Any
import asyncio
from sqlalchemy.ext.asyncio import create_async_session

from core.config import settings
from core.database import async_session_maker
from services.scan_service import ScanService
from services.bug_service import BugService
from scanners.orchestrator import ScannerOrchestrator


class ScanTask(Task):
    """Base task for scanning operations"""
    
    def __init__(self):
        self._orchestrator = None
    
    @property
    def orchestrator(self):
        if self._orchestrator is None:
            self._orchestrator = ScannerOrchestrator()
        return self._orchestrator


def run_async(coro):
    """Helper to run async code in sync context"""
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(coro)


def execute_scan(scan_id: int) -> Dict[str, Any]:
    """Execute security scan"""
    async def _execute():
        async with async_session_maker() as db:
            scan_service = ScanService(db)
            bug_service = BugService(db)
            
            scan = await scan_service.get_scan_by_id(scan_id)
            if not scan:
                return {"error": "Scan not found"}
            
            await scan_service.update_scan_status(scan_id, "running")
            
            try:
                orchestrator = ScannerOrchestrator()
                results = await orchestrator.execute_scan(
                    target_url=scan.target_url,
                    scan_type=scan.scan_type,
                    target_platform=scan.target_platform
                )
                
                vulnerabilities_found = len(results.get("vulnerabilities", []))
                
                for vuln in results.get("vulnerabilities", []):
                    await bug_service.create_bug(
                        user_id=scan.user_id,
                        title=vuln.get("title"),
                        description=vuln.get("description"),
                        bug_type=vuln.get("type"),
                        severity=vuln.get("severity"),
                        target_url=scan.target_url,
                        proof_of_concept=vuln.get("proof_of_concept", ""),
                        cvss_score=vuln.get("cvss_score"),
                        ai_generated=True,
                        ai_confidence=vuln.get("confidence", 0.0)
                    )
                
                results["vulnerabilities_found"] = vulnerabilities_found
                
                await scan_service.update_scan_status(
                    scan_id,
                    "completed",
                    results=results
                )
                
                return results
                
            except Exception as e:
                await scan_service.update_scan_status(
                    scan_id,
                    "failed",
                    error_message=str(e)
                )
                return {"error": str(e)}
    
    return run_async(_execute())


def generate_ai_report(bug_id: int) -> Dict[str, Any]:
    """Generate AI-powered vulnerability report"""
    async def _generate():
        async with async_session_maker() as db:
            bug_service = BugService(db)
            
            bug = await bug_service.get_bug_by_id(bug_id)
            if not bug:
                return {"error": "Bug not found"}
            
            from agents.reporter import AIReporter
            reporter = AIReporter()
            
            report = await reporter.generate_report(
                title=bug.title,
                description=bug.description,
                severity=bug.severity.value,
                proof_of_concept=bug.proof_of_concept,
                target_url=bug.target_url
            )
            
            return report
    
    return run_async(_generate())


def analyze_exploit_chain(bug_ids: list) -> Dict[str, Any]:
    """Analyze potential exploit chains"""
    async def _analyze():
        async with async_session_maker() as db:
            from agents.analyzer import ExploitChainAnalyzer
            analyzer = ExploitChainAnalyzer()
            
            bug_service = BugService(db)
            bugs = []
            
            for bug_id in bug_ids:
                bug = await bug_service.get_bug_by_id(bug_id)
                if bug:
                    bugs.append(bug)
            
            if not bugs:
                return {"error": "No bugs found"}
            
            chains = await analyzer.analyze_chain(bugs)
            
            return {"chains": chains}
    
    return run_async(_analyze())


def process_payment(payment_id: int) -> Dict[str, Any]:
    """Process marketplace payment"""
    async def _process():
        async with async_session_maker() as db:
            from models.marketplace import Payment, PaymentStatus
            from sqlalchemy import select
            
            result = await db.execute(
                select(Payment).where(Payment.id == payment_id)
            )
            payment = result.scalar_one_or_none()
            
            if not payment:
                return {"error": "Payment not found"}
            
            try:
                payment.status = PaymentStatus.PROCESSING
                await db.commit()
                
                if payment.payment_method == "stripe":
                    from integrations.stripe_client import StripeClient
                    stripe_client = StripeClient()
                    result = await stripe_client.process_payment(
                        amount=payment.amount,
                        currency=payment.currency
                    )
                    
                    if result.get("success"):
                        payment.status = PaymentStatus.COMPLETED
                        payment.transaction_id = result.get("transaction_id")
                    else:
                        payment.status = PaymentStatus.FAILED
                        payment.error_message = result.get("error")
                
                await db.commit()
                
                return {"status": payment.status.value}
                
            except Exception as e:
                payment.status = PaymentStatus.FAILED
                payment.error_message = str(e)
                await db.commit()
                return {"error": str(e)}
    
    return run_async(_process())


def send_notification_email(user_id: int, subject: str, body: str) -> Dict[str, Any]:
    """Send email notification"""
    async def _send():
        from integrations.email_client import EmailClient
        from models.user import User
        from sqlalchemy import select
        
        async with async_session_maker() as db:
            result = await db.execute(
                select(User).where(User.id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                return {"error": "User not found"}
            
            email_client = EmailClient()
            success = await email_client.send_email(
                to_email=user.email,
                subject=subject,
                body=body
            )
            
            return {"success": success}
    
    return run_async(_send())
