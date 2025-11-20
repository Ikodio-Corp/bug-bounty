"""
Notification tasks
"""

from typing import Dict, Any
import asyncio


def run_async(coro):
    """Helper to run async code in sync context"""
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(coro)


def send_bug_notification(user_id: int, bug_id: int, notification_type: str) -> Dict[str, Any]:
    """Send bug-related notification"""
    async def _send():
        from integrations.email_client import EmailClient
        from core.database import async_session_maker
        from models.user import User
        from models.bug import Bug
        from sqlalchemy import select
        
        async with async_session_maker() as db:
            user_result = await db.execute(select(User).where(User.id == user_id))
            user = user_result.scalar_one_or_none()
            
            bug_result = await db.execute(select(Bug).where(Bug.id == bug_id))
            bug = bug_result.scalar_one_or_none()
            
            if not user or not bug:
                return {"error": "User or bug not found"}
            
            email_client = EmailClient()
            
            if notification_type == "bug_validated":
                subject = f"Bug Validated: {bug.title}"
                body = f"Your bug report '{bug.title}' has been validated and approved."
            elif notification_type == "bug_fixed":
                subject = f"Bug Fixed: {bug.title}"
                body = f"The bug '{bug.title}' has been marked as fixed."
            elif notification_type == "bounty_paid":
                subject = f"Bounty Paid: ${bug.bounty_amount}"
                body = f"You have received ${bug.bounty_amount} for bug: {bug.title}"
            else:
                subject = f"Bug Update: {bug.title}"
                body = f"There has been an update on your bug: {bug.title}"
            
            success = await email_client.send_email(
                to_email=user.email,
                subject=subject,
                body=body
            )
            
            return {"success": success}
    
    return run_async(_send())


def send_marketplace_notification(
    user_id: int,
    notification_type: str,
    data: Dict[str, Any]
) -> Dict[str, Any]:
    """Send marketplace notification"""
    async def _send():
        from integrations.email_client import EmailClient
        from core.database import async_session_maker
        from models.user import User
        from sqlalchemy import select
        
        async with async_session_maker() as db:
            result = await db.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
            
            if not user:
                return {"error": "User not found"}
            
            email_client = EmailClient()
            
            if notification_type == "listing_sold":
                subject = "Your Listing Has Been Sold"
                body = f"Your listing has been sold for ${data.get('price', 0)}"
            elif notification_type == "purchase_confirmed":
                subject = "Purchase Confirmed"
                body = f"Your purchase has been confirmed. Transaction ID: {data.get('transaction_id')}"
            elif notification_type == "nft_minted":
                subject = "NFT Successfully Minted"
                body = f"Your bug NFT has been minted. Token ID: {data.get('token_id')}"
            else:
                subject = "Marketplace Update"
                body = "There has been an update on your marketplace activity"
            
            success = await email_client.send_email(
                to_email=user.email,
                subject=subject,
                body=body
            )
            
            return {"success": success}
    
    return run_async(_send())


def send_guild_notification(
    user_id: int,
    guild_name: str,
    notification_type: str
) -> Dict[str, Any]:
    """Send guild notification"""
    async def _send():
        from integrations.email_client import EmailClient
        from core.database import async_session_maker
        from models.user import User
        from sqlalchemy import select
        
        async with async_session_maker() as db:
            result = await db.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
            
            if not user:
                return {"error": "User not found"}
            
            email_client = EmailClient()
            
            if notification_type == "tier_upgraded":
                subject = f"Guild Tier Upgraded: {guild_name}"
                body = f"Congratulations! Your tier in {guild_name} has been upgraded."
            elif notification_type == "proposal_created":
                subject = f"New Proposal: {guild_name}"
                body = f"A new proposal has been created in {guild_name}. Vote now!"
            elif notification_type == "proposal_passed":
                subject = f"Proposal Passed: {guild_name}"
                body = f"A proposal you voted on in {guild_name} has passed."
            else:
                subject = f"Guild Update: {guild_name}"
                body = f"There has been an update in {guild_name}"
            
            success = await email_client.send_email(
                to_email=user.email,
                subject=subject,
                body=body
            )
            
            return {"success": success}
    
    return run_async(_send())


def send_scan_complete_notification(user_id: int, scan_id: int) -> Dict[str, Any]:
    """Send scan completion notification"""
    async def _send():
        from integrations.email_client import EmailClient
        from core.database import async_session_maker
        from models.user import User
        from models.bug import Scan
        from sqlalchemy import select
        
        async with async_session_maker() as db:
            user_result = await db.execute(select(User).where(User.id == user_id))
            user = user_result.scalar_one_or_none()
            
            scan_result = await db.execute(select(Scan).where(Scan.id == scan_id))
            scan = scan_result.scalar_one_or_none()
            
            if not user or not scan:
                return {"error": "User or scan not found"}
            
            email_client = EmailClient()
            
            subject = "Security Scan Complete"
            body = f"""
Your security scan has completed.

Target: {scan.target_url}
Vulnerabilities Found: {scan.vulnerabilities_found}
Duration: {scan.duration_seconds} seconds

View results: https://platform.ikodio.com/scans/{scan_id}
            """
            
            success = await email_client.send_email(
                to_email=user.email,
                subject=subject,
                body=body
            )
            
            return {"success": success}
    
    return run_async(_send())
