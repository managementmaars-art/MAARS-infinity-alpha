#!/usr/bin/env python3
"""Compute lint scores for all wiki pages.

Usage:
    python3 lint_scores.py                       # default wiki/ directory
    python3 lint_scores.py <wiki_dir>            # custom wiki path
    python3 lint_scores.py <wiki_dir> --top N    # only emit N worst pages
    python3 lint_scores.py <wiki_dir> --minimal  # only {page, composite}

Outputs JSON array sorted by composite score (worst first).
All scores are floats in [0, 1]. Higher = needs more work.

Flags exist because a full lint dump at 1000 pages is ~50k tokens, and the
ITERATE batch phase only ever needs the top few. Pass `--top N --minimal`
to shrink the payload ~800x for ITERATE target selection.
"""

import json
import re
import sys
from pathlib import Path

SKIP_FILES = {"index.md", "log.md", "schema.md"}


def wiki_pages_in(wiki_dir: Path):
    return [p for p in wiki_dir.rglob("*.md")
            if p.name not in SKIP_FILES and not p.name.startswith(".")]


def crossref_sparsity(text: str, all_titles: set, own_stem: str) -> float:
    """Fraction of linkable entity/concept mentions that aren't [[linked]].

    A mention is linkable if a wiki page exists with that title. Self-references
    are excluded so a page cannot satisfy the metric by linking to itself —
    that reward-hack was observed in the epoch-5 run of 2026-04-11.

    Score 0 = every linkable mention is linked. Score 1 = nothing linked.
    Pages with zero mentions of any other wiki title return 0 (informationless
    for this dimension; orphan_rate picks up the under-connection signal).
    """
    if not all_titles:
        return 0.0

    text_lower = text.lower()
    mentioned = {t for t in all_titles
                 if t != own_stem and len(t) > 3 and t in text_lower}
    if not mentioned:
        return 0.0

    linked = {t for t in mentioned
              if f"[[{t}]]" in text_lower or f"[[{t}|" in text_lower}
    return round(1.0 - (len(linked) / len(mentioned)), 2)


def orphan_rate(own_stem: str, inbound: dict) -> float:
    """Penalty for pages with few inbound wikilinks from elsewhere in the wiki.

    0 inbound → 1.0 (orphan)
    1 inbound → 0.66
    2 inbound → 0.33
    3+ inbound → 0.0
    """
    n = inbound.get(own_stem, 0)
    if n == 0:
        return 1.0
    if n == 1:
        return 0.66
    if n == 2:
        return 0.33
    return 0.0


def unsourced_density(text: str) -> float:
    """Fraction of substantive prose lines that carry no (vault:...) citation.

    Skips YAML frontmatter, headings, empty lines, and lines under 5 words.
    Gives the ratchet a second real signal independent of wikilink counting.
    """
    substantive = 0
    unsourced = 0
    in_frontmatter = False
    frontmatter_seen = 0
    for line in text.split("\n"):
        s = line.strip()
        if s == "---":
            frontmatter_seen += 1
            in_frontmatter = frontmatter_seen == 1
            continue
        if in_frontmatter or not s or s.startswith("#"):
            continue
        if len(s.split()) < 5:
            continue
        substantive += 1
        if "(vault:" not in s:
            unsourced += 1
    if substantive == 0:
        return 0.0
    return round(unsourced / substantive, 2)


def query_misses(page_stem: str, log_text: str) -> float:
    """Fraction of queries involving this page that needed vault fallback.

    Parsed from log.md. Returns 0.5 (unknown) if no queries found.
    """
    if not log_text:
        return 0.5

    # Find query log blocks
    blocks = re.findall(
        r'## \[.*?\] query \|.*?\n(.*?)(?=\n## |\Z)',
        log_text, re.DOTALL
    )

    relevant = [b for b in blocks if page_stem.lower() in b.lower()]
    if not relevant:
        return 0.5  # no queries touched this page — unknown

    fallbacks = sum(1 for b in relevant if "vault fallback" in b.lower())
    return round(fallbacks / len(relevant), 2)


NEGATION_WORDS = {"not", "no", "never", "neither", "nor", "without",
                   "cannot", "can't", "doesn't", "don't", "isn't", "aren't",
                   "wasn't", "weren't", "won't", "wouldn't", "shouldn't",
                   "couldn't", "unlikely", "false", "incorrect", "wrong"}


def _extract_sourced_claims(text: str) -> list:
    """Extract lines with (vault:...) citations as sourced claim strings."""
    claims = []
    for line in text.split("\n"):
        s = line.strip()
        if "(vault:" in s and len(s.split()) >= 4:
            claims.append(s)
    return claims


def _significant_words(text: str) -> set:
    """Extract lowercase content words (>3 chars, no stopwords).

    Strips (vault:...) citations and [[wikilink]] markup before extraction
    to avoid false matches on vault filenames and link syntax.
    """
    stop = {"the", "and", "for", "are", "was", "were", "been", "being",
            "have", "has", "had", "with", "from", "that", "this", "which",
            "their", "there", "about", "also", "more", "than", "into",
            "some", "only", "other", "such", "each", "used", "using",
            "source", "material", "related", "vault", "wiki", "wikipedia",
            "extracted"}
    # Strip vault citations and wikilinks before word extraction
    cleaned = re.sub(r"\(vault:[^)]*\)", "", text)
    cleaned = re.sub(r"\[\[[^\]]*\]\]", "", cleaned)
    words = re.findall(r"[a-z]{4,}", cleaned.lower())
    return {w for w in words if w not in stop}


def _has_negation(text: str) -> bool:
    """Check if text contains negation words."""
    words = set(re.findall(r"[a-z']+", text.lower()))
    return bool(words & NEGATION_WORDS)


def contradictions(text: str, all_page_claims: dict, own_stem: str) -> float:
    """Fraction of sourced claims that potentially contradict another page.

    For each sourced claim on this page, finds claims on other pages that
    share >= 4 distinctive content words but differ in negation polarity.
    Requires at least one shared word > 6 chars to avoid false positives
    from common short words. Deterministic, no LLM.

    Source stubs (pages in sources/) are excluded from cross-comparison
    since their boilerplate text shares words without making factual claims.
    """
    own_claims = _extract_sourced_claims(text)
    if not own_claims:
        return 0.0

    # Filter out source stubs from comparison pool
    concept_claims = {k: v for k, v in all_page_claims.items()
                      if not k.startswith("sources/")}

    flagged = 0
    for claim in own_claims:
        claim_words = _significant_words(claim)
        claim_neg = _has_negation(claim)
        found_tension = False
        for other_stem, other_claims in concept_claims.items():
            if other_stem == own_stem or found_tension:
                break
            for other_claim in other_claims:
                other_words = _significant_words(other_claim)
                shared = claim_words & other_words
                # Require heavy overlap with multiple distinctive words
                # to avoid false positives in a densely-connected wiki
                distinctive = [w for w in shared if len(w) > 6]
                if len(shared) >= 5 and len(distinctive) >= 2:
                    if claim_neg != _has_negation(other_claim):
                        flagged += 1
                        found_tension = True
                        break

    return round(min(1.0, flagged / len(own_claims)), 2)


def vault_coverage_gap(page_stem: str, text: str, vault_db_path) -> float:
    """Fraction of relevant vault material not cited on this page.

    Queries vault.db FTS (BM25) for the page's topic. Counts how many of
    the top vault hits aren't cited via (vault:...). Higher = more relevant
    source material that this page hasn't incorporated yet. Measures
    curiosity gap: how much unexplored ground exists in the vault.

    Returns 0.0 if vault.db doesn't exist or has no relevant hits.
    """
    if vault_db_path is None or not vault_db_path.exists():
        return 0.0

    query = page_stem.replace("-", " ").replace("_", " ")
    if len(query) < 3:
        return 0.0

    try:
        import sqlite3
        conn = sqlite3.connect(str(vault_db_path))
        rows = conn.execute(
            "SELECT path FROM sources WHERE sources MATCH ? "
            "ORDER BY bm25(sources) LIMIT 10",
            (query,),
        ).fetchall()
        conn.close()
    except Exception:
        return 0.0

    if not rows:
        return 0.0

    text_lower = text.lower()
    uncited = 0
    for (path,) in rows:
        # Check both (vault:filename) and bare filename mentions
        if f"(vault:{path})" not in text_lower and path.lower() not in text_lower:
            uncited += 1

    return round(uncited / len(rows), 2)


def compute_all(wiki_dir: Path) -> list:
    """Score every page under wiki_dir. Sorted worst-first by composite.

    Three passes: (1) gather inbound-link counts, (2) gather sourced claims
    for cross-page contradiction detection, (3) score each page.

    All six dimensions are now live with real implementations:
    - crossref_sparsity (0.25) — outbound link quality
    - orphan_rate (0.25) — inbound link coverage
    - unsourced_density (0.20) — citation coverage
    - contradictions (0.10) — cross-page factual tension
    - vault_coverage_gap (0.10) — unexplored vault material
    - query_misses (0.10) — vault fallback frequency in queries
    """
    pages = wiki_pages_in(wiki_dir)
    pages_text = {p: p.read_text() for p in pages}
    titles = {p.stem.lower() for p in pages}
    log_path = wiki_dir / "log.md"
    log_text = log_path.read_text() if log_path.exists() else ""
    vault_db_path = wiki_dir.parent / "vault" / "vault.db"

    # Pass 1: global inbound-link count per title (excluding self-links)
    inbound = {t: 0 for t in titles}
    for page, text in pages_text.items():
        own = page.stem.lower()
        text_lower = text.lower()
        for t in titles:
            if t == own:
                continue
            if f"[[{t}]]" in text_lower or f"[[{t}|" in text_lower:
                inbound[t] += 1

    # Pass 2: gather sourced claims per page for contradiction detection.
    # Keys use relative path so contradictions() can filter source stubs.
    all_page_claims = {}
    for page, text in pages_text.items():
        claims = _extract_sourced_claims(text)
        if claims:
            rel = str(page.relative_to(wiki_dir))
            all_page_claims[rel] = claims

    # Pass 3: per-page scoring
    results = []
    for page, text in pages_text.items():
        own = page.stem.lower()
        scores = {
            "crossref_sparsity": crossref_sparsity(text, titles, own),
            "orphan_rate": orphan_rate(own, inbound),
            "unsourced_density": unsourced_density(text),
            "contradictions": contradictions(text, all_page_claims,
                                             str(page.relative_to(wiki_dir))),
            "vault_coverage_gap": vault_coverage_gap(own, text, vault_db_path),
            "query_misses": query_misses(page.stem, log_text),
        }
        scores["composite"] = round(
            0.25 * scores["crossref_sparsity"]
            + 0.25 * scores["orphan_rate"]
            + 0.20 * scores["unsourced_density"]
            + 0.10 * scores["contradictions"]
            + 0.10 * scores["vault_coverage_gap"]
            + 0.10 * scores["query_misses"],
            3,
        )
        results.append({
            "page": str(page.relative_to(wiki_dir)),
            "scores": scores,
        })

    results.sort(key=lambda x: x["scores"]["composite"], reverse=True)
    return results


def main():
    args = [a for a in sys.argv[1:]]
    top_n = None
    minimal = False
    positional = []
    i = 0
    while i < len(args):
        if args[i] == "--top":
            top_n = int(args[i + 1])
            i += 2
        elif args[i] == "--minimal":
            minimal = True
            i += 1
        else:
            positional.append(args[i])
            i += 1

    wiki_dir = Path(positional[0]) if positional else Path("wiki")
    results = compute_all(wiki_dir)

    if top_n is not None:
        results = results[:top_n]
    if minimal:
        results = [{"page": r["page"], "composite": r["scores"]["composite"]} for r in results]

    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
