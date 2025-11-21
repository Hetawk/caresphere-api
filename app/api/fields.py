"""API routes for field configuration management."""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api import deps
from app.database import get_db
from app.models.field_config import EntityType
from app.models.user import User, UserRole
from app.schemas.field_config import (
    BulkFieldValuesUpdate,
    EntityFieldsResponse,
    FieldConfigurationCreate,
    FieldConfigurationPublic,
    FieldConfigurationUpdate,
)
from app.services import field_config_service
from app.utils import responses

router = APIRouter()

ADMIN_ROLES = (UserRole.SUPER_ADMIN, UserRole.ADMIN)


@router.post("/configurations", status_code=status.HTTP_201_CREATED)
async def create_field_configuration(
    payload: FieldConfigurationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.require_roles(*ADMIN_ROLES)),
):
    """Create a new field configuration."""
    field_config = field_config_service.create_field_configuration(
        db, current_user.organization_id, payload, current_user
    )
    body = FieldConfigurationPublic.model_validate(
        field_config).model_dump(by_alias=True)
    return responses.success_response(body, status_code=status.HTTP_201_CREATED)


@router.get("/configurations")
async def list_field_configurations(
    entity_type: EntityType | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """List all field configurations for the organization."""
    configurations = field_config_service.list_field_configurations(
        db, current_user.organization_id, entity_type
    )
    data = [
        FieldConfigurationPublic.model_validate(
            config).model_dump(by_alias=True)
        for config in configurations
    ]
    return responses.success_response({"configurations": data})


@router.get("/configurations/{config_id}")
async def get_field_configuration(
    config_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(deps.get_current_user),
):
    """Get a specific field configuration."""
    config = field_config_service.get_field_configuration(db, config_id)
    body = FieldConfigurationPublic.model_validate(
        config).model_dump(by_alias=True)
    return responses.success_response(body)


@router.put("/configurations/{config_id}")
async def update_field_configuration(
    config_id: str,
    payload: FieldConfigurationUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(deps.require_roles(*ADMIN_ROLES)),
):
    """Update a field configuration."""
    config = field_config_service.update_field_configuration(
        db, config_id, payload)
    body = FieldConfigurationPublic.model_validate(
        config).model_dump(by_alias=True)
    return responses.success_response(body)


@router.delete("/configurations/{config_id}")
async def delete_field_configuration(
    config_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(deps.require_roles(*ADMIN_ROLES)),
):
    """Delete a field configuration."""
    field_config_service.delete_field_configuration(db, config_id)
    return responses.success_response({"message": "Field configuration deleted successfully"})


@router.get("/entities/{entity_type}/{entity_id}")
async def get_entity_fields(
    entity_type: EntityType,
    entity_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """Get all field configurations and values for a specific entity."""
    data = field_config_service.get_entity_fields(
        db, current_user.organization_id, entity_type, entity_id
    )

    configurations = [
        FieldConfigurationPublic.model_validate(
            config).model_dump(by_alias=True)
        for config in data["configurations"]
    ]

    response_data = EntityFieldsResponse(
        configurations=configurations,
        values=data["values"]
    )

    return responses.success_response(response_data.model_dump(by_alias=True))


@router.post("/entities/values")
async def save_entity_fields(
    payload: BulkFieldValuesUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """Save or update field values for an entity."""
    data = field_config_service.save_entity_fields(
        db, current_user.organization_id, payload)

    configurations = [
        FieldConfigurationPublic.model_validate(
            config).model_dump(by_alias=True)
        for config in data["configurations"]
    ]

    response_data = EntityFieldsResponse(
        configurations=configurations,
        values=data["values"]
    )

    return responses.success_response(response_data.model_dump(by_alias=True))


@router.post("/initialize/members")
async def initialize_default_member_fields(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.require_roles(*ADMIN_ROLES)),
):
    """Initialize default field configurations for members."""
    field_config_service.initialize_default_member_fields(
        db, current_user.organization_id)
    return responses.success_response(
        {"message": "Default member fields initialized successfully"}
    )
