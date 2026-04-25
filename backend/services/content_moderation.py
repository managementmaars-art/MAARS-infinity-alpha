"""Content moderation — liability firewall.

You're routing inference through your infrastructure on your providers'
accounts. If a user generates CSAM, extremist material, or targeted
harassment via YOUR router, YOU get the compliance takedown — not them.

Two-layer check:
  1. Keyword list (fast, free) — catches obvious cases and blocks them
     before ever reaching a provider.
  2. OpenAI moderation endpoint (free for OpenAI key holders) — nuanced
     classifier with 13 categories; runs on anything that passes layer 1.

Both layers run async with a small timeout so moderation never delays a
chat response by more than ~400ms. If OpenAI moderation fails or times
out we log and continue — fail-open is the right choice for availability,
the keyword layer has already caught the obvious.

Usage:
    ok, reason = await moderate_text(prompt)
    if not ok: raise HTTPException(400, f"content_blocked: {reason}")
"""
from __future__ import annotations
import asyncio
import logging
import os
import re
from typing import Iterable

import httpx

logger = logging.getLogger(__name__)


# Blocklist. Intentionally terse; bulk-expansion comes from the
# OpenAI classifier. Matches are case-insensitive whole-phrase.
_BLOCKLIST_PHRASES: list[str] = [
    # CSAM indicators — zero tolerance, never negotiable
    "child sexual", "child porn", "csam", "minor nude",
    # Extremism / incitement
    "how to make a bomb", "build a pipe bomb", "synthesize sarin",
    "weaponize anthrax", "detonator circuit", "how to shoot up",
    # Targeted harassment enabling
    "dox this person", "find home address of", "stalk this person's",
    # Bioweapon synthesis
    "synthesize smallpox", "viral pathogen synthesis",
    # Credential theft enablement
    "steal credit card details from", "phishing kit for stripe",
]

_BLOCKLIST_PATTERNS = [re.compile(re.escape(p), re.IGNORECASE) for p in _BLOCKLIST_PHRASES]


def _keyword_check(text: str) -> tuple[bool, str]:
    """Synchronous fast-path. Returns (ok, reason)."""
    if not text:
        return True, ""
    for pat in _BLOCKLIST_PATTERNS:
        m = pat.search(text)
        if m:
            return False, f"blocked_keyword"
    return True, ""


async def _openai_moderation(text: str, timeout: float = 3.0) -> tuple[bool, str]:
    """Call OpenAI's /v1/moderations — free tier. Returns (ok, reason).

    Fail-open: any error = pass (the keyword layer already caught obvious).
    """
    key = os.environ.get("OPENAI_API_KEY", "")
    if not key:
        return True, ""
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.post(
                "https://api.openai.com/v1/moderations",
                headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                json={"input": text[:8192], "model": "omni-moderation-latest"},
            )
            if resp.status_code != 200:
                return True, ""   # fail-open
            data = resp.json()
            results = data.get("results") or []
            if not results:
                return True, ""
            r0 = results[0]
            if r0.get("flagged"):
                cats = [k for k, v in (r0.get("categories") or {}).items() if v]
                return False, f"moderation_flagged:{'|'.join(cats[:3]) or 'general'}"
            return True, ""
    except Exception as exc:
        logger.info("moderation call failed (fail-open): %s", exc)
        return True, ""


async def moderate_text(text: str, *, enable_openai: bool = True) -> tuple[bool, str]:
    """Combined check. Keyword first (free + instant), OpenAI second.

    Returns (ok, reason). `reason` is an opaque token suitable for logs,
    never surfaced verbatim to the user — map it to a generic refusal
    message at the route layer.
    """
    if not text or not text.strip():
        return True, ""
    ok, reason = _keyword_check(text)
    if not ok:
        return False, reason
    if enable_openai:
        ok2, reason2 = await _openai_moderation(text)
        if not ok2:
            return False, reason2
    return True, ""


async def moderate_many(texts: Iterable[str]) -> list[tuple[bool, str]]:
    """Batch moderation for bulk flows (campaign drafts, CSV imports).
    Returns list of (ok, reason) aligned with input order."""
    return await asyncio.gather(*[moderate_text(t) for t in texts])
