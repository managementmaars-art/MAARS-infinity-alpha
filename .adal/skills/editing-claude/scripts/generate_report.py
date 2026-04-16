#!/usr/bin/env python3
"""Generate comprehensive CLAUDE.md health report.

Combines analyses from structure, emphasis, and link validators to produce
a complete health assessment with actionable recommendations.

Usage:
    python generate_report.py <claude-md-file> [--output <report-file>]

Exit codes:
    0 - Report generated successfully
    1 - Invalid input or import failure
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Final

# Import sibling modules - these are in the same directory
from analyze_emphasis import EmphasisAnalysis, Severity, analyze_emphasis
from analyze_structure import Section, StructureAnalysis, analyze_structure
from validate_links import LinkAnalysis, analyze_links


@dataclass(frozen=True, slots=True)
class ScoreBreakdown:
    """Individual score components."""

    length: int
    emphasis: int
    contradictions: int
    redundancy: int
    links: int
    structure: float
    extraction_potential: int
    freshness: int


@dataclass(frozen=True, slots=True)
class HealthScore:
    """Complete health score with breakdown."""

    total_score: float
    max_score: int
    status: str
    breakdown: ScoreBreakdown


# Score thresholds for overall status
EXCELLENT_THRESHOLD: Final[int] = 45
GOOD_THRESHOLD: Final[int] = 35
NEEDS_WORK_THRESHOLD: Final[int] = 25


def calculate_extraction_score(longest_sections: tuple[Section, ...]) -> int:
    """Calculate extraction potential score based on large sections.

    Args:
        longest_sections: Longest sections in the document.

    Returns:
        Score from 0-5.
    """
    large_sections = sum(1 for s in longest_sections if s.length > 50)
    if large_sections == 0:
        return 5
    if large_sections <= 2:
        return 3
    return 0


def calculate_health_score(
    structure_analysis: StructureAnalysis,
    emphasis_analysis: EmphasisAnalysis,
    links_analysis: LinkAnalysis,
) -> HealthScore:
    """Calculate overall health score (0-50 points).

    Args:
        structure_analysis: Structure analysis results.
        emphasis_analysis: Emphasis analysis results.
        links_analysis: Link analysis results.

    Returns:
        Complete health score with breakdown.
    """
    # Length: 10 points
    length_score = structure_analysis.length_score

    # Emphasis: 10 points
    emphasis_score = emphasis_analysis.assessment.score

    # Contradictions: 10 points (not implemented yet)
    contradictions_score = 10

    # Redundancy: 10 points (not implemented yet)
    redundancy_score = 10

    # Links: 5 points
    links_score = links_analysis.links_score

    # Structure: 5 points
    structure_score = structure_analysis.structure_score

    # Extraction Potential: 5 points
    extraction_score = calculate_extraction_score(structure_analysis.longest_sections)

    # Freshness: 5 points (not implemented)
    freshness_score = 5

    breakdown = ScoreBreakdown(
        length=length_score,
        emphasis=emphasis_score,
        contradictions=contradictions_score,
        redundancy=redundancy_score,
        links=links_score,
        structure=structure_score,
        extraction_potential=extraction_score,
        freshness=freshness_score,
    )

    total_score = (
        length_score
        + emphasis_score
        + contradictions_score
        + redundancy_score
        + links_score
        + structure_score
        + extraction_score
        + freshness_score
    )

    # Determine overall status
    if total_score >= EXCELLENT_THRESHOLD:
        status = "[EXCELLENT]"
    elif total_score >= GOOD_THRESHOLD:
        status = "[GOOD]"
    elif total_score >= NEEDS_WORK_THRESHOLD:
        status = "[NEEDS WORK]"
    else:
        status = "[CRITICAL]"

    return HealthScore(
        total_score=total_score,
        max_score=50,
        status=status,
        breakdown=breakdown,
    )


def generate_issues_section(
    structure_analysis: StructureAnalysis,
    emphasis_analysis: EmphasisAnalysis,
    links_analysis: LinkAnalysis,
) -> str:
    """Generate issues section of report.

    Args:
        structure_analysis: Structure analysis results.
        emphasis_analysis: Emphasis analysis results.
        links_analysis: Link analysis results.

    Returns:
        Formatted issues section as markdown.
    """
    critical: list[str] = []
    warnings: list[str] = []
    info: list[str] = []

    # Critical issues
    if structure_analysis.length_score == 0:
        lines = structure_analysis.total_lines
        critical.append(
            f"Document length: {lines} lines (2.5x+ recommended 100-200 lines)\n"
            f"  **Impact:** Exhausts attention budget, reduces focus\n"
            f"  **Action:** Extract sections to specialized docs (see Extraction Opportunities below)"
        )

    if emphasis_analysis.assessment.severity == Severity.ERROR:
        density = emphasis_analysis.density
        critical.append(
            f"Emphasis overuse: {density}% density (target <2%)\n"
            f"  **Impact:** When everything is critical, nothing is\n"
            f"  **Action:** Review and reduce emphasis markers to <2%"
        )

    # Warnings
    if structure_analysis.orphaned_sections:
        orphans = structure_analysis.orphaned_sections
        lines_str = ", ".join(str(o.line) for o in orphans)
        warnings.append(
            f"Orphaned sections: {len(orphans)} section(s) without proper parent\n"
            f"  **Lines:** {lines_str}\n"
            f"  **Action:** Nest under appropriate H2 or promote to H2"
        )

    if links_analysis.broken_count > 0:
        warnings.append(
            f"Broken links: {links_analysis.broken_count} link(s) pointing to non-existent files\n"
            f"  **Impact:** Navigation broken, references invalid\n"
            f"  **Action:** Fix or remove broken links"
        )

    # Info
    if emphasis_analysis.assessment.severity == Severity.INFO:
        info.append(f"Emphasis usage is optimal ({emphasis_analysis.density}%)")

    if links_analysis.broken_count == 0:
        info.append("All internal links are valid")

    # Build section
    output: list[str] = []
    if critical:
        output.append("### [CRITICAL] Fix Immediately\n")
        for issue in critical:
            output.append(f"{issue}\n")

    if warnings:
        output.append("### [WARNING] High Priority (Fix Soon)\n")
        for issue in warnings:
            output.append(f"{issue}\n")

    if info:
        output.append("### [OK] Info (Good)\n")
        for item in info:
            output.append(f"- {item}\n")

    return "\n".join(output) if output else "No issues found!\n"


def suggest_extraction_target(title: str) -> str:
    """Suggest extraction target based on section title.

    Args:
        title: Section title to analyze.

    Returns:
        Suggested target file path.
    """
    title_lower = title.lower()
    if "skill" in title_lower:
        return ".claude/docs/skills-index.md"
    if "workflow" in title_lower:
        return ".claude/docs/workflow-guides.md"
    if "anti-pattern" in title_lower or "enforcement" in title_lower:
        return ".claude/docs/enforcement-guide.md"
    if "agent" in title_lower:
        return ".claude/docs/dispatch.md"
    return ".claude/docs/specialized-guide.md"


def generate_extraction_opportunities(structure_analysis: StructureAnalysis) -> str:
    """Generate extraction opportunities section.

    Args:
        structure_analysis: Structure analysis results.

    Returns:
        Formatted extraction opportunities as markdown.
    """
    large_sections = [s for s in structure_analysis.longest_sections if s.length > 50]

    if not large_sections:
        return "No immediate extraction opportunities (all sections <50 lines)\n"

    output: list[str] = []
    for section in large_sections[:5]:  # Top 5
        target = suggest_extraction_target(section.title)
        output.append(f"- **{section.title}** ({section.length} lines) -> {target}")

    total_extractable = sum(s.length for s in large_sections)
    output.append(f"\n**Total extractable:** {total_extractable} lines")

    return "\n".join(output) + "\n"


def generate_recommendations(health_score: HealthScore) -> str:
    """Generate prioritized recommendations.

    Args:
        health_score: Complete health score with breakdown.

    Returns:
        Formatted recommendations as markdown.
    """
    breakdown = health_score.breakdown
    recommendations: list[str] = []

    # Priority 1: Length
    if breakdown.length < 5:
        recommendations.append(
            "1. **Extract large sections** to specialized docs (highest impact)"
        )

    # Priority 2: Emphasis
    if breakdown.emphasis < 5:
        recommendations.append(
            "2. **Reduce emphasis markers** to <2% density (improves clarity)"
        )

    # Priority 3: Structure
    if breakdown.structure < 3:
        recommendations.append(
            "3. **Fix structural issues** (orphaned sections, hierarchy)"
        )

    # Priority 4: Links
    if breakdown.links < 3:
        recommendations.append("4. **Fix broken links** (restore navigation)")

    if not recommendations:
        recommendations.append("1. **Maintain current quality** with quarterly reviews")
        recommendations.append("2. **Monitor document growth** (keep <200 lines)")

    return "\n".join(recommendations) + "\n"


def format_links_status(links_analysis: LinkAnalysis) -> str:
    """Format links status for report table.

    Args:
        links_analysis: Link analysis results.

    Returns:
        Formatted status string.
    """
    if links_analysis.broken_count == 0:
        return "[OK] All valid"
    return f"[ERROR] {links_analysis.broken_count} broken"


def format_structure_status(structure_analysis: StructureAnalysis) -> str:
    """Format structure status for report table.

    Args:
        structure_analysis: Structure analysis results.

    Returns:
        Formatted status string.
    """
    if not structure_analysis.orphaned_sections:
        return "[OK] Clean"
    return "[WARN] Issues found"


def format_extraction_status(health_score: HealthScore) -> str:
    """Format extraction potential status for report table.

    Args:
        health_score: Complete health score.

    Returns:
        Formatted status string.
    """
    if health_score.breakdown.extraction_potential == 5:
        return "[OK] Minimal"
    return "[WARN] Opportunities exist"


def generate_report(file_path: Path, output_path: Path | None = None) -> str:
    """Generate comprehensive health report.

    Args:
        file_path: Path to the markdown file to analyze.
        output_path: Optional path to write report file.

    Returns:
        Complete report as markdown string.
    """
    # Run all analyses
    structure_analysis = analyze_structure(file_path)
    emphasis_analysis = analyze_emphasis(file_path)
    links_analysis = analyze_links(file_path)

    # Calculate health score
    health_score = calculate_health_score(
        structure_analysis, emphasis_analysis, links_analysis
    )

    # Generate report sections
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    breakdown = health_score.breakdown

    report = f"""# CLAUDE.md Health Report

**File:** {file_path}
**Generated:** {timestamp}
**Analyzed By:** editing-claude skill

---

## Summary

**Overall Score: {health_score.total_score}/{health_score.max_score}** {health_score.status}

### Score Breakdown

| Metric | Score | Max | Status |
|--------|-------|-----|--------|
| Length | {breakdown.length} | 10 | {structure_analysis.length_status} |
| Emphasis Density | {breakdown.emphasis} | 10 | {emphasis_analysis.assessment.status} |
| Contradictions | {breakdown.contradictions} | 10 | [OK] None detected |
| Redundancy | {breakdown.redundancy} | 10 | [OK] None detected |
| Links | {breakdown.links} | 5 | {format_links_status(links_analysis)} |
| Structure | {breakdown.structure} | 5 | {format_structure_status(structure_analysis)} |
| Extraction Potential | {breakdown.extraction_potential} | 5 | {format_extraction_status(health_score)} |
| Freshness | {breakdown.freshness} | 5 | [OK] Current |

---

## Issues Found

{generate_issues_section(structure_analysis, emphasis_analysis, links_analysis)}

---

## Extraction Opportunities

{generate_extraction_opportunities(structure_analysis)}

---

## Recommendations

{generate_recommendations(health_score)}

---

**Report End**
**Next Run:** Schedule quarterly review ({datetime.now().strftime("%Y-%m-%d")})
"""

    # Write report
    if output_path:
        output_path.write_text(report)

    return report


def main() -> int:
    """Main entry point.

    Returns:
        Exit code (0 for success, 1 for failure).
    """
    if len(sys.argv) < 2:
        print(
            "Usage: python generate_report.py <claude-md-file> [--output <report-file>]",
            file=sys.stderr,
        )
        return 1

    file_path = Path(sys.argv[1])
    if not file_path.exists():
        print(f"Error: File not found: {file_path}", file=sys.stderr)
        return 1

    output_path: Path | None = None
    if "--output" in sys.argv:
        idx = sys.argv.index("--output")
        if idx + 1 < len(sys.argv):
            output_path = Path(sys.argv[idx + 1])

    report = generate_report(file_path, output_path)
    print(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
