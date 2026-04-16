#!/usr/bin/env python3
"""Example Hook Integration with ClaudeAgent.

This demonstrates how to use claude_agent.py from hooks to call specialized agents.
The agent can help with tasks like:
- Code review before commits
- Automatic documentation
- Error analysis and suggestions
- Context-aware assistance

Hook Types Supported:
- PreToolUse: Before tool execution (validate, analyze, suggest)
- PostToolUse: After tool execution (review, document, optimize)
- UserPromptSubmit: When user submits prompt (enhance, clarify, route)
- SessionStart: At session beginning (setup, configure, prepare)
- SessionEnd: At session end (summarize, analyze, report)

Requires: claude_agent module from tools/agents/
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
from collections.abc import Callable, Coroutine
from pathlib import Path
from typing import Any, Protocol

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

    def error(self, message: str) -> None:
        """Log error message."""
        ...

    def warning(self, message: str) -> None:
        """Log warning message."""
        ...

    def exception(self, message: str) -> None:
        """Log exception message."""
        ...


class SimpleLogger:
    """Simple logger for examples when full logging not available."""

    def info(self, message: str) -> None:
        """Print info message."""
        print(message)

    def error(self, message: str) -> None:
        """Print error message."""
        print(f"ERROR: {message}")

    def warning(self, message: str) -> None:
        """Print warning message."""
        print(f"WARNING: {message}")

    def exception(self, message: str) -> None:
        """Print exception message."""
        print(f"EXCEPTION: {message}")


logger: LoggerProtocol = SimpleLogger()

# Try to import claude_agent, but continue if it's not available
try:
    from claude_agent import ClaudeAgent, quick_ask_from_hook

    CLAUDE_AGENT_AVAILABLE = True
except ImportError:
    CLAUDE_AGENT_AVAILABLE = False

    # Define stub classes for documentation purposes only
    class ClaudeAgent:  # type: ignore[no-redef]
        """Stub for ClaudeAgent when module not available."""

        def __init__(self, config: Any | None = None) -> None:
            """Initialize stub agent."""
            pass

        async def __aenter__(self) -> "ClaudeAgent":
            """Async context manager entry."""
            return self

        async def __aexit__(self, *args: object) -> None:
            """Async context manager exit."""
            pass

        async def ask_from_hook(
            self,
            agent_name: str,
            prompt: str,
            hook_name: str,
        ) -> Any:
            """Stub ask_from_hook method."""
            raise NotImplementedError("ClaudeAgent not available")

        async def continue_session(self, session_id: str, prompt: str) -> Any:
            """Stub continue_session method."""
            raise NotImplementedError("ClaudeAgent not available")

    async def quick_ask_from_hook(
        agent_name: str,
        prompt: str,
        hook_name: str,
    ) -> str:
        """Stub quick_ask_from_hook function."""
        raise NotImplementedError("claude_agent module not available")


# Type alias for hook input/output
type HookInput = dict[str, Any]
type HookOutput = dict[str, Any]


# ========== Hook Examples ==========


async def pre_tool_use_hook_example(hook_input: HookInput) -> HookOutput:
    """Example PreToolUse hook that validates tool usage with an agent.

    This hook:
    1. Intercepts tool calls before execution
    2. Asks a code-review agent to validate the operation
    3. Can block dangerous operations
    4. Logs recommendations

    Args:
        hook_input: Hook input data with tool_name, parameters, etc.

    Returns:
        Hook output (empty dict = allow, {"decision": "block"} = block).
    """
    tool_name = hook_input.get("tool_name", "unknown")
    logger.info(f"PreToolUse hook triggered for: {tool_name}")

    # Example: Validate Write operations
    if tool_name == "Write":
        file_path = hook_input.get("parameters", {}).get("file_path", "")
        content = hook_input.get("parameters", {}).get("content", "")

        # Ask agent to review the code being written
        try:
            response = await quick_ask_from_hook(
                agent_name="code-review-expert",
                prompt=f"Quick review of code being written to {file_path}:\n\n{content[:500]}",
                hook_name="PreToolUse",
            )

            logger.info(f"Agent review: {response[:200]}...")

            # Could add logic here to block based on agent response
            # For now, just log
            return {}

        except NotImplementedError:
            logger.warning("claude_agent module not available")
            return {}
        except RuntimeError as e:
            logger.exception(f"Failed to get agent review: {e}")
            return {}

    return {}


async def post_tool_use_hook_example(hook_input: HookInput) -> HookOutput:
    """Example PostToolUse hook that logs tool results to an agent.

    This hook:
    1. Captures tool results after execution
    2. Asks an agent to analyze the results
    3. Stores learnings for future sessions
    4. Provides recommendations

    Args:
        hook_input: Hook input data with tool results.

    Returns:
        Hook output (logging only).
    """
    tool_name = hook_input.get("tool_name", "unknown")
    result = hook_input.get("result", {})

    logger.info(f"PostToolUse hook triggered for: {tool_name}")

    # Example: Analyze test failures
    command = hook_input.get("parameters", {}).get("command", "")
    if tool_name == "Bash" and "pytest" in command:
        result_text = result.get("output", "")

        if "FAILED" in result_text or "ERROR" in result_text:
            try:
                # Ask agent to analyze test failures
                response = await quick_ask_from_hook(
                    agent_name="debugging-expert",
                    prompt=f"Analyze this test failure:\n\n{result_text[:1000]}",
                    hook_name="PostToolUse",
                )

                logger.info(f"Agent analysis: {response[:200]}...")

                # Could store this in memory for future reference
                # await store_test_failure_analysis(response)

            except NotImplementedError:
                logger.warning("claude_agent module not available")
            except RuntimeError as e:
                logger.exception(f"Failed to get agent analysis: {e}")

    return {}


async def user_prompt_submit_hook_example(hook_input: HookInput) -> HookOutput:
    """Example UserPromptSubmit hook that enhances user prompts with agent assistance.

    This hook:
    1. Intercepts user prompts before processing
    2. Can enhance or clarify ambiguous requests
    3. Routes to appropriate specialized agents
    4. Adds context from previous sessions

    Args:
        hook_input: Hook input with user's prompt.

    Returns:
        Hook output (could modify prompt, but we just log).
    """
    prompt = hook_input.get("prompt", "")
    logger.info("UserPromptSubmit hook triggered")

    # Example: Detect if user is asking for help with architecture
    architecture_keywords = ["architecture", "design", "pattern"]
    if any(keyword in prompt.lower() for keyword in architecture_keywords):
        try:
            # Ask architecture-guardian for context
            context_response = await quick_ask_from_hook(
                agent_name="architecture-guardian",
                prompt=(
                    f"User is asking about: {prompt[:200]}. "
                    "What architectural principles should guide the response?"
                ),
                hook_name="UserPromptSubmit",
            )

            logger.info(f"Architecture context: {context_response[:200]}...")

            # Could inject this context into the conversation
            # For now, just log it

        except NotImplementedError:
            logger.warning("claude_agent module not available")
        except RuntimeError as e:
            logger.exception(f"Failed to get architectural context: {e}")

    return {}


async def session_start_hook_example(hook_input: HookInput) -> HookOutput:
    """Example SessionStart hook that prepares agent sessions.

    This hook:
    1. Runs at session startup
    2. Can load relevant context from previous sessions
    3. Prepares specialized agents
    4. Sets up logging and monitoring

    Args:
        hook_input: Hook input with session info.

    Returns:
        Hook output with session metadata.
    """
    session_id = hook_input.get("session_id", "unknown")
    logger.info(f"SessionStart hook triggered for session: {session_id}")

    try:
        # Ask memory-analyzer for relevant context
        context_response = await quick_ask_from_hook(
            agent_name="memory-analyzer",
            prompt="What were the key issues from recent sessions?",
            hook_name="SessionStart",
        )

        logger.info(f"Session context: {context_response[:200]}...")

        # Return metadata that could be used by the session
        return {"context_loaded": True, "session_context": context_response[:500]}

    except NotImplementedError:
        logger.warning("claude_agent module not available")
        return {}
    except RuntimeError as e:
        logger.exception(f"Failed to load session context: {e}")
        return {}


async def session_end_hook_example(hook_input: HookInput) -> HookOutput:
    """Example SessionEnd hook that analyzes and stores session learnings.

    This hook:
    1. Runs at session completion
    2. Analyzes what was accomplished
    3. Extracts learnings and patterns
    4. Stores insights for future sessions

    Args:
        hook_input: Hook input with session summary.

    Returns:
        Hook output with analysis results.
    """
    session_id = hook_input.get("session_id", "unknown")
    logger.info(f"SessionEnd hook triggered for session: {session_id}")

    # Get session summary from hook input
    summary = hook_input.get("summary", "")

    try:
        # Ask memory-analyzer to extract and store learnings
        analysis_response = await quick_ask_from_hook(
            agent_name="memory-analyzer",
            prompt=f"Analyze this session and extract key learnings:\n\n{summary[:1000]}",
            hook_name="SessionEnd",
        )

        logger.info(f"Session analysis: {analysis_response[:200]}...")

        return {"analysis_complete": True, "learnings_stored": True}

    except NotImplementedError:
        logger.warning("claude_agent module not available")
        return {}
    except RuntimeError as e:
        logger.exception(f"Failed to analyze session: {e}")
        return {}


# ========== Advanced Examples ==========


async def code_review_workflow_example() -> None:
    """Example: Multi-step code review workflow using agents."""
    logger.info("\n=== Code Review Workflow Example ===")

    # Simulated hook input
    file_path = "src/services/example.py"
    code_content = """
def process_data(data):
    result = []
    for item in data:
        if item > 0:
            result.append(item * 2)
    return result
"""

    async with ClaudeAgent() as agent:
        # Step 1: Code quality review
        logger.info("Step 1: Code quality review...")
        quality_response = await agent.ask_from_hook(
            agent_name="code-review-expert",
            prompt=f"Review code quality for {file_path}:\n{code_content}",
            hook_name="PreCommit",
        )
        logger.info(f"Quality: {quality_response.text[:150]}...")

        # Step 2: Architecture validation
        logger.info("\nStep 2: Architecture validation...")
        arch_response = await agent.ask_from_hook(
            agent_name="architecture-guardian",
            prompt=f"Validate architecture compliance for:\n{code_content}",
            hook_name="PreCommit",
        )
        logger.info(f"Architecture: {arch_response.text[:150]}...")

        # Step 3: Security check
        logger.info("\nStep 3: Security check...")
        security_response = await agent.ask_from_hook(
            agent_name="code-review-expert",
            prompt=f"Check for security issues in:\n{code_content}",
            hook_name="PreCommit",
        )
        logger.info(f"Security: {security_response.text[:150]}...")


async def error_recovery_workflow_example() -> None:
    """Example: Error recovery workflow with agent assistance."""
    logger.info("\n=== Error Recovery Workflow Example ===")

    # Simulated error from a test run
    error_output = """
FAILED tests/unit/test_example.py::test_process_data - AssertionError: assert [] == [2, 4, 6]
E       assert [] == [2, 4, 6]
E        +  where [] = process_data([1, 2, 3])
"""

    async with ClaudeAgent() as agent:
        # Step 1: Analyze the error
        logger.info("Step 1: Analyzing error...")
        analysis = await agent.ask_from_hook(
            agent_name="debugging-expert",
            prompt=f"Analyze this test failure:\n{error_output}",
            hook_name="PostToolUse",
        )
        logger.info(f"Analysis: {analysis.text[:150]}...")

        # Step 2: Get fix suggestions
        logger.info("\nStep 2: Getting fix suggestions...")
        fix_suggestions = await agent.continue_session(
            session_id=analysis.session_id,
            prompt="What are the steps to fix this?",
        )
        logger.info(f"Suggestions: {fix_suggestions.text[:150]}...")

        # Step 3: Verify the fix approach
        logger.info("\nStep 3: Verifying fix approach...")
        verification = await agent.continue_session(
            session_id=analysis.session_id,
            prompt="Is this fix approach safe and follows best practices?",
        )
        logger.info(f"Verification: {verification.text[:150]}...")


# ========== Hook Entrypoint ==========

# Handler type alias
type HookHandler = Callable[[HookInput], Coroutine[Any, Any, HookOutput]]


async def hook_main() -> None:
    """Main entrypoint for hook execution.

    This demonstrates how to call the appropriate hook handler based on
    the HOOK_EVENT_NAME environment variable.
    """
    hook_event = os.environ.get("HOOK_EVENT_NAME", "")
    logger.info(f"Hook event: {hook_event}")

    if not hook_event:
        logger.error("No HOOK_EVENT_NAME environment variable found")
        return

    # Read hook input from stdin (Claude passes this)
    try:
        hook_input: HookInput = json.loads(sys.stdin.read())
    except json.JSONDecodeError as e:
        logger.exception(f"Failed to parse hook input: {e}")
        return
    except OSError as e:
        logger.exception(f"Failed to read stdin: {e}")
        return

    # Route to appropriate handler
    handlers: dict[str, HookHandler] = {
        "PreToolUse": pre_tool_use_hook_example,
        "PostToolUse": post_tool_use_hook_example,
        "UserPromptSubmit": user_prompt_submit_hook_example,
        "SessionStart": session_start_hook_example,
        "SessionEnd": session_end_hook_example,
    }

    handler = handlers.get(hook_event)
    if handler:
        result = await handler(hook_input)
        # Output result as JSON
        print(json.dumps(result))
    else:
        logger.warning(f"No handler for hook event: {hook_event}")


def _print_demo_menu() -> None:
    """Print the demo mode menu."""
    print("\n" + "=" * 70)
    print("Claude Agent Hook Integration Examples")
    print("=" * 70)
    print("\nThis module demonstrates how to integrate claude_agent with hooks")
    print("for autonomous agent assistance in Claude Code workflows.\n")

    print("Hook Types Supported:")
    print("-" * 70)
    hooks = [
        ("PreToolUse", "Validate and analyze tool calls before execution"),
        ("PostToolUse", "Review and learn from tool results after execution"),
        ("UserPromptSubmit", "Enhance user prompts with context and suggestions"),
        ("SessionStart", "Prepare agents and load context at session startup"),
        ("SessionEnd", "Analyze and store learnings at session completion"),
    ]

    for hook_name, description in hooks:
        print(f"  {hook_name:<20} -> {description}")

    print("\n" + "=" * 70)
    print("Example Workflows:")
    print("-" * 70)
    workflows = [
        ("Code Review", "Multi-step code quality, architecture, and security checks"),
        ("Error Recovery", "Analyze test failures and suggest fixes"),
    ]

    for workflow, description in workflows:
        print(f"  {workflow:<20} -> {description}")

    print("\n" + "=" * 70)
    print("NOTE: Full examples require the ClaudeAgent module to be installed.")
    print("These are template examples showing intended hook integration patterns.")
    print("=" * 70 + "\n")


async def demo_main() -> None:
    """Demo mode - run examples without hook environment."""
    _print_demo_menu()


if __name__ == "__main__":
    # Check if running as a hook or in demo mode
    if os.environ.get("HOOK_EVENT_NAME"):
        # Running as a hook
        asyncio.run(hook_main())
    else:
        # Running in demo mode
        asyncio.run(demo_main())
