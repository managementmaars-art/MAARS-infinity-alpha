#!/usr/bin/env python3
"""
Fetch companion files (references/, scripts/, docs/, templates/, examples/)
for installed skills that reference them but don't have them locally.
Uses GitHub raw URLs constructed from cached githubUrl values.
"""
import os, re, json, time, sys
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

SKILLS_DIR = r'C:\Users\Yaleena Yara\MAARS-Command\.claude\skills'
CACHE_FILE = r'C:\Users\Yaleena Yara\MAARS-Command\harvest_skills_cache.json'
LOG_FILE   = r'C:\Users\Yaleena Yara\MAARS-Command\companion_fetch.log'

REF_PATTERN = re.compile(
    r'(?:references|scripts|docs|templates|examples)/[\w\-\.]+\.(?:md|py|sh|json|yaml|yml|txt)',
    re.IGNORECASE
)

def make_session():
    s = requests.Session()
    retry = Retry(total=3, backoff_factor=0.5, status_forcelist=[429, 500, 502, 503, 504])
    s.mount('https://', HTTPAdapter(max_retries=retry))
    s.headers['User-Agent'] = 'Mozilla/5.0 (companion-fetcher)'
    return s

def github_url_to_raw(github_url: str, rel_path: str) -> list[str]:
    """Convert github tree URL + relative path to candidate raw URLs."""
    # https://github.com/user/repo/tree/branch/path/to/skill
    m = re.match(r'https://github\.com/([^/]+)/([^/]+)/tree/([^/]+)/(.*)', github_url)
    if not m:
        # https://github.com/user/repo
        m2 = re.match(r'https://github\.com/([^/]+)/([^/]+)/?$', github_url)
        if m2:
            user, repo = m2.group(1), m2.group(2)
            for branch in ('main', 'master'):
                yield f'https://raw.githubusercontent.com/{user}/{repo}/{branch}/{rel_path}'
        return
    user, repo, branch, base_path = m.groups()
    base_path = base_path.rstrip('/')
    yield f'https://raw.githubusercontent.com/{user}/{repo}/{branch}/{base_path}/{rel_path}'
    # Also try without the skill subpath (in case it's at repo root)
    parent = '/'.join(base_path.split('/')[:-1])
    if parent:
        yield f'https://raw.githubusercontent.com/{user}/{repo}/{branch}/{parent}/{rel_path}'

def fetch_raw(session, url: str, timeout=12) -> str | None:
    try:
        r = session.get(url, timeout=timeout)
        if r.status_code == 200 and len(r.text) > 10:
            return r.text
    except Exception:
        pass
    return None

def get_missing_refs(skill_name: str) -> list[str]:
    skill_dir = os.path.join(SKILLS_DIR, skill_name)
    skill_md  = os.path.join(skill_dir, 'SKILL.md')
    if not os.path.exists(skill_md):
        return []
    raw  = open(skill_md, encoding='utf-8', errors='ignore').read()
    refs = list(set(REF_PATTERN.findall(raw)))
    return [r for r in refs if not os.path.exists(os.path.join(skill_dir, r))]

def process_skill(args):
    skill_name, github_url, session = args
    missing = get_missing_refs(skill_name)
    if not missing:
        return skill_name, 0, 0

    fetched = 0
    failed  = 0
    skill_dir = os.path.join(SKILLS_DIR, skill_name)

    for rel_path in missing:
        content = None
        if github_url:
            for raw_url in github_url_to_raw(github_url, rel_path):
                content = fetch_raw(session, raw_url)
                if content:
                    break

        if content:
            dest = os.path.join(skill_dir, rel_path)
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            open(dest, 'w', encoding='utf-8', errors='replace').write(content)
            fetched += 1
        else:
            failed += 1

    return skill_name, fetched, failed

def main():
    log = open(LOG_FILE, 'w', encoding='utf-8')
    def log_print(msg):
        print(msg, flush=True)
        log.write(msg + '\n')
        log.flush()

    # Build name → github_url map from cache
    log_print('Loading cache...')
    cache = json.load(open(CACHE_FILE, encoding='utf-8'))
    url_map = {}
    for s in cache.values():
        name = (s.get('name') or '').strip()
        url  = s.get('githubUrl') or s.get('github_url') or s.get('url') or ''
        if name and url:
            url_map[name] = url
    log_print(f'Cache loaded: {len(cache)} entries, {len(url_map)} with github URLs')

    # Find all skills with missing refs
    log_print('Scanning installed skills for missing companion files...')
    installed = os.listdir(SKILLS_DIR)
    tasks = []
    for skill_name in installed:
        missing = get_missing_refs(skill_name)
        if missing:
            github_url = url_map.get(skill_name, '')
            tasks.append((skill_name, github_url, None))  # session added per-thread

    log_print(f'Skills needing companion files: {len(tasks)}')
    log_print(f'Skills without github URL in cache: {sum(1 for t in tasks if not t[1])}')

    total_fetched = 0
    total_failed  = 0
    total_done    = 0
    checkpoint    = 500

    sessions = [make_session() for _ in range(40)]

    def make_task(i, skill_name, github_url):
        return (skill_name, github_url, sessions[i % len(sessions)])

    tasks_with_sessions = [make_task(i, t[0], t[1]) for i, t in enumerate(tasks)]

    log_print(f'Starting fetch with 40 workers...')
    with ThreadPoolExecutor(max_workers=40) as ex:
        futures = {ex.submit(process_skill, t): t[0] for t in tasks_with_sessions}
        for fut in as_completed(futures):
            skill_name, fetched, failed = fut.result()
            total_fetched += fetched
            total_failed  += failed
            total_done    += 1
            if total_done % checkpoint == 0:
                log_print(
                    f'  {total_done}/{len(tasks)} | fetched={total_fetched} failed={total_failed}'
                )

    log_print(f'\n=== Done ===')
    log_print(f'Skills processed: {total_done}')
    log_print(f'Files fetched:    {total_fetched}')
    log_print(f'Files not found:  {total_failed}')

    # Final count of extra files
    extra = sum(
        len(os.listdir(os.path.join(SKILLS_DIR, n))) - 1  # minus SKILL.md
        for n in os.listdir(SKILLS_DIR)
        if os.path.isdir(os.path.join(SKILLS_DIR, n))
    )
    log_print(f'Total companion files on disk: {extra}')
    log.close()

if __name__ == '__main__':
    main()
