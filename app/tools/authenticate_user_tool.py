"""
Authenticate User Tool.

Used when the user is not logged in but wants to access
their private information.

The tool authenticates the user using the registered email.
"""

from typing import Any, ClassVar, Dict

from sqlalchemy import select

from app.models.user import User
from app.schemas.tool_results import AuthenticationResult
from app.schemas.tool_results import ToolError
from app.tools.base_tool import BaseTool


class AuthenticateUserTool(BaseTool):

    name: ClassVar[str] = "authenticate_user"

    description: ClassVar[str] = (
        "Authenticate a user using their registered email address. "
        "Use this only when the user wants personal information "
        "such as profile, orders or addresses and they are not logged in."
    )

    parameters: ClassVar[Dict[str, Any]] = {
        "type": "object",
        "properties": {
            "email": {
                "type": "string",
                "description": "Registered email address."
            }
        },
        "required": ["email"],
    }

    async def run(self, email: str) -> AuthenticationResult | ToolError:

        result = await self.db.execute(
            select(User).where(User.email == email)
        )

        user = result.scalar_one_or_none()

        if user is None:
            return ToolError(
                error="INVALID_EMAIL"
            )

        return AuthenticationResult(
            authenticated=True,
            user_id=user.id,
        )