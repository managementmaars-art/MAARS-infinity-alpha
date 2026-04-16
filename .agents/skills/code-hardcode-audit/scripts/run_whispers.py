# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Whispers wrapper for secret/credential detection.

Usage:
    uv run --script run_whispers.py -- <path> [--output {json,text}]

Detects hardcoded secrets, credentials, API keys, and sensitive values.
"""

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path


def _build_whispers_config(target: Path) -> str:
    """Build whispers config YAML with .gitignore-aware exclusions."""
    patterns = [".git/**"]  # Always exclude .git
    gitignore = target / ".gitignore"
    if gitignore.exists():
        for line in gitignore.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and not line.startswith("!"):
                clean = line.rstrip("/")
                if clean:
                    patterns.append(f"{clean}/**")
    lines = ["exclude:", "  files:"]
    for p in patterns:
        lines.append(f'    - "{p}"')
    return "\n".join(lines) + "\n"


def run_whispers(target: Path, output_format: str = "text") -> int:
    """Run Whispers secret detection with .gitignore-aware exclusions."""
    config_yaml = _build_whispers_config(target)
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".yml",
        prefix="whispers_config_",
        delete=False,
    ) as cfg_file:
        cfg_file.write(config_yaml)
        cfg_path = cfg_file.name

    cmd = [
        "whispers",
        str(target),
        "-j",
        "-c",
        cfg_path,
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
        )

        if output_format == "json":
            if result.stdout and result.stdout.strip():
                findings = json.loads(result.stdout)
            else:
                findings = []
            output = {
                "tool": "whispers",
                "rule": "config-secret-detection",
                "total_findings": len(findings),
                "findings": findings,
            }
            print(json.dumps(output, indent=2))
        else:
            if result.stdout and result.stdout.strip():
                findings = json.loads(result.stdout)
                for finding in findings:
                    file_path = finding.get("file", "")
                    line = finding.get("line", "")
                    rule_id = finding.get("rule_id", "")
                    key = finding.get("key", "")
                    value = str(finding.get("value", ""))
                    truncated_value = value[:30] if len(value) > 30 else value
                    print(f"{file_path}:{line}: {rule_id} - {key}={truncated_value} [whispers]")
            if result.stderr:
                for line in result.stderr.splitlines():
                    print(line, file=sys.stderr)

        return 0 if result.returncode in (0, 1) else result.returncode

    except FileNotFoundError:
        print(
            "Error: whispers not found. Install with: uv tool install whispers",
            file=sys.stderr,
        )
        return 1
    except subprocess.TimeoutExpired:
        print(
            "Error: whispers timed out after 120 seconds.",
            file=sys.stderr,
        )
        return 1
    except json.JSONDecodeError as e:
        print(f"Error parsing whispers output: {e}", file=sys.stderr)
        return 1
    finally:
        Path(cfg_path).unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run Whispers secret/credential detection"
    )
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

    return run_whispers(args.path, args.output)


if __name__ == "__main__":
    sys.exit(main())
