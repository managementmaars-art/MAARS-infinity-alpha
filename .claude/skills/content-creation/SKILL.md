---
name: content-creation
description: AI content creation skills — blog posts, copywriting, scripts, newsletters, product descriptions, SEO articles, storytelling frameworks for MAARS content agents
---

# Content Creation AI — MAARS Reference

## Writing Frameworks

### Blog Post Structure
```
TITLE: [Power word] + [Number/How] + [Keyword] + [Promise]
       "7 Proven Ways to [Achieve X] Without [Common Pain]"

HOOK (100 words): Bold claim → relatable problem → promise of solution

INTRO: What they'll learn, why it matters, credibility signal

BODY SECTIONS (H2s):
  - Each section = one idea + explanation + example + takeaway
  - Use bucket brigades: "But here's the thing..." / "Here's why..."
  - Data points + stories alternate

CTA: Specific next step, not generic "learn more"

SEO: Target keyword in title, H1, first 100 words, 2-3 H2s, meta description
```

### Copywriting Formulas
```python
COPY_FORMULAS = {
    "AIDA": "Attention → Interest → Desire → Action",
    "PAS": "Problem → Agitate → Solve",
    "FAB": "Feature → Advantage → Benefit",
    "4Ps": "Promise → Picture → Proof → Push",
    "BAB": "Before → After → Bridge",
    "SLAP": "Stop → Look → Act → Purchase",
    "Star_Story_Solution": "Relatable protagonist → conflict → resolution",
}
```

### Product Description Template
```
HEADLINE: [Primary benefit] + [Product name]
SUBHEADLINE: [Who it's for] + [Key differentiator]

BODY:
- Lead with the transformation, not the features
- 3 key benefits (not features) with proof
- Handle the #1 objection
- Social proof (number, testimonial, or logo)

TECHNICAL SPECS: (for consideration stage buyers)
CTA: Action verb + benefit + urgency (if genuine)
```

### Newsletter Structure
```
SUBJECT LINE: [Curiosity gap] OR [Specific benefit] OR [News hook]
PREVIEW TEXT: Extends subject, adds intrigue

OPENING: Personal, relatable, 2-3 sentences
MAIN STORY: One idea, deeply explored (300-600 words)
SECONDARY ITEMS: 2-3 short links with context (not just URLs)
ACTIONABLE TAKEAWAY: One thing they can do today
CTA: Single, clear, relevant
SIGN-OFF: Personal, consistent voice
```

### Video Script Formula
```
0:00-0:03  HOOK: Most compelling moment or bold statement (pattern interrupt)
0:03-0:15  PROBLEM: Viewer's pain point, make them feel seen
0:15-0:45  AGITATE: Why it's worse than they think / common failed solutions
0:45-2:00  SOLUTION: Your method, step by step
2:00-2:30  PROOF: Results, testimonial, or demonstration
2:30-3:00  CTA: Specific action + benefit of taking it
```

### SEO Content Brief
```python
SEO_BRIEF = {
    "primary_keyword": "",
    "secondary_keywords": [],
    "search_intent": "informational|navigational|commercial|transactional",
    "target_word_count": 1500,
    "competing_articles_to_beat": [],
    "required_sections": [],
    "internal_links": [],
    "target_featured_snippet": "",
    "meta_title": "",  # <60 chars, include primary KW
    "meta_description": "",  # <160 chars, include CTA
}
```

### Tone & Voice Spectrum
```
FORMAL ←──────────────────────────────────────→ CASUAL
Corporate  Professional  Friendly  Conversational  Playful

FOR EACH BRAND SET:
- Vocabulary level (simple/intermediate/advanced)
- Sentence length (short=punchy / long=authoritative)
- Use of humor (none/subtle/frequent)
- Use of contractions (formal=no / casual=yes)
- Second person (you/your) usage
- Active vs passive voice ratio
```

## Models to Use
- **Long-form articles**: `claude-opus-4-6` (best writing quality)
- **Ad copy / short-form**: `gpt-4o` (fast + creative)
- **Bulk product descriptions**: `gpt-4o-mini` or `deepseek-chat`
- **Scripts**: `claude-sonnet-4-6`
- **Multilingual content**: `qwen-max` or `mistral-large`
