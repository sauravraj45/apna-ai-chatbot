"""
AI Service.

The central orchestrator for a single chat turn:
1. Load conversation history from memory.
2. Resolve the caller's identity for this turn (JWT user, an already
   step-up-authenticated anonymous user, or a fully anonymous user), and
   handle any pending "waiting for email" step-up flow.
3. Build the message list via PromptManager.
4. Call the LLM with the available tool specs.
5. If the LLM requests tool calls, dispatch them (scoped to the
   *effective* user_id for this conversation), feed results back, and loop
   until the LLM produces a final text answer (bounded by
   MAX_TOOL_ITERATIONS to avoid infinite loops). Protected tools are never
   dispatched without a resolved identity -- the loop instead pauses the
   conversation and asks the user for their registered email.
6. Format the final reply and persist both turns to memory.

This is the ONLY place that talks to the LLM client -- routers never call
it directly, keeping API logic and AI logic cleanly separated per the
project's architecture requirements.

NOTE ON ChatStateManager:
ChatStateManager is a process-wide singleton imported from
app.services.chat_state, holding state objects in memory. Its API is
synchronous:
    state = chat_state_manager.get(conversation_id)
    chat_state_manager.clear(conversation_id)
There is no get_or_create()/save() -- since state objects are stored by
reference in memory, mutating the object returned by .get() is enough to
persist changes; no explicit save call is needed. The state object
exposes:
    state.awaiting_email: bool
    state.pending_query: str | None
    state.authenticated_user_id: int | None
    state.require_email(pending_query: str) -> None
    state.authenticate(user_id: int) -> None
"""

import json
import re
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from app.memory.conversation_memory import ConversationMemory
from app.prompts.prompt_manager import PromptManager
from app.services.auth_service import AuthService
from app.services.chat_state import chat_state_manager
from app.services.llm_client import LLMClient
from app.services.response_formatter import ResponseFormatter
from app.tools.tool_registry import dispatch_tool_call, get_tool_specs, requires_auth
from app.utils.logger import get_logger

logger = get_logger(__name__)

MAX_TOOL_ITERATIONS = 5

EMAIL_PROMPT = "Please enter your registered email address."
EMAIL_NOT_RECOGNIZED_PROMPT = (
    "This email address is not registered. Please enter your registered email address."
)
EMAIL_INVALID_FORMAT_PROMPT = "Please enter a valid registered email address."

# Simple format check, not a full RFC 5322 validator -- just enough to
# avoid sending obviously-non-email strings ("hello", "12345") to the
# database on every message while awaiting_email is True.
_EMAIL_FORMAT_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class AIService:
    """Coordinates prompt building, tool calling, memory, auth, and formatting."""

    def __init__(self) -> None:
        self.prompt_manager = PromptManager()
        self.llm_client = LLMClient()
        self.formatter = ResponseFormatter()
        self.auth_service = AuthService()

    async def handle_chat_turn(
        self,
        db: AsyncSession,
        user_id: int | None,
        user_message: str,
        conversation_id: str | None,
    ) -> tuple[str, str]:
        """Process one user message end-to-end.

        `user_id` may be None for anonymous (not-logged-in) callers. In that
        case, identity for the conversation is tracked separately via
        ChatStateManager and may be established mid-conversation through the
        email step-up flow (see CASE 3/4/5 in _resolve_identity_for_turn).

        Returns:
            (reply_text, conversation_id)
        """
        # STEP 1: if this is an existing conversation, consult ChatState
        # BEFORE creating ConversationMemory. A prior turn may have
        # authenticated this conversation via the email step-up flow and
        # transferred its backend ownership to a real user_id, even though
        # the JWT user_id on THIS request is still None (anonymous callers
        # don't get a JWT just because they authenticated by email mid-chat).
        # Without consulting ChatState first, ConversationMemory would be
        # created with the stale (None) user_id, fail to find the
        # now-user-15-owned conversation, and silently spawn a new anonymous
        # one -- losing history and re-triggering the email prompt.
        chat_state = chat_state_manager.get(conversation_id) if conversation_id else None

        # STEP 2: effective_memory_user is the id that actually owns the
        # conversation record in the backend right now -- the
        # step-up-authenticated user_id if this conversation was already
        # claimed, otherwise the JWT user_id.
        effective_memory_user = (
            chat_state.authenticated_user_id
            if chat_state is not None and getattr(chat_state, "authenticated_user_id", None) is not None
            else user_id
        )

        # STEP 3 & 4: create ConversationMemory scoped to the correct
        # owner, then load (or create) the conversation record under that
        # ownership.
        memory = ConversationMemory(user_id=effective_memory_user)
        record = await memory.get_or_create(conversation_id)
        resolved_conversation_id = record.conversation_id

        # Brand-new conversation (conversation_id was None above, so
        # ChatState couldn't be looked up yet) -- fetch/create it now that
        # we have a definite conversation_id.
        if chat_state is None:
            chat_state = chat_state_manager.get(resolved_conversation_id)

        # Resolve identity for this turn and figure out what the LLM should
        # actually be asked about (normally user_message, but if this turn
        # is the reply to a "please enter your email" prompt, either an
        # error message is returned directly, or -- on success -- the
        # original pending question is replayed instead of the email).
        (
            effective_user_id,
            effective_message,
            early_reply,
            is_replay,
        ) = await self._resolve_identity_for_turn(
            db=db,
            user_id=effective_memory_user,
            memory=memory,
            chat_state=chat_state,
            conversation_id=resolved_conversation_id,
            user_message=user_message,
        )

        if early_reply is not None:
            formatted_reply = self.formatter.format(early_reply)
            await memory.add_user_message(resolved_conversation_id, user_message)
            await memory.add_assistant_message(resolved_conversation_id, formatted_reply)
            return formatted_reply, resolved_conversation_id

        if is_replay:
            # Ownership of the conversation was just transferred to
            # effective_user_id inside _resolve_identity_for_turn(). The
            # `record` loaded above still reflects the pre-authentication
            # (anonymous) ownership snapshot -- reload a fresh record under
            # the now-correct owner rather than continuing to use the
            # stale one, so history and future lookups stay consistent
            # with the conversation's real backend ownership.
            memory = ConversationMemory(user_id=effective_user_id)
            record = await memory.get_required(resolved_conversation_id)

        history = memory.to_llm_messages(record.messages)

        if is_replay and history and history[-1]["role"] == "assistant" and history[-1]["content"] == self.formatter.format(EMAIL_PROMPT):
            # The last assistant turn was us asking for the registered
            # email -- that's an artifact of the step-up-auth flow, not
            # part of the actual conversation. Leaving it in would make
            # the LLM see its own "please enter your email" prompt right
            # before the replayed question and reply with something like
            # "Thank you for authenticating" instead of answering the
            # original request. Drop just that one trailing message; every
            # other message in history is left untouched.
            history = history[:-1]

        messages = self.prompt_manager.build_messages(history, effective_message)

        reply_text = await self._run_tool_loop(
            db=db,
            effective_user_id=effective_user_id,
            messages=messages,
            chat_state=chat_state,
            conversation_id=resolved_conversation_id,
            fallback_pending_query=effective_message,
        )
        formatted_reply = self.formatter.format(reply_text)

        # Save the turn using the message that was actually answered.
        # On a replay turn (step-up auth just succeeded), the original
        # question was already saved as a user message in the earlier turn
        # that triggered the email prompt -- what arrived THIS turn was the
        # email address itself, which is never stored as if it were the
        # user's question. So only the new assistant answer is appended,
        # continuing that earlier question rather than duplicating it.
        if not is_replay:
            await memory.add_user_message(resolved_conversation_id, effective_message)
        await memory.add_assistant_message(resolved_conversation_id, formatted_reply)

        return formatted_reply, resolved_conversation_id

    async def reset_conversation(self, conversation_id: str) -> None:
        """Clear step-up-auth state for a conversation.

        REQUIRED INTEGRATION: every conversation delete/reset endpoint (and
        logout endpoint, if it resets a conversation) MUST call:

            await ai_service.reset_conversation(conversation_id)

        immediately after deleting/resetting the conversation's memory.
        Without this call, chat_state_manager keeps authenticated_user_id
        and pending_query for that conversation_id around indefinitely,
        even though the conversation itself was deleted or reset.
        """
        chat_state_manager.clear(conversation_id)

    async def _resolve_identity_for_turn(
        self,
        db: AsyncSession,
        user_id: int | None,
        memory: ConversationMemory,
        chat_state,
        conversation_id: str,
        user_message: str,
    ) -> tuple[int | None, str, str | None, bool]:
        """Resolve the effective_user_id and the message to process.

        Returns (effective_user_id, effective_message, early_reply, is_replay).
        `early_reply`, when not None, means the caller should return it
        immediately without invoking the LLM (used for the email-collection
        and email-rejection responses). `is_replay` is True only on the
        turn where step-up auth just succeeded and effective_message is the
        original pending_query being replayed rather than a fresh message.
        """
        # CASE 1 & 2: already-authenticated JWT user, or anonymous user not
        # currently in the middle of a step-up flow -- nothing special to do.
        if not getattr(chat_state, "awaiting_email", False):
            effective_user_id = (
                chat_state.authenticated_user_id
                if getattr(chat_state, "authenticated_user_id", None) is not None
                else user_id
            )
            return effective_user_id, user_message, None, False

        # CASE 4/5: we previously asked for an email; this message should be
        # treated as that email address.
        email = user_message.strip()

        # Validate format BEFORE touching the database -- rejects "hello",
        # "12345", etc. without an authenticate_by_email() call.
        if not _EMAIL_FORMAT_RE.match(email):
            chat_state.require_email(pending_query=chat_state.pending_query)
            logger.info(
                "Authentication failed for conversation_id=%s (invalid email format)",
                conversation_id,
            )
            return user_id, user_message, EMAIL_INVALID_FORMAT_PROMPT, False

        logger.info("Authentication requested for conversation_id=%s", conversation_id)
        auth = await self.auth_service.authenticate_by_email(db, email)

        if not auth["success"]:
            # CASE 4 (failure): keep awaiting_email=True, ask again.
            chat_state.require_email(pending_query=chat_state.pending_query)
            logger.info("Authentication failed for conversation_id=%s", conversation_id)
            return user_id, user_message, EMAIL_NOT_RECOGNIZED_PROMPT, False

        user = auth["user"]
        logger.info(
            "Authentication successful for conversation_id=%s user_id=%s",
            conversation_id,
            user.id,
        )

        # CASE 5 (success): capture pending_query BEFORE calling
        # authenticate(), since authenticate() clears it. Then authenticate
        # the chat state, and transfer ownership of the conversation record
        # itself (not just the local ConversationMemory object's user_id)
        # to the now-authenticated user -- see conversation_memory.py /
        # memory_store.py for the corresponding backend change.
        pending_query = chat_state.pending_query
        chat_state.authenticate(user.id)
        await memory.transfer_ownership(conversation_id, user.id)
        logger.info(
            "Conversation ownership transferred for conversation_id=%s user_id=%s",
            conversation_id,
            user.id,
        )

        effective_user_id = user.id
        return effective_user_id, pending_query, None, True

    async def _run_tool_loop(
        self,
        db: AsyncSession,
        effective_user_id: int | None,
        messages: List[dict],
        chat_state,
        conversation_id: str,
        fallback_pending_query: str,
    ) -> str:
        """Repeatedly call the LLM, executing any requested tool calls, until
        it returns a plain text answer or the iteration cap is hit.

        Before dispatching any tool call, checks requires_auth(tool_name).
        If the tool needs auth and no effective_user_id is available yet,
        the conversation is paused (state.require_email is recorded) and
        the email prompt is returned immediately -- no further tool
        execution or LLM calls happen for this turn.
        """
        tool_specs = get_tool_specs()
        working_messages = list(messages)

        for iteration in range(MAX_TOOL_ITERATIONS):
            message = await self.llm_client.chat_completion(working_messages, tools=tool_specs)

            tool_calls = getattr(message, "tool_calls", None)
            if not tool_calls:
                return message.content or ""

            # The assistant's tool-call request must be included in history
            # before the corresponding tool results, per the chat-completions
            # tool-calling protocol.
            working_messages.append(
                {
                    "role": "assistant",
                    "content": message.content or "",
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                        }
                        for tc in tool_calls
                    ],
                }
            )

            for tool_call in tool_calls:
                tool_name = tool_call.function.name

                # CASE 3: protected tool requested with no resolved identity
                # -- pause the conversation and ask for the registered email
                # instead of dispatching the tool.
                if requires_auth(tool_name) and effective_user_id is None:
                    chat_state.require_email(pending_query=fallback_pending_query)
                    logger.info(
                        "Authentication requested for conversation_id=%s (protected tool call)",
                        conversation_id,
                    )
                    return EMAIL_PROMPT

                try:
                    arguments = json.loads(tool_call.function.arguments or "{}")
                except json.JSONDecodeError:
                    logger.warning("Malformed tool arguments from LLM for tool=%s", tool_name)
                    arguments = {}

                try:
                    result = await dispatch_tool_call(tool_name, arguments, db, effective_user_id)
                except Exception as exc:
                    logger.exception(
                        "Tool execution failed for %s",
                        tool_name,
                    )
                    result = {
                        "error": str(exc)
                    }

                working_messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(result, default=str),
                    }
                )

        logger.warning("Tool loop hit MAX_TOOL_ITERATIONS without a final answer")
        return (
            "I'm having trouble putting together a complete answer right now. "
            "Could you try rephrasing your question, or ask about one thing at a time?"
        )