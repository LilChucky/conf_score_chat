"""
Shared test fixtures.
"""

import pytest
from unittest.mock import AsyncMock, patch
from httpx import ASGITransport, AsyncClient
from langchain_core.messages import AIMessage

from src.api.app import app


@pytest.fixture
def mock_ai_reply():
    """A reusable mock AIMessage."""
    return AIMessage(content="Hello from the test agent!")


@pytest.fixture
def mock_core_chat(mock_ai_reply):
    """Patch core.chat so no real LLM calls are made."""
    with patch("src.api.routes.core_chat", new_callable=AsyncMock, return_value=mock_ai_reply) as m:
        yield m


@pytest.fixture
async def client():
    """Async test client for the FastAPI app."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
