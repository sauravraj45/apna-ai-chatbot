"""
Security utilities: JWT verification.

The chatbot never issues the "real" login tokens for the storefront -- those
are minted by the existing Node.js/Express backend. This module only
*verifies* tokens signed with the shared JWT_SECRET and extracts the
authenticated user's id.

It also provides helper functions for creating AI chat JWTs and
development JWTs for local testing.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict

import jwt

from app.config.settings import get_settings
from app.utils.exceptions import AuthenticationError
from app.utils.logger import get_logger

logger = get_logger(__name__)


def decode_jwt(token: str) -> Dict[str, Any]:
    """
    Verify and decode a JWT, returning its claims.
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
        raise AuthenticationError(
            "Your session has expired. Please log in again."
        )

    except jwt.InvalidTokenError:
        logger.info("Rejected invalid JWT")
        raise AuthenticationError(
            "Invalid authentication token."
        )


def extract_user_id(payload: Dict[str, Any]) -> int:
    """
    Extract the authenticated user's ID from JWT claims.
    """
    settings = get_settings()

    claim = settings.JWT_USER_ID_CLAIM

    raw_value = payload.get(claim)

    if raw_value is None:
        logger.warning(
            "JWT payload missing expected user id claim '%s'",
            claim,
        )
        raise AuthenticationError(
            "Authentication token is missing required data."
        )

    try:
        return int(raw_value)

    except (TypeError, ValueError):
        raise AuthenticationError(
            "Authentication token contains an invalid user id."
        )


def create_chat_jwt(
    user_id: int,
    expires_minutes: int = 60,
) -> str:
    """
    Create a JWT for AI chat authentication.
    """

    settings = get_settings()

    now = datetime.now(timezone.utc)

    payload = {
        settings.JWT_USER_ID_CLAIM: user_id,
        "iat": now,
        "exp": now + timedelta(minutes=expires_minutes),
    }

    return jwt.encode(
        payload,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )


def create_dev_jwt(
    user_id: int,
    expires_minutes: int = 60,
) -> str:
    """
    Backward-compatible development JWT.

    This simply reuses create_chat_jwt() so existing code that
    imports create_dev_jwt() continues to work.
    """
    return create_chat_jwt(
        user_id=user_id,
        expires_minutes=expires_minutes,
    )