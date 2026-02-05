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
    if payload.password is not None:
        # Hash the new password
        from app.utils.security import hash_password
        target_user.password_hash = hash_password(payload.password)

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
    Delete a user.
    Requires authentication.
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
    db.delete(target_user)
    db.commit()

    logger.info(f"User {current_user.email} deleted user {user_email}")

    return responses.success_response({"message": f"User {user_email} deleted successfully"})


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


@router.post("/bootstrap-admin")
async def bootstrap_admin(
    db: Session = Depends(get_db)
):
    """
    Bootstrap endpoint to promote admin@jinanicf.com to super_admin.
    This is a one-time setup endpoint that requires no authentication.
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
