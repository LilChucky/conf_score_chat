"""
Backend chat logic — creates LLM instances and handles conversations.
"""

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from config import llm_config, AVAILABLE_MODELS, DEFAULT_MODEL


def get_llm(model_name: str = DEFAULT_MODEL, temperature: float | None = None) -> ChatOpenAI:
    """Return a ChatOpenAI instance for the given model name."""
    model_id = AVAILABLE_MODELS.get(model_name, AVAILABLE_MODELS[DEFAULT_MODEL])
    return ChatOpenAI(
        model=model_id,
        base_url=llm_config.base_url,
        api_key=llm_config.api_key,
        temperature=temperature or llm_config.default_temperature,
    )


def chat(messages: list, model_name: str = DEFAULT_MODEL, temperature: float | None = None) -> AIMessage:
    """Send a list of messages to the LLM and return the AI response."""
    llm = get_llm(model_name, temperature)
    return llm.invoke(messages)


# Quick smoke test when run directly
if __name__ == "__main__":
    response = chat([HumanMessage(content="What is the capital of France?")])
    print(response.content)