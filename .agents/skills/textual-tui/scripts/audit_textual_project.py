#!/usr/bin/env python3
"""Audit a Textual project for architecture, performance, and testing issues."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List

from _textual_skill_utils import json_dumps, scan_project


def add_finding(findings: List[Dict[str, object]], severity: str, title: str, evidence: List[str], recommendation: str) -> None:
    findings.append(
        {
            "severity": severity,
            "title": title,
            "evidence": evidence,
            "recommendation": recommendation,
        }
    )


def audit(project_root: Path) -> Dict[str, object]:
    project = scan_project(project_root)
    findings: List[Dict[str, object]] = []

    files = project["files"]
    apps = project["apps"]
    widget_usage = {item["widget"]: item["count"] for item in project["widget_usage"]}

    if not project["textual_detected"]:
        add_finding(
            findings,
            "error",
            "No Textual project detected",
            ["No Textual app classes, widget imports, or `.tcss` files were found."],
            "Confirm the project root is correct or add Textual-specific files before using this audit.",
        )
        return {
            "project_root": project["project_root"],
            "textual_detected": False,
            "findings": findings,
            "summary": {"errors": 1, "warnings": 0, "info": 0},
        }

    if not project["tests"]:
        add_finding(
            findings,
            "warning",
            "No Textual tests detected",
            ["No files under `tests/` appeared to use `run_test()` or `Pilot`."],
            "Add at least a smoke test and one interaction test using `run_test()` and `Pilot`.",
        )

    if not project["stylesheets"]:
        inline_css_apps = []
        for file_scan in files:
            for app_class in file_scan["app_classes"]:
                if app_class["css_paths"]:
                    continue
                for class_record in file_scan["classes"]:
                    if class_record["name"] == app_class["name"]:
                        inline_css_apps.append("{0}:{1}".format(file_scan["path"], app_class["name"]))
        if inline_css_apps:
            add_finding(
                findings,
                "info",
                "No external TCSS files detected",
                inline_css_apps[:5],
                "Keep inline `CSS` for toy apps only. Move styling into `.tcss` once layout or theming grows beyond a handful of rules.",
            )

    for file_scan in files:
        for app_class in file_scan["app_classes"]:
            actions = app_class["methods"]["actions"]
            handlers = app_class["methods"]["handlers"]
            total_methods = len(actions) + len(handlers)
            if app_class["span"] >= 250 or total_methods >= 12:
                add_finding(
                    findings,
                    "warning",
                    "Large App class likely needs extraction",
                    [
                        "{0}:{1} spans {2} lines with {3} actions/handlers.".format(
                            file_scan["path"], app_class["name"], app_class["span"], total_methods
                        )
                    ],
                    "Split screen-specific logic into `Screen` classes and reusable widgets. Keep the `App` focused on orchestration.",
                )

            if app_class["bindings"] and len(app_class["bindings"]) >= 7 and not file_scan["uses"]["command_palette"]:
                add_finding(
                    findings,
                    "info",
                    "Many bindings but no command palette integration",
                    [
                        "{0}:{1} defines {2} bindings.".format(
                            file_scan["path"], app_class["name"], len(app_class["bindings"])
                        )
                    ],
                    "Add app-level or screen-level `COMMANDS` providers so features remain discoverable beyond the footer.",
                )

            if app_class["modes"] and not app_class["screens"]:
                add_finding(
                    findings,
                    "info",
                    "Modes configured without named screens",
                    [
                        "{0}:{1} defines MODES={2}.".format(
                            file_scan["path"], app_class["name"], sorted(app_class["modes"].keys())
                        )
                    ],
                    "This can be valid, but named screens in `SCREENS` often make navigation and testing easier when the mode stack grows.",
                )

            if (
                (widget_usage.get("DataTable", 0) or widget_usage.get("DirectoryTree", 0))
                and not app_class["breakpoints"]
                and not file_scan["uses"]["breakpoints"]
            ):
                add_finding(
                    findings,
                    "info",
                    "Explorer-style layout has no responsive breakpoints",
                    [
                        "{0}:{1} uses data/browser widgets without `HORIZONTAL_BREAKPOINTS` or `VERTICAL_BREAKPOINTS`.".format(
                            file_scan["path"], app_class["name"]
                        )
                    ],
                    "Use breakpoint classes so the layout degrades gracefully on narrow terminals and in the browser.",
                )

    for file_scan in files:
        blocking = file_scan["handler_blocking_calls"]
        if blocking:
            evidence = []
            for handler_name, calls in sorted(blocking.items()):
                evidence.append("{0}:{1} calls {2}".format(file_scan["path"], handler_name, ", ".join(calls)))
            add_finding(
                findings,
                "warning",
                "Potentially blocking work in handlers",
                evidence[:10],
                "Move network, subprocess, or sleep-heavy logic out of `on_*` / `action_*` handlers into `@work` or `run_worker(...)`.",
            )

        for class_record in file_scan["classes"]:
            computes = class_record["methods"]["computes"]
            if computes:
                add_finding(
                    findings,
                    "info",
                    "Compute methods present",
                    [
                        "{0}:{1} defines {2}".format(file_scan["path"], class_record["name"], ", ".join(computes))
                    ],
                    "Keep `compute_*` methods fast and side-effect free; move I/O or heavy work elsewhere.",
                )

    manual_table_files = []
    for file_scan in files:
        rich_imports = set(file_scan["imports"]["rich"])
        if rich_imports and not file_scan["imports"]["widgets"]:
            continue
        if "Table" in rich_imports and widget_usage.get("DataTable", 0) == 0:
            manual_table_files.append(file_scan["path"])
    if manual_table_files:
        add_finding(
            findings,
            "info",
            "Manual Rich tables may be a missed DataTable opportunity",
            manual_table_files[:5],
            "If the table needs focus, sorting, cursoring, or row selection, prefer `DataTable` over manual Rich tables inside `Static`.",
        )

    export_like_files = []
    for file_scan in files:
        path_lower = file_scan["path"].lower()
        text_flags = file_scan["uses"]
        if any(token in path_lower for token in ("export", "report", "download", "share")) and not text_flags["deliver"]:
            export_like_files.append(file_scan["path"])
    if export_like_files:
        add_finding(
            findings,
            "info",
            "Export-like flows without delivery APIs",
            export_like_files[:5],
            "If the app may be served in a browser, prefer `deliver_text`, `deliver_binary`, or `deliver_screenshot` instead of assuming local file-system access.",
        )

    info_count = sum(1 for finding in findings if finding["severity"] == "info")
    warning_count = sum(1 for finding in findings if finding["severity"] == "warning")
    error_count = sum(1 for finding in findings if finding["severity"] == "error")

    next_steps = [
        "Run `python scripts/inspect_textual_project.py .` to see the raw project inventory.",
        "Refactor any blocking handlers into workers before adding polish.",
        "Leave behind Pilot tests whenever behaviour changes.",
    ]

    return {
        "project_root": project["project_root"],
        "textual_detected": True,
        "apps": apps,
        "findings": findings,
        "summary": {
            "errors": error_count,
            "warnings": warning_count,
            "info": info_count,
            "total": len(findings),
        },
        "next_steps": next_steps,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit a Textual project for likely architecture, performance, and testing issues."
    )
    parser.add_argument(
        "project_root",
        nargs="?",
        default=".",
        help="Project directory to audit (default: current directory).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON only.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    project_root = Path(args.project_root).expanduser().resolve()
    if not project_root.exists():
        print("Error: project root does not exist: {0}".format(project_root), file=sys.stderr)
        return 2
    report = audit(project_root)
    if args.json:
        print(json_dumps(report))
        return 0

    print("# Textual project audit")
    print()
    print("Project: {0}".format(report["project_root"]))
    print("Apps: {0}".format(len(report["apps"])))
    print(
        "Findings: {0} total ({1} errors, {2} warnings, {3} info)".format(
            report["summary"]["total"],
            report["summary"]["errors"],
            report["summary"]["warnings"],
            report["summary"]["info"],
        )
    )
    print()

    if not report["findings"]:
        print("No issues detected by the heuristic audit.")
        return 0

    for finding in report["findings"]:
        print("## [{0}] {1}".format(finding["severity"].upper(), finding["title"]))
        for line in finding["evidence"]:
            print("- {0}".format(line))
        print("Recommendation: {0}".format(finding["recommendation"]))
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
