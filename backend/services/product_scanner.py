"""Product Scanner Service - Identifies products from images, searches for details and better reference images."""

import logging
import asyncio
import re
from typing import Dict, List, Optional

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


async def search_product_images(query: str, max_results: int = 6) -> List[Dict]:
    """Search for high-quality product images using DuckDuckGo Images."""
    try:
        from ddgs import DDGS

        def _search():
            with DDGS() as ddgs:
                return list(ddgs.images(f"{query} product professional photo", max_results=max_results))

        raw = await asyncio.to_thread(_search)
        images = []
        for r in raw:
            img_url = r.get("image", "")
            thumb_url = r.get("thumbnail", "")
            if img_url:
                images.append({
                    "url": img_url,
                    "thumbnail": thumb_url or img_url,
                    "title": r.get("title", ""),
                    "source": r.get("source", ""),
                    "width": r.get("width", 0),
                    "height": r.get("height", 0),
                })
        logger.info(f"Product image search '{query[:40]}': {len(images)} images found")
        return images
    except Exception as e:
        logger.error(f"Product image search failed: {e}")
        return []


async def search_product_details(query: str) -> Dict:
    """Search the web for detailed product information - specs, pricing, reviews."""
    try:
        from ddgs import DDGS

        def _search():
            with DDGS() as ddgs:
                return list(ddgs.text(f"{query} specifications features price review", max_results=5))

        raw = await asyncio.to_thread(_search)
        details = {"sources": [], "snippets": []}
        for r in raw:
            details["sources"].append({
                "title": r.get("title", ""),
                "url": r.get("href", r.get("link", "")),
                "snippet": r.get("body", r.get("snippet", "")),
            })
            details["snippets"].append(r.get("body", r.get("snippet", "")))

        # Scrape the top 2 results for richer data
        scraped_content = []
        for source in details["sources"][:2]:
            url = source.get("url", "")
            if not url:
                continue
            try:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                    "Accept": "text/html,application/xhtml+xml",
                }
                async with httpx.AsyncClient(follow_redirects=True, timeout=8, headers=headers) as client:
                    resp = await client.get(url)
                    if resp.status_code == 200 and "text/html" in resp.headers.get("content-type", ""):
                        soup = BeautifulSoup(resp.text, "html.parser")
                        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
                            tag.decompose()
                        text = soup.get_text(separator="\n", strip=True)
                        # Get first 2000 chars of meaningful content
                        lines = [l.strip() for l in text.splitlines() if len(l.strip()) > 30]
                        scraped_content.append("\n".join(lines[:40]))
            except Exception:
                pass

        details["scraped_content"] = scraped_content
        logger.info(f"Product details search '{query[:40]}': {len(details['sources'])} sources")
        return details
    except Exception as e:
        logger.error(f"Product details search failed: {e}")
        return {"sources": [], "snippets": [], "scraped_content": []}


async def download_reference_image(url: str, upload_dir) -> Optional[str]:
    """Download a reference image from URL and save to uploads directory."""
    import uuid
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Accept": "image/*",
        }
        async with httpx.AsyncClient(follow_redirects=True, timeout=10, headers=headers) as client:
            resp = await client.get(url)
            if resp.status_code != 200:
                return None
            content_type = resp.headers.get("content-type", "")
            if "image" not in content_type:
                return None
            ext = "jpg"
            if "png" in content_type:
                ext = "png"
            elif "webp" in content_type:
                ext = "webp"
            filename = f"ref_{uuid.uuid4().hex[:10]}.{ext}"
            filepath = upload_dir / filename
            with open(filepath, "wb") as f:
                f.write(resp.content)
            logger.info(f"Downloaded reference image: {filename} ({len(resp.content)} bytes)")
            return str(filepath)
    except Exception as e:
        logger.debug(f"Failed to download reference image: {e}")
        return None


def build_product_context(product_name: str, details: Dict, images: List[Dict]) -> str:
    """Build a comprehensive product context string for the LLM."""
    lines = []
    lines.append(f"\n=== PRODUCT SCAN RESULTS: {product_name} ===")

    # Details from web
    if details.get("snippets"):
        lines.append("\n**Product Information (from web):**")
        for i, snippet in enumerate(details["snippets"][:5], 1):
            lines.append(f"  {i}. {snippet}")

    if details.get("scraped_content"):
        lines.append("\n**Detailed Product Data:**")
        for content in details["scraped_content"][:2]:
            lines.append(content[:1500])

    # Reference images
    if images:
        lines.append(f"\n**High-Quality Reference Images Found:** {len(images)} images")
        for i, img in enumerate(images[:4], 1):
            lines.append(f"  {i}. [{img['title'][:60]}]({img['url']}) ({img.get('width', '?')}x{img.get('height', '?')})")

    # Sources
    if details.get("sources"):
        lines.append("\n**Sources:**")
        for s in details["sources"][:3]:
            lines.append(f"  - [{s['title'][:60]}]({s['url']})")

    lines.append("=== END PRODUCT SCAN ===\n")
    return "\n".join(lines)


async def scan_product(product_query: str, upload_dir=None) -> Dict:
    """Main entry: search for product details, images, and optionally download best reference image."""
    # Run details and image searches in parallel
    details_task = search_product_details(product_query)
    images_task = search_product_images(product_query)
    details, images = await asyncio.gather(details_task, images_task)

    # Download the best reference image for video generation
    best_ref_path = None
    if upload_dir and images:
        # Try downloading the highest-resolution image
        sorted_images = sorted(images, key=lambda x: (x.get("width", 0) * x.get("height", 0)), reverse=True)
        for img in sorted_images[:3]:
            path = await download_reference_image(img["url"], upload_dir)
            if path:
                best_ref_path = path
                break

    context = build_product_context(product_query, details, images)

    return {
        "product_query": product_query,
        "details": details,
        "images": images,
        "reference_image_path": best_ref_path,
        "context": context,
    }
