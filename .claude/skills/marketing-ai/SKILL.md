---
name: marketing-ai
description: AI-powered marketing skills — campaign strategy, ad copy, social media content, email sequences, brand messaging, A/B testing, funnel optimization for MAARS marketing agents
---

# Marketing AI — MAARS Reference

## Core Marketing Agent Capabilities

### Campaign Strategy Framework
```
1. AUDIENCE: Demographics, psychographics, pain points, jobs-to-be-done
2. POSITIONING: Unique value prop, differentiation, competitive moat
3. CHANNELS: Paid (Meta/Google/LinkedIn), Organic (SEO/Content), CRM
4. FUNNEL: Awareness → Consideration → Decision → Retention
5. METRICS: CTR, CPC, CPL, CAC, LTV, ROAS, MQLs, pipeline value
6. TESTING: A/B hypotheses, success criteria, min sample sizes
```

### Ad Copy Prompts
```python
AD_COPY_PROMPT = """
You are Zara Mitchell, MAARS Marketing Specialist.

Create {num_variants} ad copy variants for:
- Platform: {platform} (Facebook/Google/LinkedIn/TikTok)
- Product: {product}
- Target audience: {audience}
- Pain point addressed: {pain_point}
- CTA: {cta}
- Character limit: {char_limit}

For each variant provide:
1. Headline
2. Body copy
3. CTA button text
4. Hook type used (curiosity/pain/social proof/urgency/benefit)
"""
```

### Email Sequence Templates
```python
EMAIL_SEQUENCES = {
    "welcome": ["Day 0: Welcome + quick win", "Day 2: Core value education", 
                "Day 5: Social proof", "Day 7: Soft pitch"],
    "nurture": ["Value content", "Case study", "Pain amplification", "Solution pitch"],
    "reengagement": ["We miss you", "What's changed", "Special offer", "Last chance"],
    "onboarding": ["Account setup", "Feature 1", "Feature 2", "Success milestone"],
}
```

### Social Media Content Calendar
```python
CONTENT_PILLARS = {
    "educational": 0.40,   # 40% — teach something valuable
    "inspirational": 0.20, # 20% — motivation, success stories
    "promotional": 0.20,   # 20% — product/service focus
    "engaging": 0.20,      # 20% — polls, questions, UGC
}

PLATFORM_FORMATS = {
    "linkedin": {"post_length": "1300 chars", "hashtags": 3, "tone": "professional"},
    "instagram": {"caption_length": "150 chars", "hashtags": 10, "tone": "visual-first"},
    "twitter": {"length": "280 chars", "hashtags": 2, "tone": "conversational"},
    "tiktok": {"hook": "first 3 seconds critical", "length": "30-60s", "tone": "entertaining"},
}
```

### Brand Voice Analysis
```python
BRAND_VOICE_PROMPT = """
Analyze this brand's voice and create a style guide:
- Tone: formal/casual/playful/authoritative
- Language: simple/technical/aspirational
- Personality traits: 3-5 adjectives
- Words to use: 10 examples
- Words to avoid: 10 examples
- Example good sentence: 
- Example bad sentence:
"""
```

### GTM Strategy Template
```
TARGET MARKET: [Specific segment, not "everyone"]
VALUE PROPOSITION: [1 sentence, customer-centric]
PRICING: [Model + rationale]
CHANNELS: [Ranked by CAC efficiency]
LAUNCH SEQUENCE: [Week 1-12 milestones]
SUCCESS METRICS: [What defines PMF]
BUDGET ALLOCATION: [% by channel]
```

### Performance Benchmarks
```python
BENCHMARKS = {
    "email": {"open_rate": 0.21, "ctr": 0.025, "conversion": 0.01},
    "facebook_ads": {"ctr": 0.009, "cpm": 14.0, "conversion_rate": 0.09},
    "google_ads": {"ctr": 0.05, "cpc": 2.5, "conversion_rate": 0.04},
    "linkedin_ads": {"ctr": 0.004, "cpm": 33.0, "conversion_rate": 0.025},
    "seo": {"ctr_position_1": 0.28, "ctr_position_5": 0.06},
}
```

## Models to Use
- **Strategy + Copy**: `gpt-5.2` or `claude-opus-4-6`
- **Bulk content generation**: `gpt-4o` or `mistral-large`
- **Social captions**: `gpt-4o-mini` or `deepseek-chat`
- **Performance analysis**: `gpt-4o` with Code Interpreter
