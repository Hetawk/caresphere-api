"""Settings management routes."""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api import deps
from app.database import get_db
from app.models.setting import SettingScope
from app.models.user import User, UserRole
from app.schemas.setting import (
    ResolvedSenderSettings,
    SenderSettingCreate,
    SenderSettingPublic,
    SenderSettingUpdate,
)
from app.services import settings_service
from app.utils import responses
from app.utils.exceptions import ValidationError

router = APIRouter()


@router.get("/senders/resolved")
async def get_resolved_sender_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """Get the final resolved sender settings for the current user."""
    name, email, phone, layers = settings_service.get_resolved_sender_settings(db, current_user)
    
    # Determine primary source
    source = "environment"
    if "user" in layers:
        source = "user"
    elif "organization" in layers:
        source = "organization"
    elif "global" in layers:
        source = "global"
    
    response = ResolvedSenderSettings(
        senderName=name,
        senderEmail=email,
        senderPhone=phone,
        source=source,
        layers=layers
    )
    return responses.success_response(response.model_dump())


@router.get("/senders")
async def get_sender_setting(
    scope: str = Query(..., description="Setting scope: global, organization, or user"),
    reference_id: str | None = Query(None, description="Reference ID (org ID or user ID)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """Get specific sender setting by scope and reference."""
    try:
        scope_enum = SettingScope(scope)
    except ValueError as exc:
        raise ValidationError({"scope": "Invalid scope value"}) from exc
    
    # Auto-fill reference_id for user scope
    if scope_enum == SettingScope.USER and not reference_id:
        reference_id = current_user.id
    elif scope_enum == SettingScope.ORGANIZATION and not reference_id:
        reference_id = current_user.organization_id
    
    # Validate permissions
    settings_service._validate_setting_permissions(current_user, scope_enum, reference_id)
    
    setting = settings_service.get_sender_setting(db, scope_enum, reference_id)
    if not setting:
        return responses.success_response({"setting": None})
    
    return responses.success_response({
        "setting": SenderSettingPublic.model_validate(setting).model_dump(by_alias=True)
    })


@router.put("/senders", status_code=status.HTTP_200_OK)
async def update_sender_setting(
    payload: SenderSettingUpdate,
    scope: str = Query(..., description="Setting scope: global, organization, or user"),
    reference_id: str | None = Query(None, description="Reference ID (org ID or user ID)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """Update sender setting for specific scope."""
    try:
        scope_enum = SettingScope(scope)
    except ValueError as exc:
        raise ValidationError({"scope": "Invalid scope value"}) from exc
    
    # Auto-fill reference_id for user scope
    if scope_enum == SettingScope.USER and not reference_id:
        reference_id = current_user.id
    elif scope_enum == SettingScope.ORGANIZATION and not reference_id:
        reference_id = current_user.organization_id
    
    setting = settings_service.create_or_update_sender_setting(
        db, payload, current_user=current_user, scope=scope_enum, reference_id=reference_id
    )
    
    return responses.success_response(
        SenderSettingPublic.model_validate(setting).model_dump(by_alias=True)
    )


@router.post("/senders", status_code=status.HTTP_201_CREATED)
async def create_sender_setting(
    payload: SenderSettingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """Create new sender setting."""
    setting = settings_service.create_or_update_sender_setting(db, payload, current_user=current_user)
    
    return responses.success_response(
        SenderSettingPublic.model_validate(setting).model_dump(by_alias=True),
        status_code=status.HTTP_201_CREATED
    )


@router.delete("/senders")
async def delete_sender_setting(
    scope: str = Query(..., description="Setting scope: global, organization, or user"),
    reference_id: str | None = Query(None, description="Reference ID (org ID or user ID)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """Delete sender setting for specific scope."""
    try:
        scope_enum = SettingScope(scope)
    except ValueError as exc:
        raise ValidationError({"scope": "Invalid scope value"}) from exc
    
    # Auto-fill reference_id for user scope
    if scope_enum == SettingScope.USER and not reference_id:
        reference_id = current_user.id
    elif scope_enum == SettingScope.ORGANIZATION and not reference_id:
        reference_id = current_user.organization_id
    
    settings_service.delete_sender_setting(db, scope_enum, reference_id, current_user=current_user)
    
    return responses.success_response({"message": "Sender setting deleted successfully"})