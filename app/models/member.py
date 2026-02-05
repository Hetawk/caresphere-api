"""Member domain model."""

from __future__ import annotations

import enum

from sqlalchemy import JSON, Boolean, Column, Date, Enum, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class Gender(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"


class MemberStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    ARCHIVED = "archived"


class Member(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "members"

    organization_id = Column(String(36), ForeignKey(
        "organizations.id"), nullable=True, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), index=True)
    phone = Column(String(20))
    date_of_birth = Column(Date)
    gender = Column(Enum(Gender))
    address = Column(Text)
    city = Column(String(100))
    state = Column(String(100))
    zip_code = Column(String(20))
    country = Column(String(100))
    member_status = Column(
        Enum(MemberStatus), nullable=False, default=MemberStatus.ACTIVE)
    membership_type = Column(String(50))
    join_date = Column(Date)
    photo_url = Column(String(500))
    notes = Column(Text)
    tags = Column(JSON, default=list)
    custom_fields = Column(JSON, default=dict)
    created_by = Column(String(36), ForeignKey("users.id"))

    # Additional fields from CSV import
    work_school = Column(String(200))  # Work or School information
    whatsapp_number = Column(String(20))  # WhatsApp contact
    wechat_id = Column(String(100))  # WeChat ID
    hear_about_us = Column(Text)  # How they heard about the organization
    involvement = Column(Text)  # Ministries/groups they want to join
    comments = Column(Text)  # Additional comments
    consent_given = Column(Boolean, default=False)  # Data consent

    creator = relationship("User", foreign_keys=[
                           created_by], lazy="joined", viewonly=True)


class MemberNote(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "member_notes"

    member_id = Column(String(36), ForeignKey(
        "members.id"), nullable=False, index=True)
    note = Column(Text, nullable=False)
    note_type = Column(String(50))
    is_private = Column(Boolean, nullable=False, default=False)
    created_by = Column(String(36), ForeignKey("users.id"))

    member = relationship("Member", backref="member_notes", lazy="joined")
    creator = relationship("User", foreign_keys=[created_by], lazy="joined")


class MemberActivity(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "member_activities"

    member_id = Column(String(36), ForeignKey(
        "members.id"), nullable=False, index=True)
    activity_type = Column(String(50), nullable=False)
    description = Column(Text)
    activity_metadata = Column("metadata", JSON, default=dict)
    created_by = Column(String(36), ForeignKey("users.id"))

    member = relationship("Member", backref="activities", lazy="joined")
    creator = relationship("User", foreign_keys=[created_by], lazy="joined")
