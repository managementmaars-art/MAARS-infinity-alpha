"""Citation extraction — attribute assistant claims back to source passages.

RAG answers without citations are black boxes. Two ways we can add
attribution:

  1. PROMPT-TIME: wrap each retrieved passage with a numbered marker
     [S1], [S2], ... and instruct the model to cite inline. We parse
     [Sn] tokens out of the response and return (text, citations).
  2. POST-HOC: for responses we didn't cite-wrap at prompt time, do a
     cheap second-pass match: for each sentence in the response, find
     the retrieval passage with highest overlap (shingle Jaccard) and
     attach that as the citation.

Method 1 is cheaper at quality; method 2 is a fallback for traffic we
can't touch at prompt time.
"""
from __future__ import annotations
import logging
import re
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class Citation:
    source_id: str
    source_text: str
    span: str          # the sentence in the answer that this source backs up
    score: float = 1.0


_MARKER_RE = re.compile(r"\[S(\d+)\]")


def build_cite_wrapped_prompt(sources: list[str]) -> str:
    """Format sources as [S1] ... [S2] ... ready to paste into a system
    prompt. Use with an instruction like: 'Cite every claim with [Sn] tags.'"""
    return "\n\n".join(f"[S{i+1}] {s}" for i, s in enumerate(sources))


def parse_inline_citations(answer: str, sources: list[str]) -> tuple[str, list[Citation]]:
    """Strip [Sn] markers from answer text and return the (clean_text,
    citations) pair."""
    cites: list[Citation] = []
    for m in _MARKER_RE.finditer(answer):
        idx = int(m.group(1)) - 1
        if 0 <= idx < len(sources):
            # Extract the sentence this marker appears in.
            sent_start = answer.rfind(".", 0, m.start()) + 1
            sent_end = answer.find(".", m.end())
            sent_end = sent_end if sent_end != -1 else len(answer)
            span = answer[sent_start:sent_end].strip()
            cites.append(Citation(
                source_id=f"S{idx+1}",
                source_text=sources[idx],
                span=span[:300],
            ))
    clean = _MARKER_RE.sub("", answer)
    clean = re.sub(r"\s{2,}", " ", clean).strip()
    return clean, cites


def _shingles(s: str, k: int = 5) -> set[str]:
    s2 = " ".join(s.lower().split())
    return {s2[i:i+k] for i in range(max(0, len(s2) - (k - 1)))}


def _best_match(sentence: str, sources: list[str]) -> tuple[int, float]:
    """Return (best_source_index, jaccard)."""
    s_sh = _shingles(sentence)
    best_i, best_j = -1, 0.0
    for i, src in enumerate(sources):
        src_sh = _shingles(src)
        if not s_sh or not src_sh:
            continue
        j = len(s_sh & src_sh) / max(len(s_sh | src_sh), 1)
        if j > best_j:
            best_j = j
            best_i = i
    return best_i, best_j


def attribute_post_hoc(
    answer: str,
    sources: list[str],
    *,
    min_jaccard: float = 0.15,
) -> list[Citation]:
    """For each sentence in the answer, find the retrieval passage with
    highest shingle overlap. Attach when overlap exceeds the threshold."""
    if not answer or not sources:
        return []
    cites: list[Citation] = []
    for sent in re.split(r"(?<=[.!?])\s+(?=[A-Z])", answer.strip()):
        if len(sent) < 20:
            continue
        idx, j = _best_match(sent, sources)
        if idx >= 0 and j >= min_jaccard:
            cites.append(Citation(
                source_id=f"S{idx+1}",
                source_text=sources[idx][:400],
                span=sent.strip()[:300],
                score=round(j, 3),
            ))
    return cites
