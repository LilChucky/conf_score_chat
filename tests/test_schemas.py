"""Tests for src.api.schemas."""

import pytest
from pydantic import ValidationError

from src.api.schemas import Message, ChatRequest, ChatResponse, ModelsResponse


class TestMessageSchema:

    def test_valid_message(self):
        m = Message(role="user", content="hello")
        assert m.role == "user"
        assert m.content == "hello"

    def test_missing_role_raises(self):
        with pytest.raises(ValidationError):
            Message(content="hello")  # role is required

    def test_missing_content_raises(self):
        with pytest.raises(ValidationError):
            Message(role="user")  # content is required


class TestChatRequest:

    def test_defaults(self):
        req = ChatRequest(messages=[Message(role="user", content="hi")])
        assert req.model is not None  # has default
        assert req.temperature is None  # optional

    def test_custom_values(self):
        req = ChatRequest(
            messages=[Message(role="user", content="hi")],
            model="Mistral",
            temperature=0.3,
        )
        assert req.model == "Mistral"
        assert req.temperature == 0.3

    def test_empty_messages(self):
        req = ChatRequest(messages=[])
        assert req.messages == []


class TestChatResponse:

    def test_valid(self):
        resp = ChatResponse(content="world", model="Phi-3")
        assert resp.content == "world"

    def test_missing_content_raises(self):
        with pytest.raises(ValidationError):
            ChatResponse(model="Phi-3")


class TestModelsResponse:

    def test_valid(self):
        resp = ModelsResponse(models=["Phi-3", "Mistral"], default="Phi-3")
        assert len(resp.models) == 2
        assert resp.default == "Phi-3"
