"""Custom roles and permissions model."""

from __future__ import annotations

from sqlalchemy import Boolean, Column, ForeignKey, JSON, String, Table
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin

# Association table for role permissions
role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", String(36), ForeignKey(
        "roles.id", ondelete="CASCADE"), primary_key=True),
    Column("permission_id", String(36), ForeignKey(
        "permissions.id", ondelete="CASCADE"), primary_key=True),
)


class Permission(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Granular permissions that can be assigned to roles."""
    __tablename__ = "permissions"

    # e.g., "manage_members"
    name = Column(String(100), unique=True, nullable=False)
    # e.g., "Manage Members"
    display_name = Column(String(255), nullable=False)
    description = Column(String(500))
    # e.g., "members", "messages", "settings"
    category = Column(String(50), nullable=False)
    # System permissions cannot be deleted
    is_system = Column(Boolean, default=False)

    roles = relationship("Role", secondary=role_permissions,
                         back_populates="permissions")


class Role(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Custom roles for organizations with flexible permissions."""
    __tablename__ = "roles"

    organization_id = Column(String(36), ForeignKey(
        "organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    # e.g., "Youth Leader", "Treasurer"
    name = Column(String(100), nullable=False)
    display_name = Column(String(255), nullable=False)
    description = Column(String(500))
    # System roles (super_admin, admin, etc.) cannot be deleted
    is_system = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    color = Column(String(7), default="#6B7280")  # Hex color for UI display

    organization = relationship("Organization", back_populates="roles")
    permissions = relationship(
        "Permission", secondary=role_permissions, back_populates="roles")
    organization_users = relationship(
        "OrganizationUser", back_populates="role")


class OrganizationUser(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Many-to-many relationship between users and organizations with roles."""
    __tablename__ = "organization_users"

    user_id = Column(String(36), ForeignKey(
        "users.id", ondelete="CASCADE"), nullable=False, index=True)
    organization_id = Column(String(36), ForeignKey(
        "organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    role_id = Column(String(36), ForeignKey(
        "roles.id", ondelete="SET NULL"), nullable=True, index=True)

    is_owner = Column(Boolean, default=False)  # Organization owner (creator)
    is_active = Column(Boolean, default=True)
    invited_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    # Date user accepted invitation
    joined_at = Column(String(50), nullable=True)

    user = relationship("User", foreign_keys=[
                        user_id], back_populates="organization_memberships")
    organization = relationship("Organization", back_populates="members")
    role = relationship("Role", back_populates="organization_users")
    inviter = relationship("User", foreign_keys=[invited_by])


class UserInvitation(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Pending invitations for users to join organizations."""
    __tablename__ = "user_invitations"

    organization_id = Column(String(36), ForeignKey(
        "organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    email = Column(String(255), nullable=False, index=True)
    role_id = Column(String(36), ForeignKey(
        "roles.id", ondelete="SET NULL"), nullable=True)
    invited_by = Column(String(36), ForeignKey("users.id"), nullable=False)

    token = Column(String(255), unique=True,
                   nullable=False)  # Invitation token
    expires_at = Column(String(50), nullable=False)
    accepted_at = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True)
    message = Column(String(1000), nullable=True)  # Custom invitation message

    organization = relationship("Organization")
    role = relationship("Role")
    inviter = relationship("User", foreign_keys=[invited_by])
