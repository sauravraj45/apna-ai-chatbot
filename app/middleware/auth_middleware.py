"""
Authentication dependency.

Every protected route depends on `get_current_user_id`, which:
1. Reads the `Authorization: Bearer <token>` header.
2. Verifies the JWT signature and expiry.
3. Extracts and returns the user_id claim.

No route/tool/service downstream should ever accept a user_id from the
request body or query params -- it must always come from this dependency,
which is the single source of truth tying a request to an authenticated
user. This is what prevents one user from ever reading another user's data.
"""

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.utils.exceptions import AuthenticationError
from app.utils.logger import get_logger, redact
from app.utils.security import decode_jwt, extract_user_id

logger = get_logger(__name__)

_bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> int:
    """FastAPI dependency: resolve the authenticated user's id from the JWT.

    Raises:
        AuthenticationError: if no/invalid token is supplied.
    """
    if credentials is None or not credentials.credentials:
        raise AuthenticationError("Missing authentication token.")

    token = credentials.credentials
    payload = decode_jwt(token)
    user_id = extract_user_id(payload)
    logger.info("Authenticated request for user_id=%s (token=%s)", user_id, redact(token))
    return user_id
