"""Main chat endpoint -- the primary integration point for the frontend."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.middleware.auth_middleware import get_current_user_id
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.ai_service import AIService

router = APIRouter(tags=["Chat"])
_ai_service = AIService()


@router.post("/chat", response_model=ChatResponse)
async def chat(
    payload: ChatRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> ChatResponse:
    """Send a message to the shopping assistant and get a reply.

    Requires a valid `Authorization: Bearer <jwt>` header. The assistant
    only ever accesses data belonging to the authenticated user.
    """
    reply, conversation_id = await _ai_service.handle_chat_turn(
        db=db,
        user_id=user_id,
        user_message=payload.message,
        conversation_id=payload.conversation_id,
    )

    return ChatResponse(
        success=True,
        reply=reply,
        conversation_id=conversation_id,
        timestamp=datetime.now(timezone.utc),
    )
