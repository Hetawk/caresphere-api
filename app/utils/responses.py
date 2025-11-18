"""Standard response helpers to keep API payloads consistent."""

from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import status
from fastapi.responses import JSONResponse


def success_response(
    data: Any,
    *,
    status_code: int = status.HTTP_200_OK,
    metadata: Optional[Dict[str, Any]] = None,
) -> JSONResponse:
    """Return a JSON response using the shared envelope format."""
    body = {
        "success": True,
        "data": data,
        "error": None,
        "metadata": metadata or {},
    }
    return JSONResponse(content=body, status_code=status_code)


def error_response(
    *,
    code: str,
    message: str,
    status_code: int,
    details: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> JSONResponse:
    """Return a JSON error response that matches the mobile client's expectations."""
    body = {
        "success": False,
        "data": None,
        "error": {
            "code": code,
            "message": message,
            "details": details or {},
        },
        "metadata": metadata or {},
    }
    return JSONResponse(content=body, status_code=status_code)
