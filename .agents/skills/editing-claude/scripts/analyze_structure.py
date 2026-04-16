#!/usr/bin/env python3
"""Analyze CLAUDE.md document structure.

Examines headings, sections, hierarchy violations, and orphaned sections
to assess document organization quality.

Usage:
    python analyze_structure.py <claude-md-file>

Exit codes:
    0 - Structure acceptable
    1 - Critical structural issues or invalid input
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Final


@dataclass(frozen=True, slots=True)
class Heading:
    """A markdown heading extracted from content."""

    line: int
    level: int
    title: str
    raw: str


@dataclass(frozen=True, slots=True)
class Section:
    """A document section with computed metrics."""

    line: int
    level: int
    title: str
    raw: str
    start_line: int
    end_line: int
    length: int
    percentage: float


@dataclass(frozen=True, slots=True)
class OrphanedSection:
    """An H3+ section without proper parent heading."""

    line: int
    title: str
    reason: str


@dataclass(frozen=True, slots=True)
class HierarchyIssue:
    """A heading hierarchy violation."""

    line: int
    title: str
    reason: str
    severity: str


@dataclass(frozen=True, slots=True)
class StructureAnalysis:
    """Complete structure analysis results."""

    total_lines: int
    total_headings: int
    h1_count: int
    h2_count: int
    h3_count: int
    sections: tuple[Section, ...]
    longest_sections: tuple[Section, ...]
    orphaned_sections: tuple[OrphanedSection, ...]
    hierarchy_issues: tuple[HierarchyIssue, ...]
    length_status: str
    length_score: int
    structure_score: float


HEADING_PATTERN: Final[re.Pattern[str]] = re.compile(r"^(#{1,6})\s+(.+)$")


def extract_headings(content: str) -> tuple[Heading, ...]:
    """Extract all headings with line numbers and levels.

    Args:
        content: Markdown content to analyze.

    Returns:
        Tuple of extracted headings.
    """
    headings: list[Heading] = []
    lines = content.split("\n")

    for idx, line in enumerate(lines, 1):
        match = HEADING_PATTERN.match(line)
        if match:
            level = len(match.group(1))
            title = match.group(2).strip()
            headings.append(Heading(line=idx, level=level, title=title, raw=line))

    return tuple(headings)


def calculate_section_lengths(
    content: str,
    headings: tuple[Heading, ...],
) -> tuple[Section, ...]:
    """Calculate line count for each section.

    Args:
        content: Markdown content.
        headings: Extracted headings.

    Returns:
        Tuple of sections with computed metrics.
    """
    lines = content.split("\n")
    total_lines = len(lines)
    sections: list[Section] = []

    for i, heading in enumerate(headings):
        start_line = heading.line
        # Find end line (next heading or end of file)
        end_line = headings[i + 1].line - 1 if i + 1 < len(headings) else total_lines
        length = end_line - start_line + 1

        sections.append(
            Section(
                line=heading.line,
                level=heading.level,
                title=heading.title,
                raw=heading.raw,
                start_line=start_line,
                end_line=end_line,
                length=length,
                percentage=round((length / total_lines) * 100, 1)
                if total_lines > 0
                else 0.0,
            )
        )

    return tuple(sections)


def detect_orphaned_sections(
    sections: tuple[Section, ...],
) -> tuple[OrphanedSection, ...]:
    """Detect H3 sections without H2 parent.

    Args:
        sections: Document sections to analyze.

    Returns:
        Tuple of orphaned sections found.
    """
    orphans: list[OrphanedSection] = []
    current_h2: Section | None = None

    for section in sections:
        if section.level == 2:
            current_h2 = section
        elif section.level == 3 and current_h2 is None:
            orphans.append(
                OrphanedSection(
                    line=section.line,
                    title=section.title,
                    reason="H3 without H2 parent",
                )
            )

    return tuple(orphans)


def detect_hierarchy_issues(
    sections: tuple[Section, ...],
) -> tuple[HierarchyIssue, ...]:
    """Detect heading hierarchy violations (e.g., H1 -> H3 skip).

    Args:
        sections: Document sections to analyze.

    Returns:
        Tuple of hierarchy issues found.
    """
    issues: list[HierarchyIssue] = []
    prev_level = 0

    for section in sections:
        level = section.level
        if level - prev_level > 1:
            issues.append(
                HierarchyIssue(
                    line=section.line,
                    title=section.title,
                    reason=f"Skipped from H{prev_level} to H{level}",
                    severity="warning",
                )
            )
        prev_level = level

    return tuple(issues)


def assess_length(total_lines: int) -> tuple[str, int]:
    """Assess document length against recommended limits.

    Args:
        total_lines: Total line count.

    Returns:
        Tuple of (status message, score 0-10).
    """
    if total_lines <= 200:
        return "[OK] Within recommended range (100-200)", 10
    if total_lines <= 300:
        return f"[WARN] Above recommended ({total_lines} lines, target 100-200)", 7
    if total_lines <= 500:
        return f"[WARN] 2x recommended ({total_lines} lines, target 100-200)", 3
    return f"[ERROR] 2.5x+ recommended ({total_lines} lines, target 100-200)", 0


def calculate_structure_score(
    orphans: tuple[OrphanedSection, ...],
    hierarchy_issues: tuple[HierarchyIssue, ...],
) -> float:
    """Calculate structure quality score.

    Args:
        orphans: Orphaned sections found.
        hierarchy_issues: Hierarchy issues found.

    Returns:
        Score from 0-5.
    """
    score = 5.0  # Start with perfect
    score -= len(orphans)
    score -= len(hierarchy_issues) * 0.5
    return max(0.0, score)


def analyze_structure(file_path: Path) -> StructureAnalysis:
    """Analyze structure of a markdown file.

    Args:
        file_path: Path to the markdown file.

    Returns:
        Complete structure analysis results.
    """
    content = file_path.read_text()
    lines = content.split("\n")
    total_lines = len(lines)

    headings = extract_headings(content)
    sections = calculate_section_lengths(content, headings)
    orphans = detect_orphaned_sections(sections)
    hierarchy_issues = detect_hierarchy_issues(sections)

    # Count by level
    h1_count = sum(1 for s in sections if s.level == 1)
    h2_count = sum(1 for s in sections if s.level == 2)
    h3_count = sum(1 for s in sections if s.level == 3)

    # Find longest sections
    longest_sections = tuple(sorted(sections, key=lambda x: x.length, reverse=True)[:5])

    # Assess length
    length_status, length_score = assess_length(total_lines)

    # Calculate structure score
    structure_score = calculate_structure_score(orphans, hierarchy_issues)

    return StructureAnalysis(
        total_lines=total_lines,
        total_headings=len(headings),
        h1_count=h1_count,
        h2_count=h2_count,
        h3_count=h3_count,
        sections=sections,
        longest_sections=longest_sections,
        orphaned_sections=orphans,
        hierarchy_issues=hierarchy_issues,
        length_status=length_status,
        length_score=length_score,
        structure_score=structure_score,
    )


def print_report(analysis: StructureAnalysis) -> None:
    """Print human-readable structure report.

    Args:
        analysis: Structure analysis results to report.
    """
    print("=" * 60)
    print("Structure Analysis Report")
    print("=" * 60)

    print(f"\nDocument Size: {analysis.total_lines} lines")
    print(f"Status: {analysis.length_status}")
    print(f"Length Score: {analysis.length_score}/10")
    print(f"Structure Score: {analysis.structure_score}/5")

    print("\nHeading Distribution:")
    print(f"  H1: {analysis.h1_count}")
    print(f"  H2: {analysis.h2_count}")
    print(f"  H3: {analysis.h3_count}")
    print(f"  Total: {analysis.total_headings}")

    if analysis.longest_sections:
        print("\nLongest Sections (Top 5):")
        for section in analysis.longest_sections:
            marker = "[WARN]" if section.length > 100 else "[OK]"
            print(
                f"  {marker} {section.title} ({section.length} lines, {section.percentage}%)"
            )

    if analysis.orphaned_sections:
        print(f"\nOrphaned Sections ({len(analysis.orphaned_sections)}):")
        for orphan in analysis.orphaned_sections:
            print(f"  Line {orphan.line}: {orphan.title}")
            print(f"    Reason: {orphan.reason}")
    else:
        print("\n[OK] No orphaned sections found")

    if analysis.hierarchy_issues:
        print(f"\nHierarchy Issues ({len(analysis.hierarchy_issues)}):")
        for issue in analysis.hierarchy_issues:
            print(f"  Line {issue.line}: {issue.title}")
            print(f"    Issue: {issue.reason}")
    else:
        print("[OK] Hierarchy is correct")


def main() -> int:
    """Main entry point.

    Returns:
        Exit code (0 for success, 1 for failure).
    """
    if len(sys.argv) < 2:
        print("Usage: python analyze_structure.py <claude-md-file>", file=sys.stderr)
        return 1

    file_path = Path(sys.argv[1])
    if not file_path.exists():
        print(f"Error: File not found: {file_path}", file=sys.stderr)
        return 1

    analysis = analyze_structure(file_path)
    print_report(analysis)

    # Exit code based on severity
    if analysis.length_score == 0 or analysis.orphaned_sections:
        return 1  # Critical issues
    return 0


if __name__ == "__main__":
    sys.exit(main())
