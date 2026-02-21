"""
LangGraph ReAct agent with tool support.
The agent automatically decides when to call tools (e.g. web search)
based on the user's message.
"""

from typing import Any
from uuid import UUID
from datetime import datetime, timezone

from langchain_core.callbacks import AsyncCallbackHandler
from langchain_core.messages import AIMessage
from langchain_core.outputs import LLMResult
from langchain.agents import create_agent

from src.common.config import DEFAULT_MODEL, get_chat_model
from src.common.logger import get_logger
from src.core.tools import ALL_TOOLS

log = get_logger(__name__)

_MAX_RESULT_LOG_LEN = 300  # truncate long tool outputs in logs


class AgentLogger(AsyncCallbackHandler):
    """Async callback handler that logs each step of the ReAct loop."""

    async def on_llm_start(self, serialized: dict, prompts: list[str], **kwargs: Any) -> None:
        model = serialized.get("kwargs", {}).get("model_name") or serialized.get("name", "llm")
        log.debug("LLM thinking: model=%s, prompt_messages=%d", model, len(prompts))

    async def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        usage = getattr(response, "llm_output", {}) or {}
        token_info = usage.get("token_usage") or usage.get("usage") or {}
        if token_info:
            log.debug(
                "LLM done: prompt_tokens=%s, completion_tokens=%s",
                token_info.get("prompt_tokens", "?"),
                token_info.get("completion_tokens", "?"),
            )
        else:
            log.debug("LLM done")

    async def on_tool_start(
        self, serialized: dict, input_str: str, *, run_id: UUID, **kwargs: Any
    ) -> None:
        tool_name = serialized.get("name", "tool")
        log.info("Tool call → %s | query: %s", tool_name, input_str[:200])

    async def on_tool_end(self, output: Any, *, run_id: UUID, **kwargs: Any) -> None:
        text = str(output)
        truncated = text[:_MAX_RESULT_LOG_LEN] + ("…" if len(text) > _MAX_RESULT_LOG_LEN else "")
        log.info("Tool result (%d chars): %s", len(text), truncated)

    async def on_tool_error(self, error: BaseException, *, run_id: UUID, **kwargs: Any) -> None:
        log.error("Tool error: %s", error)


_callback = AgentLogger()


def _build_system_prompt() -> str:
    """Build the agent system prompt with the current UTC date/time injected."""
    now = datetime.now(timezone.utc)
    timestamp = now.strftime("%A, %B %d, %Y %H:%M UTC")
    return (
        f"Today is {timestamp}.\n\n"
        "You are a helpful assistant with access to the following tools ONLY:\n"
        + "\n".join(f"- {t.name}: {t.description}" for t in ALL_TOOLS)
        + "\n\nIMPORTANT RULES:\n"
        "1. You may ONLY call the tools listed above. Never invent or hallucinate tool names.\n"
        "2. If search results contain URLs, summarise the information — do NOT try to open or fetch URLs.\n"
        "3. If you cannot answer from the search results, say so honestly.\n"
    )


def build_agent(model_name: str = DEFAULT_MODEL, temperature: float | None = None):
    """Build a compiled LangGraph ReAct agent for the given model."""
    model = get_chat_model(model_name, temperature)
    log.debug("Building ReAct agent: model=%s, tools=%s", model_name, [t.name for t in ALL_TOOLS])
    return create_agent(model, ALL_TOOLS, system_prompt=_build_system_prompt())


async def run_agent(
    messages: list,
    model_name: str = DEFAULT_MODEL,
    temperature: float | None = None,
) -> AIMessage:
    """
    Run the ReAct agent against the provided message history.

    The agent will invoke tools as needed before composing its
    final reply. Returns the last AIMessage from the graph.
    """
    log.info("Agent invoked: model=%s, input_messages=%d", model_name, len(messages))
    agent = build_agent(model_name, temperature)

    max_retries = 2
    for attempt in range(1, max_retries + 2):
        try:
            result = await agent.ainvoke(
                {"messages": messages},
                config={"callbacks": [_callback]},
            )
            break
        except Exception as exc:
            # Retry on hallucinated tool calls (Groq returns 400)
            if "not in request.tools" in str(exc) and attempt <= max_retries:
                log.warning(
                    "Model hallucinated a tool call (attempt %d/%d), retrying: %s",
                    attempt, max_retries, exc,
                )
                continue
            raise

    all_messages = result["messages"]
    final = all_messages[-1]
    tool_calls = sum(1 for m in all_messages if getattr(m, "type", None) == "tool")
    log.info(
        "Agent done: total_messages=%d, tool_calls=%d, reply=%d chars",
        len(all_messages),
        tool_calls,
        len(final.content),
    )
    return final
