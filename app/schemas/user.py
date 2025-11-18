"""Pydantic schemas for user and auth flows."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.user import UserRole, UserStatus


class UserBase(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    email: EmailStr
    fullName: str = Field(alias="full_name")
    displayName: Optional[str] = Field(default=None, alias="display_name")
    avatarUrl: Optional[str] = Field(default=None, alias="avatar_url")
    role: UserRole
    status: UserStatus
    emailVerified: bool = Field(alias="email_verified")
    lastLoginAt: Optional[datetime] = Field(default=None, alias="last_login_at")


class UserPublic(UserBase):
    id: str
    createdAt: datetime = Field(alias="created_at")
    updatedAt: datetime = Field(alias="updated_at")


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    fullName: str
    displayName: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenPair(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    accessToken: str
    refreshToken: str
    expiresIn: int


class AuthResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    user: UserPublic
    accessToken: str
    refreshToken: str
    expiresIn: int


class RefreshRequest(BaseModel):
    refreshToken: str


class RefreshResponse(BaseModel):
    accessToken: str
    expiresIn: int


class MessageResponse(BaseModel):
    message: str
