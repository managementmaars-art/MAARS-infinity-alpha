"""Context-window packing — fit the most valuable content in the budget.

Problem: 32K / 128K / 1M context windows sound huge, but (a) pricing
scales with used tokens, and (b) "lost in the middle" literature
(Liu et al. 2023) shows models under-attend to the middle 60-80% of
long contexts. Putting every RAG chunk in regardless of relevance hurts
you twice: cost up, quality down.

This module:
  1. Takes a token budget.
  2. Takes a ranked list of candidate context chunks.
  3. Greedy-knapsacks them by (rerank_score / token_count), keeping the
     highest value-per-token first.
  4. Orders output by a "position-aware" pattern: highest-signal chunks
     FIRST and LAST in the packed context (so they fall in the
     attention-favored regions), lower-signal chunks in the middle.

`pack()` returns a single formatted string ready to paste into a
prompt, plus the usage breakdown.
"""
from __future__ import annotations
import logging
from dataclasses import dataclass
from typing import Iterable

logger = logging.getLogger(__name__)


@dataclass
class Chunk:
    text: str
    score: float = 1.0
    tokens: int = 0           # populated if caller pre-counted; otherwise estimated


@dataclass
class PackResult:
    packed: str
    used_tokens: int
    used_chunks: int
    dropped_chunks: int


def _estimate_tokens(text: str) -> int:
    try:
        from services.token_counter import count_tokens
        return count_tokens(text)
    except Exception:
        return max(1, len(text) // 4)


def pack(
    chunks: list[Chunk],
    *,
    budget_tokens: int,
    separator: str = "\n\n---\n\n",
) -> PackResult:
    """Knapsack + position-aware reorder. Returns packed string."""
    if not chunks or budget_tokens <= 0:
        return PackResult(packed="", used_tokens=0, used_chunks=0, dropped_chunks=len(chunks or []))

    # Fill token counts where missing.
    for c in chunks:
        if c.tokens <= 0:
            c.tokens = _estimate_tokens(c.text)

    # Value per token = score / tokens (simple density knapsack).
    ranked = sorted(
        chunks, key=lambda c: c.score / max(c.tokens, 1), reverse=True,
    )
    picked: list[Chunk] = []
    used = 0
    for c in ranked:
        if used + c.tokens <= budget_tokens:
            picked.append(c)
            used += c.tokens
    dropped = len(chunks) - len(picked)

    if not picked:
        return PackResult(packed="", used_tokens=0, used_chunks=0, dropped_chunks=dropped)

    # Position-aware reorder: put highest-score first, second-highest
    # last (primacy + recency), then interleave mids in the middle.
    by_score = sorted(picked, key=lambda c: c.score, reverse=True)
    if len(by_score) == 1:
        ordered = by_score
    elif len(by_score) == 2:
        ordered = by_score
    else:
        head, tail = by_score[0], by_score[1]
        mids = by_score[2:]
        ordered = [head, *mids, tail]

    packed = separator.join(c.text.strip() for c in ordered if c.text.strip())
    return PackResult(
        packed=packed,
        used_tokens=used,
        used_chunks=len(picked),
        dropped_chunks=dropped,
    )
