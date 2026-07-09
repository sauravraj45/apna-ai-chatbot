"""
Application configuration.

All runtime configuration is loaded from environment variables via a single
Pydantic `Settings` object. Nothing in the rest of the codebase should call
`os.environ` directly -- import `get_settings()` instead so configuration
stays centralized, typed, and easy to test (via dependency override).
"""

from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Strongly-typed application settings.

    Values are read from environment variables / a `.env` file. See
    `.env.example` for the full list of variables the service needs.
    """

    # --- App metadata -----------------------------------------------------
    APP_NAME: str = "APNA AI - Shopping Assistant"
    APP_ENV: str = "development"  # development | staging | production
    DEBUG: bool = True
    PORT: int = 8000

    # --- Database -----------------------------------------------------------
    DATABASE_URL: str
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_TIMEOUT: int = 30
    DB_ECHO: bool = False

    # --- Auth ---------------------------------------------------------------
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    # If your Node.js backend issues tokens with a different claim name for
    # the user id, adjust this so the FastAPI service reads the right field.
    JWT_USER_ID_CLAIM: str = "user_id"

    # --- LLM provider ---------------------------------------------------
    LLM_PROVIDER: str = "openai"  # openai | gemini
    OPENAI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    MODEL_NAME: str = "gpt-4o-mini"
    LLM_REQUEST_TIMEOUT: int = 30
    LLM_MAX_TOKENS: int = 800
    LLM_TEMPERATURE: float = 0.4

    # --- Conversation memory ----------------------------------------------
    MAX_MEMORY_MESSAGES: int = 20
    MEMORY_BACKEND: str = "in_memory"  # in_memory | redis (future)

    # --- CORS ---------------------------------------------------------------
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"

    # --- Logging --------------------------------------------------------
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    @property
    def cors_origins_list(self) -> List[str]:
        """Return CORS_ORIGINS as a parsed list."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance (singleton for the process)."""
    return Settings()
