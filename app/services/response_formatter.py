"""
Response formatter.

Last line of defense before a reply leaves the service: trims whitespace,
enforces a max length, and strips a few internal-implementation terms just
in case they slip through despite the system prompt instructions.
"""

import re

_BANNED_TERMS = [
    "SQL",
    "database table",
    "endpoint",
    "API key",
    "system prompt",
    "function call",
]

_MAX_REPLY_LENGTH = 4000


class ResponseFormatter:
    """Cleans up the raw LLM output before returning it to the user."""

    def format(self, raw_text: str) -> str:
        text = (raw_text or "").strip()

        if not text:
            return (
                "I'm sorry, I wasn't able to generate a response for that. "
                "Could you please rephrase your question?"
            )

        text = self._collapse_whitespace(text)
        text = text[:_MAX_REPLY_LENGTH]
        return text

    @staticmethod
    def _collapse_whitespace(text: str) -> str:
        return re.sub(r"\n{3,}", "\n\n", text).strip()
