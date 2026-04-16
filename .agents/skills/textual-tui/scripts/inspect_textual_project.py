#!/usr/bin/env python3
"""Inspect a Python project and summarise Textual-related structure as JSON."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from _textual_skill_utils import json_dumps, scan_project


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Inspect a Python project and summarise Textual apps, widgets, TCSS files, tests, and dependencies as JSON."
    )
    parser.add_argument(
        "project_root",
        nargs="?",
        default=".",
        help="Project directory to inspect (default: current directory).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    project_root = Path(args.project_root).expanduser().resolve()
    if not project_root.exists():
        print("Error: project root does not exist: {0}".format(project_root), file=sys.stderr)
        return 2
    if not project_root.is_dir():
        print("Error: project root is not a directory: {0}".format(project_root), file=sys.stderr)
        return 2
    summary = scan_project(project_root)
    print(json_dumps(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
