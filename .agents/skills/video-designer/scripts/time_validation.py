"""
Time validation script for video scene animations.
Validates if an element's animation fits within a scene's time bounds.
"""

import sys
import argparse
import json
from pathlib import Path
from typing import Tuple, List, Dict, Any

# Add project root to path for imports
project_root = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(project_root))

from scripts.controllers.output_controller import OutputController
from scripts.enums import AssetType
from scripts.claude_cli.claude_cli_config import ClaudeCliConfig


def get_design_path(scene_index: int) -> str:
    """Get the latest design file path for a given scene index."""
    path_template = ClaudeCliConfig.get_latest_path(AssetType.DESIGN)
    return path_template.format(scene_index=scene_index)


def load_design_data(scene_index: int = None, file_path: str = None) -> Dict[str, Any]:
    """Load design data from scene index or file path."""
    if file_path:
        full_path = Path(file_path)
    elif scene_index is not None:
        design_path = get_design_path(scene_index)
        full_path = project_root / design_path
    else:
        print("Error: Either scene_index or file_path must be provided")
        sys.exit(1)

    if not full_path.exists():
        print(f"Error: Design file not found at {full_path}")
        sys.exit(1)

    with open(full_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def validate_animation_time(scene_index: int, start_time: int, anim_duration: int) -> bool:
    """Validate if a single animation fits within scene bounds."""
    output_controller = OutputController()
    direction_data = output_controller.read_output(AssetType.DIRECTION)

    if not direction_data or 'scenes' not in direction_data:
        print("Error: Could not read direction data")
        sys.exit(1)

    scenes = direction_data['scenes']

    if scene_index < 0 or scene_index >= len(scenes):
        print(f"Error: Invalid scene_index {scene_index}. Valid range: 0-{len(scenes) - 1}")
        sys.exit(1)

    scene = scenes[scene_index]
    scene_end_time = scene.get('sceneEndTime', 0)

    animation_end_time = start_time + anim_duration

    return animation_end_time <= scene_end_time


def validate_all_animations(scene_index: int = None, file_path: str = None) -> Tuple[bool, List[Dict[str, Any]]]:
    """
    Validate that all animations in a scene complete within the scene time.

    Args:
        scene_index: Scene index (0-based). Used to load design from default path.
        file_path: Direct path to a design JSON file. Takes precedence over scene_index.

    Returns:
        Tuple containing:
        - bool: True if all animations are valid, False otherwise
        - List[Dict]: List of validation errors with element details
    """
    # Load design data for the scene
    design_data = load_design_data(scene_index=scene_index, file_path=file_path)
    elements = design_data.get('elements', [])

    # Get scene_index from design data if using file_path
    if file_path and scene_index is None:
        scene_index = design_data.get('scene', 0)

    # Load direction data for scene end time
    output_controller = OutputController()
    direction_data = output_controller.read_output(AssetType.DIRECTION)

    if not direction_data or 'scenes' not in direction_data:
        print("Error: Could not read direction data")
        sys.exit(1)

    scenes = direction_data['scenes']

    if scene_index < 0 or scene_index >= len(scenes):
        print(f"Error: Invalid scene_index {scene_index}. Valid range: 0-{len(scenes) - 1}")
        sys.exit(1)

    scene = scenes[scene_index]
    scene_end_time = scene.get('sceneEndTime', 0)

    errors = []

    for element in elements:
        element_id = element.get('id', 'unknown')
        animation = element.get('animation', {})

        enter_time = element.get('enterOn', 0)
        exit_time = element.get('exitOn', scene_end_time)

        # Check entrance animation
        entrance = animation.get('entrance', {})
        entrance_duration = entrance.get('duration', 0)
        entrance_end = enter_time + entrance_duration

        if entrance_end > scene_end_time:
            errors.append({
                'element_id': element_id,
                'error_type': 'entrance_exceeds_scene',
                'animation_type': 'entrance',
                'start_time': enter_time,
                'duration': entrance_duration,
                'end_time': entrance_end,
                'scene_end_time': scene_end_time,
                'overflow': entrance_end - scene_end_time
            })

        # Check exit animation
        exit_anim = animation.get('exit', {})
        exit_duration = exit_anim.get('duration', 0)
        exit_end = exit_time

        if exit_end > scene_end_time:
            errors.append({
                'element_id': element_id,
                'error_type': 'exit_exceeds_scene',
                'animation_type': 'exit',
                'exit_on': exit_time,
                'duration': exit_duration,
                'end_time': exit_end,
                'scene_end_time': scene_end_time,
                'overflow': exit_end - scene_end_time
            })

        # Check action animations
        actions = animation.get('actions', [])
        for i, action in enumerate(actions):
            action_start = action.get('on', 0)
            action_duration = action.get('duration', 0)
            action_end = action_start + action_duration

            if action_end > scene_end_time:
                errors.append({
                    'element_id': element_id,
                    'error_type': 'action_exceeds_scene',
                    'animation_type': f'action[{i}]',
                    'target_property': action.get('targetProperty') or action.get('type', 'unknown'),
                    'start_time': action_start,
                    'duration': action_duration,
                    'end_time': action_end,
                    'scene_end_time': scene_end_time,
                    'overflow': action_end - scene_end_time
                })

    is_valid = len(errors) == 0
    return is_valid, errors


def main():
    parser = argparse.ArgumentParser(
        description='Validate animation timing within scene bounds'
    )
    parser.add_argument(
        'scene_index',
        type=int,
        nargs='?',
        help='Scene index (0-based). Required if not using --file'
    )
    parser.add_argument(
        '--file', '-f',
        type=str,
        help='Path to design JSON file to validate (alternative to scene_index)'
    )

    args = parser.parse_args()

    if args.file is None and args.scene_index is None:
        print("Error: Either scene_index or --file must be provided")
        sys.exit(1)

    is_valid, errors = validate_all_animations(
        scene_index=args.scene_index,
        file_path=args.file
    )

    source = args.file if args.file else f"scene {args.scene_index}"
    if is_valid:
        print(f"All animations in {source} are valid and complete within scene time.")
    else:
        print(f"Found {len(errors)} animation timing error(s) in {source}:\n")
        for error in errors:
            print(f"  Element: {error['element_id']}")
            print(f"    Animation: {error['animation_type']}")
            print(f"    Start: {error.get('start_time', error.get('exit_on', 'N/A'))}ms")
            print(f"    Duration: {error.get('duration', 'N/A')}ms")
            print(f"    End: {error['end_time']}ms")
            print(f"    Scene End: {error['scene_end_time']}ms")
            print(f"    Overflow: {error['overflow']}ms")
            print()


if __name__ == '__main__':
    main()