"""
Code executor tool — run untrusted Python in a subprocess with timeout + output caps.

This is a minimal sandbox suitable for arithmetic, string manipulation, and data
shaping. It is NOT a production sandbox — untrusted network / file IO is still
possible. Treat as a convenience for agent-driven computation, not as a security
boundary.
"""
from __future__ import annotations

import asyncio
import sys
import time
from typing import Any

from .base import Tool, ToolResult

_MAX_OUTPUT_BYTES = 64 * 1024   # 64 KiB
_MAX_CODE_BYTES = 8 * 1024      # 8 KiB


class CodeExecutorTool(Tool):
    name = "code_executor"
    description = "Execute a short Python snippet in a subprocess and return stdout."
    argument_schema = {
        "type": "object",
        "required": ["code"],
        "properties": {
            "code":    {"type": "string", "description": "Python source to execute"},
            "stdin":   {"type": "string", "default": ""},
            "timeout": {"type": "number", "default": 5.0, "minimum": 0.1, "maximum": 15.0},
        },
    }
    credit_cost = 2
    timeout_seconds = 15.0

    async def run(self, args: dict[str, Any]) -> ToolResult:
        code = args.get("code") or ""
        if not code.strip():
            return ToolResult(ok=False, error="code is required")
        if len(code.encode("utf-8")) > _MAX_CODE_BYTES:
            return ToolResult(ok=False, error=f"code exceeds {_MAX_CODE_BYTES} bytes")

        timeout = float(min(args.get("timeout", 5.0), self.timeout_seconds))
        stdin_bytes = (args.get("stdin") or "").encode("utf-8")

        t0 = time.time()
        try:
            proc = await asyncio.create_subprocess_exec(
                sys.executable, "-I", "-B", "-S", "-c", code,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            try:
                stdout, stderr = await asyncio.wait_for(proc.communicate(stdin_bytes), timeout)
            except asyncio.TimeoutError:
                proc.kill()
                await proc.wait()
                return ToolResult(ok=False, error=f"timeout after {timeout}s",
                                  latency_ms=int((time.time() - t0) * 1000))
        except NotImplementedError:
            # Windows SelectorEventLoop can't spawn subprocesses — signal to the caller.
            return ToolResult(ok=False, error="subprocess not available on this event loop")
        except Exception as exc:
            return ToolResult(ok=False, error=f"{type(exc).__name__}: {exc}",
                              latency_ms=int((time.time() - t0) * 1000))

        return ToolResult(
            ok=(proc.returncode == 0),
            data={
                "stdout": stdout[:_MAX_OUTPUT_BYTES].decode("utf-8", errors="replace"),
                "stderr": stderr[:_MAX_OUTPUT_BYTES].decode("utf-8", errors="replace"),
                "return_code": proc.returncode,
            },
            latency_ms=int((time.time() - t0) * 1000),
            metadata={"timeout_seconds": timeout},
        )
