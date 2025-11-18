"""Shared SQLAlchemy mixins and base utilities."""

from __future__ import annotations

import uuid

from sqlalchemy import Column, DateTime, func
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import declared_attr


class UUIDPrimaryKeyMixin:
    """Adds a string based UUID primary key."""

    @declared_attr
    def id(cls):  # type: ignore[override]
        return Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))


class TimestampMixin:
    """Adds created_at/updated_at timestamps."""

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
