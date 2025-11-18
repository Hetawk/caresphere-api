from __future__ import annotations

from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from app.models.organization import Organization
from app.models.setting import SenderSetting, SettingScope
from app.models.user import User, UserRole
from app.schemas.setting import SenderSettingCreate, SenderSettingUpdate
from app.services import settings_service
from app.utils.exceptions import AuthorizationError, NotFoundError


@pytest.fixture
def organization(db: Session) -> Organization:
    org = Organization(
        name="Test Organization",
        slug=f"test-org-{uuid4().hex[:8]}",
        domain="test.example.com",
    )
    db.add(org)
    db.commit()
    db.refresh(org)
    return org


@pytest.fixture
def super_admin(db: Session, organization: Organization) -> User:
    user = User(
        email=f"super.admin+{uuid4().hex}@example.com",
        password_hash="hash",
        full_name="Super Admin",
        role=UserRole.SUPER_ADMIN,
        organization_id=organization.id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def org_admin(db: Session, organization: Organization) -> User:
    user = User(
        email=f"org.admin+{uuid4().hex}@example.com",
        password_hash="hash",
        full_name="Org Admin",
        role=UserRole.ADMIN,
        organization_id=organization.id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def regular_user(db: Session, organization: Organization) -> User:
    user = User(
        email=f"user+{uuid4().hex}@example.com",
        password_hash="hash",
        full_name="Regular User",
        role=UserRole.MEMBER,
        organization_id=organization.id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def test_resolve_sender_settings_cascades_correctly(db: Session, super_admin: User, org_admin: User, regular_user: User, organization: Organization):
    """Test that settings cascade from user -> org -> global -> env."""
    
    # Start with env defaults only
    name, email, phone, layers = settings_service.get_resolved_sender_settings(db, regular_user)
    assert name == "CareSphere"  # from env
    assert email == "no-reply@caresphere.ekddigital.com"  # from env
    assert "environment" in layers
    
    # Add global setting
    global_setting = SenderSetting(
        scope=SettingScope.GLOBAL,
        sender_name="Global CareSphere",
        sender_email="global@caresphere.com",
    )
    db.add(global_setting)
    db.commit()
    
    name, email, phone, layers = settings_service.get_resolved_sender_settings(db, regular_user)
    assert name == "Global CareSphere"
    assert email == "global@caresphere.com"
    assert "global" in layers
    
    # Add org setting
    org_setting = SenderSetting(
        scope=SettingScope.ORGANIZATION,
        reference_id=organization.id,
        sender_name="Org CareSphere",
        sender_phone="+1-555-ORG-PHONE",
    )
    db.add(org_setting)
    db.commit()
    
    name, email, phone, layers = settings_service.get_resolved_sender_settings(db, regular_user)
    assert name == "Org CareSphere"  # overridden by org
    assert email == "global@caresphere.com"  # still from global
    assert phone == "+1-555-ORG-PHONE"  # from org
    assert "organization" in layers
    
    # Add user setting
    user_setting = SenderSetting(
        scope=SettingScope.USER,
        reference_id=regular_user.id,
        sender_email="user@personal.com",
    )
    db.add(user_setting)
    db.commit()
    
    name, email, phone, layers = settings_service.get_resolved_sender_settings(db, regular_user)
    assert name == "Org CareSphere"  # still from org
    assert email == "user@personal.com"  # overridden by user
    assert phone == "+1-555-ORG-PHONE"  # still from org
    assert "user" in layers


def test_create_global_setting_requires_super_admin(db: Session, org_admin: User, regular_user: User):
    """Only super admins can create global settings."""
    
    payload = SenderSettingCreate(
        scope=SettingScope.GLOBAL,
        senderName="Global Setting",
    )
    
    with pytest.raises(AuthorizationError):
        settings_service.create_or_update_sender_setting(db, payload, current_user=org_admin)
    
    with pytest.raises(AuthorizationError):
        settings_service.create_or_update_sender_setting(db, payload, current_user=regular_user)


def test_create_org_setting_requires_admin(db: Session, super_admin: User, org_admin: User, regular_user: User, organization: Organization):
    """Admins can manage org settings for their organization."""
    
    payload = SenderSettingCreate(
        scope=SettingScope.ORGANIZATION,
        referenceId=organization.id,
        senderName="Org Setting",
    )
    
    # Super admin can create any org setting
    setting = settings_service.create_or_update_sender_setting(db, payload, current_user=super_admin)
    assert setting.sender_name == "Org Setting"
    
    # Org admin can create for their own org
    payload.senderName = "Updated Org Setting"
    setting = settings_service.create_or_update_sender_setting(db, payload, current_user=org_admin)
    assert setting.sender_name == "Updated Org Setting"
    
    # Regular user cannot create org settings
    with pytest.raises(AuthorizationError):
        settings_service.create_or_update_sender_setting(db, payload, current_user=regular_user)


def test_create_user_setting_for_self(db: Session, regular_user: User):
    """Users can manage their own settings."""
    
    payload = SenderSettingCreate(
        scope=SettingScope.USER,
        referenceId=regular_user.id,
        senderName="Personal Setting",
        senderEmail="personal@example.com",
    )
    
    setting = settings_service.create_or_update_sender_setting(db, payload, current_user=regular_user)
    assert setting.sender_name == "Personal Setting"
    assert setting.sender_email == "personal@example.com"


def test_update_existing_setting(db: Session, regular_user: User):
    """Updating existing settings works correctly."""
    
    # Create initial setting
    initial = SenderSetting(
        scope=SettingScope.USER,
        reference_id=regular_user.id,
        sender_name="Initial Name",
    )
    db.add(initial)
    db.commit()
    
    # Update it
    payload = SenderSettingUpdate(senderName="Updated Name", senderEmail="new@example.com")
    updated = settings_service.create_or_update_sender_setting(
        db, payload, current_user=regular_user, scope=SettingScope.USER, reference_id=regular_user.id
    )
    
    assert updated.id == initial.id  # Same record
    assert updated.sender_name == "Updated Name"
    assert updated.sender_email == "new@example.com"


def test_delete_setting_with_permissions(db: Session, super_admin: User, regular_user: User):
    """Delete operations respect permissions."""
    
    # Create user setting
    setting = SenderSetting(
        scope=SettingScope.USER,
        reference_id=regular_user.id,
        sender_name="To Delete",
    )
    db.add(setting)
    db.commit()
    
    # User can delete their own setting
    settings_service.delete_sender_setting(db, SettingScope.USER, regular_user.id, current_user=regular_user)
    
    # Verify it's gone
    assert settings_service.get_sender_setting(db, SettingScope.USER, regular_user.id) is None


def test_cross_org_admin_permissions(db: Session, org_admin: User):
    """Org admins cannot manage other organizations."""
    
    # Create another org
    other_org = Organization(name="Other Org", slug=f"other-{uuid4().hex[:8]}")
    db.add(other_org)
    db.commit()
    
    payload = SenderSettingCreate(
        scope=SettingScope.ORGANIZATION,
        referenceId=other_org.id,
        senderName="Cross Org Setting",
    )
    
    with pytest.raises(AuthorizationError):
        settings_service.create_or_update_sender_setting(db, payload, current_user=org_admin)


def test_get_setting_returns_none_for_nonexistent(db: Session):
    """Getting non-existent settings returns None."""
    
    # Test with specific non-existent reference_id
    setting = settings_service.get_sender_setting(db, SettingScope.USER, "non-existent-user-id")
    assert setting is None
    
    setting = settings_service.get_sender_setting(db, SettingScope.ORGANIZATION, "non-existent-org-id")
    assert setting is None


def test_delete_nonexistent_setting_raises_not_found(db: Session, super_admin: User):
    """Deleting non-existent settings raises NotFoundError."""
    
    # Try to delete a setting with a non-existent reference_id
    with pytest.raises(NotFoundError):
        settings_service.delete_sender_setting(db, SettingScope.USER, "non-existent-user-id", current_user=super_admin)