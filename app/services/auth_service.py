"""
Auth service.

Production token issuance is owned entirely by the existing Node.js/Express
backend.

This service:
- Issues dev tokens (local development)
- Authenticates a user by registered email for AI chat
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import get_settings
from app.models.user import User
from app.utils.exceptions import AuthorizationError
from app.utils.security import create_chat_jwt, create_dev_jwt


class AuthService:
    """Authentication related operations."""

    def issue_dev_token(self, user_id: int) -> str:
        """
        Issue a short-lived JWT for local testing.
        """

        settings = get_settings()

        if settings.APP_ENV == "production":
            raise AuthorizationError(
                "Dev token issuance is disabled in production."
            )

        return create_dev_jwt(user_id)

    async def authenticate_by_email(
        self,
        db: AsyncSession,
        email: str,
    ) -> dict:
        """
        Authenticate a user using registered email.

        Returns:
        {
            "success": bool,
            "user": User | None,
            "token": str | None
        }
        """

        result = await db.execute(
            select(User).where(User.email == email)
        )

        user = result.scalar_one_or_none()

        if user is None:
            return {
                "success": False,
                "user": None,
                "token": None,
            }

        token = create_chat_jwt(user.id)

        return {
            "success": True,
            "user": user,
            "token": token,
        }