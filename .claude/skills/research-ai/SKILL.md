---
name: research-ai
description: AI research skills — academic research, market research, competitive intelligence, literature review, fact-checking, citation management for MAARS research agents
---

# Research AI — MAARS Reference

## Research Framework
```python
RESEARCH_PROMPT = """
You are Dr. Clara Voss, MAARS Research Specialist.

Research question: {question}
Scope: {scope} (academic/market/competitive/technical)
Depth: {depth} (overview/comprehensive/exhaustive)
Output format: {format} (brief/report/memo/presentation)

Research process:
1. Define key terms and scope boundaries
2. Identify primary sources
3. Synthesize findings across sources
4. Identify consensus vs. contested areas
5. Flag knowledge gaps
6. Provide confidence level for each claim

Always:
- Cite sources with URLs or references
- Distinguish between facts, opinions, and projections
- Note recency of information
- Flag areas needing expert verification
"""
```

## Market Research Template
```
MARKET OVERVIEW:
- Total Addressable Market (TAM): $X billion by YEAR
- Serviceable Addressable Market (SAM): $X
- Growth rate: X% CAGR
- Key growth drivers (3-5)
- Key headwinds (2-3)

COMPETITIVE LANDSCAPE:
- Market leaders + estimated market share
- Emerging challengers
- Competitive dynamics (price/feature/distribution)
- Consolidation trends

CUSTOMER INSIGHTS:
- Primary buyer personas
- Key pain points (ranked by frequency)
- Buying process and decision criteria
- Price sensitivity

REGULATORY ENVIRONMENT:
- Current regulations affecting market
- Pending legislation
- Compliance costs

OPPORTUNITIES:
- Underserved segments
- Technology-driven disruption potential
- Geographic expansion opportunities
```

## Literature Review System
```python
LITERATURE_REVIEW_PROMPT = """
Conduct a literature review on: {topic}

Sources to cover:
- Academic papers (Google Scholar, PubMed, arXiv)
- Industry reports (Gartner, McKinsey, Forrester)
- News and recent developments

Structure:
1. OVERVIEW: Current state of knowledge
2. THEORETICAL FRAMEWORKS: Main models/theories
3. KEY FINDINGS: What research shows (with citations)
4. METHODOLOGIES: How researchers study this
5. DEBATES: Areas of disagreement
6. GAPS: What's not yet known
7. RECENT DEVELOPMENTS: Last 12 months
8. REFERENCES: APA format citations

Confidence levels: Mark each claim as (High/Medium/Low confidence)
"""
```

## Fact-Checking Protocol
```python
FACT_CHECK_PROMPT = """
Fact-check these claims:
{claims}

For each claim:
1. VERDICT: True / Mostly True / Misleading / False / Unverifiable
2. EVIDENCE: Specific sources that support or refute
3. NUANCE: Important context or caveats
4. SOURCES: Direct links to primary sources

Priority: Use primary sources over secondary. 
Flag claims that cannot be verified from available sources.
"""
```

## Citation Formats
```python
CITATION_FORMATS = {
    "APA": "{author} ({year}). {title}. {journal}, {volume}({issue}), {pages}. {doi}",
    "MLA": '{author}. "{title}." {journal} {volume}.{issue} ({year}): {pages}.',
    "Chicago": '{author}. "{title}." {journal} {volume}, no. {issue} ({year}): {pages}.',
    "Harvard": '{author} ({year}) "{title}", {journal}, vol. {volume}, pp. {pages}.',
}
```

## Source Quality Hierarchy
```python
SOURCE_HIERARCHY = {
    "tier_1": ["Peer-reviewed journals", "Government statistics", "Primary research"],
    "tier_2": ["Established news organizations", "Industry reports (Big 4, Gartner)",
               "Company official statements"],
    "tier_3": ["Reputable blogs by domain experts", "Conference proceedings",
               "Wikipedia (as starting point only)"],
    "avoid": ["Anonymous sources", "Outdated data (>3 years for fast-moving fields)",
              "Single-source claims without corroboration"],
}
```

## Models to Use
- **Deep research**: `perplexity/sonar-deep-research` (real-time, multi-step)
- **Academic synthesis**: `claude-opus-4-6` (best at nuanced analysis)
- **Market research**: `gpt-5.2` + Perplexity `sonar-pro`
- **Fast fact-checks**: `grok-3` (real-time web)
- **Long document synthesis**: `moonshot/kimi-latest` (1M context)
