"""Email service for sending emails via EKDSend API."""

from __future__ import annotations

import httpx
from typing import List, Optional, Dict, Any
import logging

from app.config import settings

logger = logging.getLogger(__name__)

# EKDSend API Configuration
EKDSEND_API_URL = "https://es.ekddigital.com/api/v1"


class EmailService:
    """Service for sending emails via EKDSend API."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the email service with an API key."""
        self.api_key = api_key or getattr(settings, 'EKDSEND_API_KEY', None)
        self.api_url = getattr(settings, 'EKDSEND_API_URL', EKDSEND_API_URL)

    async def send_email(
        self,
        to: str | List[str],
        subject: str,
        body: str,
        *,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        reply_to: Optional[str] = None,
        template: Optional[str] = None,
        template_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Send an email via EKDSend API.

        Args:
            to: Recipient email address(es)
            subject: Email subject line
            body: Email body content (HTML supported)
            from_email: Custom sender email (requires verified domain)
            from_name: Custom sender name
            cc: Carbon copy recipients
            bcc: Blind carbon copy recipients
            reply_to: Reply-to email address
            template: Built-in template name (welcome, verification, etc.)
            template_data: Variables for template substitution

        Returns:
            Dict with success status and messageId

        Raises:
            EmailSendError: If the API request fails
        """
        if not self.api_key:
            raise EmailConfigError("EKDSEND_API_KEY is not configured")

        # Build the request payload
        payload: Dict[str, Any] = {
            "type": "email",
            "to": to,
        }

        # Add subject and body for non-template emails
        if template:
            payload["template"] = template
            if template_data:
                payload["templateData"] = template_data
        else:
            payload["subject"] = subject
            payload["body"] = body

        # Optional fields
        if from_email:
            payload["from"] = from_email
        if cc:
            payload["cc"] = cc
        if bcc:
            payload["bcc"] = bcc
        if reply_to:
            payload["replyTo"] = reply_to

        # Make the API request
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.api_url}/send",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                    timeout=30.0,
                )

                result = response.json()

                if response.status_code == 202 and result.get("success"):
                    logger.info(
                        f"Email queued successfully. MessageId: {result.get('messageId')}"
                    )
                    return {
                        "success": True,
                        "messageId": result.get("messageId"),
                        "queuedAt": result.get("queuedAt"),
                    }
                else:
                    error_msg = result.get("error", {}).get(
                        "message", "Unknown error")
                    error_code = result.get("error", {}).get("code", "UNKNOWN")
                    logger.error(
                        f"Email send failed: {error_code} - {error_msg}")
                    raise EmailSendError(error_msg, code=error_code)

            except httpx.TimeoutException:
                logger.error("Email API request timed out")
                raise EmailSendError("Request timed out", code="TIMEOUT")
            except httpx.RequestError as e:
                logger.error(f"Email API request failed: {e}")
                raise EmailSendError(str(e), code="REQUEST_ERROR")

    async def send_sms(
        self,
        to: str | List[str],
        body: str,
    ) -> Dict[str, Any]:
        """
        Send an SMS via EKDSend API.

        Args:
            to: Recipient phone number(s) in E.164 format
            body: SMS message content

        Returns:
            Dict with success status and messageId
        """
        if not self.api_key:
            raise EmailConfigError("EKDSEND_API_KEY is not configured")

        payload = {
            "type": "sms",
            "to": to,
            "body": body,
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.api_url}/send",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                    timeout=30.0,
                )

                result = response.json()

                if response.status_code == 202 and result.get("success"):
                    logger.info(
                        f"SMS queued successfully. MessageId: {result.get('messageId')}"
                    )
                    return {
                        "success": True,
                        "messageId": result.get("messageId"),
                        "queuedAt": result.get("queuedAt"),
                    }
                else:
                    error_msg = result.get("error", {}).get(
                        "message", "Unknown error")
                    error_code = result.get("error", {}).get("code", "UNKNOWN")
                    logger.error(
                        f"SMS send failed: {error_code} - {error_msg}")
                    raise EmailSendError(error_msg, code=error_code)

            except httpx.TimeoutException:
                logger.error("SMS API request timed out")
                raise EmailSendError("Request timed out", code="TIMEOUT")
            except httpx.RequestError as e:
                logger.error(f"SMS API request failed: {e}")
                raise EmailSendError(str(e), code="REQUEST_ERROR")

    async def send_voice(
        self,
        to: str,
        body: str,
    ) -> Dict[str, Any]:
        """
        Send a voice call via EKDSend API.

        Args:
            to: Recipient phone number in E.164 format
            body: Text to be spoken during the call

        Returns:
            Dict with success status and messageId
        """
        if not self.api_key:
            raise EmailConfigError("EKDSEND_API_KEY is not configured")

        payload = {
            "type": "voice",
            "to": to,
            "body": body,
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.api_url}/send",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                    timeout=30.0,
                )

                result = response.json()

                if response.status_code == 202 and result.get("success"):
                    logger.info(
                        f"Voice call queued successfully. MessageId: {result.get('messageId')}"
                    )
                    return {
                        "success": True,
                        "messageId": result.get("messageId"),
                        "queuedAt": result.get("queuedAt"),
                    }
                else:
                    error_msg = result.get("error", {}).get(
                        "message", "Unknown error")
                    error_code = result.get("error", {}).get("code", "UNKNOWN")
                    logger.error(
                        f"Voice call failed: {error_code} - {error_msg}")
                    raise EmailSendError(error_msg, code=error_code)

            except httpx.TimeoutException:
                logger.error("Voice API request timed out")
                raise EmailSendError("Request timed out", code="TIMEOUT")
            except httpx.RequestError as e:
                logger.error(f"Voice API request failed: {e}")
                raise EmailSendError(str(e), code="REQUEST_ERROR")


class EmailConfigError(Exception):
    """Raised when email configuration is missing or invalid."""
    pass


class EmailSendError(Exception):
    """Raised when email sending fails."""

    def __init__(self, message: str, code: str = "UNKNOWN"):
        super().__init__(message)
        self.code = code


# Global service instance (can be configured at startup)
email_service = EmailService()


# Convenience functions for direct use
async def send_email(
    to: str | List[str],
    subject: str,
    body: str,
    **kwargs
) -> Dict[str, Any]:
    """Send an email via the global email service."""
    return await email_service.send_email(to, subject, body, **kwargs)


async def send_sms(
    to: str | List[str],
    body: str,
) -> Dict[str, Any]:
    """Send an SMS via the global email service."""
    return await email_service.send_sms(to, body)


async def send_voice(
    to: str,
    body: str,
) -> Dict[str, Any]:
    """Send a voice call via the global email service."""
    return await email_service.send_voice(to, body)
