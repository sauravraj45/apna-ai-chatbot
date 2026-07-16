
"""
Async SQLAlchemy 2.0 database session management.

Connects to the SAME Railway MySQL database used by the existing
Node.js backend.

The chatbot mainly performs read operations but uses a standard
async SQLAlchemy session so future features (logging, support
tickets, etc.) can also write to the database.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config.settings import get_settings
from app.utils.exceptions import (
    AppException,
    DatabaseError,
)
from app.utils.logger import get_logger

logger = get_logger(__name__)

_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def _normalize_db_url(url: str) -> str:
    """
    Normalize database URLs so SQLAlchemy uses the correct async driver.

    Supported databases:
    - MySQL (Railway)
    - PostgreSQL (Future support)
    """

    # Railway MySQL
    if url.startswith("mysql://"):
        return url.replace(
            "mysql://",
            "mysql+asyncmy://",
            1,
        )

    if url.startswith("mysql+pymysql://"):
        return url.replace(
            "mysql+pymysql://",
            "mysql+asyncmy://",
            1,
        )

    # PostgreSQL
    if url.startswith("postgresql://"):
        return url.replace(
            "postgresql://",
            "postgresql+asyncpg://",
            1,
        )

    if url.startswith("postgres://"):
        return url.replace(
            "postgres://",
            "postgresql+asyncpg://",
            1,
        )

    return url


def get_engine() -> AsyncEngine:
    """Create (if necessary) and return the global async database engine."""

    global _engine

    if _engine is None:
        settings = get_settings()

        _engine = create_async_engine(
            _normalize_db_url(settings.DATABASE_URL),
            echo=settings.DB_ECHO,
            pool_size=settings.DB_POOL_SIZE,
            max_overflow=settings.DB_MAX_OVERFLOW,
            pool_timeout=settings.DB_POOL_TIMEOUT,
            pool_pre_ping=True,
            pool_recycle=3600,
            future=True,
        )

    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Create (if necessary) and return the async session factory."""

    global _session_factory

    if _session_factory is None:
        _session_factory = async_sessionmaker(
            bind=get_engine(),
            expire_on_commit=False,
            autoflush=False,
            autocommit=False,
        )

    return _session_factory


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency.

    Example:

        async def endpoint(
            db: AsyncSession = Depends(get_db)
        ):
            ...
    """

    session_factory = get_session_factory()

    async with session_factory() as session:
        try:
            yield session

        # Let application errors pass through unchanged
        except AppException:
            raise

        # Convert only real database/session errors
        except Exception as exc:
            await session.rollback()
            logger.exception("Database session error")
            raise DatabaseError() from exc

        finally:
            await session.close()


@asynccontextmanager
async def db_session_scope() -> AsyncGenerator[AsyncSession, None]:
    """
    Async context manager for using a DB session outside
    FastAPI dependency injection.
    """

    session_factory = get_session_factory()

    async with session_factory() as session:
        try:
            yield session

        # Let application errors pass through unchanged
        except AppException:
            raise

        # Convert only database errors
        except Exception as exc:
            await session.rollback()
            logger.exception("Database session error")
            raise DatabaseError() from exc

        finally:
            await session.close()


async def check_db_connection() -> bool:
    """
    Used by the /health endpoint.

    Returns:
        True  -> Database connected
        False -> Database unreachable
    """

    try:
        engine = get_engine()

        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))

        logger.info("Database connection successful.")

        return True

    except Exception:
        logger.exception("Database health check failed.")
        return False


async def dispose_engine() -> None:
    """
    Dispose the SQLAlchemy connection pool during shutdown.
    """

    global _engine
    global _session_factory

    if _engine is not None:
        await _engine.dispose()

    _engine = None
    _session_factory = None