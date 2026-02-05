"""Schemas for messaging endpoints."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.message import MessageStatus, MessageType, RecipientStatus, SenderChannel


class MessageRecipientBase(BaseModel):
    recipientEmail: Optional[str] = Field(default=None, alias="recipient_email")
    recipientPhone: Optional[str] = Field(default=None, alias="recipient_phone")


class MessageRecipientPublic(MessageRecipientBase):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    status: RecipientStatus
    sentAt: Optional[datetime] = Field(default=None, alias="sent_at")
    deliveredAt: Optional[datetime] = Field(default=None, alias="delivered_at")
    openedAt: Optional[datetime] = Field(default=None, alias="opened_at")
    clickedAt: Optional[datetime] = Field(default=None, alias="clicked_at")
    errorMessage: Optional[str] = Field(default=None, alias="error_message")


class MessageBase(BaseModel):
    title: str
    content: str
    messageType: MessageType = Field(alias="message_type", default=MessageType.EMAIL)
    status: MessageStatus = Field(alias="status", default=MessageStatus.DRAFT)
    scheduledFor: Optional[datetime] = Field(default=None, alias="scheduled_for")
    templateId: Optional[str] = Field(default=None, alias="template_id")
    senderProfileId: Optional[str] = Field(default=None, alias="sender_profile_id")
    senderName: Optional[str] = Field(default=None, alias="sender_name")
    senderEmail: Optional[str] = Field(default=None, alias="sender_email")
    senderPhone: Optional[str] = Field(default=None, alias="sender_phone")
    metadata: dict = Field(default_factory=dict, validation_alias="message_metadata")


class MessageCreate(MessageBase):
    recipientMemberIds: List[str] = Field(default_factory=list, alias="recipient_member_ids")
    recipientOverrideList: List[MessageRecipientBase] = Field(
        default_factory=list, alias="recipient_override_list"
    )


class MessageUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    title: Optional[str] = None
    content: Optional[str] = None
    status: Optional[MessageStatus] = None
    scheduledFor: Optional[datetime] = Field(default=None, alias="scheduled_for")
    senderProfileId: Optional[str] = Field(default=None, alias="sender_profile_id")
    senderName: Optional[str] = Field(default=None, alias="sender_name")
    senderEmail: Optional[str] = Field(default=None, alias="sender_email")
    senderPhone: Optional[str] = Field(default=None, alias="sender_phone")
    metadata: Optional[dict] = Field(default=None, validation_alias="message_metadata")


class MessagePublic(MessageBase):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    createdAt: datetime = Field(alias="created_at")
    updatedAt: datetime = Field(alias="updated_at")
    sentAt: Optional[datetime] = Field(default=None, alias="sent_at")
    recipientCount: int = Field(alias="recipient_count")
    openedCount: int = Field(alias="opened_count")
    clickedCount: int = Field(alias="clicked_count")
    failedCount: int = Field(alias="failed_count")


class MessageListResponse(BaseModel):
    messages: List[MessagePublic]
    pagination: dict


class MessageAnalyticsResponse(BaseModel):
    totalSent: int
    totalDelivered: int
    totalOpened: int
    totalClicked: int
    totalFailed: int
    openRate: float
    clickRate: float


class MessageSenderProfileBase(BaseModel):
    label: str
    channel: SenderChannel
    senderEmail: Optional[str] = Field(default=None, alias="sender_email")
    senderPhone: Optional[str] = Field(default=None, alias="sender_phone")
    isDefault: bool = Field(default=False, alias="is_default")


class MessageSenderProfileCreate(MessageSenderProfileBase):
    pass


class MessageSenderProfileUpdate(BaseModel):
    label: Optional[str] = None
    senderEmail: Optional[str] = Field(default=None, alias="sender_email")
    senderPhone: Optional[str] = Field(default=None, alias="sender_phone")
    isDefault: Optional[bool] = Field(default=None, alias="is_default")


class MessageSenderProfilePublic(MessageSenderProfileBase):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    createdAt: datetime = Field(alias="created_at")
    updatedAt: datetime = Field(alias="updated_at")
    # End of MessageSenderProfilePublic class
