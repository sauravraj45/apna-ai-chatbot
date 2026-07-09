"""Shared response schemas used across the API."""

from typing import Any, Optional

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """Consistent error envelope returned by the global exception handler."""

    success: bool = False
    error_code: str
    message: str
    details: Optional[Any] = None


class HealthResponse(BaseModel):
    """Response for GET /health."""

    status: str
    database: str
    version: str
