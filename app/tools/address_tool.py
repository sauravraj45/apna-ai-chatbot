"""Address Tool -- read the authenticated user's saved addresses."""

from typing import Any, ClassVar, Dict

from sqlalchemy import select

from app.models.address import Address
from app.schemas.tool_results import AddressListResult, AddressResult
from app.tools.base_tool import BaseTool
from app.utils.logger import get_logger

logger = get_logger(__name__)


class AddressTool(BaseTool):
    """Fetches all saved delivery addresses belonging to the current user."""

    name: ClassVar[str] = "get_user_addresses"
    description: ClassVar[str] = (
        "Get the list of saved delivery addresses for the authenticated user. "
        "Takes no arguments -- always scoped to the current logged-in user."
    )
    parameters: ClassVar[Dict[str, Any]] = {"type": "object", "properties": {}, "required": []}

    async def run(self, **kwargs: Any) -> AddressListResult:
        result = await self.db.execute(
            select(Address).where(Address.user_id == self.user_id)
        )
        rows = result.scalars().all()

        addresses = [
            AddressResult(
                id=row.id,
                full_name=row.name,
                phone=row.phone,
                address_line1=row.address,
                address_line2=None,
                city=row.city,
                state=row.state,
                pincode=row.pincode,
                country="India",
                is_default=False,
            )
            for row in rows
        ]

        if not addresses:
            logger.info("No addresses found for user_id=%s", self.user_id)

        return AddressListResult(addresses=addresses)
