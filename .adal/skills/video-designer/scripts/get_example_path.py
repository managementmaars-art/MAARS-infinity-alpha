#!/usr/bin/env python3

import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

from scripts.claude_cli.claude_cli_config import ClaudeCliConfig
from scripts.controllers.manifest_controller import ManifestController


def get_example_path(topic: str) -> str:
    ClaudeCliConfig.set_topic(topic)
    manifest_controller = ManifestController()
    manifest_controller.set_topic(topic)

    metadata = manifest_controller.get_metadata()
    video_style = metadata["video_style"]

    example_file = ClaudeCliConfig.EXAMPLE_MAP[video_style]

    return f"{ClaudeCliConfig.BASE_OUTPUT_PATH}/{topic}/Design/examples/{example_file}"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", type=str, required=True)
    args = parser.parse_args()

    path = get_example_path(args.topic)
    print("Read file from : ",path)

if __name__ == "__main__":
    main()
