"""
Backend chat logic — creates LLM instances and handles conversations.
"""

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from groq import Groq

from config import llm_config, groq_config, AVAILABLE_MODELS, DEFAULT_MODEL, ModelProvider


def get_llm(model_name: str = DEFAULT_MODEL, temperature: float | None = None) -> ChatOpenAI:
    """Return a ChatOpenAI instance for the given model name (local models only)."""
    provider, model_id = AVAILABLE_MODELS.get(model_name, AVAILABLE_MODELS[DEFAULT_MODEL])
    
    if provider != ModelProvider.LOCAL:
        raise ValueError(f"Model {model_name} is not a local model. Use chat() instead.")
    
    return ChatOpenAI(
        model=model_id,
        base_url=llm_config.base_url,
        api_key=llm_config.api_key,
        temperature=temperature or llm_config.default_temperature,
    )


def get_groq_client() -> Groq:
    """Return a Groq client instance."""
    return Groq(api_key=groq_config.api_key)


def chat(messages: list, model_name: str = DEFAULT_MODEL, temperature: float | None = None, stream: bool = False) -> AIMessage | str:
    """
    Send a list of messages to the LLM and return the AI response.
    Supports both local models (via LangChain) and Groq models.
    
    Args:
        messages: List of messages (HumanMessage, AIMessage, SystemMessage, or dicts)
        model_name: Name of the model to use
        temperature: Temperature for response generation
        stream: Whether to stream the response (Groq only)
    
    Returns:
        AIMessage for local models or string for Groq models
    """
    provider, model_id = AVAILABLE_MODELS.get(model_name, AVAILABLE_MODELS[DEFAULT_MODEL])
    temp = temperature or (groq_config.default_temperature if provider == ModelProvider.GROQ else llm_config.default_temperature)
    
    if provider == ModelProvider.LOCAL:
        # Use LangChain for local models
        llm = ChatOpenAI(
            model=model_id,
            base_url=llm_config.base_url,
            api_key=llm_config.api_key,
            temperature=temp,
        )
        return llm.invoke(messages)
    
    elif provider == ModelProvider.GROQ:
        # Use Groq API
        groq_client = get_groq_client()
        
        # Convert LangChain messages to Groq format
        groq_messages = []
        for msg in messages:
            if isinstance(msg, HumanMessage):
                groq_messages.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AIMessage):
                groq_messages.append({"role": "assistant", "content": msg.content})
            elif isinstance(msg, SystemMessage):
                groq_messages.append({"role": "system", "content": msg.content})
            elif isinstance(msg, dict):
                groq_messages.append(msg)
        
        # Make Groq API call
        if stream:
            # Return streaming response as generator
            completion = groq_client.chat.completions.create(
                model=model_id,
                messages=groq_messages,
                temperature=temp,
                stream=True,
            )
            
            full_response = ""
            for chunk in completion:
                content = chunk.choices[0].delta.content or ""
                full_response += content
            return AIMessage(content=full_response)
        else:
            # Non-streaming response
            completion = groq_client.chat.completions.create(
                model=model_id,
                messages=groq_messages,
                temperature=temp,
                stream=False,
            )
            return AIMessage(content=completion.choices[0].message.content)
    
    else:
        raise ValueError(f"Unknown provider: {provider}")


# Quick smoke test when run directly
if __name__ == "__main__":
    response = chat([HumanMessage(content="What is the capital of France?")])
    print(response.content)