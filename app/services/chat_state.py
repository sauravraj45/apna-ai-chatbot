"""
Temporary chat authentication state.

This service stores short-lived state for each conversation.

It is NOT conversation history.
It only remembers whether the assistant is waiting for the
user's registered email and what question should be retried
after authentication.

Later this can easily be moved to Redis.
"""

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class ChatState:
    """
    Stores temporary authentication state for one conversation.
    """

    # Waiting for the user's registered email
    awaiting_email: bool = False

    # Original question that should be retried after authentication
    pending_query: Optional[str] = None

    # Authenticated user for this conversation
    authenticated_user_id: Optional[int] = None

    def authenticate(self, user_id: int) -> None:
        """
        Mark this conversation as authenticated.
        """
        self.awaiting_email = False
        self.pending_query = None
        self.authenticated_user_id = user_id

    def require_email(self, pending_query: str) -> None:
        """
        Ask the user for their registered email before continuing.
        """
        self.awaiting_email = True
        self.pending_query = pending_query

    def reset(self) -> None:
        """
        Reset the authentication state.
        """
        self.awaiting_email = False
        self.pending_query = None
        self.authenticated_user_id = None


class ChatStateManager:
    """
    Keeps authentication state for every conversation.
    """

    def __init__(self):
        self._states: Dict[str, ChatState] = {}

    def get(self, conversation_id: str) -> ChatState:
        """
        Return the state for a conversation.
        """
        if conversation_id not in self._states:
            self._states[conversation_id] = ChatState()

        return self._states[conversation_id]

    def clear(self, conversation_id: str) -> None:
        """
        Remove conversation state.
        """
        self._states.pop(conversation_id, None)


# Global singleton
chat_state_manager = ChatStateManager()