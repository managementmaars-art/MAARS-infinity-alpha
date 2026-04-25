"""
Fix SKILL.md files from .claude/skills_backup/ and write clean versions to .claude/skills/.

Fixes applied:
- Reconstructs YAML frontmatter if missing or unparseable.
- Strips 'hooks' and other invalid Claude Code skill frontmatter fields
  (hooks live in settings.json, not in skill frontmatter).
- Keeps only the fields Claude Code actually reads from skill frontmatter:
  name, description, license, allowed-tools.
- Falls back to the folder name for `name` and to the first body paragraph
  (or a default) for `description` when those are missing or garbage.
- Ensures description is a single line within 1024 chars (Claude Code's cap).
- Copies all other files in the skill directory verbatim.
- Emits a summary of what was fixed.
"""
from __future__ import annotations

import os
import re
import shutil
import sys
import traceback
from collections import Counter
from pathlib import Path

import yaml

SRC = Path(r"c:\Users\Yaleena Yara\MAARS-Command\.claude\skills_backup")
DST = Path(r"c:\Users\Yaleena Yara\MAARS-Command\skills")

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*(\n|$)", re.DOTALL)

# Claude Code's skill-frontmatter whitelist. Everything else (including `hooks`)
# is stripped from the final file.
KEEP_FIELDS = {"name", "description", "license", "allowed-tools"}

# Max chars Claude Code allows for each field.
NAME_MAX = 64
DESC_MAX = 1024

# Only letters, digits, hyphens.
NAME_ALLOWED = re.compile(r"[^a-z0-9-]+")

stats = Counter()


def safe_name(raw: str) -> str:
    """Convert an arbitrary folder name into a valid Claude Code skill name."""
    s = raw.strip().lower()
    s = s.replace(" ", "-").replace("_", "-")
    s = NAME_ALLOWED.sub("-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    if not s:
        s = "unnamed-skill"
    return s[:NAME_MAX]


def clean_description(raw: str) -> str:
    """Collapse whitespace/newlines and trim to DESC_MAX."""
    if raw is None:
        return ""
    s = str(raw).replace("\r", " ").replace("\n", " ")
    s = re.sub(r"\s+", " ", s).strip()
    if len(s) > DESC_MAX:
        s = s[: DESC_MAX - 1].rstrip() + "…"
    return s


def extract_frontmatter(text: str):
    """Return (frontmatter_str, body_str)."""
    if not text.startswith("---"):
        return None, text
    m = FRONTMATTER_RE.match(text)
    if not m:
        return None, text
    return m.group(1), text[m.end():]


def parse_yaml_resilient(fm: str):
    """Try yaml.safe_load; on failure, try progressive repair strategies.

    Returns (dict_or_None, parse_status_string).
    """
    if not fm or not fm.strip():
        return None, "empty"
    try:
        data = yaml.safe_load(fm)
        if isinstance(data, dict):
            return data, "clean"
        if data is None:
            return None, "empty"
        return None, "not_a_dict"
    except Exception:
        pass

    # Strategy 1: strip trailing "..." or stray control chars, collapse tabs
    trial = fm.replace("\t", "  ")
    trial = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", trial)
    try:
        data = yaml.safe_load(trial)
        if isinstance(data, dict):
            return data, "repaired_controlchars"
    except Exception:
        pass

    # Strategy 2: line-by-line, keep only lines of form `key: value` where
    # value is either a simple scalar, a quoted string, or the start of a list.
    kept: list[str] = []
    cur_key: str | None = None
    for line in fm.splitlines():
        if not line.strip():
            kept.append("")
            continue
        if line.startswith(" ") or line.startswith("\t"):
            # Only keep indented lines if they're list items under a current key.
            if cur_key and line.lstrip().startswith("- "):
                kept.append(line)
            continue
        m = re.match(r"^([A-Za-z_][\w-]*)\s*:\s*(.*)$", line)
        if not m:
            continue
        key, val = m.group(1), m.group(2)
        cur_key = key
        if val == "":
            kept.append(f"{key}:")
        else:
            # Quote the value defensively.
            safe_val = val.strip()
            if safe_val.startswith(("'", '"', "[", "{")) or safe_val in {
                "true", "false", "null", "yes", "no"
            } or re.match(r"^-?\d", safe_val):
                kept.append(f"{key}: {safe_val}")
            else:
                escaped = safe_val.replace('"', '\\"')
                kept.append(f'{key}: "{escaped}"')
    rebuilt = "\n".join(kept)
    try:
        data = yaml.safe_load(rebuilt)
        if isinstance(data, dict):
            return data, "repaired_line_by_line"
    except Exception:
        pass

    # Strategy 3: last-ditch regex extraction of `key: value` pairs only.
    out: dict = {}
    for m in re.finditer(r"(?m)^([A-Za-z_][\w-]*)\s*:\s*(.*)$", fm):
        k = m.group(1)
        v = m.group(2).strip().strip('"').strip("'")
        if k in {"name", "description", "license", "allowed-tools"} and v:
            out[k] = v
    if out:
        return out, "regex_extracted"
    return None, "unparseable"


def first_body_paragraph(body: str) -> str:
    """Return the first non-heading, non-empty paragraph of the body."""
    if not body:
        return ""
    for para in re.split(r"\n\s*\n", body.strip()):
        para = para.strip()
        if not para:
            continue
        if para.startswith("#"):
            # Skip markdown headings
            continue
        if para.startswith(("```", "|", "- ", "* ")):
            continue
        return para
    # Fallback: first non-empty line that isn't a heading
    for line in body.splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            return line
    return ""


def fix_one(skill_dir: Path) -> tuple[bool, str]:
    """Process one skill directory. Returns (ok, note)."""
    src_md = skill_dir / "SKILL.md"
    if not src_md.is_file():
        return False, "no_SKILL.md"

    try:
        text = src_md.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        return False, f"read_error:{type(e).__name__}"

    folder_name = skill_dir.name
    safe_folder_name = safe_name(folder_name)

    fm, body = extract_frontmatter(text)
    parse_status = "no_frontmatter"
    data: dict = {}
    if fm is not None:
        parsed, parse_status = parse_yaml_resilient(fm)
        if isinstance(parsed, dict):
            data = parsed

    # --- Name ---
    name_raw = data.get("name") or folder_name
    if not isinstance(name_raw, str):
        name_raw = str(name_raw)
    name_val = safe_name(name_raw)
    if name_val != name_raw.strip().lower().replace("_", "-"):
        stats["name_normalized"] += 1

    # --- Description ---
    desc_raw = data.get("description")
    desc_val = clean_description(desc_raw) if desc_raw else ""
    if not desc_val:
        # Fallback: first paragraph of body
        desc_val = clean_description(first_body_paragraph(body))
        stats["description_from_body"] += 1
    if not desc_val:
        desc_val = f"Skill: {name_val}"
        stats["description_defaulted"] += 1

    # --- Allowed tools (optional) ---
    allowed = data.get("allowed-tools") or data.get("allowed_tools")
    allowed_list: list[str] | None = None
    if isinstance(allowed, list):
        allowed_list = [str(x) for x in allowed if x]
    elif isinstance(allowed, str) and allowed.strip():
        allowed_list = [s.strip() for s in allowed.split(",") if s.strip()]

    # --- License (optional) ---
    license_val = data.get("license")
    if license_val is not None and not isinstance(license_val, str):
        license_val = str(license_val)

    # --- Strip hooks and other non-Claude-Code fields ---
    stripped = [k for k in data.keys() if k not in KEEP_FIELDS]
    if "hooks" in data:
        stats["hooks_stripped"] += 1
    if stripped:
        stats["fields_stripped"] += 1

    # --- Rebuild YAML frontmatter deterministically ---
    yaml_doc: dict = {"name": name_val, "description": desc_val}
    if allowed_list:
        yaml_doc["allowed-tools"] = allowed_list
    if license_val:
        yaml_doc["license"] = license_val

    fm_out = yaml.safe_dump(
        yaml_doc,
        default_flow_style=False,
        allow_unicode=True,
        sort_keys=False,
        width=4096,
    ).rstrip("\n")

    # --- Rebuild body ---
    body_clean = body.lstrip("\n")
    if not body_clean.strip():
        body_clean = f"# {name_val}\n\n{desc_val}\n"
    new_text = f"---\n{fm_out}\n---\n\n{body_clean}"
    if not new_text.endswith("\n"):
        new_text += "\n"

    # --- Write to destination ---
    # Destination folder uses safe name so duplicates collide; handle by suffix.
    dst_dir = DST / safe_folder_name
    if dst_dir.exists():
        # Collision - append short hash of original path
        import hashlib
        h = hashlib.sha1(folder_name.encode("utf-8")).hexdigest()[:6]
        dst_dir = DST / f"{safe_folder_name}-{h}"
        stats["name_collision_suffix"] += 1
    dst_dir.mkdir(parents=True, exist_ok=True)

    # Copy all sibling files/dirs from source (excluding SKILL.md which we rewrote).
    for child in skill_dir.iterdir():
        if child.name == "SKILL.md":
            continue
        target = dst_dir / child.name
        try:
            if child.is_dir():
                shutil.copytree(child, target, dirs_exist_ok=True)
            else:
                shutil.copy2(child, target)
        except Exception:
            stats["sibling_copy_fail"] += 1

    (dst_dir / "SKILL.md").write_text(new_text, encoding="utf-8")

    stats[f"parse_{parse_status}"] += 1
    stats["ok"] += 1
    return True, parse_status


def main():
    if not SRC.is_dir():
        print(f"Source not found: {SRC}", file=sys.stderr)
        sys.exit(1)
    DST.mkdir(parents=True, exist_ok=True)

    dirs = [p for p in SRC.iterdir() if p.is_dir()]
    total = len(dirs)
    print(f"Found {total} skill directories", flush=True)

    for i, d in enumerate(dirs, 1):
        if i % 2000 == 0 or i == total:
            done = stats.get("ok", 0)
            print(
                f"  {i}/{total}  ok={done}  fail={i - done}  hooks_stripped={stats.get('hooks_stripped', 0)}",
                flush=True,
            )
        try:
            ok, note = fix_one(d)
            if not ok:
                stats[f"fail_{note}"] += 1
        except Exception as e:
            stats["exception"] += 1
            stats[f"exc_{type(e).__name__}"] += 1
            if stats["exception"] <= 5:
                print(f"EXC on {d.name}: {e}", flush=True)
                traceback.print_exc()

    print("\n=== SUMMARY ===")
    for k, v in stats.most_common():
        print(f"  {v:>7}  {k}")


if __name__ == "__main__":
    main()
