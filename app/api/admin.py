"""Admin-only routes for system management."""

import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.api import deps
from app.database import get_db
from app.models.user import User, UserRole, UserStatus
from app.schemas.user import UserPublic
from app.utils import responses

logger = logging.getLogger(__name__)

router = APIRouter()


class PromoteUserRequest(BaseModel):
    """Request to promote a user to admin."""
    email: EmailStr
    role: UserRole = UserRole.SUPER_ADMIN


class UpdateUserRequest(BaseModel):
    """Request to update user details."""
    email: EmailStr | None = None
    fullName: str | None = None
    displayName: str | None = None
    avatarUrl: str | None = None
    role: UserRole | None = None
    status: UserStatus | None = None
    emailVerified: bool | None = None
    password: str | None = None  # New password if changing


class UserRoleResponse(BaseModel):
    """Response after updating user role."""
    email: str
    role: UserRole
    message: str


class UsersListResponse(BaseModel):
    """Response for listing users."""
    users: List[UserPublic]
    total: int


@router.get("/users")
async def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    List all users in the system.
    Requires authentication.
    """
    users = db.query(User).order_by(User.created_at.desc()).all()
    user_publics = [UserPublic.model_validate(user) for user in users]

    response = UsersListResponse(
        users=user_publics,
        total=len(user_publics)
    )

    return responses.success_response(response.model_dump(by_alias=True))


@router.patch("/users/{user_id}")
async def update_user(
    user_id: str,
    payload: UpdateUserRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Update user details.
    Requires authentication.
    """
    target_user = db.get(User, user_id)

    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )

    # Update fields if provided
    if payload.email is not None:
        target_user.email = payload.email
    if payload.fullName is not None:
        target_user.full_name = payload.fullName
    if payload.displayName is not None:
        target_user.display_name = payload.displayName
    if payload.avatarUrl is not None:
        target_user.avatar_url = payload.avatarUrl
    if payload.role is not None:
        target_user.role = payload.role
    if payload.status is not None:
        target_user.status = payload.status
    if payload.emailVerified is not None:
        target_user.email_verified = payload.emailVerified
    if payload.password is not None and len(payload.password.strip()) > 0:
        # Hash the new password (only if not empty)
        from app.utils.security import get_password_hash
        target_user.password_hash = get_password_hash(payload.password)

    db.commit()
    db.refresh(target_user)

    logger.info(f"User {current_user.email} updated user {target_user.email}")

    user_public = UserPublic.model_validate(target_user)
    return responses.success_response(user_public.model_dump(by_alias=True))


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Delete a user and handle all related records.
    Requires authentication.

    This endpoint will:
    - Delete user's sender profiles
    - Nullify created_by references (templates, messages, members, etc.)
    - Remove organization memberships
    - Delete organization invitations sent by the user
    """
    target_user = db.get(User, user_id)

    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )

    # Prevent deleting yourself
    if target_user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )

    user_email = target_user.email

    try:
        # Import models to access related tables
        from app.models.message import SenderProfile, Message, MessageRecipient
        from app.models.member import Member, MemberNote, MemberGroup
        from app.models.template import Template
        from app.models.automation import Automation
        from app.models.role import OrganizationUser, OrganizationInvitation
        from app.models.setting import SenderSetting, SettingScope

        # 1. Delete messages and their recipients (created by this user)
        # Get message IDs first
        message_ids = [msg.id for msg in db.query(
            Message.id).filter(Message.created_by == user_id).all()]
        if message_ids:
            # Delete message recipients first (foreign key constraint)
            db.query(MessageRecipient).filter(MessageRecipient.message_id.in_(
                message_ids)).delete(synchronize_session=False)
            # Then delete messages
            db.query(Message).filter(Message.created_by ==
                                     user_id).delete(synchronize_session=False)

        # 2. Delete sender profiles owned by this user
        db.query(SenderProfile).filter(
            SenderProfile.user_id == user_id).delete()

        # 3. Delete user-scoped sender settings
        db.query(SenderSetting).filter(
            SenderSetting.scope == SettingScope.USER,
            SenderSetting.reference_id == user_id
        ).delete()

        # 4. Nullify created_by references (preserve data created by this user)
        db.query(Template).filter(Template.created_by == user_id).update(
            {"created_by": None}, synchronize_session=False)
        db.query(Member).filter(Member.created_by == user_id).update(
            {"created_by": None}, synchronize_session=False)
        db.query(MemberNote).filter(MemberNote.created_by == user_id).update(
            {"created_by": None}, synchronize_session=False)
        db.query(MemberGroup).filter(MemberGroup.created_by == user_id).update(
            {"created_by": None}, synchronize_session=False)
        db.query(Automation).filter(Automation.created_by == user_id).update(
            {"created_by": None}, synchronize_session=False)

        # 5. Nullify member.user_id (unlink members from this user account)
        db.query(Member).filter(Member.user_id == user_id).update(
            {"user_id": None}, synchronize_session=False)

        # 6. Delete organization memberships
        db.query(OrganizationUser).filter(
            OrganizationUser.user_id == user_id).delete()

        # 7. Delete invitations sent by this user
        db.query(OrganizationInvitation).filter(
            OrganizationInvitation.invited_by == user_id).delete()

        # 8. Finally, delete the user
        db.delete(target_user)
        db.commit()

        logger.info(
            f"User {current_user.email} deleted user {user_email} and cleaned up {len(message_ids) if message_ids else 0} messages and all related records")

        return responses.success_response({
            "message": f"User {user_email} deleted successfully",
            "deleted_messages": len(message_ids) if message_ids else 0
        })

    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting user {user_email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete user: {str(e)}"
        )


@router.post("/promote-user", response_model=UserRoleResponse, status_code=status.HTTP_200_OK)
async def promote_user(
    payload: PromoteUserRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Promote a user to admin role.

    This endpoint allows any authenticated user to promote ANY user (including themselves)
    to admin during initial setup. In production, add proper authorization checks.
    """
    # Find target user
    target_user = db.query(User).filter(User.email == payload.email).first()

    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with email {payload.email} not found"
        )

    # Update role
    old_role = target_user.role
    target_user.role = payload.role

    db.commit()
    db.refresh(target_user)

    logger.info(
        f"User {current_user.email} promoted {target_user.email} from {old_role} to {payload.role}")

    response = UserRoleResponse(
        email=target_user.email,
        role=target_user.role,
        message=f"Successfully promoted {target_user.email} to {payload.role}"
    )

    return responses.success_response(response.model_dump())


@router.get("/bootstrap-admin")
async def bootstrap_admin(
    db: Session = Depends(get_db)
):
    """
    Bootstrap endpoint to promote admin@jinanicf.com to super_admin.
    This is a one-time setup endpoint that requires no authentication.
    Just visit this URL in your browser to activate.
    """
    target_email = "admin@jinanicf.com"

    # Find target user
    target_user = db.query(User).filter(User.email == target_email).first()

    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with email {target_email} not found. Please register first."
        )

    # Update to super admin
    old_role = target_user.role
    target_user.role = UserRole.SUPER_ADMIN
    target_user.email_verified = True
    target_user.status = UserStatus.ACTIVE

    db.commit()
    db.refresh(target_user)

    logger.info(
        f"Bootstrap: Promoted {target_user.email} from {old_role} to SUPER_ADMIN")

    return responses.success_response({
        "message": f"Successfully promoted {target_user.email} to SUPER_ADMIN",
        "email": target_user.email,
        "role": target_user.role,
        "oldRole": old_role
    })
