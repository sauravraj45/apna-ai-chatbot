"""
Memory backend abstraction.

`MemoryBackend` is an abstract interface so the storage mechanism can be
swapped later (Redis, a `conversations` DB table, etc.) without touching
`ConversationMemory` or the AI service. `InMemoryBackend` is the default,
process-local implementation -- fine for a single instance / local dev, but
state is lost on restart and isn't shared across multiple replicas. See
README > "Future Expansion" for the Redis upgrade path.
"""

from abc import ABC, abstractmethod
from collections import OrderedDict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional


@dataclass
class StoredMessage:
    role: str  # "user" | "assistant"
    content: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ConversationRecord:
    conversation_id: str
    user_id: int | None
    messages: List[StoredMessage] = field(default_factory=list)


class MemoryBackend(ABC):
    """Abstract conversation storage backend."""

    @abstractmethod
    async def get(self, conversation_id: str, user_id: int | None) -> Optional[ConversationRecord]:
        ...

    @abstractmethod
    async def create(self, conversation_id: str, user_id: int | None) -> ConversationRecord:
        ...

    @abstractmethod
    async def append_message(self, conversation_id: str, user_id: int | None, role: str, content: str) -> None:
        ...

    @abstractmethod
    async def delete(self, conversation_id: str, user_id: int | None) -> None:
        ...

    @abstractmethod
    async def transfer_ownership(
        self,
        conversation_id: str,
        old_user_id: int | None,
        new_user_id: int,
    ) -> None:
        ...


class InMemoryBackend(MemoryBackend):
    """Simple process-local in-memory store, keyed by conversation_id.

    A `user_id` check is enforced on every read/write so one user's request
    can never read or mutate another user's conversation, even if they
    guessed/leaked a conversation_id.
    """

    def __init__(self, max_messages: int = 20):
        self._conversations: "OrderedDict[str, ConversationRecord]" = OrderedDict()
        self._max_messages = max_messages

    async def get(self, conversation_id: str, user_id: int | None) -> Optional[ConversationRecord]:
        record = self._conversations.get(conversation_id)
        if record is None or record.user_id != user_id:
            return None
        return record

    async def create(self, conversation_id: str, user_id: int | None) -> ConversationRecord:
        record = ConversationRecord(conversation_id=conversation_id, user_id=user_id)
        self._conversations[conversation_id] = record
        return record

    async def append_message(self, conversation_id: str, user_id: int | None, role: str, content: str) -> None:
        record = await self.get(conversation_id, user_id)
        if record is None:
            record = await self.create(conversation_id, user_id)
        record.messages.append(StoredMessage(role=role, content=content))
        # Keep only the most recent N messages to bound memory/token usage.
        if len(record.messages) > self._max_messages:
            record.messages = record.messages[-self._max_messages :]

    async def delete(self, conversation_id: str, user_id: int | None) -> None:
        record = self._conversations.get(conversation_id)
        if record is not None and record.user_id == user_id:
            del self._conversations[conversation_id]

    async def transfer_ownership(
        self,
        conversation_id: str,
        old_user_id: int | None,
        new_user_id: int,
    ) -> None:
        record = self._conversations.get(conversation_id)
        if record is None:
            return
        if record.user_id != old_user_id:
            return
        record.user_id = new_user_id