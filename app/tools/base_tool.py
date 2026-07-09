"""
Base tool contract.

Every tool:
1. Is instantiated with a DB session and the CURRENT AUTHENTICATED user_id
   (never a user_id supplied by the LLM or the request body).
2. Exposes an async `run(**kwargs)` method that queries the database and
   returns a small, typed Pydantic result (never a raw ORM object).
3. Declares a JSON-Schema-like `parameters` spec and `description` so it can
   be registered with the LLM's function/tool-calling API.

This indirection is what stops the LLM from ever running arbitrary SQL or
seeing another user's data -- it can only call these pre-defined, scoped
functions.
"""

from abc import ABC, abstractmethod
from typing import Any, ClassVar, Dict

from sqlalchemy.ext.asyncio import AsyncSession


class BaseTool(ABC):
    """Abstract base class every tool must implement."""

    #: Unique name the LLM uses to invoke this tool.
    name: ClassVar[str]
    #: Human-readable description shown to the LLM for tool selection.
    description: ClassVar[str]
    #: JSON-schema `parameters` object describing the tool's arguments.
    parameters: ClassVar[Dict[str, Any]] = {"type": "object", "properties": {}, "required": []}

    def __init__(self, db: AsyncSession, user_id: int):
        self.db = db
        self.user_id = user_id  # trusted, comes only from the JWT

    @abstractmethod
    async def run(self, **kwargs: Any) -> Any:
        """Execute the tool and return a structured (Pydantic) result."""
        raise NotImplementedError

    @classmethod
    def openai_spec(cls) -> Dict[str, Any]:
        """Return this tool's definition in OpenAI-style function-calling format."""
        return {
            "type": "function",
            "function": {
                "name": cls.name,
                "description": cls.description,
                "parameters": cls.parameters,
            },
        }
