"""Global exception handlers for the FastAPI app."""

from __future__ import annotations

import logging
from typing import Any, Dict

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

from app.utils import responses
from app.utils.exceptions import AppException, ValidationError as DomainValidationError

logger = logging.getLogger(__name__)


def init_exception_handlers(app: FastAPI) -> None:
    """Register shared exception handlers on the FastAPI application."""

    @app.exception_handler(AppException)
    async def handle_app_exception(_: Request, exc: AppException):
        return responses.error_response(
            code=exc.code,
            message=exc.message,
            status_code=exc.status_code,
            details=exc.details,
        )

    @app.exception_handler(DomainValidationError)
    async def handle_domain_validation(_: Request, exc: DomainValidationError):
        return responses.error_response(
            code=exc.code,
            message=exc.message,
            status_code=exc.status_code,
            details=exc.details,
        )

    @app.exception_handler(RequestValidationError)
    async def handle_request_validation(_: Request, exc: RequestValidationError):
        details = _format_validation_errors(exc.errors())
        return responses.error_response(
            code="VALIDATION_ERROR",
            message="Invalid request payload",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details,
        )

    @app.exception_handler(Exception)
    async def handle_unexpected(_: Request, exc: Exception):
        logger.exception("Unhandled exception", exc_info=exc)
        return responses.error_response(
            code="INTERNAL_ERROR",
            message="Unexpected server error",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


def _format_validation_errors(errors: Any) -> Dict[str, Any]:
    formatted: Dict[str, Any] = {}
    for err in errors:
        loc = err.get("loc", [])
        field = ".".join(str(part) for part in loc if part not in {"body", "query"})
        formatted[field or "body"] = err.get("msg", "Invalid value")
    return formatted
