"""Transactional email service for common automated emails.

This service provides convenience methods for sending transactional emails
like password resets, welcome emails, verification codes, etc.
"""

from __future__ import annotations

import logging
from typing import Optional, Dict, Any

from app.config import settings
from app.services.email_service import email_service, EmailSendError, EmailConfigError

logger = logging.getLogger(__name__)


def get_email_header() -> str:
    """Get the common email header with logo."""
    logo_url = f"{settings.API_BASE_URL}/static/images/logo.png"
    return f"""
    <div style="text-align: center; padding: 20px 0; border-bottom: 1px solid #eee; margin-bottom: 20px;">
        <img src="{logo_url}" alt="{settings.APP_NAME}" style="max-width: 150px; height: auto;" />
    </div>
    """


def get_email_footer() -> str:
    """Get the common email footer."""
    return f"""
    <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #eee; text-align: center; color: #666; font-size: 12px;">
        <p>&copy; 2025 {settings.APP_NAME}. All rights reserved.</p>
        <p style="margin-top: 10px;">
            This email was sent by {settings.APP_NAME}.<br>
            If you have questions, please contact us.
        </p>
    </div>
    """


def wrap_email_body(content: str) -> str:
    """Wrap email content with header, footer, and base styling."""
    return f"""
    <html>
    <body style="font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; background-color: #f9fafb; margin: 0; padding: 0;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; background-color: #ffffff;">
            {get_email_header()}
            {content}
            {get_email_footer()}
        </div>
    </body>
    </html>
    """


class TransactionalEmailService:
    """Service for sending transactional emails via EKDSend API."""

    def __init__(self):
        self.from_email = settings.MSG_SENDER_EMAIL
        self.from_name = settings.MSG_SENDER_NAME

    async def send_welcome_email(
        self,
        to: str,
        user_name: str,
        *,
        login_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Send a welcome email to a new user.

        Args:
            to: Recipient email address
            user_name: User's display name
            login_url: URL to the login page

        Returns:
            Dict with success status and messageId
        """
        subject = f"Welcome to {settings.APP_NAME}!"

        action_button = ""
        if login_url:
            action_button = f'<p style="text-align: center;"><a href="{login_url}" style="display: inline-block; background-color: #2563eb; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px;">Get Started</a></p>'

        content = f"""
        <h1 style="color: #2563eb; margin-bottom: 20px;">Welcome to {settings.APP_NAME}!</h1>
        
        <p>Hi {user_name},</p>
        
        <p>Thank you for joining {settings.APP_NAME}! We're excited to have you as part of our community.</p>
        
        <p>With {settings.APP_NAME}, you can:</p>
        <ul>
            <li>Stay connected with your community</li>
            <li>Receive important updates and announcements</li>
            <li>Access resources and information</li>
        </ul>
        
        {action_button}
        
        <p>If you have any questions, feel free to reach out to us.</p>
        
        <p>Best regards,<br>The {settings.APP_NAME} Team</p>
        """

        body = wrap_email_body(content)

        try:
            result = await email_service.send_email(
                to=to,
                subject=subject,
                body=body,
                from_email=self.from_email,
            )
            logger.info(f"Welcome email sent to {to}")
            return result
        except EmailSendError as e:
            logger.error(f"Failed to send welcome email to {to}: {e}")
            raise

    async def send_password_reset_email(
        self,
        to: str,
        user_name: str,
        reset_token: str,
        reset_url: str,
        *,
        expires_in_hours: int = 24,
    ) -> Dict[str, Any]:
        """
        Send a password reset email.

        Args:
            to: Recipient email address
            user_name: User's display name
            reset_token: Password reset token
            reset_url: Full URL for password reset (including token)
            expires_in_hours: Token expiration time in hours

        Returns:
            Dict with success status and messageId
        """
        subject = f"Reset Your {settings.APP_NAME} Password"

        content = f"""
        <h1 style="color: #2563eb; margin-bottom: 20px;">Password Reset Request</h1>
        
        <p>Hi {user_name},</p>
        
        <p>We received a request to reset your password for your {settings.APP_NAME} account.</p>
        
        <p>Your reset code is:</p>
        
        <div style="text-align: center; margin: 30px 0;">
            <div style="display: inline-block; background-color: #f3f4f6; padding: 20px 40px; border-radius: 8px; font-size: 32px; font-weight: bold; letter-spacing: 8px; color: #2563eb;">
                {reset_token}
            </div>
        </div>
        
        <p style="color: #666; font-size: 14px;">This code will expire in {expires_in_hours} hour(s).</p>
        
        <p>If you didn't request a password reset, you can safely ignore this email. Your password will remain unchanged.</p>
        
        <p>Best regards,<br>The {settings.APP_NAME} Team</p>
        """

        body = wrap_email_body(content)

        try:
            result = await email_service.send_email(
                to=to,
                subject=subject,
                body=body,
                from_email=self.from_email,
            )
            logger.info(f"Password reset email sent to {to}")
            return result
        except EmailSendError as e:
            logger.error(f"Failed to send password reset email to {to}: {e}")
            raise

    async def send_verification_code_email(
        self,
        to: str,
        user_name: str,
        verification_code: str,
        *,
        expires_in_minutes: int = 15,
    ) -> Dict[str, Any]:
        """
        Send a verification code email.

        Args:
            to: Recipient email address
            user_name: User's display name
            verification_code: The verification code
            expires_in_minutes: Code expiration time in minutes

        Returns:
            Dict with success status and messageId
        """
        subject = f"Your {settings.APP_NAME} Verification Code"

        content = f"""
        <h1 style="color: #2563eb; margin-bottom: 20px;">Verification Code</h1>
        
        <p>Hi {user_name},</p>
        
        <p>Your verification code is:</p>
        
        <div style="text-align: center; margin: 30px 0;">
            <div style="display: inline-block; background-color: #f3f4f6; padding: 20px 40px; border-radius: 8px; font-size: 32px; font-weight: bold; letter-spacing: 8px; color: #2563eb;">
                {verification_code}
            </div>
        </div>
        
        <p style="color: #666; font-size: 14px;">This code will expire in {expires_in_minutes} minutes.</p>
        
        <p>If you didn't request this code, please ignore this email.</p>
        
        <p>Best regards,<br>The {settings.APP_NAME} Team</p>
        """

        body = wrap_email_body(content)

        try:
            result = await email_service.send_email(
                to=to,
                subject=subject,
                body=body,
                from_email=self.from_email,
            )
            logger.info(f"Verification code email sent to {to}")
            return result
        except EmailSendError as e:
            logger.error(
                f"Failed to send verification code email to {to}: {e}")
            raise

    async def send_notification_email(
        self,
        to: str,
        user_name: str,
        title: str,
        message: str,
        *,
        action_url: Optional[str] = None,
        action_text: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Send a general notification email.

        Args:
            to: Recipient email address
            user_name: User's display name
            title: Notification title
            message: Notification message (HTML supported)
            action_url: Optional URL for a call-to-action button
            action_text: Text for the action button

        Returns:
            Dict with success status and messageId
        """
        subject = f"{title} - {settings.APP_NAME}"

        action_button = ""
        if action_url and action_text:
            action_button = f"""
            <p style="text-align: center; margin: 30px 0;">
                <a href="{action_url}" style="display: inline-block; background-color: #2563eb; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px;">{action_text}</a>
            </p>
            """

        content = f"""
        <h1 style="color: #2563eb; margin-bottom: 20px;">{title}</h1>
        
        <p>Hi {user_name},</p>
        
        <div style="margin: 20px 0;">
            {message}
        </div>
        
        {action_button}
        
        <p>Best regards,<br>The {settings.APP_NAME} Team</p>
        """

        body = wrap_email_body(content)

        try:
            result = await email_service.send_email(
                to=to,
                subject=subject,
                body=body,
                from_email=self.from_email,
            )
            logger.info(f"Notification email sent to {to}")
            return result
        except EmailSendError as e:
            logger.error(f"Failed to send notification email to {to}: {e}")
            raise

    async def send_sms_verification(
        self,
        to: str,
        verification_code: str,
    ) -> Dict[str, Any]:
        """
        Send an SMS verification code.

        Args:
            to: Recipient phone number in E.164 format
            verification_code: The verification code

        Returns:
            Dict with success status and messageId
        """
        message = f"Your {settings.APP_NAME} verification code is: {verification_code}. Valid for 15 minutes."

        try:
            result = await email_service.send_sms(
                to=to,
                body=message,
            )
            logger.info(f"SMS verification code sent to {to}")
            return result
        except EmailSendError as e:
            logger.error(f"Failed to send SMS verification to {to}: {e}")
            raise


# Global service instance
transactional_email = TransactionalEmailService()


# Convenience functions for direct use
async def send_welcome_email(to: str, user_name: str, **kwargs) -> Dict[str, Any]:
    """Send a welcome email via the global transactional email service."""
    return await transactional_email.send_welcome_email(to, user_name, **kwargs)


async def send_password_reset_email(
    to: str, user_name: str, reset_token: str, reset_url: str, **kwargs
) -> Dict[str, Any]:
    """Send a password reset email via the global transactional email service."""
    return await transactional_email.send_password_reset_email(
        to, user_name, reset_token, reset_url, **kwargs
    )


async def send_verification_code_email(
    to: str, user_name: str, verification_code: str, **kwargs
) -> Dict[str, Any]:
    """Send a verification code email via the global transactional email service."""
    return await transactional_email.send_verification_code_email(
        to, user_name, verification_code, **kwargs
    )


async def send_notification_email(
    to: str, user_name: str, title: str, message: str, **kwargs
) -> Dict[str, Any]:
    """Send a notification email via the global transactional email service."""
    return await transactional_email.send_notification_email(
        to, user_name, title, message, **kwargs
    )


async def send_sms_verification(to: str, verification_code: str) -> Dict[str, Any]:
    """Send an SMS verification code via the global transactional email service."""
    return await transactional_email.send_sms_verification(to, verification_code)
