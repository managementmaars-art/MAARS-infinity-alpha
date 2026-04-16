#!/usr/bin/env python3
"""Index extracted text into the vault's FTS5 search database.

Usage:
    python3 vault_index.py <extracted_file.md> "<title>"
    python3 vault_index.py --init              # create empty DB
    python3 vault_index.py --rebuild           # reindex all .extracted.md files
    python3 vault_index.py --count             # print document count
"""

import sqlite3
import sys
from pathlib import Path
from datetime import datetime

DB = Path("vault/vault.db")


def init_db():
    DB.parent.mkdir(exist_ok=True)
    c = sqlite3.connect(str(DB))
    c.execute("PRAGMA journal_mode=WAL")
    c.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS sources USING fts5(
            path, title, body, date, source_path,
            tokenize='porter unicode61'
        )
    """)
    c.commit()
    c.close()


def index_file(path_str, title):
    init_db()
    p = Path(path_str)
    if not p.exists():
        print(f"Error: {p} not found")
        sys.exit(1)
    text = p.read_text()
    rel = str(p.relative_to(Path("vault"))) if str(p).startswith("vault") else str(p)

    # Find the original (non-extracted) file
    stem = p.name.replace(".extracted.md", "")
    originals = [f for f in p.parent.glob(f"{stem}.*") if ".extracted." not in f.name]
    src = ""
    if originals:
        try:
            src = str(originals[0].relative_to(Path("vault")))
        except ValueError:
            src = str(originals[0])

    c = sqlite3.connect(str(DB))
    c.execute("PRAGMA journal_mode=WAL")
    c.execute(
        "INSERT INTO sources(path, title, body, date, source_path) VALUES(?,?,?,?,?)",
        (rel, title, text, datetime.now().strftime("%Y-%m-%d"), src)
    )
    c.commit()
    c.close()
    print(f"Indexed: {rel} ({len(text)} chars)")


def rebuild():
    """Delete and rebuild index from all .extracted.md files."""
    DB.unlink(missing_ok=True)
    init_db()
    vault = Path("vault")
    count = 0
    c = sqlite3.connect(str(DB))
    c.execute("PRAGMA journal_mode=WAL")
    for f in sorted(vault.rglob("*.extracted.md")):
        text = f.read_text()
        rel = str(f.relative_to(vault))
        stem = f.name.replace(".extracted.md", "")
        originals = [o for o in f.parent.glob(f"{stem}.*") if ".extracted." not in o.name]
        src = str(originals[0].relative_to(vault)) if originals else ""
        c.execute(
            "INSERT INTO sources(path, title, body, date, source_path) VALUES(?,?,?,?,?)",
            (rel, stem, text, "", src)
        )
        count += 1
    c.commit()
    c.close()
    print(f"Rebuilt index: {count} documents")


def count():
    if not DB.exists():
        print("0")
        return
    c = sqlite3.connect(str(DB))
    n = c.execute("SELECT COUNT(*) FROM sources").fetchone()[0]
    c.close()
    print(n)


if __name__ == "__main__":
    if "--init" in sys.argv:
        init_db()
        print("vault.db initialized")
    elif "--rebuild" in sys.argv:
        rebuild()
    elif "--count" in sys.argv:
        count()
    elif len(sys.argv) >= 3:
        index_file(sys.argv[1], sys.argv[2])
    else:
        print("Usage: vault_index.py <file.extracted.md> <title>")
        print("       vault_index.py --init | --rebuild | --count")
        sys.exit(1)
