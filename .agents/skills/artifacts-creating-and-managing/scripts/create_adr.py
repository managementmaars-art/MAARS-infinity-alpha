#!/usr/bin/env python3
"""Create an Architecture Decision Record (ADR) artifact.

This script creates a new ADR file in the docs/adr/{status_folder}/ directory
with auto-incremented numbering and a standard template structure.

The project uses status-based folders:
- in_progress/ - for proposed and in-progress ADRs
- not_started/ - for ADRs not yet started
- accepted/ - for accepted ADRs
- deprecated/ - for deprecated ADRs

Templates are loaded from the templates/ directory and can be customized.

Example usage:
    python create_adr.py --title "Use Langchain for Agent Coordination" \\
        --status proposed \\
        --context "Need to coordinate multiple agents efficiently"
"""

import argparse
import re
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


MAX_TITLE_LENGTH: Final[int] = 100

# Map status to folder name
STATUS_FOLDER_MAP: Final[dict[str, str]] = {
    "proposed": "in_progress",
    "in_progress": "in_progress",
    "not_started": "not_started",
    "accepted": "accepted",
    "deprecated": "deprecated",
    "superseded": "superseded",
}

VALID_STATUSES: Final[frozenset[str]] = frozenset(STATUS_FOLDER_MAP.keys())

# Template directory relative to this script
TEMPLATE_DIR: Final[Path] = Path(__file__).parent.parent / "templates"
ADR_TEMPLATE_FILE: Final[str] = "adr_template.md"


def get_next_adr_number(adr_base_dir: Path) -> int:
    """Get the next ADR number by scanning all status folders.

    Args:
        adr_base_dir: Base ADR directory (docs/adr/).

    Returns:
        Next ADR number (e.g., 4 if highest existing is 003).
    """
    if not adr_base_dir.exists():
        return 1

    pattern = re.compile(r"^(\d+)-")
    numbers: list[int] = []

    # Scan all status folders for existing ADR numbers
    for status_folder in STATUS_FOLDER_MAP.values():
        folder_path = adr_base_dir / status_folder
        if not folder_path.exists():
            continue

        for item in folder_path.iterdir():
            # Check both directories and files
            match = pattern.match(item.name)
            if match:
                numbers.append(int(match.group(1)))

    return max(numbers, default=0) + 1


def validate_title(title: str) -> None:
    """Validate ADR title format.

    Args:
        title: Title to validate.

    Raises:
        ValueError: If title is empty or too long.
    """
    validate_non_empty(title, "Title")
    validate_max_length(title, MAX_TITLE_LENGTH, "Title")


def validate_status(status: str) -> None:
    """Validate ADR status value.

    Args:
        status: Status to validate.

    Raises:
        ValueError: If status is not valid.
    """
    if status not in VALID_STATUSES:
        raise ValueError(f"Status must be one of: {', '.join(sorted(VALID_STATUSES))}")


def get_status_folder(status: str) -> str:
    """Get the folder name for a given status.

    Args:
        status: ADR status.

    Returns:
        Folder name for the status.
    """
    return STATUS_FOLDER_MAP[status]


def create_adr_content(
    number: int,
    title: str,
    status: str,
    context: str,
    template_dir: Path,
) -> str:
    """Create ADR markdown content from template.

    Args:
        number: ADR number (e.g., 4).
        title: Decision title.
        status: Status (proposed/accepted/deprecated/superseded).
        context: Context summary explaining the decision background.
        template_dir: Directory containing template files.

    Returns:
        Formatted ADR markdown content.
    """
    template_file = template_dir / ADR_TEMPLATE_FILE
    template = load_template(template_file)

    date_str = get_today_date()
    context_text = (
        context
        if context
        else "[Describe the context and background for this decision.]"
    )

    replacements = {
        "NUMBER": f"{number:03d}",
        "TITLE": title,
        "STATUS": status.upper(),
        "DATE": date_str,
        "CONTEXT": context_text,
    }

    return fill_template(template, replacements)


def create_adr(
    adr_base_dir: Path,
    title: str,
    status: str = "proposed",
    context: str = "",
    template_dir: Path = TEMPLATE_DIR,
) -> Path:
    """Create a new ADR file.

    Args:
        adr_base_dir: Base ADR directory (docs/adr/).
        title: ADR title.
        status: Decision status (default: proposed).
        context: Context summary (optional).
        template_dir: Directory containing template files.

    Returns:
        Path to created ADR file.

    Raises:
        ValueError: If validation fails.
        FileExistsError: If ADR file already exists.
        FileNotFoundError: If template file not found.
    """
    # Validate inputs
    validate_title(title)
    validate_status(status)

    # Get next number scanning all status folders
    number = get_next_adr_number(adr_base_dir)
    slug = slugify(title)

    # Determine target folder based on status
    status_folder = get_status_folder(status)
    target_dir = adr_base_dir / status_folder
    adr_folder = target_dir / f"{number:03d}-{slug}"

    if adr_folder.exists():
        raise FileExistsError(f"ADR directory already exists: {adr_folder}")

    # Create directory
    adr_folder.mkdir(parents=True, exist_ok=False)

    # Create README.md from template
    adr_file = adr_folder / "README.md"
    content = create_adr_content(number, title, status, context, template_dir)
    adr_file.write_text(content, encoding="utf-8")

    return adr_file


def main() -> None:
    """Parse arguments and create ADR."""
    parser = argparse.ArgumentParser(
        description="Create a new Architecture Decision Record (ADR)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create ADR with minimal arguments (goes to in_progress/)
  python create_adr.py --title "Use Langchain for Coordination"

  # Create ADR with full details
  python create_adr.py \\
    --title "Use Langchain for Multi-Agent Coordination" \\
    --status proposed \\
    --context "Need efficient coordination between multiple Claude agents"

  # Create ADR in not_started folder
  python create_adr.py \\
    --title "Implement CQRS Pattern" \\
    --status not_started

Status folder mapping:
  proposed, in_progress -> docs/adr/in_progress/
  not_started           -> docs/adr/not_started/
  accepted              -> docs/adr/accepted/
  deprecated            -> docs/adr/deprecated/
  superseded            -> docs/adr/superseded/

Template:
  The ADR template is loaded from templates/adr_template.md
  Edit this file to customize the ADR structure.
        """,
    )

    parser.add_argument(
        "--title",
        type=str,
        required=True,
        help="ADR title (max 100 characters)",
    )
    parser.add_argument(
        "--status",
        type=str,
        default="proposed",
        choices=sorted(VALID_STATUSES),
        help="Decision status (default: proposed)",
    )
    parser.add_argument(
        "--context",
        type=str,
        default="",
        help="Context summary explaining the decision background",
    )
    parser.add_argument(
        "--adr-dir",
        type=Path,
        default=Path("docs/adr"),
        help="Base ADR directory (default: docs/adr)",
    )
    parser.add_argument(
        "--template-dir",
        type=Path,
        default=TEMPLATE_DIR,
        help=f"Template directory (default: {TEMPLATE_DIR})",
    )

    args = parser.parse_args()

    try:
        adr_file = create_adr(
            adr_base_dir=args.adr_dir,
            title=args.title,
            status=args.status,
            context=args.context,
            template_dir=args.template_dir,
        )
        status_folder = get_status_folder(args.status)
        print("ADR created successfully")  # noqa: T201
        print(f"  Location: {adr_file.absolute()}")  # noqa: T201
        print(f"  Status folder: {status_folder}/")  # noqa: T201
        print(f"  ADR: {adr_file.parent.name}")  # noqa: T201
        print(f"  Template: {args.template_dir / ADR_TEMPLATE_FILE}")  # noqa: T201
    except (ValueError, FileExistsError, FileNotFoundError) as e:
        print(f"Error: {e}")  # noqa: T201
        sys.exit(1)


if __name__ == "__main__":
    main()
