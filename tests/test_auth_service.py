from __future__ import annotations

from uuid import uuid4

import pytest

from app.models.user import UserRole
from app.schemas.user import UserCreate, UserLogin
from app.services import auth_service
from app.utils import security
from app.utils.exceptions import AuthenticationError, ConflictError


@pytest.fixture
def user_payload() -> UserCreate:
    unique = uuid4().hex
    return UserCreate(
        email=f"new.user+{unique}@Example.com",
        password="Sup3rSecret!1",
        fullName="New User",
        displayName="Newbie",
    )


def test_create_user_lowercases_email_and_hashes_password(db, user_payload):
    user = auth_service.create_user(db, user_payload, role=UserRole.ADMIN)

    assert user.email == user_payload.email.lower()
    assert user.role == UserRole.ADMIN
    assert user.password_hash != user_payload.password
    assert security.verify_password(user_payload.password, user.password_hash)


def test_create_user_with_duplicate_email_raises_conflict(db, user_payload):
    auth_service.create_user(db, user_payload)

    with pytest.raises(ConflictError):
        auth_service.create_user(db, user_payload)


def test_authenticate_user_success_and_invalid_password(db, user_payload):
    created = auth_service.create_user(db, user_payload)

    login_payload = UserLogin(email=user_payload.email, password=user_payload.password)
    authenticated = auth_service.authenticate_user(db, login_payload)
    assert authenticated.id == created.id

    with pytest.raises(AuthenticationError):
        auth_service.authenticate_user(db, UserLogin(email=user_payload.email, password="WrongPass999"))


def test_authenticate_user_missing_account(db):
    with pytest.raises(AuthenticationError):
        auth_service.authenticate_user(
            db,
            UserLogin(email="missing@example.com", password="Whatever123"),
        )


def test_issue_tokens_include_expected_claims(db, user_payload):
    user = auth_service.create_user(db, user_payload, role=UserRole.MINISTRY_LEADER)

    access, refresh, expires = auth_service.issue_tokens(user)
    assert isinstance(access, str) and isinstance(refresh, str)
    assert expires > 0

    access_claims = security.decode_token(access)
    assert access_claims["sub"] == user.id
    assert access_claims["role"] == user.role.value

    fresh_access, access_expires = auth_service.issue_access_token(user)
    assert access_expires > 0
    refreshed_claims = security.decode_token(fresh_access)
    assert refreshed_claims["sub"] == user.id
    assert refreshed_claims["role"] == user.role.value
