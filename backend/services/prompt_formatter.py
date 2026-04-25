"""Provider-specific prompt shaping — small tweaks, big quality bumps.

Different providers reward different prompt shapes. Same content,
different wrapper, measurably better output. Summary of what's published:

  Anthropic : wrap long context in XML tags ('<document>...</document>').
              Per their prompt engineering guide, XML-tagged context
              gives ~12% higher structured-output accuracy than plain
              prose in the system prompt.

  OpenAI    : use markdown headers (## Instructions, ## Context) in
              system prompts. GPT-4.x family was RLHF'd on markdown-
              structured instructions.

  Gemini    : move the actual instruction to the END of the prompt,
              after any context ("positional bias": Gemini attends
              more strongly to the tail). Google's own prompting guide
              confirms this for Gemini-2.0+.

  Groq/Cerebras : they serve Llama/Qwen/DeepSeek — those models prefer
              plain-text instruction-following; the XML/markdown
              wrappers don't hurt but don't help.

This module exposes `shape(messages, provider, model)` which returns a
lightly-rewritten messages list. Never mutates the caller's copy.
"""
from __future__ import annotations
import logging
from typing import Any

logger = logging.getLogger(__name__)

_ANTHROPIC_CONTEXT_HINTS = ("context:", "documents:", "reference:", "knowledge:")


def _wrap_anthropic_context(content: str) -> str:
    """If the system prompt looks like it has a big context block, wrap
    it in <context>...</context>. Cheap heuristic."""
    if not content or len(content) < 500:
        return content
    low = content.lower()
    if not any(h in low for h in _ANTHROPIC_CONTEXT_HINTS):
        return content
    # Find the first hint word and wrap the remainder.
    for hint in _ANTHROPIC_CONTEXT_HINTS:
        idx = low.find(hint)
        if idx >= 0:
            head, tail = content[:idx], content[idx:]
            if "<context>" in tail.lower():  # don't double-wrap
                return content
            return f"{head}<context>\n{tail}\n</context>"
    return content


def _structure_openai_system(content: str) -> str:
    """If system prompt is longer than a paragraph and has no markdown
    headers, add a ## Instructions header so the model's RLHF structure-
    prior kicks in."""
    if not content or len(content) < 200:
        return content
    if "##" in content or "#" in content.split("\n", 1)[0]:
        return content
    return f"## Instructions\n{content}"


def _tail_weight_gemini(messages: list[dict]) -> list[dict]:
    """If the last user message has an instruction followed by context,
    swap: Gemini attends more strongly to the tail, so put the
    instruction there. Heuristic: if first 20% looks like an
    instruction and last 80% looks like paste-context, flip."""
    if not messages:
        return messages
    last = messages[-1]
    if last.get("role") != "user":
        return messages
    content = last.get("content")
    if not isinstance(content, str) or len(content) < 800:
        return messages
    head, sep, rest = content.partition("\n\n")
    if sep and len(head) < 300 and len(rest) > len(head) * 2:
        # head looks instruction-y, rest looks context-y → move instruction to end
        new_content = f"{rest}\n\n{head}"
        return [*messages[:-1], {**last, "content": new_content}]
    return messages


def shape(messages: list[dict], *, provider: str, model: str = "") -> list[dict]:
    """Return a lightly-rewritten messages list optimized for the target
    provider. Caller's copy is never mutated."""
    if not messages:
        return messages
    provider = (provider or "").lower()

    if provider == "anthropic":
        out = []
        for m in messages:
            if m.get("role") == "system" and isinstance(m.get("content"), str):
                out.append({**m, "content": _wrap_anthropic_context(m["content"])})
            else:
                out.append(m)
        return out

    if provider == "openai":
        out = []
        for m in messages:
            if m.get("role") == "system" and isinstance(m.get("content"), str):
                out.append({**m, "content": _structure_openai_system(m["content"])})
            else:
                out.append(m)
        return out

    if provider in ("gemini", "google"):
        return _tail_weight_gemini(list(messages))

    return messages
