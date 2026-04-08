---
name: seo-ai
description: AI SEO skills — keyword research, technical SEO audits, on-page optimization, link building, local SEO, schema markup, Core Web Vitals for MAARS SEO agents
---

# SEO AI — MAARS Reference

## Keyword Research Framework
```python
KEYWORD_RESEARCH_PROMPT = """
You are Derek Huang, MAARS SEO Specialist.

For the topic "{topic}", provide:

1. PRIMARY KEYWORD: Highest volume, best fit
2. SECONDARY KEYWORDS: 5-10 semantically related terms
3. LONG-TAIL KEYWORDS: 10 low-competition, high-intent phrases
4. LSI KEYWORDS: 10 latent semantic terms Google expects to see
5. QUESTION KEYWORDS: "People Also Ask" style queries
6. COMPETITOR KEYWORDS: Gaps vs top 3 competitors

For each keyword estimate: Monthly Volume / Difficulty (1-100) / Intent
"""
```

## Technical SEO Audit Checklist
```python
TECHNICAL_SEO = {
    "crawlability": ["robots.txt", "xml_sitemap", "canonical_tags", "noindex_check",
                     "crawl_budget", "internal_linking_depth"],
    "indexability": ["meta_noindex", "canonical_conflicts", "redirect_chains",
                     "orphan_pages", "duplicate_content"],
    "page_speed": ["core_web_vitals", "lcp_target_<2.5s", "fid_target_<100ms",
                   "cls_target_<0.1", "ttfb_target_<200ms"],
    "mobile": ["responsive_design", "viewport_meta", "tap_targets", "font_sizes"],
    "structured_data": ["organization", "product", "faq", "article", "breadcrumb",
                        "local_business", "review"],
    "security": ["https", "mixed_content", "hsts"],
}
```

## On-Page SEO Template
```
TITLE TAG: Primary KW near front + brand | 50-60 chars
META DESC: Include KW + CTA + unique value | 150-160 chars
H1: Exact match or close variant of primary KW (1 per page)
H2s: Secondary KWs + question variants
URL SLUG: /primary-keyword/ (short, hyphenated, no stop words)
IMAGE ALT: Descriptive + KW where natural
INTERNAL LINKS: 3-5 to relevant pages with descriptive anchor text
EXTERNAL LINKS: 1-2 authoritative sources (opens new tab)
CONTENT: KW in first 100 words, natural density 1-2%
SCHEMA: Article / Product / FAQ as applicable
```

## Content Gap Analysis
```python
CONTENT_GAP_PROMPT = """
Compare these URLs for keyword coverage:
MINE: {my_url}
COMPETITORS: {comp1}, {comp2}, {comp3}

Find:
1. Keywords competitors rank for that I don't
2. Topics covered by 2+ competitors but not me
3. Featured snippets I'm missing
4. Related questions I haven't answered
5. Priority order: (search volume × competition difficulty gap)
"""
```

## Local SEO Checklist
```
GMB OPTIMIZATION:
□ Complete NAP (Name, Address, Phone) — exact match across web
□ Business categories (primary + secondary)
□ Business description with local keywords
□ Photos (exterior, interior, team, products)
□ Posts (weekly updates)
□ Q&A section seeded with common questions
□ Review response strategy

LOCAL CITATIONS:
□ Google Business Profile
□ Apple Maps / Bing Places
□ Yelp, TripAdvisor (if relevant)
□ Industry-specific directories
□ Chamber of commerce listing

LOCAL SCHEMA:
□ LocalBusiness schema with coordinates
□ OpeningHours
□ AggregateRating
```

## Link Building Strategies
```python
LINK_BUILDING = {
    "digital_pr": "Create data studies, surveys, original research that journalists cite",
    "guest_posting": "Target DA 40+ sites in your niche, pitch unique angles",
    "broken_link": "Find broken links on resource pages, offer your content as replacement",
    "skyscraper": "Find top-ranking content, create 10x better version, outreach to linkers",
    "resource_pages": "Find 'best X resources' pages, pitch to be added",
    "competitor_backlinks": "Reverse engineer competitor links, replicate best ones",
    "brand_mentions": "Find unlinked brand mentions, request link attribution",
    "HARO": "Respond to journalist queries for authoritative media backlinks",
}
```

## Core Web Vitals Optimization
```python
CWV_FIXES = {
    "LCP": {
        "target": "<2.5s",
        "fixes": ["preload hero image", "CDN for images", "optimize server response time",
                  "remove render-blocking resources", "lazy load below-fold images"],
    },
    "INP": {
        "target": "<200ms",
        "fixes": ["reduce JavaScript execution time", "defer non-critical JS",
                  "optimize event handlers", "use web workers"],
    },
    "CLS": {
        "target": "<0.1",
        "fixes": ["set explicit dimensions on images/videos", "reserve space for ads",
                  "avoid inserting content above existing content"],
    },
}
```

## Models to Use
- **Keyword research + strategy**: `gpt-5.2` + Perplexity `sonar-pro` for real-time data
- **Content writing**: `claude-opus-4-6`
- **Technical audits**: `gpt-4o` with code tools
- **Local SEO**: `gpt-4o`
