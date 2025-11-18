"""Settings service for managing configurable sender preferences."""

from __future__ import annotations

from typing import Dict, Optional, Tuple

from sqlalchemy.orm import Session

from app.config import settings
from app.models.setting import SenderSetting, SettingScope
from app.models.user import User, UserRole
from app.schemas.setting import SenderSettingCreate, SenderSettingUpdate
from app.utils.exceptions import AuthorizationError, NotFoundError


def get_resolved_sender_settings(db: Session, current_user: User) -> Tuple[str, str, str, Dict]:
    """
    Resolve sender settings with precedence: user → organization → global → environment.
    Returns (name, email, phone, layers_info).
    """
    layers = {}
    
    # Start with environment defaults
    final_name = settings.MSG_SENDER_NAME
    final_email = settings.MSG_SENDER_EMAIL
    final_phone = settings.MSG_SENDER_PHONE
    layers["environment"] = {
        "name": final_name,
        "email": final_email,
        "phone": final_phone
    }
    
    # Check global settings
    global_setting = db.query(SenderSetting).filter(
        SenderSetting.scope == SettingScope.GLOBAL,
        SenderSetting.reference_id.is_(None)
    ).first()
    
    if global_setting:
        layers["global"] = {}
        if global_setting.sender_name:
            final_name = global_setting.sender_name
            layers["global"]["name"] = final_name
        if global_setting.sender_email:
            final_email = global_setting.sender_email
            layers["global"]["email"] = final_email
        if global_setting.sender_phone:
            final_phone = global_setting.sender_phone
            layers["global"]["phone"] = final_phone
    
    # Check organization settings
    if current_user.organization_id:
        org_setting = db.query(SenderSetting).filter(
            SenderSetting.scope == SettingScope.ORGANIZATION,
            SenderSetting.reference_id == current_user.organization_id
        ).first()
        
        if org_setting:
            layers["organization"] = {}
            if org_setting.sender_name:
                final_name = org_setting.sender_name
                layers["organization"]["name"] = final_name
            if org_setting.sender_email:
                final_email = org_setting.sender_email
                layers["organization"]["email"] = final_email
            if org_setting.sender_phone:
                final_phone = org_setting.sender_phone
                layers["organization"]["phone"] = final_phone
    
    # Check user settings
    user_setting = db.query(SenderSetting).filter(
        SenderSetting.scope == SettingScope.USER,
        SenderSetting.reference_id == current_user.id
    ).first()
    
    if user_setting:
        layers["user"] = {}
        if user_setting.sender_name:
            final_name = user_setting.sender_name
            layers["user"]["name"] = final_name
        if user_setting.sender_email:
            final_email = user_setting.sender_email
            layers["user"]["email"] = final_email
        if user_setting.sender_phone:
            final_phone = user_setting.sender_phone
            layers["user"]["phone"] = final_phone
    
    return final_name, final_email, final_phone, layers


def get_sender_setting(db: Session, scope: SettingScope, reference_id: Optional[str] = None) -> Optional[SenderSetting]:
    """Get sender setting for specific scope and reference."""
    return db.query(SenderSetting).filter(
        SenderSetting.scope == scope,
        SenderSetting.reference_id == reference_id
    ).first()


def create_or_update_sender_setting(
    db: Session,
    payload: SenderSettingCreate | SenderSettingUpdate,
    *,
    current_user: User,
    scope: Optional[SettingScope] = None,
    reference_id: Optional[str] = None
) -> SenderSetting:
    """Create or update sender setting with proper authorization checks."""
    
    # Determine scope and reference_id
    if isinstance(payload, SenderSettingCreate):
        target_scope = payload.scope
        target_reference_id = payload.referenceId
    else:
        if scope is None:
            raise ValueError("Scope must be provided for updates")
        target_scope = scope
        target_reference_id = reference_id
    
    # Authorization checks
    _validate_setting_permissions(current_user, target_scope, target_reference_id)
    
    # Find existing or create new
    setting = get_sender_setting(db, target_scope, target_reference_id)
    
    if setting:
        # Update existing
        update_data = payload.model_dump(exclude_unset=True, by_alias=True, exclude={"scope", "reference_id"})
        for key, value in update_data.items():
            setattr(setting, key, value)
    else:
        # Create new
        create_data = payload.model_dump(by_alias=True)
        if isinstance(payload, SenderSettingUpdate):
            create_data.update({
                "scope": target_scope,
                "reference_id": target_reference_id
            })
        setting = SenderSetting(**create_data)
        db.add(setting)
    
    db.commit()
    db.refresh(setting)
    return setting


def delete_sender_setting(
    db: Session,
    scope: SettingScope,
    reference_id: Optional[str],
    *,
    current_user: User
) -> None:
    """Delete sender setting with proper authorization."""
    _validate_setting_permissions(current_user, scope, reference_id)
    
    setting = get_sender_setting(db, scope, reference_id)
    if not setting:
        raise NotFoundError("Sender setting", f"{scope}:{reference_id or 'null'}")
    
    db.delete(setting)
    db.commit()


def _validate_setting_permissions(
    current_user: User,
    scope: SettingScope,
    reference_id: Optional[str]
) -> None:
    """Validate user permissions for setting operations."""
    
    if scope == SettingScope.GLOBAL:
        if current_user.role != UserRole.SUPER_ADMIN:
            raise AuthorizationError("Only super admins can manage global settings")
    
    elif scope == SettingScope.ORGANIZATION:
        if current_user.role not in (UserRole.SUPER_ADMIN, UserRole.ADMIN):
            raise AuthorizationError("Only admins can manage organization settings")
        
        if (current_user.role == UserRole.ADMIN and 
            current_user.organization_id != reference_id):
            raise AuthorizationError("Admins can only manage their own organization settings")
    
    elif scope == SettingScope.USER:
        if (current_user.role != UserRole.SUPER_ADMIN and 
            current_user.id != reference_id):
            raise AuthorizationError("Users can only manage their own settings")