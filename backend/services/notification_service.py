"""
Notification Service
Email, SMS, Slack, Discord notifications
"""

import asyncio
import aiohttp
from typing import Dict, List, Any, Optional
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class EmailNotificationService:
    """Email notification service"""
    
    def __init__(
        self,
        smtp_host: str,
        smtp_port: int,
        smtp_user: str,
        smtp_password: str,
        from_email: str,
        from_name: str = "IKODIO BugBounty"
    ):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password
        self.from_email = from_email
        self.from_name = from_name
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send email"""
        
        try:
            msg = MIMEMultipart("alternative")
            msg["From"] = f"{self.from_name} <{self.from_email}>"
            msg["To"] = to_email
            msg["Subject"] = subject
            
            if text_body:
                msg.attach(MIMEText(text_body, "plain"))
            
            msg.attach(MIMEText(html_body, "html"))
            
            await asyncio.to_thread(self._send_smtp, msg, to_email)
            
            return {
                "success": True,
                "to": to_email,
                "subject": subject
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _send_smtp(self, msg: MIMEMultipart, to_email: str):
        """Send email via SMTP"""
        with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
            server.starttls()
            server.login(self.smtp_user, self.smtp_password)
            server.send_message(msg)
    
    async def send_vulnerability_alert(
        self,
        to_email: str,
        vulnerability: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Send vulnerability alert email"""
        
        subject = f"[ALERT] {vulnerability.get('severity', 'Unknown').upper()} Vulnerability Detected"
        
        html_body = f"""
        <html>
        <body>
            <h2>Vulnerability Detected</h2>
            <p><strong>Type:</strong> {vulnerability.get('type', 'Unknown')}</p>
            <p><strong>Severity:</strong> {vulnerability.get('severity', 'Unknown')}</p>
            <p><strong>Target:</strong> {vulnerability.get('target_url', 'N/A')}</p>
            <p><strong>Description:</strong></p>
            <p>{vulnerability.get('description', 'No description')}</p>
            <hr>
            <p>View full details in your dashboard.</p>
        </body>
        </html>
        """
        
        return await self.send_email(to_email, subject, html_body)
    
    async def send_scan_complete(
        self,
        to_email: str,
        scan_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Send scan completion email"""
        
        subject = "Scan Completed"
        
        html_body = f"""
        <html>
        <body>
            <h2>Scan Completed Successfully</h2>
            <p><strong>Target:</strong> {scan_result.get('target_url', 'N/A')}</p>
            <p><strong>Duration:</strong> {scan_result.get('duration', 0)} seconds</p>
            <p><strong>Vulnerabilities Found:</strong> {scan_result.get('total_vulnerabilities', 0)}</p>
            <ul>
                <li>Critical: {scan_result.get('critical', 0)}</li>
                <li>High: {scan_result.get('high', 0)}</li>
                <li>Medium: {scan_result.get('medium', 0)}</li>
                <li>Low: {scan_result.get('low', 0)}</li>
            </ul>
            <p>View full report in your dashboard.</p>
        </body>
        </html>
        """
        
        return await self.send_email(to_email, subject, html_body)


class SlackNotificationService:
    """Slack notification service"""
    
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
    
    async def send_message(
        self,
        text: str,
        blocks: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Send Slack message"""
        
        payload = {"text": text}
        if blocks:
            payload["blocks"] = blocks
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.webhook_url, json=payload) as response:
                    return {
                        "success": response.status == 200,
                        "status": response.status
                    }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def send_vulnerability_alert(
        self,
        vulnerability: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Send vulnerability alert to Slack"""
        
        severity = vulnerability.get('severity', 'unknown').upper()
        color = {
            "CRITICAL": "#FF0000",
            "HIGH": "#FF6B00",
            "MEDIUM": "#FFB600",
            "LOW": "#36A64F"
        }.get(severity, "#808080")
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"New Vulnerability: {severity}"
                }
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Type:*\n{vulnerability.get('type', 'Unknown')}"},
                    {"type": "mrkdwn", "text": f"*Severity:*\n{severity}"},
                    {"type": "mrkdwn", "text": f"*Target:*\n{vulnerability.get('target_url', 'N/A')}"},
                    {"type": "mrkdwn", "text": f"*CVSS:*\n{vulnerability.get('cvss_score', 'N/A')}"}
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Description:*\n{vulnerability.get('description', 'No description')}"
                }
            }
        ]
        
        return await self.send_message(
            f"New {severity} vulnerability detected",
            blocks
        )


class DiscordNotificationService:
    """Discord notification service"""
    
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
    
    async def send_message(
        self,
        content: str,
        embeds: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Send Discord message"""
        
        payload = {"content": content}
        if embeds:
            payload["embeds"] = embeds
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.webhook_url, json=payload) as response:
                    return {
                        "success": response.status == 204,
                        "status": response.status
                    }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def send_vulnerability_alert(
        self,
        vulnerability: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Send vulnerability alert to Discord"""
        
        severity = vulnerability.get('severity', 'unknown').upper()
        color = {
            "CRITICAL": 0xFF0000,
            "HIGH": 0xFF6B00,
            "MEDIUM": 0xFFB600,
            "LOW": 0x36A64F
        }.get(severity, 0x808080)
        
        embed = {
            "title": f"New Vulnerability Detected: {severity}",
            "color": color,
            "fields": [
                {"name": "Type", "value": vulnerability.get('type', 'Unknown'), "inline": True},
                {"name": "Severity", "value": severity, "inline": True},
                {"name": "Target", "value": vulnerability.get('target_url', 'N/A'), "inline": False},
                {"name": "Description", "value": vulnerability.get('description', 'No description')[:1024], "inline": False}
            ],
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return await self.send_message(
            f"New {severity} vulnerability detected!",
            [embed]
        )


class NotificationOrchestrator:
    """Orchestrate all notifications"""
    
    def __init__(self, config: Dict[str, Any]):
        self.services = {}
        
        if "email" in config:
            self.services["email"] = EmailNotificationService(**config["email"])
        
        if "slack" in config:
            self.services["slack"] = SlackNotificationService(config["slack"]["webhook_url"])
        
        if "discord" in config:
            self.services["discord"] = DiscordNotificationService(config["discord"]["webhook_url"])
    
    async def notify_vulnerability(
        self,
        vulnerability: Dict[str, Any],
        channels: List[str],
        user_email: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send vulnerability notification to all channels"""
        
        results = {}
        
        if "email" in channels and user_email and "email" in self.services:
            results["email"] = await self.services["email"].send_vulnerability_alert(
                user_email,
                vulnerability
            )
        
        if "slack" in channels and "slack" in self.services:
            results["slack"] = await self.services["slack"].send_vulnerability_alert(
                vulnerability
            )
        
        if "discord" in channels and "discord" in self.services:
            results["discord"] = await self.services["discord"].send_vulnerability_alert(
                vulnerability
            )
        
        return results
    
    async def notify_scan_complete(
        self,
        scan_result: Dict[str, Any],
        user_email: str
    ) -> Dict[str, Any]:
        """Notify when scan is complete"""
        
        if "email" in self.services:
            return await self.services["email"].send_scan_complete(
                user_email,
                scan_result
            )
        
        return {"success": False, "error": "Email service not configured"}
