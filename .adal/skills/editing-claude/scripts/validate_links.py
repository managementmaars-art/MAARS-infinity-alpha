#!/usr/bin/env python3
"""Validate all markdown links in CLAUDE.md files.

This module extracts and validates markdown links, categorizing them as
internal (file paths), external (URLs), or anchor links.

Usage:
    python validate_links.py <claude-md-file>

Exit codes:
    0 - All links valid
    1 - Broken links found or invalid input
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Final


class LinkType(StrEnum):
    """Classification of markdown link types."""

    INTERNAL = "internal"
    EXTERNAL = "external"
    ANCHOR = "anchor"


@dataclass(frozen=True, slots=True)
class MarkdownLink:
    """Represents a markdown link extracted from content."""

    line: int
    text: str
    path: str
    link_type: LinkType
    raw: str


@dataclass(frozen=True, slots=True)
class LinkValidation:
    """Result of validating an internal link."""

    line: int
    text: str
    path: str
    target: str
    exists: bool
    is_file: bool

    @property
    def valid(self) -> bool:
        """Link is valid if target exists and is a file."""
        return self.exists and self.is_file


@dataclass(frozen=True, slots=True)
class LinkAnalysis:
    """Complete link analysis results."""

    total_links: int
    internal_count: int
    external_count: int
    anchor_count: int
    validation_results: tuple[LinkValidation, ...]
    valid_count: int
    broken_count: int
    links_score: int


# Pattern: [text](path) or [text](url)
LINK_PATTERN: Final[re.Pattern[str]] = re.compile(r"\[([^\]]+)\]\(([^\)]+)\)")


def classify_link(path: str) -> LinkType:
    """Classify a link path into its type.

    Args:
        path: The link destination path or URL.

    Returns:
        The link type classification.
    """
    if path.startswith(("http://", "https://")):
        return LinkType.EXTERNAL
    if path.startswith("#"):
        return LinkType.ANCHOR
    return LinkType.INTERNAL


def extract_links(content: str) -> tuple[MarkdownLink, ...]:
    """Extract all markdown links from content.

    Args:
        content: Markdown content to parse.

    Returns:
        Tuple of extracted markdown links.
    """
    links: list[MarkdownLink] = []
    lines = content.split("\n")

    for idx, line in enumerate(lines, 1):
        for match in LINK_PATTERN.finditer(line):
            text = match.group(1)
            path = match.group(2)
            link_type = classify_link(path)

            links.append(
                MarkdownLink(
                    line=idx,
                    text=text,
                    path=path,
                    link_type=link_type,
                    raw=match.group(0),
                )
            )

    return tuple(links)


def validate_internal_links(
    links: tuple[MarkdownLink, ...],
    base_path: Path,
) -> tuple[LinkValidation, ...]:
    """Validate internal file links exist.

    Args:
        links: Extracted markdown links.
        base_path: Base file path for resolving relative links.

    Returns:
        Tuple of validation results for internal links.
    """
    results: list[LinkValidation] = []

    for link in links:
        if link.link_type != LinkType.INTERNAL:
            continue

        # Resolve relative path from base_path
        target_path = (base_path.parent / link.path).resolve()
        exists = target_path.exists()
        is_file = target_path.is_file() if exists else False

        results.append(
            LinkValidation(
                line=link.line,
                text=link.text,
                path=link.path,
                target=str(target_path),
                exists=exists,
                is_file=is_file,
            )
        )

    return tuple(results)


def calculate_links_score(validation_results: tuple[LinkValidation, ...]) -> int:
    """Calculate link validation score.

    Args:
        validation_results: Validation results for internal links.

    Returns:
        Score from 0-5 based on broken link count.
    """
    if len(validation_results) == 0:
        return 5  # No links = no broken links

    broken_count = sum(1 for r in validation_results if not r.valid)

    if broken_count == 0:
        return 5  # All valid
    if broken_count <= 2:
        return 3  # Few broken
    return 0  # Many broken


def analyze_links(file_path: Path) -> LinkAnalysis:
    """Analyze all links in a markdown file.

    Args:
        file_path: Path to the markdown file.

    Returns:
        Complete link analysis results.
    """
    content = file_path.read_text()
    links = extract_links(content)

    # Classify links by type
    internal_links = tuple(lnk for lnk in links if lnk.link_type == LinkType.INTERNAL)
    external_links = tuple(lnk for lnk in links if lnk.link_type == LinkType.EXTERNAL)
    anchor_links = tuple(lnk for lnk in links if lnk.link_type == LinkType.ANCHOR)

    # Validate internal links
    validation_results = validate_internal_links(links, file_path)

    # Count valid/broken
    valid_count = sum(1 for r in validation_results if r.valid)
    broken_count = len(validation_results) - valid_count

    return LinkAnalysis(
        total_links=len(links),
        internal_count=len(internal_links),
        external_count=len(external_links),
        anchor_count=len(anchor_links),
        validation_results=validation_results,
        valid_count=valid_count,
        broken_count=broken_count,
        links_score=calculate_links_score(validation_results),
    )


def print_report(analysis: LinkAnalysis) -> None:
    """Print human-readable link validation report.

    Args:
        analysis: Link analysis results to report.
    """
    print("=" * 60)
    print("Link Validation Report")
    print("=" * 60)
    print(f"Total links: {analysis.total_links}")
    print(f"  Internal: {analysis.internal_count}")
    print(f"  External: {analysis.external_count}")
    print(f"  Anchors: {analysis.anchor_count}")
    print(f"\nValid: {analysis.valid_count}")
    print(f"Broken: {analysis.broken_count}")

    if analysis.broken_count == 0:
        print("\n[OK] All links are valid!")
    else:
        print("\n[ERROR] Broken Links Found:")
        for result in analysis.validation_results:
            if not result.valid:
                print(f"  Line {result.line}: {result.path}")
                print(f"    Text: {result.text}")


def main() -> int:
    """Main entry point.

    Returns:
        Exit code (0 for success, 1 for failure).
    """
    if len(sys.argv) < 2:
        print("Usage: python validate_links.py <claude-md-file>", file=sys.stderr)
        return 1

    file_path = Path(sys.argv[1])
    if not file_path.exists():
        print(f"Error: File not found: {file_path}", file=sys.stderr)
        return 1

    analysis = analyze_links(file_path)
    print_report(analysis)

    return 1 if analysis.broken_count > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
