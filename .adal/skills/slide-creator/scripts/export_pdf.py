#!/usr/bin/env python3
"""
HTML Slide Deck → PDF exporter using Playwright.
Serves the HTML locally, then uses headless Chromium to print exact 16:9 pages.
"""
import argparse
import asyncio
import os
import threading
import http.server
import functools

async def export_pdf(html_dir: str, output_path: str, width: int = 1280, height: int = 720):
    """Export all slides in html_dir/index.html to a single PDF."""
    from playwright.async_api import async_playwright

    # 1. Start a local HTTP server (fonts need http:// not file://)
    port = 18923
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=html_dir)
    httpd = http.server.HTTPServer(("127.0.0.1", port), handler)
    server_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    server_thread.start()

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page(viewport={"width": width, "height": height})

            # Navigate and wait for fonts + images
            await page.goto(f"http://127.0.0.1:{port}/index.html", wait_until="networkidle")
            # Extra wait for Google Fonts rendering
            await page.wait_for_timeout(1500)

            # Count slides
            slide_count = await page.eval_on_selector_all(
                "section.slide", "els => els.length"
            )
            print(f"Found {slide_count} slides ({width}x{height})")

            # Generate PDF with exact page size
            await page.pdf(
                path=output_path,
                width=f"{width}px",
                height=f"{height}px",
                margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
                print_background=True,
                prefer_css_page_size=False,
            )
            print(f"✅ PDF saved → {output_path}")

            await browser.close()
    finally:
        httpd.shutdown()


def main():
    parser = argparse.ArgumentParser(description="Export HTML slide deck to 16:9 PDF")
    parser.add_argument("--dir", default=".", help="Directory containing index.html")
    parser.add_argument("--output", "-o", default=None, help="Output PDF path")
    parser.add_argument("--width", type=int, default=1280, help="Slide width in px")
    parser.add_argument("--height", type=int, default=720, help="Slide height in px")
    args = parser.parse_args()

    html_dir = os.path.abspath(args.dir)
    if args.output:
        output = args.output
    else:
        output = os.path.join(html_dir, "deck.pdf")

    asyncio.run(export_pdf(html_dir, output, args.width, args.height))


if __name__ == "__main__":
    main()
