"""Common schema fragments shared between resources."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ResponseMetadata(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    requestId: Optional[str] = None
    version: str = "1.0.0"
    pagination: Optional[dict] = None


class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=20, ge=1, le=100)
    search: Optional[str] = None
    status: Optional[str] = None


class MessageResponse(BaseModel):
    message: str
