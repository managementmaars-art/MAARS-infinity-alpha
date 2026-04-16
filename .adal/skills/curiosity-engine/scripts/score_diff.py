#!/usr/bin/env python3
"""Minimal mechanical gate for wiki edits.

Hard floors only — the opus judge handles nuanced quality review.
These gates catch catastrophic regressions that no edit should cause:
  1. No citation loss: sourced_claims(after) >= sourced_claims(before)
  2. No extreme bloat: tokens(after) <= tokens(before) * 2.0
  3. New pages: ≥2 citations, ≥2 wikilinks, ≥100 words

Usage:
    echo "<new text>" | python3 score_diff.py <page.md> --new-text-stdin
    python3 score_diff.py <page.md> --new-file <candidate.md>
    python3 score_diff.py <page.md> --new-page --new-file <candidate.md>

Outputs one JSON line to stdout. Exit code always 0 on well-formed input.
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from compress import compress, token_count, sourced_claims  # noqa: E402

WIKILINK_RE = re.compile(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]")


def lint_matchable_links(text: str) -> int:
    """Count wikilinks in hyphen-case form (no spaces)."""
    count = 0
    for m in WIKILINK_RE.finditer(text):
        target = m.group(1).strip()
        if " " not in target:
            count += 1
    return count


def metrics(text: str) -> dict:
    comp = compress(text)
    return {
        "tokens": token_count(comp),
        "claims": max(sourced_claims(text), 1),
        "wikilinks": lint_matchable_links(text),
    }


def verdict(before: dict, after: dict) -> tuple:
    """Minimal accept/reject: citation loss and extreme bloat only."""
    if after["claims"] < before["claims"]:
        return False, f"citation loss ({before['claims']}->{after['claims']})"
    if before["tokens"] > 0 and after["tokens"] > before["tokens"] * 2.0:
        return False, f"extreme bloat ({before['tokens']}->{after['tokens']}, >100%)"
    return True, "pass"


def new_page_verdict(text: str) -> tuple:
    """Minimum-quality floors for new pages."""
    m = metrics(text)
    words = len(text.split())
    if m["claims"] < 2:
        return False, f"too few citations ({m['claims']}; need ≥2)"
    if m["wikilinks"] < 2:
        return False, f"too few wikilinks ({m['wikilinks']}; need ≥2)"
    if words < 100:
        return False, f"too short ({words} words; need ≥100)"
    return True, f"claims={m['claims']}, wikilinks={m['wikilinks']}, words={words}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("page")
    ap.add_argument("--new-file", default=None)
    ap.add_argument("--new-text-stdin", action="store_true")
    ap.add_argument("--new-page", action="store_true",
                    help="Page does not exist yet; uses new-page gates.")
    args = ap.parse_args()

    page = Path(args.page)

    # Read candidate text
    if args.new_file:
        new_text = Path(args.new_file).read_text()
    elif args.new_text_stdin:
        new_text = sys.stdin.read()
    else:
        print(json.dumps({"error": "need --new-file or --new-text-stdin", "applied": False}))
        return

    # New page path
    if args.new_page:
        accept, reason = new_page_verdict(new_text)
        result = {
            "page": str(page), "accept": accept, "reason": reason,
            "after": metrics(new_text), "applied": False, "new_page": True,
        }
        if accept:
            page.parent.mkdir(parents=True, exist_ok=True)
            page.write_text(new_text)
            result["applied"] = True
        print(json.dumps(result))
        return

    # Existing page edit path
    if not page.exists():
        print(json.dumps({"error": f"page not found: {page}", "applied": False}))
        return

    old_text = page.read_text()
    before = metrics(old_text)
    after = metrics(new_text)
    accept, reason = verdict(before, after)

    result = {
        "page": str(page), "accept": accept, "reason": reason,
        "before": before, "after": after, "applied": False,
    }
    if accept:
        page.write_text(new_text)
        result["applied"] = True

    print(json.dumps(result))


if __name__ == "__main__":
    main()
