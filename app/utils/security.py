"""
Security utilities: JWT verification.

The chatbot never issues the "real" login tokens for the storefront -- those
are minted by the existing Node.js/Express backend. This module only
*verifies* tokens signed with the shared JWT_SECRET and extracts the
authenticated user's id. A local `/auth/dev-token` endpoint is provided
purely for local testing (see routers/auth.py) and should be disabled in
production.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict

import jwt

from app.config.settings import get_settings
from app.utils.exceptions import AuthenticationError
from app.utils.logger import get_logger

logger = get_logger(__name__)


def decode_jwt(token: str) -> Dict[str, Any]:
    """Verify and decode a JWT, returning its claims.

    Raises:
        AuthenticationError: if the token is missing, malformed, expired,
            or has an invalid signature.
    """
    settings = get_settings()
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except jwt.ExpiredSignatureError:
        logger.info("Rejected expired JWT")
        raise AuthenticationError("Your session has expired. Please log in again.")
    except jwt.InvalidTokenError:
        logger.info("Rejected invalid JWT")
        raise AuthenticationError("Invalid authentication token.")


def extract_user_id(payload: Dict[str, Any]) -> int:
    """Pull the user id out of decoded JWT claims.

    Raises:
        AuthenticationError: if the expected claim is missing or not an int.
    """
    settings = get_settings()
    claim = settings.JWT_USER_ID_CLAIM
    raw_value = payload.get(claim)
    if raw_value is None:
        logger.warning("JWT payload missing expected user id claim '%s'", claim)
        raise AuthenticationError("Authentication token is missing required data.")
    try:
        return int(raw_value)
    except (TypeError, ValueError):
        raise AuthenticationError("Authentication token contains an invalid user id.")


def create_dev_jwt(user_id: int, expires_minutes: int = 60) -> str:
    """Create a short-lived JWT for LOCAL TESTING ONLY.

    This mirrors the shape of tokens the Node.js backend is expected to
    issue. It must never be exposed in a production deployment -- the
    `/auth/dev-token` route that calls this is gated by `APP_ENV`.
    """
    settings = get_settings()
    now = datetime.now(timezone.utc)
    payload = {
        settings.JWT_USER_ID_CLAIM: user_id,
        "iat": now,
        "exp": now + timedelta(minutes=expires_minutes),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
