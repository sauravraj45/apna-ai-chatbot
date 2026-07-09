# """
# LLM client abstraction.

# Wraps the OpenAI Python SDK (also used, via its compatible API surface, for
# Gemini if you point OPENAI base_url at Gemini's OpenAI-compatible endpoint,
# or extend this class with a native Gemini SDK branch). Keeping this behind
# one interface means `ai_service.py` never depends on a specific provider's
# SDK shapes directly.
# """

# import asyncio
# from typing import Any, Dict, List

# from openai import APITimeoutError, AsyncOpenAI, OpenAIError

# from app.config.settings import get_settings
# from app.utils.exceptions import LLMServiceError, LLMTimeoutError
# from app.utils.logger import get_logger

# logger = get_logger(__name__)


# class LLMClient:
#     """Provider-agnostic chat-completion client with tool-calling support."""

#     def __init__(self) -> None:
#         settings = get_settings()
#         self._settings = settings

#         if settings.LLM_PROVIDER == "gemini":
#             # Gemini's OpenAI-compatible endpoint. See:
#             # https://ai.google.dev/gemini-api/docs/openai
#             self._client = AsyncOpenAI(
#                 api_key=settings.GEMINI_API_KEY,
#                 base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
#                 timeout=settings.LLM_REQUEST_TIMEOUT,
#             )
#         else:
#             self._client = AsyncOpenAI(
#                 api_key=settings.OPENAI_API_KEY,
#                 timeout=settings.LLM_REQUEST_TIMEOUT,
#             )

#     async def chat_completion(
#         self,
#         messages: List[Dict[str, Any]],
#         tools: List[Dict[str, Any]] | None = None,
#     ) -> Any:
#         """Call the chat completion API once, optionally with tool definitions.

#         Returns the raw `choices[0].message` object from the SDK response.

#         Raises:
#             LLMTimeoutError: if the request times out.
#             LLMServiceError: for any other provider-side failure.
#         """
#         try:
#             response = await self._client.chat.completions.create(
#                 model=self._settings.MODEL_NAME,
#                 messages=messages,
#                 tools=tools if tools else None,
#                 tool_choice="auto" if tools else None,
#                 max_tokens=self._settings.LLM_MAX_TOKENS,
#                 temperature=self._settings.LLM_TEMPERATURE,
#             )
#             return response.choices[0].message
#         except APITimeoutError as exc:
#             logger.error("LLM request timed out")
#             raise LLMTimeoutError() from exc
#         except asyncio.TimeoutError as exc:
#             logger.error("LLM request timed out (asyncio)")
#             raise LLMTimeoutError() from exc
#         except OpenAIError as exc:
#             logger.error("LLM provider error: %s", type(exc).__name__)
#             raise LLMServiceError() from exc

"""
LLM client abstraction.

Wraps the OpenAI Python SDK (also used, via its compatible API surface, for
Gemini if you point OPENAI base_url at Gemini's OpenAI-compatible endpoint).

This client normalizes provider-specific errors into our custom application
exceptions so the frontend always receives meaningful error messages.
"""

import asyncio
from typing import Any, Dict, List

from openai import (
    APITimeoutError,
    AsyncOpenAI,
    AuthenticationError,
    OpenAIError,
    RateLimitError,
)

from app.config.settings import get_settings
from app.utils.exceptions import (
    LLMQuotaExceededError,
    LLMServiceError,
    LLMTimeoutError,
)
from app.utils.logger import get_logger

logger = get_logger(__name__)


class LLMClient:
    """Provider-agnostic chat-completion client."""

    def __init__(self) -> None:
        settings = get_settings()
        self._settings = settings

        if settings.LLM_PROVIDER.lower() == "gemini":
            logger.info("Using Gemini API")

            self._client = AsyncOpenAI(
                api_key=settings.GEMINI_API_KEY,
                base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
                timeout=settings.LLM_REQUEST_TIMEOUT,
            )
        else:
            logger.info("Using OpenAI API")

            self._client = AsyncOpenAI(
                api_key=settings.OPENAI_API_KEY,
                timeout=settings.LLM_REQUEST_TIMEOUT,
            )

    async def chat_completion(
        self,
        messages: List[Dict[str, Any]],
        tools: List[Dict[str, Any]] | None = None,
    ) -> Any:
        """
        Execute one chat completion request.

        Returns:
            response.choices[0].message

        Raises:
            LLMTimeoutError
            LLMQuotaExceededError
            LLMServiceError
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

        # -----------------------------
        # Timeout
        # -----------------------------
        except APITimeoutError as exc:
            logger.error("LLM request timed out")
            raise LLMTimeoutError() from exc

        except asyncio.TimeoutError as exc:
            logger.error("Async timeout while calling LLM")
            raise LLMTimeoutError() from exc

        # -----------------------------
        # Rate Limit / Quota Exceeded
        # -----------------------------
        except RateLimitError as exc:
            logger.error("LLM quota exceeded: %s", exc)

            raise LLMQuotaExceededError() from exc

        # -----------------------------
        # Invalid API Key
        # -----------------------------
        except AuthenticationError as exc:
            logger.error("Invalid API Key: %s", exc)

            raise LLMServiceError(
                "AI service configuration error. Please contact support."
            ) from exc

        # -----------------------------
        # Other OpenAI/Gemini Errors
        # -----------------------------
        except OpenAIError as exc:

            error = str(exc)

            logger.error("LLM provider error: %s", error)

            # Gemini Free Tier Limit
            if (
                "RESOURCE_EXHAUSTED" in error
                or "Quota exceeded" in error
                or "generate_content_free_tier_requests" in error
                or "429" in error
            ):
                raise LLMQuotaExceededError() from exc

            # Invalid API Key
            if (
                "API_KEY_INVALID" in error
                or "invalid api key" in error.lower()
                or "authentication" in error.lower()
            ):
                raise LLMServiceError(
                    "AI service configuration error. Please contact support."
                ) from exc

            raise LLMServiceError() from exc

        # -----------------------------
        # Unexpected Errors
        # -----------------------------
        except Exception as exc:
            logger.exception("Unexpected error while calling LLM")

            raise LLMServiceError() from exc