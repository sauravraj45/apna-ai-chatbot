"""
Global exception handlers.

Registered on the FastAPI app in main.py. Ensures:
- Every error returns the same JSON shape (`ErrorResponse`).
- Internal details (stack traces, DB errors, library exceptions) are never
  leaked to the client -- only the safe `public_message` on AppException
  subclasses, or a generic message for anything unexpected.
"""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.schemas.common import ErrorResponse
from app.utils.exceptions import AppException
from app.utils.logger import get_logger

logger = get_logger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    """Attach all global exception handlers to the FastAPI app instance."""

    @app.exception_handler(AppException)
    async def handle_app_exception(request: Request, exc: AppException) -> JSONResponse:
        logger.warning("AppException on %s: %s (%s)", request.url.path, exc.error_code, exc.message)
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(error_code=exc.error_code, message=exc.message).model_dump(),
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
        logger.info("Validation error on %s", request.url.path)
        return JSONResponse(
            status_code=422,
            content=ErrorResponse(
                error_code="validation_error",
                message="The request was invalid. Please check your input and try again.",
                details=exc.errors(),
            ).model_dump(),
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
        # Catch-all: never leak internals of unexpected exceptions.
        logger.exception("Unhandled exception on %s", request.url.path)
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                error_code="internal_error",
                message="Something went wrong on our end. Please try again shortly.",
            ).model_dump(),
        )
