"""
Conversation memory manager.

Thin, higher-level wrapper around a `MemoryBackend` that the AI service
uses. Generates conversation ids, formats history for the LLM, and exposes
reset/history operations for the corresponding REST endpoints.
"""

import uuid
from typing import List

from app.config.settings import get_settings
from app.memory.memory_store import (
    ConversationRecord,
    InMemoryBackend,
    MemoryBackend,
    StoredMessage,
)
from app.utils.exceptions import ConversationNotFoundError

_backend: MemoryBackend | None = None


def get_memory_backend() -> MemoryBackend:
    """Return the process-wide memory backend (singleton)."""
    global _backend

    if _backend is None:
        settings = get_settings()
        _backend = InMemoryBackend(
            max_messages=settings.MAX_MEMORY_MESSAGES
        )

    return _backend


class ConversationMemory:
    """Per-request facade over the memory backend for a single user."""

    def __init__(self, user_id: int | None):
        self.user_id = user_id
        self.backend = get_memory_backend()

    def set_user(self, user_id: int | None) -> None:
        """
        Update the user associated with this conversation.

        Useful when an anonymous conversation becomes authenticated
        after email verification.
        """
        self.user_id = user_id

    async def get_or_create(
        self,
        conversation_id: str | None,
    ) -> ConversationRecord:
        """
        Return an existing conversation (verifying ownership)
        or create a new one.
        """

        if conversation_id:
            record = await self.backend.get(
                conversation_id,
                self.user_id,
            )

            if record is not None:
                return record

        new_id = conversation_id or str(uuid.uuid4())

        return await self.backend.create(
            new_id,
            self.user_id,
        )

    async def get_required(
        self,
        conversation_id: str,
    ) -> ConversationRecord:
        """
        Fetch an existing conversation,
        raising if it doesn't exist.
        """

        record = await self.backend.get(
            conversation_id,
            self.user_id,
        )

        if record is None:
            raise ConversationNotFoundError()

        return record

    async def add_user_message(
        self,
        conversation_id: str,
        content: str,
    ) -> None:
        await self.backend.append_message(
            conversation_id,
            self.user_id,
            "user",
            content,
        )

    async def add_assistant_message(
        self,
        conversation_id: str,
        content: str,
    ) -> None:
        await self.backend.append_message(
            conversation_id,
            self.user_id,
            "assistant",
            content,
        )

    async def reset(
        self,
        conversation_id: str,
    ) -> None:
        await self.backend.delete(
            conversation_id,
            self.user_id,
        )

    async def transfer_ownership(
        self,
        conversation_id: str,
        new_user_id: int,
    ) -> None:
        """
        Reassign an existing conversation to a newly-authenticated user.

        Used by the email step-up auth flow: a conversation that started
        anonymous (self.user_id is None, or a placeholder id) must be
        re-owned by the real user_id once they authenticate mid-conversation,
        so that subsequent lookups scoped to that user_id (e.g.
        backend.get(conversation_id, user_id)) still find the conversation
        and its full message history. This does NOT create a new
        conversation -- conversation_id and all existing messages are
        preserved; only ownership changes.

        NOTE: this requires MemoryBackend (app/memory/memory_store.py) to
        expose a corresponding `transfer_ownership` method -- that is not
        part of this file's scope and must be added there separately.
        """
        await self.backend.transfer_ownership(
            conversation_id,
            old_user_id=self.user_id,
            new_user_id=new_user_id,
        )
        self.user_id = new_user_id

    @staticmethod
    def to_llm_messages(
        messages: List[StoredMessage],
    ) -> List[dict]:
        """
        Convert stored messages into the format expected by the LLM.
        """

        return [
            {
                "role": message.role,
                "content": message.content,
            }
            for message in messages
        ]