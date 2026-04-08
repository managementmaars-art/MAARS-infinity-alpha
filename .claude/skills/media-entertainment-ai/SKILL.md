---
name: media-entertainment-ai
description: AI media & entertainment skills — script writing, content strategy, streaming analytics, audience analysis, IP development, production planning for MAARS media agents
---

# Media & Entertainment AI — MAARS Reference

## Script & Screenplay Writing
```python
SCREENPLAY_PROMPT = """
Write a screenplay scene in proper format.
Genre: {genre}
Project: {title}
Scene location: INT./EXT. {location} - {time_of_day}
Characters in scene: {characters}
Scene purpose: {dramatic_purpose}
Previous scene: {preceding_scene}
Scene goal: What must happen by end of scene

Write following professional screenplay format:
- Scene heading (SLUGLINE)
- Action lines (present tense, visual, no camera directions)
- Dialogue with character cues and parentheticals (use sparingly)
- Page target: {target_pages} pages

Craft:
- Subtext: Characters rarely say what they mean
- Conflict: Every scene needs tension or stakes
- Economy: Every word serves the story
- Voice: Consistent with {tone} tone established
"""

TV_BIBLE_TEMPLATE = """
SERIES TITLE: {title}
Format: {format} (30-min comedy/60-min drama/limited series)
Network target: {network}
Logline: (25 words max)

THE WORLD: Where and when. What makes this world unique.

PREMISE: The hook. The ongoing dramatic engine. What happens week-to-week.

CHARACTERS:
- {protagonist}: [Who they are, what they want, what they need, flaw]
- [Supporting characters with their dramatic function]

SEASON ARC:
- Season 1 beginning/middle/end
- Episodic vs. serialized balance

EPISODE TEMPLATE: What a typical episode looks like

LONG-TERM VISION: Where the show goes in seasons 2-5

TONE: Comparable shows (A + B = us)
"""
```

## Content Strategy for Streaming
```python
CONTENT_STRATEGY_PROMPT = """
Develop content strategy for: {platform}
Platform type: {type} (SVOD/AVOD/FAST/Linear)
Target demographic: {demographic}
Current catalog: {catalog_size} titles
Budget: ${content_budget}/year
Competitors: {competitors}

Strategy framework:
1. AUDIENCE ANALYSIS:
   - Core viewer profiles (3-4 personas)
   - Content preferences by demo
   - Viewing patterns (binge vs. weekly)

2. CONTENT PILLARS:
   - Tent pole originals (5-10% of budget, drives subs)
   - Reliable returning series (retention)
   - Acquired content (volume, breadth)
   - Niche/passion content (superfans, churn prevention)

3. GENRE STRATEGY:
   - Priority genres by audience affinity score
   - Gaps vs. competition
   - International co-production opportunities

4. COMMISSIONING RECOMMENDATIONS:
   - Original series: {num_series} per year at {avg_budget}
   - Films: {num_films} per year
   - Docuseries: {num_docs} per year

5. WINDOWING STRATEGY:
   - Release pattern: all-at-once vs. weekly
   - International vs. domestic timing
   - Theatrical window if applicable
"""
```

## Audience Analytics
```python
AUDIENCE_ANALYSIS_PROMPT = """
Analyze streaming/media audience data:
Platform: {platform}
Period: {period}
Data provided: {available_metrics}

{audience_data}

Analyze:
1. ENGAGEMENT METRICS:
   - Completion rate by content type/genre
   - Binge rate (% watching 3+ episodes in 24h)
   - Return visits after premiere
   - Day-1 vs. Day-7 vs. Day-30 viewership

2. SUBSCRIBER HEALTH:
   - Churn rate and drivers (exit survey data)
   - Acquisition source and quality
   - LTV by cohort and acquisition channel
   - Churn prediction signals

3. CONTENT PERFORMANCE:
   - Title-level: Views, completion, save rate
   - Genre performance vs. expected
   - Time decay analysis

4. RECOMMENDATIONS ENGINE METRICS:
   - Click-through on recommendations
   - Discovery vs. search vs. browse ratio
   - Recommendation diversity score

5. ACTIONABLE INSIGHTS:
   - Content to greenlight/cancel
   - Retention opportunities
   - Pricing optimization
"""
```

## IP Development
```python
IP_DEVELOPMENT_PROMPT = """
Develop intellectual property concept:
Concept seed: {seed_idea}
Target format: {formats} (TV series/film franchise/book/game/theme park)
Target audience: {audience}
Tone: {tone}

Develop:
1. CORE CONCEPT: The heart of the IP (30 words)
2. WORLD BUILDING:
   - Setting (when/where/how different from our world)
   - Rules and logic of the world
   - History and mythology
   - Factions and power structures

3. CENTRAL CHARACTERS:
   - Hero/Protagonist: want, need, wound, flaw, strength
   - Antagonist: motivation (must be as valid as hero's)
   - Ensemble: 3-4 supporting characters with distinct functions

4. FRANCHISE ARCHITECTURE:
   - Primary format strategy
   - Spin-off and expansion opportunities
   - Transmedia potential (game, book, merch)
   - Real-world experiences

5. AUDIENCE APPEAL:
   - Core fan base
   - Casual viewer/reader appeal
   - International marketability

6. COMPARABLE FRANCHISES: What this is + what it isn't

7. THEMES: The deeper meaning beyond the plot
"""
```

## Production Planning AI
```python
PRODUCTION_BUDGET_PROMPT = """
Estimate production budget for: {project}
Format: {format}
Duration: {duration}
Production model: {model} (in-house/indie/studio/streaming)
Location: {location}
Union status: {union} (SAG/DGA/WGA/IATSE or non-union)

Budget breakdown:
1. ABOVE THE LINE:
   - Writer/Showrunner: ${range}
   - Director: ${range}
   - Producers: ${range}
   - Lead cast: ${range}

2. BELOW THE LINE:
   - Production crew (key dept. heads)
   - Equipment (camera, lighting, sound)
   - Locations (permits, fees)
   - Set construction/art department
   - Wardrobe/hair/makeup
   - VFX/post-production

3. POST-PRODUCTION:
   - Editing
   - Color grading
   - Sound design/mix
   - Music/score/licensing
   - Deliverables

4. CONTINGENCY: 10-15% of total

5. SHOOTING SCHEDULE:
   - Pages per day estimate
   - Total shoot days
   - Prep and wrap weeks

TOTAL ESTIMATED BUDGET: ${range}
COST PER EPISODE: ${range}
"""
```

## Social & Digital Media
```python
CONTENT_CALENDAR_PROMPT = """
Create a {duration}-month social media content calendar.
Brand: {brand}
Platforms: {platforms}
Content pillars: {pillars}
Key dates: {key_dates}
Tone: {tone}
Resources: {resources} (team size, budget)

For each week:
- HERO CONTENT (1x): High-production brand story
- HUB CONTENT (3x): Regular series/recurring format
- HYGIENE CONTENT (5-7x): Responsive, timely, evergreen
- COMMUNITY (daily): Engagement, replies, sharing

Include:
- Platform-specific format notes
- Hashtag strategy
- Influencer collaboration opportunities
- Paid amplification recommendations
- Performance benchmarks to track
"""
```

## Rights & Licensing Management
```python
RIGHTS_ANALYSIS_PROMPT = """
Analyze rights situation for: {content_title}
Ownership structure: {ownership}
Existing licenses: {existing_licenses}
Target deal: {deal_structure}

Audit:
1. RIGHTS CHAIN: Underlying rights (source material, music, clips)
2. TERRITORY AVAILABILITY: Which territories are free for licensing
3. PLATFORM RESTRICTIONS: Exclusivity windows
4. TALENT AGREEMENTS: Union residuals obligations
5. MUSIC CLEARANCES: Sync + master licenses needed
6. CLIP LICENSES: Third-party footage clearances
7. FORMAT RIGHTS: Which formats are covered

Estimate:
- Rights clearance costs for {territory} release
- Residuals obligations
- Guild requirements

RED FLAGS: Any rights issues that could block distribution
"""
```

## Models to Use
- **Script writing**: `claude-opus-4-6` (best creative writer, structure)
- **Audience analytics**: `gpt-4o` with code tools (data analysis)
- **Content strategy**: `claude-opus-4-6` (strategic thinking + creative)
- **IP development**: `claude-opus-4-6` (world building, character)
- **Production planning**: `claude-sonnet-4-6` (structured planning)
- **Rights research**: `perplexity/sonar-pro` (current deals, availability)
- **Social media content**: `claude-sonnet-4-6` (brand voice, platform-native)
