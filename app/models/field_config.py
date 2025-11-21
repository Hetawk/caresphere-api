"""Field configuration models for flexible form management."""

from __future__ import annotations

import enum

from sqlalchemy import JSON, Boolean, Column, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class FieldType(str, enum.Enum):
    """Types of fields that can be configured."""
    TEXT = "text"
    EMAIL = "email"
    PHONE = "phone"
    NUMBER = "number"
    DATE = "date"
    SELECT = "select"  # Dropdown
    MULTISELECT = "multiselect"
    CHECKBOX = "checkbox"
    TEXTAREA = "textarea"
    URL = "url"
    FILE = "file"


class EntityType(str, enum.Enum):
    """Entities that can have configurable fields."""
    MEMBER = "member"
    MESSAGE = "message"
    EVENT = "event"
    DONATION = "donation"
    VOLUNTEER = "volunteer"


class FieldConfiguration(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Defines configurable fields for different entities."""
    __tablename__ = "field_configurations"

    organization_id = Column(String(36), ForeignKey(
        "organizations.id"), nullable=False, index=True)
    entity_type = Column(Enum(EntityType), nullable=False, index=True)
    # Internal key (e.g., "work_school")
    field_key = Column(String(100), nullable=False)
    # Display label (e.g., "Work/School")
    field_label = Column(String(200), nullable=False)
    field_type = Column(Enum(FieldType), nullable=False,
                        default=FieldType.TEXT)
    description = Column(Text)  # Help text for the field
    placeholder = Column(String(200))  # Placeholder text
    options = Column(JSON, default=list)  # For select/multiselect fields
    # Required, min, max, regex, etc.
    validation_rules = Column(JSON, default=dict)
    is_required = Column(Boolean, default=False)
    is_visible = Column(Boolean, default=True)
    is_searchable = Column(Boolean, default=False)
    display_order = Column(Integer, default=0)
    default_value = Column(String(500))
    # For grouping fields (e.g., "Contact Info", "Personal Details")
    group_name = Column(String(100))

    organization = relationship(
        "Organization", backref="field_configurations", lazy="joined")

    def __repr__(self):
        return f"<FieldConfiguration(entity={self.entity_type}, key={self.field_key}, label={self.field_label})>"


class FieldValue(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Stores actual values for configurable fields."""
    __tablename__ = "field_values"

    field_configuration_id = Column(String(36), ForeignKey(
        "field_configurations.id"), nullable=False, index=True)
    entity_type = Column(Enum(EntityType), nullable=False, index=True)
    # ID of the member, message, etc.
    entity_id = Column(String(36), nullable=False, index=True)
    value = Column(Text)  # Stored as text, can be JSON for complex values

    field_configuration = relationship("FieldConfiguration", lazy="joined")

    def __repr__(self):
        return f"<FieldValue(entity={self.entity_type}, entity_id={self.entity_id}, value={self.value[:50]})>"
