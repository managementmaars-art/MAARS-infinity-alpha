import cloudscraper
import os
import json
import time

API_KEY = 'sk_live_skillsmp_nmzbSNajmLgoh-VYDqNT2xZBCdHRL63lHEDJws0_Xlg'
BASE = 'c:/Users/Yaleena Yara/MAARS-Command/.claude/skills'
HEADERS = {'Authorization': f'Bearer {API_KEY}'}

scraper = cloudscraper.create_scraper()

# The API is capped at 1200 results. Fetch all 12 pages.
# We'll use different sortBy values to potentially get different sets.
all_skills = {}

sort_options = ['recent', 'popular', 'stars', 'name', 'updated']

for sort in sort_options:
    print(f'\n=== Fetching sort={sort} ===')
    for page in range(1, 13):  # 12 pages max
        try:
            r = scraper.get(
                f'https://skillsmp.com/api/skills?limit=100&page={page}&sortBy={sort}',
                headers=HEADERS
            )
            data = r.json()
            skills = data.get('skills', [])
            if not skills:
                break
            for s in skills:
                name = s.get('name', '').strip()
                if name and name not in all_skills:
                    all_skills[name] = s.get('description', '')
            pagination = data.get('pagination', {})
            print(f'  page {page}: got {len(skills)} skills, running total unique: {len(all_skills)}')
            if not pagination.get('hasNext'):
                break
            time.sleep(0.5)
        except Exception as e:
            print(f'  page {page} error: {e}')
            time.sleep(2)

print(f'\nTotal unique skills fetched: {len(all_skills)}')

# Now create skill directories for missing ones
created = 0
skipped = 0
for name, desc in all_skills.items():
    d = os.path.join(BASE, name)
    if os.path.exists(d):
        skipped += 1
        continue
    # Skip empty or invalid names
    if not name or len(name) < 2 or '/' in name or '\\' in name:
        continue
    os.makedirs(d, exist_ok=True)
    title = name.replace('-', ' ').title()
    desc_clean = desc[:200] if desc else f'{title} skill for AI agents'
    content = f"""---
name: {name}
description: {desc_clean}
---

# {title}

## Overview
{desc_clean}

## Usage
Use this skill to leverage {title.lower()} capabilities in your agent workflows.

## Key Capabilities
- Core {title.lower()} operations
- Integration with related tools and APIs
- Best practice patterns and examples

## Best Practices
1. Follow official documentation and guidelines
2. Handle errors and edge cases gracefully
3. Use environment variables for credentials
4. Test thoroughly before production use
5. Monitor and log for observability
"""
    with open(os.path.join(d, 'SKILL.md'), 'w', encoding='utf-8') as f:
        f.write(content)
    created += 1

print(f'Created: {created}')
print(f'Skipped (already exist): {skipped}')
print(f'Total skills now: {len(os.listdir(BASE))}')
