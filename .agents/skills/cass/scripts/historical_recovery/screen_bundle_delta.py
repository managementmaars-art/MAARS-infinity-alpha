#!/usr/bin/env python3

import argparse
import glob
import json
import sqlite3
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Sequence, Tuple


DEFAULT_CANONICAL_DB = "/home/ubuntu/.local/share/coding-agent-search/agent_search.db"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fast exact-key screening for historical bundle deltas vs the canonical cass DB."
    )
    parser.add_argument(
        "--canonical-db",
        default=DEFAULT_CANONICAL_DB,
        help=f"Canonical cass DB path. Default: {DEFAULT_CANONICAL_DB}",
    )
    parser.add_argument(
        "paths",
        nargs="+",
        help="Bundle paths or glob patterns to screen.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Stop after this many resolved bundle paths.",
    )
    return parser.parse_args()


def resolve_paths(patterns: Sequence[str]) -> List[Path]:
    resolved: List[Path] = []
    seen = set()
    for pattern in patterns:
        matches = glob.glob(pattern)
        if not matches:
            matches = [pattern]
        for match in matches:
            path = Path(match).expanduser().resolve()
            if not path.exists() or path.is_dir():
                continue
            path_str = str(path)
            if any(path_str.endswith(suffix) for suffix in ("-wal", "-shm", "-journal")):
                continue
            name = path.name
            if any(marker in name for marker in (".db-wal.", ".db-shm.", ".db-journal.")):
                continue
            if path in seen:
                continue
            seen.add(path)
            resolved.append(path)
    return resolved


def open_ro(path: Path) -> sqlite3.Connection:
    uri = path.resolve().as_uri() + "?mode=ro"
    conn = sqlite3.connect(uri, uri=True, timeout=20.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA query_only = ON")
    conn.execute("PRAGMA writable_schema = ON")
    return conn


def load_canonical_keys(canonical_db: Path) -> Dict[Tuple[str, str, str], int]:
    conn = sqlite3.connect(canonical_db, timeout=20.0)
    conn.row_factory = sqlite3.Row
    result: Dict[Tuple[str, str, str], int] = {}
    try:
        for row in conn.execute(
            """
            SELECT c.source_id, a.slug, c.external_id, COUNT(m.id) AS message_count
            FROM conversations c
            JOIN agents a ON a.id = c.agent_id
            LEFT JOIN messages m ON m.conversation_id = c.id
            WHERE c.external_id IS NOT NULL
            GROUP BY c.id, c.source_id, a.slug, c.external_id
            """
        ):
            result[(str(row["source_id"]), str(row["slug"]), str(row["external_id"]))] = int(
                row["message_count"]
            )
    finally:
        conn.close()
    return result


def screen_bundle(path: Path, canonical_keys: Dict[Tuple[str, str, str], int]) -> Dict[str, object]:
    conn = open_ro(path)
    stats = {
        "bundle": str(path),
        "total_conversations": 0,
        "missing_exact_key_conversations": 0,
        "matched_conversations_with_more_messages": 0,
        "matched_conversations": 0,
        "schema_error": None,
    }
    try:
        agents = {
            int(row["id"]): str(row["slug"])
            for row in conn.execute("SELECT id, slug FROM agents")
        }
        for row in conn.execute(
            """
            SELECT c.id, c.source_id, c.external_id, c.agent_id,
                   (SELECT COUNT(*) FROM messages m WHERE m.conversation_id = c.id) AS message_count
            FROM conversations c
            WHERE c.external_id IS NOT NULL
            ORDER BY c.id
            """
        ):
            stats["total_conversations"] += 1
            key = (
                str(row["source_id"] or "local"),
                agents[int(row["agent_id"])],
                str(row["external_id"]),
            )
            canonical_message_count = canonical_keys.get(key)
            if canonical_message_count is None:
                stats["missing_exact_key_conversations"] += 1
                continue
            stats["matched_conversations"] += 1
            if int(row["message_count"]) > canonical_message_count:
                stats["matched_conversations_with_more_messages"] += 1
    except sqlite3.Error as exc:
        stats["schema_error"] = f"{type(exc).__name__}: {exc}"
    finally:
        conn.close()
    return stats


def main() -> int:
    args = parse_args()
    canonical_db = Path(args.canonical_db).expanduser().resolve()
    paths = resolve_paths(args.paths)
    if args.limit is not None:
        paths = paths[: args.limit]
    canonical_keys = load_canonical_keys(canonical_db)
    for path in paths:
        print(json.dumps(screen_bundle(path, canonical_keys), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
