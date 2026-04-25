"""Tool base class — all agent-callable tools inherit from `Tool`."""
from __future__ import annotations

import abc
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ToolResult:
    ok: bool
    data: Any = None
    error: str = ""
    latency_ms: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


class Tool(abc.ABC):
    name: str = ""
    description: str = ""
    argument_schema: dict[str, Any] = {}          # JSON Schema for args
    credit_cost: int = 1                          # credits to debit per call
    timeout_seconds: float = 15.0

    @abc.abstractmethod
    async def run(self, args: dict[str, Any]) -> ToolResult:
        """Execute the tool. MUST NOT raise — catch and convert to ToolResult(ok=False)."""

    def spec(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "arguments": self.argument_schema,
            "credit_cost": self.credit_cost,
            "timeout_seconds": self.timeout_seconds,
        }
