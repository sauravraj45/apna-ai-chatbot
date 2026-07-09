"""
Auth service.

Production token issuance is owned entirely by the existing Node.js/Express
backend -- this service only ever verifies tokens (see
`app.utils.security.decode_jwt`). The one exception is `issue_dev_token`,
used solely by the local-testing-only `/auth/dev-token` route so you can
exercise the chatbot without standing up the full Node.js login flow.
"""

from app.config.settings import get_settings
from app.utils.exceptions import AuthorizationError
from app.utils.security import create_dev_jwt


class AuthService:
    """Encapsulates auth-related operations not covered by the JWT dependency."""

    def issue_dev_token(self, user_id: int) -> str:
        """Issue a short-lived JWT for local testing.

        Raises:
            AuthorizationError: if called outside a non-production environment.
        """
        settings = get_settings()
        if settings.APP_ENV == "production":
            raise AuthorizationError("Dev token issuance is disabled in production.")
        return create_dev_jwt(user_id)
