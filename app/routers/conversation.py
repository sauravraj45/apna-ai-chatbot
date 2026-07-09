"""Conversation management endpoints: view history and reset a conversation."""

from fastapi import APIRouter, Depends, Query

from app.memory.conversation_memory import ConversationMemory
from app.middleware.auth_middleware import get_current_user_id
from app.schemas.chat import ConversationHistoryResponse, ConversationResetResponse, MessageOut

router = APIRouter(prefix="/conversation", tags=["Conversation"])


@router.post("/reset", response_model=ConversationResetResponse)
async def reset_conversation(
    conversation_id: str = Query(..., description="The conversation id to reset"),
    user_id: int = Depends(get_current_user_id),
) -> ConversationResetResponse:
    """Clear a conversation's memory. Only works on conversations owned by the caller."""
    memory = ConversationMemory(user_id=user_id)
    await memory.reset(conversation_id)
    return ConversationResetResponse(conversation_id=conversation_id)


@router.get("/history", response_model=ConversationHistoryResponse)
async def get_conversation_history(
    conversation_id: str = Query(..., description="The conversation id to fetch"),
    user_id: int = Depends(get_current_user_id),
) -> ConversationHistoryResponse:
    """Return the stored message history for a conversation owned by the caller."""
    memory = ConversationMemory(user_id=user_id)
    record = await memory.get_required(conversation_id)
    return ConversationHistoryResponse(
        conversation_id=conversation_id,
        messages=[MessageOut(role=m.role, content=m.content, timestamp=m.timestamp) for m in record.messages],
    )
