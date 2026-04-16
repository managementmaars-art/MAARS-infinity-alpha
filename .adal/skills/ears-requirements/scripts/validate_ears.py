#!/usr/bin/env python3
"""Validate EARS requirements and classify their pattern."""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import List

WEAK_TERMS = [
    "as appropriate",
    "if possible",
    "etc",
    "normally",
    "quickly",
    "user-friendly",
]


def classify_pattern(text: str) -> str:
    lowered = text.strip().lower()
    if lowered.startswith("if "):
        return "unwanted-behavior"
    if lowered.startswith("while ") and " when " in lowered:
        if lowered.find("while ") < lowered.find(" when "):
            return "complex"
    if lowered.startswith("while "):
        return "state-driven"
    if lowered.startswith("when "):
        return "event-driven"
    if lowered.startswith("where "):
        return "optional-feature"
    if lowered.startswith("the "):
        return "ubiquitous"
    return "unknown"


def validate_requirement(text: str) -> dict:
    issues = []
    lowered = text.lower().strip()
    pattern = classify_pattern(text)

    shall_count = len(re.findall(r"\bshall\b", lowered))
    if shall_count == 0:
        issues.append("Missing required keyword 'shall'.")
    elif shall_count > 1:
        issues.append("Use one behavior per statement: multiple 'shall' found.")

    if pattern == "unwanted-behavior":
        if not re.search(r"^if\s+.+,\s*then\s+the\s+.+\s+shall\s+.+", lowered):
            issues.append("Unwanted-behavior form should be: If ..., then the <system> shall ...")
    elif pattern == "complex":
        if not re.search(r"^while\s+.+,\s*when\s+.+,\s*the\s+.+\s+shall\s+.+", lowered):
            issues.append("Complex form should be: While ..., when ..., the <system> shall ...")
    elif pattern == "state-driven":
        if not re.search(r"^while\s+.+,\s*the\s+.+\s+shall\s+.+", lowered):
            issues.append("State-driven form should be: While ..., the <system> shall ...")
    elif pattern == "event-driven":
        if not re.search(r"^when\s+.+,\s*the\s+.+\s+shall\s+.+", lowered):
            issues.append("Event-driven form should be: When ..., the <system> shall ...")
    elif pattern == "optional-feature":
        if not re.search(r"^where\s+.+,\s*the\s+.+\s+shall\s+.+", lowered):
            issues.append("Optional-feature form should be: Where ..., the <system> shall ...")
    elif pattern == "ubiquitous":
        if not re.search(r"^the\s+.+\s+shall\s+.+", lowered):
            issues.append("Ubiquitous form should be: The <system> shall ...")
    else:
        issues.append("Cannot classify EARS pattern from leading clause.")

    if " if " in lowered and pattern != "unwanted-behavior":
        issues.append("Use 'If ..., then ...' only for unwanted-behavior requirements.")
    if " while " in lowered and " when " in lowered and lowered.find(" when ") < lowered.find(" while "):
        issues.append("Clause order violation: place 'While ...' before 'when ...'.")

    for term in WEAK_TERMS:
        if term in lowered:
            issues.append(f"Avoid weak wording: '{term}'.")

    if " and " in lowered and shall_count >= 1:
        issues.append("Potential multiple behaviors in one requirement; split if independent.")

    return {
        "requirement": text,
        "pattern": pattern,
        "valid": len(issues) == 0,
        "issues": issues,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate EARS requirement statements.")
    parser.add_argument("--requirement", help="Single requirement text to validate.")
    parser.add_argument("--file", help="Path to a text file with one requirement per line.")
    parser.add_argument("--json", action="store_true", help="Output JSON.")
    return parser.parse_args()


def load_requirements(args: argparse.Namespace) -> List[str]:
    if args.requirement and args.file:
        print("Use either --requirement or --file, not both.", file=sys.stderr)
        sys.exit(2)
    if not args.requirement and not args.file:
        print("Provide --requirement or --file.", file=sys.stderr)
        sys.exit(2)

    if args.requirement:
        return [args.requirement.strip()]

    path = Path(args.file)
    if not path.exists():
        print(f"File not found: {path}", file=sys.stderr)
        sys.exit(2)

    lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines()]
    return [line for line in lines if line]


def main() -> None:
    args = parse_args()
    requirements = load_requirements(args)
    results = [validate_requirement(item) for item in requirements]

    if args.json:
        print(json.dumps(results, ensure_ascii=True, indent=2))
        return

    for idx, result in enumerate(results, start=1):
        status = "PASS" if result["valid"] else "FAIL"
        print(f"[{status}] #{idx} pattern={result['pattern']}")
        print(f"  {result['requirement']}")
        if result["issues"]:
            for issue in result["issues"]:
                print(f"  - {issue}")


if __name__ == "__main__":
    main()
