"""Schemas for field configuration management."""

from __future__ import annotations

from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.field_config import EntityType, FieldType


# Base schemas
class FieldConfigurationBase(BaseModel):
    """Base schema for field configuration."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    entityType: EntityType = Field(alias="entity_type")
    fieldKey: str = Field(alias="field_key", min_length=1, max_length=100)
    fieldLabel: str = Field(alias="field_label", min_length=1, max_length=200)
    fieldType: FieldType = Field(alias="field_type")
    description: Optional[str] = None
    placeholder: Optional[str] = None
    options: List[str] = Field(default_factory=list)
    validationRules: dict = Field(
        default_factory=dict, alias="validation_rules")
    isRequired: bool = Field(default=False, alias="is_required")
    isVisible: bool = Field(default=True, alias="is_visible")
    isSearchable: bool = Field(default=False, alias="is_searchable")
    displayOrder: int = Field(default=0, alias="display_order")
    defaultValue: Optional[str] = Field(default=None, alias="default_value")
    groupName: Optional[str] = Field(default=None, alias="group_name")


class FieldConfigurationCreate(FieldConfigurationBase):
    """Schema for creating a field configuration."""
    pass


class FieldConfigurationUpdate(BaseModel):
    """Schema for updating a field configuration."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    fieldLabel: Optional[str] = Field(default=None, alias="field_label")
    fieldType: Optional[FieldType] = Field(default=None, alias="field_type")
    description: Optional[str] = None
    placeholder: Optional[str] = None
    options: Optional[List[str]] = None
    validationRules: Optional[dict] = Field(
        default=None, alias="validation_rules")
    isRequired: Optional[bool] = Field(default=None, alias="is_required")
    isVisible: Optional[bool] = Field(default=None, alias="is_visible")
    isSearchable: Optional[bool] = Field(default=None, alias="is_searchable")
    displayOrder: Optional[int] = Field(default=None, alias="display_order")
    defaultValue: Optional[str] = Field(default=None, alias="default_value")
    groupName: Optional[str] = Field(default=None, alias="group_name")


class FieldConfigurationPublic(FieldConfigurationBase):
    """Schema for field configuration responses."""
    id: str
    organizationId: str = Field(alias="organization_id")
    createdAt: datetime = Field(alias="created_at")
    updatedAt: datetime = Field(alias="updated_at")


class FieldValueBase(BaseModel):
    """Base schema for field values."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    fieldConfigurationId: str = Field(alias="field_configuration_id")
    value: Optional[str] = None


class FieldValueCreate(FieldValueBase):
    """Schema for creating a field value."""
    pass


class FieldValueUpdate(BaseModel):
    """Schema for updating a field value."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    value: Optional[str] = None


class FieldValuePublic(FieldValueBase):
    """Schema for field value responses."""
    id: str
    entityType: EntityType = Field(alias="entity_type")
    entityId: str = Field(alias="entity_id")
    createdAt: datetime = Field(alias="created_at")
    updatedAt: datetime = Field(alias="updated_at")


class EntityFieldsResponse(BaseModel):
    """Response containing all field configurations and values for an entity."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    configs: List[FieldConfigurationPublic]
    values: dict[str, Any] = Field(default_factory=dict)  # field_key -> value


class BulkFieldValuesUpdate(BaseModel):
    """Schema for bulk updating field values."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    entityType: EntityType = Field(alias="entity_type")
    entityId: str = Field(alias="entity_id")
    values: dict[str, Any]  # field_key -> value
