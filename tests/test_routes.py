"""Tests for API routes (FastAPI endpoints)."""

import pytest
from src.common.config import AVAILABLE_MODELS, DEFAULT_MODEL


class TestHealth:

    async def test_health_returns_ok(self, client):
        resp = await client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}


class TestGetModels:

    async def test_returns_model_list(self, client):
        resp = await client.get("/models")
        assert resp.status_code == 200
        data = resp.json()
        assert "models" in data
        assert "default" in data
        assert data["default"] == DEFAULT_MODEL
        assert len(data["models"]) == len(AVAILABLE_MODELS)

    async def test_all_registered_models_present(self, client):
        resp = await client.get("/models")
        models = resp.json()["models"]
        for name in AVAILABLE_MODELS:
            assert name in models


class TestPostChat:

    async def test_successful_chat(self, client, mock_core_chat, mock_ai_reply):
        payload = {
            "messages": [{"role": "user", "content": "Hi"}],
            "model": DEFAULT_MODEL,
        }
        resp = await client.post("/chat", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["content"] == mock_ai_reply.content
        assert data["model"] == DEFAULT_MODEL
        mock_core_chat.assert_awaited_once()

    async def test_unknown_model_422(self, client):
        payload = {
            "messages": [{"role": "user", "content": "Hi"}],
            "model": "NonExistentModel",
        }
        resp = await client.post("/chat", json=payload)
        assert resp.status_code == 422

    async def test_invalid_role_422(self, client, mock_core_chat):
        payload = {
            "messages": [{"role": "alien", "content": "Hi"}],
            "model": DEFAULT_MODEL,
        }
        resp = await client.post("/chat", json=payload)
        assert resp.status_code == 422

    async def test_empty_messages(self, client, mock_core_chat, mock_ai_reply):
        payload = {"messages": [], "model": DEFAULT_MODEL}
        resp = await client.post("/chat", json=payload)
        assert resp.status_code == 200

    async def test_system_and_user_messages(self, client, mock_core_chat, mock_ai_reply):
        payload = {
            "messages": [
                {"role": "system", "content": "You are helpful."},
                {"role": "user", "content": "Hi"},
            ],
            "model": DEFAULT_MODEL,
        }
        resp = await client.post("/chat", json=payload)
        assert resp.status_code == 200

    async def test_chat_error_returns_500(self, client):
        """If the agent raises, the route should return 500."""
        from unittest.mock import AsyncMock, patch

        with patch(
            "src.api.routes.core_chat",
            new_callable=AsyncMock,
            side_effect=RuntimeError("LLM exploded"),
        ):
            payload = {
                "messages": [{"role": "user", "content": "Hi"}],
                "model": DEFAULT_MODEL,
            }
            resp = await client.post("/chat", json=payload)
            assert resp.status_code == 500
            assert "LLM exploded" in resp.json()["detail"]
