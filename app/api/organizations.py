"""Organization management API endpoints."""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api import deps
from app.database import get_db
from app.models.user import User
from app.schemas.organization import (
    JoinOrganizationRequest,
    OrganizationCreate,
    OrganizationPublic,
    OrganizationWithCode,
    RegenerateCodeRequest,
)
from app.services.organization_service import OrganizationService
from app.utils import responses
from app.utils.exceptions import ValidationError, NotFoundError, PermissionError

logger = logging.getLogger(__name__)

router = APIRouter()
org_service = OrganizationService()


@router.post("/join", status_code=status.HTTP_200_OK)
async def join_organization(
    payload: JoinOrganizationRequest,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(get_db),
):
    """
    Join an organization using its 7-digit code.
    User will be added as a member.
    """
    org = org_service.join_organization(db, payload.code, current_user)
    
    if not org:
        raise ValidationError({"code": "Invalid organization code or organization not active"})
    
    response_data = OrganizationPublic.model_validate(org)
    return responses.success_response(
        {
            "message": f"Successfully joined {org.name}",
            "organization": response_data.model_dump(by_alias=True)
        },
        status_code=status.HTTP_200_OK
    )


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_organization(
    payload: OrganizationCreate,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new organization.
    Creator automatically becomes super admin.
    """
    # Check if user already belongs to an organization
    existing_org = org_service.get_user_organization(db, current_user)
    if existing_org:
        raise ValidationError({"error": "You already belong to an organization"})
    
    org = org_service.create_organization(db, payload, current_user)
    
    response_data = OrganizationWithCode.model_validate(org)
    return responses.success_response(
        {
            "message": f"Organization '{org.name}' created successfully",
            "organization": response_data.model_dump(by_alias=True)
        },
        status_code=status.HTTP_201_CREATED
    )


@router.get("/my-organization")
async def get_my_organization(
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get the current user's organization.
    Includes organization code if user is admin.
    """
    org = org_service.get_user_organization(db, current_user)
    
    if not org:
        return responses.success_response(
            {"organization": None, "message": "Not part of any organization"},
            status_code=status.HTTP_200_OK
        )
    
    # Check if user is admin to include code
    is_admin = org_service.is_org_admin(db, current_user, org)
    
    if is_admin:
        response_data = OrganizationWithCode.model_validate(org)
    else:
        response_data = OrganizationPublic.model_validate(org)
    
    return responses.success_response(
        {
            "organization": response_data.model_dump(by_alias=True),
            "isAdmin": is_admin
        },
        status_code=status.HTTP_200_OK
    )


@router.post("/regenerate-code", status_code=status.HTTP_200_OK)
async def regenerate_organization_code(
    payload: RegenerateCodeRequest,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(get_db),
):
    """
    Regenerate organization code.
    Only super admin or admin can perform this action.
    """
    org = org_service.get_user_organization(db, current_user)
    
    if not org:
        raise NotFoundError("You are not part of any organization")
    
    # Check if user is admin
    is_admin = org_service.is_org_admin(db, current_user, org)
    if not is_admin:
        raise PermissionError("Only administrators can regenerate organization codes")
    
    # Regenerate code
    new_code = org_service.regenerate_code(db, org, payload.reason)
    
    return responses.success_response(
        {
            "message": "Organization code regenerated successfully",
            "newCode": new_code,
            "reason": payload.reason
        },
        status_code=status.HTTP_200_OK
    )
