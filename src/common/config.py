"""
Centralized configuration for the chat application.
Loads environment variables and exposes available models.
"""

import os
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()


class LLMConfig(BaseModel):
    """Configuration for connecting to the LLM via LiteLLM proxy."""
    base_url: str = os.getenv("OPENAI_ENDPOINT", "http://localhost:4000/")
    api_key: str = os.getenv("OPENAI_API_KEY", "my-secret-key")
    default_temperature: float = 0.7


class GroqConfig(BaseModel):
    """Configuration for connecting to Groq API."""
    api_key: str = os.getenv("GROQ_API_KEY", "")
    default_temperature: float = 0.7


# Model providers
class ModelProvider:
    LOCAL = "local"
    GROQ = "groq"


# Registry of available models (maps display name -> (provider, model_id))
AVAILABLE_MODELS: dict[str, tuple[str, str]] = {
    # Local models via LiteLLM
    "Phi-3": (ModelProvider.LOCAL, os.getenv("PHI3_DEPLOYMENT", "phi3")),
    "Gemma 2B": (ModelProvider.LOCAL, os.getenv("GEMMA_DEPLOYMENT", "gemma:2b")),
    "Mistral": (ModelProvider.LOCAL, os.getenv("MISTRAL_DEPLOYMENT", "mistral")),
    "GPT-4 Turbo": (ModelProvider.LOCAL, os.getenv("GPT_DEPLOYMENT", "gpt-4-turbo")),
    "Qwen3 4B": (ModelProvider.LOCAL, os.getenv("QWEN_DEPLOYMENT", "qwen3")),
    # Groq models
    "Groq GPT-OSS 120B": (ModelProvider.GROQ, "openai/gpt-oss-120b"),
    "Groq Llama 3.1 70B": (ModelProvider.GROQ, "llama-3.1-70b-versatile"),
    "Groq Llama 3.1 8B": (ModelProvider.GROQ, "llama-3.1-8b-instant"),
    "Groq Mixtral 8x7B": (ModelProvider.GROQ, "mixtral-8x7b-32768"),
}

DEFAULT_MODEL = "Phi-3"

# Singleton config instances
llm_config = LLMConfig()
groq_config = GroqConfig()


def get_chat_model(model_name: str = DEFAULT_MODEL, temperature: float | None = None):
    """Return the appropriate LangChain chat model for the given model name."""
    from langchain_openai import ChatOpenAI
    from langchain_groq import ChatGroq

    provider, model_id = AVAILABLE_MODELS.get(model_name, AVAILABLE_MODELS[DEFAULT_MODEL])

    if provider == ModelProvider.LOCAL:
        return ChatOpenAI(
            model=model_id,
            base_url=llm_config.base_url,
            api_key=llm_config.api_key,
            temperature=temperature or llm_config.default_temperature,
        )
    elif provider == ModelProvider.GROQ:
        return ChatGroq(
            model=model_id,
            api_key=groq_config.api_key,
            temperature=temperature or groq_config.default_temperature,
        )
    else:
        raise ValueError(f"Unknown provider: {provider}")
