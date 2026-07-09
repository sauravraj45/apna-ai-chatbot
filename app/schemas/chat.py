"""Pydantic schemas for the /chat and /conversation endpoints."""

from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Incoming chat message from the authenticated user."""

    message: str = Field(..., min_length=1, max_length=2000, description="The user's message")
    conversation_id: Optional[str] = Field(
        default=None,
        description="Existing conversation id to continue. Omit to start a new conversation.",
    )


class ChatResponse(BaseModel):
    """Standard response envelope returned by /chat."""

    success: bool = True
    reply: str
    conversation_id: str
    timestamp: datetime


class MessageOut(BaseModel):
    """A single message as returned by the conversation history endpoint."""

    role: Literal["user", "assistant"]
    content: str
    timestamp: datetime


class ConversationHistoryResponse(BaseModel):
    """Response for GET /conversation/history."""

    success: bool = True
    conversation_id: str
    messages: List[MessageOut]


class ConversationResetResponse(BaseModel):
    """Response for POST /conversation/reset."""

    success: bool = True
    message: str = "Conversation has been reset."
    conversation_id: str
