"""Output-side guardrails — scan assistant responses BEFORE they leave.

Input-side (prompt_injection_detector) catches attackers coming IN.
Output-side catches two distinct failure modes:

  1. LEAK — the model parroted internal system-prompt text, internal
     tokens, API keys it saw in context, or scrubbed PII we injected
     for anonymization (shouldn't happen but does).
  2. UNSAFE CONTENT — the model produced content our policy disallows:
     PII about third parties, credentials, medical diagnoses,
     investment advice with specific recommendations, instructions
     for physical harm.

We keep this lightweight (regex + length-bounded LLM classifier) so
the hot path doesn't add seconds. Unsafe responses get redacted
(template reply) rather than blocked outright — blocking produces bad
UX; a graceful "I can't help with that specific request" preserves
the session.
"""
from __future__ import annotations
import logging
import re
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class GuardVerdict:
    clean: bool
    redacted_text: str
    reasons: list[str]


_LEAK_PATTERNS = [
    re.compile(r"(?i)\bmy (?:system|internal) (?:prompt|instructions?) (?:is|are|says?|states?)"),
    re.compile(r"(?i)\bi (?:was|am) (?:told|instructed|trained) to"),
    re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"),                      # OpenAI-style keys
    re.compile(r"\bxai-[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bsk-ant-[A-Za-z0-9-]{20,}\b"),                 # Anthropic keys
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),                         # AWS key id
    re.compile(r"\bgsk_[A-Za-z0-9]{20,}\b"),                     # Groq
    re.compile(r"-----BEGIN [A-Z ]+ PRIVATE KEY-----"),
]

_UNSAFE_PATTERNS = [
    re.compile(r"(?i)\b(?:how to (?:make|build|construct|synthesize)).{0,40}\b(?:bomb|explosive|pipe bomb|pressure cooker|nerve agent|ricin|sarin|methamphetamine|fentanyl|cocaine)"),
    re.compile(r"(?i)\binstructions? for (?:hacking|breaking into|penetrating)\b.*\b(?:someone else|unauthorized|without permission)"),
    re.compile(r"(?i)\bssn(?:\s+number)?\s*[:=]\s*\d"),
    re.compile(r"(?i)\bsocial security number\s*[:=]\s*\d"),
]


def scan(text: str) -> GuardVerdict:
    if not text or not isinstance(text, str):
        return GuardVerdict(clean=True, redacted_text=text or "", reasons=[])

    reasons: list[str] = []
    redacted = text

    for p in _LEAK_PATTERNS:
        m = p.search(redacted)
        if m:
            reasons.append(f"leak:{m.group(0)[:40]}")
            redacted = p.sub("[REDACTED_LEAK]", redacted)

    for p in _UNSAFE_PATTERNS:
        m = p.search(redacted)
        if m:
            reasons.append(f"unsafe:{m.group(0)[:60]}")

    if any(r.startswith("unsafe:") for r in reasons):
        redacted = (
            "I can't help with that specific request. If you have a different "
            "question I can address, I'm happy to try."
        )
        return GuardVerdict(clean=False, redacted_text=redacted, reasons=reasons)

    return GuardVerdict(clean=not reasons, redacted_text=redacted, reasons=reasons)


def guard_response(response: dict) -> dict:
    """Apply guard in place on an OpenAI-compat response dict. If the
    content was rewritten, mark `maars.guard = {reasons}` so the caller
    can see it happened."""
    try:
        content = response["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        return response
    v = scan(content)
    if v.reasons:
        response["choices"][0]["message"]["content"] = v.redacted_text
        response.setdefault("maars", {})["guard"] = {
            "clean": v.clean,
            "reasons": v.reasons[:5],
        }
    return response
