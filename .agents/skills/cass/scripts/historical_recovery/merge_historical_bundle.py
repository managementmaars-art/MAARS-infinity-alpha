#!/usr/bin/env python3

import argparse
from collections import Counter
import hashlib
import json
import sqlite3
import sys
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple


DEFAULT_CANONICAL_DB = "/home/ubuntu/.local/share/coding-agent-search/agent_search.db"
SUMMARY_COLUMNS = (
    "total_input_tokens",
    "total_output_tokens",
    "total_cache_read_tokens",
    "total_cache_creation_tokens",
    "grand_total_tokens",
    "estimated_cost_usd",
    "primary_model",
    "api_call_count",
    "tool_call_count",
    "user_message_count",
    "assistant_message_count",
)
USER_ROLES = {"user"}
ASSISTANTISH_ROLES = {"assistant", "agent", "gemini"}
TOOLISH_CONTENT_TYPES = {"tool_use", "tool_call", "function_call", "computer_call"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Merge one historical SQLite bundle into the canonical cass DB."
    )
    parser.add_argument("source_db", help="Historical source bundle to read from.")
    parser.add_argument(
        "--canonical-db",
        default=DEFAULT_CANONICAL_DB,
        help=f"Canonical cass DB path. Default: {DEFAULT_CANONICAL_DB}",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Analyze deltas without modifying the canonical DB.",
    )
    parser.add_argument(
        "--start-source-row-id",
        type=int,
        default=0,
        help="Skip source conversations with id <= this value.",
    )
    parser.add_argument(
        "--max-conversations",
        type=int,
        default=None,
        help="Stop after this many source conversations.",
    )
    parser.add_argument(
        "--commit-every",
        type=int,
        default=25,
        help="Commit after this many source conversations in write mode.",
    )
    parser.add_argument(
        "--progress-every",
        type=int,
        default=500,
        help="Emit progress to stderr every N processed source conversations. Use 0 to disable.",
    )
    parser.add_argument(
        "--meta-key-prefix",
        default="historical_bundle_python_merge",
        help="Prefix for the meta ledger entry written after a successful merge.",
    )
    return parser.parse_args()


def now_ms() -> int:
    return int(time.time() * 1000)


def open_source_readonly(path: Path) -> sqlite3.Connection:
    uri = path.resolve().as_uri() + "?mode=ro"
    conn = sqlite3.connect(uri, uri=True, timeout=30.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA query_only = ON")
    conn.execute("PRAGMA writable_schema = ON")
    return conn


def open_canonical_rw(path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(path, timeout=30.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA busy_timeout = 30000")
    return conn


def get_table_columns(conn: sqlite3.Connection, table_name: str) -> Set[str]:
    return {
        str(row["name"])
        for row in conn.execute(f"PRAGMA table_info({table_name})")
        if row["name"] is not None
    }


def build_source_conversation_sql(columns: Set[str]) -> str:
    select_fields = [
        "c.id",
        "c.agent_id",
        "c.workspace_id",
        "c.source_id",
        "c.external_id",
        "c.title",
        "c.source_path",
        "c.started_at",
        "c.ended_at",
        "c.approx_tokens",
        "c.metadata_json",
        "c.origin_host",
        "c.metadata_bin",
    ]
    for column in SUMMARY_COLUMNS:
        if column in columns:
            select_fields.append(f"c.{column}")
        else:
            select_fields.append(f"NULL AS {column}")
    return f"""
        SELECT
            {", ".join(select_fields)}
        FROM conversations c
        WHERE c.id > ?
        ORDER BY c.id
    """


def content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()


def parse_json_dict(raw: Optional[str]) -> Optional[Dict[str, Any]]:
    if raw is None:
        return None
    text = raw.strip()
    if not text:
        return None
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return None
    if isinstance(parsed, dict):
        return parsed
    return None


def coerce_int(value: Any) -> Optional[int]:
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


def coerce_float(value: Any) -> Optional[float]:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        raw = value.strip()
        if not raw:
            return None
        try:
            return float(raw)
        except ValueError:
            return None
    return None


def preferred_model_from_metadata(conv_row: sqlite3.Row) -> Optional[str]:
    metadata = parse_json_dict(conv_row["metadata_json"])
    if metadata is None:
        return None
    candidates: List[Any] = [
        metadata.get("model"),
        metadata.get("primary_model"),
    ]
    cass = metadata.get("cass")
    if isinstance(cass, dict):
        candidates.extend([cass.get("model"), cass.get("primary_model")])
    for candidate in candidates:
        if isinstance(candidate, str) and candidate.strip():
            return candidate.strip()
    return None


def first_non_empty_text(*values: Any) -> Optional[str]:
    for value in values:
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def count_tool_items(items: Any) -> int:
    if not isinstance(items, list):
        return 0
    total = 0
    for item in items:
        if not isinstance(item, dict):
            continue
        item_type = item.get("type")
        if not isinstance(item_type, str):
            continue
        if item_type in TOOLISH_CONTENT_TYPES:
            total += 1
    return total


def extract_message_summary(
    conv_row: sqlite3.Row,
    agent_slug: str,
    source_messages: Sequence[sqlite3.Row],
) -> Dict[str, Any]:
    total_input_tokens = 0
    total_output_tokens = 0
    total_cache_read_tokens = 0
    total_cache_creation_tokens = 0
    grand_total_tokens = 0
    estimated_cost_usd = 0.0
    api_call_count = 0
    tool_call_count = 0
    user_message_count = 0
    assistant_message_count = 0
    saw_token_usage = False
    saw_tool_signal = False
    saw_cost = False
    model_candidates: Counter[str] = Counter()

    metadata_model = preferred_model_from_metadata(conv_row)
    if metadata_model is not None:
        model_candidates[metadata_model] += 1

    for message in source_messages:
        role = first_non_empty_text(message["role"])
        if role is not None:
            lowered_role = role.lower()
            if lowered_role in USER_ROLES:
                user_message_count += 1
            if lowered_role in ASSISTANTISH_ROLES:
                assistant_message_count += 1

        extra = parse_json_dict(message["extra_json"])
        if extra is None:
            continue

        model = first_non_empty_text(
            extra.get("model"),
            extra.get("primary_model"),
        )
        if model is None:
            nested_message = extra.get("message")
            if isinstance(nested_message, dict):
                model = first_non_empty_text(
                    nested_message.get("model"),
                    nested_message.get("primary_model"),
                )
        if model is None:
            payload = extra.get("payload")
            if isinstance(payload, dict):
                model = first_non_empty_text(
                    payload.get("model"),
                    payload.get("primary_model"),
                )
        if model is not None:
            model_candidates[model] += 1

        nested_message = extra.get("message")
        if isinstance(nested_message, dict):
            nested_tool_calls = count_tool_items(nested_message.get("content"))
            tool_call_count += nested_tool_calls
            if nested_tool_calls:
                saw_tool_signal = True

        gemini_tool_calls = extra.get("toolCalls")
        if isinstance(gemini_tool_calls, list):
            tool_call_count += len(gemini_tool_calls)
            saw_tool_signal = True

        cass = extra.get("cass")
        usage_obj: Optional[Dict[str, Any]] = None
        if isinstance(cass, dict) and isinstance(cass.get("token_usage"), dict):
            usage_obj = cass["token_usage"]
        elif isinstance(nested_message, dict) and isinstance(nested_message.get("usage"), dict):
            usage_obj = nested_message["usage"]
        elif isinstance(extra.get("tokens"), dict):
            usage_obj = extra["tokens"]

        if usage_obj is None:
            continue

        input_tokens = coerce_int(
            usage_obj.get("input_tokens", usage_obj.get("input"))
        )
        output_tokens = coerce_int(
            usage_obj.get("output_tokens", usage_obj.get("output", usage_obj.get("tokens")))
        )
        cache_read_tokens = coerce_int(
            usage_obj.get("cache_read_tokens", usage_obj.get("cache_read_input_tokens", usage_obj.get("cached")))
        )
        cache_creation_tokens = coerce_int(
            usage_obj.get("cache_creation_tokens", usage_obj.get("cache_creation_input_tokens"))
        )
        if cache_creation_tokens is None:
            cache_creation = usage_obj.get("cache_creation")
            if isinstance(cache_creation, dict):
                cache_creation_tokens = sum(
                    value
                    for value in (
                        coerce_int(cache_creation.get("ephemeral_5m_input_tokens")),
                        coerce_int(cache_creation.get("ephemeral_1h_input_tokens")),
                    )
                    if value is not None
                ) or None
        explicit_total = coerce_int(usage_obj.get("total_tokens", usage_obj.get("total")))
        estimated_cost = coerce_float(usage_obj.get("estimated_cost_usd"))

        usage_parts = [input_tokens, output_tokens, cache_read_tokens, cache_creation_tokens]
        if explicit_total is None:
            explicit_total = sum(value for value in usage_parts if value is not None) or None

        saw_usage = any(value is not None for value in usage_parts) or explicit_total is not None
        if not saw_usage:
            continue

        saw_token_usage = True
        api_call_count += 1
        if input_tokens is not None:
            total_input_tokens += input_tokens
        if output_tokens is not None:
            total_output_tokens += output_tokens
        if cache_read_tokens is not None:
            total_cache_read_tokens += cache_read_tokens
        if cache_creation_tokens is not None:
            total_cache_creation_tokens += cache_creation_tokens
        if explicit_total is not None:
            grand_total_tokens += explicit_total
        if estimated_cost is not None:
            estimated_cost_usd += estimated_cost
            saw_cost = True

        explicit_tool_calls = coerce_int(usage_obj.get("tool_call_count"))
        if explicit_tool_calls is not None:
            tool_call_count += explicit_tool_calls
            saw_tool_signal = True

    return {
        "total_input_tokens": total_input_tokens if saw_token_usage else None,
        "total_output_tokens": total_output_tokens if saw_token_usage else None,
        "total_cache_read_tokens": total_cache_read_tokens if saw_token_usage else None,
        "total_cache_creation_tokens": total_cache_creation_tokens if saw_token_usage else None,
        "grand_total_tokens": grand_total_tokens if saw_token_usage else None,
        "estimated_cost_usd": estimated_cost_usd if saw_cost else None,
        "primary_model": model_candidates.most_common(1)[0][0] if model_candidates else None,
        "api_call_count": api_call_count if saw_token_usage else None,
        "tool_call_count": tool_call_count if saw_tool_signal else None,
        "user_message_count": user_message_count,
        "assistant_message_count": assistant_message_count,
    }


def prefer_source_or_derived(existing: Any, derived: Any) -> Any:
    if existing is None:
        return derived
    if isinstance(existing, str):
        return existing if existing.strip() else derived
    if isinstance(existing, (int, float)) and existing == 0 and derived not in (None, 0):
        return derived
    return existing


def resolve_conversation_summary(
    conv_row: sqlite3.Row,
    agent_slug: str,
    source_messages: Sequence[sqlite3.Row],
) -> Dict[str, Any]:
    derived = extract_message_summary(conv_row, agent_slug, source_messages)
    return {
        column: prefer_source_or_derived(conv_row[column], derived[column])
        for column in SUMMARY_COLUMNS
    }


def message_merge_fingerprint(row: sqlite3.Row) -> Tuple[int, Optional[int], str, Optional[str], str]:
    return (
        int(row["idx"]),
        row["created_at"],
        row["role"],
        row["author"],
        content_hash(row["content"] or ""),
    )


def message_replay_fingerprint(row: sqlite3.Row) -> Tuple[Optional[int], str, Optional[str], str]:
    return (
        row["created_at"],
        row["role"],
        row["author"],
        content_hash(row["content"] or ""),
    )


def fetch_source_agents(conn: sqlite3.Connection) -> Dict[int, sqlite3.Row]:
    return {
        int(row["id"]): row
        for row in conn.execute(
            "SELECT id, slug, name, version, kind, created_at, updated_at FROM agents"
        )
    }


def fetch_source_workspaces(conn: sqlite3.Connection) -> Dict[int, sqlite3.Row]:
    return {
        int(row["id"]): row
        for row in conn.execute("SELECT id, path, display_name FROM workspaces")
    }


def fetch_source_sources(conn: sqlite3.Connection) -> Dict[str, sqlite3.Row]:
    return {
        str(row["id"]): row
        for row in conn.execute(
            "SELECT id, kind, host_label, machine_id, platform, config_json, created_at, updated_at FROM sources"
        )
    }


def ensure_agent(
    canon: sqlite3.Connection,
    agent_cache: Dict[str, int],
    agent_row: sqlite3.Row,
) -> int:
    slug = str(agent_row["slug"])
    cached = agent_cache.get(slug)
    if cached is not None:
        return cached
    canon.execute(
        """
        INSERT INTO agents(slug, name, version, kind, created_at, updated_at)
        VALUES(?, ?, ?, ?, ?, ?)
        ON CONFLICT(slug) DO UPDATE SET
            name = excluded.name,
            version = excluded.version,
            kind = excluded.kind,
            updated_at = excluded.updated_at
        """,
        (
            slug,
            agent_row["name"],
            agent_row["version"],
            agent_row["kind"],
            agent_row["created_at"],
            agent_row["updated_at"],
        ),
    )
    agent_id = canon.execute(
        "SELECT id FROM agents WHERE slug = ? LIMIT 1", (slug,)
    ).fetchone()[0]
    agent_cache[slug] = int(agent_id)
    return int(agent_id)


def ensure_workspace(
    canon: sqlite3.Connection,
    workspace_cache: Dict[str, int],
    workspace_row: Optional[sqlite3.Row],
) -> Optional[int]:
    if workspace_row is None:
        return None
    path = str(workspace_row["path"])
    cached = workspace_cache.get(path)
    if cached is not None:
        return cached
    canon.execute(
        """
        INSERT INTO workspaces(path, display_name)
        VALUES(?, ?)
        ON CONFLICT(path) DO UPDATE SET
            display_name = COALESCE(excluded.display_name, workspaces.display_name)
        """,
        (path, workspace_row["display_name"]),
    )
    workspace_id = canon.execute(
        "SELECT id FROM workspaces WHERE path = ? LIMIT 1", (path,)
    ).fetchone()[0]
    workspace_cache[path] = int(workspace_id)
    return int(workspace_id)


def ensure_source(
    canon: sqlite3.Connection,
    source_cache: Dict[str, bool],
    source_id: str,
    source_row: Optional[sqlite3.Row],
) -> None:
    if source_id in source_cache:
        return
    if source_row is None:
        stamp = now_ms()
        canon.execute(
            """
            INSERT INTO sources(id, kind, host_label, machine_id, platform, config_json, created_at, updated_at)
            VALUES(?, 'local', NULL, NULL, NULL, NULL, ?, ?)
            ON CONFLICT(id) DO NOTHING
            """,
            (source_id, stamp, stamp),
        )
    else:
        canon.execute(
            """
            INSERT INTO sources(id, kind, host_label, machine_id, platform, config_json, created_at, updated_at)
            VALUES(?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                kind = excluded.kind,
                host_label = COALESCE(excluded.host_label, sources.host_label),
                machine_id = COALESCE(excluded.machine_id, sources.machine_id),
                platform = COALESCE(excluded.platform, sources.platform),
                config_json = COALESCE(excluded.config_json, sources.config_json),
                updated_at = excluded.updated_at
            """,
            (
                source_id,
                source_row["kind"],
                source_row["host_label"],
                source_row["machine_id"],
                source_row["platform"],
                source_row["config_json"],
                source_row["created_at"],
                source_row["updated_at"],
            ),
        )
    source_cache[source_id] = True


def build_canonical_caches(
    canon: sqlite3.Connection,
) -> Tuple[Dict[str, int], Dict[str, int], Dict[str, bool], Dict[Tuple[str, str, str], int]]:
    agent_cache = {
        str(row["slug"]): int(row["id"])
        for row in canon.execute("SELECT id, slug FROM agents")
    }
    workspace_cache = {
        str(row["path"]): int(row["id"])
        for row in canon.execute("SELECT id, path FROM workspaces")
    }
    source_cache = {
        str(row["id"]): True
        for row in canon.execute("SELECT id FROM sources")
    }
    conversation_index: Dict[Tuple[str, str, str], int] = {}
    for row in canon.execute(
        """
        SELECT c.id, c.source_id, c.external_id, a.slug
        FROM conversations c
        JOIN agents a ON a.id = c.agent_id
        WHERE c.external_id IS NOT NULL
        """
    ):
        key = (str(row["source_id"]), str(row["slug"]), str(row["external_id"]))
        conversation_index[key] = int(row["id"])
    return agent_cache, workspace_cache, source_cache, conversation_index


def fetch_source_messages(conn: sqlite3.Connection, conversation_id: int) -> List[sqlite3.Row]:
    return list(
        conn.execute(
            """
            SELECT id, idx, role, author, created_at, content, extra_json, extra_bin
            FROM messages
            WHERE conversation_id = ?
            ORDER BY idx, id
            """,
            (conversation_id,),
        )
    )


def fetch_source_snippets(conn: sqlite3.Connection, source_message_ids: Sequence[int]) -> Dict[int, List[sqlite3.Row]]:
    if not source_message_ids:
        return {}
    placeholders = ",".join("?" for _ in source_message_ids)
    rows = list(
        conn.execute(
            f"""
            SELECT id, message_id, file_path, start_line, end_line, language, snippet_text
            FROM snippets
            WHERE message_id IN ({placeholders})
            ORDER BY id
            """,
            tuple(source_message_ids),
        )
    )
    grouped: Dict[int, List[sqlite3.Row]] = {}
    for row in rows:
        grouped.setdefault(int(row["message_id"]), []).append(row)
    return grouped


def load_existing_message_state(
    canon: sqlite3.Connection,
    conversation_id: int,
) -> Tuple[Dict[int, Tuple[int, Optional[int], str, Optional[str], str]], set]:
    by_idx: Dict[int, Tuple[int, Optional[int], str, Optional[str], str]] = {}
    replay = set()
    for row in canon.execute(
        """
        SELECT idx, role, author, created_at, content
        FROM messages
        WHERE conversation_id = ?
        ORDER BY idx, id
        """,
        (conversation_id,),
    ):
        fp = message_merge_fingerprint(row)
        by_idx[int(row["idx"])] = fp
        replay.add(message_replay_fingerprint(row))
    return by_idx, replay


def insert_snippets(
    canon: sqlite3.Connection,
    target_message_id: int,
    snippets: Sequence[sqlite3.Row],
) -> int:
    inserted = 0
    for snippet in snippets:
        canon.execute(
            """
            INSERT INTO snippets(message_id, file_path, start_line, end_line, language, snippet_text)
            VALUES(?, ?, ?, ?, ?, ?)
            """,
            (
                target_message_id,
                snippet["file_path"],
                snippet["start_line"],
                snippet["end_line"],
                snippet["language"],
                snippet["snippet_text"],
            ),
        )
        inserted += 1
    return inserted


def effective_started_at(conv_row: sqlite3.Row, source_messages: Sequence[sqlite3.Row]) -> Optional[int]:
    if conv_row["started_at"] is not None:
        return int(conv_row["started_at"])
    timestamps = [row["created_at"] for row in source_messages if row["created_at"] is not None]
    return min(timestamps) if timestamps else None


def process_bundle(args: argparse.Namespace) -> Dict[str, object]:
    source_path = Path(args.source_db).expanduser().resolve()
    canonical_path = Path(args.canonical_db).expanduser().resolve()

    source = open_source_readonly(source_path)
    canon = open_canonical_rw(canonical_path)

    source_agents = fetch_source_agents(source)
    source_workspaces = fetch_source_workspaces(source)
    source_sources = fetch_source_sources(source)
    (
        agent_cache,
        workspace_cache,
        source_cache,
        conversation_index,
    ) = build_canonical_caches(canon)

    stats = {
        "source_db": str(source_path),
        "canonical_db": str(canonical_path),
        "dry_run": bool(args.dry_run),
        "processed_conversations": 0,
        "inserted_conversations": 0,
        "matched_existing_conversations": 0,
        "inserted_messages": 0,
        "skipped_duplicate_messages_same_idx": 0,
        "skipped_replay_equivalent_messages": 0,
        "message_idx_conflicts": 0,
        "inserted_snippets": 0,
        "max_source_row_id_seen": 0,
        "started_at_ms": now_ms(),
    }

    if not args.dry_run:
        canon.execute("BEGIN")

    source_sql = build_source_conversation_sql(get_table_columns(source, "conversations"))

    processed_since_commit = 0

    try:
        for conv_row in source.execute(source_sql, (args.start_source_row_id,)):
            source_conv_id = int(conv_row["id"])
            if (
                args.max_conversations is not None
                and stats["processed_conversations"] >= args.max_conversations
            ):
                break
            stats["max_source_row_id_seen"] = source_conv_id
            stats["processed_conversations"] += 1
            if (
                args.progress_every
                and stats["processed_conversations"] % args.progress_every == 0
            ):
                print(
                    json.dumps(
                        {
                            "progress": {
                                "source_db": str(source_path),
                                "processed_conversations": stats["processed_conversations"],
                                "inserted_conversations": stats["inserted_conversations"],
                                "inserted_messages": stats["inserted_messages"],
                                "max_source_row_id_seen": stats["max_source_row_id_seen"],
                                "dry_run": bool(args.dry_run),
                            }
                        },
                        sort_keys=True,
                    ),
                    file=sys.stderr,
                    flush=True,
                )

            source_agent_row = source_agents[int(conv_row["agent_id"])]
            agent_slug = str(source_agent_row["slug"])
            source_id = str(conv_row["source_id"] or "local")
            external_id = conv_row["external_id"]

            source_messages = fetch_source_messages(source, source_conv_id)
            source_snippets = fetch_source_snippets(
                source,
                [int(row["id"]) for row in source_messages],
            )
            started_at = effective_started_at(conv_row, source_messages)
            resolved_summary = resolve_conversation_summary(
                conv_row,
                agent_slug,
                source_messages,
            )

            try:
                existing_conv_id: Optional[int] = None
                if external_id is not None:
                    existing_conv_id = conversation_index.get((source_id, agent_slug, str(external_id)))

                if existing_conv_id is None and external_id is None:
                    # Conservative fallback for legacy rows lacking external_id.
                    row = canon.execute(
                        """
                        SELECT c.id
                        FROM conversations c
                        JOIN agents a ON a.id = c.agent_id
                        WHERE c.source_id = ?
                          AND a.slug = ?
                          AND c.source_path = ?
                          AND (
                                (c.started_at IS NULL AND ? IS NULL)
                                OR c.started_at = ?
                              )
                        ORDER BY c.id
                        LIMIT 1
                        """,
                        (source_id, agent_slug, conv_row["source_path"], started_at, started_at),
                    ).fetchone()
                    if row is not None:
                        existing_conv_id = int(row["id"])

                if existing_conv_id is None:
                    if not args.dry_run:
                        ensure_source(canon, source_cache, source_id, source_sources.get(source_id))
                        canonical_agent_id = ensure_agent(canon, agent_cache, source_agent_row)
                        canonical_workspace_id = ensure_workspace(
                            canon,
                            workspace_cache,
                            source_workspaces.get(conv_row["workspace_id"])
                            if conv_row["workspace_id"] is not None
                            else None,
                        )
                        canon.execute(
                            """
                            INSERT INTO conversations(
                                agent_id, workspace_id, source_id, external_id, title, source_path,
                                started_at, ended_at, approx_tokens, metadata_json, origin_host, metadata_bin,
                                total_input_tokens, total_output_tokens, total_cache_read_tokens,
                                total_cache_creation_tokens, grand_total_tokens, estimated_cost_usd,
                                primary_model, api_call_count, tool_call_count, user_message_count, assistant_message_count
                            )
                            VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """,
                            (
                                canonical_agent_id,
                                canonical_workspace_id,
                                source_id,
                                external_id,
                                conv_row["title"],
                                conv_row["source_path"],
                                started_at,
                                conv_row["ended_at"],
                                conv_row["approx_tokens"],
                                conv_row["metadata_json"],
                                conv_row["origin_host"],
                                conv_row["metadata_bin"],
                                resolved_summary["total_input_tokens"],
                                resolved_summary["total_output_tokens"],
                                resolved_summary["total_cache_read_tokens"],
                                resolved_summary["total_cache_creation_tokens"],
                                resolved_summary["grand_total_tokens"],
                                resolved_summary["estimated_cost_usd"],
                                resolved_summary["primary_model"],
                                resolved_summary["api_call_count"],
                                resolved_summary["tool_call_count"],
                                resolved_summary["user_message_count"],
                                resolved_summary["assistant_message_count"],
                            ),
                        )
                        existing_conv_id = int(canon.execute("SELECT last_insert_rowid()").fetchone()[0])
                        if external_id is not None:
                            conversation_index[(source_id, agent_slug, str(external_id))] = existing_conv_id

                        for source_msg in source_messages:
                            canon.execute(
                                """
                                INSERT INTO messages(
                                    conversation_id, idx, role, author, created_at, content, extra_json, extra_bin
                                )
                                VALUES(?, ?, ?, ?, ?, ?, ?, ?)
                                """,
                                (
                                    existing_conv_id,
                                    source_msg["idx"],
                                    source_msg["role"],
                                    source_msg["author"],
                                    source_msg["created_at"],
                                    source_msg["content"],
                                    source_msg["extra_json"],
                                    source_msg["extra_bin"],
                                ),
                            )
                            target_message_id = int(
                                canon.execute("SELECT last_insert_rowid()").fetchone()[0]
                            )
                            stats["inserted_messages"] += 1
                            stats["inserted_snippets"] += insert_snippets(
                                canon,
                                target_message_id,
                                source_snippets.get(int(source_msg["id"]), []),
                            )
                    else:
                        stats["inserted_messages"] += len(source_messages)
                        stats["inserted_snippets"] += sum(len(v) for v in source_snippets.values())

                    stats["inserted_conversations"] += 1
                else:
                    stats["matched_existing_conversations"] += 1
                    existing_by_idx, existing_replay = load_existing_message_state(canon, existing_conv_id)
                    latest_end = None
                    for source_msg in source_messages:
                        merge_fp = message_merge_fingerprint(source_msg)
                        replay_fp = message_replay_fingerprint(source_msg)
                        idx = int(source_msg["idx"])
                        existing_fp = existing_by_idx.get(idx)
                        if existing_fp is not None:
                            if existing_fp != merge_fp:
                                stats["message_idx_conflicts"] += 1
                            stats["skipped_duplicate_messages_same_idx"] += 1
                            continue
                        if replay_fp in existing_replay:
                            stats["skipped_replay_equivalent_messages"] += 1
                            continue

                        if not args.dry_run:
                            canon.execute(
                                """
                                INSERT INTO messages(
                                    conversation_id, idx, role, author, created_at, content, extra_json, extra_bin
                                )
                                VALUES(?, ?, ?, ?, ?, ?, ?, ?)
                                """,
                                (
                                    existing_conv_id,
                                    source_msg["idx"],
                                    source_msg["role"],
                                    source_msg["author"],
                                    source_msg["created_at"],
                                    source_msg["content"],
                                    source_msg["extra_json"],
                                    source_msg["extra_bin"],
                                ),
                            )
                            target_message_id = int(
                                canon.execute("SELECT last_insert_rowid()").fetchone()[0]
                            )
                            stats["inserted_snippets"] += insert_snippets(
                                canon,
                                target_message_id,
                                source_snippets.get(int(source_msg["id"]), []),
                            )

                        stats["inserted_messages"] += 1
                        existing_by_idx[idx] = merge_fp
                        existing_replay.add(replay_fp)
                        if source_msg["created_at"] is not None:
                            latest_end = max(
                                latest_end if latest_end is not None else int(source_msg["created_at"]),
                                int(source_msg["created_at"]),
                            )

                    if not args.dry_run and latest_end is not None:
                        canon.execute(
                            """
                            UPDATE conversations
                            SET ended_at = CASE
                                WHEN ended_at IS NULL THEN ?
                                WHEN ended_at < ? THEN ?
                                ELSE ended_at
                            END
                            WHERE id = ?
                            """,
                            (latest_end, latest_end, latest_end, existing_conv_id),
                        )
            except sqlite3.DatabaseError as exc:
                raise sqlite3.DatabaseError(
                    f"{exc} | source_row_id={source_conv_id} agent={agent_slug} source_id={source_id} external_id={external_id!r} source_path={conv_row['source_path']!r}"
                ) from exc

            processed_since_commit += 1
            if not args.dry_run and processed_since_commit >= max(args.commit_every, 1):
                canon.commit()
                canon.execute("BEGIN")
                processed_since_commit = 0

        if not args.dry_run:
            bundle_hash = hashlib.sha256(str(source_path).encode("utf-8")).hexdigest()
            meta_key = f"{args.meta_key_prefix}:{bundle_hash}"
            stats["completed_at_ms"] = now_ms()
            canon.execute(
                "INSERT INTO meta(key, value) VALUES(?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value",
                (meta_key, json.dumps(stats, sort_keys=True)),
            )
            canon.commit()
        else:
            stats["completed_at_ms"] = now_ms()
    finally:
        source.close()
        canon.close()

    return stats


def main() -> int:
    args = parse_args()
    stats = process_bundle(args)
    print(json.dumps(stats, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
