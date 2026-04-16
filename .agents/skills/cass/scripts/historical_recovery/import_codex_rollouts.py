#!/usr/bin/env python3

import argparse
import hashlib
import json
import math
import sqlite3
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple


DEFAULT_CANONICAL_DB = "/home/ubuntu/.local/share/coding-agent-search/agent_search.db"
DEFAULT_SESSIONS_ROOT = "/home/ubuntu/.codex/sessions"
DEFAULT_STATE_DB = "/home/ubuntu/.codex/state_5.sqlite"
LOCAL_SOURCE_ID = "local"
LARGE_SESSION_EXTRA_COMPACT_THRESHOLD_BYTES = 32 * 1024 * 1024


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Reconcile raw Codex rollout session files into the canonical cass DB."
    )
    parser.add_argument(
        "--canonical-db",
        default=DEFAULT_CANONICAL_DB,
        help=f"Canonical cass DB path. Default: {DEFAULT_CANONICAL_DB}",
    )
    parser.add_argument(
        "--sessions-root",
        default=DEFAULT_SESSIONS_ROOT,
        help=f"Root containing Codex rollout files. Default: {DEFAULT_SESSIONS_ROOT}",
    )
    parser.add_argument(
        "--state-db",
        default=DEFAULT_STATE_DB,
        help=(
            "Optional Codex state DB used only as metadata fallback "
            f"(default: {DEFAULT_STATE_DB})."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Analyze deltas without modifying the canonical DB.",
    )
    parser.add_argument(
        "--commit-every",
        type=int,
        default=25,
        help="Commit after this many processed rollout files in write mode.",
    )
    parser.add_argument(
        "--progress-every",
        type=int,
        default=100,
        help="Emit progress to stderr every N rollout files. Use 0 to disable.",
    )
    parser.add_argument(
        "--max-files",
        type=int,
        default=None,
        help="Stop after processing this many rollout files.",
    )
    parser.add_argument(
        "--start-after",
        default=None,
        help="Skip rollout paths lexically <= this absolute path.",
    )
    parser.add_argument(
        "--meta-key-prefix",
        default="raw_codex_rollout_python_import",
        help="Prefix for the meta ledger entry written after a successful import.",
    )
    return parser.parse_args()


def now_ms() -> int:
    return int(time.time() * 1000)


def coerce_ts_ms(value: object) -> Optional[int]:
    if value is None or isinstance(value, bool):
        return None

    if isinstance(value, int):
        return value * 1000 if 0 <= value < 100_000_000_000 else value

    if isinstance(value, float):
        if not math.isfinite(value) or value <= 0:
            return None
        scaled = value * 1000 if value < 100_000_000_000 else value
        return int(round(scaled))

    if isinstance(value, str):
        raw = value.strip()
        if not raw:
            return None
        try:
            return coerce_ts_ms(int(raw))
        except ValueError:
            pass
        try:
            return coerce_ts_ms(float(raw))
        except ValueError:
            pass
        candidate = raw[:-1] + "+00:00" if raw.endswith("Z") else raw
        try:
            dt = datetime.fromisoformat(candidate)
        except ValueError:
            return None
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return int(round(dt.timestamp() * 1000))

    return None


def flatten_content(value: object) -> str:
    if isinstance(value, str):
        return value

    if isinstance(value, list):
        parts: List[str] = []
        for item in value:
            part = extract_content_part(item)
            if part:
                parts.append(part)
        return "\n".join(parts)

    return ""


def extract_content_part(item: object) -> Optional[str]:
    if isinstance(item, str):
        return item
    if not isinstance(item, dict):
        return None

    item_type = item.get("type")
    text = item.get("text")
    if isinstance(text, str) and (item_type is None or item_type in {"text", "input_text"}):
        return text

    if item_type == "tool_use":
        name = item.get("name") if isinstance(item.get("name"), str) else "unknown"
        desc = ""
        input_obj = item.get("input")
        if isinstance(input_obj, dict):
            if isinstance(input_obj.get("description"), str):
                desc = input_obj["description"]
            elif isinstance(input_obj.get("file_path"), str):
                desc = input_obj["file_path"]
        return f"[Tool: {name}]" if not desc else f"[Tool: {name} - {desc}]"

    return None


def compact_message_extra(raw: Dict[str, object]) -> Dict[str, object]:
    cass: Dict[str, object] = {}

    model = raw.get("model")
    if isinstance(model, str) and model.strip():
        cass["model"] = model
    else:
        response = raw.get("response")
        if isinstance(response, dict):
            nested_model = response.get("model")
            if isinstance(nested_model, str) and nested_model.strip():
                cass["model"] = nested_model

    attachments = raw.get("attachment_refs")
    if attachments is None:
        attachments = raw.get("attachments")
    if attachments is not None:
        cass["attachments"] = attachments

    return {} if not cass else {"cass": cass}


def token_usage_from_payload(payload: Dict[str, object]) -> Optional[Dict[str, object]]:
    input_tokens = payload.get("input_tokens")
    output_tokens = payload.get("output_tokens")
    if output_tokens is None:
        output_tokens = payload.get("tokens")

    usage: Dict[str, object] = {}
    parsed_input = coerce_ts_like_integer(input_tokens)
    parsed_output = coerce_ts_like_integer(output_tokens)

    if parsed_input is not None:
        usage["input_tokens"] = parsed_input
    if parsed_output is not None:
        usage["output_tokens"] = parsed_output
    if not usage:
        return None

    usage["data_source"] = "api"
    return usage


def coerce_ts_like_integer(value: object) -> Optional[int]:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(round(value))
    if isinstance(value, str):
        raw = value.strip()
        if not raw:
            return None
        try:
            return int(raw)
        except ValueError:
            try:
                return int(round(float(raw)))
            except ValueError:
                return None
    return None


def update_time_bounds(
    started_at: Optional[int],
    ended_at: Optional[int],
    timestamp_ms: Optional[int],
) -> Tuple[Optional[int], Optional[int]]:
    if timestamp_ms is None:
        return started_at, ended_at
    if started_at is None or timestamp_ms < started_at:
        started_at = timestamp_ms
    if ended_at is None or timestamp_ms > ended_at:
        ended_at = timestamp_ms
    return started_at, ended_at


def maybe_compact_extra(path: Path, payload: Dict[str, object], compact: bool) -> Dict[str, object]:
    if compact:
        return compact_message_extra(payload)
    return payload


def attach_token_usage_to_latest_assistant(
    messages: List[Dict[str, object]],
    token_usage: Dict[str, object],
) -> bool:
    for message in reversed(messages):
        if message["role"] == "assistant" and message["author"] is None:
            extra = message["extra"]
            if not isinstance(extra, dict):
                extra = {}
                message["extra"] = extra
            cass = extra.get("cass")
            if not isinstance(cass, dict):
                cass = {}
                extra["cass"] = cass
            cass["token_usage"] = token_usage
            return True
    return False


def derive_title(messages: Sequence[Dict[str, object]], fallback: Optional[str]) -> Optional[str]:
    for message in messages:
        if message["role"] == "user":
            first_line = message["content"].splitlines()[0] if message["content"] else ""
            if first_line:
                return first_line[:100]
    if messages:
        first_line = messages[0]["content"].splitlines()[0] if messages[0]["content"] else ""
        if first_line:
            return first_line[:100]
    if fallback:
        return fallback[:100]
    return None


def reindex_messages(messages: List[Dict[str, object]]) -> None:
    for idx, message in enumerate(messages):
        message["idx"] = idx


def canonical_message_fingerprint(
    row: sqlite3.Row,
) -> Tuple[int, Optional[int], str, Optional[str], str]:
    return (
        int(row["idx"]),
        row["created_at"],
        row["role"],
        row["author"],
        hashlib.sha256((row["content"] or "").encode("utf-8", errors="replace")).hexdigest(),
    )


def canonical_replay_fingerprint(
    created_at: Optional[int],
    role: str,
    author: Optional[str],
    content: str,
) -> Tuple[Optional[int], str, Optional[str], str]:
    return (
        created_at,
        role,
        author,
        hashlib.sha256(content.encode("utf-8", errors="replace")).hexdigest(),
    )


def message_merge_fingerprint(message: Dict[str, object]) -> Tuple[int, Optional[int], str, Optional[str], str]:
    return (
        int(message["idx"]),
        message["created_at"],
        str(message["role"]),
        message["author"],
        hashlib.sha256(str(message["content"]).encode("utf-8", errors="replace")).hexdigest(),
    )


def load_existing_message_state(
    conn: sqlite3.Connection,
    conversation_id: int,
) -> Tuple[Dict[int, Tuple[int, Optional[int], str, Optional[str], str]], set]:
    by_idx: Dict[int, Tuple[int, Optional[int], str, Optional[str], str]] = {}
    replay = set()
    for row in conn.execute(
        """
        SELECT idx, role, author, created_at, content
        FROM messages
        WHERE conversation_id = ?
        ORDER BY idx, id
        """,
        (conversation_id,),
    ):
        merge_fp = canonical_message_fingerprint(row)
        by_idx[int(row["idx"])] = merge_fp
        replay.add(
            canonical_replay_fingerprint(
                row["created_at"],
                str(row["role"]),
                row["author"],
                str(row["content"] or ""),
            )
        )
    return by_idx, replay


def open_canonical_rw(path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(path, timeout=30.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA busy_timeout = 30000")
    return conn


def ensure_meta_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS meta(
            key TEXT PRIMARY KEY,
            value TEXT
        )
        """
    )


def ensure_source(conn: sqlite3.Connection, source_id: str) -> None:
    stamp = now_ms()
    conn.execute(
        """
        INSERT INTO sources(id, kind, host_label, machine_id, platform, config_json, created_at, updated_at)
        VALUES(?, 'local', NULL, NULL, NULL, NULL, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            kind = excluded.kind,
            updated_at = excluded.updated_at
        """,
        (source_id, stamp, stamp),
    )


def ensure_agent(conn: sqlite3.Connection, slug: str) -> int:
    row = conn.execute("SELECT id FROM agents WHERE slug = ? LIMIT 1", (slug,)).fetchone()
    if row is not None:
        return int(row["id"])
    stamp = now_ms()
    cursor = conn.execute(
        """
        INSERT INTO agents(slug, name, version, kind, created_at, updated_at)
        VALUES(?, ?, NULL, 'cli', ?, ?)
        """,
        (slug, slug, stamp, stamp),
    )
    return int(cursor.lastrowid)


def find_agent_id(conn: sqlite3.Connection, slug: str) -> Optional[int]:
    row = conn.execute("SELECT id FROM agents WHERE slug = ? LIMIT 1", (slug,)).fetchone()
    return None if row is None else int(row["id"])


def ensure_workspace(
    conn: sqlite3.Connection,
    workspace_cache: Dict[str, int],
    workspace_path: Optional[str],
) -> Optional[int]:
    if not workspace_path:
        return None
    cached = workspace_cache.get(workspace_path)
    if cached is not None:
        return cached
    conn.execute(
        """
        INSERT INTO workspaces(path, display_name)
        VALUES(?, ?)
        ON CONFLICT(path) DO UPDATE SET
            display_name = COALESCE(workspaces.display_name, excluded.display_name)
        """,
        (workspace_path, workspace_path),
    )
    row = conn.execute(
        "SELECT id FROM workspaces WHERE path = ? LIMIT 1",
        (workspace_path,),
    ).fetchone()
    workspace_id = int(row["id"])
    workspace_cache[workspace_path] = workspace_id
    return workspace_id


def build_canonical_codex_index(
    conn: sqlite3.Connection,
    agent_id: Optional[int],
) -> Tuple[int, Dict[str, int], Dict[str, Dict[str, object]], Dict[str, Dict[str, object]]]:
    workspace_cache = {
        str(row["path"]): int(row["id"])
        for row in conn.execute("SELECT id, path FROM workspaces")
    }
    by_path: Dict[str, Dict[str, object]] = {}
    by_external: Dict[str, Dict[str, object]] = {}
    if agent_id is None:
        return -1, workspace_cache, by_path, by_external
    for row in conn.execute(
        """
        WITH msg_counts AS (
            SELECT conversation_id, COUNT(*) AS message_count
            FROM messages
            GROUP BY conversation_id
        )
        SELECT
            c.id,
            c.external_id,
            c.source_path,
            c.started_at,
            c.ended_at,
            c.title,
            c.workspace_id,
            w.path AS workspace_path,
            c.metadata_json,
            c.total_input_tokens,
            c.total_output_tokens,
            c.grand_total_tokens,
            c.user_message_count,
            c.assistant_message_count,
            COALESCE(msg_counts.message_count, 0) AS message_count
        FROM conversations c
        LEFT JOIN workspaces w ON w.id = c.workspace_id
        LEFT JOIN msg_counts ON msg_counts.conversation_id = c.id
        WHERE c.agent_id = ?
        """,
        (agent_id,),
    ):
        entry = {
            "id": int(row["id"]),
            "external_id": row["external_id"],
            "source_path": str(row["source_path"]),
            "started_at": row["started_at"],
            "ended_at": row["ended_at"],
            "title": row["title"],
            "workspace_id": row["workspace_id"],
            "workspace_path": row["workspace_path"],
            "metadata_json": row["metadata_json"],
            "message_count": int(row["message_count"]),
        }
        by_path[str(row["source_path"])] = entry
        if row["external_id"] is not None:
            by_external[str(row["external_id"])] = entry
    return agent_id, workspace_cache, by_path, by_external


def load_thread_fallbacks(state_db_path: Optional[Path]) -> Dict[str, Dict[str, object]]:
    if state_db_path is None or not state_db_path.exists():
        return {}

    conn = sqlite3.connect(state_db_path, timeout=30.0)
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name='threads' LIMIT 1"
        ).fetchone()
        if row is None:
            return {}

        fallback: Dict[str, Dict[str, object]] = {}
        for thread in conn.execute(
            """
            SELECT rollout_path, created_at, updated_at, cwd, title, first_user_message, model
            FROM threads
            WHERE rollout_path IS NOT NULL AND rollout_path != ''
            """
        ):
            rollout_path = str(Path(thread["rollout_path"]).expanduser().resolve())
            fallback[rollout_path] = {
                "created_at": coerce_ts_ms(thread["created_at"]),
                "updated_at": coerce_ts_ms(thread["updated_at"]),
                "cwd": thread["cwd"],
                "title": thread["title"],
                "first_user_message": thread["first_user_message"],
                "model": thread["model"],
            }
        return fallback
    finally:
        conn.close()


def enumerate_rollout_files(sessions_root: Path) -> List[Path]:
    files = list(sessions_root.rglob("rollout-*.jsonl"))
    files.extend(sessions_root.rglob("rollout-*.json"))
    return sorted(path.resolve() for path in files if path.is_file())


def derive_external_id(path: Path, sessions_root: Path) -> str:
    try:
        relative = path.resolve().relative_to(sessions_root.resolve())
        return relative.with_suffix("").as_posix()
    except ValueError:
        return path.stem


def serialize_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def compute_message_stats(messages: Sequence[Dict[str, object]]) -> Dict[str, Optional[int]]:
    total_input_tokens = 0
    total_output_tokens = 0
    api_call_count = 0
    user_message_count = 0
    assistant_message_count = 0

    for message in messages:
        if message["role"] == "user":
            user_message_count += 1
        elif message["role"] == "assistant":
            assistant_message_count += 1

        extra = message["extra"]
        if not isinstance(extra, dict):
            continue
        cass = extra.get("cass")
        if not isinstance(cass, dict):
            continue
        token_usage = cass.get("token_usage")
        if not isinstance(token_usage, dict):
            continue
        api_call_count += 1
        input_tokens = coerce_ts_like_integer(token_usage.get("input_tokens"))
        output_tokens = coerce_ts_like_integer(token_usage.get("output_tokens"))
        if input_tokens is not None:
            total_input_tokens += input_tokens
        if output_tokens is not None:
            total_output_tokens += output_tokens

    return {
        "total_input_tokens": total_input_tokens or None,
        "total_output_tokens": total_output_tokens or None,
        "grand_total_tokens": (total_input_tokens + total_output_tokens) or None,
        "api_call_count": api_call_count,
        "tool_call_count": 0,
        "user_message_count": user_message_count,
        "assistant_message_count": assistant_message_count,
    }


def parse_rollout(path: Path, sessions_root: Path, thread_fallback: Optional[Dict[str, object]]) -> Dict[str, object]:
    ext = path.suffix.lower()
    compact_extras = False
    messages: List[Dict[str, object]] = []
    started_at: Optional[int] = None
    ended_at: Optional[int] = None
    workspace_path: Optional[str] = None
    parse_errors = 0
    saw_metadata = False

    if ext == ".jsonl":
        with path.open("r", encoding="utf-8", errors="replace") as handle:
            for line_number, line in enumerate(handle, start=1):
                if not line.strip():
                    continue
                try:
                    payload = json.loads(line)
                except json.JSONDecodeError:
                    parse_errors += 1
                    continue
                if not isinstance(payload, dict):
                    continue

                entry_type = payload.get("type")
                entry_payload = payload.get("payload")
                created_at = coerce_ts_ms(payload.get("timestamp"))

                if entry_type == "session_meta":
                    saw_metadata = True
                    if isinstance(entry_payload, dict) and isinstance(entry_payload.get("cwd"), str):
                        workspace_path = entry_payload["cwd"]
                    if created_at is None and isinstance(entry_payload, dict):
                        created_at = coerce_ts_ms(entry_payload.get("timestamp"))
                    started_at, ended_at = update_time_bounds(started_at, ended_at, created_at)
                    continue

                if entry_type == "response_item" and isinstance(entry_payload, dict):
                    role = entry_payload.get("role")
                    if not isinstance(role, str) or not role:
                        role = "agent"
                    content = flatten_content(entry_payload.get("content"))
                    if not content.strip():
                        continue
                    started_at, ended_at = update_time_bounds(started_at, ended_at, created_at)
                    messages.append(
                        {
                            "idx": 0,
                            "role": role,
                            "author": None,
                            "created_at": created_at,
                            "content": content,
                            "extra": maybe_compact_extra(path, payload, compact_extras),
                        }
                    )
                    continue

                if entry_type != "event_msg" or not isinstance(entry_payload, dict):
                    continue

                event_type = entry_payload.get("type")
                if event_type == "user_message":
                    text = entry_payload.get("message")
                    if isinstance(text, str) and text:
                        started_at, ended_at = update_time_bounds(started_at, ended_at, created_at)
                        messages.append(
                            {
                                "idx": 0,
                                "role": "user",
                                "author": None,
                                "created_at": created_at,
                                "content": text,
                                "extra": maybe_compact_extra(path, payload, compact_extras),
                            }
                        )
                elif event_type == "agent_reasoning":
                    text = entry_payload.get("text")
                    if isinstance(text, str) and text:
                        started_at, ended_at = update_time_bounds(started_at, ended_at, created_at)
                        messages.append(
                            {
                                "idx": 0,
                                "role": "assistant",
                                "author": "reasoning",
                                "created_at": created_at,
                                "content": text,
                                "extra": maybe_compact_extra(path, payload, compact_extras),
                            }
                        )
                elif event_type == "token_count":
                    token_usage = token_usage_from_payload(entry_payload)
                    if token_usage is not None:
                        attach_token_usage_to_latest_assistant(messages, token_usage)
    elif ext == ".json":
        with path.open("r", encoding="utf-8", errors="replace") as handle:
            try:
                payload = json.load(handle)
            except json.JSONDecodeError:
                payload = None
                parse_errors += 1

        if isinstance(payload, dict):
            saw_metadata = True
            session_obj = payload.get("session")
            if isinstance(session_obj, dict) and isinstance(session_obj.get("cwd"), str):
                workspace_path = session_obj["cwd"]

            items = payload.get("items")
            if isinstance(items, list):
                for item in items:
                    if not isinstance(item, dict):
                        continue
                    role = item.get("role")
                    if not isinstance(role, str) or not role:
                        role = "agent"
                    content = flatten_content(item.get("content"))
                    if not content.strip():
                        continue
                    created_at = coerce_ts_ms(item.get("timestamp"))
                    started_at, ended_at = update_time_bounds(started_at, ended_at, created_at)
                    messages.append(
                        {
                            "idx": 0,
                            "role": role,
                            "author": None,
                            "created_at": created_at,
                            "content": content,
                            "extra": maybe_compact_extra(path, item, compact_extras),
                        }
                    )

    if thread_fallback:
        saw_metadata = True
        if not workspace_path and isinstance(thread_fallback.get("cwd"), str):
            workspace_path = thread_fallback["cwd"]
        fallback_start = thread_fallback.get("created_at")
        fallback_end = thread_fallback.get("updated_at")
        if started_at is None and isinstance(fallback_start, int):
            started_at = fallback_start
        if ended_at is None and isinstance(fallback_end, int):
            ended_at = fallback_end
        if ended_at is None and started_at is not None:
            ended_at = started_at

    reindex_messages(messages)

    fallback_title = None
    if thread_fallback:
        if isinstance(thread_fallback.get("title"), str) and thread_fallback.get("title"):
            fallback_title = str(thread_fallback["title"])
        elif isinstance(thread_fallback.get("first_user_message"), str) and thread_fallback.get("first_user_message"):
            fallback_title = str(thread_fallback["first_user_message"])

    return {
        "external_id": derive_external_id(path, sessions_root),
        "source_path": str(path.resolve()),
        "title": derive_title(messages, fallback_title),
        "workspace_path": workspace_path,
        "started_at": started_at,
        "ended_at": ended_at,
        "messages": messages,
        "metadata_json": serialize_json(
            {
                "source": "rollout_json" if ext == ".json" else "rollout",
                "cass": {
                    "origin": {
                        "source_id": LOCAL_SOURCE_ID,
                        "kind": "local",
                        "host": None,
                    }
                },
            }
        ),
        "stats": compute_message_stats(messages),
        "parse_errors": parse_errors,
        "metadata_only": saw_metadata and not messages,
    }


def fast_path_unchanged(existing: Dict[str, object], parsed: Dict[str, object]) -> bool:
    if existing["message_count"] != len(parsed["messages"]):
        return False

    if parsed["workspace_path"] and not existing["workspace_path"]:
        return False
    if parsed["title"] and not existing["title"]:
        return False
    if parsed["started_at"] is not None and (
        existing["started_at"] is None or parsed["started_at"] < existing["started_at"]
    ):
        return False
    if parsed["ended_at"] is not None and (
        existing["ended_at"] is None or parsed["ended_at"] > existing["ended_at"]
    ):
        return False

    return True


def insert_message(
    conn: sqlite3.Connection,
    conversation_id: int,
    message: Dict[str, object],
) -> int:
    cursor = conn.execute(
        """
        INSERT INTO messages(
            conversation_id, idx, role, author, created_at, content, extra_json, extra_bin
        )
        VALUES(?, ?, ?, ?, ?, ?, ?, NULL)
        """,
        (
            conversation_id,
            message["idx"],
            message["role"],
            message["author"],
            message["created_at"],
            message["content"],
            serialize_json(message["extra"]),
        ),
    )
    return int(cursor.lastrowid)


def update_conversation_metadata(
    conn: sqlite3.Connection,
    conversation_id: int,
    parsed: Dict[str, object],
    workspace_id: Optional[int],
) -> None:
    stats = parsed["stats"]
    conn.execute(
        """
        UPDATE conversations
        SET
            workspace_id = COALESCE(workspace_id, ?),
            title = COALESCE(title, ?),
            started_at = CASE
                WHEN started_at IS NULL THEN ?
                WHEN ? IS NOT NULL AND started_at > ? THEN ?
                ELSE started_at
            END,
            ended_at = CASE
                WHEN ended_at IS NULL THEN ?
                WHEN ? IS NOT NULL AND ended_at < ? THEN ?
                ELSE ended_at
            END,
            metadata_json = COALESCE(metadata_json, ?),
            total_input_tokens = COALESCE(?, total_input_tokens),
            total_output_tokens = COALESCE(?, total_output_tokens),
            grand_total_tokens = COALESCE(?, grand_total_tokens),
            api_call_count = COALESCE(?, api_call_count),
            tool_call_count = COALESCE(?, tool_call_count),
            user_message_count = COALESCE(?, user_message_count),
            assistant_message_count = COALESCE(?, assistant_message_count)
        WHERE id = ?
        """,
        (
            workspace_id,
            parsed["title"],
            parsed["started_at"],
            parsed["started_at"],
            parsed["started_at"],
            parsed["started_at"],
            parsed["ended_at"],
            parsed["ended_at"],
            parsed["ended_at"],
            parsed["ended_at"],
            parsed["metadata_json"],
            stats["total_input_tokens"],
            stats["total_output_tokens"],
            stats["grand_total_tokens"],
            stats["api_call_count"],
            stats["tool_call_count"],
            stats["user_message_count"],
            stats["assistant_message_count"],
            conversation_id,
        ),
    )


def process_rollouts(args: argparse.Namespace) -> Dict[str, object]:
    canonical_path = Path(args.canonical_db).expanduser().resolve()
    sessions_root = Path(args.sessions_root).expanduser().resolve()
    state_db = Path(args.state_db).expanduser().resolve() if args.state_db else None

    if not sessions_root.exists():
        raise SystemExit(f"sessions root does not exist: {sessions_root}")

    conn = open_canonical_rw(canonical_path)
    if args.dry_run:
        agent_id = find_agent_id(conn, "codex")
    else:
        ensure_meta_table(conn)
        ensure_source(conn, LOCAL_SOURCE_ID)
        agent_id = ensure_agent(conn, "codex")
    agent_id, workspace_cache, by_path, by_external = build_canonical_codex_index(conn, agent_id)
    thread_fallbacks = load_thread_fallbacks(state_db)
    rollout_files = enumerate_rollout_files(sessions_root)
    if args.start_after:
        start_after = str(Path(args.start_after).expanduser().resolve())
        rollout_files = [path for path in rollout_files if str(path) > start_after]
    if args.max_files is not None:
        rollout_files = rollout_files[: args.max_files]

    stats = {
        "canonical_db": str(canonical_path),
        "sessions_root": str(sessions_root),
        "state_db": str(state_db) if state_db is not None and state_db.exists() else None,
        "dry_run": bool(args.dry_run),
        "thread_fallback_rows": len(thread_fallbacks),
        "candidate_files": len(rollout_files),
        "processed_files": 0,
        "parsed_files": 0,
        "parse_errors": 0,
        "empty_files_skipped": 0,
        "metadata_only_conversations": 0,
        "existing_conversations_examined": 0,
        "existing_conversations_unchanged": 0,
        "existing_conversations_updated": 0,
        "inserted_conversations": 0,
        "inserted_messages": 0,
        "message_idx_conflicts": 0,
        "skipped_same_idx_messages": 0,
        "skipped_replay_equivalent_messages": 0,
        "files_missing_from_canonical": 0,
        "source_path_matches": 0,
        "external_id_matches": 0,
        "started_at_ms": now_ms(),
    }

    processed_since_commit = 0
    if not args.dry_run:
        conn.commit()
        conn.execute("BEGIN")

    try:
        for path in rollout_files:
            stats["processed_files"] += 1
            if args.progress_every and stats["processed_files"] % args.progress_every == 0:
                print(
                    json.dumps(
                        {
                            "progress": {
                                "processed_files": stats["processed_files"],
                                "parsed_files": stats["parsed_files"],
                                "inserted_conversations": stats["inserted_conversations"],
                                "inserted_messages": stats["inserted_messages"],
                                "existing_conversations_updated": stats["existing_conversations_updated"],
                            }
                        },
                        sort_keys=True,
                    ),
                    file=sys.stderr,
                    flush=True,
                )

            source_path = str(path)
            parsed = parse_rollout(path, sessions_root, thread_fallbacks.get(source_path))
            stats["parse_errors"] += int(parsed["parse_errors"])

            if not parsed["messages"] and not parsed["metadata_only"]:
                stats["empty_files_skipped"] += 1
                continue

            stats["parsed_files"] += 1
            if parsed["metadata_only"]:
                stats["metadata_only_conversations"] += 1
            existing = by_path.get(source_path)
            if existing is not None:
                stats["source_path_matches"] += 1
            else:
                existing = by_external.get(str(parsed["external_id"]))
                if existing is not None:
                    stats["external_id_matches"] += 1

            workspace_id = ensure_workspace(conn, workspace_cache, parsed["workspace_path"]) if not args.dry_run else (
                workspace_cache.get(str(parsed["workspace_path"])) if parsed["workspace_path"] else None
            )

            if existing is None:
                stats["files_missing_from_canonical"] += 1
                if not args.dry_run:
                    cursor = conn.execute(
                        """
                        INSERT INTO conversations(
                            agent_id, workspace_id, source_id, external_id, title, source_path,
                            started_at, ended_at, approx_tokens, metadata_json, origin_host, metadata_bin,
                            total_input_tokens, total_output_tokens, total_cache_read_tokens,
                            total_cache_creation_tokens, grand_total_tokens, estimated_cost_usd,
                            primary_model, api_call_count, tool_call_count, user_message_count, assistant_message_count
                        )
                        VALUES(?, ?, ?, ?, ?, ?, ?, ?, NULL, ?, NULL, NULL, ?, ?, NULL, NULL, ?, NULL, NULL, ?, ?, ?, ?)
                        """,
                        (
                            agent_id,
                            workspace_id,
                            LOCAL_SOURCE_ID,
                            parsed["external_id"],
                            parsed["title"],
                            parsed["source_path"],
                            parsed["started_at"],
                            parsed["ended_at"],
                            parsed["metadata_json"],
                            parsed["stats"]["total_input_tokens"],
                            parsed["stats"]["total_output_tokens"],
                            parsed["stats"]["grand_total_tokens"],
                            parsed["stats"]["api_call_count"],
                            parsed["stats"]["tool_call_count"],
                            parsed["stats"]["user_message_count"],
                            parsed["stats"]["assistant_message_count"],
                        ),
                    )
                    conversation_id = int(cursor.lastrowid)
                    for message in parsed["messages"]:
                        insert_message(conn, conversation_id, message)
                        stats["inserted_messages"] += 1
                else:
                    conversation_id = -1
                    stats["inserted_messages"] += len(parsed["messages"])

                stats["inserted_conversations"] += 1
                entry = {
                    "id": conversation_id,
                    "external_id": parsed["external_id"],
                    "source_path": parsed["source_path"],
                    "started_at": parsed["started_at"],
                    "ended_at": parsed["ended_at"],
                    "title": parsed["title"],
                    "workspace_id": workspace_id,
                    "workspace_path": parsed["workspace_path"],
                    "metadata_json": parsed["metadata_json"],
                    "message_count": len(parsed["messages"]),
                }
                by_path[parsed["source_path"]] = entry
                by_external[str(parsed["external_id"])] = entry
            else:
                stats["existing_conversations_examined"] += 1
                if fast_path_unchanged(existing, parsed):
                    stats["existing_conversations_unchanged"] += 1
                else:
                    existing_by_idx, existing_replay = load_existing_message_state(conn, int(existing["id"]))
                    inserted_for_conv = 0
                    for message in parsed["messages"]:
                        idx = int(message["idx"])
                        merge_fp = message_merge_fingerprint(message)
                        replay_fp = canonical_replay_fingerprint(
                            message["created_at"],
                            str(message["role"]),
                            message["author"],
                            str(message["content"]),
                        )
                        existing_fp = existing_by_idx.get(idx)
                        if existing_fp is not None:
                            stats["skipped_same_idx_messages"] += 1
                            if existing_fp != merge_fp:
                                stats["message_idx_conflicts"] += 1
                            continue
                        if replay_fp in existing_replay:
                            stats["skipped_replay_equivalent_messages"] += 1
                            continue
                        if not args.dry_run:
                            insert_message(conn, int(existing["id"]), message)
                        inserted_for_conv += 1
                        stats["inserted_messages"] += 1
                        existing_by_idx[idx] = merge_fp
                        existing_replay.add(replay_fp)

                    if not args.dry_run:
                        update_conversation_metadata(conn, int(existing["id"]), parsed, workspace_id)

                    if inserted_for_conv > 0 or not fast_path_unchanged(existing, parsed):
                        stats["existing_conversations_updated"] += 1
                    else:
                        stats["existing_conversations_unchanged"] += 1

                    existing["message_count"] = max(int(existing["message_count"]), len(parsed["messages"]))
                    if existing["started_at"] is None or (
                        parsed["started_at"] is not None and parsed["started_at"] < existing["started_at"]
                    ):
                        existing["started_at"] = parsed["started_at"]
                    if existing["ended_at"] is None or (
                        parsed["ended_at"] is not None and parsed["ended_at"] > existing["ended_at"]
                    ):
                        existing["ended_at"] = parsed["ended_at"]
                    if not existing["title"] and parsed["title"]:
                        existing["title"] = parsed["title"]
                    if not existing["workspace_path"] and parsed["workspace_path"]:
                        existing["workspace_path"] = parsed["workspace_path"]
                        existing["workspace_id"] = workspace_id

            processed_since_commit += 1
            if not args.dry_run and processed_since_commit >= max(args.commit_every, 1):
                conn.commit()
                conn.execute("BEGIN")
                processed_since_commit = 0

        stats["completed_at_ms"] = now_ms()
        if not args.dry_run:
            ledger_key = (
                f"{args.meta_key_prefix}:"
                f"{hashlib.sha256(str(sessions_root).encode('utf-8')).hexdigest()}"
            )
            conn.execute(
                """
                INSERT INTO meta(key, value)
                VALUES(?, ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value
                """,
                (ledger_key, json.dumps(stats, sort_keys=True)),
            )
            conn.commit()
    finally:
        conn.close()

    return stats


def main() -> int:
    args = parse_args()
    stats = process_rollouts(args)
    print(json.dumps(stats, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
