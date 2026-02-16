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


# Registry of available models (maps display name -> LiteLLM model_name)
AVAILABLE_MODELS: dict[str, str] = {
    "Phi-3": os.getenv("PHI3_DEPLOYMENT", "phi3"),
    "Gemma 2B": os.getenv("GEMMA_DEPLOYMENT", "gemma:2b"),
    "Mistral": os.getenv("MISTRAL_DEPLOYMENT", "mistral"),
    "GPT-4 Turbo": os.getenv("GPT_DEPLOYMENT", "gpt-4-turbo"),
    "Qwen3 4B": os.getenv("QWEN_DEPLOYMENT", "qwen3"),
}

DEFAULT_MODEL = "Phi-3"

# Singleton config instance
llm_config = LLMConfig()
