"""
Exhaust skillsmp.com API by probing for a search parameter,
then iterating all two-letter prefixes (aa-zz = 676 queries x 1200 = 811,200 potential results).
"""
import cloudscraper
import os
import json
import time
import re
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from itertools import product
import string
import sys

# Force UTF-8 output
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

API_KEY = 'sk_live_skillsmp_nmzbSNajmLgoh-VYDqNT2xZBCdHRL63lHEDJws0_Xlg'
BASE = 'c:/Users/Yaleena Yara/MAARS-Command/.claude/skills'
HEADERS = {'Authorization': f'Bearer {API_KEY}'}

scraper = cloudscraper.create_scraper()

# ── Step 1: Probe for a working search/filter parameter ──────────────────────
SEARCH_PARAM = None
PROBE_PARAMS = ['q', 'search', 'name', 'query', 'filter', 'prefix', 'keyword', 'term']

print('=== Probing for search parameter ===')

# Get baseline count (no filter)
try:
    r_base = scraper.get('https://skillsmp.com/api/skills?limit=100&page=1', headers=HEADERS, timeout=20)
    base_data = r_base.json()
    base_total = base_data.get('pagination', {}).get('totalAll', 0)
    base_count = len(base_data.get('skills', []))
    print(f'Baseline: {base_count} results per page, totalAll={base_total}')
except Exception as e:
    print(f'Baseline fetch failed: {e}')
    base_count = 100
    base_total = 784822

for param in PROBE_PARAMS:
    try:
        r = scraper.get(
            f'https://skillsmp.com/api/skills?limit=100&page=1&{param}=react',
            headers=HEADERS, timeout=15
        )
        data = r.json()
        skills = data.get('skills', [])
        total = data.get('pagination', {}).get('totalAll', base_total)
        print(f'  {param}=react: {len(skills)} results, totalAll={total}')
        if total < base_total * 0.5:  # significantly fewer = search is filtering
            SEARCH_PARAM = param
            print(f'  >> Found search param: {param} (total dropped {base_total} -> {total})')
            break
        elif len(skills) < base_count * 0.8 and skills:
            names = [s.get('name', '').lower() for s in skills]
            if any('react' in n for n in names):
                SEARCH_PARAM = param
                print(f'  >> Found search param: {param}')
                break
    except Exception as e:
        print(f'  {param}: error - {e}')
    time.sleep(0.5)

# Also test q= with different value to confirm
if SEARCH_PARAM == 'q' or (not SEARCH_PARAM):
    try:
        r2 = scraper.get('https://skillsmp.com/api/skills?limit=100&page=1&q=zzzyyyxxx', headers=HEADERS, timeout=15)
        d2 = r2.json()
        t2 = d2.get('pagination', {}).get('totalAll', -1)
        cnt2 = len(d2.get('skills', []))
        print(f'  q=zzzyyyxxx: {cnt2} results, totalAll={t2}')
        if t2 == 0 or cnt2 == 0:
            SEARCH_PARAM = 'q'
            print(f'  >> Confirmed: q= is the search param (returns 0 for nonsense)')
        elif t2 == base_total:
            print(f'  >> q= does NOT filter (ignores unknown param)')
            if SEARCH_PARAM == 'q':
                SEARCH_PARAM = None
    except Exception as e:
        print(f'  Confirm test error: {e}')

print(f'\nSearch param: {SEARCH_PARAM or "NOT FOUND"}')

# ── Step 2: Load already-installed skills ────────────────────────────────────
existing = set(os.listdir(BASE)) if os.path.exists(BASE) else set()
print(f'Already installed: {len(existing)} skills')

# ── Step 3: Fetch all skills ─────────────────────────────────────────────────
all_skills = {}  # id -> skill object

def fetch_page(url, retries=3):
    for attempt in range(retries):
        try:
            r = scraper.get(url, headers=HEADERS, timeout=30)
            return r.json()
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
    return {}

def fetch_with_param(param_name, param_value):
    results = {}
    for page in range(1, 14):
        url = f'https://skillsmp.com/api/skills?limit=100&page={page}&{param_name}={param_value}'
        data = fetch_page(url)
        skills = data.get('skills', [])
        if not skills:
            break
        for s in skills:
            sid = s.get('id', '') or s.get('name', '')
            if sid:
                results[sid] = s
        if not data.get('pagination', {}).get('hasNext'):
            break
        time.sleep(0.1)
    return results

def fetch_with_sort(sort_value):
    results = {}
    for page in range(1, 14):
        url = f'https://skillsmp.com/api/skills?limit=100&page={page}&sortBy={sort_value}'
        data = fetch_page(url)
        skills = data.get('skills', [])
        if not skills:
            break
        for s in skills:
            sid = s.get('id', '') or s.get('name', '')
            if sid:
                results[sid] = s
        if not data.get('pagination', {}).get('hasNext'):
            break
        time.sleep(0.1)
    return results

if SEARCH_PARAM:
    # All two-letter combos: aa-zz (676) + single letters/digits (36) = 712 queries
    chars = string.ascii_lowercase
    single = list(chars + string.digits)
    two_letter = [a + b for a, b in product(chars, chars)]
    # Also try three-letter for common prefixes
    all_queries = single + two_letter
    print(f'\n=== Fetching with ?{SEARCH_PARAM}=<prefix>: {len(all_queries)} queries ===')

    done = 0
    start = time.time()
    for q in all_queries:
        batch = fetch_with_param(SEARCH_PARAM, q)
        new_count = sum(1 for k in batch if k not in all_skills)
        all_skills.update(batch)
        done += 1
        if done % 100 == 0 or new_count > 0:
            elapsed = time.time() - start
            eta = (elapsed / done) * (len(all_queries) - done) if done > 0 else 0
            print(f'  [{done}/{len(all_queries)}] q={q!r}: +{new_count} | total={len(all_skills)} | ETA={eta/60:.1f}m')
        time.sleep(0.1)

else:
    # Fallback: sort-based strategy + category/tag enumeration
    print('\n=== Fallback: sort-based strategy ===')
    sort_options = ['recent', 'popular', 'stars', 'name', 'updated']
    for sort in sort_options:
        batch = fetch_with_sort(sort)
        new_count = sum(1 for k in batch if k not in all_skills)
        all_skills.update(batch)
        print(f'  sort={sort}: +{new_count} | total={len(all_skills)}')
        time.sleep(0.5)

    # Print sample skill to see available fields for further enumeration
    if all_skills:
        sample = next(iter(all_skills.values()))
        print(f'\nSample skill fields: {list(sample.keys())}')
        for field in ['category', 'categories', 'tag', 'tags', 'type', 'language', 'framework', 'author', 'org']:
            val = sample.get(field)
            if val:
                print(f'  {field}={val!r}')

print(f'\nTotal unique skills found: {len(all_skills)}')

# ── Step 4: GitHub content fetching ──────────────────────────────────────────
def github_url_to_raw(github_url, path='SKILL.md', branch='main'):
    github_url = github_url.rstrip('/')
    m = re.match(r'https://github\.com/([^/]+)/([^/]+)/tree/([^/]+)/(.*)', github_url)
    if m:
        owner, repo, br, subpath = m.groups()
        return f'https://raw.githubusercontent.com/{owner}/{repo}/{br}/{subpath}/{path}'
    m = re.match(r'https://github\.com/([^/]+)/([^/]+)$', github_url)
    if m:
        owner, repo = m.groups()
        return f'https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}'
    return None

def fetch_skill_content(skill):
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
    for alt in ['master', 'main']:
        if alt == branch:
            continue
        raw_url = github_url_to_raw(github_url, path, alt)
        if raw_url:
            try:
                r = requests.get(raw_url, timeout=10)
                if r.status_code == 200:
                    return r.text
            except Exception:
                pass
    return None

def create_skill(skill, content=None):
    name = skill.get('name', '').strip()
    if not name or len(name) < 2 or '/' in name or '\\' in name or ' ' in name:
        return False
    d = os.path.join(BASE, name)
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

# ── Step 5: Determine what needs processing ───────────────────────────────────
to_process = []
for sid, skill in all_skills.items():
    name = skill.get('name', '').strip()
    if not name:
        continue
    d = os.path.join(BASE, name)
    skill_file = os.path.join(d, 'SKILL.md')
    if not os.path.exists(d):
        to_process.append(('new', skill))
    elif os.path.exists(skill_file):
        with open(skill_file, encoding='utf-8', errors='ignore') as f:
            content = f.read()
        if ('Key Capabilities' in content and 'Best practice patterns' in content) or \
           (len(content) < 300 and skill.get('githubUrl')):
            to_process.append(('update', skill))

print(f'Skills to process: {len(to_process)}')

# ── Step 6: Parallel fetch + create ──────────────────────────────────────────
print(f'\n=== Processing {len(to_process)} skills (30 workers) ===')
created = updated = fallback = failed = 0

def process_one(item):
    kind, skill = item
    content = fetch_skill_content(skill)
    return kind, skill, content

with ThreadPoolExecutor(max_workers=30) as executor:
    futures = {executor.submit(process_one, item): item for item in to_process}
    done = 0
    for future in as_completed(futures):
        done += 1
        kind, skill, content = future.result()
        if create_skill(skill, content):
            if content:
                if kind == 'new':
                    created += 1
                else:
                    updated += 1
            else:
                fallback += 1
        else:
            failed += 1
        if done % 500 == 0:
            print(f'  {done}/{len(to_process)} | created={created} updated={updated} fallback={fallback} failed={failed}')

print(f'\n=== Done ===')
print(f'Created (real content): {created}')
print(f'Updated (real content): {updated}')
print(f'Created (fallback):     {fallback}')
print(f'Failed:                 {failed}')
print(f'Total skills on disk:   {len(os.listdir(BASE))}')
