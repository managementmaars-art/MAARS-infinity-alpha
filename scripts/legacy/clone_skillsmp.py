import cloudscraper
import os
import json
import time
import re
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

API_KEY = 'sk_live_skillsmp_nmzbSNajmLgoh-VYDqNT2xZBCdHRL63lHEDJws0_Xlg'
BASE = 'c:/Users/Yaleena Yara/MAARS-Command/.claude/skills'
HEADERS = {'Authorization': f'Bearer {API_KEY}'}

scraper = cloudscraper.create_scraper()

def fetch_all_skills():
    """Fetch all unique skills from the API across all sort orders."""
    all_skills = {}
    sort_options = ['recent', 'popular', 'stars', 'name', 'updated']

    for sort in sort_options:
        print(f'Fetching sort={sort}...')
        for page in range(1, 13):
            try:
                r = scraper.get(
                    f'https://skillsmp.com/api/skills?limit=100&page={page}&sortBy={sort}',
                    headers=HEADERS, timeout=30
                )
                data = r.json()
                skills = data.get('skills', [])
                if not skills:
                    break
                for s in skills:
                    sid = s.get('id', '')
                    if sid and sid not in all_skills:
                        all_skills[sid] = s
                if not data.get('pagination', {}).get('hasNext'):
                    break
                time.sleep(0.3)
            except Exception as e:
                print(f'  Error page {page}: {e}')
                time.sleep(2)
        print(f'  Total unique so far: {len(all_skills)}')

    return list(all_skills.values())

def github_url_to_raw(github_url, path='SKILL.md', branch='main'):
    """Convert GitHub tree URL to raw content URL."""
    # https://github.com/owner/repo/tree/branch/subdir -> raw URL
    # https://github.com/owner/repo -> raw URL
    github_url = github_url.rstrip('/')

    # Match: github.com/owner/repo/tree/branch/subpath
    m = re.match(r'https://github\.com/([^/]+)/([^/]+)/tree/([^/]+)/(.*)', github_url)
    if m:
        owner, repo, br, subpath = m.groups()
        return f'https://raw.githubusercontent.com/{owner}/{repo}/{br}/{subpath}/{path}'

    # Match: github.com/owner/repo
    m = re.match(r'https://github\.com/([^/]+)/([^/]+)$', github_url)
    if m:
        owner, repo = m.groups()
        return f'https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}'

    return None

def fetch_skill_content(skill):
    """Fetch the actual SKILL.md content from GitHub."""
    github_url = skill.get('githubUrl', '')
    path = skill.get('path', 'SKILL.md')
    branch = skill.get('branch', 'main')

    if not github_url:
        return None

    raw_url = github_url_to_raw(github_url, path, branch)
    if not raw_url:
        return None

    try:
        r = requests.get(raw_url, timeout=10)
        if r.status_code == 200:
            return r.text
    except Exception:
        pass

    # Try alternate branches
    for alt_branch in ['master', 'main']:
        if alt_branch == branch:
            continue
        raw_url = github_url_to_raw(github_url, path, alt_branch)
        if raw_url:
            try:
                r = requests.get(raw_url, timeout=10)
                if r.status_code == 200:
                    return r.text
            except Exception:
                pass

    return None

def create_skill(skill, content=None):
    """Create skill directory with SKILL.md content."""
    name = skill.get('name', '').strip()
    if not name or len(name) < 2 or '/' in name or '\\' in name or ' ' in name:
        return False

    d = os.path.join(BASE, name)

    # Use fetched content if available, otherwise build from API data
    if content:
        skill_md = content
    else:
        desc = skill.get('description', f'{name} skill')[:300]
        title = name.replace('-', ' ').title()
        skill_md = f"""---
name: {name}
description: {desc}
---

# {title}

## Overview
{desc}

## Usage
Use this skill to leverage {title.lower()} capabilities in your agent workflows.

## Best Practices
1. Follow official documentation and guidelines
2. Handle errors and edge cases gracefully
3. Test thoroughly before production use
"""

    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, 'SKILL.md'), 'w', encoding='utf-8') as f:
        f.write(skill_md)
    return True

# Step 1: Fetch all skills from API
print('=== Step 1: Fetching all skills from skillsmp API ===')
all_skills = fetch_all_skills()
print(f'\nTotal unique skills from API: {len(all_skills)}')

# Step 2: Filter out already-installed ones that already have content
new_skills = []
update_skills = []
for s in all_skills:
    name = s.get('name', '').strip()
    if not name:
        continue
    d = os.path.join(BASE, name)
    skill_file = os.path.join(d, 'SKILL.md')
    if not os.path.exists(d):
        new_skills.append(s)
    elif os.path.exists(skill_file):
        # Check if it was auto-generated (no real content from GitHub)
        with open(skill_file, encoding='utf-8', errors='ignore') as f:
            content = f.read()
        if 'Key Capabilities' in content and 'Best practice patterns' in content:
            update_skills.append(s)  # Replace with real content

print(f'New skills to create: {len(new_skills)}')
print(f'Skills to update with real content: {len(update_skills)}')

to_process = new_skills + update_skills

# Step 3: Fetch real SKILL.md content from GitHub and create/update
print(f'\n=== Step 2: Cloning {len(to_process)} skills from GitHub ===')

created = 0
updated = 0
fallback = 0
failed = 0

def process_skill(skill):
    content = fetch_skill_content(skill)
    return skill, content

with ThreadPoolExecutor(max_workers=20) as executor:
    futures = {executor.submit(process_skill, s): s for s in to_process}
    done = 0
    for future in as_completed(futures):
        done += 1
        skill, content = future.result()
        name = skill.get('name', '')
        is_new = skill in new_skills

        if create_skill(skill, content):
            if content:
                if is_new:
                    created += 1
                else:
                    updated += 1
            else:
                fallback += 1
        else:
            failed += 1

        if done % 100 == 0:
            print(f'  Processed {done}/{len(to_process)} | created={created} updated={updated} fallback={fallback} failed={failed}')

print(f'\n=== Done ===')
print(f'Created (with real content): {created}')
print(f'Updated (with real content): {updated}')
print(f'Created (fallback/no GitHub): {fallback}')
print(f'Failed: {failed}')
print(f'Total skills now: {len(os.listdir(BASE))}')
