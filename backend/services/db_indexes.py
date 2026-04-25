"""MongoDB indexes for every hot-path collection.

At 100 users the dashboard is snappy. At 1K it starts dragging. At
10K — without indexes — every query scans the whole collection and
the app breaks. This module ensures the critical indexes exist on
startup; idempotent (Mongo silently skips if they already exist).

Call `ensure_indexes()` once from the FastAPI startup event.
"""
from __future__ import annotations
import logging

import pymongo

logger = logging.getLogger(__name__)


# Each entry: (collection, [(field|list_of_tuples, {kwargs}), ...])
# Use ASCENDING when filter equality; combine (field, DESC) when the
# query sorts on it. Compound indexes follow the ESR rule — Equality,
# Sort, Range — from left to right.
_INDEX_SPECS: list[tuple[str, list[tuple]]] = [
    # Hot read path: /me/usage filters by user_id + date
    ("gateway_usage_logs", [
        ([("user_id", 1), ("created_at", -1)], {}),
        ([("provider", 1)], {}),
        ([("source", 1)], {}),
    ]),
    # Legacy collection — same shape
    ("usage_logs", [
        ([("user_id", 1), ("created_at", -1)], {}),
        ([("provider", 1)], {}),
    ]),
    # Cold emails + scheduled queue (scheduler polls by status + time)
    ("cold_emails", [
        ([("status", 1), ("scheduled_at", 1)], {}),
        ([("user_id", 1), ("status", 1)], {}),
        ([("campaign_id", 1)], {}),
        ([("to_email", 1)], {}),
    ]),
    # Social posts + cold calls — same shape
    ("social_posts", [
        ([("status", 1), ("scheduled_at", 1)], {}),
        ([("user_id", 1)], {}),
    ]),
    ("cold_calls", [
        ([("status", 1), ("scheduled_at", 1)], {}),
        ([("user_id", 1)], {}),
    ]),
    ("social_schedule", [
        ([("status", 1), ("scheduled_at", 1)], {}),
        ([("user_id", 1)], {}),
    ]),
    # Wallets — unique user
    ("wallets", [
        ([("user_id", 1)], {"unique": True}),
    ]),
    # Ledger — user + time queries
    ("ledger_entries", [
        ([("user_id", 1), ("created_at", -1)], {}),
        ([("charge_id", 1)], {"sparse": True}),
    ]),
    # Campaigns
    ("outbound_campaigns", [
        ([("user_id", 1), ("created_at", -1)], {}),
        ([("status", 1)], {}),
    ]),
    # Referrals
    ("referral_codes", [
        ([("user_id", 1)], {"unique": True}),
        ([("code", 1)], {"unique": True}),
    ]),
    ("referral_attributions", [
        ([("referred_user_id", 1)], {"unique": True}),
        ([("code", 1)], {}),
    ]),
    # Webhooks — customer facing
    ("webhook_subscriptions", [
        ([("user_id", 1), ("status", 1)], {}),
        ([("events", 1), ("status", 1)], {}),
    ]),
    # Suppression list — hit on every email send
    ("email_suppressions", [
        ([("email", 1)], {"unique": True}),
    ]),
    # Email events — customer analytics
    ("email_events", [
        ([("email", 1), ("received_at", -1)], {}),
        ([("event_type", 1)], {}),
    ]),
    # Chats + messages
    ("chats", [
        ([("user_id", 1), ("updated_at", -1)], {}),
    ]),
    ("messages", [
        ([("chat_id", 1), ("created_at", 1)], {}),
        ([("user_id", 1), ("created_at", -1)], {}),
    ]),
    # Users — email lookup is the most common auth path
    ("users", [
        ([("email", 1)], {"unique": True}),
        ([("user_id", 1)], {"unique": True}),
    ]),
    # Subscriptions
    ("subscriptions", [
        ([("user_id", 1)], {}),
        ([("stripe_customer_id", 1)], {"sparse": True}),
    ]),
    # Team seats
    ("team_members", [
        ([("workspace_id", 1), ("user_id", 1)], {"unique": True}),
    ]),
    ("team_invites", [
        ([("token", 1)], {"unique": True}),
        ([("workspace_id", 1), ("status", 1)], {}),
    ]),
    # Workflows
    ("workflows", [
        ([("user_id", 1), ("updated_at", -1)], {}),
    ]),
    ("workflow_runs", [
        ([("workflow_id", 1), ("started_at", -1)], {}),
        ([("status", 1)], {}),
    ]),
    # Prompt library
    ("prompts_library", [
        ([("owner_user_id", 1), ("updated_at", -1)], {}),
        ([("workspace_id", 1), ("shared_with_workspace", 1)], {}),
    ]),
    # Lead lists
    ("imported_lead_lists", [
        ([("user_id", 1), ("imported_at", -1)], {}),
    ]),
    # Changelog
    ("changelog_entries", [
        ([("slug", 1)], {"unique": True}),
        ([("published", 1), ("published_at", -1)], {}),
    ]),
    # Notifications (new)
    ("notifications", [
        ([("user_id", 1), ("created_at", -1)], {}),
        ([("user_id", 1), ("read", 1)], {}),
    ]),
    # Customer webhooks delivery audit
    ("webhook_deliveries", [
        ([("subscription_id", 1), ("attempted_at", -1)], {}),
    ]),
    # Agents — hot read on every chat/workflow; agent_id used as FK everywhere
    # and is_infinity + network as filter fields in admin catalog + training.
    ("agents", [
        ([("agent_id", 1)], {"unique": True}),
        ([("is_infinity", 1)], {"sparse": True}),
        ([("network", 1)], {"sparse": True}),
        ([("role", 1)], {"sparse": True}),
    ]),
    # Gateway API keys — looked up by raw_key on every /v1/chat/completions
    # hit. Without a unique index this is an O(n) table scan per call.
    ("api_keys", [
        ([("key", 1)], {"unique": True}),
        ([("user_id", 1)], {"sparse": True}),
    ]),
    ("client_gateway_keys", [
        ([("key", 1)], {"unique": True}),
        ([("user_id", 1)], {"sparse": True}),
    ]),
    # Agent teams + campaigns + batch jobs — admin list/filter hot paths
    ("agent_teams", [
        ([("user_id", 1), ("created_at", -1)], {}),
        ([("agent_id", 1)], {"sparse": True}),
    ]),
    ("campaigns", [
        ([("user_id", 1), ("created_at", -1)], {}),
        ([("status", 1)], {"sparse": True}),
    ]),
    ("batch_jobs", [
        ([("user_id", 1), ("created_at", -1)], {}),
        ([("status", 1)], {"sparse": True}),
    ]),
    # Training / per-agent features added in recent audits
    ("agent_golden_examples", [
        ([("scope", 1), ("scope_value", 1)], {}),
        ([("example_id", 1)], {"unique": True}),
        ([("scope_value", 1), ("weight", -1)], {}),
    ]),
    ("agent_skill_cache", [
        ([("fingerprint", 1)], {"unique": True}),
        ([("agent_id", 1)], {}),
        ([("expires_at", 1)], {"expireAfterSeconds": 0}),
    ]),
    ("agent_training_queue", [
        ([("status", 1), ("queued_at", -1)], {}),
        ([("agent_id", 1)], {}),
    ]),
    ("agent_role_map", [
        ([("role_key", 1)], {"unique": True}),
    ]),
    # Integration driver audit + authority
    ("integration_action_log", [
        ([("user_id", 1), ("at", -1)], {}),
        ([("provider", 1), ("at", -1)], {}),
    ]),
    ("integration_authority", [
        ([("user_id", 1), ("agent_id", 1)], {"unique": True}),
    ]),
    # Gateway usage log — Financials + workflow stats read by timestamp range
    ("gateway_usage_logs", [
        ([("user_id", 1), ("timestamp", -1)], {}),
        ([("source", 1), ("timestamp", -1)], {}),
        ([("agent_id", 1), ("timestamp", -1)], {"sparse": True}),
    ]),
    # RAG — doc catalog + chunks (chunks queried by user_id + embedded flag)
    ("rag_docs", [
        ([("user_id", 1), ("created_at", -1)], {}),
        ([("doc_id", 1)], {"unique": True}),
    ]),
    ("rag_chunks", [
        ([("user_id", 1)], {}),
        ([("doc_id", 1), ("index", 1)], {}),
        ([("chunk_id", 1)], {"unique": True}),
    ]),
    # Memory graph — temporal facts
    ("memory_graph", [
        ([("user_id", 1), ("subject", 1), ("predicate", 1)], {}),
        ([("user_id", 1), ("valid_from", -1)], {}),
        ([("user_id", 1), ("topic", 1)], {}),
        ([("fact_id", 1)], {"unique": True}),
    ]),
    # SME corrections
    ("sme_corrections", [
        ([("status", 1), ("queued_at", -1)], {}),
        ([("user_id", 1), ("status", 1)], {}),
        ([("correction_id", 1)], {"unique": True}),
    ]),
    # Eval runs
    ("eval_runs", [
        ([("finished_at", -1)], {}),
        ([("run_id", 1)], {"unique": True}),
    ]),
    ("eval_golden_set", [
        ([("task", 1), ("created_at", -1)], {}),
        ([("item_id", 1)], {"unique": True}),
    ]),
    # MCP tokens
    ("mcp_tokens", [
        ([("token", 1)], {"unique": True}),
        ([("user_id", 1)], {}),
    ]),
    # Video ingest (Gemini File API)
    ("rag_videos", [
        ([("user_id", 1), ("uploaded_at", -1)], {}),
        ([("file_id", 1)], {}),
    ]),
]


async def ensure_indexes() -> dict:
    """Create every index defined above. Safe to re-run (Mongo is
    idempotent on index creation). Returns a summary dict."""
    from db import db
    created: list[str] = []
    skipped: list[str] = []
    errored: list[tuple[str, str]] = []
    for coll_name, specs in _INDEX_SPECS:
        for keys, kwargs in specs:
            # Build a stable index name so Mongo doesn't try to create
            # duplicates with slightly different auto-names.
            if isinstance(keys, list):
                name = "_".join(f"{k}_{v}" for k, v in keys)
            else:
                name = f"{keys}_1"
                keys = [(keys, pymongo.ASCENDING)]
            try:
                await db[coll_name].create_index(keys, name=name, **kwargs)
                created.append(f"{coll_name}.{name}")
            except pymongo.errors.OperationFailure as exc:
                # Most commonly: index exists with same name. Safe to ignore.
                if "already exists" in str(exc).lower() or exc.code == 85 or exc.code == 86:
                    skipped.append(f"{coll_name}.{name}")
                else:
                    errored.append((f"{coll_name}.{name}", str(exc)))
            except Exception as exc:
                errored.append((f"{coll_name}.{name}", f"{type(exc).__name__}: {exc}"))
    summary = {
        "created_or_existing": len(created) + len(skipped),
        "errored_count": len(errored),
        "sample_created": created[:10],
        "errors": errored[:10],
    }
    if errored:
        logger.warning("Index creation had %d errors: %s", len(errored), errored[:5])
    else:
        logger.info("Indexes ensured: %d total", summary["created_or_existing"])
    return summary
