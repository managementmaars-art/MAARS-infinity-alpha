#!/usr/bin/env python3
"""Validate the skill package by scaffolding templates and compiling generated code."""

from __future__ import annotations

import py_compile
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

TEMPLATES = [
    "dashboard",
    "form",
    "chat",
    "data-explorer",
    "file-browser",
    "settings",
    "wizard",
    "log-monitor",
    "editor",
    "admin-modes",
    "download-demo",
]


def compile_python_files(paths):
    for path in paths:
        py_compile.compile(str(path), doraise=True)


def main() -> int:
    skill_root = Path(__file__).resolve().parents[1]
    scripts_dir = skill_root / "scripts"

    try:
        compile_python_files(path for path in scripts_dir.glob("*.py"))
    except Exception as error:
        print("Script compilation failed: {0}".format(error), file=sys.stderr)
        return 1

    temp_root = Path(tempfile.mkdtemp(prefix="textual-skill-check-"))
    try:
        for template in TEMPLATES:
            module = template.replace("-", "_")
            class_name = "".join(part.title() for part in module.split("_")) + "App"
            output_dir = temp_root / template
            command = [
                sys.executable,
                str(scripts_dir / "scaffold_textual_app.py"),
                "--template",
                template,
                "--module",
                module,
                "--class-name",
                class_name,
                "--app-title",
                template.replace("-", " ").title(),
                "--output-dir",
                str(output_dir),
                "--force",
                "--with-pyproject",
                "--with-ci",
            ]
            subprocess.run(command, check=True, cwd=str(skill_root))
            compile_python_files(output_dir.rglob("*.py"))
    except Exception as error:
        print("Self-check failed: {0}".format(error), file=sys.stderr)
        return 1
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)

    print("Self-check passed for scripts and all templates.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
