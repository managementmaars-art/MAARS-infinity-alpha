#!/usr/bin/env python3
"""
Task Precision Validator

Validates task descriptions against the SMART+ framework and precision checklist.
Can be used to check individual tasks or entire todo.md files.

Usage:
    python validate_task.py "task description"
    python validate_task.py --file todo.md
"""

import argparse
import re
import sys
from dataclasses import dataclass
from enum import Enum
from typing import List, Tuple


class Severity(Enum):
    """Validation issue severity levels."""

    ERROR = "ERROR"  # Must fix (blocks autonomous execution)
    WARNING = "WARNING"  # Should fix (reduces clarity)
    INFO = "INFO"  # Nice to have (improves quality)


@dataclass
class ValidationIssue:
    """Represents a validation issue found in a task."""

    severity: Severity
    component: str  # Which SMART+ component (S, M, A, R, T, +)
    message: str
    suggestion: str = ""


# Forbidden vague patterns from SKILL.md Section 6
FORBIDDEN_PATTERNS = {
    r"\bimplement the feature\b": "Implement [specific feature] in [class/file]",
    r"\badd tests\b": "Add unit tests for [component] covering [cases]",
    r"\bfix the bug\b": "Fix [error type] in [file:line] caused by [root cause]",
    r"\bupdate the code\b": "Update [function] to [specific change]",
    r"\bhandle errors\b": "Add try/except for [error type] in [location]",
    r"\brefactor\b(?! [^\s]+)": "Extract [logic] from [source] into [destination]",
    r"\bimprove performance\b": "Reduce [operation] from [baseline] to [target]",
    r"\badd logging\b": "Add [library] logging to [function] for events [A, B, C]",
    r"\bdocument the code\b": "Add [style] docstring to [function]",
}

# Required action verbs (precise)
PRECISE_VERBS = {
    "create",
    "add",
    "modify",
    "remove",
    "rename",
    "extract",
    "move",
}

# Vague action verbs (should avoid)
VAGUE_VERBS = {
    "fix",
    "update",
    "improve",
    "handle",
    "implement",
    "refactor",
}


def validate_task(task_description: str) -> List[ValidationIssue]:
    """
    Validate a task description against SMART+ framework.

    Args:
        task_description: The task description to validate

    Returns:
        List of validation issues found
    """
    issues = []

    # Clean up task description (remove checkbox, task number)
    task = re.sub(r"^-?\s*\[[ xX]?\]\s*", "", task_description)
    task = re.sub(r"^Task\s+\d+:\s*", "", task, flags=re.IGNORECASE)
    task = task.strip()

    # S - Specific
    issues.extend(_validate_specific(task))

    # M - Measurable
    issues.extend(_validate_measurable(task_description))

    # A - Actionable
    issues.extend(_validate_actionable(task))

    # R - Referenced
    issues.extend(_validate_referenced(task_description))

    # T - Testable
    issues.extend(_validate_testable(task_description))

    # Check forbidden vague patterns
    issues.extend(_check_forbidden_patterns(task))

    return issues


def _validate_specific(task: str) -> List[ValidationIssue]:
    """Validate task specificity (S component)."""
    issues = []

    # Check for vague action verbs
    words = task.lower().split()
    if not words:
        issues.append(
            ValidationIssue(
                severity=Severity.ERROR,
                component="S",
                message="Task description is empty",
                suggestion="Provide a clear task description",
            )
        )
        return issues

    first_verb = words[0] if words else ""

    if first_verb in VAGUE_VERBS:
        issues.append(
            ValidationIssue(
                severity=Severity.WARNING,
                component="S",
                message=f"Vague action verb: '{first_verb}'",
                suggestion=f"Use precise verb: {', '.join(sorted(PRECISE_VERBS))}",
            )
        )

    # Check for generic references
    if re.search(r"\bthe (code|file|function|class|bug|feature)\b", task, re.IGNORECASE):
        issues.append(
            ValidationIssue(
                severity=Severity.ERROR,
                component="S",
                message="Generic reference found (e.g., 'the code', 'the file')",
                suggestion="Specify exact file/class/function name",
            )
        )

    # Check task length (too short is usually vague)
    if len(task) < 20:
        issues.append(
            ValidationIssue(
                severity=Severity.WARNING,
                component="S",
                message="Task description very short (may lack specificity)",
                suggestion="Add more details: what file, what change, what outcome",
            )
        )

    return issues


def _validate_measurable(full_task: str) -> List[ValidationIssue]:
    """Validate task measurability (M component)."""
    issues = []

    # Check for Verify: line
    if not re.search(r"\bVerify:\s*\S+", full_task, re.IGNORECASE):
        issues.append(
            ValidationIssue(
                severity=Severity.ERROR,
                component="M",
                message="No verification command specified",
                suggestion="Add 'Verify: [command to run] (expected outcome)'",
            )
        )
    else:
        # Check if verify line has actual command
        verify_match = re.search(
            r"Verify:\s*(.+?)(?:\n|$)", full_task, re.IGNORECASE | re.MULTILINE
        )
        if verify_match:
            verify_text = verify_match.group(1).strip()
            # Check for vague verify statements
            if any(
                vague in verify_text.lower()
                for vague in ["works", "everything passes", "looks good", "is better"]
            ):
                issues.append(
                    ValidationIssue(
                        severity=Severity.ERROR,
                        component="M",
                        message=f"Vague verification: '{verify_text}'",
                        suggestion="Use specific command: pytest [path], mypy [path], etc.",
                    )
                )

    return issues


def _validate_actionable(task: str) -> List[ValidationIssue]:
    """Validate task actionability (A component)."""
    issues = []

    # Check for decision/research keywords (not actionable)
    decision_keywords = [
        "decide",
        "research",
        "investigate",
        "explore",
        "figure out",
        "determine",
    ]

    for keyword in decision_keywords:
        if keyword in task.lower():
            issues.append(
                ValidationIssue(
                    severity=Severity.ERROR,
                    component="A",
                    message=f"Task contains decision/research keyword: '{keyword}'",
                    suggestion="Separate research into ADR/spike, make implementation task actionable",
                )
            )

    return issues


def _validate_referenced(full_task: str) -> List[ValidationIssue]:
    """Validate task references (R component)."""
    issues = []

    # Check for Location: line
    if not re.search(r"\bLocation:\s*\S+", full_task, re.IGNORECASE):
        issues.append(
            ValidationIssue(
                severity=Severity.ERROR,
                component="R",
                message="No file location specified",
                suggestion="Add 'Location: path/to/file.py:Class.method'",
            )
        )

    # Check for relative path indicators (should use full path)
    if re.search(r"Location:\s*\./", full_task, re.IGNORECASE):
        issues.append(
            ValidationIssue(
                severity=Severity.WARNING,
                component="R",
                message="Relative path used in Location",
                suggestion="Use full path from project root (e.g., src/module/file.py)",
            )
        )

    return issues


def _validate_testable(full_task: str) -> List[ValidationIssue]:
    """Validate task testability (T component)."""
    issues = []

    # Check for Tests: or Test cases: sections
    has_tests = re.search(r"\bTests?:\s*\S+", full_task, re.IGNORECASE)
    has_test_cases = re.search(r"\bTest cases?:\s*", full_task, re.IGNORECASE)

    if not has_tests and not has_test_cases:
        # Only warn if this looks like an implementation task
        if not any(
            keyword in full_task.lower()
            for keyword in ["rename", "move", "delete", "remove"]
        ):
            issues.append(
                ValidationIssue(
                    severity=Severity.WARNING,
                    component="T",
                    message="No test specification found",
                    suggestion="Add 'Tests: path/to/test_file.py' and enumerate test cases",
                )
            )

    return issues


def _check_forbidden_patterns(task: str) -> List[ValidationIssue]:
    """Check for forbidden vague patterns."""
    issues = []

    for pattern, suggestion in FORBIDDEN_PATTERNS.items():
        if re.search(pattern, task, re.IGNORECASE):
            issues.append(
                ValidationIssue(
                    severity=Severity.ERROR,
                    component="*",
                    message=f"Forbidden vague pattern: {pattern}",
                    suggestion=f"Use precise alternative: {suggestion}",
                )
            )

    return issues


def validate_file(file_path: str) -> List[Tuple[str, List[ValidationIssue]]]:
    """
    Validate all tasks in a file (e.g., todo.md).

    Args:
        file_path: Path to file containing tasks

    Returns:
        List of (task_description, issues) tuples
    """
    with open(file_path, "r") as f:
        content = f.read()

    # Extract tasks (lines starting with - [ ] or - [x])
    tasks = []
    current_task = []

    for line in content.split("\n"):
        if re.match(r"^\s*-\s*\[[ xX]?\]", line):
            # Start of new task
            if current_task:
                tasks.append("\n".join(current_task))
            current_task = [line]
        elif current_task and line.strip() and not line.startswith("#"):
            # Continuation of current task
            current_task.append(line)

    # Don't forget last task
    if current_task:
        tasks.append("\n".join(current_task))

    results = []
    for task in tasks:
        issues = validate_task(task)
        if issues:  # Only include tasks with issues
            results.append((task, issues))

    return results


def print_validation_results(
    results: List[Tuple[str, List[ValidationIssue]]], verbose: bool = False
) -> int:
    """
    Print validation results.

    Args:
        results: List of (task, issues) tuples
        verbose: Show full task descriptions

    Returns:
        Exit code (0 if no errors, 1 if errors found)
    """
    total_errors = 0
    total_warnings = 0

    for task, issues in results:
        # Extract first line of task for summary
        first_line = task.split("\n")[0].strip()
        if len(first_line) > 80:
            first_line = first_line[:77] + "..."

        print(f"\nTask: {first_line}")
        if verbose:
            print(f"Full task:\n{task}\n")

        for issue in issues:
            severity_symbol = "❌" if issue.severity == Severity.ERROR else "⚠️"
            print(f"  {severity_symbol} [{issue.component}] {issue.message}")
            if issue.suggestion:
                print(f"      → {issue.suggestion}")

            if issue.severity == Severity.ERROR:
                total_errors += 1
            elif issue.severity == Severity.WARNING:
                total_warnings += 1

    # Summary
    print("\n" + "=" * 80)
    if total_errors == 0 and total_warnings == 0:
        print("✅ All tasks pass validation!")
        return 0
    else:
        print(f"Validation complete: {total_errors} errors, {total_warnings} warnings")
        return 1 if total_errors > 0 else 0


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate task descriptions against SMART+ framework"
    )
    parser.add_argument(
        "task", nargs="?", help="Task description to validate (quote if multi-word)"
    )
    parser.add_argument(
        "--file", "-f", help="Validate all tasks in a file (e.g., todo.md)"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Show full task descriptions"
    )

    args = parser.parse_args()

    if args.file:
        # Validate file
        try:
            results = validate_file(args.file)
            exit_code = print_validation_results(results, args.verbose)
            sys.exit(exit_code)
        except FileNotFoundError:
            print(f"❌ File not found: {args.file}")
            sys.exit(1)
    elif args.task:
        # Validate single task
        issues = validate_task(args.task)
        results = [(args.task, issues)]
        exit_code = print_validation_results(results, args.verbose)
        sys.exit(exit_code)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
