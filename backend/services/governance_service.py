"""
Runtime governance — per-request policy enforcement.

Checks every inference request against:
    * max_credits_per_request      (wallet protection)
    * max_input_tokens             (prompt size)
    * max_output_tokens            (max_tokens param cap)
    * rate_limit_rpm               (per user, sliding window)
    * safety: deny-list keywords

Returns a GovernanceDecision — `allow=True` or the structured reason for block.
Callers (v1_gateway) can surface the reason to the user as a 4xx error.

This is a thin service. It sits alongside the existing checks in
backend/governance/* (circuit_breaker, budget, policy, recovery) — not a
replacement.
"""
from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass, field
from threading import Lock
from typing import Any, Iterable, Optional

# --------------------------------------------------------------------------- defaults

DEFAULT_LIMITS = {
    "max_credits_per_request":  1000,
    "max_input_tokens":       200_000,
    "max_output_tokens":       32_000,
    "rate_limit_rpm":              60,
    "deny_keywords": [
        # Conservative defaults — extend via env/admin config.
        "CREATE MALWARE",
        "CHILD SEXUAL ABUSE",
    ],
}

# --------------------------------------------------------------------------- per-user RPM (in-process; fine for single-process dev, replace with Redis for prod scale)

_RPM_WINDOWS: dict[str, deque] = {}
_RPM_LOCK = Lock()


def _rpm_hit(user_id: str, limit: int) -> tuple[bool, int, int]:
    """True when within limit. Returns (allowed, current_count, retry_in_seconds)."""
    now = time.time()
    cutoff = now - 60.0
    with _RPM_LOCK:
        dq = _RPM_WINDOWS.setdefault(user_id, deque())
        while dq and dq[0] < cutoff:
            dq.popleft()
        if len(dq) >= limit:
            retry = int(60 - (now - dq[0])) + 1
            return False, len(dq), max(retry, 1)
        dq.append(now)
        return True, len(dq), 0


# --------------------------------------------------------------------------- decision shape

@dataclass
class GovernanceDecision:
    allow: bool
    reason: str = ""
    code: str = "allowed"
    retry_after_seconds: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "allow": self.allow,
            "reason": self.reason,
            "code": self.code,
            "retry_after_seconds": self.retry_after_seconds,
            "metadata": self.metadata,
        }


# --------------------------------------------------------------------------- checks

def _estimate_prompt_tokens(messages: Iterable[dict[str, Any]]) -> int:
    total = 0
    for m in messages:
        content = m.get("content")
        if isinstance(content, str):
            total += int(len(content.split()) * 1.3)
        elif isinstance(content, list):
            for part in content:
                if isinstance(part, dict) and isinstance(part.get("text"), str):
                    total += int(len(part["text"].split()) * 1.3)
    return total


def _contains_deny_keyword(messages: Iterable[dict[str, Any]], deny: list[str]) -> Optional[str]:
    if not deny:
        return None
    joined = " ".join(
        (m.get("content") if isinstance(m.get("content"), str) else "")
        for m in messages
    ).upper()
    for needle in deny:
        if needle.upper() in joined:
            return needle
    return None


def check_request(
    *,
    user_id: str,
    messages: list[dict[str, Any]],
    requested_max_tokens: Optional[int] = None,
    estimated_credits: int = 0,
    limits: Optional[dict[str, Any]] = None,
) -> GovernanceDecision:
    """
    Evaluate a single inference request against governance policy. Fast and
    in-process — callers run this before any provider call.
    """
    L = {**DEFAULT_LIMITS, **(limits or {})}

    if estimated_credits > L["max_credits_per_request"]:
        return GovernanceDecision(
            allow=False,
            code="credits_cap_exceeded",
            reason=f"Request would charge {estimated_credits} credits (cap is {L['max_credits_per_request']}).",
            metadata={"estimated_credits": estimated_credits, "cap": L["max_credits_per_request"]},
        )

    input_tokens = _estimate_prompt_tokens(messages)
    if input_tokens > L["max_input_tokens"]:
        return GovernanceDecision(
            allow=False,
            code="prompt_too_large",
            reason=f"Prompt is ~{input_tokens:,} tokens; cap is {L['max_input_tokens']:,}.",
            metadata={"estimated_input_tokens": input_tokens, "cap": L["max_input_tokens"]},
        )

    if requested_max_tokens is not None and requested_max_tokens > L["max_output_tokens"]:
        return GovernanceDecision(
            allow=False,
            code="output_too_large",
            reason=f"max_tokens={requested_max_tokens} exceeds cap {L['max_output_tokens']:,}.",
            metadata={"requested_max_tokens": requested_max_tokens, "cap": L["max_output_tokens"]},
        )

    hit = _contains_deny_keyword(messages, L.get("deny_keywords") or [])
    if hit:
        return GovernanceDecision(
            allow=False,
            code="safety_violation",
            reason="Request contains disallowed content.",
            metadata={"matched_rule": hit[:80]},
        )

    allowed, count, retry = _rpm_hit(user_id, int(L["rate_limit_rpm"]))
    if not allowed:
        return GovernanceDecision(
            allow=False,
            code="rate_limited",
            reason=f"Rate limit of {L['rate_limit_rpm']} requests/min exceeded.",
            retry_after_seconds=retry,
            metadata={"current_count": count, "rpm_limit": L["rate_limit_rpm"]},
        )

    return GovernanceDecision(
        allow=True, code="allowed",
        metadata={"estimated_input_tokens": input_tokens, "rpm_count": count},
    )
