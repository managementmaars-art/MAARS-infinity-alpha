#!/usr/bin/env python3
"""Validate ADR (Architecture Decision Record) completeness.

This script validates ADR files against a set of rules to ensure they
follow the expected format and contain all required information.

Usage:
    python validate_adr.py <path-to-adr.md>

Checks:
- Status is valid value (Proposed, Accepted, In Progress, Completed, Superseded)
- Date is in YYYY-MM-DD format
- Required sections present (Context, Decision, Consequences, Alternatives)
- No placeholder text (TODO, TBD, FILL, etc.)
- Filename matches format NNN-kebab-case-title.md
- ADR number in title matches filename number

Exit codes:
    0: Validation passed
    1: Validation failed or invalid arguments
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Final


# Constants using Final for type safety
VALID_STATUSES: Final[frozenset[str]] = frozenset({
    "Proposed",
    "Accepted",
    "In Progress",
    "Completed",
    "Superseded",
})

REQUIRED_SECTIONS: Final[tuple[str, ...]] = (
    "Context",
    "Decision",
    "Consequences",
    "Alternatives Considered",
)

# Compiled regex patterns for better performance
PLACEHOLDER_PATTERNS: Final[tuple[re.Pattern[str], ...]] = (
    re.compile(r"\[TODO[:\]]", re.IGNORECASE),
    re.compile(r"\[FILL.+?\]", re.IGNORECASE),
    re.compile(r"\[TBD\]", re.IGNORECASE),
    re.compile(r"\[PLACEHOLDER\]", re.IGNORECASE),
    re.compile(r"XXX", re.IGNORECASE),
)

FILENAME_PATTERN: Final[re.Pattern[str]] = re.compile(r"^\d{3}-[a-z0-9-]+\.md$")
STATUS_FIELD_PATTERN: Final[re.Pattern[str]] = re.compile(r"\*\*Status:\*\*\s*(.+?)(?:\n|$)")
DATE_FIELD_PATTERN: Final[re.Pattern[str]] = re.compile(r"\*\*Date:\*\*\s*(.+?)(?:\n|$)")
DATE_FORMAT_PATTERN: Final[re.Pattern[str]] = re.compile(r"^\d{4}-\d{2}-\d{2}$")
STRIKETHROUGH_PATTERN: Final[re.Pattern[str]] = re.compile(r"~~(.+?)~~")
TITLE_PATTERN: Final[re.Pattern[str]] = re.compile(r"^# ADR-(\d+):", re.MULTILINE)


@dataclass(frozen=True, slots=True)
class ValidationResult:
    """Result of ADR validation.

    Attributes:
        is_valid: Whether the ADR passed all validation checks.
        errors: List of validation error messages (empty if valid).
        file_path: Path to the validated file.
    """

    is_valid: bool
    errors: tuple[str, ...]
    file_path: Path

    @property
    def error_count(self) -> int:
        """Return the number of validation errors."""
        return len(self.errors)


@dataclass(slots=True)
class ADRValidator:
    """Validates ADR files against formatting and content rules.

    This validator checks:
    - Filename format (NNN-kebab-case-title.md)
    - Required metadata fields (Status, Date)
    - Required sections (Context, Decision, Consequences, Alternatives)
    - No placeholder text
    - ADR number consistency between title and filename

    Attributes:
        valid_statuses: Set of valid status values.
        required_sections: Tuple of required section names.
        placeholder_patterns: Compiled regex patterns for placeholder detection.
    """

    valid_statuses: frozenset[str] = field(default_factory=lambda: VALID_STATUSES)
    required_sections: tuple[str, ...] = field(default_factory=lambda: REQUIRED_SECTIONS)
    placeholder_patterns: tuple[re.Pattern[str], ...] = field(
        default_factory=lambda: PLACEHOLDER_PATTERNS
    )

    def validate(self, adr_path: Path) -> ValidationResult:
        """Validate an ADR file.

        Args:
            adr_path: Path to the ADR markdown file.

        Returns:
            ValidationResult containing validation status and any errors.
        """
        errors: list[str] = []

        if not adr_path.exists():
            return ValidationResult(
                is_valid=False,
                errors=(f"File not found: {adr_path}",),
                file_path=adr_path,
            )

        content = adr_path.read_text(encoding="utf-8")
        filename = adr_path.name

        # Run all validation checks
        errors.extend(self._validate_filename(filename))
        errors.extend(self._validate_status(content))
        errors.extend(self._validate_date(content))
        errors.extend(self._validate_sections(content))
        errors.extend(self._validate_placeholders(content))
        errors.extend(self._validate_title(content, filename))

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=tuple(errors),
            file_path=adr_path,
        )

    def _validate_filename(self, filename: str) -> list[str]:
        """Validate filename format: NNN-kebab-case-title.md."""
        if not FILENAME_PATTERN.match(filename):
            return [
                f"Invalid filename format: {filename}. "
                "Expected: NNN-kebab-case-title.md (e.g., 028-graph-database-selection.md)"
            ]
        return []

    def _validate_status(self, content: str) -> list[str]:
        """Validate the Status field."""
        status_match = STATUS_FIELD_PATTERN.search(content)
        if not status_match:
            return ["Missing **Status:** field"]

        status = status_match.group(1).strip()
        # Remove strikethrough if present (superseded ADRs)
        status_clean = STRIKETHROUGH_PATTERN.sub("", status).strip()

        # Extract base status (handle "Proposed (Blocked)" -> "Proposed")
        status_parsed = status_clean.split("(")[0].strip() if "(" in status_clean else status_clean

        if status_parsed not in self.valid_statuses:
            return [
                f"Invalid status: '{status_parsed}'. "
                f"Must be one of: {', '.join(sorted(self.valid_statuses))}"
            ]
        return []

    def _validate_date(self, content: str) -> list[str]:
        """Validate the Date field format (YYYY-MM-DD)."""
        date_match = DATE_FIELD_PATTERN.search(content)
        if not date_match:
            return ["Missing **Date:** field"]

        date = date_match.group(1).strip()
        if not DATE_FORMAT_PATTERN.match(date):
            return [f"Invalid date format: '{date}'. Expected: YYYY-MM-DD (e.g., 2025-10-17)"]
        return []

    def _validate_sections(self, content: str) -> list[str]:
        """Validate that all required sections are present."""
        errors: list[str] = []
        for section in self.required_sections:
            section_pattern = rf"^##+ {re.escape(section)}"
            if not re.search(section_pattern, content, re.MULTILINE):
                errors.append(f"Missing required section: {section}")
        return errors

    def _validate_placeholders(self, content: str) -> list[str]:
        """Validate that no placeholder text remains."""
        errors: list[str] = []
        for pattern in self.placeholder_patterns:
            for match in pattern.finditer(content):
                line_num = content[: match.start()].count("\n") + 1
                errors.append(f"Placeholder text found at line {line_num}: '{match.group()}'")
        return errors

    def _validate_title(self, content: str, filename: str) -> list[str]:
        """Validate ADR title format and number consistency."""
        title_match = TITLE_PATTERN.search(content)
        if not title_match:
            return ["Title must start with '# ADR-NNN:' (e.g., '# ADR-028: Title')"]

        adr_num = title_match.group(1)
        filename_num = filename[:3]
        if adr_num != filename_num:
            return [
                f"ADR number mismatch: title says ADR-{adr_num}, filename says {filename_num}"
            ]
        return []


def validate_adr(adr_path: Path) -> tuple[bool, list[str]]:
    """Validate an ADR file.

    This is a convenience function that wraps ADRValidator for simple use cases.

    Args:
        adr_path: Path to the ADR markdown file.

    Returns:
        Tuple of (is_valid, errors) where errors is a list of validation
        failure messages. Empty list if validation passed.
    """
    validator = ADRValidator()
    result = validator.validate(adr_path)
    return result.is_valid, list(result.errors)


def format_validation_output(result: ValidationResult) -> str:
    """Format validation result for human-readable output.

    Args:
        result: The validation result to format.

    Returns:
        Formatted string suitable for terminal output.
    """
    lines: list[str] = []

    if result.is_valid:
        lines.append(f"[PASS] ADR validation passed: {result.file_path}")
    else:
        lines.append(f"[FAIL] ADR validation failed: {result.file_path}")
        lines.append(f"\nFound {result.error_count} error(s):\n")
        for i, error in enumerate(result.errors, 1):
            lines.append(f"  {i}. {error}")

    return "\n".join(lines)


def main() -> int:
    """Main entry point for the CLI.

    Returns:
        Exit code: 0 for success, 1 for validation failure or errors.
    """
    if len(sys.argv) != 2:
        print("Usage: validate_adr.py <path-to-adr.md>")
        print("\nExample:")
        print("  python validate_adr.py docs/adr/001-example.md")
        return 1

    adr_path = Path(sys.argv[1])
    validator = ADRValidator()
    result = validator.validate(adr_path)

    print(format_validation_output(result))
    return 0 if result.is_valid else 1


if __name__ == "__main__":
    sys.exit(main())
