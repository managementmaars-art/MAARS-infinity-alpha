"""Web search and browsing service for MAARS Command agents.
Gives agents the ability to search the internet and extract information, similar to ChatGPT browsing."""

import logging
import asyncio
import re
from typing import List, Dict, Optional
from datetime import datetime, timezone

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# Keywords/patterns that suggest the user needs web data
WEB_TRIGGER_PATTERNS = [
    r'\b(latest|current|today|recent|new|updated|now|this year|this month)\b',
    r'\b(202[3-9]|203[0-9])\b',
    r'\b(price|rate|cost|stock|market|exchange|salary|wage)\b',
    r'\b(news|happened|announced|released|launched|trending)\b',
    r'\b(what is|what are|who is|who are|where is|how to|how much|how many|when is|when did)\b',
    r'\b(weather|forecast|score|result|standings|schedule)\b',
    r'\b(law|regulation|policy|circular|act|amendment|rule|guideline|deadline)\b',
    r'\b(review|compare|comparison|vs|versus|best|top|ranking)\b',
    r'\b(website|url|link|site|source|reference)\b',
    r'\b(find|search|look up|lookup|google|check|verify)\b',
    r'\b(tell me about|explain|describe|details about|info on|information about)\b',
    r'\b(country|government|bank|company|organization|university)\b',
]


def needs_web_search(message: str) -> bool:
    """Detect if a message likely needs web search for accurate answers."""
    msg_lower = message.lower()

    # Skip very short messages or greetings
    if len(message.split()) < 4:
        return False
    greetings = ["hello", "hi", "hey", "thanks", "thank you", "bye", "ok", "yes", "no"]
    if msg_lower.strip().rstrip("!.?") in greetings:
        return False

    # Check trigger patterns
    match_count = sum(1 for p in WEB_TRIGGER_PATTERNS if re.search(p, msg_lower))
    return match_count >= 2


async def web_search(query: str, max_results: int = 5) -> List[Dict]:
    """Search the web using DDGS and return results."""
    try:
        from ddgs import DDGS
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                results.append({
                    "title": r.get("title", ""),
                    "url": r.get("href", r.get("link", "")),
                    "snippet": r.get("body", r.get("snippet", "")),
                })
        logger.info(f"Web search '{query[:50]}': {len(results)} results")
        return results
    except Exception as e:
        logger.error(f"Web search failed: {e}")
        return []


async def scrape_page(url: str, timeout: float = 8.0) -> str:
    """Scrape a webpage and extract clean text content."""
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=timeout) as client:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
            }
            resp = await client.get(url, headers=headers)
            resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")

        # Remove scripts, styles, nav, footer
        for tag in soup(["script", "style", "nav", "footer", "header", "aside", "iframe", "noscript"]):
            tag.decompose()

        # Get text from main content areas
        main = soup.find("main") or soup.find("article") or soup.find("div", {"role": "main"})
        if main:
            text = main.get_text(separator="\n", strip=True)
        else:
            text = soup.get_text(separator="\n", strip=True)

        # Clean up
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        text = "\n".join(lines)

        # Limit to ~2000 chars
        if len(text) > 2000:
            text = text[:2000] + "..."

        return text
    except Exception as e:
        logger.debug(f"Failed to scrape {url}: {e}")
        return ""


async def search_and_browse(query: str, max_results: int = 3, max_scrape: int = 2) -> Dict:
    """Search the web and scrape top results for detailed content."""
    results = await web_search(query, max_results=max_results)
    if not results:
        return {"query": query, "results": [], "content": ""}

    # Scrape top results concurrently
    scrape_tasks = []
    for r in results[:max_scrape]:
        if r.get("url"):
            scrape_tasks.append(scrape_page(r["url"]))

    scraped = []
    if scrape_tasks:
        scraped = await asyncio.gather(*scrape_tasks, return_exceptions=True)

    # Build content
    enriched_results = []
    for i, r in enumerate(results):
        entry = {
            "title": r["title"],
            "url": r["url"],
            "snippet": r["snippet"],
        }
        if i < len(scraped) and isinstance(scraped[i], str) and scraped[i]:
            entry["full_text"] = scraped[i]
        enriched_results.append(entry)

    return {
        "query": query,
        "results": enriched_results,
        "searched_at": datetime.now(timezone.utc).isoformat(),
    }


def build_web_context(search_data: Dict) -> str:
    """Build context string from web search results for injection into agent prompt."""
    results = search_data.get("results", [])
    if not results:
        return ""

    parts = ["\n--- WEB SEARCH RESULTS ---"]
    parts.append(f"Search query: \"{search_data.get('query', '')}\"")
    parts.append(f"Searched at: {search_data.get('searched_at', 'now')}\n")

    for i, r in enumerate(results, 1):
        parts.append(f"[Web Source {i}: {r['title']}]")
        parts.append(f"URL: {r['url']}")
        if r.get("full_text"):
            parts.append(r["full_text"][:1500])
        elif r.get("snippet"):
            parts.append(r["snippet"])
        parts.append("")

    parts.append("WEB CITATION INSTRUCTIONS: When using web information, cite the source like: \"According to [Source Title](URL)...\" or include the URL. Always mention if information might be outdated.")
    parts.append("--- END WEB SEARCH ---\n")
    return "\n".join(parts)


async def auto_search_for_message(message: str, agent_role: str = "") -> Optional[str]:
    """Auto-detect if web search is needed and return context if so."""
    if not needs_web_search(message):
        return None

    # Formulate a good search query from the user's message
    # Use the message directly, trimmed to a reasonable length
    query = message.strip()
    if len(query) > 200:
        # Take the first sentence or key part
        sentences = re.split(r'[.!?\n]', query)
        query = sentences[0][:200] if sentences else query[:200]

    search_data = await search_and_browse(query, max_results=4, max_scrape=2)

    if not search_data.get("results"):
        return None

    return build_web_context(search_data)
