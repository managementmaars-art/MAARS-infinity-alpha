#!/usr/bin/env python3
"""Verify Claude Agent SDK installation and configuration.

Usage:
    python verify_sdk.py [--verbose]

Checks:
- Python version compatibility (3.12+)
- SDK installation
- Claude CLI availability
- Environment variables
- Basic query functionality
"""

from __future__ import annotations

import asyncio
import os
import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable, Coroutine
    from typing import Any

# Setup: Add .claude to path for skill_utils
_claude_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(_claude_root))

from skill_utils import ensure_path_setup  # noqa: E402

ensure_path_setup()

# Minimum supported Python version for this project
MIN_PYTHON_VERSION: tuple[int, int] = (3, 12)


def check_python_version() -> tuple[bool, str]:
    """Check if Python version is compatible.

    Returns:
        Tuple of (success, message) indicating version compatibility.
    """
    version = sys.version_info
    if version >= MIN_PYTHON_VERSION:
        return True, f"[OK] Python {version.major}.{version.minor}.{version.micro}"
    return (
        False,
        f"[FAIL] Python {version.major}.{version.minor} "
        f"(requires {MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]}+)",
    )


def check_sdk_installation() -> tuple[bool, str]:
    """Check if Claude Agent SDK is installed.

    Returns:
        Tuple of (success, message) indicating SDK availability.
    """
    try:
        import claude_agent_sdk

        version = getattr(claude_agent_sdk, "__version__", "unknown")
        return True, f"[OK] claude-agent-sdk {version}"
    except ImportError:
        return False, "[FAIL] claude-agent-sdk not installed"


def check_claude_cli() -> tuple[bool, str]:
    """Check if Claude CLI is available.

    Returns:
        Tuple of (success, message) indicating CLI availability.
    """
    try:
        result = subprocess.run(
            ["claude-code", "--version"],
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            version = result.stdout.strip()
            return True, f"[OK] Claude CLI installed ({version})"
        return False, "[FAIL] Claude CLI not responding"
    except FileNotFoundError:
        return False, "[FAIL] Claude CLI not found (install with: npm install -g claude-code)"
    except subprocess.TimeoutExpired:
        return False, "[FAIL] Claude CLI timed out"
    except OSError as e:
        return False, f"[FAIL] Claude CLI error: {e}"


def check_environment() -> tuple[bool, str]:
    """Check environment variables for authentication.

    Returns:
        Tuple of (success, message) indicating authentication status.
    """
    checks: list[str] = []

    # Check for API key
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if api_key:
        # Safely mask the API key
        if len(api_key) > 12:
            masked = api_key[:8] + "..." + api_key[-4:]
        else:
            masked = "***"
        checks.append(f"[OK] ANTHROPIC_API_KEY set ({masked})")
    # Check for alternative auth methods
    elif os.environ.get("CLAUDE_CODE_USE_BEDROCK"):
        checks.append("[OK] Bedrock authentication configured")
    elif os.environ.get("CLAUDE_CODE_USE_VERTEX"):
        checks.append("[OK] Vertex AI authentication configured")
    else:
        checks.append("[WARN] No authentication configured (set ANTHROPIC_API_KEY)")

    return len(checks) > 0, "\n  ".join(checks)


async def check_basic_query() -> tuple[bool, str]:
    """Test basic query functionality with Claude Agent SDK.

    Returns:
        Tuple of (success, message) indicating query test result.
    """
    try:
        from claude_agent_sdk import ClaudeAgentOptions, query

        # Simple test query with 1 turn limit
        message_count = 0
        async for _message in query(
            prompt="Say 'test successful'",
            options=ClaudeAgentOptions(max_turns=1),
        ):
            message_count += 1

        if message_count > 0:
            return True, f"[OK] Basic query works ({message_count} messages)"
        return False, "[FAIL] Query returned no messages"

    except ImportError as e:
        return False, f"[FAIL] Import error: {e}"
    except TimeoutError:
        return False, "[FAIL] Query timed out"
    except RuntimeError as e:
        return False, f"[FAIL] Query failed: {e}"


# Type alias for check functions
type CheckFunc = Callable[[], tuple[bool, str]]
type AsyncCheckFunc = Callable[[], Coroutine[Any, Any, tuple[bool, str]]]


async def main() -> int:
    """Run all verification checks.

    Returns:
        Exit code: 0 for success, 1 for any failures.
    """
    print("=" * 60)
    print("Claude Agent SDK Verification")
    print("=" * 60)

    checks: list[tuple[str, CheckFunc | AsyncCheckFunc]] = [
        ("Python Version", check_python_version),
        ("SDK Installation", check_sdk_installation),
        ("Claude CLI", check_claude_cli),
        ("Environment", check_environment),
    ]

    results: list[bool] = []
    for name, check_func in checks:
        if asyncio.iscoroutinefunction(check_func):
            success, message = await check_func()
        else:
            # Sync function - call directly
            sync_func: CheckFunc = check_func  # type: ignore[assignment]
            success, message = sync_func()

        results.append(success)
        print(f"\n{name}:")
        print(f"  {message}")

    # Optional: Test basic query if everything else passes
    if all(results):
        print("\nBasic Query Test:")
        success, message = await check_basic_query()
        results.append(success)
        print(f"  {message}")

    # Summary
    passed = sum(results)
    total = len(results)
    print("\n" + "=" * 60)
    print(f"Summary: {passed}/{total} checks passed")
    print("=" * 60)

    return 0 if all(results) else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
