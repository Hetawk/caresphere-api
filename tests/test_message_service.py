from __future__ import annotations

from datetime import datetime

import pytest

from sqlalchemy.orm import Session

from app.models.user import User, UserRole
from app.models.member import Member
from app.schemas.message import MessageCreate
from app.services import message_service
from app.models.message import MessageStatus, RecipientStatus


@pytest.fixture
def current_user(db: Session):
    from uuid import uuid4

    user = User(email=f"tester+{uuid4()}@example.com", password_hash="x", full_name="Test User", role=UserRole.ADMIN)
    db.add(user)
    db.flush()
    db.commit()
    return user


@pytest.fixture
def members(db: Session):
    m1 = Member(first_name="Alice", last_name="A", email="alice@example.com")
    m2 = Member(first_name="Bob", last_name="B", email="bob@example.com")
    db.add_all([m1, m2])
    db.flush()
    db.commit()
    return [m1, m2]


def test_create_and_send_message(db: Session, current_user: User, members: list[Member]):
    payload = MessageCreate(
        title="Hello",
        content="Hi there",
        recipient_member_ids=[],
        recipient_override_list=[{"recipient_email": "override@example.com"}],
    )

    message = message_service.create_message(db, payload, current_user=current_user)
    assert message.title == "Hello"
    # verify recipients were correctly created
    from app.models.message import MessageRecipient

    # The internal builder should return recipients for the override entries
    built = message_service._build_recipients(
        db, message_id=message.id, member_ids=[], overrides=[{"recipient_email": "override@example.com"}]
    )
    assert len(built) == 1

    recipients = db.query(MessageRecipient).filter(MessageRecipient.message_id == message.id).all()
    assert len(recipients) == 1
    db.refresh(message)
    assert message.recipient_count == 1
    assert message.status == MessageStatus.DRAFT

    # Send the message
    sent = message_service.send_message(db, message.id)
    assert sent.status == MessageStatus.SENT
    assert sent.sent_at is not None
    assert sent.recipient_count == 1
    # Check recipient statuses
    assert all(r.status == RecipientStatus.SENT for r in sent.recipients)

    analytics = message_service.get_message_analytics(db, message.id)
    assert analytics["totalSent"] == 1
    assert analytics["totalDelivered"] == 1


def test_list_sender_profiles_and_create(db: Session, current_user: User):
    # initially none
    profiles = message_service.list_sender_profiles(db, current_user=current_user)
    assert profiles == []

    # create via schema with explicit python names
    from app.schemas.message import MessageSenderProfileCreate
    from app.models.message import SenderChannel

    payload = MessageSenderProfileCreate(
        label="Test Email",
        channel=SenderChannel.EMAIL,
        sender_email="noreply@example.com",
        is_default=True,
    )
    profile = message_service.create_sender_profile(db, payload, current_user=current_user)

    assert profile.user_id == current_user.id
    assert profile.is_default

    fetched = message_service.list_sender_profiles(db, current_user=current_user)
    assert len(fetched) == 1

 