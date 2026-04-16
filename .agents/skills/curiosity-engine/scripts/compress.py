#!/usr/bin/env python3
"""Caveman compression: strip predictable grammar, keep facts.

Usage:
    python3 compress.py <file.md>           # compressed_tokens, sourced_claims, tpc
    python3 compress.py <file.md> --full    # print compressed text
    python3 compress.py <file.md> --ratio   # print token reduction ratio

Zero dependencies. Applied at read-time only — wiki is stored as clean markdown.
LLMs reconstruct grammar from facts natively. This just avoids wasting context on it.
"""

import re
import sys
from pathlib import Path

# Words that carry near-zero information for an LLM reader.
# Organized by category for maintainability.
REMOVE = {
    # articles
    "a", "an", "the",
    # copula / auxiliary verbs
    "is", "are", "was", "were", "be", "been", "being",
    "has", "have", "had", "do", "does", "did",
    # filler adverbs
    "very", "really", "quite", "rather", "somewhat",
    "just", "simply", "basically", "essentially", "actually",
    "generally", "typically", "usually", "often", "commonly",
    # pronouns (recoverable from context)
    "it", "its", "this", "that", "these", "those",
    "which", "who", "whom", "whose",
    # transition words (LLM reconstructs logical flow)
    "however", "therefore", "furthermore", "moreover",
    "additionally", "consequently", "nevertheless",
    # high-frequency prepositions (most can be inferred)
    "in", "of", "for", "to", "with", "by", "from", "as",
    "on", "at", "into", "through", "during", "about",
}


def compress(text: str) -> str:
    """Compress text by removing predictable grammar tokens.

    Preserves: headings, YAML frontmatter, code blocks, wikilinks,
    vault citations, numbers, negation.
    """
    out = []
    in_code_block = False

    for line in text.split("\n"):
        s = line.strip()

        # Preserve code blocks verbatim
        if s.startswith("```"):
            in_code_block = not in_code_block
            out.append(line)
            continue
        if in_code_block:
            out.append(line)
            continue

        # Preserve structural lines verbatim
        if s.startswith("#") or s.startswith("---"):
            out.append(line)
            continue

        # Preserve YAML frontmatter lines
        if ":" in s and s[0:1].isalpha() and s.index(":") < 30:
            out.append(line)
            continue

        # Preserve empty lines
        if not s:
            out.append("")
            continue

        # Compress prose lines
        words = line.split()
        kept = []
        for w in words:
            # Always keep special tokens
            if "[[" in w or "(vault:" in w or w.startswith("`"):
                kept.append(w)
                continue

            # Always keep negation (changes meaning)
            if w.lower() in ("not", "no", "never", "none", "neither", "nor"):
                kept.append(w)
                continue

            # Remove if in the removal set
            cleaned = w.lower().strip(".,;:!?()")
            if cleaned in REMOVE:
                continue

            kept.append(w)

        out.append(" ".join(kept))

    return "\n".join(out)


def token_count(text: str) -> int:
    """Rough token count (whitespace-split). Close enough for ratios."""
    return len(text.split())


def sourced_claims(text: str) -> int:
    """Count lines containing a vault citation."""
    return sum(1 for line in text.split("\n")
               if "(vault:" in line and line.strip())


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: compress.py <file.md> [--full | --ratio]")
        sys.exit(1)

    text = Path(sys.argv[1]).read_text()
    compressed = compress(text)

    if "--full" in sys.argv:
        print(compressed)
    elif "--ratio" in sys.argv:
        orig = token_count(text)
        comp = token_count(compressed)
        pct = (comp * 100 // orig) if orig > 0 else 100
        print(f"{orig} → {comp} tokens ({pct}%)")
    else:
        toks = token_count(compressed)
        claims = max(sourced_claims(text), 1)
        tpc = toks / claims
        print(f"compressed_tokens={toks} sourced_claims={claims} tpc={tpc:.1f}")
