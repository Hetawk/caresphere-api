"""Authentication routes."""

import logging

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api import deps
from app.config import settings
from app.database import get_db
from app.models.user import User
from app.schemas.user import (
    AuthResponse,
    ChangePasswordRequest,
    ForgotPasswordRequest,
    MessageResponse,
    RefreshRequest,
    RefreshResponse,
    ResetPasswordRequest,
    UserCreate,
    UserLogin,
    UserPublic,
    VerifyEmailRequest,
)
from app.services import auth_service
from app.services.transactional_email_service import (
    send_password_reset_email,
    send_verification_code_email,
    send_welcome_email,
)
from app.utils import responses, security
from app.utils.exceptions import AuthenticationError

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(payload: UserCreate, db: Session = Depends(get_db)):
    user = auth_service.create_user(db, payload)
    access, refresh, expires = auth_service.issue_tokens(user)

    # Send welcome email
    try:
        await send_welcome_email(
            to=user.email,
            user_name=user.full_name or user.email,
        )
        logger.info(f"Welcome email sent to {user.email}")
    except Exception as e:
        logger.error(f"Failed to send welcome email to {user.email}: {e}")
        # Don't fail registration if email fails

    response = AuthResponse(
        user=UserPublic.model_validate(user),
        accessToken=access,
        refreshToken=refresh,
        expiresIn=expires,
    )
    return responses.success_response(
        response.model_dump(by_alias=True), status_code=status.HTTP_201_CREATED
    )


@router.post("/login")
async def login_user(payload: UserLogin, db: Session = Depends(get_db)):
    user = auth_service.authenticate_user(db, payload)
    access, refresh, expires = auth_service.issue_tokens(user)
    response = AuthResponse(
        user=UserPublic.model_validate(user),
        accessToken=access,
        refreshToken=refresh,
        expiresIn=expires,
    )
    return responses.success_response(response.model_dump(by_alias=True))


@router.post("/refresh")
async def refresh_token(payload: RefreshRequest, db: Session = Depends(get_db)):
    try:
        claims = security.decode_token(payload.refreshToken)
    except ValueError as exc:
        raise AuthenticationError("Invalid refresh token") from exc

    user_id = claims.get("sub")
    if not user_id:
        raise AuthenticationError("Invalid refresh token")

    user = db.get(User, user_id)
    if not user:
        raise AuthenticationError("User not found for refresh token")

    access, expires = auth_service.issue_access_token(user)
    response = RefreshResponse(accessToken=access, expiresIn=expires)
    return responses.success_response(response.model_dump())


@router.get("/profile")
async def get_profile(current_user: User = Depends(deps.get_current_user)):
    profile = UserPublic.model_validate(current_user)
    return responses.success_response(profile.model_dump(by_alias=True))


@router.post("/logout")
async def logout_user(_: User = Depends(deps.get_current_user)):
    response = MessageResponse(message="Logged out successfully")
    return responses.success_response(response.model_dump())


@router.post("/change-password")
async def change_password(
    payload: ChangePasswordRequest,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(get_db),
):
    """Change password for authenticated user."""
    auth_service.change_password(
        db,
        current_user,
        payload.currentPassword,
        payload.newPassword
    )
    response = MessageResponse(message="Password changed successfully")
    return responses.success_response(response.model_dump())


@router.post("/forgot-password")
async def forgot_password(
    payload: ForgotPasswordRequest,
    db: Session = Depends(get_db),
):
    """Initiate password reset flow. Sends reset token via email."""
    try:
        user, token = auth_service.initiate_password_reset(db, payload.email)

        # Send password reset email via EKDSend
        try:
            # Build reset URL (adjust based on your frontend URL)
            reset_url = f"caresphere://reset-password?email={payload.email}&token={token}"

            await send_password_reset_email(
                to=user.email,
                user_name=user.full_name or user.email,
                reset_token=token,
                reset_url=reset_url,
                expires_in_hours=1,
            )
            logger.info(f"Password reset email sent to {payload.email}")
        except Exception as e:
            logger.error(f"Failed to send password reset email: {e}")
            # Still return success to not leak info, but log the error

        # In debug mode, also return the token for testing
        if settings.DEBUG:
            response = MessageResponse(
                message=f"Password reset token sent to {payload.email}. Token: {token} (debug mode)"
            )
        else:
            response = MessageResponse(
                message=f"If an account exists with {payload.email}, a password reset link has been sent"
            )
        return responses.success_response(response.model_dump())
    except Exception:
        # Return same message even if user not found (security best practice)
        response = MessageResponse(
            message=f"If an account exists with {payload.email}, a password reset link has been sent"
        )
        return responses.success_response(response.model_dump())


@router.post("/reset-password")
async def reset_password(
    payload: ResetPasswordRequest,
    db: Session = Depends(get_db),
):
    """Reset password using token from forgot-password flow."""
    auth_service.reset_password_with_token(
        db,
        payload.email,
        payload.token,
        payload.newPassword
    )
    response = MessageResponse(
        message="Password reset successfully. You can now log in with your new password")
    return responses.success_response(response.model_dump())


@router.post("/verify-email")
async def verify_email(
    payload: VerifyEmailRequest,
    db: Session = Depends(get_db),
):
    """Verify user email using verification token."""
    auth_service.verify_email_with_token(db, payload.email, payload.token)
    response = MessageResponse(message="Email verified successfully")
    return responses.success_response(response.model_dump())
