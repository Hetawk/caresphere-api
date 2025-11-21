"""Service for managing field configurations and values."""

from __future__ import annotations

from typing import Any

from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.models.field_config import EntityType, FieldConfiguration, FieldValue
from app.models.organization import Organization
from app.models.user import User
from app.schemas.field_config import (
    BulkFieldValuesUpdate,
    FieldConfigurationCreate,
    FieldConfigurationUpdate,
)
from app.utils.exceptions import NotFoundError


def create_field_configuration(
    db: Session, organization_id: str, payload: FieldConfigurationCreate, current_user: User
) -> FieldConfiguration:
    """Create a new field configuration."""
    # Verify organization exists
    org = db.query(Organization).filter(
        Organization.id == organization_id).first()
    if not org:
        raise NotFoundError("Organization not found")

    field_config = FieldConfiguration(
        organization_id=organization_id,
        entity_type=payload.entityType,
        field_key=payload.fieldKey,
        field_label=payload.fieldLabel,
        field_type=payload.fieldType,
        description=payload.description,
        placeholder=payload.placeholder,
        options=payload.options,
        validation_rules=payload.validationRules,
        is_required=payload.isRequired,
        is_visible=payload.isVisible,
        is_searchable=payload.isSearchable,
        display_order=payload.displayOrder,
        default_value=payload.defaultValue,
        group_name=payload.groupName,
    )

    db.add(field_config)
    db.commit()
    db.refresh(field_config)
    return field_config


def list_field_configurations(
    db: Session, organization_id: str, entity_type: EntityType | None = None
) -> list[FieldConfiguration]:
    """List all field configurations for an organization."""
    query = db.query(FieldConfiguration).filter(
        FieldConfiguration.organization_id == organization_id
    )

    if entity_type:
        query = query.filter(FieldConfiguration.entity_type == entity_type)

    return query.order_by(FieldConfiguration.display_order, FieldConfiguration.field_label).all()


def get_field_configuration(db: Session, config_id: str) -> FieldConfiguration:
    """Get a specific field configuration."""
    config = db.query(FieldConfiguration).filter(
        FieldConfiguration.id == config_id).first()
    if not config:
        raise NotFoundError("Field configuration not found")
    return config


def update_field_configuration(
    db: Session, config_id: str, payload: FieldConfigurationUpdate
) -> FieldConfiguration:
    """Update a field configuration."""
    config = get_field_configuration(db, config_id)

    update_data = payload.model_dump(exclude_unset=True, by_alias=False)
    for key, value in update_data.items():
        setattr(config, key, value)

    db.commit()
    db.refresh(config)
    return config


def delete_field_configuration(db: Session, config_id: str) -> None:
    """Delete a field configuration and its values."""
    config = get_field_configuration(db, config_id)

    # Delete all field values associated with this configuration
    db.query(FieldValue).filter(
        FieldValue.field_configuration_id == config_id).delete()

    db.delete(config)
    db.commit()


def get_entity_fields(
    db: Session, organization_id: str, entity_type: EntityType, entity_id: str
) -> dict[str, Any]:
    """Get all field configurations and values for a specific entity."""
    # Get configurations
    configurations = list_field_configurations(
        db, organization_id, entity_type)

    # Get values
    values_query = (
        db.query(FieldValue)
        .join(FieldConfiguration)
        .filter(
            and_(
                FieldConfiguration.organization_id == organization_id,
                FieldValue.entity_type == entity_type,
                FieldValue.entity_id == entity_id,
            )
        )
    )

    values = values_query.all()

    # Build response
    values_dict = {
        db.query(FieldConfiguration)
        .filter(FieldConfiguration.id == v.field_configuration_id)
        .first()
        .field_key: v.value
        for v in values
    }

    return {"configurations": configurations, "values": values_dict}


def save_entity_fields(
    db: Session, organization_id: str, payload: BulkFieldValuesUpdate
) -> dict[str, Any]:
    """Save or update field values for an entity."""
    # Get configurations
    configurations = list_field_configurations(
        db, organization_id, payload.entityType)
    config_map = {config.field_key: config for config in configurations}

    # Process each field value
    for field_key, value in payload.values.items():
        if field_key not in config_map:
            continue  # Skip unknown fields

        config = config_map[field_key]

        # Check if value already exists
        existing_value = (
            db.query(FieldValue)
            .filter(
                and_(
                    FieldValue.field_configuration_id == config.id,
                    FieldValue.entity_type == payload.entityType,
                    FieldValue.entity_id == payload.entityId,
                )
            )
            .first()
        )

        if existing_value:
            # Update existing value
            existing_value.value = str(value) if value is not None else None
        else:
            # Create new value
            new_value = FieldValue(
                field_configuration_id=config.id,
                entity_type=payload.entityType,
                entity_id=payload.entityId,
                value=str(value) if value is not None else None,
            )
            db.add(new_value)

    db.commit()

    # Return updated fields
    return get_entity_fields(db, organization_id, payload.entityType, payload.entityId)


def initialize_default_member_fields(db: Session, organization_id: str) -> None:
    """Initialize default field configurations for members (based on CSV structure)."""
    default_fields = [
        {
            "entity_type": EntityType.MEMBER,
            "field_key": "work_school",
            "field_label": "Work/School",
            "field_type": "text",
            "description": "Place of work or educational institution",
            "placeholder": "e.g., Shandong University",
            "group_name": "Professional",
            "display_order": 1,
        },
        {
            "entity_type": EntityType.MEMBER,
            "field_key": "whatsapp_number",
            "field_label": "WhatsApp Number",
            "field_type": "phone",
            "description": "WhatsApp contact number",
            "placeholder": "+1234567890",
            "group_name": "Contact",
            "display_order": 2,
        },
        {
            "entity_type": EntityType.MEMBER,
            "field_key": "wechat_id",
            "field_label": "WeChat ID",
            "field_type": "text",
            "description": "WeChat user ID",
            "placeholder": "WeChat ID",
            "group_name": "Contact",
            "display_order": 3,
        },
        {
            "entity_type": EntityType.MEMBER,
            "field_key": "hear_about_us",
            "field_label": "How did you hear about us?",
            "field_type": "select",
            "description": "How this person learned about your organization",
            "options": [
                "Friend/Family",
                "Social Media",
                "Internet Search",
                "Event",
                "Word of Mouth",
                "Other",
            ],
            "group_name": "Engagement",
            "display_order": 4,
        },
        {
            "entity_type": EntityType.MEMBER,
            "field_key": "involvement",
            "field_label": "Areas of Interest",
            "field_type": "multiselect",
            "description": "Ministries or groups they want to join",
            "options": [
                "Prayer Ministry",
                "Worship Ministry",
                "Usher Ministry",
                "Media Team",
                "Music Department",
                "Children Ministry",
                "Small Groups",
                "Leadership",
                "Welfare Ministry",
            ],
            "group_name": "Engagement",
            "display_order": 5,
        },
        {
            "entity_type": EntityType.MEMBER,
            "field_key": "comments",
            "field_label": "Additional Comments",
            "field_type": "textarea",
            "description": "Any additional notes or comments",
            "placeholder": "Share any additional information...",
            "group_name": "Notes",
            "display_order": 6,
        },
        {
            "entity_type": EntityType.MEMBER,
            "field_key": "consent_given",
            "field_label": "Data Usage Consent",
            "field_type": "checkbox",
            "description": "Consent to use and store personal data",
            "default_value": "false",
            "group_name": "Legal",
            "display_order": 7,
        },
    ]

    for field_data in default_fields:
        # Check if field already exists
        existing = (
            db.query(FieldConfiguration)
            .filter(
                and_(
                    FieldConfiguration.organization_id == organization_id,
                    FieldConfiguration.entity_type == field_data["entity_type"],
                    FieldConfiguration.field_key == field_data["field_key"],
                )
            )
            .first()
        )

        if not existing:
            field_config = FieldConfiguration(
                organization_id=organization_id, **field_data)
            db.add(field_config)

    db.commit()
