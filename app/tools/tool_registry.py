"""
Tool registry.

Single place that knows about every available tool. The AI service uses
this to (a) build the tool specs sent to the LLM, and (b) dispatch a
tool-call by name to the right class, always constructed with the current
DB session + authenticated user_id.
"""

from typing import Any, Dict, List, Type

from sqlalchemy.ext.asyncio import AsyncSession

from app.tools.address_tool import AddressTool
from app.tools.base_tool import BaseTool
from app.tools.faq_tool import FAQTool
from app.tools.order_address_tool import OrderAddressTool
from app.tools.order_items_tool import OrderItemsTool
from app.tools.orders_tool import OrdersTool
from app.tools.user_tool import UserTool
from app.utils.exceptions import ValidationAppError
from app.utils.logger import get_logger

logger = get_logger(__name__)

TOOL_CLASSES: List[Type[BaseTool]] = [
    UserTool,
    AddressTool,
    OrdersTool,
    OrderItemsTool,
    OrderAddressTool,
    FAQTool,
]

_TOOLS_BY_NAME: Dict[str, Type[BaseTool]] = {
    cls.name: cls for cls in TOOL_CLASSES
}

# ---------------------------------------------------------------------
# Tools that require the user to be authenticated.
# Public tools (FAQ, Product Search, Policy etc.) should NOT be added here.
# ---------------------------------------------------------------------
AUTH_REQUIRED_TOOLS = {
    UserTool.name,
    AddressTool.name,
    OrdersTool.name,
    OrderItemsTool.name,
    OrderAddressTool.name,
}


def requires_auth(tool_name: str) -> bool:
    """
    Returns True if the requested tool requires authentication.
    """
    return tool_name in AUTH_REQUIRED_TOOLS


def get_tool_specs() -> List[Dict[str, Any]]:
    """Return all tool specs in OpenAI function-calling format."""
    return [cls.openai_spec() for cls in TOOL_CLASSES]


async def dispatch_tool_call(
    tool_name: str,
    arguments: Dict[str, Any],
    db: AsyncSession,
    user_id: int,
) -> Any:
    """
    Instantiate and run the requested tool.
    """

    tool_cls = _TOOLS_BY_NAME.get(tool_name)

    if tool_cls is None:
        logger.warning("LLM requested unknown tool: %s", tool_name)
        raise ValidationAppError(f"Unknown tool requested: {tool_name}")

    arguments = arguments or {}

    tool = tool_cls(db=db, user_id=user_id)

    logger.info(
        "Dispatching tool=%s user_id=%s args=%s",
        tool_name,
        user_id,
        list(arguments.keys()),
    )

    result = await tool.run(**arguments)

    if hasattr(result, "model_dump"):
        return result.model_dump(mode="json")

    return result