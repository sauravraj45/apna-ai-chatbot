"""FAQ Tool -- answer general store policy questions (returns, refunds, etc.)."""

from typing import Any, ClassVar, Dict

from app.schemas.tool_results import FAQResult, ToolError
from app.tools.base_tool import BaseTool
from app.tools.faq_knowledge import find_faq_answer
from app.utils.logger import get_logger

logger = get_logger(__name__)


class FAQTool(BaseTool):
    """Looks up store policy answers (cancellation, refunds, returns, etc.)
    from a structured knowledge base -- never invents policy details."""

    name: ClassVar[str] = "search_faq"
    description: ClassVar[str] = (
        "Search APNA STORE's policy knowledge base for general questions about "
        "orders, payments, refunds, returns, replacements, shipping, coupons, "
        "account/login, or support. Use this for policy/how-to questions that "
        "are NOT about the user's specific personal data."
    )
    parameters: ClassVar[Dict[str, Any]] = {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "The user's question, in their own words."},
        },
        "required": ["query"],
    }

    async def run(self, query: str, **kwargs: Any) -> FAQResult | ToolError:
        entry = find_faq_answer(query)
        if entry is None:
            logger.info("No FAQ match for query: %s", query[:80])
            return ToolError(
                error=(
                    "I don't have a specific policy article for that. Please contact "
                    "customer support for further help."
                )
            )
        return FAQResult(topic=entry["topic"], answer=entry["answer"])
