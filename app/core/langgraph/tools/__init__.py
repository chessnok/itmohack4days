"""LangGraph tools for enhanced language model capabilities.

This package contains custom tools that can be used with LangGraph to extend
the capabilities of language models. Currently includes tools for web search
and other external integrations.
"""

from langchain_core.tools.base import BaseTool

from .QueryTool import file_search_tool
from .duckduckgo_search import duckduckgo_search_tool

tools: list[BaseTool] = [duckduckgo_search_tool,file_search_tool]
