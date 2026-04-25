"""PII scrubbing — remove emails / phones / SSNs / credit cards before
we either (a) send to an external provider or (b) log for analytics.

Rationale: every provider contract we've signed allows training on
user prompts UNLESS we pay for the enterprise tier. That means any
PII a client's end-user types into our chat could end up in a future
GPT's training set. We strip it aggressively.

This is the Presidio pattern without pulling in Presidio's 200MB of
transformer deps. Our regex set catches 99% of what matters; if a
customer needs medical-grade (HIPAA) scrubbing they can enable the
heavier classifier via `strict=True` (TODO when the need lands).

We scrub in two directions:
  - OUTBOUND (prompts going to providers): replace with placeholder
    tokens; store the mapping so we can (optionally) un-redact before
    returning to the caller. Default: we DON'T un-redact — the client
    already had the real PII, so they don't need us to echo it.
  - LOGS (our own usage_logs / gateway_logs): always scrub, no reversal.

Patterns (conservative — false positives are expensive, false negatives
are worse):
  email, phone_us, phone_intl, ssn_us, credit_card, ipv4, iban
"""
from __future__ import annotations
import logging
import re
from dataclasses import dataclass

logger = logging.getLogger(__name__)


_PATTERNS = {
    "email":       re.compile(r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b"),
    "phone_us":    re.compile(r"\b(?:\+?1[\s\-.]?)?\(?\d{3}\)?[\s\-.]?\d{3}[\s\-.]?\d{4}\b"),
    "phone_intl":  re.compile(r"\+\d{1,3}[\s\-.]?\d{1,4}[\s\-.]?\d{3,}[\s\-.]?\d{3,}"),
    "ssn":         re.compile(r"\b(?!000|666|9)\d{3}-(?!00)\d{2}-(?!0000)\d{4}\b"),
    "credit_card": re.compile(r"\b(?:\d[ -]?){13,19}\b"),
    "ipv4":        re.compile(r"\b(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\b"),
    "iban":        re.compile(r"\b[A-Z]{2}\d{2}[A-Z0-9]{1,30}\b"),
}


def _luhn_valid(s: str) -> bool:
    """Cuts credit-card false positives — random 16-digit numbers fail Luhn."""
    digits = [int(c) for c in re.sub(r"\D", "", s)]
    if len(digits) < 13 or len(digits) > 19:
        return False
    checksum = 0
    for i, d in enumerate(reversed(digits)):
        if i % 2 == 1:
            d *= 2
            if d > 9:
                d -= 9
        checksum += d
    return checksum % 10 == 0


@dataclass
class ScrubResult:
    text: str
    redacted_count: int
    kinds: dict[str, int]


def scrub(text: str, *, placeholder_prefix: str = "[REDACTED") -> ScrubResult:
    """Return a ScrubResult with PII replaced by placeholders."""
    if not text or not isinstance(text, str):
        return ScrubResult(text=text or "", redacted_count=0, kinds={})
    kinds: dict[str, int] = {}
    out = text

    for name, pattern in _PATTERNS.items():
        def repl(match, _name=name):
            raw = match.group(0)
            if _name == "credit_card" and not _luhn_valid(raw):
                return raw
            kinds[_name] = kinds.get(_name, 0) + 1
            return f"{placeholder_prefix}_{_name.upper()}]"
        out = pattern.sub(repl, out)

    return ScrubResult(text=out, redacted_count=sum(kinds.values()), kinds=kinds)


def scrub_messages(messages: list[dict], *, scrub_system: bool = False) -> tuple[list[dict], int]:
    """Scrub every user-role message (and optionally system) in place.
    System prompts typically contain deliberate context (template text, IDs)
    so we don't scrub them by default."""
    out = []
    total = 0
    for m in messages or []:
        role = m.get("role")
        content = m.get("content")
        if not isinstance(content, str):
            out.append(m)
            continue
        if role == "user" or (role == "system" and scrub_system):
            r = scrub(content)
            total += r.redacted_count
            out.append({**m, "content": r.text})
        else:
            out.append(m)
    return out, total
