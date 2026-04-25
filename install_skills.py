"""
Install all skills from skills-top-9788.pdf.

Strategy:
- Parse `npx skills add <repo> --skill <name>` lines from the PDF.
- Dedupe (by skill name — we only need one copy of `skill-creator` etc.).
- Skip skills already present at .claude/skills/<name>.
- Run N installs in parallel (subprocess pool) with per-command timeout.
- Log success/failure to install_log.jsonl for post-hoc review.

This is an idempotent, resumable script — failures don't block progress.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

try:
    import pypdf
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "pypdf"], check=False)
    import pypdf

ROOT = Path(r"c:\Users\Yaleena Yara\MAARS-Command")
PDF = Path(r"c:\Users\Yaleena Yara\Desktop\skills-export\skills-top-9788.pdf")
SKILLS_DIR = ROOT / ".claude" / "skills"
LOG = ROOT / "install_log.jsonl"
CMD_FILE = ROOT / "install_commands.txt"

CMD_RE = re.compile(
    r"npx skills add (https://github\.com/[^\s]+)\s+--skill\s+([^\s]+)"
)
PARALLEL = 20
TIMEOUT = 60  # seconds per install


def extract_commands(pdf_path: Path) -> list[tuple[str, str]]:
    reader = pypdf.PdfReader(str(pdf_path))
    cmds: list[tuple[str, str]] = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        for m in CMD_RE.finditer(text):
            cmds.append((m.group(1), m.group(2)))
        if (i + 1) % 10 == 0:
            print(f"  parsed page {i + 1}/{len(reader.pages)} ({len(cmds)} cmds so far)", flush=True)
    return cmds


def dedupe_and_filter(cmds: list[tuple[str, str]]) -> list[tuple[str, str]]:
    """Dedupe by skill name; skip any skill already installed."""
    existing = {p.name.lower() for p in SKILLS_DIR.iterdir() if p.is_dir()} if SKILLS_DIR.exists() else set()
    seen: set[str] = set()
    out: list[tuple[str, str]] = []
    for repo, skill in cmds:
        key = skill.lower()
        if key in seen or key in existing:
            continue
        seen.add(key)
        out.append((repo, skill))
    return out


def run_one(repo: str, skill: str) -> dict:
    t0 = time.time()
    try:
        r = subprocess.run(
            ["npx", "-y", "skills", "add", repo, "--skill", skill, "--yes"],
            cwd=str(ROOT),
            capture_output=True,
            timeout=TIMEOUT,
            text=True,
        )
        ok = r.returncode == 0
        return {
            "skill": skill,
            "repo": repo,
            "ok": ok,
            "code": r.returncode,
            "stderr": r.stderr[-400:] if not ok else "",
            "dt": round(time.time() - t0, 2),
        }
    except subprocess.TimeoutExpired:
        return {"skill": skill, "repo": repo, "ok": False, "code": -1, "stderr": "timeout", "dt": TIMEOUT}
    except Exception as e:
        return {"skill": skill, "repo": repo, "ok": False, "code": -2, "stderr": f"{type(e).__name__}: {e}"[:400], "dt": round(time.time() - t0, 2)}


def main():
    if not PDF.exists():
        print(f"PDF not found: {PDF}", file=sys.stderr)
        sys.exit(1)

    print("Parsing PDF...", flush=True)
    cmds = extract_commands(PDF)
    print(f"  raw commands: {len(cmds)}", flush=True)

    filtered = dedupe_and_filter(cmds)
    print(f"  after dedupe + skip-existing: {len(filtered)}", flush=True)

    CMD_FILE.write_text(
        "\n".join(f"{r}\t{s}" for r, s in filtered), encoding="utf-8"
    )
    print(f"  commands saved to {CMD_FILE}", flush=True)

    if not filtered:
        print("Nothing to install.", flush=True)
        return

    ok_count = 0
    fail_count = 0
    t_start = time.time()

    with LOG.open("w", encoding="utf-8") as fh, ThreadPoolExecutor(max_workers=PARALLEL) as pool:
        futures = {pool.submit(run_one, repo, skill): (repo, skill) for repo, skill in filtered}
        for i, fut in enumerate(as_completed(futures), 1):
            res = fut.result()
            fh.write(json.dumps(res) + "\n")
            if res["ok"]:
                ok_count += 1
            else:
                fail_count += 1
            if i % 50 == 0 or i == len(filtered):
                elapsed = time.time() - t_start
                rate = i / elapsed if elapsed else 0
                eta = (len(filtered) - i) / rate if rate else 0
                print(
                    f"  {i}/{len(filtered)}  ok={ok_count}  fail={fail_count}  "
                    f"rate={rate:.1f}/s  eta={eta/60:.1f}min",
                    flush=True,
                )

    print(f"\nDONE: {ok_count} installed, {fail_count} failed. Log: {LOG}", flush=True)


if __name__ == "__main__":
    main()
