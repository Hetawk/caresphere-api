"""Organization/tenant model."""

from __future__ import annotations

from sqlalchemy import Boolean, Column, JSON, String
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class Organization(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "organizations"

    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False)
    domain = Column(String(255), nullable=True)
    settings = Column(JSON, default=dict)
    is_active = Column(Boolean, nullable=False, default=True)

    users = relationship("User", back_populates="organization", cascade="all, delete-orphan", lazy="selectin")
