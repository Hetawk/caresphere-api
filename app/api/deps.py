"""Reusable FastAPI dependencies."""

from __future__ import annotations

from typing import Annotated, Callable

from fastapi import Depends, Header
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, UserRole, UserStatus
from app.utils.exceptions import AuthenticationError, AuthorizationError
from app.utils.security import decode_token

async def get_current_user(
    db: Session = Depends(get_db),
    authorization: Annotated[str | None, Header(alias="Authorization")] = None,
) -> User:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise AuthenticationError("Missing bearer token")

    token = authorization.split(" ", 1)[1]
    try:
        payload = decode_token(token)
    except ValueError as exc:  # pragma: no cover - surfaces as 401
        raise AuthenticationError("Invalid token") from exc

    user_id = payload.get("sub")
    if not user_id:
        raise AuthenticationError("Invalid token payload")

    user = db.get(User, user_id)
    if not user:
        raise AuthenticationError("User not found")
    if user.status != UserStatus.ACTIVE:
        raise AuthorizationError("User account is not active")

    return user

def require_roles(*roles: UserRole | str) -> Callable[[User], User]:
    allowed = {role if isinstance(role, UserRole) else UserRole(role) for role in roles}

    async def dependency(current_user: Annotated[User, Depends(get_current_user)]) -> User:
        if allowed and current_user.role not in allowed:
            raise AuthorizationError("You do not have permission to perform this action")
        return current_user

    return dependency
