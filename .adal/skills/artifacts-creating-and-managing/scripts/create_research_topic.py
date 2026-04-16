#!/usr/bin/env python3
"""Create a research/spike topic artifact.

This script creates a new research topic in the .claude/artifacts/ directory
with today's date and a standard template structure.

Templates are loaded from the templates/ directory and can be customized.

Example usage:
    python create_research_topic.py \\
        --topic "Langfuse Integration" \\
        --objective "Evaluate Langfuse for LLM observability and tracing" \\
        --questions "Does it support custom events?" "What's the pricing model?"
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


MAX_TOPIC_LENGTH: Final[int] = 80

# Template directory relative to this script
TEMPLATE_DIR: Final[Path] = Path(__file__).parent.parent / "templates"
RESEARCH_TEMPLATE_FILE: Final[str] = "research_template.md"


def validate_topic(topic: str) -> None:
    """Validate research topic format.

    Args:
        topic: Topic name to validate.

    Raises:
        ValueError: If topic is empty or too long.
    """
    validate_non_empty(topic, "Topic name")
    validate_max_length(topic, MAX_TOPIC_LENGTH, "Topic name")


def validate_objective(objective: str) -> None:
    """Validate research objective format.

    Args:
        objective: Objective to validate.

    Raises:
        ValueError: If objective is empty.
    """
    validate_non_empty(objective, "Objective")


def format_questions(questions: list[str]) -> str:
    """Format list of questions as markdown.

    Args:
        questions: List of question strings.

    Returns:
        Formatted markdown list of questions.
    """
    if not questions:
        return "- [Add key questions to answer]\n"

    formatted = ""
    for raw_question in questions:
        question = raw_question.strip()
        if question:
            formatted += f"- {question}\n"

    return formatted or "- [Add key questions to answer]\n"


def create_research_content(
    topic: str,
    objective: str,
    questions: list[str],
    template_dir: Path,
) -> str:
    """Create research document markdown content from template.

    Args:
        topic: Research topic name.
        objective: Research objective/goal.
        questions: List of key questions to answer.
        template_dir: Directory containing template files.

    Returns:
        Formatted research markdown content.
    """
    template_file = template_dir / RESEARCH_TEMPLATE_FILE
    template = load_template(template_file)

    date_str = get_today_date()
    questions_md = format_questions(questions)

    replacements = {
        "TOPIC": topic,
        "DATE": date_str,
        "OBJECTIVE": objective,
        "QUESTIONS": questions_md,
    }

    return fill_template(template, replacements)


def create_research_topic(
    artifacts_dir: Path,
    topic: str,
    objective: str,
    questions: list[str] | None = None,
    template_dir: Path = TEMPLATE_DIR,
) -> Path:
    """Create a new research topic artifact.

    Args:
        artifacts_dir: Base artifacts directory (.claude/artifacts/).
        topic: Research topic name.
        objective: Research objective/goal.
        questions: List of key questions (optional).
        template_dir: Directory containing template files.

    Returns:
        Path to created research file.

    Raises:
        ValueError: If validation fails.
        FileExistsError: If file already exists.
        FileNotFoundError: If template file not found.
    """
    # Validate inputs
    validate_topic(topic)
    validate_objective(objective)

    if questions is None:
        questions = []

    # Create directory structure
    today = get_today_date()
    topic_slug = slugify(topic)

    # Create date folder and analysis subfolder
    date_dir = artifacts_dir / today
    analysis_dir = date_dir / "analysis"
    topic_dir = analysis_dir / topic_slug

    # Check if directory exists
    if topic_dir.exists():
        raise FileExistsError(f"Research topic already exists: {topic_dir}")

    # Create directories
    topic_dir.mkdir(parents=True, exist_ok=False)

    # Create research document from template
    research_file = topic_dir / "RESEARCH_SUMMARY.md"
    content = create_research_content(topic, objective, questions, template_dir)
    research_file.write_text(content, encoding="utf-8")

    return research_file


def main() -> None:
    """Parse arguments and create research topic."""
    parser = argparse.ArgumentParser(
        description="Create a new research/spike topic artifact",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create research topic with minimal arguments
  python create_research_topic.py \\
    --topic "Langfuse Integration" \\
    --objective "Evaluate Langfuse for LLM observability"

  # Create research topic with questions
  python create_research_topic.py \\
    --topic "Async Context Manager Patterns" \\
    --objective "Research best practices for async context managers in Python" \\
    --questions "How do we handle async cleanup?" "What are common pitfalls?" \\
    --questions "How does pytest handle async fixtures?"

  # Use custom artifacts directory
  python create_research_topic.py \\
    --artifacts-dir /path/to/artifacts \\
    --topic "Framework Comparison" \\
    --objective "Compare React vs Vue vs Svelte"

Template:
  The research template is loaded from templates/research_template.md
  Edit this file to customize the research structure.
        """,
    )

    parser.add_argument(
        "--topic",
        type=str,
        required=True,
        help="Research topic name (max 80 characters)",
    )
    parser.add_argument(
        "--objective",
        type=str,
        required=True,
        help="Research objective or goal",
    )
    parser.add_argument(
        "--questions",
        type=str,
        nargs="*",
        default=[],
        help="Key questions to answer (can be specified multiple times)",
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
        research_file = create_research_topic(
            artifacts_dir=args.artifacts_dir,
            topic=args.topic,
            objective=args.objective,
            questions=args.questions if args.questions else None,
            template_dir=args.template_dir,
        )
        print("Research topic created successfully")  # noqa: T201
        print(f"  Location: {research_file.absolute()}")  # noqa: T201
        print(f"  Date: {get_today_date()}")  # noqa: T201
        print(f"  Topic: {research_file.parent.name}")  # noqa: T201
        print(f"  Template: {args.template_dir / RESEARCH_TEMPLATE_FILE}")  # noqa: T201
    except (ValueError, FileExistsError, FileNotFoundError) as e:
        print(f"Error: {e}")  # noqa: T201
        sys.exit(1)


if __name__ == "__main__":
    main()
