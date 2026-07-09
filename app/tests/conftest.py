"""Shared pytest fixtures."""

import os
from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient

# Ensure required env vars exist before Settings() is constructed anywhere.
os.environ.setdefault("DATABASE_URL", "postgresql://user:pass@localhost:5432/testdb")
os.environ.setdefault("JWT_SECRET", "test-secret-key-for-unit-tests")
os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("APP_ENV", "testing")

from app.main import create_app  # noqa: E402
from app.utils.security import create_dev_jwt  # noqa: E402


@pytest.fixture
def app():
    return create_app()


@pytest.fixture
async def client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def auth_headers():
    token = create_dev_jwt(user_id=1)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def mock_db_session():
    """A minimal AsyncMock standing in for an AsyncSession in tool unit tests."""
    return AsyncMock()
