"""Tests for JWT authentication behavior."""

import pytest

from app.utils.exceptions import AuthenticationError
from app.utils.security import create_dev_jwt, decode_jwt, extract_user_id


def test_valid_token_round_trip():
    token = create_dev_jwt(user_id=42)
    payload = decode_jwt(token)
    assert extract_user_id(payload) == 42


def test_invalid_token_raises_authentication_error():
    with pytest.raises(AuthenticationError):
        decode_jwt("not-a-real-jwt")


def test_missing_user_id_claim_raises():
    import jwt as pyjwt

    from app.config.settings import get_settings

    settings = get_settings()
    bad_payload = {"some_other_claim": 1}
    token = pyjwt.encode(bad_payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    payload = decode_jwt(token)
    with pytest.raises(AuthenticationError):
        extract_user_id(payload)


@pytest.mark.anyio
async def test_chat_requires_auth(client):
    response = await client.post("/chat", json={"message": "hello"})
    assert response.status_code == 401


@pytest.mark.anyio
async def test_dev_token_endpoint_issues_working_token(client):
    resp = await client.post("/auth/dev-token", json={"user_id": 7})
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    payload = decode_jwt(token)
    assert extract_user_id(payload) == 7
