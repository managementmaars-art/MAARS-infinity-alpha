---
name: web-scraping
description: AI web scraping — Playwright, BeautifulSoup, Firecrawl, web intelligence, competitive monitoring, data extraction for MAARS web intelligence agents
---

# Web Scraping & Intelligence — MAARS Reference

## Playwright (JavaScript-rendered sites)
```python
from playwright.async_api import async_playwright

async def scrape_dynamic(url: str, selector: str = None) -> str:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Set realistic headers
        await page.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        })
        
        await page.goto(url, wait_until="networkidle")
        
        if selector:
            content = await page.inner_text(selector)
        else:
            content = await page.content()
        
        await browser.close()
        return content
```

## BeautifulSoup (Static sites)
```python
import httpx
from bs4 import BeautifulSoup

async def scrape_static(url: str) -> dict:
    async with httpx.AsyncClient(follow_redirects=True, timeout=30) as client:
        response = await client.get(url, headers={
            "User-Agent": "Mozilla/5.0 (compatible; MAARS-Bot/1.0)"
        })
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Remove boilerplate
    for tag in soup(["script", "style", "nav", "footer", "aside"]):
        tag.decompose()
    
    return {
        "title": soup.title.string if soup.title else "",
        "text": soup.get_text(separator="\n", strip=True),
        "links": [a.get("href") for a in soup.find_all("a", href=True)][:50],
        "headings": [h.text for h in soup.find_all(["h1","h2","h3"])],
        "meta_description": soup.find("meta", {"name": "description"})
                               and soup.find("meta", {"name": "description"}).get("content"),
    }
```

## Firecrawl (LLM-ready web scraping)
```python
from firecrawl import FirecrawlApp

app = FirecrawlApp(api_key=FIRECRAWL_API_KEY)

# Single URL → clean markdown
result = app.scrape_url(url, params={"formats": ["markdown"]})
content = result["markdown"]

# Crawl entire site
crawl_result = app.crawl_url(
    url,
    params={
        "crawlerOptions": {"maxDepth": 2},
        "pageOptions": {"onlyMainContent": True},
    }
)

# Extract structured data
extract_result = app.extract([url], {
    "prompt": "Extract: company name, pricing, key features",
    "schema": {
        "type": "object",
        "properties": {
            "company_name": {"type": "string"},
            "pricing": {"type": "array", "items": {"type": "string"}},
            "features": {"type": "array", "items": {"type": "string"}},
        }
    }
})
```

## AI-Powered Extraction
```python
async def extract_with_llm(html: str, schema: dict, url: str = "") -> dict:
    """Extract structured data from HTML using LLM."""
    # Clean HTML first
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style"]): tag.decompose()
    clean_text = soup.get_text(separator="\n", strip=True)[:8000]  # limit tokens
    
    prompt = f"""Extract the following information from this webpage content:

URL: {url}
SCHEMA: {json.dumps(schema, indent=2)}

CONTENT:
{clean_text}

Return valid JSON matching the schema exactly. If a field is not found, use null."""
    
    response = await llm_call("gpt-4o", prompt, response_format={"type": "json_object"})
    return json.loads(response)
```

## Competitive Intelligence Monitor
```python
async def monitor_competitor(
    competitor_url: str,
    check_frequency_hours: int = 24,
) -> dict:
    current = await scrape_static(competitor_url)
    
    # Compare with previous scrape
    previous = await db.get_latest_scrape(competitor_url)
    
    changes = {
        "pricing_changed": detect_pricing_changes(previous, current),
        "new_features": detect_feature_changes(previous, current),
        "messaging_changed": detect_messaging_changes(previous, current),
    }
    
    if any(changes.values()):
        await notify_agent("agent_strategist", changes)
    
    return changes
```

## Rate Limiting & Ethics
```python
import asyncio

class PoliteScraperConfig:
    delay_between_requests: float = 1.0  # seconds
    respect_robots_txt: bool = True
    max_concurrent: int = 3
    
async def polite_scrape(urls: list[str]) -> list[dict]:
    semaphore = asyncio.Semaphore(PoliteScraperConfig.max_concurrent)
    results = []
    
    for url in urls:
        async with semaphore:
            result = await scrape_static(url)
            results.append(result)
            await asyncio.sleep(PoliteScraperConfig.delay_between_requests)
    
    return results
```

## Models to Use
- **Content extraction + summarization**: `gpt-4o` or `claude-sonnet-4-6`
- **Structured data extraction**: `gpt-4o` with JSON mode
- **Real-time web queries**: `grok-3` or `perplexity/sonar` (built-in search)
- **Large page processing**: `moonshot/kimi-latest` (1M context)
