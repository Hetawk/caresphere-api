"""Security utilities for hashing and JWT handling."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings

_pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=settings.BCRYPT_ROUNDS,
)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return _pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return _pwd_context.hash(password)


def create_token(
    *,
    subject: str,
    expires_delta: timedelta,
    additional_claims: Optional[Dict[str, Any]] = None,
) -> str:
    payload: Dict[str, Any] = {
        "sub": subject,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + expires_delta,
    }
    if additional_claims:
        payload.update(additional_claims)

    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)


def create_access_token(*, subject: str, claims: Optional[Dict[str, Any]] = None) -> str:
    return create_token(
        subject=subject,
        expires_delta=timedelta(seconds=settings.JWT_EXP),
        additional_claims=claims,
    )


def create_refresh_token(*, subject: str) -> str:
    return create_token(
        subject=subject,
        expires_delta=timedelta(seconds=settings.JWT_REFRESH_EXP),
    )


def decode_token(token: str) -> Dict[str, Any]:
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALG])
    except JWTError as exc:  # pragma: no cover - jose raises JWTError for all decode issues
        raise ValueError("Invalid token") from exc
