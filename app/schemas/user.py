"""Pydantic schemas for user and auth flows."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_serializer

from app.models.user import UserRole, UserStatus


class UserPermissions(BaseModel):
    """User permission flags based on role."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    manageUsers: bool = False
    manageMembers: bool = False
    sendMessages: bool = False
    viewAnalytics: bool = False
    manageAutomation: bool = False
    manageTemplates: bool = False
    manageOrganization: bool = False
    manageSettings: bool = False
    exportData: bool = False
    deleteData: bool = False


def get_permissions_for_role(role: UserRole) -> UserPermissions:
    """Return permissions based on user role."""
    if role == UserRole.SUPER_ADMIN:
        return UserPermissions(
            manageUsers=True,
            manageMembers=True,
            sendMessages=True,
            viewAnalytics=True,
            manageAutomation=True,
            manageTemplates=True,
            manageOrganization=True,
            manageSettings=True,
            exportData=True,
            deleteData=True,
        )
    elif role == UserRole.ADMIN:
        return UserPermissions(
            manageUsers=True,
            manageMembers=True,
            sendMessages=True,
            viewAnalytics=True,
            manageAutomation=True,
            manageTemplates=True,
            manageOrganization=False,
            manageSettings=True,
            exportData=True,
            deleteData=True,
        )
    elif role == UserRole.MINISTRY_LEADER:
        return UserPermissions(
            manageUsers=False,
            manageMembers=True,
            sendMessages=True,
            viewAnalytics=True,
            manageAutomation=True,
            manageTemplates=True,
            manageOrganization=False,
            manageSettings=False,
            exportData=False,
            deleteData=False,
        )
    elif role == UserRole.VOLUNTEER:
        return UserPermissions(
            manageUsers=False,
            manageMembers=True,
            sendMessages=True,
            viewAnalytics=False,
            manageAutomation=False,
            manageTemplates=False,
            manageOrganization=False,
            manageSettings=False,
            exportData=False,
            deleteData=False,
        )
    else:  # MEMBER
        return UserPermissions(
            manageUsers=False,
            manageMembers=False,
            sendMessages=False,
            viewAnalytics=False,
            manageAutomation=False,
            manageTemplates=False,
            manageOrganization=False,
            manageSettings=False,
            exportData=False,
            deleteData=False,
        )


class UserOrganizationRole(BaseModel):
    """Role information within an organization."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    displayName: str = Field(alias="display_name")

    @field_serializer('displayName')
    def serialize_display_name(self, value: str) -> str:
        return value


class UserOrganizationInfo(BaseModel):
    """Basic organization info for user display."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    slug: str
    isActive: bool = Field(alias="is_active")


class UserOrganizationMembership(BaseModel):
    """User's membership in an organization with role."""
    model_config = ConfigDict(from_attributes=True)

    organization: UserOrganizationInfo
    role: Optional[UserOrganizationRole] = None
    isOwner: bool = Field(alias="is_owner")
    isActive: bool = Field(alias="is_active")
    joinedAt: Optional[str] = Field(default=None, alias="joined_at")


class UserBase(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    email: EmailStr
    fullName: str = Field(alias="full_name")
    displayName: Optional[str] = Field(default=None, alias="display_name")
    avatarUrl: Optional[str] = Field(default=None, alias="avatar_url")
    role: UserRole
    status: UserStatus
    emailVerified: bool = Field(alias="email_verified")
    lastLoginAt: Optional[datetime] = Field(
        default=None, alias="last_login_at")

    @field_serializer('lastLoginAt')
    def serialize_last_login(self, value: Optional[datetime]) -> Optional[str]:
        return value.isoformat() if value else None


class UserPublic(UserBase):
    id: str
    createdAt: datetime = Field(alias="created_at")
    updatedAt: datetime = Field(alias="updated_at")
    permissions: UserPermissions = Field(
        default_factory=lambda: UserPermissions())
    organizations: list[UserOrganizationMembership] = Field(
        default_factory=list)

    @field_serializer('createdAt', 'updatedAt')
    def serialize_datetime(self, value: datetime) -> str:
        return value.isoformat()

    @classmethod
    def model_validate(cls, obj, **kwargs):
        """Override to add permissions based on role."""
        instance = super().model_validate(obj, **kwargs)
        # Add permissions based on role
        instance.permissions = get_permissions_for_role(obj.role)
        return instance


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


class ChangePasswordRequest(BaseModel):
    """Schema for changing password when user is logged in."""
    currentPassword: str = Field(min_length=1)
    newPassword: str = Field(min_length=8)


class ForgotPasswordRequest(BaseModel):
    """Schema for initiating password reset flow."""
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Schema for completing password reset with token."""
    email: EmailStr
    token: str = Field(min_length=6, max_length=6)
    newPassword: str = Field(min_length=8)


class VerifyEmailRequest(BaseModel):
    """Schema for email verification."""
    email: EmailStr
    token: str = Field(min_length=6, max_length=6)


class RegisterWithOrganizationRequest(BaseModel):
    """Combined schema for user registration with organization options."""
    email: EmailStr
    password: str = Field(min_length=8)
    fullName: str = Field(alias="full_name")
    displayName: Optional[str] = Field(default=None, alias="display_name")
    action: str = Field(pattern=r"^(create|join|skip)$")
    organizationName: Optional[str] = Field(
        default=None, alias="organization_name", min_length=2, max_length=255)
    organizationCode: Optional[str] = Field(
        default=None, alias="organization_code", min_length=7, max_length=7, pattern=r"^\d{7}$")
    verificationCode: str = Field(
        alias="verification_code", min_length=6, max_length=6)


class SendVerificationCodeRequest(BaseModel):
    """Schema for requesting a verification code."""
    email: EmailStr
