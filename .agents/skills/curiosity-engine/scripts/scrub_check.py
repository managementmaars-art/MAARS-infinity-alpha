#!/usr/bin/env python3
"""scrub_check.py — prompt-injection tripwire for curator writes.

Scans a markdown file for known injection markers. Exit 1 if any match.
Intended to run on:
  - wiki pages the agent writes in auto mode (before commit)
  - vault extractions (optional, after fetch)

Scanning only looks at the authored body: frontmatter is ignored and any
<!-- BEGIN FETCHED CONTENT --> ... <!-- END FETCHED CONTENT --> blocks are
stripped before the scan, because those are quarantined data by construction.

Usage:
    scrub_check.py <path.md>
    scrub_check.py --mode wiki <path.md>   # stricter: also bans raw URLs in body
    scrub_check.py --mode vault <path.md>  # marker scan only
"""

import argparse
import json
import re
import sys
from pathlib import Path

MARKERS = [
    (r"ignore\s+(all\s+)?(the\s+)?previous\s+instructions", "ignore-previous-instructions"),
    (r"disregard\s+(all\s+|the\s+)?(previous|above)", "disregard-previous"),
    (r"forget\s+(all\s+|the\s+)?(previous|above)\s+instructions", "forget-previous"),
    (r"new\s+instructions:\s*", "new-instructions"),
    (r"override\s+(your|the)\s+(rules|instructions|schema|policy)", "override-rules"),
    (r"system\s+prompt", "system-prompt-ref"),
    (r"\bSYSTEM:\s", "system-directive"),
    (r"\[INST\]", "chatml-inst"),
    (r"\[/INST\]", "chatml-inst-close"),
    (r"###\s*Instruction", "alpaca-instruction"),
    (r"<\|im_start\|>", "chatml-start"),
    (r"<\|im_end\|>", "chatml-end"),
    (r"<\|system\|>", "chatml-system"),
    (r"<\|assistant\|>", "chatml-assistant"),
    (r"you\s+are\s+now\s+(a|an|the)\s+", "persona-hijack"),
    (r"act\s+as\s+if\s+you\s+are", "persona-hijack-act"),
    (r"pretend\s+(to\s+be|you\s+are)", "persona-hijack-pretend"),
    (r"reveal\s+(your|the)\s+(system\s+)?prompt", "reveal-prompt"),
    (r"exfiltrate|base64\s+encode|curl\s+[^\n]*\|", "exfil-pattern"),
]

URL_IN_BODY = re.compile(r"https?://[^\s)\"'`<>]+")

FETCHED_BLOCK = re.compile(
    r"<!--\s*BEGIN FETCHED CONTENT.*?END FETCHED CONTENT\s*-->",
    flags=re.DOTALL,
)


def strip_frontmatter(text: str) -> str:
    if text.startswith("---\n"):
        end = text.find("\n---\n", 4)
        if end > 0:
            return text[end + 5:]
        end = text.find("\n---", 4)
        if end > 0:
            return text[end + 4:]
    return text


def strip_fetched_blocks(text: str) -> str:
    return FETCHED_BLOCK.sub("", text)


def scan(text: str, mode: str) -> list:
    body = strip_frontmatter(strip_fetched_blocks(text))
    low = body.lower()
    hits: list = []
    for pattern, name in MARKERS:
        if re.search(pattern, low):
            hits.append(name)
    if mode == "wiki":
        urls = URL_IN_BODY.findall(body)
        if urls:
            hits.append(f"url-in-body:{len(urls)}")
    return hits


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("path", type=Path)
    ap.add_argument("--mode", choices=["wiki", "vault"], default="wiki")
    args = ap.parse_args()
    if not args.path.exists():
        print(json.dumps({"path": str(args.path), "error": "missing"}))
        return 2
    text = args.path.read_text()
    hits = scan(text, args.mode)
    print(json.dumps({"path": str(args.path), "mode": args.mode, "hits": hits}))
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main())
