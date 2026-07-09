"""
APNA AI -- Shopping Assistant microservice entrypoint.

Run locally with:
    uvicorn app.main:app --reload --port 8000

See README.md for full setup, environment variables, and deployment
instructions.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware



from app.config.settings import get_settings
from app.database.session import dispose_engine
from app.middleware.error_handler import register_exception_handlers
from app.middleware.logging_middleware import RequestLoggingMiddleware
from app.routers import auth, chat, conversation, health
from app.utils.logger import get_logger
from app.routers import debug


logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown hooks -- e.g. dispose the DB connection pool cleanly."""
    settings = get_settings()
    logger.info("Starting %s in %s mode", settings.APP_NAME, settings.APP_ENV)
    yield
    logger.info("Shutting down, disposing DB engine")
    await dispose_engine()


def create_app() -> FastAPI:
    """Application factory -- makes it easy to spin up isolated app
    instances in tests (see app/tests/conftest.py)."""
    settings = get_settings()

    app = FastAPI(
        title=settings.APP_NAME,
        description=(
            "Standalone AI shopping-assistant microservice for APNA STORE. "
            "Provides authenticated, tool-grounded chat over order, address, "
            "and account data, plus general store policy Q&A."
        ),
        version="1.0.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RequestLoggingMiddleware)

    register_exception_handlers(app)

    app.include_router(health.router)
    app.include_router(chat.router)
    app.include_router(conversation.router)
    app.include_router(auth.router)
    app.include_router(debug.router)

    return app


app = create_app()
