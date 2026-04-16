#!/usr/bin/env python3
"""
Screenshot Capture Tool
Based on: https://github.com/python-pillow/Pillow

Usage:
    python screenshot_capture.py --output screen.png
    python screenshot_capture.py --region 0,0,800,600 --output region.png
"""

import argparse
import sys
import time
from datetime import datetime
from pathlib import Path

def capture_screenshot(output=None, region=None, delay=0):
    """Capture screenshot."""
    try:
        from PIL import ImageGrab
    except ImportError:
        print("Error: Pillow required. Install: pip install Pillow", file=sys.stderr)
        sys.exit(1)
    
    if delay > 0:
        print(f"Capturing in {delay} seconds...")
        time.sleep(delay)
    
    if region:
        x1, y1, x2, y2 = region
        screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))
    else:
        screenshot = ImageGrab.grab()
    
    if not output:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output = f"screenshot_{timestamp}.png"
    
    screenshot.save(output)
    print(f"✓ Screenshot saved: {output} ({screenshot.size[0]}x{screenshot.size[1]})")
    return output

def main():
    parser = argparse.ArgumentParser(description="Capture screenshots")
    parser.add_argument('--output', '-o', help='Output file')
    parser.add_argument('--region', '-r', help='Region: x1,y1,x2,y2')
    parser.add_argument('--delay', '-d', type=int, default=0, help='Delay in seconds')
    parser.add_argument('--format', '-f', default='png', choices=['png', 'jpg', 'bmp'])
    args = parser.parse_args()
    
    region = None
    if args.region:
        region = tuple(map(int, args.region.split(',')))
        if len(region) != 4:
            parser.error("Region must be x1,y1,x2,y2")
    
    capture_screenshot(args.output, region, args.delay)

if __name__ == "__main__":
    main()
