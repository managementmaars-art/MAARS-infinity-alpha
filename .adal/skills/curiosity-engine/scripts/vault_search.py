#!/usr/bin/env python3
"""BM25-ranked full-text search over vault sources.

Usage:
    python3 vault_search.py "query"              # top 10 results as JSON
    python3 vault_search.py "query" --limit 5    # top 5
    python3 vault_search.py "query" --text        # include full extracted text
    python3 vault_search.py --count              # total indexed documents
"""

import sqlite3
import json
import sys
from pathlib import Path

DB = Path("vault/vault.db")


def search(query, limit=10, include_text=False):
    if not DB.exists():
        print("[]")
        return

    c = sqlite3.connect(str(DB))
    c.execute("PRAGMA journal_mode=WAL")

    if include_text:
        rows = c.execute("""
            SELECT path, title, source_path, date, body, bm25(sources) as rank
            FROM sources WHERE sources MATCH ? ORDER BY rank LIMIT ?
        """, (query, limit)).fetchall()
        c.close()
        results = [{"path": r[0], "title": r[1], "source_path": r[2],
                     "date": r[3], "text": r[4], "rank": r[5]} for r in rows]
    else:
        rows = c.execute("""
            SELECT path, title, source_path, date,
                   snippet(sources, 2, '>>>', '<<<', '...', 40) as snippet,
                   bm25(sources) as rank
            FROM sources WHERE sources MATCH ? ORDER BY rank LIMIT ?
        """, (query, limit)).fetchall()
        c.close()
        results = [{"path": r[0], "title": r[1], "source_path": r[2],
                     "date": r[3], "snippet": r[4], "rank": r[5]} for r in rows]

    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    if "--count" in sys.argv:
        if DB.exists():
            c = sqlite3.connect(str(DB))
            print(c.execute("SELECT COUNT(*) FROM sources").fetchone()[0])
            c.close()
        else:
            print("0")
        sys.exit(0)

    query = None
    limit = 10
    include_text = "--text" in sys.argv

    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if args:
        query = args[0]
    if "--limit" in sys.argv:
        idx = sys.argv.index("--limit")
        if idx + 1 < len(sys.argv):
            limit = int(sys.argv[idx + 1])

    if query:
        search(query, limit, include_text)
    else:
        print('Usage: vault_search.py "query" [--limit N] [--text]')
        sys.exit(1)
