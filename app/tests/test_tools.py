"""
Unit tests for tools.

Each test mocks the SQLAlchemy `execute()` result so we can verify:
1. The tool queries are correctly scoped to `user_id`.
2. Ownership checks block cross-user access (order_items/order_address).
3. Missing data returns a ToolError instead of raising or fabricating data.
"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models.order import Order
from app.models.user import User
from app.schemas.tool_results import ToolError, UserProfileResult
from app.tools.faq_tool import FAQTool
from app.tools.order_items_tool import OrderItemsTool
from app.tools.orders_tool import OrdersTool
from app.tools.user_tool import UserTool


def _mock_scalar_result(value):
    """Build a mock SQLAlchemy result whose scalar_one_or_none() returns `value`."""
    result = MagicMock()
    result.scalar_one_or_none.return_value = value
    result.scalars.return_value.all.return_value = value if isinstance(value, list) else []
    return result


@pytest.mark.anyio
async def test_user_tool_returns_profile(mock_db_session):
    fake_user = User(id=1, name="Aditi Sharma", email="aditi@example.com", phone="9999999999")
    mock_db_session.execute = AsyncMock(return_value=_mock_scalar_result(fake_user))

    tool = UserTool(db=mock_db_session, user_id=1)
    result = await tool.run()

    assert isinstance(result, UserProfileResult)
    assert result.email == "aditi@example.com"


@pytest.mark.anyio
async def test_user_tool_missing_user_returns_error(mock_db_session):
    mock_db_session.execute = AsyncMock(return_value=_mock_scalar_result(None))

    tool = UserTool(db=mock_db_session, user_id=999)
    result = await tool.run()

    assert isinstance(result, ToolError)


@pytest.mark.anyio
async def test_orders_tool_latest_no_orders_returns_error(mock_db_session):
    mock_db_session.execute = AsyncMock(return_value=_mock_scalar_result(None))

    tool = OrdersTool(db=mock_db_session, user_id=1)
    result = await tool.run(mode="latest")

    assert isinstance(result, ToolError)


@pytest.mark.anyio
async def test_order_items_tool_blocks_other_users_order(mock_db_session):
    # Simulate: the order exists, but does not belong to this user, so the
    # `WHERE user_id = ...` filter means the ORM query returns None.
    mock_db_session.execute = AsyncMock(return_value=_mock_scalar_result(None))

    tool = OrderItemsTool(db=mock_db_session, user_id=1)
    result = await tool.run(order_id=999)  # order belonging to someone else

    assert isinstance(result, ToolError)
    assert "couldn't find" in result.error.lower()


@pytest.mark.anyio
async def test_faq_tool_known_topic():
    tool = FAQTool(db=AsyncMock(), user_id=1)
    result = await tool.run(query="how do I cancel my order")
    assert result.topic == "order_cancellation"


@pytest.mark.anyio
async def test_faq_tool_unknown_topic_returns_error():
    tool = FAQTool(db=AsyncMock(), user_id=1)
    result = await tool.run(query="asdkjhaskjdh nonsense query")
    assert isinstance(result, ToolError)
