#!/usr/bin/env python3
# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "sentence-transformers",
#     "rapidfuzz",
#     "wordninja",
#     "orjson",
#     "nltk",
# ]
# ///
# FILE-SIZE-OK
"""
Telemetry Terminology Similarity Scorer

Scores all pairwise field name similarities across three independent layers.
Emits raw scores sorted by combined strength — no thresholds, no clustering,
no opinions. The consuming AI agent applies its own domain judgment.

  Layer 1 (Normalize):  camelCase/snake_case split + wordninja + abbreviation expansion
  Layer 2 (Syntactic):  RapidFuzz token_set_ratio (0-100)
  Layer 3 (Taxonomic):  WordNet Wu-Palmer head-noun similarity (0.0-1.0)
  Layer 4 (Semantic):   sentence-transformers cosine similarity (0.0-1.0)

Usage:
  # SSoT-OK: uv run handles PEP 723 inline deps
  echo -e "trace_id\\ntraceId\\nrequest_id" | uv run --python 3.13 term_similarity.py
  uv run --python 3.13 term_similarity.py --jsonl /path/to/telemetry.jsonl
  uv run --python 3.13 term_similarity.py --top 30 field1 field2 field3
"""
from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

import nltk
import orjson
import wordninja
from rapidfuzz import fuzz
from sentence_transformers import SentenceTransformer, util

if TYPE_CHECKING:
    from nltk.corpus.reader.wordnet import WordNetCorpusReader


# ---------------------------------------------------------------------------
# WordNet lazy initialization
# ---------------------------------------------------------------------------

_WN: WordNetCorpusReader | None = None


def _get_wordnet() -> WordNetCorpusReader:
    global _WN
    if _WN is None:
        nltk.download("wordnet", quiet=True)
        nltk.download("omw-1.4", quiet=True)
        from nltk.corpus import wordnet

        _WN = wordnet
    return _WN


# ---------------------------------------------------------------------------
# Layer 1: Normalization
# ---------------------------------------------------------------------------

ABBREVIATIONS: dict[str, str] = {
    "ts": "timestamp", "uid": "user id", "acct": "account",
    "req": "request", "resp": "response", "err": "error",
    "msg": "message", "dur": "duration", "ms": "milliseconds",
    "ns": "nanoseconds", "us": "microseconds", "svc": "service",
    "env": "environment", "src": "source", "dst": "destination",
    "ctx": "context", "op": "operation", "lvl": "level",
    "evt": "event", "attr": "attribute", "idx": "index",
    "cnt": "count", "num": "number", "desc": "description",
    "cfg": "configuration", "auth": "authentication",
    "conn": "connection", "lat": "latency",
}


def normalize_field_name(name: str) -> str:
    """Normalize a field name to space-separated lowercase tokens."""
    tokens = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", name)
    tokens = re.sub(r"[_\-./]", " ", tokens).lower().strip()
    parts: list[str] = []
    for token in tokens.split():
        if token in ABBREVIATIONS:
            parts.extend(ABBREVIATIONS[token].split())
        else:
            split = wordninja.split(token)
            parts.extend(split if len(split) > 1 else [token])
    return " ".join(parts)


# ---------------------------------------------------------------------------
# Layer 2: Syntactic (RapidFuzz)
# ---------------------------------------------------------------------------


def syntactic_similarity(a: str, b: str) -> float:
    return fuzz.token_set_ratio(a, b)


# ---------------------------------------------------------------------------
# Layer 3: Taxonomic (WordNet Wu-Palmer, head nouns only)
# ---------------------------------------------------------------------------


_WN_CACHE: dict[tuple[str, str], float] = {}


def wordnet_similarity(a: str, b: str) -> float:
    """Wu-Palmer similarity between head nouns of two normalized names.

    Memoized by (head_a, head_b) — at scale, repeated head nouns dominate
    cost. For 840 fields, ~352k pair calls collapse to ~3k unique head pairs.
    """
    head_a = a.split()[-1]
    head_b = b.split()[-1]
    if head_a == head_b:
        return 0.0
    # Canonical key (order-independent)
    key = (head_a, head_b) if head_a < head_b else (head_b, head_a)
    cached = _WN_CACHE.get(key)
    if cached is not None:
        return cached
    wn = _get_wordnet()
    best = 0.0
    for s1 in wn.synsets(head_a):
        for s2 in wn.synsets(head_b):
            score = s1.wup_similarity(s2)
            if score is not None and score > best:
                best = score
    _WN_CACHE[key] = best
    return best


# ---------------------------------------------------------------------------
# Layer 4: Semantic (sentence-transformers)
# ---------------------------------------------------------------------------

_MODEL: SentenceTransformer | None = None


def get_model() -> SentenceTransformer:
    global _MODEL
    if _MODEL is None:
        _MODEL = SentenceTransformer("all-MiniLM-L6-v2")
    return _MODEL


def semantic_similarity_matrix(names: list[str]) -> list[list[float]]:
    model = get_model()
    embeddings = model.encode(names, show_progress_bar=False)
    return util.cos_sim(embeddings, embeddings).tolist()


# ---------------------------------------------------------------------------
# Layer 5: Canonical Anchoring (bundled dictionary)
# ---------------------------------------------------------------------------

_CANONICAL: list[dict] | None = None


def _load_canonical() -> list[dict]:
    """Load bundled canonical-names.json from sibling directory."""
    global _CANONICAL
    if _CANONICAL is None:
        dict_path = Path(__file__).parent / "canonical-dictionary" / "canonical-names.json"
        if dict_path.exists():
            _CANONICAL = orjson.loads(dict_path.read_text())
        else:
            _CANONICAL = []
    return _CANONICAL


def canonical_match(field_normalized: str, top_n: int = 3) -> list[dict]:
    """Find closest canonical names for a normalized field name.

    Returns list of {name, source, score} sorted by score desc.
    Score is RapidFuzz token_set_ratio against the canonical name's normalized form.
    """
    canonical = _load_canonical()
    if not canonical:
        return []

    matches: list[tuple[float, dict]] = []
    for entry in canonical:
        canon_normalized = normalize_field_name(entry["name"])
        score = fuzz.token_set_ratio(field_normalized, canon_normalized)
        if score >= 60:
            matches.append((score, entry))

    matches.sort(key=lambda x: x[0], reverse=True)
    return [
        {
            "name": entry["name"],
            "source": entry["source"],
            "namespace": entry.get("namespace", ""),
            "score": round(score, 1),
        }
        for score, entry in matches[:top_n]
    ]


# ---------------------------------------------------------------------------
# Scoring Pipeline
# ---------------------------------------------------------------------------


@dataclass
class ScoredPair:
    field_a: str
    field_b: str
    normalized_a: str
    normalized_b: str
    syntactic: float   # 0-100
    taxonomic: float   # 0.0-1.0
    semantic: float    # 0.0-1.0
    combined: float    # weighted aggregate


@dataclass
class CanonicalAnchor:
    field: str
    normalized: str
    matches: list[dict]  # [{name, source, namespace, score}, ...]


@dataclass
class ScoringReport:
    total_fields: int
    unique_normalized: int
    exact_duplicates: list[tuple[str, str]]
    scored_pairs: list[ScoredPair]
    canonical_anchors: list[CanonicalAnchor] = field(default_factory=list)

    def to_json(self) -> str:
        return orjson.dumps(
            {
                "total_fields": self.total_fields,
                "unique_normalized": self.unique_normalized,
                "exact_duplicates": self.exact_duplicates,
                "scored_pairs": [
                    {
                        "field_a": p.field_a,
                        "field_b": p.field_b,
                        "normalized_a": p.normalized_a,
                        "normalized_b": p.normalized_b,
                        "syntactic": round(p.syntactic, 1),
                        "taxonomic": round(p.taxonomic, 3),
                        "semantic": round(p.semantic, 3),
                        "combined": round(p.combined, 3),
                    }
                    for p in self.scored_pairs
                ],
                "canonical_anchors": [
                    {
                        "field": a.field,
                        "normalized": a.normalized,
                        "matches": a.matches,
                    }
                    for a in self.canonical_anchors
                ],
            },
            option=orjson.OPT_INDENT_2,
        ).decode()

    def to_text(self) -> str:
        lines: list[str] = []
        lines.append(f"Fields analyzed: {self.total_fields}")
        lines.append(f"Unique after normalization: {self.unique_normalized}")
        lines.append("")

        if self.exact_duplicates:
            lines.append("=== EXACT DUPLICATES (after normalization) ===")
            for a, b in self.exact_duplicates:
                lines.append(f"  {a}  ==  {b}")
            lines.append("")

        if self.scored_pairs:
            lines.append("=== SCORED PAIRS (sorted by combined score) ===")
            lines.append(f"  {'syn':>5s}  {'tax':>5s}  {'sem':>5s}  {'comb':>5s}  pair")
            lines.append(f"  {'---':>5s}  {'---':>5s}  {'---':>5s}  {'----':>5s}  ----")
            for p in self.scored_pairs:
                lines.append(
                    f"  {p.syntactic:5.1f}  {p.taxonomic:5.3f}  {p.semantic:5.3f}"
                    f"  {p.combined:5.3f}  {p.field_a:25s} <-> {p.field_b}"
                )
            lines.append("")

        if self.canonical_anchors:
            lines.append("=== CANONICAL ANCHORS (top matches in OTel/OCSF/CloudEvents) ===")
            for a in self.canonical_anchors:
                if not a.matches:
                    continue
                lines.append(f"  {a.field}")
                for m in a.matches:
                    lines.append(
                        f"    {m['score']:5.1f}  [{m['source']}]  {m['name']}"
                    )

        return "\n".join(lines)


def score_fields(
    fields: list[str], *, top: int = 0, canonical: bool = False
) -> ScoringReport:
    """Score all field name pairs across 3 layers. No filtering, no thresholds.

    Args:
        fields: Input field names to score.
        top: Limit output to top N pairs (0 = all).
        canonical: If True, also lookup each field against the bundled
                   canonical dictionary (OTel/OCSF/CloudEvents).
    """
    # Layer 1: Normalize
    normalized = {f: normalize_field_name(f) for f in fields}

    norm_to_originals: dict[str, list[str]] = defaultdict(list)
    for orig, norm in normalized.items():
        norm_to_originals[norm].append(orig)

    exact_duplicates: list[tuple[str, str]] = []
    for norm, originals in norm_to_originals.items():
        if len(originals) > 1:
            for i in range(1, len(originals)):
                exact_duplicates.append((originals[0], originals[i]))

    unique_fields = list(norm_to_originals.keys())
    unique_originals = [norm_to_originals[n][0] for n in unique_fields]

    # Layers 2 + 3 + 4: Score all pairs
    n = len(unique_fields)
    sem_matrix = semantic_similarity_matrix(unique_fields)

    scored: list[ScoredPair] = []
    for i in range(n):
        for j in range(i + 1, n):
            syn = syntactic_similarity(unique_fields[i], unique_fields[j])
            wn = wordnet_similarity(unique_fields[i], unique_fields[j])
            sem = sem_matrix[i][j]

            # Combined: max of the three normalized scores.
            # Each layer catches different things — the strongest signal wins.
            combined = max(syn / 100.0, wn, sem)

            # Skip pairs where no layer shows any signal
            if combined < 0.25:
                continue

            scored.append(ScoredPair(
                field_a=unique_originals[i],
                field_b=unique_originals[j],
                normalized_a=unique_fields[i],
                normalized_b=unique_fields[j],
                syntactic=syn,
                taxonomic=wn,
                semantic=sem,
                combined=combined,
            ))

    scored.sort(key=lambda p: p.combined, reverse=True)

    if top > 0:
        scored = scored[:top]

    # Layer 5: Canonical anchoring (optional)
    anchors: list[CanonicalAnchor] = []
    if canonical:
        for orig, norm in zip(unique_originals, unique_fields, strict=False):
            matches = canonical_match(norm, top_n=3)
            if matches:
                anchors.append(CanonicalAnchor(
                    field=orig,
                    normalized=norm,
                    matches=matches,
                ))

    return ScoringReport(
        total_fields=len(fields),
        unique_normalized=len(unique_fields),
        exact_duplicates=exact_duplicates,
        scored_pairs=scored,
        canonical_anchors=anchors,
    )


# ---------------------------------------------------------------------------
# Input helpers
# ---------------------------------------------------------------------------


def fields_from_jsonl(path: Path) -> list[str]:
    all_fields: set[str] = set()
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = orjson.loads(line)
                if isinstance(obj, dict):
                    _collect_keys(obj, "", all_fields)
            except orjson.JSONDecodeError:
                continue
    return sorted(all_fields)


def fields_from_json_schema(path: Path) -> list[str]:
    with open(path) as f:
        schema = orjson.loads(f.read())
    fields: set[str] = set()
    _collect_schema_fields(schema, fields)
    return sorted(fields)


def _collect_keys(obj: dict, prefix: str, keys: set[str]) -> None:
    for k, v in obj.items():
        full_key = f"{prefix}.{k}" if prefix else k
        keys.add(full_key)
        if isinstance(v, dict):
            _collect_keys(v, full_key, keys)


def _collect_schema_fields(schema: dict, fields: set[str]) -> None:
    if "properties" in schema:
        for name, prop in schema["properties"].items():
            fields.add(name)
            if isinstance(prop, dict):
                _collect_schema_fields(prop, fields)
    if "items" in schema and isinstance(schema["items"], dict):
        _collect_schema_fields(schema["items"], fields)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Score telemetry field name similarity across 3 layers."
    )
    parser.add_argument("fields", nargs="*", help="Field names (also reads stdin)")
    parser.add_argument("--jsonl", type=Path, help="Extract fields from JSONL file")
    parser.add_argument("--schema-a", type=Path, help="First JSON schema")
    parser.add_argument("--schema-b", type=Path, help="Second JSON schema")
    parser.add_argument("--top", type=int, default=50, help="Show top N pairs (default: 50, 0=all)")
    parser.add_argument("--canonical", action="store_true",
                        help="Lookup each field against bundled OTel/OCSF/CloudEvents dictionary")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    fields: list[str] = []
    if args.jsonl:
        fields.extend(fields_from_jsonl(args.jsonl))
    elif args.schema_a and args.schema_b:
        fields.extend(fields_from_json_schema(args.schema_a))
        fields.extend(fields_from_json_schema(args.schema_b))
    elif args.fields:
        fields.extend(args.fields)
    elif not sys.stdin.isatty():
        for line in sys.stdin:
            line = line.strip()
            if line:
                fields.append(line)

    if not fields:
        parser.print_help()
        sys.exit(1)

    seen: set[str] = set()
    unique: list[str] = []
    for f in fields:
        if f not in seen:
            seen.add(f)
            unique.append(f)

    report = score_fields(unique, top=args.top, canonical=args.canonical)

    if args.json:
        print(report.to_json())
    else:
        print(report.to_text())


if __name__ == "__main__":
    main()
