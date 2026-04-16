#!/usr/bin/env python3
"""Generate a GitHub Actions workflow for a Textual project."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from _textual_skill_utils import load_asset, render_template, write_text_file, json_dumps


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a GitHub Actions workflow for Textual tests."
    )
    parser.add_argument(
        "--python-versions",
        nargs="+",
        default=["3.10", "3.11", "3.12"],
        help="Python versions for the CI matrix (default: 3.10 3.11 3.12).",
    )
    parser.add_argument(
        "--install-command",
        default="python -m pip install -e .[dev]",
        help="Command used to install project dependencies in CI.",
    )
    parser.add_argument(
        "--pytest-command",
        default="pytest",
        help="Command used to execute the test suite in CI.",
    )
    parser.add_argument(
        "--output",
        default=".github/workflows/textual-tests.yml",
        help="Output workflow path.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite the workflow if it already exists.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    replacements = {
        "PYTHON_VERSIONS_JSON": "[" + ", ".join('"{0}"'.format(item) for item in args.python_versions) + "]",
        "INSTALL_COMMAND": args.install_command,
        "PYTEST_COMMAND": args.pytest_command,
    }
    content = render_template(
        load_asset("project", "github-actions-ci.yml.tmpl"),
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
                "python_versions": args.python_versions,
                "install_command": args.install_command,
                "pytest_command": args.pytest_command,
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
