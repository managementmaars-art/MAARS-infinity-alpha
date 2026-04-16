#!/usr/bin/env python3
"""Report the most frequently touched files in recent git history."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path


def run_git_log(repo: Path, days: int) -> str:
    cmd = [
        "git",
        "log",
        f"--since={days}.days",
        "--name-only",
        "--pretty=format:",
        "--no-merges",
    ]
    result = subprocess.run(
        cmd,
        cwd=repo,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "git log failed")
    return result.stdout


def collect_hotspots(log_output: str, limit: int) -> list[dict[str, int | str]]:
    counts: Counter[str] = Counter()
    for line in log_output.splitlines():
        path = line.strip()
        if not path:
            continue
        counts[path] += 1
    return [
        {"path": path, "change_count": count}
        for path, count in counts.most_common(limit)
    ]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Find recently touched git files by change frequency."
    )
    parser.add_argument(
        "--repo",
        default=".",
        help="Path to the git repository. Defaults to the current directory.",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="How many days of history to inspect. Defaults to 30.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=5,
        help="How many files to return. Defaults to 5.",
    )
    parser.add_argument(
        "--output",
        help="Optional path to save the JSON result.",
    )
    args = parser.parse_args()

    repo = Path(args.repo).resolve()
    try:
        log_output = run_git_log(repo, args.days)
        hotspots = collect_hotspots(log_output, args.limit)
    except Exception as exc:  # pragma: no cover
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 1

    payload = {
        "repo": str(repo),
        "days": args.days,
        "limit": args.limit,
        "files": hotspots,
    }

    output_text = json.dumps(payload, indent=2)
    if args.output:
        Path(args.output).write_text(output_text + "\n", encoding="utf-8")
    else:
        print(output_text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
