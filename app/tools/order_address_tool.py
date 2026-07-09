"""Order Address Tool -- read the delivery address for a specific order.

Same ownership-verification pattern as OrderItemsTool: order_id is
attacker-influenced input (comes via the LLM from user text), so ownership
is always re-checked against `self.user_id` before returning anything.
"""

from typing import Any, ClassVar, Dict

from sqlalchemy import select

from app.models.order import Order
from app.models.order_address import OrderAddress
from app.schemas.tool_results import DeliveryAddressResult, ToolError
from app.tools.base_tool import BaseTool
from app.utils.logger import get_logger

logger = get_logger(__name__)


class OrderAddressTool(BaseTool):
    """Fetches the delivery address recorded for a specific order."""

    name: ClassVar[str] = "get_order_delivery_address"
    description: ClassVar[str] = (
        "Get the delivery address for a specific order (e.g. answering "
        "'where will my order be delivered?'). If the user hasn't specified "
        "which order, use the most recent order_id from get_user_orders. "
        "Ownership is always verified against the current logged-in user."
    )
    parameters: ClassVar[Dict[str, Any]] = {
        "type": "object",
        "properties": {
            "order_id": {"type": "integer", "description": "The order id to fetch the delivery address for."},
        },
        "required": ["order_id"],
    }

    async def run(self, order_id: int, **kwargs: Any) -> DeliveryAddressResult | ToolError:
        order_result = await self.db.execute(
            select(Order).where(Order.id == order_id, Order.user_id == self.user_id)
        )
        order = order_result.scalar_one_or_none()

        if order is None:
            logger.warning(
                "Blocked order_address lookup: order_id=%s not owned by user_id=%s",
                order_id,
                self.user_id,
            )
            return ToolError(error="We couldn't find that order for your account.")

        addr_result = await self.db.execute(
            select(OrderAddress).where(OrderAddress.order_id == order_id)
        )
        addr = addr_result.scalar_one_or_none()

        if addr is None:
            return ToolError(error="No delivery address is on file for that order.")

        return DeliveryAddressResult(
            order_id=order_id,
            full_name=addr.name,
            address_line1=addr.address,
            address_line2=None,
            city=addr.city,
            state=addr.state,
            pincode=addr.pincode,
            country="India",
        )
