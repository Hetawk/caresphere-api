"""Messaging domain models."""

from __future__ import annotations

import enum

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class MessageType(str, enum.Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"


class MessageStatus(str, enum.Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    SENDING = "sending"
    SENT = "sent"
    FAILED = "failed"


class Message(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "messages"

    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    message_type = Column(Enum(MessageType), nullable=False, default=MessageType.EMAIL)
    status = Column(Enum(MessageStatus), nullable=False, default=MessageStatus.DRAFT)
    scheduled_for = Column(DateTime(timezone=True))
    sent_at = Column(DateTime(timezone=True))
    sender_name = Column(String(255))
    sender_email = Column(String(255))
    sender_phone = Column(String(50))
    template_id = Column(String(36), ForeignKey("templates.id"), nullable=True)
    sender_profile_id = Column(String(36), ForeignKey("message_sender_profiles.id"), nullable=True)
    created_by = Column(String(36), ForeignKey("users.id"), nullable=False)

    recipient_count = Column(Integer, nullable=False, default=0)
    opened_count = Column(Integer, nullable=False, default=0)
    clicked_count = Column(Integer, nullable=False, default=0)
    failed_count = Column(Integer, nullable=False, default=0)
    message_metadata = Column("metadata", JSON, default=dict)

    template = relationship("Template", lazy="joined")
    sender_profile = relationship("MessageSenderProfile", lazy="joined")


class RecipientStatus(str, enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    OPENED = "opened"
    CLICKED = "clicked"
    FAILED = "failed"


class MessageRecipient(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "message_recipients"

    message_id = Column(String(36), ForeignKey("messages.id"), nullable=False, index=True)
    member_id = Column(String(36), ForeignKey("members.id"), nullable=True)
    recipient_email = Column(String(255))
    recipient_phone = Column(String(20))
    status = Column(Enum(RecipientStatus), nullable=False, default=RecipientStatus.PENDING)
    sent_at = Column(DateTime(timezone=True))
    delivered_at = Column(DateTime(timezone=True))
    opened_at = Column(DateTime(timezone=True))
    clicked_at = Column(DateTime(timezone=True))
    error_message = Column(Text)
    recipient_metadata = Column("metadata", JSON, default=dict)

    message = relationship("Message", backref="recipients", lazy="joined")


class SenderChannel(str, enum.Enum):
    EMAIL = "email"
    SMS = "sms"


class MessageSenderProfile(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "message_sender_profiles"

    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    label = Column(String(100), nullable=False)
    channel = Column(Enum(SenderChannel), nullable=False)
    sender_email = Column(String(255))
    sender_phone = Column(String(50))
    is_default = Column(Boolean, nullable=False, default=False)

    user = relationship("User", backref="sender_profiles", lazy="joined")
