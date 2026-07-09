"""Pydantic schemas for the local-testing-only auth endpoint."""

from pydantic import BaseModel


class DevTokenRequest(BaseModel):
    """Request body for POST /auth/dev-token (local testing only)."""

    user_id: int


class DevTokenResponse(BaseModel):
    """Response body for POST /auth/dev-token."""

    access_token: str
    token_type: str = "bearer"
