import argparse
import json
import sys
import re


def merge_paths(paths: list) -> str:
    """
    Merge multiple path strings into a single continuous path.
    Removes M (moveTo) commands from all paths except the first.

    paths: list of path d-attribute strings
           e.g. ["M 50 400 L 150 100", "M 150 100 Q 250 400 350 250", ...]

    Returns: single merged path string
    """
    if not paths:
        return ""

    if len(paths) == 1:
        return paths[0].strip()

    merged = [paths[0].strip()]

    for path in paths[1:]:
        stripped = path.strip()
        # Remove leading M/m command with its coordinates
        # Matches: "M 100 200", "M100 200", "m 100 200"
        stripped = re.sub(r'^[Mm]\s*[-\d.]+\s+[-\d.]+\s*', '', stripped)
        if stripped:
            merged.append(stripped)

    return ' '.join(merged)


def main():
    parser = argparse.ArgumentParser(
        description="Merge multiple SVG path strings into a single continuous path.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example:
  python merge-paths.py --paths '["M 50 400 L 150 100", "M 150 100 Q 250 400 350 250", "M 350 250 L 500 250"]'

  Output: M 50 400 L 150 100 Q 250 400 350 250 L 500 250
        """
    )

    parser.add_argument(
        "--paths",
        type=str,
        required=True,
        help="JSON array of path d-attribute strings"
    )

    args = parser.parse_args()

    try:
        paths = json.loads(args.paths)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(paths, list):
        print("Error: --paths must be a JSON array", file=sys.stderr)
        sys.exit(1)

    result = merge_paths(paths)
    print(result)


if __name__ == "__main__":
    main()
