#!/usr/bin/env python3
import argparse
import base64
import os
import sys
from pathlib import Path


def _extract_image_bytes(response):
    """Best-effort extraction for google-genai SDK response shapes."""
    # Newer SDKs may expose quick access on response.generated_images
    generated_images = getattr(response, "generated_images", None)
    if generated_images:
        first = generated_images[0]
        image = getattr(first, "image", None)
        image_bytes = getattr(image, "image_bytes", None)
        if image_bytes:
            return image_bytes

    candidates = getattr(response, "candidates", None) or []
    for candidate in candidates:
        content = getattr(candidate, "content", None)
        parts = getattr(content, "parts", None) or []
        for part in parts:
            inline_data = getattr(part, "inline_data", None)
            if not inline_data:
                continue
            data = getattr(inline_data, "data", None)
            if isinstance(data, bytes):
                return data
            if isinstance(data, str):
                try:
                    return base64.b64decode(data)
                except Exception:
                    continue
    return None


def main():
    parser = argparse.ArgumentParser(description="Generate an image using Gemini Nano Banana.")
    parser.add_argument("--prompt", required=True, help="Text prompt for the image.")
    parser.add_argument("--out", required=True, help="Output PNG path.")
    parser.add_argument(
        "--model",
        default="gemini-2.5-flash-image-preview",
        help="Gemini image model name.",
    )
    parser.add_argument("--seed", type=int, default=None, help="Optional seed for determinism (if supported).")
    args = parser.parse_args()

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("ERROR: GOOGLE_API_KEY is not set.", file=sys.stderr)
        print("Set it like: export GOOGLE_API_KEY='...'", file=sys.stderr)
        sys.exit(2)

    try:
        from google import genai
        from google.genai import types
    except ImportError:
        print("ERROR: Missing dependency: google-genai", file=sys.stderr)
        print("Install with: pip install google-genai", file=sys.stderr)
        sys.exit(3)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    client = genai.Client(api_key=api_key)

    try:
        config = types.GenerateContentConfig(response_modalities=["IMAGE", "TEXT"])
        if args.seed is not None:
            setattr(config, "seed", args.seed)

        try:
            response = client.models.generate_content(
                model=args.model,
                contents=args.prompt,
                config=config,
            )
        except Exception as exc:
            if args.seed is not None and "seed" in str(exc).lower():
                config = types.GenerateContentConfig(response_modalities=["IMAGE", "TEXT"])
                response = client.models.generate_content(
                    model=args.model,
                    contents=args.prompt,
                    config=config,
                )
            else:
                raise

        image_bytes = _extract_image_bytes(response)
        if not image_bytes:
            raise RuntimeError("Model response did not include image bytes.")

        out_path.write_bytes(image_bytes)
        print(f"Saved: {out_path}")
        print("Prompt used:")
        print(args.prompt)
    except Exception as e:
        print("ERROR while generating image:", file=sys.stderr)
        print(str(e), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
