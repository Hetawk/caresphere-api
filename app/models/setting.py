"""Configurable sender settings supporting multiple scopes."""

from __future__ import annotations

import enum

from sqlalchemy import Column, Enum, String, UniqueConstraint

from app.database import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class SettingScope(str, enum.Enum):
    GLOBAL = "global"
    ORGANIZATION = "organization"
    USER = "user"


class SenderSetting(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "sender_settings"
    __table_args__ = (
        UniqueConstraint("scope", "reference_id", name="uq_sender_settings_scope_ref"),
    )

    scope = Column(Enum(SettingScope), nullable=False)
    reference_id = Column(String(36), nullable=True)
    sender_name = Column(String(255), nullable=True)
    sender_email = Column(String(255), nullable=True)
    sender_phone = Column(String(50), nullable=True)
