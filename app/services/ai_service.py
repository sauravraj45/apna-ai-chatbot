"""
AI Service.

The central orchestrator for a single chat turn:
1. Load conversation history from memory.
2. Build the message list via PromptManager.
3. Call the LLM with the available tool specs.
4. If the LLM requests tool calls, dispatch them (scoped to the
   authenticated user_id), feed results back, and loop until the LLM
   produces a final text answer (bounded by MAX_TOOL_ITERATIONS to avoid
   infinite loops).
5. Format the final reply and persist both turns to memory.

This is the ONLY place that talks to the LLM client -- routers never call
it directly, keeping API logic and AI logic cleanly separated per the
project's architecture requirements.
"""

import json
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from app.memory.conversation_memory import ConversationMemory
from app.prompts.prompt_manager import PromptManager
from app.services.llm_client import LLMClient
from app.services.response_formatter import ResponseFormatter
from app.tools.tool_registry import dispatch_tool_call, get_tool_specs
from app.utils.logger import get_logger

logger = get_logger(__name__)

MAX_TOOL_ITERATIONS = 5


class AIService:
    """Coordinates prompt building, tool calling, memory, and formatting."""

    def __init__(self) -> None:
        self.prompt_manager = PromptManager()
        self.llm_client = LLMClient()
        self.formatter = ResponseFormatter()

    async def handle_chat_turn(
        self,
        db: AsyncSession,
        user_id: int,
        user_message: str,
        conversation_id: str | None,
    ) -> tuple[str, str]:
        """Process one user message end-to-end.

        Returns:
            (reply_text, conversation_id)
        """
        memory = ConversationMemory(user_id=user_id)
        record = await memory.get_or_create(conversation_id)
        resolved_conversation_id = record.conversation_id

        history = memory.to_llm_messages(record.messages)
        messages = self.prompt_manager.build_messages(history, user_message)

        reply_text = await self._run_tool_loop(db=db, user_id=user_id, messages=messages)
        formatted_reply = self.formatter.format(reply_text)

        await memory.add_user_message(resolved_conversation_id, user_message)
        await memory.add_assistant_message(resolved_conversation_id, formatted_reply)

        return formatted_reply, resolved_conversation_id

    async def _run_tool_loop(
        self,
        db: AsyncSession,
        user_id: int,
        messages: List[dict],
    ) -> str:
        """Repeatedly call the LLM, executing any requested tool calls, until
        it returns a plain text answer or the iteration cap is hit."""
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
                try:
                    arguments = json.loads(tool_call.function.arguments or "{}")
                except json.JSONDecodeError:
                    logger.warning("Malformed tool arguments from LLM for tool=%s", tool_name)
                    arguments = {}

                try:
                    result = await dispatch_tool_call(tool_name, arguments, db, user_id)
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
