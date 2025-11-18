"""Business logic for authentication and user management."""

from __future__ import annotations

from typing import Tuple

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.config import settings
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserLogin
from app.utils import security
from app.utils.exceptions import AuthenticationError, ConflictError


def create_user(db: Session, payload: UserCreate, *, role: UserRole = UserRole.MEMBER) -> User:
    """Create a new user enforcing unique email constraint."""
    user = User(
        email=payload.email.lower(),
        full_name=payload.fullName,
        display_name=payload.displayName,
        password_hash=security.get_password_hash(payload.password),
        role=role,
    )

    db.add(user)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ConflictError("User with this email already exists") from exc

    db.refresh(user)
    return user


def authenticate_user(db: Session, payload: UserLogin) -> User:
    user = (
        db.query(User)
        .filter(User.email == payload.email.lower())
        .first()
    )
    if not user or not security.verify_password(payload.password, user.password_hash):
        raise AuthenticationError("Incorrect email or password")
    return user


def issue_tokens(user: User) -> Tuple[str, str, int]:
    expires_in = settings.JWT_EXP
    claims = {"email": user.email, "role": user.role.value}
    access = security.create_access_token(subject=user.id, claims=claims)
    refresh = security.create_refresh_token(subject=user.id)
    return access, refresh, expires_in


def issue_access_token(user: User) -> Tuple[str, int]:
    expires_in = settings.JWT_EXP
    claims = {"email": user.email, "role": user.role.value}
    access = security.create_access_token(subject=user.id, claims=claims)
    return access, expires_in
