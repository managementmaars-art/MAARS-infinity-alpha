"""Single-flight request coalescing — the Groupcache pattern.

When N in-flight callers ask for the same thing at the same moment, only
one of them should actually hit the backend. The others wait on the same
future and get the same answer.

Classic scenario for us: a landing-page embed suddenly gets a spike and
20 visitors each trigger "generate a quick intro email for hello@x.com".
Without coalescing we fire 20 provider calls; with coalescing we fire
one and all 20 get served the same response. Same cost for 20× the
throughput.

We only coalesce deterministic calls (temperature ≈ 0 + no tools) since
we're going to hand the same bytes to multiple callers. If the request
is stochastic, every caller gets its own async task.

Keyed by: sha256(model, normalized-messages, temperature, max_tokens).
"""
from __future__ import annotations
import asyncio
import hashlib
import json
import logging
from typing import Any, Awaitable, Callable, Optional

logger = logging.getLogger(__name__)

_inflight: dict[str, asyncio.Future] = {}


def _key(model: str, messages: list[dict], temperature: Optional[float], max_tokens: Optional[int]) -> str:
    normalized = [{"r": m.get("role"), "c": " ".join(str(m.get("content") or "").split()).lower()} for m in messages or []]
    blob = json.dumps(
        {"m": model, "t": temperature, "x": max_tokens, "p": normalized},
        sort_keys=True,
    ).encode()
    return hashlib.sha256(blob).hexdigest()


def is_coalescible(*, temperature: Optional[float], has_tools: bool, stream: bool) -> bool:
    if stream or has_tools:
        return False
    if temperature is not None and temperature > 0.1:
        return False
    return True


async def coalesce(
    *,
    model: str,
    messages: list[dict],
    temperature: Optional[float],
    max_tokens: Optional[int],
    producer: Callable[[], Awaitable[Any]],
    has_tools: bool = False,
    stream: bool = False,
) -> tuple[Any, bool]:
    """Return (result, was_shared). If was_shared=True, we piggybacked on
    an already-running call."""
    if not is_coalescible(temperature=temperature, has_tools=has_tools, stream=stream):
        return await producer(), False
    k = _key(model, messages, temperature, max_tokens)
    fut = _inflight.get(k)
    if fut is not None and not fut.done():
        try:
            return await fut, True
        except Exception:
            # Primary flight failed — fall through and try again ourselves.
            pass
    loop = asyncio.get_event_loop()
    fut = loop.create_future()
    _inflight[k] = fut
    try:
        result = await producer()
        if not fut.done():
            fut.set_result(result)
        return result, False
    except Exception as exc:
        if not fut.done():
            fut.set_exception(exc)
        raise
    finally:
        # Clear the map AFTER we've set the result so waiters don't race
        # ahead of the resolution. We guard against double-pop via .get.
        if _inflight.get(k) is fut:
            _inflight.pop(k, None)


def inflight_count() -> int:
    return sum(1 for f in _inflight.values() if not f.done())
