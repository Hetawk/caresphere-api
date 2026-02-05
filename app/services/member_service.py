"""Member domain services."""

from __future__ import annotations

from typing import List, Tuple

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.models.member import Member, MemberActivity, MemberNote, MemberStatus
from app.models.user import User
from app.schemas.member import MemberCreate, MemberNoteCreate, MemberSearchPayload, MemberUpdate
from app.utils.exceptions import NotFoundError


def list_members(
    db: Session,
    *,
    page: int,
    limit: int,
    status_filter: MemberStatus | None = None,
    search: str | None = None,
    organization_id: str | None = None,
) -> Tuple[List[Member], int]:
    query = db.query(Member)

    # Filter by organization if provided
    if organization_id:
        query = query.filter(Member.organization_id == organization_id)

    if status_filter:
        query = query.filter(Member.member_status == status_filter)

    if search:
        like = f"%{search.lower()}%"
        full_name = func.concat(
            func.coalesce(func.lower(Member.first_name), ""),
            " ",
            func.coalesce(func.lower(Member.last_name), ""),
        )
        email_lower = func.coalesce(func.lower(Member.email), "")
        query = query.filter(or_(full_name.like(like), email_lower.like(like)))

    total = query.count()
    items = (
        query.order_by(Member.last_name.asc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )
    return items, total


def get_member(db: Session, member_id: str) -> Member:
    member = db.get(Member, member_id)
    if not member:
        raise NotFoundError("Member", member_id)
    return member


def create_member(db: Session, payload: MemberCreate, *, current_user: User) -> Member:
    data = payload.model_dump(by_alias=True)
    # Automatically assign member to current user's organization
    member = Member(
        **data,
        created_by=current_user.id,
        organization_id=current_user.organization_id
    )
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


def update_member(db: Session, member_id: str, payload: MemberUpdate) -> Member:
    member = get_member(db, member_id)
    update_data = payload.model_dump(exclude_unset=True, by_alias=True)
    for key, value in update_data.items():
        setattr(member, key, value)
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


def delete_member(db: Session, member_id: str) -> None:
    member = get_member(db, member_id)
    db.delete(member)
    db.commit()


def search_members(db: Session, payload: MemberSearchPayload, organization_id: str | None = None) -> Tuple[List[Member], int]:
    query = db.query(Member)

    # Filter by organization if provided
    if organization_id:
        query = query.filter(Member.organization_id == organization_id)

    filters = payload.filters or {}

    status_values = filters.get("status")
    if status_values:
        statuses = [MemberStatus(value) for value in status_values]
        query = query.filter(Member.member_status.in_(statuses))

    search_term = payload.query
    if search_term:
        like = f"%{search_term.lower()}%"
        full_name = func.concat(
            func.coalesce(func.lower(Member.first_name), ""),
            " ",
            func.coalesce(func.lower(Member.last_name), ""),
        )
        email_lower = func.coalesce(func.lower(Member.email), "")
        query = query.filter(or_(full_name.like(like), email_lower.like(like)))

    if tags := filters.get("tags"):
        query = query.filter(Member.tags.contains(tags))

    total = query.count()
    items = (
        query.order_by(Member.last_name.asc())
        .offset((payload.page - 1) * payload.limit)
        .limit(payload.limit)
        .all()
    )
    return items, total


def list_notes(db: Session, member_id: str) -> List[MemberNote]:
    get_member(db, member_id)
    return (
        db.query(MemberNote)
        .filter(MemberNote.member_id == member_id)
        .order_by(MemberNote.created_at.desc())
        .all()
    )


def add_note(
    db: Session,
    member_id: str,
    payload: MemberNoteCreate,
    *,
    current_user: User,
) -> MemberNote:
    get_member(db, member_id)
    data = payload.model_dump(by_alias=True)
    note = MemberNote(
        member_id=member_id,
        created_by=current_user.id,
        **data,
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


def list_activities(db: Session, member_id: str) -> List[MemberActivity]:
    get_member(db, member_id)
    return (
        db.query(MemberActivity)
        .filter(MemberActivity.member_id == member_id)
        .order_by(MemberActivity.created_at.desc())
        .limit(100)
        .all()
    )
