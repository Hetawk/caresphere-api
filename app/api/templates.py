"""Template routes."""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api import deps
from app.config import settings
from app.database import get_db
from app.models.template import TemplateType
from app.models.user import User, UserRole
from app.schemas.template import TemplateCreate, TemplatePublic, TemplateUpdate
from app.services import template_service
from app.utils import pagination, responses
from app.utils.exceptions import ValidationError

router = APIRouter()

MANAGER_ROLES = (
    UserRole.SUPER_ADMIN,
    UserRole.ADMIN,
    UserRole.MINISTRY_LEADER,
    UserRole.VOLUNTEER,
)


@router.get("/")
async def list_templates(
    page: int = Query(settings.PAGE_DEF, ge=1),
    limit: int = Query(settings.PAGE_SIZE_DEF, ge=1, le=settings.PAGE_SIZE_MAX),
    template_type: str | None = Query(None, alias="type"),
    db: Session = Depends(get_db),
    _: User = Depends(deps.require_roles(*MANAGER_ROLES)),
):
    try:
        template_enum = TemplateType(template_type) if template_type else None
    except ValueError as exc:
        raise ValidationError({"type": "Invalid template type"}) from exc
    items, total = template_service.list_templates(
        db,
        page=page,
        limit=limit,
        template_type=template_enum,
    )
    pagination_meta = pagination.paginate_metadata(total=total, page=page, limit=limit)
    data = {
        "templates": [TemplatePublic.model_validate(item).model_dump(by_alias=True) for item in items],
        "pagination": pagination_meta,
    }
    return responses.success_response(data, metadata={"pagination": pagination_meta})


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_template(
    payload: TemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.require_roles(*MANAGER_ROLES)),
):
    template = template_service.create_template(db, payload, current_user=current_user)
    body = TemplatePublic.model_validate(template).model_dump(by_alias=True)
    return responses.success_response(body, status_code=status.HTTP_201_CREATED)


@router.get("/{template_id}")
async def get_template(
    template_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(deps.require_roles(*MANAGER_ROLES)),
):
    template = template_service.get_template(db, template_id)
    return responses.success_response(TemplatePublic.model_validate(template).model_dump(by_alias=True))


@router.put("/{template_id}")
async def update_template(
    template_id: str,
    payload: TemplateUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(deps.require_roles(*MANAGER_ROLES)),
):
    template = template_service.update_template(db, template_id, payload)
    return responses.success_response(TemplatePublic.model_validate(template).model_dump(by_alias=True))


@router.delete("/{template_id}")
async def delete_template(
    template_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(deps.require_roles(UserRole.ADMIN, UserRole.SUPER_ADMIN)),
):
    template_service.delete_template(db, template_id)
    return responses.success_response({"message": "Template deleted successfully"})
