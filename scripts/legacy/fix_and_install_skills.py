"""
fix_and_install_skills.py
Repairs malformed YAML frontmatter in all SKILL.md files from skills_backup
and installs them into .claude/skills/ so Claude Code can load them without crashing.

Root cause: description/other fields injected raw into YAML → unquoted colons,
emoji, special chars → Bun YAML parser assertion failure at ~11k files.

Fix: parse frontmatter → re-serialize with yaml.dump() (auto-quoting) → write clean file.
"""

import os
import re
import sys
import yaml
import shutil
import traceback
from concurrent.futures import ProcessPoolExecutor, as_completed

BACKUP  = r'C:\Users\Yaleena Yara\MAARS-Command\.claude\skills_backup'
TARGET  = r'C:\Users\Yaleena Yara\MAARS-Command\.claude\skills'
WORKERS = 8  # ProcessPool for CPU-bound YAML parsing

# ─── YAML helpers ────────────────────────────────────────────────────────────

FM_RE = re.compile(r'^---\s*\n(.*?)\n---\s*(\n|$)', re.DOTALL)

def _safe_str(v):
    """Coerce any value to a clean string, stripping surrounding quotes if already there."""
    if v is None:
        return ''
    s = str(v).strip()
    if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
        s = s[1:-1]
    return s


def extract_frontmatter(text):
    """
    Returns (fm_dict, body_str) or ({}, text) if no frontmatter.
    Tries yaml.safe_load first; falls back to a line-by-line key:value extractor.
    """
    m = FM_RE.match(text)
    if not m:
        return {}, text

    raw_fm = m.group(1)
    body   = text[m.end():]

    # Attempt 1: standard YAML parse
    try:
        fm = yaml.safe_load(raw_fm)
        if isinstance(fm, dict):
            return fm, body
    except yaml.YAMLError:
        pass

    # Attempt 2: line-by-line key: value extraction (handles most broken cases)
    fm = {}
    current_key = None
    list_items  = []

    for line in raw_fm.splitlines():
        # list item under current key
        if line.startswith('  - ') and current_key:
            list_items.append(line.strip()[2:])
            fm[current_key] = list_items
            continue
        # new key
        if ':' in line and not line.startswith(' '):
            if current_key and isinstance(fm.get(current_key), list):
                pass  # already stored
            current_key = None
            list_items  = []
            key, _, val = line.partition(':')
            key = key.strip()
            val = val.strip().strip('"\'')
            if key:
                current_key = key
                fm[key] = val

    return fm, body


def sanitize_fm(fm: dict, skill_name: str) -> dict:
    """
    Ensure required fields exist and all values are YAML-safe types.
    Coerces everything to str/list[str]/bool so yaml.dump() works cleanly.
    """
    out = {}

    # Required fields first (in display order)
    out['name']        = _safe_str(fm.get('name') or skill_name)
    out['description'] = _safe_str(fm.get('description') or f'{skill_name} skill')

    # Preserve optional known fields
    for key in ('category', 'risk', 'source', 'author', 'version',
                'date_added', 'id', 'homepage', 'license'):
        if key in fm:
            out[key] = _safe_str(fm[key])

    # Tags / tools → clean list of strings
    for key in ('tags', 'tools'):
        if key in fm:
            val = fm[key]
            if isinstance(val, list):
                out[key] = [_safe_str(v) for v in val if v is not None]
            elif val:
                out[key] = [_safe_str(val)]

    # Carry over any other fields we don't explicitly handle
    for key, val in fm.items():
        if key not in out:
            if isinstance(val, list):
                out[key] = [_safe_str(v) for v in val if v is not None]
            elif isinstance(val, bool):
                out[key] = val
            elif val is not None:
                out[key] = _safe_str(val)

    return out


def build_skill_md(fm: dict, body: str) -> str:
    """Serialize clean frontmatter + body."""
    # yaml.dump with allow_unicode=True so emoji/CJK pass through cleanly
    fm_yaml = yaml.dump(
        fm,
        allow_unicode=True,
        default_flow_style=False,
        sort_keys=False,
        width=10000,          # prevent line-wrapping inside values
    ).rstrip('\n')
    return f'---\n{fm_yaml}\n---\n{body}'


# ─── Per-skill worker ─────────────────────────────────────────────────────────

def process_skill(skill_name):
    src_dir  = os.path.join(BACKUP, skill_name)
    dst_dir  = os.path.join(TARGET, skill_name)
    src_file = os.path.join(src_dir, 'SKILL.md')

    if not os.path.exists(src_file):
        return ('no_md', skill_name)

    try:
        with open(src_file, encoding='utf-8', errors='ignore') as f:
            raw = f.read()

        fm, body = extract_frontmatter(raw)
        fm       = sanitize_fm(fm, skill_name)
        fixed    = build_skill_md(fm, body)

        # Validate the output parses cleanly before writing
        test_m = FM_RE.match(fixed)
        if test_m:
            yaml.safe_load(test_m.group(1))  # raises if still broken

        os.makedirs(dst_dir, exist_ok=True)
        with open(os.path.join(dst_dir, 'SKILL.md'), 'w', encoding='utf-8') as f:
            f.write(fixed)

        # Copy any other files in the skill directory (non-SKILL.md)
        for entry in os.listdir(src_dir):
            if entry == 'SKILL.md':
                continue
            s = os.path.join(src_dir, entry)
            d = os.path.join(dst_dir, entry)
            if os.path.isfile(s) and not os.path.exists(d):
                shutil.copy2(s, d)

        return ('ok', skill_name)

    except Exception as e:
        # Last-resort: write a minimal valid SKILL.md so the dir is present
        try:
            minimal_fm = {'name': skill_name, 'description': f'{skill_name} skill'}
            minimal    = build_skill_md(minimal_fm, f'\n# {skill_name}\n')
            os.makedirs(dst_dir, exist_ok=True)
            with open(os.path.join(dst_dir, 'SKILL.md'), 'w', encoding='utf-8') as f:
                f.write(minimal)
            return ('fallback', skill_name)
        except Exception as e2:
            return ('failed', f'{skill_name}: {e2}')


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    if not os.path.exists(BACKUP):
        print(f'ERROR: skills_backup not found at {BACKUP}')
        sys.exit(1)

    os.makedirs(TARGET, exist_ok=True)

    all_skills = sorted(os.listdir(BACKUP))
    total      = len(all_skills)
    print(f'=== Repairing & installing {total} skills ===')
    print(f'  Source : {BACKUP}')
    print(f'  Target : {TARGET}')
    print(f'  Workers: {WORKERS}')
    print()

    counts = {'ok': 0, 'fallback': 0, 'failed': 0, 'no_md': 0}
    done   = 0

    with ProcessPoolExecutor(max_workers=WORKERS) as pool:
        futures = {pool.submit(process_skill, name): name for name in all_skills}

        for future in as_completed(futures):
            status, info = future.result()
            counts[status] = counts.get(status, 0) + 1
            done += 1

            if done % 1000 == 0 or done == total:
                pct = done / total * 100
                print(
                    f'  {done}/{total} ({pct:.1f}%) | '
                    f'ok={counts["ok"]} fallback={counts["fallback"]} '
                    f'failed={counts["failed"]} no_md={counts["no_md"]}'
                )
                sys.stdout.flush()

            if status == 'failed':
                print(f'  FAILED: {info}')

    print()
    print('=== Done ===')
    print(f'  ok={counts["ok"]} | fallback={counts["fallback"]} | '
          f'failed={counts["failed"]} | no_md={counts["no_md"]}')
    print(f'  Total skills installed: {counts["ok"] + counts["fallback"]}')

    # Final verification: count installed
    installed = len([d for d in os.listdir(TARGET)
                     if os.path.isfile(os.path.join(TARGET, d, 'SKILL.md'))])
    print(f'  Verified on disk     : {installed}')


if __name__ == '__main__':
    main()
