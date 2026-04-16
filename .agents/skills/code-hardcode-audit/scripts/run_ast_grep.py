# /// script
# requires-python = ">=3.13"
# dependencies = []
# ///
"""ast-grep wrapper for AST-based hardcode detection.

Usage:
    uv run --python 3.13 --script run_ast_grep.py -- <path> [--output {json,text}]

Detects hardcoded literals in assignments, function arguments, return values,
URLs, and file paths using AST pattern matching (not regex).
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

RULES_DIR = Path(__file__).parent.parent / "assets" / "ast-grep-hardcode"
TIMEOUT = int(os.environ.get("AUDIT_ASTGREP_TIMEOUT", "60"))


def _find_sg_binary() -> str | None:
    """Find ast-grep binary (sg or ast-grep)."""
    for name in ("sg", "ast-grep"):
        if shutil.which(name):
            return name
    return None


def run_ast_grep(target: Path, output_format: str = "text") -> int:
    """Run ast-grep with hardcode detection rules."""
    sg = _find_sg_binary()
    if not sg:
        print("Error: ast-grep not found. Install with: cargo install ast-grep", file=sys.stderr)
        return 1

    if not RULES_DIR.exists():
        print(f"Error: ast-grep rules not found: {RULES_DIR}", file=sys.stderr)
        return 1

    cmd = [sg, "scan", str(target.resolve()), "--json=stream"]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=TIMEOUT,
            cwd=str(RULES_DIR),
        )

        # Parse NDJSON (one JSON object per line)
        findings = []
        if result.stdout.strip():
            for line in result.stdout.strip().splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    item = json.loads(line)
                    findings.append(item)
                except json.JSONDecodeError:
                    continue

        if output_format == "json":
            severity_map = {"error": "high", "warning": "medium", "hint": "low", "info": "low"}
            output_findings = []
            for i, item in enumerate(findings):
                output_findings.append({
                    "id": f"ASTGREP-{i + 1:03d}",
                    "tool": "ast-grep",
                    "rule": item.get("ruleId", "unknown"),
                    "file": item.get("file", ""),
                    "line": item.get("range", {}).get("start", {}).get("line", 0),
                    "column": item.get("range", {}).get("start", {}).get("column", 0),
                    "end_line": item.get("range", {}).get("end", {}).get("line"),
                    "message": item.get("message", ""),
                    "severity": severity_map.get(item.get("severity", "warning"), "medium"),
                    "suggested_fix": item.get("note", ""),
                })
            output = {
                "tool": "ast-grep",
                "rules_dir": str(RULES_DIR),
                "total_findings": len(output_findings),
                "findings": output_findings,
            }
            print(json.dumps(output, indent=2))
        else:
            if not findings:
                print("No hardcode patterns detected (ast-grep)")
            else:
                for item in findings:
                    file = item.get("file", "?")
                    line = item.get("range", {}).get("start", {}).get("line", 0)
                    rule = item.get("ruleId", "unknown")
                    msg = item.get("message", "")
                    print(f"{file}:{line}: {rule} {msg} [ast-grep]")
                print(f"\nTotal: {len(findings)} finding(s)")

        return 0

    except FileNotFoundError:
        print("Error: ast-grep not found. Install with: cargo install ast-grep", file=sys.stderr)
        return 1
    except subprocess.TimeoutExpired:
        print(f"Error: ast-grep timed out after {TIMEOUT} seconds", file=sys.stderr)
        return 1
    except json.JSONDecodeError as e:
        print(f"Error parsing ast-grep output: {e}", file=sys.stderr)
        return 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Run ast-grep AST-based hardcode detection")
    parser.add_argument("path", type=Path, help="Path to check")
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

    return run_ast_grep(args.path, args.output)


if __name__ == "__main__":
    sys.exit(main())
