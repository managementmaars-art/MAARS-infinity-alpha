# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Trufflehog wrapper for secret detection.

Usage:
    uv run --script run_trufflehog.py -- <path> [--output {json,text}]

Examples:
    uv run --script run_trufflehog.py -- src/
    uv run --script run_trufflehog.py -- . --output json
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

# Always exclude these (even if not in .gitignore)
_ALWAYS_EXCLUDE = [".git"]


def run_trufflehog(target: Path, output_format: str = "text") -> int:
    """Run trufflehog on target directory.

    Args:
        target: Directory to scan
        output_format: Output format (json or text)

    Returns:
        Exit code (0 = no secrets or findings present, 1 = error)
    """
    # Build exclude patterns from .gitignore + always-exclude
    # NOTE: trufflehog --exclude-paths expects REGEX, not globs
    patterns = list(_ALWAYS_EXCLUDE)
    gitignore = target / ".gitignore"
    if gitignore.exists():
        for line in gitignore.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("!"):
                continue
            clean = line.rstrip("/")
            # Skip complex globs that can't be trivially converted to regex
            if any(c in clean for c in ("*", "?", "[", "{")):
                continue
            # Simple directory/file names become regex patterns
            if clean:
                patterns.append(clean)

    # Write exclude patterns to a temp file (trufflehog --exclude-paths expects a file)
    exclude_file = tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False, prefix="trufflehog-exclude-"
    )
    try:
        exclude_file.write("\n".join(patterns) + "\n")
        exclude_file.close()

        cmd = [
            "trufflehog",
            "filesystem",
            str(target),
            "--json",
            "--no-update",
            "--exclude-paths",
            exclude_file.name,
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

        # trufflehog exit code 0 = success (findings may or may not exist);
        # check stdout for NDJSON lines to determine if secrets were found.
        if result.returncode != 0:
            print(
                f"trufflehog error (exit {result.returncode}): {result.stderr}",
                file=sys.stderr,
            )
            return result.returncode

        # Parse NDJSON output (one JSON object per line)
        findings = []
        for line in result.stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue

            # Extract fields from trufflehog NDJSON structure
            source_meta = obj.get("SourceMetadata", {})
            fs_data = source_meta.get("Data", {}).get("Filesystem", {})
            file_path = fs_data.get("file", "unknown")
            line_num = fs_data.get("line", 0)
            detector_name = obj.get("DetectorName", "unknown")
            verified = obj.get("Verified", False)
            raw = obj.get("Raw", "")[:30]  # Truncate to 30 chars for safety
            description = obj.get("DetectorDescription", "")

            findings.append(
                {
                    "file": file_path,
                    "line": line_num,
                    "detector": detector_name,
                    "verified": verified,
                    "raw_truncated": raw,
                    "description": description,
                }
            )

        if output_format == "json":
            output = {
                "tool": "trufflehog",
                "rule": "secret-detection-entropy",
                "total_findings": len(findings),
                "findings": findings,
            }
            print(json.dumps(output, indent=2))
        else:
            if not findings:
                print("No secrets detected")
            else:
                for f in findings:
                    verified_label = "verified" if f["verified"] else "unverified"
                    description = f["description"]
                    desc_part = f" - {description}" if description else ""
                    print(
                        f"{f['file']}:{f['line']}: {f['detector']}"
                        f" ({verified_label}){desc_part} [trufflehog]"
                    )
                print(f"\nTotal: {len(findings)} secret(s) detected")
            return 1 if findings else 0

        return 1 if findings else 0

    except FileNotFoundError:
        print(
            "Error: trufflehog not found. Install with: brew install trufflehog",
            file=sys.stderr,
        )
        return 1
    except subprocess.TimeoutExpired:
        print("Error: trufflehog timed out after 300 seconds", file=sys.stderr)
        return 1
    finally:
        Path(exclude_file.name).unlink(missing_ok=True)


def main() -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Run trufflehog for secret detection")
    parser.add_argument("path", type=Path, help="Directory to scan")
    parser.add_argument(
        "--output",
        choices=["json", "text"],
        default="text",
        help="Output format (default: text)",
    )
    # uv run --script <file> -- <args> passes literal '--' to the script
    argv = [a for a in sys.argv[1:] if a != "--"]
    args = parser.parse_args(argv)

    if not args.path.exists():
        print(f"Error: Path does not exist: {args.path}", file=sys.stderr)
        return 1

    return run_trufflehog(args.path, args.output)


if __name__ == "__main__":
    sys.exit(main())
