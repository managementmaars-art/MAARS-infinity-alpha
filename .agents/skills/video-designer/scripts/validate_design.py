import argparse
import hashlib
import json
import math
import os
import sys
import urllib.request
from pathlib import Path
from typing import Optional

# Add project root to Python path
# File is at .claude/skills/video-designer/scripts/validate_design.py
# Need to go up 5 levels to reach project root
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from pydantic import ValidationError
from design_schema import DesignSceneModel
from scripts.claude_cli.claude_cli_config import ClaudeCliConfig
from scripts.enums import AssetType
from scripts.controllers.manifest_controller import ManifestController

# Font cache directory
FONT_CACHE_DIR = Path(project_root) / ".cache" / "fonts"

# Default values
DEFAULT_LINE_HEIGHT = 1.5
DEFAULT_PADDING = 8


def get_font_config_for_topic(topic: str) -> dict:
    """Get the font configuration for a topic based on its video_style."""
    manifest = ManifestController()
    manifest.set_topic(topic)
    metadata = manifest.get_metadata()

    video_style = metadata.get("video_style", "what-if")
    font_config = ClaudeCliConfig.FONT_URLS.get(video_style)

    if not font_config:
        raise ValueError(f"No font configured for video_style: {video_style}")

    return font_config


def download_font(url: str, format: str) -> Path:
    """Download font from URL and cache it locally."""
    FONT_CACHE_DIR.mkdir(parents=True, exist_ok=True)

    # Create a unique filename based on URL hash
    url_hash = hashlib.md5(url.encode()).hexdigest()[:12]
    extension = ".otf" if format == "opentype" else ".ttf"
    font_path = FONT_CACHE_DIR / f"font_{url_hash}{extension}"

    # Download if not cached
    if not font_path.exists():
        try:
            urllib.request.urlretrieve(url, font_path)
        except Exception as e:
            raise RuntimeError(f"Failed to download font from {url}: {e}")

    return font_path


def get_char_width_ratio(font_path: Path) -> float:
    """
    Extract character width ratio from font file using fontTools.

    Uses average width of uppercase letters (A-Z) for conservative estimation.
    Uppercase letters are typically wider than average, making this suitable
    for overlap detection where overestimating is safer than underestimating.

    Returns:
        charWidthRatio = avgUppercaseWidth / unitsPerEm
    """
    try:
        from fontTools.ttLib import TTFont
        font = TTFont(str(font_path))
        units_per_em = font['head'].unitsPerEm
        hmtx = font['hmtx']
        cmap = font.getBestCmap()

        uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        widths = [hmtx[cmap[ord(c)]][0] for c in uppercase if ord(c) in cmap]

        if not widths:
            # Fallback if no uppercase letters found in font
            print("Warning: No uppercase letters in font. Using default charWidthRatio=0.65", file=sys.stderr)
            return 0.65

        avg_width = sum(widths) / len(widths)
        return avg_width / units_per_em
    except ImportError:
        # fontTools not installed, use default ratio
        print("Warning: fontTools not installed. Using default charWidthRatio=0.65", file=sys.stderr)
        return 0.65
    except Exception as e:
        print(f"Warning: Could not read font metrics: {e}. Using default charWidthRatio=0.65", file=sys.stderr)
        return 0.65


def calculate_text_dimensions(
    text: str,
    font_size: float,
    char_width_ratio: float,
    line_height: float = DEFAULT_LINE_HEIGHT,
    container_width: Optional[float] = None,
    padding: float = DEFAULT_PADDING
) -> tuple[float, float]:
    """
    Calculate text element dimensions using formulas.

    Args:
        text: The text content
        font_size: Font size in pixels
        char_width_ratio: Font's average character width ratio (xAvgCharWidth / unitsPerEm)
        line_height: CSS line-height value (default 1.5)
        container_width: If set, text wraps within this width
        padding: Padding in pixels (default 8)

    Returns:
        Tuple of (element_width, element_height) including padding
    """
    # Handle explicit newlines in text
    lines = text.split('\n')
    num_explicit_lines = len(lines)

    # Width is based on the longest line
    longest_line_chars = max(len(line) for line in lines)
    text_width = longest_line_chars * font_size * char_width_ratio

    if container_width and container_width > 0:
        # Fixed container - text may wrap further
        usable_width = container_width - (padding * 2)
        if usable_width > 0 and text_width > usable_width:
            # Each explicit line may wrap into multiple lines
            total_lines = 0
            for line in lines:
                line_width = len(line) * font_size * char_width_ratio
                total_lines += math.ceil(line_width / usable_width) if line_width > usable_width else 1
            num_lines = total_lines
            width = container_width
        else:
            num_lines = num_explicit_lines
            width = text_width + (padding * 2)
    else:
        # w-fit - natural width based on longest line
        num_lines = num_explicit_lines
        width = text_width + (padding * 2)

    # Calculate height
    text_height = font_size * line_height * num_lines
    height = text_height + (padding * 2)

    return width, height


def construct_file_path(topic: str, scene_index: int) -> str:
    # Sanitize inputs to prevent path traversal
    if '..' in topic or '/' in topic or '\\' in topic:
        raise ValueError("Invalid topic name. Topic cannot contain '..' or path separators.")

    # Set topic in config
    ClaudeCliConfig.set_topic(topic)

    # Get the latest file path template
    template_path = ClaudeCliConfig.get_latest_path(AssetType.DESIGN)

    # Replace scene_index placeholder (template has {scene_index} after topic formatting)
    file_path = template_path.format(scene_index=scene_index)

    return file_path


def validate_design_file(file_path: str) -> tuple[bool, Optional[DesignSceneModel], Optional[str]]:
    # Check if file exists
    if not os.path.exists(file_path):
        return False, None, f"File not found: {file_path}"

    if not os.path.isfile(file_path):
        return False, None, f"Path exists but is not a file: {file_path}"

    # Read JSON file
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        error_msg = (
            f"JSON Syntax Error:\n"
            f"  Error: {e.msg}\n"
            f"  Location: Line {e.lineno}, Column {e.colno}\n"
            f"  Hint: The JSON structure is broken. Check for missing commas (,), "
            f"misplaced brackets ([]), or braces ({{}}) around this line."
        )
        return False, None, error_msg
    except Exception as e:
        return False, None, f"Error reading file: {str(e)}"

    # Validate using Pydantic model
    try:
        validated_model = DesignSceneModel.model_validate(data)
        return True, validated_model, None
    except ValidationError as e:
        error_msg = format_validation_errors(e, os.path.basename(file_path))
        return False, None, error_msg


def format_validation_errors(validation_error: ValidationError, filename: str) -> str:
    errors = validation_error.errors()
    error_count = len(errors)

    # Group errors by category
    type_errors = []
    value_errors = []
    missing_errors = []
    other_errors = []

    for error in errors:
        error_type = error.get('type', '')
        if 'missing' in error_type:
            missing_errors.append(error)
        elif error_type.startswith('int_') or error_type.startswith('float_') or error_type.startswith('string_') or 'type' in error_type:
            type_errors.append(error)
        elif 'value_error' in error_type or error_type.startswith('greater_') or error_type.startswith('less_'):
            value_errors.append(error)
        else:
            other_errors.append(error)

    # Build error message
    lines = [
        f"\n[FAIL] Found {error_count} validation error(s) in '{filename}':\n"
    ]

    # Print missing fields
    if missing_errors:
        lines.append("Missing Required Fields:")
        for i, error in enumerate(missing_errors, 1):
            field_path = format_error_location(error['loc'])
            lines.append(f"  {i}. Field '{field_path}' is required but missing")
        lines.append("")

    # Print type errors
    if type_errors:
        lines.append("Type Errors:")
        for i, error in enumerate(type_errors, 1):
            field_path = format_error_location(error['loc'])
            msg = error.get('msg', 'Invalid type')
            input_value = error.get('input')
            lines.append(f"  {i}. {field_path}: {msg}")
            if input_value is not None:
                lines.append(f"      Got: {repr(input_value)}")
        lines.append("")

    # Print value errors
    if value_errors:
        lines.append("Value Errors:")
        for i, error in enumerate(value_errors, 1):
            field_path = format_error_location(error['loc'])
            msg = error.get('msg', 'Invalid value')
            lines.append(f"  {i}. {field_path}: {msg}")
        lines.append("")

    # Print other errors
    if other_errors:
        lines.append("Other Validation Errors:")
        for i, error in enumerate(other_errors, 1):
            field_path = format_error_location(error['loc'])
            msg = error.get('msg', 'Validation failed')
            lines.append(f"  {i}. {field_path}: {msg}")
        lines.append("")

    lines.append("Fix all these errors and re-run this script.\n")

    return "\n".join(lines)


def format_error_location(loc: tuple) -> str:
    parts = []
    for item in loc:
        if isinstance(item, int):
            parts[-1] = f"{parts[-1]}[{item}]"
        else:
            parts.append(str(item))
    return ".".join(parts)


def get_element_bounds(element: dict) -> tuple[float, float, float, float]:
    """
    Get element bounding box (left, top, right, bottom).

    x,y is ALWAYS the center point (universal coordinate system rule).
    textAlign only affects CSS text flow for multi-line text, not positioning.
    """
    x = element.get("x", 0)
    y = element.get("y", 0)
    width = element.get("_calculated_width", 0)
    height = element.get("_calculated_height", 0)

    # x,y is always center (universal rule)
    left = x - width / 2
    right = x + width / 2
    top = y - height / 2
    bottom = y + height / 2

    return left, top, right, bottom


def check_overlap(bounds1: tuple, bounds2: tuple, min_gap: int = 5) -> tuple[bool, int]:
    """
    Check if two bounding boxes are too close (gap < min_gap) or overlapping.

    Args:
        bounds1, bounds2: Tuples of (left, top, right, bottom)
        min_gap: Minimum required gap in pixels (default 5px)

    Returns:
        Tuple of (is_too_close, gap_or_overlap_amount)
        - Positive value = gap between elements
        - Negative value = overlap amount
    """
    left1, top1, right1, bottom1 = bounds1
    left2, top2, right2, bottom2 = bounds2

    # Calculate gap/overlap in each dimension
    # Positive = gap, Negative = overlap
    h_gap = max(left1, left2) - min(right1, right2)
    v_gap = max(top1, top2) - min(bottom1, bottom2)

    # If either gap is positive (no overlap in that dimension), use the smaller one
    # If both are negative (overlap in both), use the larger (less negative) one
    if h_gap >= 0 or v_gap >= 0:
        # No overlap - check if gap is too small
        gap = max(h_gap, v_gap)  # The actual separation
        return gap < min_gap, int(gap)
    else:
        # Actual overlap (both negative)
        overlap = max(h_gap, v_gap)  # Less negative = smaller overlap
        return True, int(overlap)


def is_full_viewport_element(element: dict, viewport_width: int, viewport_height: int, threshold: float = 0.95) -> bool:
    """
    Check if an element covers most of the viewport (likely a background).

    Args:
        element: The element dict
        viewport_width: Viewport width in pixels
        viewport_height: Viewport height in pixels
        threshold: Coverage threshold (default 0.95 = 95%)

    Returns:
        True if element covers >= threshold of viewport
    """
    width = element.get("width", 0)
    height = element.get("height", 0)

    if width <= 0 or height <= 0:
        return False

    coverage = (width * height) / (viewport_width * viewport_height)
    return coverage >= threshold


def validate_no_overlaps(design_data: dict, topic: str, check_types: list[str] = None) -> tuple[bool, list[str]]:
    """
    Validate that elements don't overlap using calculated/explicit dimensions.

    Args:
        design_data: The parsed design JSON
        topic: Topic name to get font for dimension calculation
        check_types: List of element types to check (default: ["text", "shape", "asset", "pattern"])

    Returns:
        Tuple of (is_valid, list of error messages)
    """
    if check_types is None:
        check_types = ["text", "shape", "asset", "pattern"]

    errors = []
    elements = design_data.get("elements", [])

    # Get viewport dimensions for full-viewport element detection
    viewport_str = design_data.get("video_metadata", {}).get("viewport_size", "1920x1080")
    try:
        viewport_width, viewport_height = map(int, viewport_str.split("x"))
    except ValueError:
        viewport_width, viewport_height = 1920, 1080

    # Get font configuration and char width ratio
    try:
        font_config = get_font_config_for_topic(topic)
        font_path = download_font(font_config["url"], font_config["format"])
        char_width_ratio = get_char_width_ratio(font_path)
    except Exception as e:
        return False, [f"Failed to load font for topic '{topic}': {e}"]

    # Build set of bgID relationships (element pairs that intentionally overlap)
    # If element A has bgID pointing to element B, they're meant to overlap
    bgid_pairs = set()
    for el in elements:
        bgid = el.get("bgID")
        if bgid:
            el_id = el.get("id")
            if el_id:
                # Store as frozenset so order doesn't matter
                bgid_pairs.add(frozenset([el_id, bgid]))

    # Build list of elements with CALCULATED dimensions for text, explicit for shape/asset/pattern
    checkable_elements = []
    for el in elements:
        if el.get("type") not in check_types:
            continue

        if el.get("type") == "text":
            text = el.get("text", "")
            font_size = el.get("fontSize")
            if not text or not font_size:
                continue

            # Get optional parameters from design
            line_height = el.get("lineHeight", DEFAULT_LINE_HEIGHT)
            container_width = el.get("containerWidth")  # Optional fixed width
            padding = el.get("padding", DEFAULT_PADDING)

            # Calculate position-based available width
            # CSS calculates available width BEFORE translate is applied:
            # For element at left: x, available_width = viewport_width - x
            # This causes text to wrap even with w-fit if text exceeds available space
            x = el.get("x", 0)
            position_based_width = viewport_width - x if x > 0 else viewport_width

            # Use the more restrictive of containerWidth or position-based width
            effective_container_width = container_width
            if effective_container_width is None or position_based_width < effective_container_width:
                effective_container_width = position_based_width

            # Calculate dimensions using formulas
            calc_width, calc_height = calculate_text_dimensions(
                text=text,
                font_size=font_size,
                char_width_ratio=char_width_ratio,
                line_height=line_height,
                container_width=effective_container_width,
                padding=padding
            )

            el_copy = dict(el)
            el_copy["_calculated_width"] = calc_width
            el_copy["_calculated_height"] = calc_height
            checkable_elements.append(el_copy)
        else:
            # For shape/asset/pattern elements, use provided width/height
            if el.get("width") and el.get("height"):
                # Skip full-viewport elements (backgrounds)
                if is_full_viewport_element(el, viewport_width, viewport_height):
                    continue

                el_copy = dict(el)
                el_copy["_calculated_width"] = el.get("width")
                el_copy["_calculated_height"] = el.get("height")
                checkable_elements.append(el_copy)

    # Check each pair
    for i, el1 in enumerate(checkable_elements):
        bounds1 = get_element_bounds(el1)

        for el2 in checkable_elements[i+1:]:
            # Skip if this pair has a bgID relationship (intentional overlap)
            pair_key = frozenset([el1.get("id"), el2.get("id")])
            if pair_key in bgid_pairs:
                continue

            bounds2 = get_element_bounds(el2)

            is_too_close, distance = check_overlap(bounds1, bounds2)
            if is_too_close:
                if distance < 0:
                    issue = f"overlaps by {-distance}px"
                else:
                    issue = f"gap only {distance}px (need 5px min)"
                errors.append(
                    f"  - '{el1.get('id')}' & '{el2.get('id')}': {issue}\n"
                    f"      {el1.get('id')}: x={el1.get('x')}, y={el1.get('y')}, "
                    f"w={el1.get('_calculated_width'):.0f}, h={el1.get('_calculated_height'):.0f}\n"
                    f"      {el2.get('id')}: x={el2.get('x')}, y={el2.get('y')}, "
                    f"w={el2.get('_calculated_width'):.0f}, h={el2.get('_calculated_height'):.0f}"
                )

    return len(errors) == 0, errors


def validate_viewport_bounds(design_data: dict, topic: str, check_types: list[str] = None) -> tuple[bool, list[str]]:
    """
    Validate that elements don't go outside viewport boundaries.

    Args:
        design_data: The parsed design JSON
        topic: Topic name to get font for dimension calculation
        check_types: List of element types to check (default: ["text", "shape", "asset", "pattern"])

    Returns:
        Tuple of (is_valid, list of error messages)
    """
    if check_types is None:
        check_types = ["text", "shape", "asset", "pattern"]

    errors = []
    elements = design_data.get("elements", [])

    # Get viewport dimensions
    viewport_str = design_data.get("video_metadata", {}).get("viewport_size", "1920x1080")
    try:
        viewport_width, viewport_height = map(int, viewport_str.split("x"))
    except ValueError:
        return False, [f"Invalid viewport_size format: {viewport_str}"]

    # Get font configuration and char width ratio
    try:
        font_config = get_font_config_for_topic(topic)
        font_path = download_font(font_config["url"], font_config["format"])
        char_width_ratio = get_char_width_ratio(font_path)
    except Exception as e:
        return False, [f"Failed to load font for topic '{topic}': {e}"]

    # Check each element
    for el in elements:
        if el.get("type") not in check_types:
            continue

        el_type = el.get("type")

        if el_type == "text":
            text = el.get("text", "")
            font_size = el.get("fontSize")
            if not text or not font_size:
                continue

            # Get optional parameters from design
            line_height = el.get("lineHeight", DEFAULT_LINE_HEIGHT)
            container_width = el.get("containerWidth")
            padding = el.get("padding", DEFAULT_PADDING)

            # Calculate position-based available width
            # CSS calculates available width BEFORE translate is applied:
            # For element at left: x, available_width = viewport_width - x
            x = el.get("x", 0)
            position_based_width = viewport_width - x if x > 0 else viewport_width

            # Use the more restrictive of containerWidth or position-based width
            effective_container_width = container_width
            if effective_container_width is None or position_based_width < effective_container_width:
                effective_container_width = position_based_width

            # Calculate dimensions
            calc_width, calc_height = calculate_text_dimensions(
                text=text,
                font_size=font_size,
                char_width_ratio=char_width_ratio,
                line_height=line_height,
                container_width=effective_container_width,
                padding=padding
            )

            el_copy = dict(el)
            el_copy["_calculated_width"] = calc_width
            el_copy["_calculated_height"] = calc_height

            # Get bounds
            left, top, right, bottom = get_element_bounds(el_copy)

            # Check boundaries
            boundary_issues = []
            if left < 0:
                boundary_issues.append(f"left edge at {left:.0f}px (outside by {-left:.0f}px)")
            if right > viewport_width:
                boundary_issues.append(f"right edge at {right:.0f}px (outside by {right - viewport_width:.0f}px)")
            if top < 0:
                boundary_issues.append(f"top edge at {top:.0f}px (outside by {-top:.0f}px)")
            if bottom > viewport_height:
                boundary_issues.append(f"bottom edge at {bottom:.0f}px (outside by {bottom - viewport_height:.0f}px)")

            if boundary_issues:
                align = el.get("textAlign", "center")
                errors.append(
                    f"  - '{el.get('id')}' (text): outside viewport ({viewport_width}x{viewport_height})\n"
                    f"      text: \"{text[:30]}{'...' if len(text) > 30 else ''}\"\n"
                    f"      position: x={el.get('x')}, y={el.get('y')}, textAlign={align}\n"
                    f"      calculated: w={calc_width:.0f}, h={calc_height:.0f}\n"
                    f"      issues: {', '.join(boundary_issues)}"
                )

        elif el_type in ["shape", "asset", "pattern"]:
            # For shape/asset/pattern, use explicit width/height
            width = el.get("width")
            height = el.get("height")
            if not width or not height:
                continue

            # Skip full-viewport elements (backgrounds)
            if is_full_viewport_element(el, viewport_width, viewport_height):
                continue

            el_copy = dict(el)
            el_copy["_calculated_width"] = width
            el_copy["_calculated_height"] = height

            # Get bounds
            left, top, right, bottom = get_element_bounds(el_copy)

            # Check boundaries
            boundary_issues = []
            if left < 0:
                boundary_issues.append(f"left edge at {left:.0f}px (outside by {-left:.0f}px)")
            if right > viewport_width:
                boundary_issues.append(f"right edge at {right:.0f}px (outside by {right - viewport_width:.0f}px)")
            if top < 0:
                boundary_issues.append(f"top edge at {top:.0f}px (outside by {-top:.0f}px)")
            if bottom > viewport_height:
                boundary_issues.append(f"bottom edge at {bottom:.0f}px (outside by {bottom - viewport_height:.0f}px)")

            if boundary_issues:
                errors.append(
                    f"  - '{el.get('id')}' ({el_type}): outside viewport ({viewport_width}x{viewport_height})\n"
                    f"      position: x={el.get('x')}, y={el.get('y')}\n"
                    f"      size: w={width:.0f}, h={height:.0f}\n"
                    f"      issues: {', '.join(boundary_issues)}"
                )

    return len(errors) == 0, errors


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
  python scripts/validation/validate_design.py --file-path Outputs/missle-infographic/Design/v1/Design_9.json
        """
    )

    parser.add_argument('--topic', help='Topic name')
    parser.add_argument('--scene-index', type=int, help='Scene index')
    parser.add_argument('--file-path', help='Direct path to design file (alternative to --topic and --scene-index)')

    args = parser.parse_args()

    # Determine file path
    if args.file_path:
        file_path = args.file_path
    elif args.topic and args.scene_index is not None:
        try:
            file_path = construct_file_path(args.topic, args.scene_index)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        parser.print_help()
        print("\nError: Either --file-path OR (--topic and --scene-index) must be provided.", file=sys.stderr)
        sys.exit(1)

    # Validate file extension
    if not file_path.lower().endswith('.json'):
        print(f"Error: The provided file '{file_path}' is not a .json file.", file=sys.stderr)
        sys.exit(1)

    # Validate the file (schema validation)
    is_valid, validated_model, error_message = validate_design_file(file_path)

    if not is_valid:
        print(error_message, file=sys.stderr)
        sys.exit(1)

    # Run overlap validation if topic is provided
    topic = args.topic
    if not topic and args.file_path:
        # Extract topic from file path: Outputs/{topic}/Design/...
        parts = args.file_path.replace('\\', '/').split('/')
        if 'Outputs' in parts:
            idx = parts.index('Outputs')
            if idx + 1 < len(parts):
                topic = parts[idx + 1]

    if topic:
        with open(file_path, 'r', encoding='utf-8') as f:
            design_data = json.load(f)

        has_errors = False

        # Validate no overlaps using calculated dimensions
        no_overlaps, overlap_errors = validate_no_overlaps(design_data, topic)
        if not no_overlaps:
            print(f"\n[FAIL] Element overlap detected in '{os.path.basename(file_path)}':\n", file=sys.stderr)
            for err in overlap_errors:
                print(err, file=sys.stderr)
            print("\nFix overlapping elements by adjusting x, y positions.\n", file=sys.stderr)
            has_errors = True

        # Validate viewport boundaries (always run, don't skip on overlap errors)
        in_bounds, boundary_errors = validate_viewport_bounds(design_data, topic)
        if not in_bounds:
            print(f"\n[FAIL] Element outside viewport in '{os.path.basename(file_path)}':\n", file=sys.stderr)
            for err in boundary_errors:
                print(err, file=sys.stderr)
            print("\nFix by adjusting x, y positions or reducing size.\n", file=sys.stderr)
            has_errors = True

        if has_errors:
            sys.exit(1)

    print(f"\n[PASS] Validation successful for '{os.path.basename(file_path)}'")


if __name__ == "__main__":
    main()
