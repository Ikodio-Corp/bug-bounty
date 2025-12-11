"""
Email Notification Client
"""

import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
from jinja2 import Template

from core.config import settings


class EmailClient:
    """Email notification client"""
    
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.FROM_EMAIL
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        plain_body: Optional[str] = None
    ) -> bool:
        """Send an email"""
        
        try:
            message = MIMEMultipart("alternative")
            message["From"] = self.from_email
            message["To"] = to_email
            message["Subject"] = subject
            
            if plain_body:
                message.attach(MIMEText(plain_body, "plain"))
            
            message.attach(MIMEText(html_body, "html"))
            
            await aiosmtplib.send(
                message,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.smtp_user,
                password=self.smtp_password,
                use_tls=True
            )
            
            return True
        
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False


async def send_verification_email(email: str, token: str, username: str) -> bool:
    """Send email verification link"""
    client = EmailClient()
    
    verification_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"
    
    subject = "Verify Your Ikodio Account"
    
    html_body = f"""
    <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #1a1a1a 0%, #000000 100%); padding: 40px; border-radius: 10px; text-align: center;">
                <h1 style="color: #ffffff; margin-bottom: 10px;">Welcome to Ikodio!</h1>
                <p style="color: #cccccc; margin-bottom: 30px;">Hi {username},</p>
                <p style="color: #ffffff; margin-bottom: 30px;">
                    Thank you for registering with Ikodio Bug Bounty Platform. 
                    Please verify your email address to complete your registration.
                </p>
                <a href="{verification_url}" 
                   style="display: inline-block; background-color: #ffffff; color: #000000; 
                          padding: 15px 40px; text-decoration: none; border-radius: 5px; 
                          font-weight: bold; margin: 20px 0;">
                    Verify Email Address
                </a>
                <p style="color: #999999; font-size: 12px; margin-top: 30px;">
                    This link will expire in 24 hours.
                </p>
                <p style="color: #999999; font-size: 12px;">
                    If you didn't create an account, please ignore this email.
                </p>
            </div>
        </body>
    </html>
    """
    
    plain_body = f"""
    Welcome to Ikodio!
    
    Hi {username},
    
    Thank you for registering with Ikodio Bug Bounty Platform.
    Please verify your email address by visiting:
    
    {verification_url}
    
    This link will expire in 24 hours.
    
    If you didn't create an account, please ignore this email.
    """
    
    return await client.send_email(email, subject, html_body, plain_body)
    
    async def send_bug_validated_email(
        self,
        to_email: str,
        bug_title: str,
        bug_id: int,
        bounty_amount: float
    ) -> bool:
        """Send bug validated notification"""
        
        subject = f"Bug Validated: {bug_title}"
        
        html_body = f"""
        <html>
            <body>
                <h2>Congratulations!</h2>
                <p>Your bug report has been validated.</p>
                <h3>{bug_title}</h3>
                <p><strong>Bug ID:</strong> #{bug_id}</p>
                <p><strong>Bounty Amount:</strong> ${bounty_amount}</p>
                <p>The bounty will be processed within 5 business days.</p>
                <p><a href="{settings.FRONTEND_URL}/bugs/{bug_id}">View Bug Report</a></p>
            </body>
        </html>
        """
        
        return await self.send_email(to_email, subject, html_body)
    
    async def send_scan_complete_email(
        self,
        to_email: str,
        scan_id: int,
        target_url: str,
        vulnerabilities_found: int
    ) -> bool:
        """Send scan completion notification"""
        
        subject = f"Scan Complete: {target_url}"
        
        html_body = f"""
        <html>
            <body>
                <h2>Security Scan Complete</h2>
                <p>Your security scan has finished.</p>
                <p><strong>Target:</strong> {target_url}</p>
                <p><strong>Vulnerabilities Found:</strong> {vulnerabilities_found}</p>
                <p><a href="{settings.FRONTEND_URL}/scans/{scan_id}">View Scan Results</a></p>
            </body>
        </html>
        """
        
        return await self.send_email(to_email, subject, html_body)
    
    async def send_marketplace_purchase_email(
        self,
        to_email: str,
        listing_title: str,
        price: float,
        transaction_id: str
    ) -> bool:
        """Send marketplace purchase confirmation"""
        
        subject = f"Purchase Confirmation: {listing_title}"
        
        html_body = f"""
        <html>
            <body>
                <h2>Purchase Successful</h2>
                <p>Thank you for your purchase!</p>
                <h3>{listing_title}</h3>
                <p><strong>Amount Paid:</strong> ${price}</p>
                <p><strong>Transaction ID:</strong> {transaction_id}</p>
                <p><a href="{settings.FRONTEND_URL}/marketplace">Browse More Items</a></p>
            </body>
        </html>
        """
        
        return await self.send_email(to_email, subject, html_body)
    
    async def send_guild_invitation_email(
        self,
        to_email: str,
        guild_name: str,
        guild_id: int,
        inviter_name: str
    ) -> bool:
        """Send guild invitation"""
        
        subject = f"Guild Invitation: {guild_name}"
        
        html_body = f"""
        <html>
            <body>
                <h2>You've Been Invited!</h2>
                <p>{inviter_name} has invited you to join {guild_name}.</p>
                <p><a href="{settings.FRONTEND_URL}/guilds/{guild_id}">View Guild</a></p>
            </body>
        </html>
        """
        
        return await self.send_email(to_email, subject, html_body)
    
    async def send_password_reset_email(
        self,
        to_email: str,
        reset_token: str
    ) -> bool:
        """Send password reset email"""
        
        subject = "Password Reset Request"
        
        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
        
        html_body = f"""
        <html>
            <body>
                <h2>Password Reset</h2>
                <p>You requested a password reset.</p>
                <p>Click the link below to reset your password:</p>
                <p><a href="{reset_url}">Reset Password</a></p>
                <p>This link expires in 1 hour.</p>
                <p>If you didn't request this, please ignore this email.</p>
            </body>
        </html>
        """
        
        return await self.send_email(to_email, subject, html_body)
    
    async def send_welcome_email(
        self,
        to_email: str,
        username: str
    ) -> bool:
        """Send welcome email to new users"""
        
        subject = "Welcome to Ikodio Bug Bounty Platform"
        
        html_body = f"""
        <html>
            <body>
                <h2>Welcome, {username}!</h2>
                <p>Thank you for joining Ikodio Bug Bounty Platform.</p>
                <h3>Get Started:</h3>
                <ul>
                    <li>Report your first bug and earn bounties</li>
                    <li>Run AI-powered security scans</li>
                    <li>Join a security guild</li>
                    <li>Browse the marketplace</li>
                </ul>
                <p><a href="{settings.FRONTEND_URL}/dashboard">Go to Dashboard</a></p>
            </body>
        </html>
        """
        
        return await self.send_email(to_email, subject, html_body)
    
    async def send_deletion_reminder(
        self,
        to_email: str,
        user_name: str,
        days_remaining: int,
        deletion_date
    ) -> bool:
        """Send account deletion reminder"""
        
        from datetime import datetime
        
        subject = f"Account Deletion in {days_remaining} Days"
        
        deletion_date_str = deletion_date.strftime("%B %d, %Y at %H:%M UTC")
        cancel_url = f"{settings.FRONTEND_URL}/account/cancel-deletion"
        
        html_body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background-color: #fff3cd; border: 2px solid #ffc107; padding: 30px; border-radius: 10px;">
                    <h2 style="color: #856404; margin-bottom: 20px;">Account Deletion Reminder</h2>
                    <p style="color: #856404; font-size: 16px;">Hi {user_name},</p>
                    <p style="color: #856404; font-size: 16px; margin: 20px 0;">
                        Your IKODIO account is scheduled for permanent deletion in <strong>{days_remaining} day(s)</strong>.
                    </p>
                    <p style="color: #856404; font-size: 16px; margin: 20px 0;">
                        <strong>Deletion Date:</strong> {deletion_date_str}
                    </p>
                    <div style="background-color: #fff; padding: 20px; border-radius: 5px; margin: 20px 0;">
                        <h3 style="color: #dc3545; margin-top: 0;">What will be deleted:</h3>
                        <ul style="color: #333;">
                            <li>Your profile and personal information</li>
                            <li>All bug reports and scan history</li>
                            <li>Marketplace transactions and listings</li>
                            <li>Guild memberships and contributions</li>
                            <li>All associated data</li>
                        </ul>
                    </div>
                    <p style="color: #856404; font-size: 16px; margin: 20px 0;">
                        <strong>This action cannot be undone after the deletion date.</strong>
                    </p>
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{cancel_url}" 
                           style="display: inline-block; background-color: #28a745; color: #ffffff; 
                                  padding: 15px 40px; text-decoration: none; border-radius: 5px; 
                                  font-weight: bold; font-size: 16px;">
                            Cancel Account Deletion
                        </a>
                    </div>
                    <p style="color: #6c757d; font-size: 12px; text-align: center;">
                        If you want to keep your account, click the button above before {deletion_date_str}.
                    </p>
                </div>
            </body>
        </html>
        """
        
        plain_body = f"""
        Account Deletion Reminder
        
        Hi {user_name},
        
        Your IKODIO account is scheduled for permanent deletion in {days_remaining} day(s).
        
        Deletion Date: {deletion_date_str}
        
        What will be deleted:
        - Your profile and personal information
        - All bug reports and scan history
        - Marketplace transactions and listings
        - Guild memberships and contributions
        - All associated data
        
        This action cannot be undone after the deletion date.
        
        To cancel the deletion, visit: {cancel_url}
        
        If you want to keep your account, please act before {deletion_date_str}.
        """
        
        return await self.send_email(to_email, subject, html_body, plain_body)

