#!/usr/bin/env python3

import argparse
import json
import sqlite3
import subprocess
import sys
from pathlib import Path
from typing import Dict, Optional, Sequence, TextIO


CORE_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS sources (
    id TEXT PRIMARY KEY,
    kind TEXT,
    host_label TEXT,
    machine_id TEXT,
    platform TEXT,
    config_json TEXT,
    created_at INTEGER,
    updated_at INTEGER
);
CREATE TABLE IF NOT EXISTS agents (
    id INTEGER PRIMARY KEY,
    slug TEXT,
    name TEXT,
    version TEXT,
    kind TEXT,
    created_at INTEGER,
    updated_at INTEGER
);
CREATE TABLE IF NOT EXISTS workspaces (
    id INTEGER PRIMARY KEY,
    path TEXT,
    display_name TEXT
);
CREATE TABLE IF NOT EXISTS conversations (
    id INTEGER PRIMARY KEY,
    agent_id INTEGER,
    workspace_id INTEGER,
    source_id TEXT,
    external_id TEXT,
    title TEXT,
    source_path TEXT,
    started_at INTEGER,
    ended_at INTEGER,
    approx_tokens INTEGER,
    metadata_json TEXT,
    origin_host TEXT,
    metadata_bin BLOB,
    total_input_tokens INTEGER,
    total_output_tokens INTEGER,
    total_cache_read_tokens INTEGER,
    total_cache_creation_tokens INTEGER,
    grand_total_tokens INTEGER,
    estimated_cost_usd REAL,
    primary_model TEXT,
    api_call_count INTEGER,
    tool_call_count INTEGER,
    user_message_count INTEGER,
    assistant_message_count INTEGER
);
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY,
    conversation_id INTEGER,
    idx INTEGER,
    role TEXT,
    author TEXT,
    created_at INTEGER,
    content TEXT,
    extra_json TEXT,
    extra_bin BLOB
);
CREATE TABLE IF NOT EXISTS snippets (
    id INTEGER PRIMARY KEY,
    message_id INTEGER,
    file_path TEXT,
    start_line INTEGER,
    end_line INTEGER,
    language TEXT,
    snippet_text TEXT
);
"""

RECOVERABLE_TABLES: Sequence[str] = (
    "sources",
    "agents",
    "workspaces",
    "conversations",
    "messages",
    "snippets",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Recover canonical session rows from a damaged historical SQLite bundle."
    )
    parser.add_argument("source_db", help="Path to the damaged historical SQLite bundle.")
    parser.add_argument("output_db", help="Path to the recovered staging SQLite database.")
    parser.add_argument(
        "--sqlite3-bin",
        default="sqlite3",
        help="Path to the sqlite3 binary.",
    )
    parser.add_argument(
        "--filtered-sql",
        default=None,
        help="Optional path to save the filtered recovery SQL stream.",
    )
    parser.add_argument(
        "--overwrite-output",
        action="store_true",
        help="Allow writing to an existing output DB path.",
    )
    return parser.parse_args()


def is_recoverable_insert(line: str) -> Optional[str]:
    for table in RECOVERABLE_TABLES:
        prefixes = (
            f"INSERT INTO '{table}'",
            f"INSERT OR IGNORE INTO '{table}'",
            f'INSERT INTO "{table}"',
            f'INSERT OR IGNORE INTO "{table}"',
        )
        if line.startswith(prefixes):
            return table
    return None


def prepare_output_db(output_db: Path, overwrite_output: bool) -> None:
    if output_db.exists() and not overwrite_output:
        raise SystemExit(
            f"Refusing to overwrite existing output DB: {output_db}. "
            "Pass --overwrite-output if you explicitly want that."
        )
    output_db.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(output_db)
    try:
        conn.executescript(CORE_SCHEMA_SQL)
        conn.commit()
    finally:
        conn.close()


def write_line(stream: TextIO, line: str) -> None:
    stream.write(line)
    if not line.endswith("\n"):
        stream.write("\n")


def summarize_output_db(output_db: Path) -> Dict[str, object]:
    conn = sqlite3.connect(output_db)
    try:
        counts = {}
        for table in RECOVERABLE_TABLES:
            counts[table] = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        return counts
    finally:
        conn.close()


def main() -> int:
    args = parse_args()
    source_db = Path(args.source_db).expanduser().resolve()
    output_db = Path(args.output_db).expanduser().resolve()

    if not source_db.exists():
        raise SystemExit(f"Source DB does not exist: {source_db}")

    prepare_output_db(output_db, args.overwrite_output)

    bundle_uri = source_db.as_uri() + "?immutable=1"
    recover = subprocess.Popen(
        [args.sqlite3_bin, bundle_uri, ".recover"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )
    importer = subprocess.Popen(
        [args.sqlite3_bin, str(output_db)],
        stdin=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )

    if recover.stdout is None or importer.stdin is None:
        raise SystemExit("Failed to open sqlite3 subprocess pipes")

    filtered_sql_handle = None
    if args.filtered_sql:
        filtered_sql_path = Path(args.filtered_sql).expanduser().resolve()
        filtered_sql_path.parent.mkdir(parents=True, exist_ok=True)
        filtered_sql_handle = filtered_sql_path.open("w", encoding="utf-8")

    recovered_inserts = 0
    recovered_by_table = {table: 0 for table in RECOVERABLE_TABLES}

    try:
        write_line(importer.stdin, "BEGIN;")
        for raw_line in recover.stdout:
            table = is_recoverable_insert(raw_line)
            if table is None:
                continue
            write_line(importer.stdin, raw_line)
            if filtered_sql_handle is not None:
                write_line(filtered_sql_handle, raw_line)
            recovered_inserts += 1
            recovered_by_table[table] += 1
        write_line(importer.stdin, "COMMIT;")
        importer.stdin.close()
    finally:
        if filtered_sql_handle is not None:
            filtered_sql_handle.close()

    recover_stderr = recover.stderr.read() if recover.stderr is not None else ""
    importer_stderr = importer.stderr.read() if importer.stderr is not None else ""

    recover_status = recover.wait()
    importer_status = importer.wait()

    if recover_status != 0:
        raise SystemExit(
            f"sqlite3 .recover failed for {source_db} with exit code {recover_status}\n{recover_stderr}"
        )
    if importer_status != 0:
        raise SystemExit(
            f"sqlite3 importer failed for {output_db} with exit code {importer_status}\n{importer_stderr}"
        )

    summary = {
        "source_db": str(source_db),
        "output_db": str(output_db),
        "filtered_insert_lines": recovered_inserts,
        "filtered_insert_lines_by_table": recovered_by_table,
        "output_counts": summarize_output_db(output_db),
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
