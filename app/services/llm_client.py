"""
LLM client abstraction.

Wraps the OpenAI Python SDK (also used, via its compatible API surface, for
Gemini if you point OPENAI base_url at Gemini's OpenAI-compatible endpoint,
or extend this class with a native Gemini SDK branch). Keeping this behind
one interface means `ai_service.py` never depends on a specific provider's
SDK shapes directly.
"""

import asyncio
from typing import Any, Dict, List

from openai import APITimeoutError, AsyncOpenAI, OpenAIError

from app.config.settings import get_settings
from app.utils.exceptions import LLMServiceError, LLMTimeoutError
from app.utils.logger import get_logger

logger = get_logger(__name__)


class LLMClient:
    """Provider-agnostic chat-completion client with tool-calling support."""
            
    def __init__(self) -> None:
        settings = get_settings()
        self._settings = settings

        # -----------------------------
        # Debug Logs (Temporary)
        # -----------------------------
        logger.info("=" * 60)
        logger.info("LLM Provider      : %s", settings.LLM_PROVIDER)
        logger.info("Model Name        : %s", settings.MODEL_NAME)

        if settings.GEMINI_API_KEY:
            logger.info(
                "Gemini Key Prefix : %s********",
                settings.GEMINI_API_KEY[:10],
            )
        else:
            logger.error("Gemini API Key is EMPTY!")

        logger.info("=" * 60)

        # -----------------------------
        # Initialize Client
        # -----------------------------
        if settings.LLM_PROVIDER.lower() == "gemini":
            logger.info("Initializing Gemini Client...")

            self._client = AsyncOpenAI(
                api_key=settings.GEMINI_API_KEY,
                base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
                timeout=settings.LLM_REQUEST_TIMEOUT,
            )

        else:
            logger.info("Initializing OpenAI Client...")

            self._client = AsyncOpenAI(
                api_key=settings.OPENAI_API_KEY,
                timeout=settings.LLM_REQUEST_TIMEOUT,
            )
    
    async def chat_completion(
        self,
        messages: List[Dict[str, Any]],
        tools: List[Dict[str, Any]] | None = None,
    ) -> Any:
        """Call the chat completion API once, optionally with tool definitions.

        Returns the raw `choices[0].message` object from the SDK response.

        Raises:
            LLMTimeoutError: if the request times out.
            LLMServiceError: for any other provider-side failure.
        """
        try:
            response = await self._client.chat.completions.create(
                model=self._settings.MODEL_NAME,
                messages=messages,
                tools=tools if tools else None,
                tool_choice="auto" if tools else None,
                max_tokens=self._settings.LLM_MAX_TOKENS,
                temperature=self._settings.LLM_TEMPERATURE,
            )
            return response.choices[0].message
        except APITimeoutError as exc:
            logger.error("LLM request timed out")
            raise LLMTimeoutError() from exc
        except asyncio.TimeoutError as exc:
            logger.error("LLM request timed out (asyncio)")
            raise LLMTimeoutError() from exc
        except OpenAIError as exc:
            logger.error("LLM provider error: %s", type(exc).__name__)
            raise LLMServiceError() from exc

