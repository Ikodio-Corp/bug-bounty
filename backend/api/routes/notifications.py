"""
Notification Management Routes
Email, Slack, Discord, SMS notifications
"""
from fastapi import APIRouter, HTTPException, Depends, Body
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any

from core.database import get_db
from core.security import get_current_user
from services.notification_service import (
    EmailNotificationService,
    SlackNotificationService,
    DiscordNotificationService,
    NotificationOrchestrator
)
from models.user import User

router = APIRouter(prefix="/notifications", tags=["Notifications"])


class EmailConfig(BaseModel):
    """Email configuration"""
    smtp_host: str
    smtp_port: int
    smtp_user: str
    smtp_password: str
    from_email: EmailStr


class SlackConfig(BaseModel):
    """Slack configuration"""
    webhook_url: str
    channel: Optional[str] = None


class DiscordConfig(BaseModel):
    """Discord configuration"""
    webhook_url: str


class SendEmailRequest(BaseModel):
    """Request to send email"""
    to_email: EmailStr
    subject: str
    body: str
    html: Optional[bool] = False


class SendSlackRequest(BaseModel):
    """Request to send Slack message"""
    message: str
    channel: Optional[str] = None


class SendDiscordRequest(BaseModel):
    """Request to send Discord message"""
    message: str
    username: Optional[str] = "IKODIO Bot"


class NotificationPreferences(BaseModel):
    """User notification preferences"""
    email_enabled: bool = True
    slack_enabled: bool = False
    discord_enabled: bool = False
    vulnerability_alerts: bool = True
    scan_completion: bool = True
    payment_receipts: bool = True
    marketing_emails: bool = False


@router.post("/email/configure")
async def configure_email(
    config: EmailConfig,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Configure email notification service
    
    Args:
        config: Email configuration
        current_user: Authenticated user
        db: Database session
        
    Returns:
        dict: Configuration status
    """
    try:
        email_service = EmailNotificationService(
            smtp_host=config.smtp_host,
            smtp_port=config.smtp_port,
            smtp_user=config.smtp_user,
            smtp_password=config.smtp_password,
            from_email=config.from_email
        )
        
        # Test connection
        test_result = await email_service.send_email(
            to_email=current_user.email,
            subject="IKODIO Email Configuration Test",
            body="Email notification service configured successfully."
        )
        
        if not test_result:
            raise HTTPException(
                status_code=400,
                detail="Failed to send test email. Check configuration."
            )
        
        return {
            "status": "configured",
            "service": "email",
            "smtp_host": config.smtp_host,
            "from_email": config.from_email,
            "test_sent": True
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Email configuration failed: {str(e)}"
        )


@router.post("/slack/configure")
async def configure_slack(
    config: SlackConfig,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Configure Slack notification service
    
    Args:
        config: Slack configuration
        current_user: Authenticated user
        db: Database session
        
    Returns:
        dict: Configuration status
    """
    try:
        slack_service = SlackNotificationService(
            webhook_url=config.webhook_url
        )
        
        # Test connection
        test_result = await slack_service.send_message(
            message="Slack notification service configured successfully.",
            channel=config.channel
        )
        
        if not test_result:
            raise HTTPException(
                status_code=400,
                detail="Failed to send test message. Check webhook URL."
            )
        
        return {
            "status": "configured",
            "service": "slack",
            "webhook_url": config.webhook_url[:50] + "...",
            "channel": config.channel,
            "test_sent": True
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Slack configuration failed: {str(e)}"
        )


@router.post("/discord/configure")
async def configure_discord(
    config: DiscordConfig,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Configure Discord notification service
    
    Args:
        config: Discord configuration
        current_user: Authenticated user
        db: Database session
        
    Returns:
        dict: Configuration status
    """
    try:
        discord_service = DiscordNotificationService(
            webhook_url=config.webhook_url
        )
        
        # Test connection
        test_result = await discord_service.send_message(
            message="Discord notification service configured successfully.",
            username="IKODIO Bot"
        )
        
        if not test_result:
            raise HTTPException(
                status_code=400,
                detail="Failed to send test message. Check webhook URL."
            )
        
        return {
            "status": "configured",
            "service": "discord",
            "webhook_url": config.webhook_url[:50] + "...",
            "test_sent": True
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Discord configuration failed: {str(e)}"
        )


@router.post("/email/send")
async def send_email_notification(
    request: SendEmailRequest,
    email_config: EmailConfig = Body(...),
    current_user: User = Depends(get_current_user)
):
    """
    Send email notification
    
    Args:
        request: Email request
        email_config: Email configuration
        current_user: Authenticated user
        
    Returns:
        dict: Send status
    """
    try:
        email_service = EmailNotificationService(
            smtp_host=email_config.smtp_host,
            smtp_port=email_config.smtp_port,
            smtp_user=email_config.smtp_user,
            smtp_password=email_config.smtp_password,
            from_email=email_config.from_email
        )
        
        success = await email_service.send_email(
            to_email=request.to_email,
            subject=request.subject,
            body=request.body
        )
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to send email"
            )
        
        return {
            "status": "sent",
            "service": "email",
            "to": request.to_email,
            "subject": request.subject
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Email send failed: {str(e)}"
        )


@router.post("/slack/send")
async def send_slack_notification(
    request: SendSlackRequest,
    slack_config: SlackConfig = Body(...),
    current_user: User = Depends(get_current_user)
):
    """
    Send Slack notification
    
    Args:
        request: Slack message request
        slack_config: Slack configuration
        current_user: Authenticated user
        
    Returns:
        dict: Send status
    """
    try:
        slack_service = SlackNotificationService(
            webhook_url=slack_config.webhook_url
        )
        
        success = await slack_service.send_message(
            message=request.message,
            channel=request.channel or slack_config.channel
        )
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to send Slack message"
            )
        
        return {
            "status": "sent",
            "service": "slack",
            "channel": request.channel or slack_config.channel
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Slack send failed: {str(e)}"
        )


@router.post("/discord/send")
async def send_discord_notification(
    request: SendDiscordRequest,
    discord_config: DiscordConfig = Body(...),
    current_user: User = Depends(get_current_user)
):
    """
    Send Discord notification
    
    Args:
        request: Discord message request
        discord_config: Discord configuration
        current_user: Authenticated user
        
    Returns:
        dict: Send status
    """
    try:
        discord_service = DiscordNotificationService(
            webhook_url=discord_config.webhook_url
        )
        
        success = await discord_service.send_message(
            message=request.message,
            username=request.username
        )
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to send Discord message"
            )
        
        return {
            "status": "sent",
            "service": "discord",
            "username": request.username
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Discord send failed: {str(e)}"
        )


@router.post("/vulnerability-alert")
async def send_vulnerability_alert(
    bug_id: int = Body(...),
    severity: str = Body(...),
    title: str = Body(...),
    description: str = Body(...),
    email_config: Optional[EmailConfig] = None,
    slack_config: Optional[SlackConfig] = None,
    discord_config: Optional[DiscordConfig] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Send vulnerability alert across configured channels
    
    Args:
        bug_id: Bug ID
        severity: Vulnerability severity
        title: Vulnerability title
        description: Vulnerability description
        email_config: Email configuration
        slack_config: Slack configuration
        discord_config: Discord configuration
        current_user: Authenticated user
        
    Returns:
        dict: Delivery status for all channels
    """
    try:
        config = {}
        
        if email_config:
            config["email"] = {
                "smtp_host": email_config.smtp_host,
                "smtp_port": email_config.smtp_port,
                "smtp_user": email_config.smtp_user,
                "smtp_password": email_config.smtp_password,
                "from_email": email_config.from_email
            }
        
        if slack_config:
            config["slack"] = {
                "webhook_url": slack_config.webhook_url,
                "channel": slack_config.channel
            }
        
        if discord_config:
            config["discord"] = {
                "webhook_url": discord_config.webhook_url
            }
        
        orchestrator = NotificationOrchestrator(config)
        
        results = await orchestrator.send_vulnerability_alert(
            bug_id=bug_id,
            severity=severity,
            title=title,
            description=description,
            recipient_email=current_user.email
        )
        
        return {
            "status": "sent",
            "bug_id": bug_id,
            "severity": severity,
            "channels": results
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Alert send failed: {str(e)}"
        )


@router.post("/scan-complete")
async def send_scan_completion(
    scan_id: int = Body(...),
    vulnerabilities_found: int = Body(...),
    scan_duration: int = Body(...),
    email_config: Optional[EmailConfig] = None,
    slack_config: Optional[SlackConfig] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Send scan completion notification
    
    Args:
        scan_id: Scan ID
        vulnerabilities_found: Number of vulnerabilities found
        scan_duration: Scan duration in seconds
        email_config: Email configuration
        slack_config: Slack configuration
        current_user: Authenticated user
        
    Returns:
        dict: Delivery status
    """
    try:
        config = {}
        
        if email_config:
            config["email"] = {
                "smtp_host": email_config.smtp_host,
                "smtp_port": email_config.smtp_port,
                "smtp_user": email_config.smtp_user,
                "smtp_password": email_config.smtp_password,
                "from_email": email_config.from_email
            }
        
        if slack_config:
            config["slack"] = {
                "webhook_url": slack_config.webhook_url,
                "channel": slack_config.channel
            }
        
        orchestrator = NotificationOrchestrator(config)
        
        results = await orchestrator.send_scan_completion(
            scan_id=scan_id,
            vulnerabilities_found=vulnerabilities_found,
            scan_duration=scan_duration,
            recipient_email=current_user.email
        )
        
        return {
            "status": "sent",
            "scan_id": scan_id,
            "channels": results
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Notification send failed: {str(e)}"
        )


@router.get("/preferences")
async def get_notification_preferences(
    current_user: User = Depends(get_current_user)
):
    """
    Get user notification preferences
    
    Args:
        current_user: Authenticated user
        
    Returns:
        dict: User notification preferences
    """
    return {
        "email_enabled": current_user.email_notifications,
        "push_enabled": current_user.push_notifications,
        "slack_configured": False,
        "discord_configured": False,
        "preferences": {
            "vulnerability_alerts": True,
            "scan_completion": True,
            "payment_receipts": True,
            "marketing_emails": False
        }
    }


@router.put("/preferences")
async def update_notification_preferences(
    preferences: NotificationPreferences,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update user notification preferences
    
    Args:
        preferences: Updated preferences
        current_user: Authenticated user
        db: Database session
        
    Returns:
        dict: Updated preferences
    """
    try:
        current_user.email_notifications = preferences.email_enabled
        current_user.push_notifications = preferences.slack_enabled or preferences.discord_enabled
        
        await db.commit()
        
        return {
            "status": "updated",
            "preferences": {
                "email_enabled": preferences.email_enabled,
                "slack_enabled": preferences.slack_enabled,
                "discord_enabled": preferences.discord_enabled,
                "vulnerability_alerts": preferences.vulnerability_alerts,
                "scan_completion": preferences.scan_completion,
                "payment_receipts": preferences.payment_receipts,
                "marketing_emails": preferences.marketing_emails
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update preferences: {str(e)}"
        )


@router.get("/channels")
async def get_available_channels():
    """
    Get list of available notification channels
    
    Returns:
        dict: Available notification channels and their features
    """
    return {
        "channels": {
            "email": {
                "name": "Email",
                "description": "SMTP email notifications",
                "features": ["HTML support", "Attachments", "Templates"],
                "required_config": ["smtp_host", "smtp_port", "smtp_user", "smtp_password"]
            },
            "slack": {
                "name": "Slack",
                "description": "Slack webhook notifications",
                "features": ["Rich formatting", "Interactive buttons", "Channels"],
                "required_config": ["webhook_url"]
            },
            "discord": {
                "name": "Discord",
                "description": "Discord webhook notifications",
                "features": ["Embeds", "Rich media", "Color coding"],
                "required_config": ["webhook_url"]
            },
            "sms": {
                "name": "SMS",
                "description": "SMS notifications via Twilio",
                "features": ["Critical alerts", "Global delivery"],
                "required_config": ["twilio_account_sid", "twilio_auth_token", "from_number"],
                "status": "coming_soon"
            }
        }
    }


@router.get("/test")
async def test_notification(
    channel: str,
    email_config: Optional[EmailConfig] = None,
    slack_config: Optional[SlackConfig] = None,
    discord_config: Optional[DiscordConfig] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Test notification channel
    
    Args:
        channel: Channel to test (email, slack, discord)
        email_config: Email configuration
        slack_config: Slack configuration
        discord_config: Discord configuration
        current_user: Authenticated user
        
    Returns:
        dict: Test result
    """
    try:
        if channel == "email" and email_config:
            service = EmailNotificationService(
                smtp_host=email_config.smtp_host,
                smtp_port=email_config.smtp_port,
                smtp_user=email_config.smtp_user,
                smtp_password=email_config.smtp_password,
                from_email=email_config.from_email
            )
            success = await service.send_email(
                to_email=current_user.email,
                subject="IKODIO Notification Test",
                body="This is a test notification from IKODIO Bug Bounty Platform."
            )
        
        elif channel == "slack" and slack_config:
            service = SlackNotificationService(
                webhook_url=slack_config.webhook_url
            )
            success = await service.send_message(
                message="This is a test notification from IKODIO Bug Bounty Platform.",
                channel=slack_config.channel
            )
        
        elif channel == "discord" and discord_config:
            service = DiscordNotificationService(
                webhook_url=discord_config.webhook_url
            )
            success = await service.send_message(
                message="This is a test notification from IKODIO Bug Bounty Platform.",
                username="IKODIO Bot"
            )
        
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid channel or missing configuration: {channel}"
            )
        
        return {
            "status": "success" if success else "failed",
            "channel": channel,
            "message": "Test notification sent successfully" if success else "Test failed"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Test failed: {str(e)}"
        )
