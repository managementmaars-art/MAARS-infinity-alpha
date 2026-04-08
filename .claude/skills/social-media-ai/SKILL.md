---
name: social-media-ai
description: AI social media skills — content strategy, platform-specific content, hashtag research, engagement tactics, viral hooks, influencer outreach for MAARS social agents
---

# Social Media AI — MAARS Reference

## Platform-Specific Content Guides

### LinkedIn (B2B Focus)
```python
LINKEDIN_POST_FORMULA = """
LINE 1: Bold hook (stat, contrarian take, story opener) — make them click "see more"
[blank line]
LINE 2-5: The payoff — insight, story, or argument
[blank line]
BULLETS: 3-5 takeaways (scannable)
[blank line]
CLOSE: Question or CTA (drives comments for reach)

HASHTAGS: 3-5 niche-specific (at end, not in text)
LENGTH: 1200-1800 chars for max reach
POSTING: Tue-Thu 8-10am local time
IMAGE: Optional but carousel = 3x reach
"""
```

### Instagram
```python
INSTAGRAM_CONTENT = {
    "feed_post": {
        "hook": "First line visible before 'more' must stop scroll",
        "caption_length": "150-300 chars or 1000+ for carousel",
        "hashtags": "10-15, mix of 10K-500K volume",
        "cta": "Save, share, or question in comments",
    },
    "reel": {
        "hook_seconds": "0-3s must grab attention",
        "optimal_length": "15-30s for max completion rate",
        "trending_audio": "Use trending sounds for algorithm boost",
        "text_overlay": "Caption key points for sound-off viewing",
    },
    "stories": {
        "swipe_up": "Use for direct conversion",
        "polls_questions": "High engagement = more reach",
        "frequency": "3-7 stories/day for active accounts",
    },
}
```

### Twitter/X
```python
TWITTER_TACTICS = {
    "thread_formula": [
        "Tweet 1: Bold claim or hook + 'thread 🧵'",
        "Tweets 2-8: One idea per tweet, numbered",
        "Tweet 9: Summary + takeaway",
        "Tweet 10: CTA (follow/RT/link)",
    ],
    "viral_hooks": [
        "I [did X] for [Y days/months]. Here's what I learned:",
        "Unpopular opinion: [controversial but defensible take]",
        "[Number] [things/mistakes/lessons] from [experience]:",
        "The [job title] playbook nobody talks about:",
    ],
    "engagement_tricks": [
        "Post at 8-10am or 6-8pm your audience timezone",
        "Reply to comments within first hour (boosts reach)",
        "Quote tweet with your take to ride trending topics",
        "Engage with larger accounts before posting",
    ],
}
```

### TikTok
```python
TIKTOK_FORMULA = {
    "hook_types": ["question", "shocking stat", "relatable pain", "transformation reveal"],
    "structure": "Hook(3s) → Problem(5s) → Solution(30s) → Result(10s) → CTA(5s)",
    "captions": "Short, keyword-rich, include 1-3 relevant hashtags",
    "sounds": "Use trending audio when relevant (check Trending tab)",
    "engagement": "Reply to comments with videos for algorithm boost",
    "best_times": "7-9am, 12-3pm, 7-11pm local time",
}
```

## Content Calendar Template
```python
CONTENT_CALENDAR_PROMPT = """
Create a 30-day social media content calendar for {brand}:
- Platforms: {platforms}
- Posting frequency: {frequency}
- Content pillars: {pillars}
- Key dates/events: {events}

For each post include:
- Date & time
- Platform
- Content type (post/reel/story/thread)
- Hook/headline
- Key message
- CTA
- Hashtags (if applicable)
- Visual direction

Balance: 40% educational, 20% entertaining, 20% promotional, 20% engagement
"""
```

## Viral Hook Templates
```python
VIRAL_HOOKS = [
    "I {action} for {timeframe}. The results shocked me.",
    "Stop {common_mistake}. Do this instead.",
    "{Number} things I wish I knew before {experience}.",
    "The {topic} playbook that took me {timeframe} to learn.",
    "Why {common_belief} is wrong (and what actually works).",
    "I asked {number} {experts} about {topic}. Here's what they said.",
    "The {job} cheat code nobody talks about.",
    "{Brand/Person} grew from {start} to {end} using this.",
]
```

## Engagement Rate Benchmarks
```python
BENCHMARKS = {
    "instagram": {"excellent": 0.06, "good": 0.035, "average": 0.018},
    "tiktok":    {"excellent": 0.18, "good": 0.09,  "average": 0.05},
    "linkedin":  {"excellent": 0.04, "good": 0.02,  "average": 0.01},
    "twitter":   {"excellent": 0.01, "good": 0.005, "average": 0.002},
    "facebook":  {"excellent": 0.03, "good": 0.015, "average": 0.007},
}
```

## Models to Use
- **Caption writing**: `gpt-4o` (fast + creative)
- **Strategy**: `claude-sonnet-4-6`
- **Trend analysis**: `grok-3` (real-time X data)
- **Bulk scheduling content**: `gpt-4o-mini` or `deepseek-chat`
