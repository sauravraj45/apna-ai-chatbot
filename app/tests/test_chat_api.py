"""
API-level tests for /chat and /conversation endpoints.

The AI service (and therefore the real LLM call) is mocked out so these
tests run fast, offline, and deterministically -- they verify routing,
auth enforcement, and response shape rather than actual model behavior.
"""

from unittest.mock import AsyncMock, patch

import pytest


@pytest.mark.anyio
async def test_chat_success(client, auth_headers):
    with patch(
        "app.routers.chat._ai_service.handle_chat_turn",
        new=AsyncMock(return_value=("Here is your latest order status.", "conv-123")),
    ):
        response = await client.post(
            "/chat",
            json={"message": "Track my latest order"},
            headers=auth_headers,
        )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["conversation_id"] == "conv-123"
    assert "order status" in body["reply"]


@pytest.mark.anyio
async def test_chat_rejects_missing_auth(client):
    response = await client.post("/chat", json={"message": "hi"})
    assert response.status_code == 401


@pytest.mark.anyio
async def test_chat_rejects_empty_message(client, auth_headers):
    response = await client.post("/chat", json={"message": ""}, headers=auth_headers)
    assert response.status_code == 422


@pytest.mark.anyio
async def test_health_endpoint_no_auth_required(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert "status" in response.json()


@pytest.mark.anyio
async def test_conversation_history_not_found(client, auth_headers):
    response = await client.get(
        "/conversation/history",
        params={"conversation_id": "does-not-exist"},
        headers=auth_headers,
    )
    assert response.status_code == 404
