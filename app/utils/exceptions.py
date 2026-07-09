"""
Custom exception hierarchy.

Using typed exceptions (instead of raising raw HTTPException everywhere)
keeps business logic decoupled from FastAPI and lets the global exception
handler in `app.middleware.error_handler` translate each one into a
consistent, safe JSON response.
"""


class AppException(Exception):
    """Base class for all application-raised, expected errors."""

    status_code: int = 500
    error_code: str = "internal_error"
    public_message: str = "Something went wrong. Please try again."

    def __init__(self, message: str | None = None):
        self.message = message or self.public_message
        super().__init__(self.message)


class AuthenticationError(AppException):
    status_code = 401
    error_code = "authentication_error"
    public_message = "Your session is invalid or has expired. Please log in again."


class AuthorizationError(AppException):
    status_code = 403
    error_code = "authorization_error"
    public_message = "You are not allowed to access this resource."

class LLMQuotaExceededError(AppException):
    status_code = 429
    error_code = "ai_quota_exceeded"
    public_message = (
        "Daily AI request limit has been reached. Please try again later."
    )

class ResourceNotFoundError(AppException):
    status_code = 404
    error_code = "not_found"
    public_message = "The requested information could not be found."


class ValidationAppError(AppException):
    status_code = 422
    error_code = "validation_error"
    public_message = "The request could not be processed. Please check your input."


class DatabaseError(AppException):
    status_code = 503
    error_code = "database_error"
    public_message = "We're having trouble reaching the database right now. Please try again shortly."


class LLMServiceError(AppException):
    status_code = 503
    error_code = "ai_service_error"
    public_message = "Our assistant is temporarily unavailable. Please try again in a moment."


class LLMTimeoutError(AppException):
    status_code = 408
    error_code = "ai_timeout"
    public_message = "The assistant took too long to respond. Please try again."


class ConversationNotFoundError(AppException):
    status_code = 404
    error_code = "conversation_not_found"
    public_message = "We couldn't find that conversation."

class LLMInvalidAPIKeyError(AppException):
    status_code = 401
    error_code = "invalid_api_key"
    public_message = "AI service configuration error. Please contact support."