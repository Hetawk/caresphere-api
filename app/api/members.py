"""Member management routes."""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api import deps
from app.config import settings
from app.database import get_db
from app.models.member import MemberStatus
from app.models.user import User, UserRole
from app.schemas.member import (
    MemberActivityPublic,
    MemberCreate,
    MemberNoteCreate,
    MemberNotePublic,
    MemberPublic,
    MemberSearchPayload,
    MemberUpdate,
)
from app.services import member_service
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
async def list_members(
    page: int = Query(settings.PAGE_DEF, ge=1),
    limit: int = Query(settings.PAGE_SIZE_DEF, ge=1,
                       le=settings.PAGE_SIZE_MAX),
    status_filter: str | None = Query(None, alias="status"),
    search: str | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.require_roles(*MANAGER_ROLES)),
):
    try:
        status_enum = MemberStatus(status_filter) if status_filter else None
    except ValueError as exc:
        raise ValidationError({"status": "Invalid status value"}) from exc
    items, total = member_service.list_members(
        db,
        page=page,
        limit=limit,
        status_filter=status_enum,
        search=search,
        organization_id=current_user.organization_id,  # Filter by user's organization
    )
    pagination_meta = pagination.paginate_metadata(
        total=total, page=page, limit=limit)
    payload = {
        "members": [MemberPublic.model_validate(item).model_dump(by_alias=True) for item in items],
        "pagination": pagination_meta,
    }
    return responses.success_response(payload, metadata={"pagination": pagination_meta})


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_member(
    payload: MemberCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.require_roles(*MANAGER_ROLES)),
):
    member = member_service.create_member(
        db, payload, current_user=current_user)
    body = MemberPublic.model_validate(member).model_dump(by_alias=True)
    return responses.success_response(body, status_code=status.HTTP_201_CREATED)


@router.get("/{member_id}")
async def get_member(member_id: str, db: Session = Depends(get_db), _: User = Depends(deps.require_roles(*MANAGER_ROLES))):
    member = member_service.get_member(db, member_id)
    return responses.success_response(MemberPublic.model_validate(member).model_dump(by_alias=True))


@router.put("/{member_id}")
async def update_member(
    member_id: str,
    payload: MemberUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(deps.require_roles(*MANAGER_ROLES)),
):
    member = member_service.update_member(db, member_id, payload)
    return responses.success_response(MemberPublic.model_validate(member).model_dump(by_alias=True))


@router.delete("/{member_id}")
async def delete_member(
    member_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(deps.require_roles(
        UserRole.ADMIN, UserRole.SUPER_ADMIN)),
):
    member_service.delete_member(db, member_id)
    return responses.success_response({"message": "Member deleted successfully"})


@router.post("/search")
async def search_members(
    payload: MemberSearchPayload,
    db: Session = Depends(get_db),
    _: User = Depends(deps.require_roles(*MANAGER_ROLES)),
):
    items, total = member_service.search_members(db, payload)
    pagination_meta = pagination.paginate_metadata(
        total=total, page=payload.page, limit=payload.limit)
    data = {
        "members": [MemberPublic.model_validate(item).model_dump(by_alias=True) for item in items],
        "pagination": pagination_meta,
    }
    return responses.success_response(data, metadata={"pagination": pagination_meta})


@router.get("/{member_id}/notes")
async def list_member_notes(
    member_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(deps.require_roles(*MANAGER_ROLES)),
):
    notes = member_service.list_notes(db, member_id)
    data = [MemberNotePublic.model_validate(
        note).model_dump(by_alias=True) for note in notes]
    return responses.success_response({"notes": data})


@router.post("/{member_id}/notes", status_code=status.HTTP_201_CREATED)
async def add_member_note(
    member_id: str,
    payload: MemberNoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.require_roles(*MANAGER_ROLES)),
):
    note = member_service.add_note(
        db, member_id, payload, current_user=current_user)
    body = MemberNotePublic.model_validate(note).model_dump(by_alias=True)
    return responses.success_response(body, status_code=status.HTTP_201_CREATED)


@router.get("/{member_id}/activities")
async def list_member_activities(
    member_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(deps.require_roles(*MANAGER_ROLES)),
):
    activities = member_service.list_activities(db, member_id)
    data = [MemberActivityPublic.model_validate(
        item).model_dump(by_alias=True) for item in activities]
    return responses.success_response({"activities": data})
