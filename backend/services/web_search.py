"""Web browsing service for MAARS Command agents.
Production-grade internet search and content extraction — works like ChatGPT browsing."""

import logging
import asyncio
import re
from typing import List, Dict, Optional
from datetime import datetime, timezone

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# Messages that should NEVER trigger search
SKIP_PATTERNS = [
    r'^(hi|hello|hey|thanks|thank you|bye|ok|yes|no|sure|great|cool|nice|good|please|alright)\s*[!.?]*$',
    r'^(what can you do|help me|who are you|introduce yourself)',
]

# Messages that should ALWAYS trigger search
FORCE_SEARCH_PATTERNS = [
    r'\b(latest|current|today|recent|now|this year|this month|right now|as of)\b',
    r'\b(202[3-9]|203[0-9])\b',
    r'\b(news|happened|announced|released|launched|trending|update)\b',
    r'\b(price|rate|cost|stock|market|exchange|salary|wage|gdp|inflation)\b',
    r'\b(weather|forecast|score|standings|schedule|election|vote)\b',
    r'\b(company|organization|startup|ceo|founder|president|minister|government)\b',
]

# Softer signals — need 2+ to trigger
SOFT_PATTERNS = [
    r'\b(what is|what are|who is|who are|where is|how to|how much|how many|when is|when did|when was|why did|why is)\b',
    r'\b(law|regulation|policy|circular|act|amendment|rule|guideline|deadline|tax|banking)\b',
    r'\b(review|compare|comparison|vs|versus|best|top|ranking|recommended)\b',
    r'\b(find|search|look up|google|check|verify|confirm)\b',
    r'\b(tell me about|explain|describe|details|info|information|learn about|research)\b',
    r'\b(country|city|state|university|hospital|bank|airport|hotel)\b',
    r'\b(recipe|tutorial|guide|instructions|steps|process|procedure)\b',
    r'\b(statistics|data|numbers|figures|percentage|report)\b',
]


def should_search(message: str) -> bool:
    """Determine if a message needs web search. Biased toward searching."""
    msg = message.strip().lower()

    # Skip very short messages
    if len(msg.split()) < 3:
        return False

    # Skip greetings/pleasantries
    for p in SKIP_PATTERNS:
        if re.match(p, msg, re.IGNORECASE):
            return False

    # Force search for time-sensitive or factual queries
    for p in FORCE_SEARCH_PATTERNS:
        if re.search(p, msg, re.IGNORECASE):
            return True

    # Check soft signals — need 2+
    soft_matches = sum(1 for p in SOFT_PATTERNS if re.search(p, msg, re.IGNORECASE))
    if soft_matches >= 2:
        return True

    # If the message is a question (ends with ?) and has 5+ words, search
    if msg.rstrip().endswith('?') and len(msg.split()) >= 5:
        return True

    return False


def extract_search_query(message: str) -> str:
    """Extract a clean, effective search query from the user's message."""
    # Remove common filler words for a tighter query
    query = message.strip()

    # If it's a question, keep it as-is but cap length
    if len(query) > 150:
        # Take up to the first sentence or 150 chars
        for sep in ['. ', '? ', '! ', '\n']:
            idx = query.find(sep)
            if 0 < idx < 200:
                query = query[:idx]
                break
        else:
            query = query[:150]

    # Remove polite prefixes
    for prefix in ['can you ', 'could you ', 'please ', 'i want to know ', 'i need to know ',
                    'tell me ', 'help me ', 'i would like to know ']:
        if query.lower().startswith(prefix):
            query = query[len(prefix):]

    return query.strip()


async def web_search(query: str, max_results: int = 5) -> List[Dict]:
    """Search the web using DuckDuckGo."""
    try:
        from ddgs import DDGS

        results = []
        # Run in thread since DDGS is synchronous
        def _search():
            with DDGS() as ddgs:
                return list(ddgs.text(query, max_results=max_results))

        raw = await asyncio.to_thread(_search)
        for r in raw:
            results.append({
                "title": r.get("title", ""),
                "url": r.get("href", r.get("link", "")),
                "snippet": r.get("body", r.get("snippet", "")),
            })
        logger.info(f"Web search '{query[:60]}': {len(results)} results")
        return results
    except Exception as e:
        logger.error(f"Web search failed: {e}")
        return []


async def scrape_url(url: str, timeout: float = 10.0) -> str:
    """Extract clean readable text from a URL."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Cache-Control": "no-cache",
        }
        async with httpx.AsyncClient(follow_redirects=True, timeout=timeout, headers=headers) as client:
            resp = await client.get(url)
            if resp.status_code != 200:
                return ""
            content_type = resp.headers.get("content-type", "")
            if "text/html" not in content_type and "application/xhtml" not in content_type:
                return ""

        soup = BeautifulSoup(resp.text, "html.parser")

        # Remove noise
        for tag in soup(["script", "style", "nav", "footer", "header", "aside",
                         "iframe", "noscript", "svg", "form", "button", "input"]):
            tag.decompose()

        # Try content-rich selectors in order of preference
        content = None
        selectors = [
            ("article", {}),
            ("main", {}),
            ("div", {"id": "mw-content-text"}),  # Wikipedia
            ("div", {"role": "main"}),
            ("div", {"class": re.compile(r"(article|post|content|entry|story)-?(body|content|text|main)", re.I)}),
            ("div", {"id": re.compile(r"(article|content|main|body)", re.I)}),
        ]
        for tag_name, attrs in selectors:
            el = soup.find(tag_name, attrs)
            if el and len(el.get_text(strip=True)) > 200:
                content = el
                break

        if content:
            text = content.get_text(separator="\n", strip=True)
        else:
            # Fallback: concatenate all meaningful <p> tags
            paragraphs = soup.find_all("p")
            texts = [p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 30]
            text = "\n".join(texts)

        # Clean
        lines = []
        for line in text.splitlines():
            line = line.strip()
            if len(line) > 20:
                lines.append(line)
        text = "\n".join(lines)

        return text[:3000] if text else ""
    except Exception as e:
        logger.debug(f"Scrape failed for {url}: {e}")
        return ""


async def search_and_extract(query: str, max_results: int = 5, max_scrape: int = 3) -> Dict:
    """Search the web and extract content from top results."""
    results = await web_search(query, max_results=max_results)
    if not results:
        return {"query": query, "sources": [], "searched_at": datetime.now(timezone.utc).isoformat()}

    # Scrape top results concurrently
    urls_to_scrape = [r["url"] for r in results[:max_scrape] if r.get("url")]
    scraped_texts = await asyncio.gather(
        *[scrape_url(u) for u in urls_to_scrape],
        return_exceptions=True
    )

    sources = []
    for i, r in enumerate(results):
        source = {
            "title": r["title"],
            "url": r["url"],
            "snippet": r["snippet"],
            "content": "",
        }
        if i < len(scraped_texts) and isinstance(scraped_texts[i], str):
            source["content"] = scraped_texts[i]
        sources.append(source)

    return {
        "query": query,
        "sources": sources,
        "searched_at": datetime.now(timezone.utc).isoformat(),
    }


def format_web_context(search_data: Dict) -> str:
    """Format web search results into a context block that the LLM MUST use."""
    sources = search_data.get("sources", [])
    if not sources:
        return ""

    lines = []
    lines.append("\n=== LIVE WEB SEARCH RESULTS ===")
    lines.append(f"Query: {search_data.get('query', '')}")
    lines.append(f"Time: {search_data.get('searched_at', '')}")
    lines.append("")

    for i, s in enumerate(sources, 1):
        lines.append(f"--- Source {i}: {s['title']} ---")
        lines.append(f"URL: {s['url']}")
        # Use full scraped content if available, otherwise snippet
        body = s.get("content") or s.get("snippet", "")
        if body:
            lines.append(body[:2000])
        lines.append("")

    lines.append("=== END WEB RESULTS ===")
    lines.append("")
    lines.append("MANDATORY: The above is LIVE data you just retrieved from the internet. You MUST:")
    lines.append("1. Base your answer on this data. Synthesize and present it clearly.")
    lines.append("2. Cite sources naturally: \"According to [Title](URL)...\" or \"Source: URL\"")
    lines.append("3. If the data doesn't fully answer the question, share what you found and note what's missing.")
    lines.append("4. NEVER say you cannot access the internet — you just did.")
    lines.append("")

    return "\n".join(lines)


async def browse_web_for_message(message: str) -> Optional[str]:
    """Main entry point: decide if search is needed, search, and return formatted context."""
    if not should_search(message):
        return None

    query = extract_search_query(message)
    if not query:
        return None

    search_data = await search_and_extract(query, max_results=5, max_scrape=3)

    if not search_data.get("sources"):
        return None

    return format_web_context(search_data)
