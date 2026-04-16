"""
Bounding Box Validation Script for Design Elements

Validates design elements for:
1. Elements going out of screen bounds
2. Elements overlapping with each other
3. Elements animating out of screen bounds (during scale animations)

Usage:
    python bounding_check.py <scene_index>

Coordinate System:
    - Position (x, y) represents the CENTER of the element
    - (0, 0) is the TOP-LEFT of the screen
    - Viewport: 1080x1920 (portrait) or 1920x1080 (landscape)
"""

import sys
import json
import os
import argparse
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

# Add project root to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))

from scripts.claude_cli import claude_cli_config
from scripts.controllers.manifest_controller import ManifestController
from scripts.enums import AssetType
from scripts.logging_config import get_utility_logger, set_console_logging
from scripts.claude_cli.claude_cli_config import ClaudeCliConfig
set_console_logging(False)
# Initialize logger
logger = get_utility_logger('BoundingCheck')


@dataclass
class BoundingBox:
    left: float
    right: float
    top: float
    bottom: float

    @property
    def width(self) -> float:
        return self.right - self.left

    @property
    def height(self) -> float:
        return self.bottom - self.top


@dataclass
class Issue:
    element_id: str
    issue_type: str
    description: str
    details: Dict[str, Any]


def get_design_path(scene_index: int) -> str:
    """Get the path to the latest design JSON for a scene."""
    path = ClaudeCliConfig.get_latest_path(AssetType.DESIGN).format(scene_index=scene_index)
    logger.debug(f"Design path for scene {scene_index}: {path}")
    return path


def get_viewport_dimensions() -> Tuple[int, int]:
    """Get viewport width and height from manifest."""
    manifest = ManifestController()
    if ClaudeCliConfig.TOPIC:
        manifest.set_topic(ClaudeCliConfig.TOPIC)
    metadata = manifest.get_metadata()
    width = metadata['viewport_width']
    height = metadata['viewport_height']
    logger.debug(f"Viewport dimensions: {width}x{height}")
    return width, height


def calculate_bounding_box(element: Dict, scale: float = 1.0) -> Optional[BoundingBox]:
    """
    Calculate bounding box from element position and size.
    Position is the CENTER of the element.
    """
    styles = element.get('styles', {})
    position = styles.get('position', {})
    size = styles.get('size', {})

    x = position.get('x')
    y = position.get('y')
    width = size.get('width')
    height = size.get('height')

    if x is None or y is None or width is None or height is None:
        logger.warning(f"Element '{element.get('id', 'unknown')}' missing position or size data")
        return None

    # Apply scale (scales from center)
    scaled_width = width * scale
    scaled_height = height * scale

    return BoundingBox(
        left=x - scaled_width / 2,
        right=x + scaled_width / 2,
        top=y - scaled_height / 2,
        bottom=y + scaled_height / 2
    )


def get_max_animated_scale(element: Dict) -> float:
    """Get the maximum scale value from animation actions."""
    initial_scale = element.get('styles', {}).get('scale', 1.0)
    max_scale = initial_scale

    animation = element.get('animation', {})
    actions = animation.get('actions', [])

    for action in actions:
        target = action.get('targetProperty', '')
        if 'scale' in target.lower():
            value = action.get('value', initial_scale)
            if isinstance(value, (int, float)):
                max_scale = max(max_scale, value)

    return max_scale


def get_timing_window(element: Dict) -> Tuple[int, int]:
    """Get the enter and exit time for an element."""
    timing = element.get('timing', {})
    enter_on = timing.get('enterOn', 0)
    exit_on = timing.get('exitOn', float('inf'))
    return enter_on, exit_on


def timing_windows_overlap(elem1: Dict, elem2: Dict) -> Tuple[bool, int, int]:
    """Check if two elements' timing windows overlap. Returns overlap status and overlap period."""
    enter1, exit1 = get_timing_window(elem1)
    enter2, exit2 = get_timing_window(elem2)

    overlap_start = max(enter1, enter2)
    overlap_end = min(exit1, exit2)

    overlaps = overlap_start < overlap_end
    return overlaps, overlap_start, overlap_end


def check_screen_bounds(
    element_id: str,
    bbox: BoundingBox,
    viewport_width: int,
    viewport_height: int,
    is_animated: bool = False,
    scale: float = 1.0
) -> List[Issue]:
    """Check if bounding box is within screen bounds."""
    issues = []
    prefix = "ANIMATED_OUT" if is_animated else "OUT_OF_BOUNDS"

    if bbox.left < 0:
        amount = abs(bbox.left)
        if is_animated:
            desc = f"Element '{element_id}' animates out on LEFT when scaled to {scale}x (left edge reaches {bbox.left:.1f}px)"
        else:
            desc = f"Element '{element_id}' exits screen on LEFT by {amount:.1f}px (left edge at {bbox.left:.1f}px)"
        issues.append(Issue(
            element_id=element_id,
            issue_type=f"{prefix}_LEFT",
            description=desc,
            details={"amount": amount, "edge_position": bbox.left, "scale": scale}
        ))
        logger.info(f"Found issue: {desc}")

    if bbox.right > viewport_width:
        amount = bbox.right - viewport_width
        if is_animated:
            desc = f"Element '{element_id}' animates out on RIGHT when scaled to {scale}x (right edge reaches {bbox.right:.1f}px, screen width: {viewport_width}px)"
        else:
            desc = f"Element '{element_id}' exits screen on RIGHT by {amount:.1f}px (right edge at {bbox.right:.1f}px, screen width: {viewport_width}px)"
        issues.append(Issue(
            element_id=element_id,
            issue_type=f"{prefix}_RIGHT",
            description=desc,
            details={"amount": amount, "edge_position": bbox.right, "scale": scale}
        ))
        logger.info(f"Found issue: {desc}")

    if bbox.top < 0:
        amount = abs(bbox.top)
        if is_animated:
            desc = f"Element '{element_id}' animates out on TOP when scaled to {scale}x (top edge reaches {bbox.top:.1f}px)"
        else:
            desc = f"Element '{element_id}' exits screen on TOP by {amount:.1f}px (top edge at {bbox.top:.1f}px)"
        issues.append(Issue(
            element_id=element_id,
            issue_type=f"{prefix}_TOP",
            description=desc,
            details={"amount": amount, "edge_position": bbox.top, "scale": scale}
        ))
        logger.info(f"Found issue: {desc}")

    if bbox.bottom > viewport_height:
        amount = bbox.bottom - viewport_height
        if is_animated:
            desc = f"Element '{element_id}' animates out on BOTTOM when scaled to {scale}x (bottom edge reaches {bbox.bottom:.1f}px, screen height: {viewport_height}px)"
        else:
            desc = f"Element '{element_id}' exits screen on BOTTOM by {amount:.1f}px (bottom edge at {bbox.bottom:.1f}px, screen height: {viewport_height}px)"
        issues.append(Issue(
            element_id=element_id,
            issue_type=f"{prefix}_BOTTOM",
            description=desc,
            details={"amount": amount, "edge_position": bbox.bottom, "scale": scale}
        ))
        logger.info(f"Found issue: {desc}")

    return issues


def is_text_element(element: Dict) -> bool:
    """Check if an element is a text element."""
    return element.get('type', '').lower() == 'text'


def check_overlap(
    elem1: Dict,
    bbox1: BoundingBox,
    elem2: Dict,
    bbox2: BoundingBox
) -> Optional[Issue]:
    """Check if two elements overlap spatially during overlapping time windows."""
    id1 = elem1.get('id', 'unknown')
    id2 = elem2.get('id', 'unknown')

    # Check timing overlap first
    overlaps_time, start_time, end_time = timing_windows_overlap(elem1, elem2)
    if not overlaps_time:
        return None

    # Check spatial overlap
    # Two rectangles overlap if they overlap on both axes
    x_overlap = bbox1.left < bbox2.right and bbox1.right > bbox2.left
    y_overlap = bbox1.top < bbox2.bottom and bbox1.bottom > bbox2.top

    if x_overlap and y_overlap:
        # Calculate overlap area
        overlap_left = max(bbox1.left, bbox2.left)
        overlap_right = min(bbox1.right, bbox2.right)
        overlap_top = max(bbox1.top, bbox2.top)
        overlap_bottom = min(bbox1.bottom, bbox2.bottom)
        overlap_area = (overlap_right - overlap_left) * (overlap_bottom - overlap_top)

        # Check if either element is text
        involves_text = is_text_element(elem1) or is_text_element(elem2)
        issue_type = "TEXT_OVERLAP" if involves_text else "OVERLAP"

        desc = f"Elements '{id1}' and '{id2}' overlap during time {start_time}ms-{end_time}ms (overlap area: {overlap_area:.0f}px squared)"
        logger.info(f"Found overlap: {desc}")

        return Issue(
            element_id=id1,
            issue_type=issue_type,
            description=desc,
            details={
                "other_element": id2,
                "overlap_area": overlap_area,
                "start_time": start_time,
                "end_time": end_time,
                "involves_text": involves_text
            }
        )

    return None


def is_full_screen_element(element: Dict, viewport_width: int, viewport_height: int) -> bool:
    """Check if element is a full-screen background element."""
    element_id = element.get('id', '')
    styles = element.get('styles', {})
    size = styles.get('size', {})
    width = size.get('width', 0)
    height = size.get('height', 0)

    # Consider it full-screen if it covers 95%+ of the viewport
    return width >= viewport_width * 0.95 and height >= viewport_height * 0.95


def validate_scene(scene_index: int) -> List[Issue]:
    """Validate all elements in a scene for bounding box issues."""
    issues = []

    # Get design file path
    design_path = get_design_path(scene_index)
    if not os.path.exists(design_path):
        logger.error(f"Design file not found at {design_path}")
        return issues

    # Load design JSON
    logger.info(f"Loading design from {design_path}")
    with open(design_path, 'r', encoding='utf-8') as f:
        design = json.load(f)

    # Get viewport dimensions
    viewport_width, viewport_height = get_viewport_dimensions()
    logger.info(f"Viewport: {viewport_width}x{viewport_height}")

    elements = design.get('elements', [])
    logger.info(f"Validating {len(elements)} elements")

    # Check each element for bounds issues
    for element in elements:
        element_id = element.get('id', 'unknown')
        logger.debug(f"Checking element: {element_id}")

        # Calculate initial bounding box
        bbox = calculate_bounding_box(element)
        if bbox is None:
            continue

        # Check initial bounds
        initial_issues = check_screen_bounds(
            element_id, bbox, viewport_width, viewport_height,
            is_animated=False
        )
        issues.extend(initial_issues)

        # Check animated bounds (max scale)
        max_scale = get_max_animated_scale(element)
        if max_scale > 1.0:
            logger.debug(f"Element {element_id} has animated scale: {max_scale}")
            animated_bbox = calculate_bounding_box(element, scale=max_scale)
            if animated_bbox:
                # Only report if the issue is new (not already out of bounds initially)
                animated_issues = check_screen_bounds(
                    element_id, animated_bbox, viewport_width, viewport_height,
                    is_animated=True, scale=max_scale
                )
                # Filter out issues that were already present in initial state
                initial_issue_types = {i.issue_type.replace("OUT_OF_BOUNDS", "") for i in initial_issues}
                for issue in animated_issues:
                    issue_direction = issue.issue_type.replace("ANIMATED_OUT", "")
                    if issue_direction not in initial_issue_types:
                        issues.append(issue)

    # Check for overlaps (excluding full-screen elements)
    non_fullscreen_elements = [
        e for e in elements
        if not is_full_screen_element(e, viewport_width, viewport_height)
    ]
    logger.debug(f"Checking overlaps for {len(non_fullscreen_elements)} non-fullscreen elements")

    # Check each pair of elements
    checked_pairs = set()
    for i, elem1 in enumerate(non_fullscreen_elements):
        bbox1 = calculate_bounding_box(elem1)
        if bbox1 is None:
            continue

        for j, elem2 in enumerate(non_fullscreen_elements):
            if i >= j:  # Skip self-comparison and already-checked pairs
                continue

            pair_key = (elem1.get('id'), elem2.get('id'))
            if pair_key in checked_pairs:
                continue
            checked_pairs.add(pair_key)

            bbox2 = calculate_bounding_box(elem2)
            if bbox2 is None:
                continue

            overlap_issue = check_overlap(elem1, bbox1, elem2, bbox2)
            if overlap_issue:
                issues.append(overlap_issue)

    logger.info(f"Validation complete. Found {len(issues)} issues.")
    return issues


def print_issues(issues: List[Issue], scene_index: int):
    """Print issues in a formatted way."""
    if not issues:
        logger.info(f"Scene {scene_index}: No overlaps found!")
        print(f"\n[OK] Scene {scene_index}: No overlaps found!")
        return

    logger.info(f"Scene {scene_index}: Found {len(issues)} issue(s)")
    print(f"\n[WARNING] Scene {scene_index}: Found {len(issues)} issue(s)\n")

    # Group by issue type
    out_of_bounds = [i for i in issues if "OUT_OF_BOUNDS" in i.issue_type]
    animated_out = [i for i in issues if "ANIMATED_OUT" in i.issue_type]
    non_text_overlaps = [i for i in issues if i.issue_type == "OVERLAP"]
    text_overlaps = [i for i in issues if i.issue_type == "TEXT_OVERLAP"]
    print("ITEMS OVERLAPS: THE FOLLOWING ITEMS OVERLAP WITH EACH OTHER")
    if out_of_bounds:
        for issue in out_of_bounds:
            print(f"  - {issue.description}")

    if animated_out:
        for issue in animated_out:
            print(f"  - {issue.description}")

    # Section 1: Non-text overlaps (check if intentional or accidental)
    if non_text_overlaps:
        for issue in non_text_overlaps:
            print(f"  - {issue.description}")

    # Section 2: Text overlaps (should not overlap)
    if text_overlaps:
        print("TEXT OVERLAPS: THE FOLLOWING TEXT SHOULD NOT OVERLAP ANYTHING")
        for issue in text_overlaps:
            print(f"  - {issue.description}")

def validate_design_file(design_path: str, viewport_width: int = 1080, viewport_height: int = 1920) -> List[Issue]:
    """Validate all elements in a design file for bounding box issues."""
    issues = []

    if not os.path.exists(design_path):
        logger.error(f"Design file not found at {design_path}")
        return issues

    # Load design JSON
    logger.info(f"Loading design from {design_path}")
    with open(design_path, 'r', encoding='utf-8') as f:
        design = json.load(f)

    # Try to get viewport from design metadata
    video_metadata = design.get('video_metadata', {})
    viewport_size = video_metadata.get('viewport_size', '')
    if viewport_size and 'x' in viewport_size:
        parts = viewport_size.split('x')
        if len(parts) == 2:
            viewport_width = int(parts[0])
            viewport_height = int(parts[1])

    logger.info(f"Viewport: {viewport_width}x{viewport_height}")

    elements = design.get('elements', [])
    logger.info(f"Validating {len(elements)} elements")

    # Check each element for bounds issues
    for element in elements:
        element_id = element.get('id', 'unknown')
        logger.debug(f"Checking element: {element_id}")

        # Calculate initial bounding box
        bbox = calculate_bounding_box(element)
        if bbox is None:
            continue

        # Check initial bounds
        initial_issues = check_screen_bounds(
            element_id, bbox, viewport_width, viewport_height,
            is_animated=False
        )
        issues.extend(initial_issues)

        # Check animated bounds (max scale)
        max_scale = get_max_animated_scale(element)
        if max_scale > 1.0:
            logger.debug(f"Element {element_id} has animated scale: {max_scale}")
            animated_bbox = calculate_bounding_box(element, scale=max_scale)
            if animated_bbox:
                # Only report if the issue is new (not already out of bounds initially)
                animated_issues = check_screen_bounds(
                    element_id, animated_bbox, viewport_width, viewport_height,
                    is_animated=True, scale=max_scale
                )
                # Filter out issues that were already present in initial state
                initial_issue_types = {i.issue_type.replace("OUT_OF_BOUNDS", "") for i in initial_issues}
                for issue in animated_issues:
                    issue_direction = issue.issue_type.replace("ANIMATED_OUT", "")
                    if issue_direction not in initial_issue_types:
                        issues.append(issue)

    # Check for overlaps (excluding full-screen elements)
    non_fullscreen_elements = [
        e for e in elements
        if not is_full_screen_element(e, viewport_width, viewport_height)
    ]
    logger.debug(f"Checking overlaps for {len(non_fullscreen_elements)} non-fullscreen elements")

    # Check each pair of elements
    checked_pairs = set()
    for i, elem1 in enumerate(non_fullscreen_elements):
        bbox1 = calculate_bounding_box(elem1)
        if bbox1 is None:
            continue

        for j, elem2 in enumerate(non_fullscreen_elements):
            if i >= j:  # Skip self-comparison and already-checked pairs
                continue

            pair_key = (elem1.get('id'), elem2.get('id'))
            if pair_key in checked_pairs:
                continue
            checked_pairs.add(pair_key)

            bbox2 = calculate_bounding_box(elem2)
            if bbox2 is None:
                continue

            overlap_issue = check_overlap(elem1, bbox1, elem2, bbox2)
            if overlap_issue:
                issues.append(overlap_issue)

    logger.info(f"Validation complete. Found {len(issues)} issues.")
    return issues


def main():
    parser = argparse.ArgumentParser(description='Validate design file bounding boxes')
    parser.add_argument('--scene', type=int, help='Scene index')
    parser.add_argument('--topic', help='Topic name')
    parser.add_argument('file_path', nargs='?', help='Design file path (alternative to --scene)')

    args = parser.parse_args()

    # Set topic if provided
    if args.topic:
        ClaudeCliConfig.set_topic(args.topic)

    # Determine mode
    if args.scene is not None:
        arg = str(args.scene)
    elif args.file_path:
        arg = args.file_path
    else:
        logger.info("Usage: python bounding_check.py --scene SCENE_INDEX --topic TOPIC")
        logger.info("       python bounding_check.py <design_file_path>")
        logger.info("Example: python bounding_check.py --scene 0 --topic my-topic")
        logger.info("Example: python bounding_check.py Outputs/my-topic/Design/Latest/latest_0.json")
        sys.exit(1)

    # Check if argument is a file path or scene index
    if os.path.exists(arg) or arg.endswith('.json'):
        # Direct file path mode
        design_path = arg
        scene_index = 0  # Default for display

        # Try to extract scene index from filename
        basename = os.path.basename(design_path)
        if basename.startswith('Design_') and basename.endswith('.json'):
            try:
                scene_index = int(basename.replace('Design_', '').replace('.json', ''))
            except ValueError:
                pass

        logger.info(f"Starting validation for design file: {design_path}")
        issues = validate_design_file(design_path)
        print_issues(issues, scene_index)
    else:
        # Scene index mode
        scene_index = int(arg)

        logger.info(f"Starting validation for scene {scene_index}")
        logger.info(f"Validating scene {scene_index}...")
        logger.info(f"Design path: {get_design_path(scene_index)}")

        viewport_width, viewport_height = get_viewport_dimensions()
        logger.info(f"Viewport: {viewport_width}x{viewport_height}")

        issues = validate_scene(scene_index)
        print_issues(issues, scene_index)

if __name__ == "__main__":
    main()
