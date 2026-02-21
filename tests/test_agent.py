"""Tests for the LangGraph agent (src.core.agent)."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from langchain_core.messages import AIMessage, HumanMessage

from src.core.agent import build_agent, run_agent, AgentLogger, _build_system_prompt


class TestSystemPrompt:

    def test_contains_current_date(self):
        from datetime import datetime, timezone
        prompt = _build_system_prompt()
        today = datetime.now(timezone.utc).strftime("%Y")  # at least the year
        assert today in prompt

    def test_contains_tool_names(self):
        from src.core.tools import ALL_TOOLS
        prompt = _build_system_prompt()
        for tool in ALL_TOOLS:
            assert tool.name in prompt

    def test_contains_utc(self):
        assert "UTC" in _build_system_prompt()

    def test_fresh_timestamp_each_call(self):
        """Two calls should produce the same date (same minute), not a stale one."""
        from datetime import datetime, timezone
        prompt = _build_system_prompt()
        year = datetime.now(timezone.utc).strftime("%Y")
        assert year in prompt


class TestBuildAgent:

    def test_returns_compiled_graph(self):
        """build_agent should return a compiled LangGraph runnable."""
        with patch("src.core.agent.get_chat_model") as mock_model:
            mock_model.return_value = MagicMock()
            agent = build_agent("Phi-3", temperature=0.5)
            # Should have ainvoke / invoke methods
            assert hasattr(agent, "ainvoke") or hasattr(agent, "invoke")


class TestRunAgent:

    async def test_returns_ai_message(self):
        """run_agent should return the last AIMessage from the graph."""
        fake_reply = AIMessage(content="Agent reply")
        fake_result = {"messages": [HumanMessage(content="Hi"), fake_reply]}

        with patch("src.core.agent.build_agent") as mock_build:
            mock_agent = AsyncMock()
            mock_agent.ainvoke.return_value = fake_result
            mock_build.return_value = mock_agent

            result = await run_agent(
                [HumanMessage(content="Hi")],
                model_name="Phi-3",
                temperature=0.5,
            )
            assert isinstance(result, AIMessage)
            assert result.content == "Agent reply"
            mock_agent.ainvoke.assert_awaited_once()

    async def test_counts_tool_calls(self):
        """run_agent logs should count tool messages."""
        tool_msg = MagicMock()
        tool_msg.type = "tool"
        tool_msg.content = "search results"
        fake_result = {
            "messages": [
                HumanMessage(content="Hi"),
                tool_msg,
                AIMessage(content="Done"),
            ]
        }

        with patch("src.core.agent.build_agent") as mock_build:
            mock_agent = AsyncMock()
            mock_agent.ainvoke.return_value = fake_result
            mock_build.return_value = mock_agent

            result = await run_agent([HumanMessage(content="Hi")])
            assert result.content == "Done"

    async def test_retries_on_hallucinated_tool(self):
        """run_agent should retry when the model hallucinates a tool call."""
        fake_reply = AIMessage(content="Retried answer")
        fake_result = {"messages": [HumanMessage(content="Hi"), fake_reply]}

        with patch("src.core.agent.build_agent") as mock_build:
            mock_agent = AsyncMock()
            # First call raises the hallucinated-tool error, second succeeds
            mock_agent.ainvoke.side_effect = [
                Exception("tool call validation failed: attempted to call tool 'open_file' which was not in request.tools"),
                fake_result,
            ]
            mock_build.return_value = mock_agent

            result = await run_agent([HumanMessage(content="Hi")])
            assert result.content == "Retried answer"
            assert mock_agent.ainvoke.await_count == 2

    async def test_raises_after_max_retries(self):
        """run_agent should raise after exceeding retry limit."""
        with patch("src.core.agent.build_agent") as mock_build:
            mock_agent = AsyncMock()
            mock_agent.ainvoke.side_effect = Exception(
                "not in request.tools"
            )
            mock_build.return_value = mock_agent

            with pytest.raises(Exception, match="not in request.tools"):
                await run_agent([HumanMessage(content="Hi")])


class TestAgentLogger:
    """Verify the async callback handler doesn't raise."""

    async def test_on_llm_start(self):
        logger = AgentLogger()
        await logger.on_llm_start({"name": "test-model"}, ["prompt1"])

    async def test_on_llm_end(self):
        logger = AgentLogger()
        mock_response = MagicMock()
        mock_response.llm_output = {"token_usage": {"prompt_tokens": 10, "completion_tokens": 5}}
        await logger.on_llm_end(mock_response)

    async def test_on_llm_end_no_usage(self):
        logger = AgentLogger()
        mock_response = MagicMock()
        mock_response.llm_output = None
        await logger.on_llm_end(mock_response)

    async def test_on_tool_start(self):
        from uuid import uuid4

        logger = AgentLogger()
        await logger.on_tool_start({"name": "web_search"}, "query text", run_id=uuid4())

    async def test_on_tool_end(self):
        from uuid import uuid4

        logger = AgentLogger()
        await logger.on_tool_end("search result text", run_id=uuid4())

    async def test_on_tool_error(self):
        from uuid import uuid4

        logger = AgentLogger()
        await logger.on_tool_error(RuntimeError("tool broke"), run_id=uuid4())
