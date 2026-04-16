#!/usr/bin/env python3
"""Generate starter Textual apps from bundled templates."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from _textual_skill_utils import (
    SKILL_ROOT,
    json_dumps,
    load_asset,
    render_template,
    write_text_file,
)

TEMPLATES = {
    "dashboard": "dashboard",
    "form": "form",
    "chat": "chat",
    "data-explorer": "data_explorer",
    "file-browser": "file_browser",
    "settings": "settings",
    "wizard": "wizard",
    "log-monitor": "log_monitor",
    "editor": "editor",
    "admin-modes": "admin_modes",
    "download-demo": "download_demo",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a starter Textual app, matching TCSS, tests, and optional project files."
    )
    parser.add_argument(
        "--template",
        choices=sorted(TEMPLATES),
        help="Starter archetype to generate.",
    )
    parser.add_argument(
        "--list-templates",
        action="store_true",
        help="Print the available templates and exit.",
    )
    parser.add_argument(
        "--module",
        help="Python module/file stem to generate, e.g. 'my_app'.",
    )
    parser.add_argument(
        "--class-name",
        help="App class name, e.g. 'MyApp'.",
    )
    parser.add_argument(
        "--app-title",
        help="Human-readable title shown in the UI.",
    )
    parser.add_argument(
        "--output-dir",
        default=".",
        help="Directory to write generated files into (default: current directory).",
    )
    parser.add_argument(
        "--project-name",
        default=None,
        help="Optional distribution/project name used when generating pyproject files.",
    )
    parser.add_argument(
        "--command-name",
        default=None,
        help="Optional console command name used when generating pyproject files.",
    )
    parser.add_argument(
        "--python-min",
        default="3.9",
        help="Minimum Python version for generated pyproject files (default: 3.9).",
    )
    parser.add_argument(
        "--no-tests",
        action="store_true",
        help="Skip generating the test file.",
    )
    parser.add_argument(
        "--with-pyproject",
        action="store_true",
        help="Also generate a Hatch-based pyproject.toml.",
    )
    parser.add_argument(
        "--with-ci",
        action="store_true",
        help="Also generate a GitHub Actions workflow.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing files if they already exist.",
    )
    return parser.parse_args()


def validate_module_name(module: str) -> None:
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", module):
        raise ValueError("--module must be a valid Python module/file stem, e.g. 'my_app'.")


def validate_class_name(class_name: str) -> None:
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", class_name):
        raise ValueError("--class-name must be a valid Python class name, e.g. 'MyApp'.")


def validate_required_args(args: argparse.Namespace) -> None:
    if args.list_templates:
        return
    missing = [name for name in ("template", "module", "class_name", "app_title") if getattr(args, name) in (None, "")]
    if missing:
        raise ValueError("Missing required arguments: {0}".format(", ".join("--" + item.replace("_", "-") for item in missing)))
    validate_module_name(args.module)
    validate_class_name(args.class_name)


def template_path(stem: str, suffix: str) -> str:
    return "templates/{0}_{1}".format(stem, suffix)


def main() -> int:
    args = parse_args()
    if args.list_templates:
        print(json.dumps(sorted(TEMPLATES.keys()), indent=2))
        return 0

    try:
        validate_required_args(args)
    except ValueError as error:
        print("Error: {0}".format(error), file=sys.stderr)
        return 2

    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    template_stem = TEMPLATES[args.template]
    replacements = {
        "MODULE": args.module,
        "CLASS_NAME": args.class_name,
        "APP_TITLE": args.app_title,
        "PROJECT_NAME": args.project_name or args.module.replace("_", "-"),
        "COMMAND_NAME": args.command_name or (args.project_name or args.module.replace("_", "-")),
        "PYTHON_MIN": args.python_min,
        "ENTRY_FUNCTION": "main",
        "PYTHON_VERSIONS_JSON": "[" + ", ".join('"{0}"'.format(item) for item in sorted({args.python_min, "3.10", "3.11", "3.12"})) + "]",
        "INSTALL_COMMAND": "python -m pip install -e .[dev]",
        "PYTEST_COMMAND": "pytest",
    }

    try:
        app_content = render_template(load_asset(*template_path(template_stem, "app.py.tmpl").split("/")), replacements)
        css_content = render_template(load_asset(*template_path(template_stem, "tcss.tmpl").split("/")), replacements)
        test_content = render_template(load_asset(*template_path(template_stem, "test.py.tmpl").split("/")), replacements)
    except FileNotFoundError as error:
        print("Error: missing bundled template: {0}".format(error), file=sys.stderr)
        return 1
    except KeyError as error:
        print("Error: {0}".format(error), file=sys.stderr)
        return 1

    written = []
    app_path = output_dir / "{0}.py".format(args.module)
    css_path = output_dir / "{0}.tcss".format(args.module)
    test_path = output_dir / "tests" / "test_{0}.py".format(args.module)

    try:
        write_text_file(app_path, app_content, force=args.force)
        written.append(str(app_path))
        write_text_file(css_path, css_content, force=args.force)
        written.append(str(css_path))
        if not args.no_tests:
            write_text_file(test_path, test_content, force=args.force)
            written.append(str(test_path))

        if args.with_pyproject:
            pyproject_content = render_template(load_asset("project", "pyproject.toml.tmpl"), replacements)
            pyproject_path = output_dir / "pyproject.toml"
            write_text_file(pyproject_path, pyproject_content, force=args.force)
            written.append(str(pyproject_path))

        if args.with_ci:
            ci_content = render_template(load_asset("project", "github-actions-ci.yml.tmpl"), replacements)
            ci_path = output_dir / ".github" / "workflows" / "textual-tests.yml"
            write_text_file(ci_path, ci_content, force=args.force)
            written.append(str(ci_path))
    except FileExistsError as error:
        print("Error: {0}".format(error), file=sys.stderr)
        return 2

    summary = {
        "template": args.template,
        "module": args.module,
        "class_name": args.class_name,
        "app_title": args.app_title,
        "output_dir": str(output_dir),
        "written_files": written,
        "next_steps": [
            "Run the app with: python {0}.py".format(args.module),
            "Iterate with: textual run --dev {0}.py".format(args.module),
            "Generate a project audit later with: python scripts/audit_textual_project.py .",
        ],
    }
    print(json_dumps(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
