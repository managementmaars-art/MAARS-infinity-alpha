# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Bandit hardcoded password/secret detection wrapper.

Usage:
    uv run --script run_bandit.py -- <path> [--output {json,text}]

Detects hardcoded passwords and secrets (B105, B106, B107) in Python code.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path


def _gitignore_excludes(target: Path) -> list[str]:
    """Read .gitignore and return exclude paths for bandit."""
    gitignore = target / ".gitignore"
    excludes = [str(target / ".venv")]  # Always exclude .venv
    if gitignore.exists():
        for line in gitignore.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            # Convert gitignore patterns to absolute paths for bandit
            clean = line.rstrip("/")
            if clean:
                excludes.append(str(target / clean))
    return excludes


def run_bandit(target: Path, output_format: str = "text") -> int:
    """Run Bandit B105/B106/B107 check."""
    excludes = _gitignore_excludes(target)
    cmd = [
        "bandit",
        "-r",
        str(target),
        "-t",
        "B105,B106,B107",
        "-f",
        "json",
        "--exclude",
        ",".join(excludes),
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

        # Bandit returns exit code 1 when findings exist — not an error
        raw = result.stdout or ""

        # Bandit JSON output may have a non-JSON prefix; find the first `{`
        brace_index = raw.find("{")
        if brace_index == -1:
            if output_format == "json":
                output = {
                    "tool": "bandit",
                    "rule": "B105-B107",
                    "total_findings": 0,
                    "findings": [],
                }
                print(json.dumps(output, indent=2))
            if result.stderr:
                print(result.stderr, file=sys.stderr)
            return 0

        json_text = raw[brace_index:]
        data = json.loads(json_text)
        results = data.get("results", [])

        if output_format == "json":
            output = {
                "tool": "bandit",
                "rule": "B105-B107",
                "total_findings": len(results),
                "findings": results,
            }
            print(json.dumps(output, indent=2))
        else:
            for finding in results:
                filename = finding.get("filename", "")
                line_number = finding.get("line_number", 0)
                test_id = finding.get("test_id", "")
                issue_text = finding.get("issue_text", "")
                print(f"{filename}:{line_number}: {test_id} - {issue_text} [bandit]")
            if result.stderr:
                print(result.stderr, file=sys.stderr)

        return 0 if not results else result.returncode

    except FileNotFoundError:
        print("Error: bandit not found. Install with: uv tool install bandit", file=sys.stderr)
        return 1
    except subprocess.TimeoutExpired:
        print("Error: bandit timed out after 120 seconds", file=sys.stderr)
        return 1
    except json.JSONDecodeError as e:
        print(f"Error parsing bandit output: {e}", file=sys.stderr)
        return 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Bandit hardcoded secret detection")
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

    return run_bandit(args.path, args.output)


if __name__ == "__main__":
    sys.exit(main())
