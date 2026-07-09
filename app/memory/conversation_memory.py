"""
Conversation memory manager.

Thin, higher-level wrapper around a `MemoryBackend` that the AI service
uses. Generates conversation ids, formats history for the LLM, and exposes
reset/history operations for the corresponding REST endpoints.
"""

import uuid
from typing import List

from app.config.settings import get_settings
from app.memory.memory_store import ConversationRecord, InMemoryBackend, MemoryBackend, StoredMessage
from app.utils.exceptions import ConversationNotFoundError

_backend: MemoryBackend | None = None


def get_memory_backend() -> MemoryBackend:
    """Return the process-wide memory backend (singleton).

    Swap `InMemoryBackend` for a Redis-backed implementation here later --
    nothing else in the codebase needs to change.
    """
    global _backend
    if _backend is None:
        settings = get_settings()
        _backend = InMemoryBackend(max_messages=settings.MAX_MEMORY_MESSAGES)
    return _backend


class ConversationMemory:
    """Per-request facade over the memory backend for a single user."""

    def __init__(self, user_id: int):
        self.user_id = user_id
        self.backend = get_memory_backend()

    async def get_or_create(self, conversation_id: str | None) -> ConversationRecord:
        """Return an existing conversation (verifying ownership) or start a new one."""
        if conversation_id:
            record = await self.backend.get(conversation_id, self.user_id)
            if record is not None:
                return record
        new_id = conversation_id or str(uuid.uuid4())
        return await self.backend.create(new_id, self.user_id)

    async def get_required(self, conversation_id: str) -> ConversationRecord:
        """Fetch an existing conversation, raising if it doesn't exist / isn't owned by user."""
        record = await self.backend.get(conversation_id, self.user_id)
        if record is None:
            raise ConversationNotFoundError()
        return record

    async def add_user_message(self, conversation_id: str, content: str) -> None:
        await self.backend.append_message(conversation_id, self.user_id, "user", content)

    async def add_assistant_message(self, conversation_id: str, content: str) -> None:
        await self.backend.append_message(conversation_id, self.user_id, "assistant", content)

    async def reset(self, conversation_id: str) -> None:
        await self.backend.delete(conversation_id, self.user_id)

    @staticmethod
    def to_llm_messages(messages: List[StoredMessage]) -> List[dict]:
        """Format stored history into the {role, content} shape LLM APIs expect."""
        return [{"role": m.role, "content": m.content} for m in messages]
