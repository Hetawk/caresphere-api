"""Pydantic schemas for sender settings management."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.setting import SettingScope


class SenderSettingBase(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    senderName: Optional[str] = Field(default=None, alias="sender_name")
    senderEmail: Optional[str] = Field(default=None, alias="sender_email")
    senderPhone: Optional[str] = Field(default=None, alias="sender_phone")


class SenderSettingCreate(SenderSettingBase):
    scope: SettingScope
    referenceId: Optional[str] = Field(default=None, alias="reference_id")


class SenderSettingUpdate(SenderSettingBase):
    pass


class SenderSettingPublic(SenderSettingBase):
    id: str
    scope: SettingScope
    referenceId: Optional[str] = Field(default=None, alias="reference_id")
    createdAt: datetime = Field(alias="created_at")
    updatedAt: datetime = Field(alias="updated_at")


class ResolvedSenderSettings(BaseModel):
    """The final resolved sender settings with source information."""
    
    senderName: str
    senderEmail: str
    senderPhone: str
    source: str  # "user", "organization", "global", or "environment"
    layers: dict  # Shows which values came from which scopes