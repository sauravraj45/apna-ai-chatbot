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
        "Search APNA STORE's FAQ knowledge base for general shopping, store policies, "
        "orders, delivery, payments, refunds, returns, replacements, account, "
        "shopping, offers, coupons, login, security and customer support questions. "
        "Use this only for general information and store policies, not for a user's "
        "personal order or account data."
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
                    "I couldn't find a matching help article for your question. "
                    "Please try asking in a different way or contact APNA STORE Customer Support if you need further assistance."
                )
            )
            
        
        return FAQResult(
            category=entry["category"],
            topic=entry["topic"],
            answer=entry["answer"],
            next_actions=entry.get("next_actions", []),
        )
