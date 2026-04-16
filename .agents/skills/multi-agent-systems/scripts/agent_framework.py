"""
Multi-Agent System Framework

Provides base classes and utilities for building orchestrator-subagent architectures.
"""

import asyncio
from typing import Any, Callable
from anthropic import Anthropic, AsyncAnthropic


class AgentBase:
    """Base class for all agents in the system."""

    def __init__(self, client: Anthropic = None, model: str = "claude-sonnet-4-5"):
        self.client = client or Anthropic()
        self.model = model
        self.system_prompt = self._get_system_prompt()
        self.tools = self._get_tools()

    def _get_system_prompt(self) -> str:
        raise NotImplementedError

    def _get_tools(self) -> list:
        return []

    def run(self, user_message: str, max_tokens: int = 4096) -> Any:
        """Execute agent synchronously."""
        messages = [{"role": "user", "content": user_message}]
        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=self.system_prompt,
            messages=messages,
            tools=self.tools
        )
        return self._process_response(response)

    def _process_response(self, response) -> Any:
        return response


class Subagent(AgentBase):
    """Base class for subagents with isolated context."""

    def __init__(self, client: Anthropic = None, model: str = "claude-sonnet-4-5"):
        super().__init__(client, model)
        self._context = []

    def add_context(self, role: str, content: str):
        """Add message to subagent context."""
        self._context.append({"role": role, "content": content})

    def run_with_context(self, user_message: str, max_tokens: int = 2048) -> Any:
        """Execute with accumulated context."""
        messages = self._context + [{"role": "user", "content": user_message}]
        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=self.system_prompt,
            messages=messages,
            tools=self.tools
        )
        return self._process_response(response)


class AsyncSubagent(Subagent):
    """Async version of Subagent."""

    def __init__(self, client: AsyncAnthropic = None, model: str = "claude-sonnet-4-5"):
        super().__init__(client, model)
        self._async_client = client or AsyncAnthropic()

    async def run_async(self, user_message: str, max_tokens: int = 2048) -> Any:
        """Execute subagent asynchronously."""
        messages = self._context + [{"role": "user", "content": user_message}]
        response = await self._async_client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=self.system_prompt,
            messages=messages,
            tools=self.tools
        )
        return self._process_response(response)


class OrchestratorAgent(AgentBase):
    """Agent that coordinates multiple subagents."""

    def __init__(self, client: Anthropic = None, model: str = "claude-sonnet-4-5"):
        super().__init__(client, model)
        self.subagents: dict[str, AgentBase] = {}

    def register_subagent(self, name: str, subagent: AgentBase):
        """Register a subagent for delegation."""
        self.subagents[name] = subagent

    def _get_delegation_tools(self) -> list:
        """Generate delegate tools for each registered subagent."""
        tools = []
        for name in self.subagents:
            tools.append({
                "name": f"delegate_to_{name}",
                "description": f"Delegate to {name} specialist",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "task": {"type": "string", "description": f"Task for {name}"}
                    },
                    "required": ["task"]
                }
            })
        return tools

    def _get_tools(self) -> list:
        return self._get_delegation_tools()
