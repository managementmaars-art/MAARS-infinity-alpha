from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any


SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT NOT NULL DEFAULT '',
    is_pinned INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE COLLATE NOCASE
);

CREATE TABLE IF NOT EXISTS note_tags (
    note_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    PRIMARY KEY (note_id, tag_id),
    FOREIGN KEY (note_id) REFERENCES notes (id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags (id) ON DELETE CASCADE
);
"""


class CliError(Exception):
    exit_code = 4
    error_code = "internal_error"

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class CliUsageError(CliError):
    exit_code = 2
    error_code = "invalid_arguments"


class ValidationError(CliError):
    exit_code = 2

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.error_code = code


class NoteNotFoundError(CliError):
    exit_code = 3
    error_code = "not_found"


class FastNoteArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise CliUsageError(message)


def parse_bool(value: str) -> bool:
    lowered = value.casefold()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    raise CliUsageError(f"Invalid boolean value '{value}'. Use true or false.")


def positive_int(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise CliUsageError(f"Invalid integer value '{value}'.") from exc
    if parsed <= 0:
        raise CliUsageError("Value must be a positive integer.")
    return parsed


def require_title(value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValidationError("invalid_title", "Field 'title' must be a non-empty string.")
    return value.strip()


def require_content(value: object) -> str:
    if not isinstance(value, str):
        raise ValidationError("invalid_content", "Field 'content' must be a string.")
    return value


def resolve_content(
    *,
    content: str | None,
    content_file: Path | None,
    content_stdin: bool,
) -> str:
    sources = int(content is not None) + int(content_file is not None) + int(content_stdin)
    if sources > 1:
        raise CliUsageError("Use only one of --content, --content-file, or --content-stdin.")
    if content_file is not None:
        try:
            return require_content(content_file.read_text(encoding="utf-8"))
        except OSError as exc:
            raise CliUsageError(f"Could not read content file '{content_file}': {exc.strerror or exc}") from exc
    if content_stdin:
        return require_content(sys.stdin.read())
    if content is None:
        return ""
    return require_content(content)


def normalize_tags(tags: Sequence[str]) -> list[str]:
    seen: set[str] = set()
    normalized: list[str] = []
    for tag in tags:
        cleaned = tag.strip()
        if not cleaned:
            continue
        key = cleaned.casefold()
        if key in seen:
            continue
        seen.add(key)
        normalized.append(cleaned)
    return normalized


def build_preview(content: str, max_length: int = 140) -> str:
    compact = " ".join(content.split())
    if len(compact) <= max_length:
        return compact
    return f"{compact[: max_length - 3].rstrip()}..."


def default_database_path() -> Path:
    if os.name == "nt":
        root = os.environ.get("LOCALAPPDATA")
        if root:
            return Path(root) / "FastNote" / "fastnote.sqlite3"
        return Path.home() / "AppData" / "Local" / "FastNote" / "fastnote.sqlite3"

    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "FastNote" / "fastnote.sqlite3"

    return Path.home() / ".local" / "share" / "FastNote" / "fastnote.sqlite3"


def connect_database(database_path: Path) -> tuple[sqlite3.Connection, dict[str, Any]]:
    database_existed = database_path.exists()
    parent_existed = database_path.parent.exists()
    database_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON;")
    connection.executescript(SCHEMA)
    connection.commit()
    meta = {
        "db_path": str(database_path.resolve()),
        "db_initialized": not database_existed,
        "data_dir_created": not parent_existed,
        "backup_reminder": "Back up this SQLite file regularly.",
    }
    return connection, meta


def row_to_note(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "id": row["id"],
        "title": row["title"],
        "content": row["content"],
        "preview": build_preview(row["content"]),
        "is_pinned": bool(row["is_pinned"]),
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
        "tags": [],
    }


def to_note_summary(note: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": note["id"],
        "title": note["title"],
        "preview": note["preview"],
        "is_pinned": note["is_pinned"],
        "created_at": note["created_at"],
        "updated_at": note["updated_at"],
        "tags": note["tags"],
    }


def attach_tags(connection: sqlite3.Connection, notes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not notes:
        return notes

    note_ids = [note["id"] for note in notes]
    placeholders = ", ".join("?" for _ in note_ids)
    rows = connection.execute(
        f"""
        SELECT nt.note_id, t.name
        FROM note_tags nt
        JOIN tags t ON t.id = nt.tag_id
        WHERE nt.note_id IN ({placeholders})
        ORDER BY LOWER(t.name) ASC
        """,
        note_ids,
    ).fetchall()

    grouped: dict[int, list[str]] = {note_id: [] for note_id in note_ids}
    for row in rows:
        grouped[row["note_id"]].append(row["name"])

    for note in notes:
        note["tags"] = grouped[note["id"]]

    return notes


def get_note(connection: sqlite3.Connection, note_id: int) -> dict[str, Any] | None:
    row = connection.execute(
        """
        SELECT id, title, content, is_pinned, created_at, updated_at
        FROM notes
        WHERE id = ?
        """,
        (note_id,),
    ).fetchone()
    if row is None:
        return None

    return attach_tags(connection, [row_to_note(row)])[0]


def replace_note_tags(connection: sqlite3.Connection, note_id: int, tags: Sequence[str]) -> None:
    connection.execute("DELETE FROM note_tags WHERE note_id = ?", (note_id,))

    for tag_name in normalize_tags(tags):
        connection.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", (tag_name,))
        tag_row = connection.execute(
            "SELECT id FROM tags WHERE name = ? COLLATE NOCASE",
            (tag_name,),
        ).fetchone()
        connection.execute(
            "INSERT OR IGNORE INTO note_tags (note_id, tag_id) VALUES (?, ?)",
            (note_id, tag_row["id"]),
        )


def list_notes(
    connection: sqlite3.Connection,
    *,
    query: str = "",
    tag: str = "",
    pinned: bool | None = None,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    clauses: list[str] = []
    params: list[Any] = []

    if query:
        like = f"%{query.strip().casefold()}%"
        clauses.append(
            """
            (
                LOWER(n.title) LIKE ?
                OR LOWER(n.content) LIKE ?
                OR EXISTS (
                    SELECT 1
                    FROM note_tags nt
                    JOIN tags t ON t.id = nt.tag_id
                    WHERE nt.note_id = n.id
                    AND LOWER(t.name) LIKE ?
                )
            )
            """
        )
        params.extend([like, like, like])

    if tag:
        clauses.append(
            """
            EXISTS (
                SELECT 1
                FROM note_tags nt
                JOIN tags t ON t.id = nt.tag_id
                WHERE nt.note_id = n.id
                AND LOWER(t.name) = ?
            )
            """
        )
        params.append(tag.strip().casefold())

    if pinned is not None:
        clauses.append("n.is_pinned = ?")
        params.append(int(pinned))

    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    limit_sql = "LIMIT ?" if limit is not None else ""
    if limit is not None:
        params.append(limit)

    rows = connection.execute(
        f"""
        SELECT n.id, n.title, n.content, n.is_pinned, n.created_at, n.updated_at
        FROM notes n
        {where}
        ORDER BY n.is_pinned DESC, n.updated_at DESC, n.id DESC
        {limit_sql}
        """,
        params,
    ).fetchall()
    notes = [row_to_note(row) for row in rows]
    return attach_tags(connection, notes)


def create_note(
    connection: sqlite3.Connection,
    *,
    title: str,
    content: str,
    tags: Sequence[str],
    is_pinned: bool,
) -> dict[str, Any]:
    cursor = connection.execute(
        """
        INSERT INTO notes (title, content, is_pinned)
        VALUES (?, ?, ?)
        """,
        (require_title(title), require_content(content), int(is_pinned)),
    )
    note_id = int(cursor.lastrowid)
    replace_note_tags(connection, note_id, tags)
    connection.commit()
    note = get_note(connection, note_id)
    if note is None:
        raise CliError("Created note could not be read back.")
    return note


def update_note(
    connection: sqlite3.Connection,
    *,
    note_id: int,
    title: str,
    content: str,
    tags: Sequence[str],
    is_pinned: bool,
) -> dict[str, Any]:
    cursor = connection.execute(
        """
        UPDATE notes
        SET title = ?, content = ?, is_pinned = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """,
        (require_title(title), require_content(content), int(is_pinned), note_id),
    )
    if cursor.rowcount == 0:
        connection.rollback()
        raise NoteNotFoundError(f"Note {note_id} not found.")

    replace_note_tags(connection, note_id, tags)
    connection.commit()
    note = get_note(connection, note_id)
    if note is None:
        raise CliError("Updated note could not be read back.")
    return note


def delete_note(connection: sqlite3.Connection, note_id: int) -> dict[str, Any]:
    cursor = connection.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    connection.commit()
    if cursor.rowcount == 0:
        raise NoteNotFoundError(f"Note {note_id} not found.")
    return {"ok": True, "deleted": True, "id": note_id}


def set_note_pin(connection: sqlite3.Connection, note_id: int, is_pinned: bool) -> dict[str, Any]:
    cursor = connection.execute(
        """
        UPDATE notes
        SET is_pinned = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """,
        (int(is_pinned), note_id),
    )
    connection.commit()
    if cursor.rowcount == 0:
        raise NoteNotFoundError(f"Note {note_id} not found.")

    note = get_note(connection, note_id)
    if note is None:
        raise CliError("Pinned note could not be read back.")
    return note


def list_tags(connection: sqlite3.Connection) -> list[dict[str, Any]]:
    rows = connection.execute(
        """
        SELECT t.name, COUNT(nt.note_id) AS note_count
        FROM tags t
        LEFT JOIN note_tags nt ON nt.tag_id = t.id
        GROUP BY t.id, t.name
        ORDER BY LOWER(t.name) ASC
        """
    ).fetchall()
    return [{"name": row["name"], "count": row["note_count"]} for row in rows]


def build_parser() -> argparse.ArgumentParser:
    parser = FastNoteArgumentParser(prog="fastnote-cli-skill", add_help=True)
    parser.add_argument("--db", type=Path, default=None, help="Path to fastnote.sqlite3")
    subparsers = parser.add_subparsers(dest="cli_command")

    list_parser = subparsers.add_parser("list", help="List notes")
    list_parser.add_argument("--q", default="", help="Search query")
    list_parser.add_argument("--tag", default="", help="Filter by tag")
    list_parser.add_argument("--pinned", type=parse_bool, default=None, help="Filter by pinned state")
    list_parser.add_argument("--limit", type=positive_int, default=None, help="Maximum notes to return")

    get_parser = subparsers.add_parser("get", help="Get one note")
    get_parser.add_argument("id", type=int)

    create_parser = subparsers.add_parser("create", help="Create a note")
    create_parser.add_argument("--title", required=True)
    create_parser.add_argument("--content", default=None)
    create_parser.add_argument("--content-file", type=Path, default=None)
    create_parser.add_argument("--content-stdin", action="store_true")
    create_parser.add_argument("--tag", action="append", default=[])
    create_parser.add_argument("--pinned", type=parse_bool, default=False)

    update_parser = subparsers.add_parser("update", help="Update a note")
    update_parser.add_argument("id", type=int)
    update_parser.add_argument("--title", required=True)
    update_parser.add_argument("--content", default=None)
    update_parser.add_argument("--content-file", type=Path, default=None)
    update_parser.add_argument("--content-stdin", action="store_true")
    update_parser.add_argument("--tag", action="append", default=[])
    update_parser.add_argument("--pinned", type=parse_bool, required=True)

    delete_parser = subparsers.add_parser("delete", help="Delete a note")
    delete_parser.add_argument("id", type=int)

    pin_parser = subparsers.add_parser("pin", help="Set note pinned state")
    pin_parser.add_argument("id", type=int)
    pin_parser.add_argument("--value", type=parse_bool, required=True)

    subparsers.add_parser("tags", help="List tags")
    return parser


def dispatch_command(connection: sqlite3.Connection, args: argparse.Namespace) -> dict[str, Any]:
    if args.cli_command == "list":
        notes = list_notes(
            connection,
            query=args.q,
            tag=args.tag,
            pinned=args.pinned,
            limit=args.limit,
        )
        return {
            "ok": True,
            "notes": [to_note_summary(note) for note in notes],
        }

    if args.cli_command == "get":
        note = get_note(connection, args.id)
        if note is None:
            raise NoteNotFoundError(f"Note {args.id} not found.")
        return {"ok": True, "note": note}

    if args.cli_command == "create":
        content = resolve_content(
            content=args.content,
            content_file=args.content_file,
            content_stdin=args.content_stdin,
        )
        note = create_note(
            connection,
            title=args.title,
            content=content,
            tags=args.tag,
            is_pinned=args.pinned,
        )
        return {"ok": True, "note": note}

    if args.cli_command == "update":
        if args.content is None and args.content_file is None and not args.content_stdin:
            raise CliUsageError("the following arguments are required: --content, --content-file, or --content-stdin")
        content = resolve_content(
            content=args.content,
            content_file=args.content_file,
            content_stdin=args.content_stdin,
        )
        note = update_note(
            connection,
            note_id=args.id,
            title=args.title,
            content=content,
            tags=args.tag,
            is_pinned=args.pinned,
        )
        return {"ok": True, "note": note}

    if args.cli_command == "delete":
        return delete_note(connection, args.id)

    if args.cli_command == "pin":
        note = set_note_pin(connection, args.id, args.value)
        return {"ok": True, "note": note}

    if args.cli_command == "tags":
        return {"ok": True, "tags": list_tags(connection)}

    raise CliUsageError("A CLI subcommand is required.")


def print_json(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False))


def with_meta(payload: dict[str, Any], meta: dict[str, Any]) -> dict[str, Any]:
    return {
        **payload,
        "meta": meta,
    }


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
        if args.cli_command is None:
            raise CliUsageError("A CLI subcommand is required.")

        database_path = args.db or default_database_path()
        connection, meta = connect_database(database_path)
        try:
            payload = dispatch_command(connection, args)
        finally:
            connection.close()

        print_json(with_meta(payload, meta))
        return 0
    except CliError as exc:
        print_json({"ok": False, "error": {"code": exc.error_code, "message": exc.message}})
        return exc.exit_code
    except Exception:
        print_json(
            {
                "ok": False,
                "error": {
                    "code": "internal_error",
                    "message": "Internal application error.",
                },
            }
        )
        return 4


if __name__ == "__main__":
    sys.exit(main())
