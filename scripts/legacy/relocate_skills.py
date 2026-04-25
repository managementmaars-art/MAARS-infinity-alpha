"""
Merge top-level skills/ into .claude/skills/:
- For each dir in skills/: if same name exists in .claude/skills/, skip (keep existing).
- Otherwise move the dir into .claude/skills/.
- After the merge, remove the now-empty skills/ directory (only if it's fully empty).

Move semantics: uses os.rename (fast, same-filesystem). Falls back to copy+delete
on cross-device errors.
"""
from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path
from collections import Counter

SRC = Path(r"c:\Users\Yaleena Yara\MAARS-Command\skills")
DST = Path(r"c:\Users\Yaleena Yara\MAARS-Command\.claude\skills")

stats = Counter()


def move_dir(src: Path, dst: Path) -> str:
    try:
        os.rename(src, dst)
        return "renamed"
    except OSError:
        pass
    # Fallback: recursive copy then remove source
    try:
        shutil.copytree(src, dst)
        shutil.rmtree(src)
        return "copied"
    except Exception as e:
        return f"error:{type(e).__name__}"


def main():
    if not SRC.is_dir():
        print(f"Source not found: {SRC}")
        return
    DST.mkdir(parents=True, exist_ok=True)

    entries = list(SRC.iterdir())
    total = len(entries)
    print(f"Moving {total} entries from {SRC} -> {DST}", flush=True)

    for i, src_entry in enumerate(entries, 1):
        if i % 5000 == 0:
            print(f"  {i}/{total}", flush=True)
        if not src_entry.is_dir():
            stats["skipped_nondir"] += 1
            continue
        dst_entry = DST / src_entry.name
        if dst_entry.exists():
            # Prefer existing .claude/skills/ version (might be curated)
            stats["skipped_existing"] += 1
            continue
        result = move_dir(src_entry, dst_entry)
        stats[result] += 1

    print("\n=== MERGE SUMMARY ===")
    for k, v in stats.most_common():
        print(f"  {v:>7}  {k}")

    # Remove top-level skills/ if now empty
    remaining = list(SRC.iterdir()) if SRC.exists() else []
    if not remaining:
        try:
            SRC.rmdir()
            print(f"\nRemoved empty {SRC}")
        except Exception as e:
            print(f"\nCould not remove {SRC}: {e}")
    else:
        print(f"\n{SRC} still has {len(remaining)} entries (left in place).")

    final_count = sum(1 for p in DST.iterdir() if p.is_dir())
    print(f"Final skills in {DST}: {final_count}")


if __name__ == "__main__":
    main()
