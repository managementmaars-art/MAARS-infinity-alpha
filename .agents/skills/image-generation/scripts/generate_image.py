#!/usr/bin/env python3
"""Generate illustration images using Google Gemini Nano Banana 2 API.

Requires GEMINI_API_KEY environment variable.

Usage:
    python generate_image.py --prompt "your prompt" [options]

Options:
    --prompt        Text prompt for image generation (required)
    --output        Output file path (default: generated_image.png)
    --model         Model ID (default: gemini-3.1-flash-image-preview)
    --aspect-ratio  Aspect ratio (default: 4:3)
    --image-size    Resolution tier: 512, 1K, 2K, 4K (default: 1K)
    --style-prefix  Custom style prefix (default: built-in minimal style)
    --no-style      Skip the default style prefix
"""

import argparse
import base64
import json
import os
import sys

import httpx

DEFAULT_MODEL = "gemini-3.1-flash-image-preview"
DEFAULT_ASPECT_RATIO = "3:2"
DEFAULT_IMAGE_SIZE = "1K"
DEFAULT_STYLE_PREFIX = (
    "Use a clean, modern color palette with soft tones. "
    "Minimalist flat illustration style with clear visual hierarchy. "
    "Professional and polished look suitable for technical blog articles. "
    "No photorealistic rendering. No excessive gradients or shadows."
)

VALID_ASPECT_RATIOS = [
    "1:1", "1:4", "1:8", "2:3", "3:2", "3:4",
    "4:1", "4:3", "4:5", "5:4", "8:1", "9:16", "16:9", "21:9",
]
VALID_IMAGE_SIZES = ["512", "1K", "2K", "4K"]


def generate_image(
    prompt: str,
    output_path: str = "generated_image.png",
    model: str = DEFAULT_MODEL,
    aspect_ratio: str = DEFAULT_ASPECT_RATIO,
    image_size: str = DEFAULT_IMAGE_SIZE,
    style_prefix: str = DEFAULT_STYLE_PREFIX,
) -> str:
    """Generate an image and save to output_path. Returns the saved file path."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    if aspect_ratio not in VALID_ASPECT_RATIOS:
        print(f"Error: Invalid aspect ratio '{aspect_ratio}'. Valid: {VALID_ASPECT_RATIOS}", file=sys.stderr)
        sys.exit(1)

    if image_size not in VALID_IMAGE_SIZES:
        print(f"Error: Invalid image size '{image_size}'. Valid: {VALID_IMAGE_SIZES}", file=sys.stderr)
        sys.exit(1)

    # Build the full prompt
    full_prompt = f"{style_prefix}\n\n{prompt}" if style_prefix else prompt

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": full_prompt}]}],
        "generationConfig": {
            "responseModalities": ["IMAGE"],
            "imageConfig": {
                "aspectRatio": aspect_ratio,
                "imageSize": image_size,
            },
        },
    }

    print(f"Model:        {model}")
    print(f"Aspect ratio: {aspect_ratio}")
    print(f"Image size:   {image_size}")
    print(f"Output:       {output_path}")
    print(f"Prompt:       {prompt[:120]}{'...' if len(prompt) > 120 else ''}")
    print("Generating...")

    resp = httpx.post(url, json=payload, timeout=180)

    if resp.status_code != 200:
        print(f"API Error {resp.status_code}: {resp.text[:500]}", file=sys.stderr)
        sys.exit(1)

    data = resp.json()
    candidates = data.get("candidates", [])
    if not candidates:
        print(f"No candidates returned. Response: {json.dumps(data)[:500]}", file=sys.stderr)
        sys.exit(1)

    parts = candidates[0].get("content", {}).get("parts", [])
    saved = False
    for part in parts:
        if "inlineData" in part:
            img_bytes = base64.b64decode(part["inlineData"]["data"])
            # Ensure parent directory exists
            parent = os.path.dirname(output_path)
            if parent:
                os.makedirs(parent, exist_ok=True)
            with open(output_path, "wb") as f:
                f.write(img_bytes)
            print(f"Done! Saved {len(img_bytes):,} bytes to {output_path}")
            saved = True
            break

    if not saved:
        # Dump text parts for debugging
        for part in parts:
            if "text" in part:
                print(f"Model text response: {part['text'][:300]}", file=sys.stderr)
        print("Error: No image data in response.", file=sys.stderr)
        sys.exit(1)

    return output_path


def main():
    parser = argparse.ArgumentParser(description="Generate images with Gemini Nano Banana 2")
    parser.add_argument("--prompt", required=True, help="Image generation prompt")
    parser.add_argument("--output", default="generated_image.png", help="Output file path")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"Model ID (default: {DEFAULT_MODEL})")
    parser.add_argument("--aspect-ratio", default=DEFAULT_ASPECT_RATIO, help=f"Aspect ratio (default: {DEFAULT_ASPECT_RATIO})")
    parser.add_argument("--image-size", default=DEFAULT_IMAGE_SIZE, help=f"Image size (default: {DEFAULT_IMAGE_SIZE})")
    parser.add_argument("--style-prefix", default=None, help="Custom style prefix (overrides default)")
    parser.add_argument("--no-style", action="store_true", help="Skip default style prefix")

    args = parser.parse_args()

    style = ""
    if args.no_style:
        style = ""
    elif args.style_prefix:
        style = args.style_prefix
    else:
        style = DEFAULT_STYLE_PREFIX

    generate_image(
        prompt=args.prompt,
        output_path=args.output,
        model=args.model,
        aspect_ratio=args.aspect_ratio,
        image_size=args.image_size,
        style_prefix=style,
    )


if __name__ == "__main__":
    main()
