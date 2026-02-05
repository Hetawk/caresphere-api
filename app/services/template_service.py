"""Template service layer."""

from __future__ import annotations

from typing import List, Tuple

from sqlalchemy.orm import Session

from app.models.template import Template, TemplateType
from app.models.user import User
from app.schemas.template import TemplateCreate, TemplateUpdate
from app.utils.exceptions import NotFoundError


def list_templates(
    db: Session,
    *,
    page: int,
    limit: int,
    template_type: TemplateType | None = None,
) -> Tuple[List[Template], int]:
    query = db.query(Template)
    if template_type:
        query = query.filter(Template.template_type == template_type)
    total = query.count()
    items = (
        query.order_by(Template.created_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )
    return items, total


def create_template(db: Session, payload: TemplateCreate, *, current_user: User) -> Template:
    template = Template(
        name=payload.name,
        description=payload.description,
        template_type=payload.templateType,
        category=payload.category,
        subject=payload.subject,
        content=payload.content,
        variables=payload.variables,
        thumbnail_url=payload.thumbnailUrl,
        is_active=payload.isActive,
        created_by=current_user.id,
    )
    db.add(template)
    db.commit()
    db.refresh(template)
    return template


def get_template(db: Session, template_id: str) -> Template:
    template = db.get(Template, template_id)
    if not template:
        raise NotFoundError("Template", template_id)
    return template


def update_template(db: Session, template_id: str, payload: TemplateUpdate) -> Template:
    template = get_template(db, template_id)
    update_data = payload.model_dump(exclude_unset=True, by_alias=True)
    for key, value in update_data.items():
        setattr(template, key, value)
    db.add(template)
    db.commit()
    db.refresh(template)
    return template


def delete_template(db: Session, template_id: str) -> None:
    template = get_template(db, template_id)
    db.delete(template)
    db.commit()
