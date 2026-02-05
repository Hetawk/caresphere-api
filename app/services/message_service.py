"""Messaging services for CRUD, send flow, and sender profiles."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from typing import Iterable, List, Optional, Tuple

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.config import settings
from app.models.member import Member
from app.models.message import (
    Message,
    MessageRecipient,
    MessageSenderProfile,
    MessageStatus,
    MessageType,
    RecipientStatus,
    SenderChannel,
)
from app.models.user import User, UserRole
from app.schemas.message import (
    MessageCreate,
    MessageSenderProfileCreate,
    MessageSenderProfileUpdate,
    MessageUpdate,
)
from app.services import settings_service
from app.services.email_service import email_service, EmailSendError
from app.utils.exceptions import NotFoundError, ValidationError

logger = logging.getLogger(__name__)


def list_messages(
    db: Session,
    *,
    page: int,
    limit: int,
    status_filter: Optional[MessageStatus] = None,
    type_filter: Optional[str] = None,
) -> Tuple[List[Message], int]:
    query = db.query(Message)

    if status_filter:
        query = query.filter(Message.status == status_filter)

    if type_filter:
        query = query.filter(Message.message_type == type_filter)

    total = query.count()
    items = (
        query.order_by(Message.created_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )
    return items, total


def get_message(db: Session, message_id: str) -> Message:
    message = db.get(Message, message_id)
    if not message:
        raise NotFoundError("Message", message_id)
    return message


def create_message(db: Session, payload: MessageCreate, *, current_user: User) -> Message:
    sender_profile = None
    if payload.senderProfileId:
        sender_profile = _get_sender_profile(
            db, payload.senderProfileId, current_user)

    sender_name, sender_email, sender_phone = _resolve_sender_details(
        sender_profile=sender_profile,
        name_override=payload.senderName,
        email_override=payload.senderEmail,
        phone_override=payload.senderPhone,
        db=db,
        current_user=current_user,
    )

    message = Message(
        title=payload.title,
        content=payload.content,
        message_type=payload.messageType,
        status=payload.status,
        scheduled_for=payload.scheduledFor,
        template_id=payload.templateId,
        sender_profile_id=payload.senderProfileId,
        sender_name=sender_name,
        sender_email=sender_email,
        sender_phone=sender_phone,
        message_metadata=payload.metadata,
        created_by=current_user.id,
    )
    db.add(message)
    db.flush()  # so message.id is available

    recipients = _build_recipients(
        db,
        message_id=message.id,
        member_ids=payload.recipientMemberIds,
        overrides=payload.recipientOverrideList,
    )
    db.add_all(recipients)
    message.recipient_count = len(recipients)

    db.commit()
    # refresh recipient_count from DB to ensure any DB defaults or triggers are applied
    from app.models.message import MessageRecipient

    message.recipient_count = (
        db.query(MessageRecipient).filter(
            MessageRecipient.message_id == message.id).count()
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def update_message(db: Session, message_id: str, payload: MessageUpdate) -> Message:
    message = get_message(db, message_id)

    if payload.senderProfileId:
        sender_profile = db.get(MessageSenderProfile, payload.senderProfileId)
        if not sender_profile:
            raise NotFoundError("Sender profile", payload.senderProfileId)
    else:
        sender_profile = None

    update_data = payload.model_dump(exclude_unset=True, by_alias=True)
    if "metadata" in update_data:
        update_data["message_metadata"] = update_data.pop("metadata")
    for key, value in update_data.items():
        setattr(message, key, value)

    if sender_profile or payload.senderName or payload.senderEmail or payload.senderPhone:
        sender_name, sender_email, sender_phone = _resolve_sender_details(
            sender_profile,
            payload.senderName,
            payload.senderEmail,
            payload.senderPhone,
            db=db,
            current_user=None,  # Update messages don't have current_user context
        )
        message.sender_name = sender_name
        message.sender_email = sender_email
        message.sender_phone = sender_phone

    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def delete_message(db: Session, message_id: str) -> None:
    message = get_message(db, message_id)
    db.delete(message)
    db.commit()


async def _send_to_recipient(
    message: Message,
    recipient: MessageRecipient,
) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Send a message to a single recipient via EKDSend API.

    Returns:
        Tuple of (success, message_id, error_message)
    """
    try:
        message_type = message.message_type

        if message_type == MessageType.EMAIL:
            if not recipient.recipient_email:
                return False, None, "No email address for recipient"

            result = await email_service.send_email(
                to=recipient.recipient_email,
                subject=message.title or "No Subject",
                body=message.content,
                from_email=message.sender_email,
            )
            return True, result.get("messageId"), None

        elif message_type == MessageType.SMS:
            if not recipient.recipient_phone:
                return False, None, "No phone number for recipient"

            result = await email_service.send_sms(
                to=recipient.recipient_phone,
                body=message.content,
            )
            return True, result.get("messageId"), None

        elif message_type == MessageType.PUSH:
            # Push notifications handled separately (not via EKDSend)
            logger.info(
                f"Push notification for recipient {recipient.id} - not yet implemented")
            return True, None, None

        else:
            return False, None, f"Unsupported message type: {message_type}"

    except EmailSendError as e:
        logger.error(
            f"Failed to send message to recipient {recipient.id}: {e}")
        return False, None, str(e)
    except Exception as e:
        logger.exception(
            f"Unexpected error sending to recipient {recipient.id}")
        return False, None, f"Unexpected error: {str(e)}"


def send_message(db: Session, message_id: str) -> Message:
    """
    Send a message to all its recipients via EKDSend API.

    This function:
    1. Updates message status to SENDING
    2. Sends to each recipient via EKDSend (email/SMS)
    3. Updates recipient statuses based on API response
    4. Updates message status to SENT or PARTIALLY_SENT
    """
    message = get_message(db, message_id)
    message.status = MessageStatus.SENDING
    db.add(message)
    db.commit()

    now = datetime.utcnow()
    success_count = 0
    failed_count = 0

    # Run the async sending in a sync context
    async def send_all():
        nonlocal success_count, failed_count
        for recipient in message.recipients:
            success, ext_message_id, error = await _send_to_recipient(message, recipient)

            if success:
                recipient.status = RecipientStatus.SENT
                recipient.sent_at = datetime.utcnow()
                # Store external message ID in metadata if returned
                if ext_message_id:
                    recipient.recipient_metadata = recipient.recipient_metadata or {}
                    recipient.recipient_metadata["ekdsend_message_id"] = ext_message_id
                success_count += 1
                logger.info(
                    f"Successfully sent to {recipient.recipient_email or recipient.recipient_phone}")
            else:
                recipient.status = RecipientStatus.FAILED
                recipient.error_message = error
                failed_count += 1
                logger.warning(
                    f"Failed to send to recipient {recipient.id}: {error}")

            db.add(recipient)

    # Execute async sending
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If we're already in an async context, create a task
            asyncio.ensure_future(send_all())
        else:
            loop.run_until_complete(send_all())
    except RuntimeError:
        # No event loop, create a new one
        asyncio.run(send_all())

    # Update message status based on results
    if failed_count == 0:
        message.status = MessageStatus.SENT
    elif success_count == 0:
        message.status = MessageStatus.FAILED
    else:
        # Some succeeded, some failed
        message.status = MessageStatus.SENT  # Consider as sent if any succeeded

    message.sent_at = now
    message.recipient_count = len(message.recipients)
    db.add(message)
    db.commit()
    db.refresh(message)

    logger.info(
        f"Message {message_id} sending complete: "
        f"{success_count} succeeded, {failed_count} failed"
    )

    return message


def get_message_analytics(db: Session, message_id: str) -> dict:
    message = get_message(db, message_id)
    total_sent = len(message.recipients)
    total_opened = sum(1 for r in message.recipients if r.status in {
                       RecipientStatus.OPENED, RecipientStatus.CLICKED})
    total_clicked = sum(
        1 for r in message.recipients if r.status == RecipientStatus.CLICKED)
    total_failed = sum(
        1 for r in message.recipients if r.status == RecipientStatus.FAILED)
    total_delivered = total_sent - total_failed

    open_rate = (total_opened / total_sent * 100) if total_sent else 0
    click_rate = (total_clicked / total_sent * 100) if total_sent else 0

    return {
        "totalSent": total_sent,
        "totalDelivered": total_delivered,
        "totalOpened": total_opened,
        "totalClicked": total_clicked,
        "totalFailed": total_failed,
        "openRate": round(open_rate, 2),
        "clickRate": round(click_rate, 2),
    }


def list_sender_profiles(db: Session, *, current_user: User) -> List[MessageSenderProfile]:
    query = db.query(MessageSenderProfile)
    if current_user.role == UserRole.SUPER_ADMIN:
        return query.order_by(MessageSenderProfile.created_at.desc()).all()
    return (
        query.filter(MessageSenderProfile.user_id == current_user.id)
        .order_by(MessageSenderProfile.created_at.desc())
        .all()
    )


def create_sender_profile(
    db: Session,
    payload: MessageSenderProfileCreate,
    *,
    current_user: User,
) -> MessageSenderProfile:
    _validate_sender_payload(payload)
    if payload.isDefault:
        # Clear any existing defaults first so our new profile can be the true default
        _clear_other_defaults(db, current_user.id, payload.channel)

    profile = MessageSenderProfile(
        user_id=current_user.id,
        label=payload.label,
        channel=payload.channel,
        sender_email=payload.senderEmail,
        sender_phone=payload.senderPhone,
        is_default=payload.isDefault,
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


def update_sender_profile(
    db: Session,
    profile_id: str,
    payload: MessageSenderProfileUpdate,
    *,
    current_user: User,
) -> MessageSenderProfile:
    profile = _get_sender_profile(db, profile_id, current_user)
    update_data = payload.model_dump(exclude_unset=True, by_alias=True)
    for key, value in update_data.items():
        setattr(profile, key, value)
    if payload.isDefault:
        _clear_other_defaults(db, current_user.id, profile.channel)
    _validate_sender_payload(profile)
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


def delete_sender_profile(db: Session, profile_id: str, *, current_user: User) -> None:
    profile = _get_sender_profile(db, profile_id, current_user)
    db.delete(profile)
    db.commit()


def _clear_other_defaults(db: Session, user_id: str, channel: SenderChannel) -> None:
    (
        db.query(MessageSenderProfile)
        .filter(
            MessageSenderProfile.user_id == user_id,
            MessageSenderProfile.channel == channel,
            MessageSenderProfile.is_default.is_(True),
        )
        .update({"is_default": False})
    )


def _validate_sender_payload(
    payload: MessageSenderProfileCreate | MessageSenderProfileUpdate | MessageSenderProfile,
) -> None:
    channel = getattr(payload, "channel", None)
    sender_email = getattr(payload, "senderEmail", None)
    sender_phone = getattr(payload, "senderPhone", None)

    if isinstance(payload, MessageSenderProfile):
        channel = payload.channel
        sender_email = payload.sender_email
        sender_phone = payload.sender_phone

    if channel == SenderChannel.EMAIL and not sender_email:
        raise ValidationError(
            {"senderEmail": "Email sender is required for email channel"})

    if channel == SenderChannel.SMS and not sender_phone:
        raise ValidationError(
            {"senderPhone": "Phone sender is required for SMS channel"})


def _get_sender_profile(db: Session, profile_id: str, current_user: User) -> MessageSenderProfile:
    profile = db.get(MessageSenderProfile, profile_id)
    if not profile:
        raise NotFoundError("Sender profile", profile_id)
    if profile.user_id != current_user.id and current_user.role != UserRole.SUPER_ADMIN:
        raise ValidationError(
            {"senderProfileId": "You do not have access to this profile"})
    return profile


def _resolve_sender_details(
    sender_profile: MessageSenderProfile | None,
    name_override: Optional[str],
    email_override: Optional[str],
    phone_override: Optional[str],
    *,
    db: Session = None,
    current_user: User = None,
) -> Tuple[str, str, str]:
    # Use overrides first
    if name_override and email_override and phone_override:
        return name_override, email_override, phone_override

    # Try sender profile next
    profile_name = sender_profile.label if sender_profile else None
    profile_email = sender_profile.sender_email if sender_profile and sender_profile.sender_email else None
    profile_phone = sender_profile.sender_phone if sender_profile and sender_profile.sender_phone else None

    # Get resolved settings as fallback
    fallback_name, fallback_email, fallback_phone = settings.MSG_SENDER_NAME, settings.MSG_SENDER_EMAIL, settings.MSG_SENDER_PHONE
    if db and current_user:
        try:
            fallback_name, fallback_email, fallback_phone, _ = settings_service.get_resolved_sender_settings(
                db, current_user)
        except Exception:
            # Fall back to env settings if there's any issue
            pass

    sender_name = name_override or profile_name or fallback_name
    sender_email = email_override or profile_email or fallback_email
    sender_phone = phone_override or profile_phone or fallback_phone

    return sender_name, sender_email, sender_phone


def _build_recipients(
    db: Session,
    *,
    message_id: str,
    member_ids: Iterable[str],
    overrides: Iterable[dict],
) -> List[MessageRecipient]:
    recipients: List[MessageRecipient] = []
    for member_id in member_ids:
        member = db.get(Member, member_id)
        if not member:
            continue
        recipients.append(
            MessageRecipient(
                message_id=message_id,
                member_id=member_id,
                recipient_email=member.email,
                recipient_phone=member.phone,
            )
        )

    for override in overrides:
        override_data = (
            override
            if isinstance(override, dict)
            else override.model_dump(exclude_none=True, by_alias=True)
        )
        recipients.append(
            MessageRecipient(
                message_id=message_id,
                recipient_email=override_data.get("recipient_email")
                or override_data.get("recipientEmail"),
                recipient_phone=override_data.get("recipient_phone")
                or override_data.get("recipientPhone"),
            )
        )
    return recipients
