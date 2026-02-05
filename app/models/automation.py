"""Automation rule models."""

from __future__ import annotations

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class AutomationRule(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "automation_rules"

    name = Column(String(255), nullable=False)
    description = Column(Text)
    trigger_type = Column(String(50), nullable=False)
    trigger_config = Column(JSON, default=dict)
    action_type = Column(String(50), nullable=False)
    action_config = Column(JSON, default=dict)
    conditions = Column(JSON, default=dict)
    is_active = Column(Boolean, nullable=False, default=True)
    last_run_at = Column(DateTime(timezone=True))
    run_count = Column(Integer, nullable=False, default=0)
    success_count = Column(Integer, nullable=False, default=0)
    failure_count = Column(Integer, nullable=False, default=0)
    created_by = Column(String(36), ForeignKey("users.id"), nullable=False)

    creator = relationship("User", lazy="joined")


class AutomationLog(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "automation_logs"

    rule_id = Column(String(36), ForeignKey("automation_rules.id"), nullable=False, index=True)
    status = Column(String(20), nullable=False)
    trigger_data = Column(JSON, default=dict)
    action_result = Column(JSON, default=dict)
    error_message = Column(Text)
    execution_time_ms = Column(Integer)
    executed_at = Column(DateTime(timezone=True))

    rule = relationship("AutomationRule", backref="logs", lazy="joined")
