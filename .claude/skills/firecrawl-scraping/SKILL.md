---
name: firecrawl-scraping
description: Web scraping and crawling with Firecrawl API including scrape, crawl, map, search, and LLM-powered extract endpoints.
---

# Firecrawl Scraping

## Overview

Firecrawl converts websites into clean, LLM-ready markdown or structured data. It handles JavaScript rendering, authentication, rate limiting, and anti-bot measures automatically.

## Installation & Setup

```bash
pip install firecrawl-py
npm install @mendable/firecrawl-js
```

```python
from firecrawl import FirecrawlApp

app = FirecrawlApp(api_key="fc-YOUR_API_KEY")
```

## Scrape Single Page

```python
# Basic scrape - returns markdown by default
result = app.scrape_url(
    "https://example.com/article",
    params={
        "formats": ["markdown", "html", "screenshot"],
        "onlyMainContent": True,       # Strip nav, footer, ads
        "includeTags": ["article", "main"],
        "excludeTags": ["nav", "footer", "aside"],
        "waitFor": 2000,               # Wait 2s for JS to render
        "timeout": 30000,
        "headers": {"User-Agent": "Mozilla/5.0"},
        "actions": [
            {"type": "wait", "milliseconds": 1000},
            {"type": "click", "selector": "#load-more"},
            {"type": "wait", "milliseconds": 2000},
        ],
    }
)

print(result["markdown"])
print(result["metadata"]["title"])
print(result["metadata"]["description"])
print(result["metadata"]["ogImage"])
```

```javascript
// JavaScript/TypeScript
import FirecrawlApp from "@mendable/firecrawl-js";

const app = new FirecrawlApp({ apiKey: "fc-YOUR_API_KEY" });

const result = await app.scrapeUrl("https://example.com", {
  formats: ["markdown", "links"],
  onlyMainContent: true,
  waitFor: 1000,
});

console.log(result.markdown);
console.log(result.links); // All links found on the page
```

## Crawl Entire Website

```python
# Start a crawl job (async for large sites)
crawl_result = app.crawl_url(
    "https://docs.example.com",
    params={
        "limit": 100,                  # Max pages to crawl
        "scrapeOptions": {
            "formats": ["markdown"],
            "onlyMainContent": True,
        },
        "includePaths": ["/docs/*", "/blog/*"],
        "excludePaths": ["/admin/*", "*.pdf"],
        "maxDepth": 3,
        "allowExternalLinks": False,
        "allowBackwardLinks": False,   # Don't go back up the tree
        "ignoreSitemap": False,
    },
    poll_interval=5,  # Poll every 5 seconds
    idempotency_key="unique-crawl-id"  # Resume if interrupted
)

# Process pages
for page in crawl_result["data"]:
    print(f"URL: {page['url']}")
    print(f"Content: {page['markdown'][:200]}")
```

```python
# Async crawl with webhook
import time

crawl_status = app.async_crawl_url(
    "https://example.com",
    params={
        "limit": 500,
        "webhook": "https://your-app.com/webhooks/firecrawl",
        "scrapeOptions": {"formats": ["markdown", "links"]},
    }
)

crawl_id = crawl_status["id"]

# Check status manually
while True:
    status = app.check_crawl_status(crawl_id)
    print(f"Status: {status['status']}, Pages: {status['completed']}/{status['total']}")
    if status["status"] in ["completed", "failed"]:
        break
    time.sleep(10)

# Get results
if status["status"] == "completed":
    pages = status["data"]
```

## Map Website URLs

```python
# Fast URL discovery without scraping content
map_result = app.map_url(
    "https://example.com",
    params={
        "search": "pricing",           # Filter URLs by keyword
        "limit": 5000,
        "includeSubdomains": False,
    }
)

urls = map_result["links"]
print(f"Found {len(urls)} URLs")
# Use for targeted scraping
for url in urls[:10]:
    print(url)
```

## Search the Web

```python
# Search and scrape results in one call
search_results = app.search(
    "best Python web frameworks 2024",
    params={
        "limit": 10,
        "lang": "en",
        "country": "us",
        "scrapeOptions": {
            "formats": ["markdown"],
            "onlyMainContent": True,
        },
    }
)

for result in search_results["data"]:
    print(f"Title: {result['metadata']['title']}")
    print(f"URL: {result['url']}")
    print(f"Content: {result['markdown'][:500]}")
    print("---")
```

## LLM-Powered Extract

```python
from pydantic import BaseModel
from typing import List, Optional

class ProductInfo(BaseModel):
    name: str
    price: float
    currency: str
    rating: Optional[float]
    reviews_count: int
    features: List[str]
    in_stock: bool

# Extract structured data using AI
extract_result = app.scrape_url(
    "https://shop.example.com/product/123",
    params={
        "formats": ["extract"],
        "extract": {
            "schema": ProductInfo.model_json_schema(),
            "prompt": "Extract the product information from this page.",
            "systemPrompt": "You are a product data extraction specialist.",
        },
    }
)

product = ProductInfo(**extract_result["extract"])
print(f"Product: {product.name}, Price: {product.price} {product.currency}")
```

```python
# Batch extraction across multiple URLs
class JobPosting(BaseModel):
    title: str
    company: str
    location: str
    salary_range: Optional[str]
    requirements: List[str]
    remote: bool

batch_result = app.batch_scrape_urls(
    [
        "https://jobs.example.com/job/1",
        "https://jobs.example.com/job/2",
        "https://jobs.example.com/job/3",
    ],
    params={
        "formats": ["extract"],
        "extract": {
            "schema": JobPosting.model_json_schema(),
        },
    }
)

for item in batch_result["data"]:
    job = JobPosting(**item["extract"])
    print(f"{job.title} at {job.company} - {job.location}")
```

## Advanced Patterns

```python
# Scrape with authentication (session cookies)
result = app.scrape_url(
    "https://app.example.com/dashboard",
    params={
        "formats": ["markdown"],
        "headers": {
            "Cookie": "session=abc123; auth_token=xyz",
            "Authorization": "Bearer token123",
        },
        "actions": [
            {"type": "screenshot"},  # Debug what page looks like
        ],
    }
)

# Monitor a page for changes
import hashlib

def monitor_page(url: str, check_interval: int = 3600):
    """Monitor a page and alert on content changes."""
    last_hash = None
    while True:
        result = app.scrape_url(url, params={"formats": ["markdown"]})
        content_hash = hashlib.sha256(result["markdown"].encode()).hexdigest()

        if last_hash and content_hash != last_hash:
            send_alert(f"Page changed: {url}")

        last_hash = content_hash
        time.sleep(check_interval)

# Rate-limited bulk scraping
from concurrent.futures import ThreadPoolExecutor, as_completed

def scrape_urls_parallel(urls: list, max_workers: int = 5):
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(
                app.scrape_url,
                url,
                {"formats": ["markdown"], "onlyMainContent": True}
            ): url
            for url in urls
        }
        for future in as_completed(futures):
            url = futures[future]
            try:
                result = future.result()
                results.append({"url": url, "content": result["markdown"]})
            except Exception as e:
                results.append({"url": url, "error": str(e)})
    return results
```

## Key Patterns

- **Use `onlyMainContent: True`** to strip boilerplate and get clean content for LLMs
- **Map first, then scrape** for large sites — map gives you all URLs instantly
- **Use `actions`** for JavaScript-heavy SPAs that require interaction before content loads
- **Batch scraping** is more efficient than sequential for multiple URLs
- **Idempotency keys** allow resuming interrupted crawls
- **Webhooks** for large crawls so you don't hold open connections

## Models to Use

- **claude-opus-4-5**: Complex extraction schemas, multi-step crawl strategies
- **claude-sonnet-4-5**: Standard scraping pipelines, data extraction
- **claude-haiku-3-5**: Quick URL mapping, simple content extraction
