#!/usr/bin/env python3
"""Analyze emphasis usage in CLAUDE.md files.

Detects emphasis markers (MUST/NEVER/ALWAYS/MANDATORY/CRITICAL) and
calculates density to identify overuse patterns.

Usage:
    python analyze_emphasis.py <claude-md-file>

Exit codes:
    0 - Emphasis usage acceptable
    1 - Critical overuse detected or invalid input
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Final


class Severity(StrEnum):
    """Assessment severity levels."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass(frozen=True, slots=True)
class EmphasisInstance:
    """Single emphasis marker found in content."""

    line: int
    pattern: str
    context: str
    is_heading: bool


@dataclass(frozen=True, slots=True)
class DensityAssessment:
    """Assessment of emphasis density."""

    status: str
    score: int
    recommendation: str
    severity: Severity


@dataclass(frozen=True, slots=True)
class DoubleEmphasis:
    """Detected double emphasis (heading + body)."""

    heading_line: int
    body_line: int
    suggestion: str


@dataclass(frozen=True, slots=True)
class EmphasisAnalysis:
    """Complete emphasis analysis results."""

    total_lines: int
    emphasis_count: int
    density: float
    assessment: DensityAssessment
    distribution: dict[str, int]
    heading_count: int
    body_count: int
    double_emphasis: tuple[DoubleEmphasis, ...]
    instances: tuple[EmphasisInstance, ...]


EMPHASIS_PATTERNS: Final[tuple[str, ...]] = (
    "CRITICAL",
    "MANDATORY",
    "MUST",
    "NEVER",
    "ALWAYS",
)


def extract_emphasis_instances(content: str) -> tuple[EmphasisInstance, ...]:
    """Extract all emphasis marker instances with context.

    Args:
        content: Markdown content to analyze.

    Returns:
        Tuple of emphasis instances found.
    """
    instances: list[EmphasisInstance] = []
    lines = content.split("\n")

    for idx, line in enumerate(lines, 1):
        for pattern in EMPHASIS_PATTERNS:
            # Match whole word only (not part of other words)
            if re.search(rf"\b{pattern}\b", line):
                instances.append(
                    EmphasisInstance(
                        line=idx,
                        pattern=pattern,
                        context=line.strip(),
                        is_heading=line.strip().startswith("#"),
                    )
                )

    return tuple(instances)


def calculate_density(total_lines: int, emphasis_count: int) -> float:
    """Calculate emphasis density as percentage.

    Args:
        total_lines: Total number of lines in document.
        emphasis_count: Number of emphasis markers found.

    Returns:
        Density as percentage (0-100).
    """
    if total_lines == 0:
        return 0.0
    return round((emphasis_count / total_lines) * 100, 2)


def assess_density(density: float) -> DensityAssessment:
    """Assess emphasis density and provide recommendations.

    Args:
        density: Emphasis density as percentage.

    Returns:
        Assessment with status, score, and recommendations.
    """
    if density < 1.0:
        return DensityAssessment(
            status="[OK] Optimal",
            score=10,
            recommendation="Emphasis usage is restrained and effective. No changes needed.",
            severity=Severity.INFO,
        )
    if density < 2.0:
        return DensityAssessment(
            status="[OK] Acceptable",
            score=8,
            recommendation="Emphasis usage is within recommended range (<2%). Consider if all instances are truly critical.",
            severity=Severity.INFO,
        )
    if density < 5.0:
        return DensityAssessment(
            status="[WARN] Warning",
            score=4,
            recommendation="Emphasis overuse detected (2-5%). Review and reduce to <2% for maximum impact.",
            severity=Severity.WARNING,
        )
    return DensityAssessment(
        status="[ERROR] Critical",
        score=0,
        recommendation="Severe emphasis overuse (>5%). When everything is critical, nothing is. Reduce to <2%.",
        severity=Severity.ERROR,
    )


def analyze_distribution(instances: tuple[EmphasisInstance, ...]) -> dict[str, int]:
    """Analyze distribution of emphasis types.

    Args:
        instances: Emphasis instances to analyze.

    Returns:
        Count of each emphasis pattern type.
    """
    distribution: dict[str, int] = dict.fromkeys(EMPHASIS_PATTERNS, 0)

    for instance in instances:
        distribution[instance.pattern] += 1

    return distribution


def find_double_emphasis(
    instances: tuple[EmphasisInstance, ...],
) -> tuple[DoubleEmphasis, ...]:
    """Find instances of double emphasis (heading + body in same section).

    Args:
        instances: Emphasis instances to analyze.

    Returns:
        Tuple of detected double emphasis occurrences.
    """
    double_emphasis: list[DoubleEmphasis] = []
    heading_lines = frozenset(i.line for i in instances if i.is_heading)

    for instance in instances:
        if not instance.is_heading:
            # Check if there's a heading with emphasis in previous 20 lines
            for heading_line in heading_lines:
                if 0 < instance.line - heading_line < 20:
                    double_emphasis.append(
                        DoubleEmphasis(
                            heading_line=heading_line,
                            body_line=instance.line,
                            suggestion="Remove body emphasis (heading already emphasized)",
                        )
                    )
                    break

    return tuple(double_emphasis)


def analyze_emphasis(file_path: Path) -> EmphasisAnalysis:
    """Analyze emphasis markers in a markdown file.

    Args:
        file_path: Path to the markdown file.

    Returns:
        Complete emphasis analysis results.
    """
    content = file_path.read_text()
    lines = content.split("\n")
    total_lines = len(lines)

    instances = extract_emphasis_instances(content)
    emphasis_count = len(instances)
    density = calculate_density(total_lines, emphasis_count)
    assessment = assess_density(density)
    distribution = analyze_distribution(instances)

    # Count heading vs body emphasis
    heading_count = sum(1 for i in instances if i.is_heading)
    body_count = emphasis_count - heading_count

    # Identify double emphasis
    double_emphasis = find_double_emphasis(instances)

    return EmphasisAnalysis(
        total_lines=total_lines,
        emphasis_count=emphasis_count,
        density=density,
        assessment=assessment,
        distribution=distribution,
        heading_count=heading_count,
        body_count=body_count,
        double_emphasis=double_emphasis,
        instances=instances,
    )


def print_report(analysis: EmphasisAnalysis) -> None:
    """Print human-readable emphasis report.

    Args:
        analysis: Emphasis analysis results to report.
    """
    print("=" * 60)
    print("Emphasis Usage Report")
    print("=" * 60)

    assessment = analysis.assessment
    print(f"\nStatus: {assessment.status}")
    print(f"Score: {assessment.score}/10")
    print(f"Density: {analysis.density}% (target: <2%)")
    print(f"  Recommendation: {assessment.recommendation}")

    print("\nDistribution:")
    total = analysis.emphasis_count
    for pattern, count in analysis.distribution.items():
        if count > 0:
            pct = round((count / total) * 100, 1) if total > 0 else 0
            print(f"  {pattern}: {count} ({pct}%)")

    print("\nCounts:")
    print(f"  Total instances: {total}")
    print(f"  In headings: {analysis.heading_count}")
    print(f"  In body: {analysis.body_count}")

    if analysis.double_emphasis:
        print("\nDouble Emphasis (5 most recent):")
        for de in analysis.double_emphasis[:5]:
            print(
                f"  Heading L{de.heading_line} + Body L{de.body_line}: {de.suggestion}"
            )

    if analysis.density > 2.0:
        print("\nHigh-Density Sections (first 10):")
        for instance in analysis.instances[:10]:
            marker = "[H]" if instance.is_heading else "   "
            print(
                f"  {marker} L{instance.line}: {instance.pattern} - {instance.context[:50]}"
            )


def main() -> int:
    """Main entry point.

    Returns:
        Exit code (0 for success, 1 for failure).
    """
    if len(sys.argv) < 2:
        print("Usage: python analyze_emphasis.py <claude-md-file>", file=sys.stderr)
        return 1

    file_path = Path(sys.argv[1])
    if not file_path.exists():
        print(f"Error: File not found: {file_path}", file=sys.stderr)
        return 1

    analysis = analyze_emphasis(file_path)
    print_report(analysis)

    return 1 if analysis.assessment.severity == Severity.ERROR else 0


if __name__ == "__main__":
    sys.exit(main())
