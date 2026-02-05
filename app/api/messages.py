"""Messaging routes."""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api import deps
from app.config import settings
from app.database import get_db
from app.models.message import MessageStatus
from app.models.user import User, UserRole
from app.schemas.message import (
    MessageAnalyticsResponse,
    MessageCreate,
    MessagePublic,
    MessageSenderProfileCreate,
    MessageSenderProfilePublic,
    MessageSenderProfileUpdate,
    MessageUpdate,
)
from app.services import message_service
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
async def list_messages(
    page: int = Query(settings.PAGE_DEF, ge=1),
    limit: int = Query(settings.PAGE_SIZE_DEF, ge=1, le=settings.PAGE_SIZE_MAX),
    status_filter: str | None = Query(None, alias="status"),
    message_type: str | None = Query(None, alias="type"),
    db: Session = Depends(get_db),
    _: User = Depends(deps.require_roles(*MANAGER_ROLES)),
):
    try:
        status_enum = MessageStatus(status_filter) if status_filter else None
    except ValueError as exc:
        raise ValidationError({"status": "Invalid status value"}) from exc
    items, total = message_service.list_messages(
        db,
        page=page,
        limit=limit,
        status_filter=status_enum,
        type_filter=message_type,
    )
    pagination_meta = pagination.paginate_metadata(total=total, page=page, limit=limit)
    data = {
        "messages": [MessagePublic.model_validate(item).model_dump(by_alias=True) for item in items],
        "pagination": pagination_meta,
    }
    return responses.success_response(data, metadata={"pagination": pagination_meta})


@router.get("/senders")
async def list_sender_profiles(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.require_roles(*MANAGER_ROLES)),
):
    profiles = message_service.list_sender_profiles(db, current_user=current_user)
    data = [MessageSenderProfilePublic.model_validate(profile).model_dump(by_alias=True) for profile in profiles]
    return responses.success_response({"senderProfiles": data})


@router.post("/senders", status_code=status.HTTP_201_CREATED)
async def create_sender_profile(
    payload: MessageSenderProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.require_roles(*MANAGER_ROLES)),
):
    profile = message_service.create_sender_profile(db, payload, current_user=current_user)
    body = MessageSenderProfilePublic.model_validate(profile).model_dump(by_alias=True)
    return responses.success_response(body, status_code=status.HTTP_201_CREATED)


@router.put("/senders/{profile_id}")
async def update_sender_profile(
    profile_id: str,
    payload: MessageSenderProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.require_roles(*MANAGER_ROLES)),
):
    profile = message_service.update_sender_profile(db, profile_id, payload, current_user=current_user)
    return responses.success_response(MessageSenderProfilePublic.model_validate(profile).model_dump(by_alias=True))


@router.delete("/senders/{profile_id}")
async def delete_sender_profile(
    profile_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.require_roles(*MANAGER_ROLES)),
):
    message_service.delete_sender_profile(db, profile_id, current_user=current_user)
    return responses.success_response({"message": "Sender profile deleted successfully"})


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_message(
    payload: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.require_roles(*MANAGER_ROLES)),
):
    message = message_service.create_message(db, payload, current_user=current_user)
    body = MessagePublic.model_validate(message).model_dump(by_alias=True)
    return responses.success_response(body, status_code=status.HTTP_201_CREATED)


@router.get("/{message_id}")
async def get_message(
    message_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(deps.require_roles(*MANAGER_ROLES)),
):
    message = message_service.get_message(db, message_id)
    return responses.success_response(MessagePublic.model_validate(message).model_dump(by_alias=True))


@router.put("/{message_id}")
async def update_message(
    message_id: str,
    payload: MessageUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(deps.require_roles(*MANAGER_ROLES)),
):
    message = message_service.update_message(db, message_id, payload)
    return responses.success_response(MessagePublic.model_validate(message).model_dump(by_alias=True))


@router.delete("/{message_id}")
async def delete_message(
    message_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(deps.require_roles(UserRole.ADMIN, UserRole.SUPER_ADMIN)),
):
    message_service.delete_message(db, message_id)
    return responses.success_response({"message": "Message deleted successfully"})


@router.post("/{message_id}/send")
async def send_message(
    message_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(deps.require_roles(*MANAGER_ROLES)),
):
    message = message_service.send_message(db, message_id)
    return responses.success_response(MessagePublic.model_validate(message).model_dump(by_alias=True))


@router.get("/{message_id}/analytics")
async def message_analytics(
    message_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(deps.require_roles(*MANAGER_ROLES)),
):
    analytics_data = message_service.get_message_analytics(db, message_id)
    body = MessageAnalyticsResponse(**analytics_data).model_dump()
    return responses.success_response(body)
