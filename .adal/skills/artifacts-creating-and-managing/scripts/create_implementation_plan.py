#!/usr/bin/env python3
"""Create an implementation plan artifact.

This script creates a new implementation plan in the .claude/artifacts/ directory
with today's date and a standard template structure for feature development.

Templates are loaded from the templates/ directory and can be customized.

Example usage:
    python create_implementation_plan.py \\
        --feature "TUI Agent Dashboard" \\
        --overview "Build interactive terminal dashboard for agent monitoring" \\
        --steps "Design widget structure" "Implement real-time log viewer" "Add status indicators"
"""

import argparse
import sys
from pathlib import Path
from typing import Final

# Import from shared tools
sys.path.insert(0, str(Path(__file__).parents[2] / ".."))
from tools.slug_utils import (
    get_today_date,
    slugify,
    validate_max_length,
    validate_non_empty,
)
from tools.template_utils import fill_template, load_template


MAX_FEATURE_LENGTH: Final[int] = 80

# Template directory relative to this script
TEMPLATE_DIR: Final[Path] = Path(__file__).parent.parent / "templates"
PLAN_TEMPLATE_FILE: Final[str] = "implementation_plan_template.md"


def validate_feature(feature: str) -> None:
    """Validate implementation plan feature name format.

    Args:
        feature: Feature name to validate.

    Raises:
        ValueError: If feature is empty or too long.
    """
    validate_non_empty(feature, "Feature name")
    validate_max_length(feature, MAX_FEATURE_LENGTH, "Feature name")


def validate_overview(overview: str) -> None:
    """Validate implementation plan overview format.

    Args:
        overview: Overview to validate.

    Raises:
        ValueError: If overview is empty.
    """
    validate_non_empty(overview, "Overview")


def format_steps(steps: list[str]) -> str:
    """Format list of implementation steps as table rows.

    Args:
        steps: List of implementation step strings.

    Returns:
        Formatted table rows for markdown table.
    """
    if not steps:
        return "| 1 | [Add task] | 1 | `temet-dev` | Not Started |\n"

    formatted = ""
    for i, raw_step in enumerate(steps, 1):
        step = raw_step.strip()
        if step:
            # Default to phase 1 and temet-dev agent
            phase = "1" if i <= len(steps) // 2 else "2"
            formatted += f"| {i} | {step} | {phase} | `temet-dev` | Not Started |\n"

    return formatted or "| 1 | [Add task] | 1 | `temet-dev` | Not Started |\n"


def create_plan_content(
    feature: str,
    overview: str,
    steps: list[str],
    template_dir: Path,
) -> str:
    """Create implementation plan markdown content from template.

    Args:
        feature: Feature name.
        overview: Feature overview/description.
        steps: List of implementation steps.
        template_dir: Directory containing template files.

    Returns:
        Formatted implementation plan markdown content.
    """
    template_file = template_dir / PLAN_TEMPLATE_FILE
    template = load_template(template_file)

    date_str = get_today_date()
    steps_md = format_steps(steps)

    task_count = len(steps) if steps else 1

    replacements = {
        "FEATURE": feature,
        "DATE": date_str,
        "OVERVIEW": overview,
        "STEPS": steps_md,
        "TASK_COUNT": str(task_count),
    }

    return fill_template(template, replacements)


def create_implementation_plan(
    artifacts_dir: Path,
    feature: str,
    overview: str,
    steps: list[str] | None = None,
    template_dir: Path = TEMPLATE_DIR,
) -> Path:
    """Create a new implementation plan artifact.

    Args:
        artifacts_dir: Base artifacts directory (.claude/artifacts/).
        feature: Feature name.
        overview: Feature overview/description.
        steps: List of implementation steps (optional).
        template_dir: Directory containing template files.

    Returns:
        Path to created implementation plan file.

    Raises:
        ValueError: If validation fails.
        FileExistsError: If file already exists.
        FileNotFoundError: If template file not found.
    """
    # Validate inputs
    validate_feature(feature)
    validate_overview(overview)

    if steps is None:
        steps = []

    # Create directory structure
    today = get_today_date()
    feature_slug = slugify(feature)

    # Create date folder and plans subfolder
    date_dir = artifacts_dir / today
    plans_dir = date_dir / "plans"
    feature_dir = plans_dir / feature_slug

    # Check if directory exists
    if feature_dir.exists():
        raise FileExistsError(f"Implementation plan already exists: {feature_dir}")

    # Create directories
    feature_dir.mkdir(parents=True, exist_ok=False)

    # Create implementation plan document from template
    plan_file = feature_dir / "IMPLEMENTATION_PLAN.md"
    content = create_plan_content(feature, overview, steps, template_dir)
    plan_file.write_text(content, encoding="utf-8")

    return plan_file


def main() -> None:
    """Parse arguments and create implementation plan."""
    parser = argparse.ArgumentParser(
        description="Create a new implementation plan artifact",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create implementation plan with minimal arguments
  python create_implementation_plan.py \\
    --feature "TUI Agent Dashboard" \\
    --overview "Build interactive terminal dashboard for agent monitoring"

  # Create implementation plan with steps
  python create_implementation_plan.py \\
    --feature "Auth Module Enhancement" \\
    --overview "Add OAuth2 support to existing auth module" \\
    --steps "Design OAuth2 flow" "Implement token validation" \\
    --steps "Add integration tests" "Update documentation"

  # Use custom artifacts directory
  python create_implementation_plan.py \\
    --artifacts-dir /path/to/artifacts \\
    --feature "Observability Stack" \\
    --overview "Integrate Langfuse and OpenTelemetry"

Template:
  The implementation plan template is loaded from templates/implementation_plan_template.md
  Edit this file to customize the plan structure.
        """,
    )

    parser.add_argument(
        "--feature",
        type=str,
        required=True,
        help="Feature name (max 80 characters)",
    )
    parser.add_argument(
        "--overview",
        type=str,
        required=True,
        help="Feature overview/description",
    )
    parser.add_argument(
        "--steps",
        type=str,
        nargs="*",
        default=[],
        help="Implementation steps (can be specified multiple times)",
    )
    parser.add_argument(
        "--artifacts-dir",
        type=Path,
        default=Path(".claude/artifacts"),
        help="Artifacts directory (default: .claude/artifacts)",
    )
    parser.add_argument(
        "--template-dir",
        type=Path,
        default=TEMPLATE_DIR,
        help=f"Template directory (default: {TEMPLATE_DIR})",
    )

    args = parser.parse_args()

    try:
        plan_file = create_implementation_plan(
            artifacts_dir=args.artifacts_dir,
            feature=args.feature,
            overview=args.overview,
            steps=args.steps if args.steps else None,
            template_dir=args.template_dir,
        )
        print("Implementation plan created successfully")  # noqa: T201
        print(f"  Location: {plan_file.absolute()}")  # noqa: T201
        print(f"  Date: {get_today_date()}")  # noqa: T201
        print(f"  Feature: {plan_file.parent.name}")  # noqa: T201
        print(f"  Template: {args.template_dir / PLAN_TEMPLATE_FILE}")  # noqa: T201
    except (ValueError, FileExistsError, FileNotFoundError) as e:
        print(f"Error: {e}")  # noqa: T201
        sys.exit(1)


if __name__ == "__main__":
    main()
