"""Orders Tool -- read the authenticated user's orders."""

from typing import Any, ClassVar, Dict

from sqlalchemy import select

from app.models.order import Order
from app.schemas.tool_results import OrderListResult, OrderSummaryResult, ToolError
from app.tools.base_tool import BaseTool
from app.utils.logger import get_logger

logger = get_logger(__name__)


class OrdersTool(BaseTool):
    """Fetches the current user's orders: either the latest one, or a
    paginated list of past orders. Every query is filtered by user_id so a
    user can never see another user's orders."""

    name: ClassVar[str] = "get_user_orders"
    description: ClassVar[str] = (
        "Get the authenticated user's orders. Use mode='latest' for the most "
        "recent order (e.g. for 'track my order' or 'cancel my order'), or "
        "mode='list' to get recent order history. Always scoped to the "
        "current logged-in user."
    )
    parameters: ClassVar[Dict[str, Any]] = {
        "type": "object",
        "properties": {
            "mode": {
                "type": "string",
                "enum": ["latest", "list"],
                "description": "'latest' for the single most recent order, 'list' for order history.",
            },
            "limit": {
                "type": "integer",
                "description": "Max number of orders to return when mode='list'. Default 5.",
            },
        },
        "required": ["mode"],
    }

    async def run(self, mode: str = "latest", limit: int = 5, **kwargs: Any) -> Any:
        if mode == "latest":
            return await self._get_latest_order()
        return await self._get_order_list(limit=limit)

    async def _get_latest_order(self) -> OrderSummaryResult | ToolError:
        result = await self.db.execute(
            select(Order)
            .where(Order.user_id == self.user_id)
            .order_by(Order.created_at.desc())
            .limit(1)
        )
        order = result.scalar_one_or_none()

        if order is None:
            logger.info("No orders found for user_id=%s", self.user_id)
            return ToolError(error="You don't have any orders yet.")

        return self._to_summary(order)

    async def _get_order_list(self, limit: int) -> OrderListResult:
        safe_limit = max(1, min(limit, 20))
        result = await self.db.execute(
            select(Order)
            .where(Order.user_id == self.user_id)
            .order_by(Order.created_at.desc())
            .limit(safe_limit)
        )
        orders = result.scalars().all()
        return OrderListResult(orders=[self._to_summary(o) for o in orders])

    @staticmethod
    def _to_summary(order: Order) -> OrderSummaryResult:
        return OrderSummaryResult(
            order_id=order.id,
            status=order.status,
            payment_method=order.payment_method,
            total_amount=float(order.total_amount) if order.total_amount is not None else None,
            tracking_id=None,
            placed_on=order.created_at,
        )
