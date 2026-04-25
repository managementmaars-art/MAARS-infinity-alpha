"""Proactive rate-limit tracking — parse the headers every provider returns.

Every major LLM API tells you (a) your remaining budget and (b) when it
resets. Reading those headers lets us:

  1. Avoid sending a request that's guaranteed to 429.
  2. Load-balance between providers by remaining capacity, not guesswork.
  3. Back off BEFORE we trip the limit, which preserves burst capacity.

Providers we handle:
  OpenAI     : x-ratelimit-remaining-requests, x-ratelimit-remaining-tokens,
               x-ratelimit-reset-requests, x-ratelimit-reset-tokens
  Anthropic  : anthropic-ratelimit-requests-remaining,
               anthropic-ratelimit-tokens-remaining,
               anthropic-ratelimit-requests-reset (ISO-8601 UTC),
               anthropic-ratelimit-tokens-reset
  Groq       : same shape as OpenAI
  Cerebras   : same shape as OpenAI
  Gemini     : no headers; rely on 429 backoff
  Cohere     : X-RateLimit-Remaining / X-RateLimit-Reset

State is in-process per provider+key-prefix. Each call updates the view;
callers can consult `budget_ok(provider)` before dispatching.
"""
from __future__ import annotations
import logging
import time
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class _RLView:
    requests_remaining: int | None = None
    tokens_remaining: int | None = None
    requests_reset_ts: float = 0.0
    tokens_reset_ts: float = 0.0
    last_updated: float = 0.0


_views: dict[str, _RLView] = {}


def _parse_reset(value: str) -> float:
    """Providers send reset as either '2s' / '1m30s' (OpenAI) or an
    ISO-8601 timestamp (Anthropic). Normalize to a Unix timestamp."""
    if not value:
        return 0.0
    now = time.time()
    v = value.strip()
    # ISO-8601 path
    if "T" in v and "Z" in v:
        try:
            from datetime import datetime, timezone
            return datetime.fromisoformat(v.replace("Z", "+00:00")).timestamp()
        except Exception:
            return now + 60
    # duration form: combine #h/#m/#s
    total = 0.0
    buf = ""
    for ch in v:
        if ch.isdigit() or ch == ".":
            buf += ch
        elif ch in ("h", "m", "s", "d"):
            try:
                n = float(buf)
            except ValueError:
                n = 0.0
            total += n * {"d": 86400, "h": 3600, "m": 60, "s": 1}[ch]
            buf = ""
        elif ch.isspace():
            continue
        else:
            # unknown suffix → assume it's plain seconds
            try:
                return now + float(v)
            except ValueError:
                return now + 60
    return now + total if total else now + 60


def update_from_response(provider: str, headers) -> None:
    """Pull rate-limit info out of a provider response's headers dict."""
    if not headers:
        return
    # headers might be a dict or httpx.Headers — normalize to lowercase keys
    h = {k.lower(): v for k, v in dict(headers).items()}
    v = _views.setdefault(provider, _RLView())
    v.last_updated = time.time()

    rr = (h.get("x-ratelimit-remaining-requests")
          or h.get("anthropic-ratelimit-requests-remaining")
          or h.get("x-ratelimit-remaining"))
    tr = (h.get("x-ratelimit-remaining-tokens")
          or h.get("anthropic-ratelimit-tokens-remaining"))
    rreset = (h.get("x-ratelimit-reset-requests")
              or h.get("anthropic-ratelimit-requests-reset")
              or h.get("x-ratelimit-reset"))
    treset = (h.get("x-ratelimit-reset-tokens")
              or h.get("anthropic-ratelimit-tokens-reset"))

    try:
        if rr is not None:
            v.requests_remaining = int(float(rr))
    except (TypeError, ValueError):
        pass
    try:
        if tr is not None:
            v.tokens_remaining = int(float(tr))
    except (TypeError, ValueError):
        pass
    if rreset:
        v.requests_reset_ts = _parse_reset(str(rreset))
    if treset:
        v.tokens_reset_ts = _parse_reset(str(treset))


def budget_ok(provider: str, *, required_tokens: int = 0) -> tuple[bool, str]:
    """Return (ok, reason). If ok=False, reason describes why.

    Conservative: treat 'unknown' as ok (no headers yet = no signal).
    """
    v = _views.get(provider)
    if v is None or v.last_updated == 0:
        return True, "no_signal"
    now = time.time()
    if v.requests_remaining is not None and v.requests_remaining <= 0:
        if v.requests_reset_ts > now:
            return False, f"no_requests_budget; resets in {int(v.requests_reset_ts - now)}s"
    if v.tokens_remaining is not None and required_tokens > 0 and v.tokens_remaining < required_tokens:
        if v.tokens_reset_ts > now:
            return False, f"tokens_budget {v.tokens_remaining} < {required_tokens}; resets in {int(v.tokens_reset_ts - now)}s"
    return True, "ok"


def snapshot() -> dict[str, dict]:
    now = time.time()
    return {
        p: {
            "requests_remaining": v.requests_remaining,
            "tokens_remaining": v.tokens_remaining,
            "requests_reset_in": max(0, int(v.requests_reset_ts - now)) if v.requests_reset_ts else None,
            "tokens_reset_in": max(0, int(v.tokens_reset_ts - now)) if v.tokens_reset_ts else None,
            "last_updated_sec_ago": int(now - v.last_updated),
        }
        for p, v in _views.items()
    }
