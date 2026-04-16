#!/usr/bin/env python3
"""Examples of using the claude_agent module.

Demonstrates:
- Basic agent calls
- Session continuation
- Hook integration
- Request/response logging
- Session management

Requires: claude_agent module from tools/agents/
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    pass

# Add paths for imports
# Calculate path relative to this file: .claude/skills/claude-agent-sdk/scripts/
# Need to go up 4 levels to .claude directory
_claude_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_claude_root / "tools" / "agents"))
sys.path.insert(0, str(_claude_root))


class LoggerProtocol(Protocol):
    """Protocol for logger interface."""

    def info(self, message: str) -> None:
        """Log info message."""
        ...

    def exception(self, message: str) -> None:
        """Log exception message."""
        ...


class SimpleLogger:
    """Simple logger for examples when full logging not available."""

    def info(self, message: str) -> None:
        """Print info message."""
        print(message)

    def exception(self, message: str) -> None:
        """Print error message."""
        print(f"ERROR: {message}")


logger: LoggerProtocol = SimpleLogger()

# Try to import claude_agent, but continue if it's not available
try:
    from claude_agent import (
        AgentConfig,
        ClaudeAgent,
        quick_ask,
        quick_ask_from_hook,
    )

    CLAUDE_AGENT_AVAILABLE = True
except ImportError:
    CLAUDE_AGENT_AVAILABLE = False

    # Define stub classes for documentation purposes only
    class AgentConfig:  # type: ignore[no-redef]
        """Stub for AgentConfig when module not available."""

        def __init__(self, **kwargs: object) -> None:
            """Initialize stub config."""
            pass

    class ClaudeAgent:  # type: ignore[no-redef]
        """Stub for ClaudeAgent when module not available."""

        def __init__(self, config: AgentConfig | None = None) -> None:
            """Initialize stub agent."""
            pass

        async def __aenter__(self) -> "ClaudeAgent":
            """Async context manager entry."""
            return self

        async def __aexit__(self, *args: object) -> None:
            """Async context manager exit."""
            pass

        async def ask(self, agent_name: str, prompt: str) -> object:
            """Stub ask method."""
            raise NotImplementedError("ClaudeAgent not available")

    async def quick_ask(
        agent_name: str,
        prompt: str,
        timeout: float = 30.0,
    ) -> str:
        """Stub quick_ask function."""
        raise NotImplementedError("claude_agent module not available")

    async def quick_ask_from_hook(
        agent_name: str,
        prompt: str,
        hook_name: str,
    ) -> str:
        """Stub quick_ask_from_hook function."""
        raise NotImplementedError("claude_agent module not available")


async def example_basic_call() -> None:
    """Example: Simple agent question."""
    logger.info("\n=== Example 1: Basic Agent Call ===")

    # Simple one-off question
    config = AgentConfig(bypass_permissions=True, timeout=30.0)
    async with ClaudeAgent(config) as agent:
        response = await agent.ask("neo4j-expert", "What is a graph database?")

        logger.info(f"Response: {response.text[:200]}...")
        logger.info(f"Session ID: {response.session_id}")
        logger.info(f"Success: {response.success}")


async def example_session_continuation() -> None:
    """Example: Continue a conversation across multiple turns."""
    logger.info("\n=== Example 2: Session Continuation ===")

    config = AgentConfig(bypass_permissions=True, timeout=30.0)
    async with ClaudeAgent(config) as agent:
        # First question - creates new session
        logger.info("Turn 1: Asking about Python async...")
        response1 = await agent.ask(
            "implementer",
            "Explain Python async/await in simple terms",
        )

        logger.info(f"Response 1: {response1.text[:150]}...")
        logger.info(f"Session ID: {response1.session_id}")

        # Second question - continues the session
        logger.info("\nTurn 2: Follow-up question...")
        response2 = await agent.continue_session(
            response1.session_id,
            "Can you give me a practical example?",
        )

        logger.info(f"Response 2: {response2.text[:150]}...")
        logger.info(f"Same session: {response2.session_id == response1.session_id}")

        # Third question - another follow-up
        logger.info("\nTurn 3: Another follow-up...")
        response3 = await agent.continue_session(
            response1.session_id,
            "What about error handling?",
        )

        logger.info(f"Response 3: {response3.text[:150]}...")
        logger.info(f"Still same session: {response3.session_id == response1.session_id}")


async def example_hook_usage() -> None:
    """Example: Calling agents from hooks."""
    logger.info("\n=== Example 3: Hook Usage ===")

    # Simulate calling from a hook
    async with ClaudeAgent() as agent:
        response = await agent.ask_from_hook(
            agent_name="code-review-expert",
            prompt="Review this code: def add(a, b): return a + b",
            hook_name="PreToolUse",
        )

        logger.info(f"Hook response: {response.text[:200]}...")
        logger.info(f"Session ID: {response.session_id}")


async def example_quick_helpers() -> None:
    """Example: Using quick helper functions."""
    logger.info("\n=== Example 4: Quick Helpers ===")

    # Quick ask - simplest usage
    logger.info("Using quick_ask()...")
    text = await quick_ask(
        "memory-analyzer",
        "Search for optimization patterns",
        timeout=20.0,
    )
    logger.info(f"Response: {text[:150]}...")

    # Quick ask from hook - hook-optimized
    logger.info("\nUsing quick_ask_from_hook()...")
    text = await quick_ask_from_hook(
        "implementer",
        "Add logging to this function",
        hook_name="PostToolUse",
    )
    logger.info(f"Response: {text[:150]}...")


async def example_session_management() -> None:
    """Example: Managing sessions."""
    logger.info("\n=== Example 5: Session Management ===")

    config = AgentConfig(bypass_permissions=True)
    agent = ClaudeAgent(config)

    # Create a couple of sessions
    async with agent:
        _ = await agent.ask("neo4j-expert", "Explain indexes")
        _ = await agent.ask("implementer", "Add error handling")

    # List all sessions
    logger.info("\nListing all sessions...")
    sessions = agent.session_manager.list_sessions()
    for session in sessions:
        logger.info(
            f"  {session.session_id}: {session.agent_name} "
            f"(turns: {session.turn_count}, last used: {session.last_used})"
        )

    # List sessions for specific agent
    logger.info("\nListing neo4j-expert sessions...")
    neo4j_sessions = agent.session_manager.list_sessions(agent_name="neo4j-expert")
    for session in neo4j_sessions:
        logger.info(f"  {session.session_id}: {session.turn_count} turns")


async def example_request_logging() -> None:
    """Example: Request/response logging."""
    logger.info("\n=== Example 6: Request/Response Logging ===")

    config = AgentConfig(bypass_permissions=True)
    agent = ClaudeAgent(config)

    # Make a request
    async with agent:
        response = await agent.ask("memory-analyzer", "What patterns do you know?")
        session_id = response.session_id

    # Read the log
    logger.info(f"\nReading log for session {session_id}...")
    log_entries = agent.request_logger.read_session_log(session_id)

    for entry in log_entries:
        entry_type = entry["type"]
        data = entry["data"]
        logger.info(f"\n[{entry_type.upper()}] Turn {data['turn']}")
        if entry_type == "request":
            logger.info(f"  Prompt: {data['prompt'][:100]}...")
        else:
            logger.info(f"  Success: {data['success']}")
            logger.info(f"  Text length: {len(data['text'])} chars")


async def example_custom_config() -> None:
    """Example: Custom configuration."""
    logger.info("\n=== Example 7: Custom Configuration ===")

    # Create custom config
    config = AgentConfig(
        timeout=90.0,
        bypass_permissions=True,
        enable_hooks=False,  # Disable hooks to avoid recursion
        model="claude-sonnet-4.5",
        allowed_tools=["Read", "Grep", "Glob"],  # Restrict to specific tools
        max_turns=5,
    )

    async with ClaudeAgent(config) as agent:
        response = await agent.ask(
            "code-review-expert",
            "Review the code structure in src/",
        )

        logger.info(f"Response: {response.text[:200]}...")
        logger.info(f"Duration: {response.duration_ms}ms")
        logger.info(f"Cost: ${response.cost_usd:.4f}")


async def example_error_handling() -> None:
    """Example: Error handling."""
    logger.info("\n=== Example 8: Error Handling ===")

    config = AgentConfig(bypass_permissions=True, timeout=5.0)  # Short timeout

    async with ClaudeAgent(config) as agent:
        try:
            # This might timeout
            response = await agent.ask("implementer", "Implement a complex feature")
            logger.info(f"Success: {response.success}")
        except TimeoutError:
            logger.info("Operation timed out as expected")
        except RuntimeError as e:
            logger.info(f"Runtime error: {e}")


async def example_multi_agent_workflow() -> None:
    """Example: Multi-agent workflow with session continuation."""
    logger.info("\n=== Example 9: Multi-Agent Workflow ===")

    config = AgentConfig(bypass_permissions=True, timeout=60.0)
    async with ClaudeAgent(config) as agent:
        # Step 1: Planner creates implementation plan
        logger.info("Step 1: Planning...")
        plan_response = await agent.ask(
            "planner",
            "Create a plan to add retry logic to database connections",
        )
        logger.info(f"Plan: {plan_response.text[:150]}...")

        # Step 2: Implementer executes (could use plan from step 1 as context)
        logger.info("\nStep 2: Implementing...")
        impl_response = await agent.ask(
            "implementer",
            f"Implement this plan:\n{plan_response.text}",
        )
        logger.info(f"Implementation: {impl_response.text[:150]}...")

        # Step 3: Reviewer checks the work
        logger.info("\nStep 3: Reviewing...")
        review_response = await agent.ask(
            "code-review-expert",
            "Review the implementation that was just done",
        )
        logger.info(f"Review: {review_response.text[:150]}...")


def _print_examples_menu() -> None:
    """Print the examples menu."""
    print("\n" + "=" * 70)
    print("Claude Agent Examples")
    print("=" * 70)
    print("\nThese examples demonstrate how to use the ClaudeAgent module")
    print("with the claude-agent-sdk for various use cases.\n")

    examples = [
        ("Basic Call", "Simple agent question - one-off queries"),
        ("Session Continuation", "Continue conversations across multiple turns"),
        ("Hook Usage", "Calling agents from hooks for dynamic processing"),
        ("Quick Helpers", "Using convenient quick_ask() and quick_ask_from_hook()"),
        ("Session Management", "Managing multiple agent sessions"),
        ("Request Logging", "Logging and reviewing agent requests/responses"),
        ("Custom Config", "Configuring agents with custom settings"),
        ("Error Handling", "Handling timeouts and other errors gracefully"),
        ("Multi-Agent Workflow", "Coordinating multiple specialized agents"),
    ]

    print("Available Examples:")
    print("-" * 70)
    for i, (name, description) in enumerate(examples, 1):
        print(f"{i}. {name}")
        print(f"   -> {description}")

    print("\n" + "=" * 70)
    print("NOTE: Full examples require the ClaudeAgent module to be installed.")
    print("These are template examples showing intended usage patterns.")
    print("=" * 70 + "\n")


async def main() -> None:
    """Run all examples (display mode only)."""
    _print_examples_menu()


if __name__ == "__main__":
    asyncio.run(main())
