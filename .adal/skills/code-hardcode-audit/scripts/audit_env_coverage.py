# /// script
# requires-python = ">=3.13"
# dependencies = []
# ///
"""Env-var coverage audit: cross-reference pydantic BaseSettings vs bare constants.

Usage:
    uv run --python 3.13 --script audit_env_coverage.py -- <path> [--output {json,text}]

Finds module-level constants and inline literals that lack env-var backing
via pydantic BaseSettings. Reports coverage gaps.
"""

import argparse
import ast
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

# Patterns for inline keyword args that should be configurable
CONFIGURABLE_KWARGS = frozenset({
    "timeout", "max_retries", "retries", "attempts", "max_attempts",
    "delay", "backoff", "interval", "port", "batch_size", "chunk_size",
    "limit", "max_results", "page_size", "threshold", "max_failures",
    "workers", "max_workers", "ttl", "budget", "cooldown",
    "blocking_timeout", "lock_timeout", "recovery_timeout",
    "failure_threshold",
})

ALL_CAPS_RE = re.compile(r"^[A-Z][A-Z0-9_]{2,}$")


@dataclass
class SettingsField:
    """A field from a pydantic BaseSettings class."""

    class_name: str
    field_name: str
    file: str
    line: int


@dataclass
class BareConstant:
    """A module-level ALL_CAPS constant with a literal value."""

    name: str
    value: str
    file: str
    line: int


@dataclass
class InlineLiteral:
    """A numeric literal in a configurable keyword argument."""

    kwarg: str
    value: str
    file: str
    line: int
    func_name: str = ""


def _extract_settings_fields(tree: ast.Module, filepath: str) -> list[SettingsField]:
    """Find all fields in BaseSettings subclasses."""
    fields = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        # Check if any base is BaseSettings (simple name check)
        is_settings = any(
            (isinstance(b, ast.Name) and b.id == "BaseSettings")
            or (isinstance(b, ast.Attribute) and b.attr == "BaseSettings")
            for b in node.bases
        )
        if not is_settings:
            continue
        for item in node.body:
            if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                fields.append(SettingsField(
                    class_name=node.name,
                    field_name=item.target.id,
                    file=filepath,
                    line=item.lineno,
                ))
            elif isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        fields.append(SettingsField(
                            class_name=node.name,
                            field_name=target.id,
                            file=filepath,
                            line=item.lineno,
                        ))
    return fields


def _extract_bare_constants(tree: ast.Module, filepath: str) -> list[BareConstant]:
    """Find module-level ALL_CAPS = literal assignments."""
    constants = []
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if not isinstance(target, ast.Name):
                continue
            if not ALL_CAPS_RE.match(target.id):
                continue
            if isinstance(node.value, ast.Constant):
                constants.append(BareConstant(
                    name=target.id,
                    value=repr(node.value.value),
                    file=filepath,
                    line=node.lineno,
                ))
    return constants


def _extract_inline_literals(tree: ast.Module, filepath: str) -> list[InlineLiteral]:
    """Find numeric literals in configurable keyword arguments."""
    literals = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func_name = ""
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            func_name = node.func.attr

        for kw in node.keywords:
            if kw.arg and kw.arg.lower() in CONFIGURABLE_KWARGS:
                if isinstance(kw.value, ast.Constant) and isinstance(kw.value.value, (int, float)):
                    literals.append(InlineLiteral(
                        kwarg=kw.arg,
                        value=repr(kw.value.value),
                        file=filepath,
                        line=kw.value.lineno,
                        func_name=func_name,
                    ))
    return literals


def audit_env_coverage(target: Path, output_format: str = "text") -> int:
    """Scan Python files and report env-var coverage gaps."""
    all_settings: list[SettingsField] = []
    all_constants: list[BareConstant] = []
    all_literals: list[InlineLiteral] = []

    # Collect all .py files
    if target.is_file():
        py_files = [target] if target.suffix == ".py" else []
    else:
        py_files = sorted(target.rglob("*.py"))

    for py_file in py_files:
        try:
            source = py_file.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(py_file))
        except (SyntaxError, UnicodeDecodeError):
            continue

        rel = str(py_file)
        all_settings.extend(_extract_settings_fields(tree, rel))
        all_constants.extend(_extract_bare_constants(tree, rel))
        all_literals.extend(_extract_inline_literals(tree, rel))

    # Build set of env-backed field names (case-insensitive)
    env_backed = {f.field_name.lower() for f in all_settings}

    # Classify constants
    findings = []
    finding_id = 0

    for const in all_constants:
        name_lower = const.name.lower()
        # Strip common prefixes for matching (_DEFAULT_, _MAX_, etc.)
        stripped = re.sub(r"^_?(DEFAULT_|MAX_|MIN_)?", "", name_lower)
        has_backing = name_lower in env_backed or stripped in env_backed
        if not has_backing:
            finding_id += 1
            findings.append({
                "id": f"ENVCOV-{finding_id:03d}",
                "tool": "env-coverage",
                "rule": "constant-no-env-backing",
                "file": const.file,
                "line": const.line,
                "column": 0,
                "end_line": None,
                "message": f"Constant {const.name}={const.value} has no BaseSettings env-var override",
                "severity": "medium",
                "suggested_fix": f"Add {const.name.lower()} field to a BaseSettings class",
            })

    for lit in all_literals:
        finding_id += 1
        ctx = f" in {lit.func_name}()" if lit.func_name else ""
        findings.append({
            "id": f"ENVCOV-{finding_id:03d}",
            "tool": "env-coverage",
            "rule": "inline-literal",
            "file": lit.file,
            "line": lit.line,
            "column": 0,
            "end_line": None,
            "message": f"Inline literal {lit.kwarg}={lit.value}{ctx} — extract to named constant",
            "severity": "high",
            "suggested_fix": f"Create {lit.kwarg.upper()} constant or add to BaseSettings",
        })

    # Sort by file, line
    findings.sort(key=lambda f: (f["file"], f["line"]))

    if output_format == "json":
        by_rule: dict[str, int] = {}
        for f in findings:
            by_rule[f["rule"]] = by_rule.get(f["rule"], 0) + 1
        output = {
            "tool": "env-coverage",
            "summary": {
                "total_settings_classes": len({f.class_name for f in all_settings}),
                "total_settings_fields": len(all_settings),
                "total_bare_constants": len(all_constants),
                "total_inline_literals": len(all_literals),
                "total_findings": len(findings),
                "by_rule": by_rule,
            },
            "findings": findings,
        }
        print(json.dumps(output, indent=2))
    else:
        if not findings:
            print("No env-var coverage gaps detected")
            print(f"  BaseSettings classes: {len({f.class_name for f in all_settings})}")
            print(f"  Env-backed fields: {len(all_settings)}")
            print(f"  Module constants: {len(all_constants)}")
        else:
            for f in findings:
                print(f"{f['file']}:{f['line']}: {f['rule']} {f['message']} [env-coverage]")
            print(f"\nSummary: {len(findings)} coverage gap(s)")
            print(f"  BaseSettings fields: {len(all_settings)}")
            print(f"  Bare constants without env backing: {sum(1 for f in findings if f['rule'] == 'constant-no-env-backing')}")
            print(f"  Inline literals: {sum(1 for f in findings if f['rule'] == 'inline-literal')}")

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit env-var coverage for Python constants")
    parser.add_argument("path", type=Path, help="Path to audit")
    parser.add_argument(
        "--output",
        choices=["json", "text"],
        default="text",
        help="Output format",
    )
    # uv run --script <file> -- <args> passes literal '--' to the script
    argv = [a for a in sys.argv[1:] if a != "--"]
    args = parser.parse_args(argv)

    if not args.path.exists():
        print(f"Error: Path does not exist: {args.path}", file=sys.stderr)
        return 1

    return audit_env_coverage(args.path, args.output)


if __name__ == "__main__":
    sys.exit(main())
