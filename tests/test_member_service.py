from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from app.models.member import MemberStatus, MemberActivity
from app.models.user import User, UserRole
from app.schemas.member import MemberCreate, MemberNoteCreate, MemberSearchPayload, MemberUpdate
from app.services import member_service
from app.utils.exceptions import NotFoundError


@pytest.fixture
def member_admin(db: Session) -> User:
    user = User(
        email=f"member-admin+{uuid4().hex}@example.com",
        password_hash="hash",
        full_name="Manager",
        role=UserRole.ADMIN,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _member_payload(*, first: str, last: str, email: str, status: MemberStatus = MemberStatus.ACTIVE, **extra) -> MemberCreate:
    base = {
        "first_name": first,
        "last_name": last,
        "email": email,
        "member_status": status,
        "phone": extra.get("phone", "555-555-0000"),
        "city": extra.get("city", "Austin"),
        "state": extra.get("state", "TX"),
        "country": extra.get("country", "USA"),
        "tags": extra.get("tags", []),
        "custom_fields": extra.get("custom_fields", {}),
    }
    return MemberCreate(**base)


def _create_member(db: Session, current_user: User, **kwargs):
    payload = _member_payload(**kwargs)
    return member_service.create_member(db, payload, current_user=current_user)


def test_list_members_supports_filters_and_search(db: Session, member_admin: User):
    _create_member(
        db,
        member_admin,
        first="Alice",
        last="Alpha",
        email=f"alice+{uuid4().hex}@example.com",
        status=MemberStatus.ACTIVE,
    )
    _create_member(
        db,
        member_admin,
        first="Alicia",
        last="Beta",
        email=f"alicia+{uuid4().hex}@example.com",
        status=MemberStatus.ACTIVE,
    )
    _create_member(
        db,
        member_admin,
        first="Bob",
        last="Builder",
        email=f"bob+{uuid4().hex}@example.com",
        status=MemberStatus.INACTIVE,
    )

    items, total = member_service.list_members(
        db,
        page=1,
        limit=10,
        status_filter=MemberStatus.ACTIVE,
        search="ali",
    )

    assert total == 2
    assert [item.first_name for item in items] == ["Alice", "Alicia"]


def test_search_members_by_status_and_tags(db: Session, member_admin: User):
    _create_member(
        db,
        member_admin,
        first="Carlos",
        last="Cedar",
        email=f"carlos+{uuid4().hex}@example.com",
        status=MemberStatus.ACTIVE,
        tags=["crew"],
    )
    target = _create_member(
        db,
        member_admin,
        first="Clara",
        last="Cypress",
        email=f"clara+{uuid4().hex}@example.com",
        status=MemberStatus.INACTIVE,
        tags=["vip", "crew"],
    )

    payload = MemberSearchPayload(
        query="cl",
        filters={"status": [MemberStatus.INACTIVE.value]},
        page=1,
        limit=5,
    )
    items, total = member_service.search_members(db, payload)

    assert total == 1
    assert items[0].id == target.id


def test_update_and_delete_member(db: Session, member_admin: User):
    member = _create_member(
        db,
        member_admin,
        first="Dana",
        last="Delta",
        email=f"dana+{uuid4().hex}@example.com",
    )

    update_payload = MemberUpdate(first_name="Danielle", city="Dallas")
    updated = member_service.update_member(db, member.id, update_payload)

    assert updated.first_name == "Danielle"
    assert updated.city == "Dallas"

    member_service.delete_member(db, member.id)
    with pytest.raises(NotFoundError):
        member_service.get_member(db, member.id)


def test_add_note_and_list_notes(db: Session, member_admin: User):
    member = _create_member(
        db,
        member_admin,
        first="Evan",
        last="Echo",
        email=f"evan+{uuid4().hex}@example.com",
    )

    note_payload = MemberNoteCreate(note="Follow up", note_type="call", is_private=True)
    note = member_service.add_note(db, member.id, note_payload, current_user=member_admin)

    notes = member_service.list_notes(db, member.id)
    assert len(notes) == 1
    assert notes[0].id == note.id
    assert notes[0].note == "Follow up"


def test_list_activities_orders_most_recent_first(db: Session, member_admin: User):
    member = _create_member(
        db,
        member_admin,
        first="Frank",
        last="Forest",
        email=f"frank+{uuid4().hex}@example.com",
    )

    first_activity = MemberActivity(
        member_id=member.id,
        activity_type="call",
        description="Intro call",
        created_by=member_admin.id,
    )
    follow_up = MemberActivity(
        member_id=member.id,
        activity_type="follow_up",
        description="Second touch",
        created_by=member_admin.id,
    )
    first_activity.created_at = datetime.now(timezone.utc) - timedelta(minutes=5)
    follow_up.created_at = datetime.now(timezone.utc)
    db.add_all([first_activity, follow_up])
    db.commit()

    activities = member_service.list_activities(db, member.id)
    assert [activity.activity_type for activity in activities] == ["follow_up", "call"]


def test_get_member_not_found(db: Session):
    with pytest.raises(NotFoundError):
        member_service.get_member(db, "non-existent-id")
