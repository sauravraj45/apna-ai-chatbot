"""HTTP-level request/response logging middleware."""

import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.utils.logger import get_logger

logger = get_logger("app.request")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Logs method, path, status code, and duration for every request.

    Deliberately does NOT log headers, bodies, or query strings, since those
    may contain JWTs or user-entered text.
    """

    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())[:8]
        start = time.perf_counter()

        logger.info("[%s] --> %s %s", request_id, request.method, request.url.path)

        try:
            response = await call_next(request)
        except Exception:
            duration_ms = (time.perf_counter() - start) * 1000
            logger.exception("[%s] <-- unhandled error after %.1fms", request_id, duration_ms)
            raise

        duration_ms = (time.perf_counter() - start) * 1000
        logger.info(
            "[%s] <-- %s %s status=%s duration=%.1fms",
            request_id,
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )
        response.headers["X-Request-ID"] = request_id
        return response
