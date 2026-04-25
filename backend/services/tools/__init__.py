"""
MAARS tool registry — agents can call any registered tool by name.

Tools are small, deterministic units of work the orchestrator can invoke mid-plan:
web_search, http_fetch, code_executor, db_query. Each implements `Tool.run(args)`
and declares JSON-schema for its arguments so the LLM can pick them correctly.
"""
from __future__ import annotations

from .base import Tool, ToolResult
from .code_executor import CodeExecutorTool
from .db_query import DBQueryTool
from .http_fetch import HttpFetchTool
from .web_search import WebSearchTool

_REGISTRY: dict[str, Tool] = {}


def register(tool: Tool) -> None:
    _REGISTRY[tool.name] = tool


def get_tool(name: str) -> Tool | None:
    return _REGISTRY.get(name)


def list_tools() -> list[Tool]:
    return list(_REGISTRY.values())


# Register defaults.
register(WebSearchTool())
register(HttpFetchTool())
register(CodeExecutorTool())
register(DBQueryTool())


__all__ = ["Tool", "ToolResult", "register", "get_tool", "list_tools"]
