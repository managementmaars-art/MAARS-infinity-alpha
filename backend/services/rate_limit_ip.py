"""
Per-IP rate limiter — pre-auth defense against abuse.

Pairs with the existing per-user RPM in services/governance_service.py and the
per-key limiter in routes/v1_gateway.py (_check_rate_limit). This one runs in
middleware so it blocks before we even look at the body or auth header —
cheap, in-process, suitable for single-process deployments.

When you need multi-process / multi-host scale, swap the in-memory deque for
a Redis INCR with TTL.
"""
from __future__ import annotations

import time
from collections import deque
from threading import Lock

_DEFAULT_RPM = 300                   # per-IP ceiling per minute

_WINDOWS: dict[str, deque] = {}
_LOCK = Lock()


def check(ip: str, *, rpm: int = _DEFAULT_RPM) -> tuple[bool, int, int]:
    """
    Returns (allowed, current_count, retry_after_seconds).

    `allowed=False` means the caller exceeded `rpm` requests in the last 60s.
    """
    if not ip:
        return True, 0, 0
    now = time.time()
    cutoff = now - 60.0
    with _LOCK:
        dq = _WINDOWS.setdefault(ip, deque())
        while dq and dq[0] < cutoff:
            dq.popleft()
        if len(dq) >= rpm:
            retry = int(60 - (now - dq[0])) + 1
            return False, len(dq), max(retry, 1)
        dq.append(now)
        return True, len(dq), 0


def reset(ip: str) -> None:
    """Drop an IP's window — used by tests."""
    with _LOCK:
        _WINDOWS.pop(ip, None)


def reset_all() -> None:
    with _LOCK:
        _WINDOWS.clear()
