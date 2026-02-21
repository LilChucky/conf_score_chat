"""
Chat service — thin async wrapper over the LangGraph ReAct agent.
All model routing and tool execution is handled in agent.py.
"""

from langchain_core.messages import AIMessage

from src.common.config import DEFAULT_MODEL
from src.common.logger import get_logger
from src.core.agent import run_agent

log = get_logger(__name__)


async def chat(
    messages: list,
    model_name: str = DEFAULT_MODEL,
    temperature: float | None = None,
) -> AIMessage:
    """
    Send a list of messages to the LangGraph ReAct agent and return the reply.
    The agent has access to web search and will use it automatically
    when the query benefits from real-time information.
    """
    log.debug("chat() → run_agent: model=%s", model_name)
    return await run_agent(messages, model_name=model_name, temperature=temperature)
