#!/usr/bin/env python3

import argparse
import json
import os
import sqlite3
import sys
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional, Sequence, Tuple


CORE_TABLES: Sequence[str] = (
    "sources",
    "agents",
    "workspaces",
    "conversations",
    "messages",
    "snippets",
    "meta",
    "fts_messages",
)
SIDE_SUFFIXES: Sequence[str] = ("-wal", "-shm", "-journal")
NAME_HINTS: Sequence[str] = (
    "agent_search",
    ".db",
    ".sqlite",
    ".sqlite3",
    ".corrupt.",
    "storage.sqlite3",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Inventory and classify likely SQLite/session bundles."
    )
    parser.add_argument(
        "--root",
        action="append",
        required=True,
        help="Root directory to scan. Can be provided multiple times.",
    )
    parser.add_argument(
        "--max-depth",
        type=int,
        default=None,
        help="Maximum walk depth relative to each root.",
    )
    parser.add_argument(
        "--with-quick-check",
        action="store_true",
        help="Run PRAGMA quick_check(1) on readable databases.",
    )
    parser.add_argument(
        "--format",
        choices=("jsonl", "json", "tsv"),
        default="jsonl",
        help="Output format.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Stop after this many candidate bundles.",
    )
    return parser.parse_args()


def sidecar_path(path: Path, suffix: str) -> Path:
    return Path(f"{path}{suffix}")


def looks_like_candidate(path: Path) -> bool:
    name = path.name
    if any(name.endswith(suffix) for suffix in SIDE_SUFFIXES):
        return False
    return any(hint in name for hint in NAME_HINTS)


def first_bytes(path: Path, byte_count: int = 16) -> bytes:
    try:
        with path.open("rb") as handle:
            return handle.read(byte_count)
    except OSError:
        return b""


def sqlite_header_state(path: Path) -> str:
    header = first_bytes(path, 16)
    if header == b"SQLite format 3\x00":
        return "sqlite"
    if not header:
        return "unreadable"
    return "non-sqlite-or-corrupt-header"


def total_bundle_bytes(path: Path) -> int:
    total = path.stat().st_size
    for suffix in SIDE_SUFFIXES:
        sidecar = sidecar_path(path, suffix)
        if sidecar.exists():
            total += sidecar.stat().st_size
    return total


def discover_candidates(roots: Sequence[Path], max_depth: Optional[int]) -> Iterator[Path]:
    seen = set()
    for root in roots:
        root = root.expanduser().resolve()
        if not root.exists():
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            current = Path(dirpath)
            if max_depth is not None:
                try:
                    rel_depth = len(current.relative_to(root).parts)
                except ValueError:
                    rel_depth = 0
                if rel_depth > max_depth:
                    dirnames[:] = []
                    continue
            for filename in filenames:
                candidate = current / filename
                if not looks_like_candidate(candidate):
                    continue
                resolved = candidate.resolve()
                if resolved in seen:
                    continue
                seen.add(resolved)
                yield resolved


def open_sqlite_readonly(path: Path) -> Tuple[Optional[sqlite3.Connection], Optional[str], Optional[str]]:
    uri_ro = path.resolve().as_uri() + "?mode=ro"
    for mode, uri in (("ro", uri_ro), ("immutable", path.resolve().as_uri() + "?immutable=1")):
        try:
            conn = sqlite3.connect(uri, uri=True, timeout=10.0)
            conn.execute("PRAGMA query_only = ON")
            conn.execute("PRAGMA writable_schema = ON")
            return conn, mode, None
        except sqlite3.Error as exc:
            last_error = f"{type(exc).__name__}: {exc}"
    return None, None, last_error


def safe_scalar(conn: sqlite3.Connection, sql: str) -> Tuple[Optional[object], Optional[str]]:
    try:
        row = conn.execute(sql).fetchone()
        return (row[0] if row else None), None
    except sqlite3.Error as exc:
        return None, f"{type(exc).__name__}: {exc}"


def probe_sqlite(path: Path, with_quick_check: bool) -> Dict[str, object]:
    record: Dict[str, object] = {
        "path": str(path),
        "header_state": sqlite_header_state(path),
        "size_bytes": path.stat().st_size,
        "bundle_bytes": total_bundle_bytes(path),
        "sidecars": {
            suffix[1:]: sidecar_path(path, suffix).stat().st_size
            for suffix in SIDE_SUFFIXES
            if sidecar_path(path, suffix).exists()
        },
    }
    conn, open_mode, open_error = open_sqlite_readonly(path)
    record["open_mode"] = open_mode
    if conn is None:
        record["status"] = "open-failed"
        record["open_error"] = open_error
        return record

    try:
        tables, tables_error = safe_scalar(
            conn,
            "SELECT json_group_array(name) FROM sqlite_master WHERE type='table' ORDER BY name",
        )
        if tables_error:
            record["status"] = "schema-unreadable"
            record["schema_error"] = tables_error
            return record

        table_names: List[str] = json.loads(tables) if tables else []
        core_presence = {table: (table in table_names) for table in CORE_TABLES}
        record["tables_present"] = core_presence
        record["table_count"] = len(table_names)

        schema_version, schema_error = safe_scalar(conn, "PRAGMA schema_version")
        if schema_error:
            record["schema_version_error"] = schema_error
        else:
            record["schema_version"] = schema_version

        if with_quick_check:
            quick_check, quick_error = safe_scalar(conn, "PRAGMA quick_check(1)")
            if quick_error:
                record["quick_check_error"] = quick_error
            else:
                record["quick_check"] = quick_check

        counts: Dict[str, Optional[int]] = {}
        count_errors: Dict[str, str] = {}
        for table in ("conversations", "messages", "agents", "workspaces", "sources"):
            if not core_presence.get(table):
                continue
            value, error = safe_scalar(conn, f"SELECT COUNT(*) FROM {table}")
            if error:
                count_errors[table] = error
            else:
                counts[table] = int(value) if value is not None else 0
        if counts:
            record["counts"] = counts
        if count_errors:
            record["count_errors"] = count_errors

        max_ids: Dict[str, Optional[int]] = {}
        for table in ("conversations", "messages"):
            if not core_presence.get(table):
                continue
            value, error = safe_scalar(conn, f"SELECT COALESCE(MAX(id), 0) FROM {table}")
            if error:
                count_errors[f"{table}_max_id"] = error
            else:
                max_ids[table] = int(value) if value is not None else 0
        if max_ids:
            record["max_ids"] = max_ids

        if core_presence.get("conversations") and core_presence.get("messages"):
            record["status"] = "core-readable"
        else:
            record["status"] = "sqlite-readable-noncore"
        return record
    finally:
        conn.close()


def emit_tsv(records: Sequence[Dict[str, object]]) -> None:
    headers = [
        "status",
        "path",
        "bundle_bytes",
        "open_mode",
        "schema_version",
        "conversations",
        "messages",
        "open_error",
        "schema_error",
    ]
    print("\t".join(headers))
    for record in records:
        counts = record.get("counts", {})
        row = [
            str(record.get("status", "")),
            str(record.get("path", "")),
            str(record.get("bundle_bytes", "")),
            str(record.get("open_mode", "")),
            str(record.get("schema_version", "")),
            str(counts.get("conversations", "")) if isinstance(counts, dict) else "",
            str(counts.get("messages", "")) if isinstance(counts, dict) else "",
            str(record.get("open_error", "")),
            str(record.get("schema_error", "")),
        ]
        print("\t".join(row))


def main() -> int:
    args = parse_args()
    roots = [Path(root) for root in args.root]
    records: List[Dict[str, object]] = []
    for idx, path in enumerate(discover_candidates(roots, args.max_depth), start=1):
        records.append(probe_sqlite(path, args.with_quick_check))
        if args.limit is not None and idx >= args.limit:
            break

    records.sort(
        key=lambda record: (
            record.get("status") != "core-readable",
            -int(record.get("bundle_bytes", 0)),
            str(record.get("path", "")),
        )
    )

    if args.format == "json":
        json.dump(records, sys.stdout, indent=2)
        print()
    elif args.format == "tsv":
        emit_tsv(records)
    else:
        for record in records:
            print(json.dumps(record, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
