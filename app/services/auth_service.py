"""Business logic for authentication and user management."""

from __future__ import annotations

import secrets
from datetime import datetime, timedelta
from typing import Optional, Tuple

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.config import settings
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserLogin
from app.utils import security
from app.utils.exceptions import AuthenticationError, ConflictError, ValidationError


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


def change_password(db: Session, user: User, current_password: str, new_password: str) -> None:
    """Change user password after verifying current password."""
    # Verify current password
    if not security.verify_password(current_password, user.password_hash):
        raise AuthenticationError("Current password is incorrect")

    # Validate new password is different
    if current_password == new_password:
        raise ValidationError(
            {"newPassword": "New password must be different from current password"})

    # Update password
    user.password_hash = security.get_password_hash(new_password)
    user.updated_at = datetime.utcnow()
    db.commit()


def generate_reset_token() -> str:
    """Generate a 6-digit numeric token for password reset."""
    return ''.join([str(secrets.randbelow(10)) for _ in range(6)])


def initiate_password_reset(db: Session, email: str) -> Tuple[User, str]:
    """
    Initiate password reset flow by generating a token.
    Returns user and token. In production, send token via email.
    Token expires in 1 hour.
    """
    user = db.query(User).filter(User.email == email.lower()).first()
    if not user:
        raise ValidationError(
            {"email": "No user found with this email address"})

    # Generate reset token
    token = generate_reset_token()
    token_hash = security.hash_password(token)  # Hash the token for storage

    # Store token and expiry (you'll need to add these fields to User model)
    user.reset_token_hash = token_hash
    user.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
    user.updated_at = datetime.utcnow()
    db.commit()

    return user, token


def reset_password_with_token(
    db: Session,
    email: str,
    token: str,
    new_password: str
) -> User:
    """
    Reset password using token from forgot password flow.
    Validates token and expiry before resetting password.
    """
    user = db.query(User).filter(User.email == email.lower()).first()
    if not user:
        raise ValidationError({"email": "Invalid email or token"})

    # Check if token exists and hasn't expired
    if not user.reset_token_hash or not user.reset_token_expires:
        raise ValidationError(
            {"token": "No password reset requested for this account"})

    if datetime.utcnow() > user.reset_token_expires:
        raise ValidationError(
            {"token": "Password reset token has expired. Please request a new one"})

    # Verify token
    if not security.verify_password(token, user.reset_token_hash):
        raise ValidationError({"token": "Invalid or expired token"})

    # Update password and clear reset token
    user.password_hash = security.get_password_hash(new_password)
    user.reset_token_hash = None
    user.reset_token_expires = None
    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)

    return user


def verify_email_with_token(db: Session, email: str, token: str) -> User:
    """
    Verify user email using verification token.
    Similar flow to password reset but marks email as verified.
    """
    user = db.query(User).filter(User.email == email.lower()).first()
    if not user:
        raise ValidationError({"email": "Invalid email or token"})

    if user.email_verified:
        raise ValidationError({"email": "Email is already verified"})

    # Check verification token (assumes similar fields as reset token)
    if not hasattr(user, 'verification_token_hash') or not user.verification_token_hash:
        raise ValidationError(
            {"token": "No verification token found for this account"})

    # Verify token
    if not security.verify_password(token, user.verification_token_hash):
        raise ValidationError({"token": "Invalid verification token"})

    # Mark email as verified
    user.email_verified = True
    user.verification_token_hash = None
    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)

    return user
