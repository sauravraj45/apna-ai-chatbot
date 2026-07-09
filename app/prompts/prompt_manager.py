"""
Prompt manager.

Assembles the final list of messages sent to the LLM: system prompt +
conversation history + the new user message. Kept separate from
`ai_service.py` so prompt construction/versioning can evolve (e.g. A/B
testing prompts, per-locale prompts) without touching orchestration logic.
"""

from typing import List

from app.prompts.system_prompt import get_system_prompt


class PromptManager:
    """Builds the message list passed to the LLM for a single chat turn."""

    def build_messages(self, history: List[dict], new_user_message: str) -> List[dict]:
        """Combine the system prompt, prior turns, and the new message.

        Args:
            history: previously stored {role, content} messages for this conversation.
            new_user_message: the latest message from the user.
        """
        messages: List[dict] = [{"role": "system", "content": get_system_prompt()}]
        messages.extend(history)
        messages.append({"role": "user", "content": new_user_message})
        return messages
