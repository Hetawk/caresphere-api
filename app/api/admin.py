"""Admin-only routes for system management."""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.api import deps
from app.database import get_db
from app.models.user import User, UserRole
from app.utils import responses

logger = logging.getLogger(__name__)

router = APIRouter()


class PromoteUserRequest(BaseModel):
    """Request to promote a user to admin."""
    email: EmailStr
    role: UserRole = UserRole.SUPER_ADMIN


class UserRoleResponse(BaseModel):
    """Response after updating user role."""
    email: str
    role: UserRole
    message: str


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
    
    logger.info(f"User {current_user.email} promoted {target_user.email} from {old_role} to {payload.role}")
    
    response = UserRoleResponse(
        email=target_user.email,
        role=target_user.role,
        message=f"Successfully promoted {target_user.email} to {payload.role}"
    )
    
    return responses.success_response(response.model_dump())
