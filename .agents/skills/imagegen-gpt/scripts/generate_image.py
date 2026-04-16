#!/usr/bin/env python3
import argparse
import base64
import os
import sys
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Generate an image using OpenAI gpt-image-1.")
    parser.add_argument("--prompt", required=True, help="Text prompt for the image.")
    parser.add_argument("--out", required=True, help="Output PNG path.")
    parser.add_argument("--size", default="1024x1024", help="Image size, e.g. 1024x1024.")
    parser.add_argument("--quality", default="high", choices=["low", "medium", "high"], help="Quality level.")
    parser.add_argument("--seed", type=int, default=None, help="Optional seed for determinism (if supported).")
    args = parser.parse_args()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY is not set.", file=sys.stderr)
        print("Set it like: export OPENAI_API_KEY='...'", file=sys.stderr)
        sys.exit(2)

    try:
        from openai import OpenAI
    except ImportError:
        print("ERROR: Missing dependency: openai", file=sys.stderr)
        print("Install with: pip install openai", file=sys.stderr)
        sys.exit(3)

    client = OpenAI()

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Note: API surface may evolve; keep this script small and easy to update.
    # This follows the official image generation guidance for gpt-image-1. 
    # If your SDK version differs, update the call accordingly.
    try:
        # Common pattern: request returns base64 image data.
        # Some SDK versions may not support "seed" in images.generate.
        params = {
            "model": "gpt-image-1",
            "prompt": args.prompt,
            "size": args.size,
            "quality": args.quality,
        }
        if args.seed is not None:
            params["seed"] = args.seed

        try:
            resp = client.images.generate(**params)
        except TypeError as e:
            if "seed" in str(e):
                params.pop("seed", None)
                resp = client.images.generate(**params)
            else:
                raise
        b64 = resp.data[0].b64_json
        img_bytes = base64.b64decode(b64)
        out_path.write_bytes(img_bytes)

        print(f"Saved: {out_path}")
        print("Prompt used:")
        print(args.prompt)
    except Exception as e:
        print("ERROR while generating image:", file=sys.stderr)
        print(str(e), file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
