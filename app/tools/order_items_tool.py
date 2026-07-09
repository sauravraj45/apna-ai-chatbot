"""Order Items Tool -- read the products within a specific order.

Security note: order_id is supplied by the LLM (derived from the
conversation), so we NEVER trust it blindly. We always join through
`orders.user_id == self.user_id` so a user can never fetch items for
another user's order, even by guessing/providing an arbitrary order_id.
"""

from typing import Any, ClassVar, Dict

from sqlalchemy import select

from app.models.order import Order
from app.models.order_item import OrderItem
from app.schemas.tool_results import OrderDetailResult, OrderItemResult, ToolError
from app.tools.base_tool import BaseTool
from app.utils.logger import get_logger

logger = get_logger(__name__)


class OrderItemsTool(BaseTool):
    """Fetches the product line items for a given order_id, but only if that
    order belongs to the authenticated user."""

    name: ClassVar[str] = "get_order_items"
    description: ClassVar[str] = (
        "Get the list of products (name, quantity, price) within a specific "
        "order. If the user hasn't specified which order, use the most "
        "recent order_id from get_user_orders. Ownership is always verified "
        "against the current logged-in user."
    )
    parameters: ClassVar[Dict[str, Any]] = {
        "type": "object",
        "properties": {
            "order_id": {"type": "integer", "description": "The order id to fetch items for."},
        },
        "required": ["order_id"],
    }

    async def run(self, order_id: int, **kwargs: Any) -> OrderDetailResult | ToolError:
        # First confirm the order belongs to this user.
        order_result = await self.db.execute(
            select(Order).where(Order.id == order_id, Order.user_id == self.user_id)
        )
        order = order_result.scalar_one_or_none()

        if order is None:
            logger.warning(
                "Blocked order_items lookup: order_id=%s not owned by user_id=%s",
                order_id,
                self.user_id,
            )
            return ToolError(error="We couldn't find that order for your account.")

        items_result = await self.db.execute(
            select(OrderItem).where(OrderItem.order_id == order_id)
        )
        items = items_result.scalars().all()

        return OrderDetailResult(
            order_id=order.id,
            status=order.status,
            payment_status=None,
            total_amount=float(order.total_amount) if order.total_amount is not None else None,
            tracking_id=None,
            placed_on=order.created_at,
            items=[
                OrderItemResult(
                    product_name=item.title,
                    quantity=item.quantity,
                    price=float(item.price) if item.price is not None else None,
                )
                for item in items
            ],
        )
