"""Tests for src.common.config."""

import pytest
from unittest.mock import patch

from src.common.config import (
    AVAILABLE_MODELS,
    DEFAULT_MODEL,
    ModelProvider,
    LLMConfig,
    GroqConfig,
    get_chat_model,
)


class TestModelRegistry:
    """Verify the model registry is well-formed."""

    def test_default_model_exists(self):
        assert DEFAULT_MODEL in AVAILABLE_MODELS

    def test_all_entries_have_provider_and_id(self):
        for name, (provider, model_id) in AVAILABLE_MODELS.items():
            assert provider in (ModelProvider.LOCAL, ModelProvider.GROQ), f"{name}: bad provider '{provider}'"
            assert isinstance(model_id, str) and len(model_id) > 0, f"{name}: empty model_id"

    def test_at_least_one_local_and_one_groq(self):
        providers = {p for p, _ in AVAILABLE_MODELS.values()}
        assert ModelProvider.LOCAL in providers
        assert ModelProvider.GROQ in providers


class TestConfigs:
    """Verify config models have sensible defaults."""

    def test_llm_config_defaults(self):
        cfg = LLMConfig()
        assert "localhost" in cfg.base_url or cfg.base_url.startswith("http")
        assert cfg.default_temperature > 0

    def test_groq_config_defaults(self):
        cfg = GroqConfig()
        assert isinstance(cfg.api_key, str)
        assert cfg.default_temperature > 0


class TestGetChatModel:
    """Verify model factory returns the right type."""

    def test_local_returns_chatopenai(self):
        model = get_chat_model("Phi-3", temperature=0.5)
        from langchain_openai import ChatOpenAI
        assert isinstance(model, ChatOpenAI)

    def test_groq_returns_chatgroq(self):
        model = get_chat_model("Groq Llama 3.1 8B", temperature=0.5)
        from langchain_groq import ChatGroq
        assert isinstance(model, ChatGroq)

    def test_unknown_model_falls_back_to_default(self):
        model = get_chat_model("NonExistentModel", temperature=0.5)
        # Should fall back to DEFAULT_MODEL (Phi-3 → local → ChatOpenAI)
        from langchain_openai import ChatOpenAI
        assert isinstance(model, ChatOpenAI)
