"""
Tool definitions for the LangGraph ReAct agent.
Each tool is a LangChain-compatible tool instance ready for binding.
"""

from langchain_community.tools import DuckDuckGoSearchResults

web_search = DuckDuckGoSearchResults(
    num_results=5,
    output_format="list",
)

# All tools available to the agent — extend this list to add new capabilities
ALL_TOOLS = [web_search]
