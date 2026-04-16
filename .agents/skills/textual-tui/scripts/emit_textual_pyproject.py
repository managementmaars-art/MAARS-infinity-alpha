#!/usr/bin/env python3
"""Generate a Hatch-based pyproject.toml for a Textual app."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from _textual_skill_utils import load_asset, render_template, write_text_file, json_dumps


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a pyproject.toml for a Textual application."
    )
    parser.add_argument("--project-name", required=True, help="Distribution name, e.g. 'ops-dashboard'.")
    parser.add_argument("--module", required=True, help="Importable module containing the app entry point, e.g. 'ops_dashboard'.")
    parser.add_argument(
        "--command-name",
        default=None,
        help="Console script name (default: project-name).",
    )
    parser.add_argument(
        "--entry-function",
        default="main",
        help="Function exposed as the console entry point (default: main).",
    )
    parser.add_argument(
        "--python-min",
        default="3.9",
        help="Minimum Python version, e.g. 3.9 (default).",
    )
    parser.add_argument(
        "--output",
        default="pyproject.toml",
        help="Output path (default: ./pyproject.toml).",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite the output file if it already exists.",
    )
    return parser.parse_args()


def validate_identifier(text: str, label: str) -> None:
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", text):
        raise ValueError("{0} must be a valid Python identifier.".format(label))


def main() -> int:
    args = parse_args()
    try:
        validate_identifier(args.module, "--module")
        validate_identifier(args.entry_function, "--entry-function")
    except ValueError as error:
        print("Error: {0}".format(error), file=sys.stderr)
        return 2

    command_name = args.command_name or args.project_name
    replacements = {
        "PROJECT_NAME": args.project_name,
        "MODULE": args.module,
        "COMMAND_NAME": command_name,
        "ENTRY_FUNCTION": args.entry_function,
        "PYTHON_MIN": args.python_min,
    }
    content = render_template(
        load_asset("project", "pyproject.toml.tmpl"),
        replacements,
    )
    output = Path(args.output).expanduser().resolve()
    try:
        write_text_file(output, content, force=args.force)
    except FileExistsError as error:
        print("Error: {0}".format(error), file=sys.stderr)
        return 2

    print(
        json_dumps(
            {
                "written_file": str(output),
                "project_name": args.project_name,
                "command_name": command_name,
                "module": args.module,
                "entry_function": args.entry_function,
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
