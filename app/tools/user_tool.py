"""User Tool -- read the authenticated user's own profile."""

from typing import Any, ClassVar, Dict

from sqlalchemy import select

from app.models.user import User
from app.schemas.tool_results import ToolError, UserProfileResult
from app.tools.base_tool import BaseTool
from app.utils.logger import get_logger

logger = get_logger(__name__)


class UserTool(BaseTool):
    """Fetches profile information (name, email, phone) for the current user."""

    name: ClassVar[str] = "get_user_profile"
    description: ClassVar[str] = (
        "Get the authenticated user's own profile information: name, email, "
        "phone number, and member-since date. Takes no arguments -- it always "
        "returns the current logged-in user's data only."
    )
    parameters: ClassVar[Dict[str, Any]] = {"type": "object", "properties": {}, "required": []}

    async def run(self, **kwargs: Any) -> UserProfileResult | ToolError:
        result = await self.db.execute(select(User).where(User.id == self.user_id))
        user = result.scalar_one_or_none()

        if user is None:
            logger.warning("User profile lookup failed for user_id=%s", self.user_id)
            return ToolError(error="We couldn't find your profile information.")

        return UserProfileResult(
            name=user.fullName,
            email=user.email,
            phone=None,
            member_since=None,
        )
        
