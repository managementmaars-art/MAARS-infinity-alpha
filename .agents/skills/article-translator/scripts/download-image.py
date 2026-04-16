#!/usr/bin/env python3
"""Download image from URL and save to local directory."""

import sys
import os
import re
import json
import base64
import urllib.request
from urllib.error import URLError, HTTPError


# Default headers to mimic browser and handle anti-hotlinking
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://www.google.com/",
    "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


def get_url_filename(url: str) -> str:
    """Extract filename from URL, generate one if missing."""
    path = url.split('/')[-1].split('?')[0]
    if not path or '.' not in path:
        # Generate name from URL hash
        name = re.sub(r'\W+', '_', url)
        path = f"image_{abs(hash(name)) % 100000:05d}.jpg"
    return path


def download_image(
    url: str,
    save_path: str,
    filename: str = None,
    referer: str = None,
    timeout: int = 30,
) -> str:
    """
    Download image from URL to save_path.

    Args:
        url: Image URL
        save_path: Directory to save image
        filename: Optional custom filename (default: extracted from URL)
        referer: Optional referer header for anti-hotlinking images
        timeout: Request timeout in seconds (default: 30)

    Returns:
        Local filename of saved image, or None on failure
    """
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    if not filename:
        filename = get_url_filename(url)

    local_path = os.path.join(save_path, filename)

    headers = DEFAULT_HEADERS.copy()
    if referer:
        headers["Referer"] = referer

    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            content = response.read()
            with open(local_path, 'wb') as f:
                f.write(content)
        return filename
    except (URLError, HTTPError, Exception) as e:
        print(f"Failed to download {url}: {e}", file=sys.stderr)
        return None


def save_base64_image(base64_data: str, save_path: str, filename: str = None) -> str:
    """
    Save base64 encoded image data to local file.

    Args:
        base64_data: Base64 string (with or without data URI prefix)
        save_path: Directory to save image
        filename: Optional custom filename (default: generated)

    Returns:
        Local filename of saved image, or None on failure
    """
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    # Remove data URI prefix if present
    if ',' in base64_data:
        base64_data = base64_data.split(',', 1)[1]

    try:
        image_data = base64.b64decode(base64_data)

        if not filename:
            filename = f"image_{abs(hash(base64_data)) % 100000:05d}.png"

        local_path = os.path.join(save_path, filename)
        with open(local_path, 'wb') as f:
            f.write(image_data)
        return filename
    except Exception as e:
        print(f"Failed to save base64 image: {e}", file=sys.stderr)
        return None


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: download-image.py <url> <save_path> [filename] [referer]", file=sys.stderr)
        print("       download-image.py --base64 <base64_string> <save_path> [filename]", file=sys.stderr)
        sys.exit(1)

    # Handle base64 mode
    if sys.argv[1] == "--base64":
        if len(sys.argv) < 4:
            print("Missing base64 string or save_path", file=sys.stderr)
            sys.exit(1)
        base64_data = sys.argv[2]
        save_path = sys.argv[3]
        filename = sys.argv[4] if len(sys.argv) > 4 else None
        result = save_base64_image(base64_data, save_path, filename)
    else:
        url = sys.argv[1]
        save_path = sys.argv[2]
        filename = sys.argv[3] if len(sys.argv) > 3 else None
        referer = sys.argv[4] if len(sys.argv) > 4 else None
        result = download_image(url, save_path, filename, referer)

    if result:
        print(result)
    else:
        sys.exit(1)
