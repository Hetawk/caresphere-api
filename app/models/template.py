"""Message template models."""

from __future__ import annotations

import enum

from sqlalchemy import Boolean, Column, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class TemplateType(str, enum.Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"


class Template(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "templates"

    name = Column(String(255), nullable=False)
    description = Column(Text)
    template_type = Column(Enum(TemplateType), nullable=False, default=TemplateType.EMAIL)
    category = Column(String(100))
    subject = Column(String(255))
    content = Column(Text, nullable=False)
    variables = Column(String(500))
    thumbnail_url = Column(String(500))
    is_active = Column(Boolean, nullable=False, default=True)
    usage_count = Column(Integer, nullable=False, default=0)
    created_by = Column(String(36), ForeignKey("users.id"), nullable=False)

    creator = relationship("User", lazy="joined")
