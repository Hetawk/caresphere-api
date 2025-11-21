"""Schemas for member management endpoints."""

from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.member import Gender, MemberStatus


class MemberBase(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    firstName: str = Field(alias="first_name")
    lastName: str = Field(alias="last_name")
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    dateOfBirth: Optional[date] = Field(default=None, alias="date_of_birth")
    gender: Optional[Gender] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zipCode: Optional[str] = Field(default=None, alias="zip_code")
    country: Optional[str] = None
    memberStatus: MemberStatus = Field(alias="member_status")
    membershipType: Optional[str] = Field(
        default=None, alias="membership_type")
    joinDate: Optional[date] = Field(default=None, alias="join_date")
    photoUrl: Optional[str] = Field(default=None, alias="photo_url")
    notes: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    customFields: dict = Field(default_factory=dict, alias="custom_fields")

    # Additional CSV fields
    workSchool: Optional[str] = Field(default=None, alias="work_school")
    whatsappNumber: Optional[str] = Field(
        default=None, alias="whatsapp_number")
    wechatId: Optional[str] = Field(default=None, alias="wechat_id")
    hearAboutUs: Optional[str] = Field(default=None, alias="hear_about_us")
    involvement: Optional[str] = None
    comments: Optional[str] = None
    consentGiven: Optional[bool] = Field(default=False, alias="consent_given")


class MemberCreate(MemberBase):
    firstName: str = Field(alias="first_name")
    lastName: str = Field(alias="last_name")
    memberStatus: MemberStatus = Field(
        default=MemberStatus.ACTIVE, alias="member_status")


class MemberUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    firstName: Optional[str] = Field(default=None, alias="first_name")
    lastName: Optional[str] = Field(default=None, alias="last_name")
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    dateOfBirth: Optional[date] = Field(default=None, alias="date_of_birth")
    gender: Optional[Gender] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zipCode: Optional[str] = Field(default=None, alias="zip_code")
    country: Optional[str] = None
    memberStatus: Optional[MemberStatus] = Field(
        default=None, alias="member_status")
    membershipType: Optional[str] = Field(
        default=None, alias="membership_type")
    joinDate: Optional[date] = Field(default=None, alias="join_date")
    photoUrl: Optional[str] = Field(default=None, alias="photo_url")
    notes: Optional[str] = None
    tags: Optional[List[str]] = None
    customFields: Optional[dict] = Field(default=None, alias="custom_fields")

    # Additional CSV fields
    workSchool: Optional[str] = Field(default=None, alias="work_school")
    whatsappNumber: Optional[str] = Field(
        default=None, alias="whatsapp_number")
    wechatId: Optional[str] = Field(default=None, alias="wechat_id")
    hearAboutUs: Optional[str] = Field(default=None, alias="hear_about_us")
    involvement: Optional[str] = None
    comments: Optional[str] = None
    consentGiven: Optional[bool] = Field(default=None, alias="consent_given")


class MemberPublic(MemberBase):
    id: str
    createdAt: datetime = Field(alias="created_at")
    updatedAt: datetime = Field(alias="updated_at")


class MemberListResponse(BaseModel):
    members: List[MemberPublic]
    pagination: dict


class MemberSearchPayload(BaseModel):
    query: Optional[str] = None
    filters: dict = Field(default_factory=dict)
    page: int = 1
    limit: int = 20


class MemberNoteBase(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    note: str
    noteType: Optional[str] = Field(default=None, alias="note_type")
    isPrivate: bool = Field(default=False, alias="is_private")


class MemberNoteCreate(MemberNoteBase):
    pass


class MemberNotePublic(MemberNoteBase):
    id: str
    createdAt: datetime = Field(alias="created_at")
    updatedAt: datetime = Field(alias="updated_at")
    createdBy: Optional[str] = Field(default=None, alias="created_by")


class MemberActivityPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    activityType: str = Field(alias="activity_type")
    description: Optional[str] = None
    metadata: dict = Field(default_factory=dict,
                           validation_alias="activity_metadata")
    createdAt: datetime = Field(alias="created_at")
    createdBy: Optional[str] = Field(default=None, alias="created_by")
