"""Template schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.template import TemplateType


class TemplateBase(BaseModel):
    name: str
    description: Optional[str] = None
    templateType: TemplateType = Field(default=TemplateType.EMAIL, alias="template_type")
    category: Optional[str] = None
    subject: Optional[str] = None
    content: str
    variables: Optional[str] = None
    thumbnailUrl: Optional[str] = Field(default=None, alias="thumbnail_url")
    isActive: bool = Field(default=True, alias="is_active")


class TemplateCreate(TemplateBase):
    pass


class TemplateUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    name: Optional[str] = None
    description: Optional[str] = None
    templateType: Optional[TemplateType] = Field(default=None, alias="template_type")
    category: Optional[str] = None
    subject: Optional[str] = None
    content: Optional[str] = None
    variables: Optional[str] = None
    thumbnailUrl: Optional[str] = Field(default=None, alias="thumbnail_url")
    isActive: Optional[bool] = Field(default=None, alias="is_active")


class TemplatePublic(TemplateBase):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    usageCount: int = Field(alias="usage_count")
    createdAt: datetime = Field(alias="created_at")
    updatedAt: datetime = Field(alias="updated_at")
