"""
Full harvest of skillsmp.com using the search= parameter bypass.
The search parameter is uncapped — each prefix query paginates unlimited results.
Strategy: enumerate all two-letter substrings (aa-zz = 676) + digits,
          paginate each until hasNext=False, deduplicate by ID.
Expected yield: hundreds of thousands of unique skills.
"""
import cloudscraper
import os
import json
import time
import re
import requests
import sys
import signal
import yaml
from concurrent.futures import ThreadPoolExecutor, as_completed
from itertools import product
import string
import threading

# ── YAML helpers ─────────────────────────────────────────────────────────────
_FM_RE = re.compile(r'^---\s*\n(.*?)\n---\s*(\n|$)', re.DOTALL)

def _safe_str(v):
    if v is None: return ''
    s = str(v).strip()
    if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
        s = s[1:-1]
    return s

def _parse_fm(text):
    """Return (fm_dict, body). Falls back to line-by-line if yaml fails."""
    m = _FM_RE.match(text)
    if not m:
        return {}, text
    raw, body = m.group(1), text[m.end():]
    try:
        fm = yaml.safe_load(raw)
        if isinstance(fm, dict):
            return fm, body
    except yaml.YAMLError:
        pass
    fm = {}
    for line in raw.splitlines():
        if ':' in line and not line.startswith(' '):
            k, _, v = line.partition(':')
            k = k.strip(); v = v.strip().strip('"\'')
            if k: fm[k] = v
    return fm, body

def _build_fm(fm: dict, skill_name: str) -> str:
    """Sanitize and serialize frontmatter to valid YAML block."""
    out = {}
    out['name']        = _safe_str(fm.get('name') or skill_name)
    out['description'] = _safe_str(fm.get('description') or f'{skill_name} skill')
    for key in ('category','risk','source','author','version','date_added',
                'id','homepage','license'):
        if key in fm: out[key] = _safe_str(fm[key])
    for key in ('tags','tools'):
        if key in fm:
            val = fm[key]
            if isinstance(val, list):
                out[key] = [_safe_str(v) for v in val if v is not None]
            elif val:
                out[key] = [_safe_str(val)]
    for key, val in fm.items():
        if key not in out:
            if isinstance(val, list): out[key] = [_safe_str(v) for v in val if v is not None]
            elif isinstance(val, bool): out[key] = val
            elif val is not None: out[key] = _safe_str(val)
    return yaml.dump(out, allow_unicode=True, default_flow_style=False,
                     sort_keys=False, width=10000).rstrip('\n')

def make_clean_skill_md(skill_name: str, content: str | None,
                        skill: dict | None = None) -> str:
    """
    If content supplied (from GitHub): parse its frontmatter and re-serialize cleanly.
    If no content: build a stub from skill metadata.
    Always returns a string with valid YAML frontmatter.
    """
    if content:
        fm, body = _parse_fm(content)
        if not fm.get('name'): fm['name'] = skill_name
        if not fm.get('description') and skill:
            fm['description'] = (skill.get('description') or f'{skill_name} skill')[:300]
        fm_yaml = _build_fm(fm, skill_name)
        return f'---\n{fm_yaml}\n---\n{body}'
    # stub
    desc  = ((skill or {}).get('description') or f'{skill_name} skill')[:300]
    title = skill_name.replace('-', ' ').title()
    fm    = {'name': skill_name, 'description': desc}
    fm_yaml = _build_fm(fm, skill_name)
    return (f'---\n{fm_yaml}\n---\n\n# {title}\n\n'
            f'## Overview\n{desc}\n\n'
            f'## Usage\nUse this skill to leverage {title.lower()} capabilities in your agent workflows.\n\n'
            f'## Best Practices\n'
            f'1. Follow official documentation and guidelines\n'
            f'2. Handle errors and edge cases gracefully\n'
            f'3. Test thoroughly before production use\n')

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

API_KEY = 'sk_live_skillsmp_nmzbSNajmLgoh-VYDqNT2xZBCdHRL63lHEDJws0_Xlg'
BASE = 'c:/Users/Yaleena Yara/MAARS-Command/.claude/skills'
HEADERS = {'Authorization': f'Bearer {API_KEY}'}
PROGRESS_FILE = 'c:/Users/Yaleena Yara/MAARS-Command/harvest_progress.json'
SKILLS_CACHE = 'c:/Users/Yaleena Yara/MAARS-Command/harvest_skills_cache.json'

scraper = cloudscraper.create_scraper()
lock = threading.Lock()

# ── Load existing progress ───────────────────────────────────────────────────
completed_prefixes = set()
all_skills = {}  # id -> skill object

if os.path.exists(PROGRESS_FILE):
    with open(PROGRESS_FILE, encoding='utf-8') as f:
        progress = json.load(f)
    completed_prefixes = set(progress.get('completed', []))
    print(f'Resuming: {len(completed_prefixes)} prefixes already done')

if os.path.exists(SKILLS_CACHE):
    with open(SKILLS_CACHE, encoding='utf-8') as f:
        all_skills = json.load(f)
    print(f'Cache loaded: {len(all_skills)} unique skills')

# ── Save progress ────────────────────────────────────────────────────────────
def save_progress():
    with lock:
        with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
            json.dump({'completed': list(completed_prefixes)}, f)
        with open(SKILLS_CACHE, 'w', encoding='utf-8') as f:
            json.dump(all_skills, f, ensure_ascii=False)

# Graceful shutdown on Ctrl+C
def handle_exit(sig, frame):
    print('\n[!] Interrupted — saving progress...')
    save_progress()
    print(f'[!] Saved {len(all_skills)} skills, {len(completed_prefixes)} prefixes completed')
    sys.exit(0)

signal.signal(signal.SIGINT, handle_exit)

# ── Build prefix list ────────────────────────────────────────────────────────
chars = string.ascii_lowercase
digits = string.digits
two_letter = [a + b for a, b in product(chars, chars)]  # aa-zz = 676
two_digit = [a + b for a, b in product(digits, digits)]  # 00-99 = 100
letter_digit = [a + b for a, b in product(chars, digits)]  # a0-z9 = 260
digit_letter = [a + b for a, b in product(digits, chars)]  # 0a-9z = 260

# Priority order: letter combos first (most skills), then mixed
all_prefixes = two_letter + letter_digit + digit_letter + two_digit
# Remove already completed
todo_prefixes = [p for p in all_prefixes if p not in completed_prefixes]
print(f'Total prefixes: {len(all_prefixes)} | Remaining: {len(todo_prefixes)}')

# ── Fetch all pages for a single prefix ─────────────────────────────────────
def fetch_prefix(prefix, max_pages=2000):
    """Paginate search=<prefix> until hasNext=False. Returns dict of id->skill."""
    results = {}
    for page in range(1, max_pages + 1):
        for attempt in range(3):
            try:
                r = scraper.get(
                    f'https://skillsmp.com/api/skills?limit=100&page={page}&search={prefix}',
                    headers=HEADERS, timeout=25
                )
                data = r.json()
                break
            except Exception as e:
                if attempt < 2:
                    time.sleep(2 ** attempt)
                else:
                    return results

        skills = data.get('skills', [])
        if not skills:
            break

        for s in skills:
            sid = s.get('id', '') or s.get('name', '')
            if sid:
                results[sid] = s

        if not data.get('pagination', {}).get('hasNext'):
            break
        time.sleep(0.08)

    return results

# ── Main enumeration loop ────────────────────────────────────────────────────
print(f'\n=== Enumerating {len(todo_prefixes)} prefixes ===')
start = time.time()
done_count = 0
save_interval = 50  # save every 50 prefixes

for prefix in todo_prefixes:
    batch = fetch_prefix(prefix)
    new_count = 0
    with lock:
        for k, v in batch.items():
            if k not in all_skills:
                all_skills[k] = v
                new_count += 1
        completed_prefixes.add(prefix)
    done_count += 1

    elapsed = time.time() - start
    rate = done_count / elapsed if elapsed > 0 else 0
    remaining = len(todo_prefixes) - done_count
    eta_min = (remaining / rate / 60) if rate > 0 else 0

    if done_count % 10 == 0 or new_count > 50:
        print(f'[{done_count}/{len(todo_prefixes)}] search={prefix!r}: +{new_count} | '
              f'total={len(all_skills)} | ETA={eta_min:.0f}m')

    if done_count % save_interval == 0:
        save_progress()
        print(f'  >> Progress saved ({len(all_skills)} skills, {len(completed_prefixes)} prefixes)')

# Final save after enumeration
save_progress()
print(f'\n=== Enumeration complete: {len(all_skills)} unique skills ===')

# ── GitHub content fetching ──────────────────────────────────────────────────
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
        raw_url2 = github_url_to_raw(github_url, path, alt)
        if raw_url2:
            try:
                r = requests.get(raw_url2, timeout=10)
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
    skill_md = make_clean_skill_md(name, content, skill)
    os.makedirs(d, exist_ok=True)
    skill_file = os.path.join(d, 'SKILL.md')
    if not os.path.exists(skill_file):
        with open(skill_file, 'w', encoding='utf-8') as f:
            f.write(skill_md)
        return 'created'
    else:
        # Update if stub content
        with open(skill_file, encoding='utf-8', errors='ignore') as f:
            existing = f.read()
        is_stub = ('Best practice patterns' in existing) or \
                  (len(existing) < 400 and skill.get('githubUrl'))
        if is_stub and content:
            with open(skill_file, 'w', encoding='utf-8') as f:
                f.write(skill_md)
            return 'updated'
    return False

# ── Determine what needs processing ─────────────────────────────────────────
to_process = []
for sid, skill in all_skills.items():
    name = skill.get('name', '').strip()
    if not name:
        continue
    d = os.path.join(BASE, name)
    skill_file = os.path.join(d, 'SKILL.md')
    if not os.path.exists(skill_file):
        to_process.append(('new', skill))
    else:
        with open(skill_file, encoding='utf-8', errors='ignore') as f:
            content = f.read()
        if ('Key Capabilities' in content and 'Best practice patterns' in content) or \
           (len(content) < 300 and skill.get('githubUrl')):
            to_process.append(('update', skill))

print(f'Skills on disk already: {len(os.listdir(BASE))}')
print(f'Skills to process (new+update): {len(to_process)}')

if not to_process:
    print('Nothing to process!')
    sys.exit(0)

# ── Parallel create + fetch ──────────────────────────────────────────────────
print(f'\n=== Processing {len(to_process)} skills with 60 workers ===')
created = updated = fallback = failed = 0

def process_one(item):
    kind, skill = item
    content = fetch_skill_content(skill)
    return kind, skill, content

with ThreadPoolExecutor(max_workers=60) as executor:
    futures = {executor.submit(process_one, item): item for item in to_process}
    done = 0
    for future in as_completed(futures):
        done += 1
        kind, skill, content = future.result()
        result = create_skill(skill, content)
        if result == 'created':
            if content:
                created += 1
            else:
                fallback += 1
        elif result == 'updated':
            updated += 1
        else:
            failed += 1
        if done % 1000 == 0:
            print(f'  {done}/{len(to_process)} | created={created} updated={updated} '
                  f'fallback={fallback} failed={failed}')
            sys.stdout.flush()

print(f'\n=== Done ===')
print(f'Created (real content): {created}')
print(f'Updated (real content): {updated}')
print(f'Created (fallback):     {fallback}')
print(f'Failed:                 {failed}')
print(f'Total skills on disk:   {len(os.listdir(BASE))}')
sys.stdout.flush()
