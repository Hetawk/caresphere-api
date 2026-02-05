"""Organization schemas for API requests and responses."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class OrganizationBase(BaseModel):
    """Base organization schema with common fields."""
    name: str = Field(..., min_length=2, max_length=255)
    slug: str = Field(..., min_length=2, max_length=255)
    domain: Optional[str] = Field(None, max_length=255)


class OrganizationCreate(OrganizationBase):
    """Schema for creating an organization."""
    pass


class OrganizationUpdate(BaseModel):
    """Schema for updating an organization."""
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    slug: Optional[str] = Field(None, min_length=2, max_length=255)
    domain: Optional[str] = Field(None, max_length=255)
    is_active: Optional[bool] = None


class OrganizationInDB(OrganizationBase):
    """Schema for organization from database."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    organization_code: str = Field(...,
                                   description="7-digit organization code")
    is_active: bool
    created_at: datetime
    updated_at: datetime


class OrganizationPublic(BaseModel):
    """Public organization schema (without sensitive data like code for non-admins)."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    slug: str
    is_active: bool


class OrganizationWithCode(OrganizationPublic):
    """Organization schema with code (for admins only)."""
    organization_code: str = Field(
        ..., description="7-digit organization code for inviting members")


class JoinOrganizationRequest(BaseModel):
    """Schema for joining an organization by code."""
    code: str = Field(..., min_length=7, max_length=7, pattern=r"^\d{7}$",
                      description="7-digit organization code")


class RegenerateCodeRequest(BaseModel):
    """Schema for regenerating organization code."""
    reason: Optional[str] = Field(None, max_length=500,
                                  description="Reason for regenerating the code (audit trail)")


class OrganizationOption(BaseModel):
    """Schema for organization selection during registration."""
    action: str = Field(..., pattern=r"^(create|join|skip)$",
                        description="Action to take: create new org, join existing, or skip")
    name: Optional[str] = Field(None, min_length=2, max_length=255,
                                description="Organization name (required if action=create)")
    code: Optional[str] = Field(None, min_length=7, maxlength=7, pattern=r"^\d{7}$",
                                description="Organization code (required if action=join)")
