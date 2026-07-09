"""
Local testing auth router.

`/auth/dev-token` lets you mint a JWT for a given user_id without running
the real Node.js login flow, so you can test /chat locally. It is
automatically disabled (403) when APP_ENV=production -- see AuthService.
"""

from fastapi import APIRouter

from app.schemas.auth import DevTokenRequest, DevTokenResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Auth (dev only)"])
_auth_service = AuthService()


@router.post("/dev-token", response_model=DevTokenResponse)
async def issue_dev_token(payload: DevTokenRequest) -> DevTokenResponse:
    """Issue a short-lived JWT for the given user_id. LOCAL/TESTING USE ONLY."""
    token = _auth_service.issue_dev_token(payload.user_id)
    return DevTokenResponse(access_token=token)
