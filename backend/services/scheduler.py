"""Background scheduler — makes MAARS 24/7 actually work.

Before this module existed, every "scheduled post / email / call" stored
`scheduled_at` in MongoDB but nothing ever fired. Operator could build a
queue; it sat forever. This module runs a single async loop that:

  1. Polls `social_posts`, `cold_emails`, `cold_calls`, `social_schedule`
     every 30 seconds for rows where `scheduled_at <= now()` and
     `status == "scheduled"`.
  2. Atomically flips status → `"processing"` so two workers never race
     (uses Mongo `findOneAndUpdate` — single-process today, but the
     atomic update means we can add more workers later without code change).
  3. Dispatches to the right executor (social adapter / email adapter /
     Twilio). Failed dispatches go to status=`"failed"` with the error
     string so the operator can inspect via the same admin panel.
  4. Successful dispatches flip to `"sent"` / `"published"` with
     `executed_at` stamped.

Design notes:
  * APScheduler's AsyncIOScheduler is lightweight — one process, shares
    the FastAPI event loop. No Redis, no Celery, no worker pool to
    deploy. Good enough for tens of thousands of scheduled items; if
    volume ever requires distributed workers, swap to Celery + beat.
  * Poll interval 30s is a tradeoff: shorter = snappier firing, longer
    = less DB churn. 30s matches "normal business scheduling precision"
    (nobody cares if a 9:00am post fires at 9:00:15).
  * `jitter=5` on the interval spreads DB reads so if two backend
    instances ever run, they don't hammer the DB at the same millisecond.

To enable: `await start_scheduler()` in server.py's startup event.
To disable (e.g. in tests): set env SCHEDULER_DISABLED=1.
"""
from __future__ import annotations
import asyncio
import logging
import os
from datetime import datetime, timezone, timedelta
from typing import Any, Callable, Awaitable

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger(__name__)

_scheduler: AsyncIOScheduler | None = None

# Dispatch registry — each entry knows which Mongo collection to poll
# and which async function to call when a due row appears. The function
# receives the full row dict and returns a dict merged into the row's
# update (e.g. {"platform_id": "..."} for a twitter post id).
DispatchFn = Callable[[dict], Awaitable[dict]]


async def _dispatch_social_post(row: dict) -> dict:
    """Fire a scheduled social post through whichever adapter matches
    its platform. LinkedIn is wired (needs OAuth app + user consent);
    others return a clear 'not yet connected' so the operator sees
    exactly which integration to set up next."""
    platform = (row.get("platform") or "").lower()
    now = datetime.now(timezone.utc).isoformat()
    try:
        if platform == "linkedin":
            from services.social_adapters import linkedin
            result = await linkedin.post_text(
                user_id=row.get("user_id") or "",
                text=row.get("content") or row.get("text") or "",
                visibility=row.get("visibility") or "PUBLIC",
            )
            return {
                "status": "published" if result.get("ok") else "failed",
                "platform_post_id": result.get("post_id"),
                "error": result.get("error"),
                "executed_at": now,
            }
        if platform in ("twitter", "x"):
            return {
                "status": "failed",
                "error": "X (Twitter) adapter not yet wired. Needs Basic Developer tier ($200/mo).",
                "executed_at": now,
            }
        if platform in ("facebook", "instagram"):
            return {
                "status": "failed",
                "error": f"{platform} adapter not yet wired. Needs Meta Business verification + App Review.",
                "executed_at": now,
            }
        if platform == "tiktok":
            return {
                "status": "failed",
                "error": "TikTok adapter not yet wired. Apply at developers.tiktok.com.",
                "executed_at": now,
            }
        return {
            "status": "failed",
            "error": f"Unknown platform: {platform}",
            "executed_at": now,
        }
    except Exception as exc:
        logger.exception("Social post dispatch failed")
        return {
            "status": "failed",
            "error": f"{type(exc).__name__}: {exc}",
            "executed_at": now,
        }


async def _dispatch_cold_email(row: dict) -> dict:
    """Send a scheduled cold email. Fires customer webhook events
    (email.sent / email.bounced) after the send so subscribed customer
    backends can react in real time."""
    from services.email_sender import send_via_configured_provider
    body_html = row.get("body_html") or row.get("body") or ""
    try:
        result = await send_via_configured_provider(
            to=row.get("to_email"),
            subject=row.get("subject"),
            body=body_html,
            from_email=row.get("from_email"),
        )
        ok = bool(result.get("ok"))
        status = "sent" if ok else "failed"
        # Fire customer-facing webhook so the user's backend can react.
        try:
            from services.customer_webhooks import fire
            event = "email.sent" if ok else "email.bounced"
            await fire(event, {
                "email_id": row.get("email_id"),
                "campaign_id": row.get("campaign_id"),
                "to": row.get("to_email"),
                "subject": row.get("subject"),
                "error": result.get("error"),
            }, user_id=row.get("user_id"))
        except Exception:
            pass
        return {
            "status": status,
            "provider_message_id": result.get("message_id"),
            "error": result.get("error"),
            "executed_at": datetime.now(timezone.utc).isoformat(),
        }
    except ImportError:
        return {
            "status": "failed",
            "error": "Email sender not configured. Add SENDGRID_API_KEY or RESEND_API_KEY to .env.",
            "executed_at": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as exc:
        logger.exception("Cold email dispatch failed")
        return {
            "status": "failed",
            "error": f"{type(exc).__name__}: {exc}",
            "executed_at": datetime.now(timezone.utc).isoformat(),
        }


async def _dispatch_cold_call(row: dict) -> dict:
    """Fire a scheduled outbound call via Twilio. Needs TWILIO_ACCOUNT_SID
    + TWILIO_AUTH_TOKEN + TWILIO_FROM_NUMBER in env + A2P 10DLC
    registration for US destinations."""
    sid = os.environ.get("TWILIO_ACCOUNT_SID")
    tok = os.environ.get("TWILIO_AUTH_TOKEN")
    frm = os.environ.get("TWILIO_FROM_NUMBER")
    if not (sid and tok and frm):
        return {
            "status": "failed",
            "error": "Twilio not configured. Set TWILIO_ACCOUNT_SID + TWILIO_AUTH_TOKEN + TWILIO_FROM_NUMBER in .env.",
            "executed_at": datetime.now(timezone.utc).isoformat(),
        }
    try:
        import httpx
        url = f"https://api.twilio.com/2010-04-01/Accounts/{sid}/Calls.json"
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.post(
                url,
                auth=(sid, tok),
                data={
                    "To": row.get("to_number"),
                    "From": frm,
                    "Twiml": f"<Response><Say>{row.get('script', 'Hello from MAARS.')}</Say></Response>",
                },
            )
            if resp.status_code in (200, 201):
                body = resp.json()
                return {
                    "status": "initiated",
                    "twilio_sid": body.get("sid"),
                    "executed_at": datetime.now(timezone.utc).isoformat(),
                }
            return {
                "status": "failed",
                "error": f"Twilio {resp.status_code}: {resp.text[:200]}",
                "executed_at": datetime.now(timezone.utc).isoformat(),
            }
    except Exception as exc:
        logger.exception("Cold call dispatch failed")
        return {
            "status": "failed",
            "error": f"{type(exc).__name__}: {exc}",
            "executed_at": datetime.now(timezone.utc).isoformat(),
        }


async def _dispatch_schedule_item(row: dict) -> dict:
    """Unified schedule entry (from /social/schedule) — routes to the
    right dispatcher based on its `type` field."""
    t = (row.get("type") or "").lower()
    if t in ("post", "social", "social_post"):
        return await _dispatch_social_post(row)
    if t in ("email", "cold_email"):
        return await _dispatch_cold_email(row)
    if t in ("call", "cold_call"):
        return await _dispatch_cold_call(row)
    return {
        "status": "failed",
        "error": f"Unknown schedule type: {t}",
        "executed_at": datetime.now(timezone.utc).isoformat(),
    }


async def _dispatch_workflow_run(row: dict) -> dict:
    """Execute one workflow run. Walks the workflow's DAG from the
    first trigger node, firing each action node through the same
    services agents already use. Each node's output becomes input
    context for the next. No LLM orchestration layer — the DAG
    author specified the flow at design time."""
    from db import db
    run_id = row.get("run_id")
    workflow_id = row.get("workflow_id")
    wf = await db.workflows.find_one({"workflow_id": workflow_id})
    if not wf:
        return {"status": "failed", "error": "workflow_not_found",
                "executed_at": datetime.now(timezone.utc).isoformat()}

    nodes = {n["id"]: n for n in wf.get("nodes", [])}
    # Start node = any "trigger"-typed node. If none, first action node.
    start_ids = [n["id"] for n in wf.get("nodes", []) if n.get("type") == "trigger"]
    if not start_ids:
        start_ids = [wf["nodes"][0]["id"]] if wf.get("nodes") else []

    ctx: dict = dict(row.get("overrides") or {})
    results: list[dict] = []

    async def _execute_tool(tool: str, params: dict, ctx: dict) -> dict:
        """One tool call. Returns the dispatcher result + any side-output."""
        try:
            if tool == "search_leads":
                from routes.lead_research import _get_adapter
                adapter = _get_adapter()
                return await adapter.search_people(**params)
            if tool == "enrich_contact":
                from routes.lead_research import _get_adapter
                adapter = _get_adapter()
                return await adapter.enrich_person(**params)
            if tool == "run_campaign":
                from services.campaign_orchestrator import run_campaign
                return await run_campaign(user_id=row.get("user_id"), **params)
            if tool == "send_cold_email":
                from services.email_sender import send_email
                return await send_email(**params)
            if tool == "post_linkedin":
                from services.social_adapters import linkedin
                return await linkedin.post_text(row.get("user_id"), params.get("text", ""))
            if tool == "schedule_post":
                from db import db
                await db.social_posts.insert_one({
                    **params,
                    "user_id": row.get("user_id"),
                    "status": "scheduled",
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "_id": None,
                })
                return {"ok": True, "scheduled": True}
            if tool == "generate_image":
                from services.media_router import route_image
                img, meta = await route_image(**params)
                return {"ok": True, "bytes_len": len(img), "meta": meta}
            if tool == "enhance_prompt":
                from services.prompt_enhancer import enhance_prompt
                enhanced, m = await enhance_prompt(**params)
                return {"ok": True, "enhanced_prompt": enhanced}
            if tool == "wait":
                import asyncio
                await asyncio.sleep(min(int(params.get("seconds", 1)), 10))
                return {"ok": True}
            if tool == "webhook_out":
                import httpx
                async with httpx.AsyncClient(timeout=15) as c:
                    r = await c.post(params["url"], json=params.get("payload") or {})
                return {"ok": r.status_code < 400, "status_code": r.status_code}
            return {"ok": False, "error": f"unknown_tool:{tool}"}
        except Exception as exc:
            return {"ok": False, "error": f"{type(exc).__name__}: {exc}"}

    # Walk the DAG breadth-first. Hard cap at 25 nodes to prevent
    # accidental infinite loops (user-authored DAGs can have cycles).
    visited: set[str] = set()
    queue = list(start_ids)
    hops = 0
    while queue and hops < 25:
        node_id = queue.pop(0)
        if node_id in visited:
            continue
        visited.add(node_id)
        node = nodes.get(node_id)
        if not node:
            continue
        if node.get("type") == "action":
            tool_result = await _execute_tool(
                node.get("tool", ""),
                node.get("params") or {},
                ctx,
            )
            results.append({"node": node_id, "tool": node.get("tool"), "result": tool_result})
            # Pipe simple output fields into ctx for downstream nodes.
            if isinstance(tool_result, dict):
                if tool_result.get("enhanced_prompt"):
                    ctx["prompt"] = tool_result["enhanced_prompt"]
                if tool_result.get("people"):
                    ctx["leads"] = tool_result["people"]
        next_ids = node.get("next") or []
        for nid in next_ids:
            if nid and nid not in visited:
                queue.append(nid)
        hops += 1

    await db.workflow_runs.update_one(
        {"run_id": run_id},
        {"$set": {
            "status": "completed",
            "results": results,
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "hops": hops,
        }},
    )
    return {"status": "completed", "hops": hops,
            "executed_at": datetime.now(timezone.utc).isoformat()}


async def _dispatch_gdpr_purge(row: dict) -> dict:
    """Hard-purge a user whose deletion_scheduled_for has elapsed.

    This dispatcher is unusual: it doesn't read from a collection of
    rows — it runs as a sweep inside the poll tick. Safe to leave
    registered because _claim_and_dispatch below falls through cleanly
    when there's nothing due.
    """
    # Actual sweep happens in _poll_all_queues extension; this function
    # is just a placeholder so the registry can reference it.
    return {"status": "noop"}


async def _gdpr_purge_sweep() -> int:
    """Walk users whose deletion_scheduled_for is past and hard-purge
    them. Runs on each scheduler tick alongside the claim loops."""
    from db import db
    now_iso = datetime.now(timezone.utc).isoformat()
    cursor = db.users.find(
        {"status": "pending_deletion", "deletion_scheduled_for": {"$lte": now_iso}},
        {"_id": 0, "user_id": 1, "email": 1},
    )
    purged = 0
    child_collections = [
        "messages", "chats", "outbound_campaigns", "cold_emails",
        "cold_calls", "social_posts", "tasks", "referral_codes",
        "referral_clicks", "referral_attributions", "webhook_subscriptions",
        "webhook_deliveries", "gateway_usage_logs", "ledger_entries",
        "wallets", "subscriptions", "linkedin_tokens", "notifications",
    ]
    async for user in cursor:
        uid = user.get("user_id")
        if not uid:
            continue
        for coll in child_collections:
            try:
                await db[coll].delete_many({"user_id": uid})
            except Exception:
                pass
        await db.users.delete_one({"user_id": uid})
        purged += 1
    return purged


# (collection_name, dispatcher). Add entries here for any new scheduled
# resource — the polling loop picks them up automatically.
DISPATCH_REGISTRY: list[tuple[str, DispatchFn]] = [
    ("social_posts",     _dispatch_social_post),
    ("cold_emails",      _dispatch_cold_email),
    ("cold_calls",       _dispatch_cold_call),
    ("social_schedule",  _dispatch_schedule_item),
    ("workflow_runs",    _dispatch_workflow_run),
]


async def _claim_and_dispatch(collection_name: str, dispatcher: DispatchFn) -> int:
    """Scan one collection for due items, atomically claim them, dispatch,
    write back the result. Returns the number of items processed."""
    from db import db
    coll = db[collection_name]
    now_iso = datetime.now(timezone.utc).isoformat()

    # Different collections use different queued-status conventions:
    #   - scheduled_at-gated queues use status="scheduled"
    #   - workflow_runs use status="queued" (set at enqueue time, no
    #     scheduled_at since they fire asap on next tick)
    if collection_name == "workflow_runs":
        match_query: dict = {"status": "queued"}
    else:
        match_query = {"status": "scheduled", "scheduled_at": {"$lte": now_iso}}

    processed = 0
    # Atomic claim: flip status → processing so concurrent pollers can't
    # double-fire. findOneAndUpdate with filter on status is the
    # canonical Mongo pattern for work-queue semantics.
    while True:
        claimed = await coll.find_one_and_update(
            match_query,
            {"$set": {"status": "processing", "claimed_at": now_iso}},
            return_document=True,
        )
        if not claimed:
            return processed

        processed += 1
        result = await dispatcher(claimed)
        # Merge dispatcher's result back onto the row. Status comes from
        # dispatcher (sent / published / failed / initiated / completed).
        await coll.update_one(
            {"_id": claimed["_id"]},
            {"$set": result},
        )
        logger.info(
            "Scheduler dispatched %s → %s",
            collection_name,
            result.get("status"),
        )


async def _poll_all_queues() -> None:
    """One tick of the scheduler: fan out across every registered
    collection. Isolated in try/except so one broken collection can't
    kill the whole loop."""
    for coll_name, dispatcher in DISPATCH_REGISTRY:
        try:
            n = await _claim_and_dispatch(coll_name, dispatcher)
            if n:
                logger.info("Scheduler processed %d items from %s", n, coll_name)
        except Exception:
            logger.exception("Scheduler tick failed for %s", coll_name)
    # GDPR purge sweep — no queue, just a user-table scan for
    # deletion_scheduled_for <= now. Runs every tick so expired grace
    # periods are cleaned up within 30s of elapsing.
    try:
        n = await _gdpr_purge_sweep()
        if n:
            logger.info("Scheduler GDPR-purged %d users", n)
    except Exception:
        logger.exception("GDPR purge sweep failed")


async def start_scheduler() -> None:
    """Start the background polling loop. Idempotent — calling twice is
    a no-op. Controlled by SCHEDULER_DISABLED env for test/CI."""
    global _scheduler
    if os.environ.get("SCHEDULER_DISABLED") == "1":
        logger.info("Scheduler disabled via SCHEDULER_DISABLED=1")
        return
    if _scheduler and _scheduler.running:
        return
    _scheduler = AsyncIOScheduler(timezone="UTC")
    _scheduler.add_job(
        _poll_all_queues,
        trigger=IntervalTrigger(seconds=30, jitter=5),
        id="maars_queue_poller",
        max_instances=1,
        coalesce=True,
        next_run_time=datetime.now(timezone.utc),
    )

    # Gateway intelligence jobs. None of these fire provider calls —
    # they roll up existing gateway_usage_logs / shadow_calls into
    # in-memory state the router reads on every request.
    async def _rebuild_scorecards():
        try:
            from services import provider_scorecard
            n = await provider_scorecard.rebuild()
            logger.info("scorecards rebuilt: %d providers", len(n))
        except Exception as exc:
            logger.warning("scorecard rebuild failed: %s", exc)

    async def _rebuild_routing_table():
        try:
            from services import routellm_matrix
            r = await routellm_matrix.rebuild_routing_table()
            logger.info("routing_table rebuild: %s", r)
        except Exception as exc:
            logger.warning("routing_table rebuild failed: %s", exc)

    async def _drift_check():
        try:
            from services import drift_detector
            r = await drift_detector.run_all_checks()
            if r.get("quality_regressions") or r.get("cost_drifts"):
                logger.warning("drift alerts: %s", r)
        except Exception as exc:
            logger.warning("drift check failed: %s", exc)

    async def _cost_anomaly_scan():
        try:
            from services.costing import cost_anomaly
            alerts = await cost_anomaly.scan_all_active_users()
            if alerts:
                logger.warning("cost anomaly: %d user(s) flagged", len(alerts))
        except Exception as exc:
            logger.warning("cost_anomaly scan failed: %s", exc)

    async def _workflow_tick():
        try:
            from services.workflows import workflow_executor
            n = await workflow_executor.pick_and_run_queued()
            if n:
                logger.info("workflow_tick: started %d queued run(s)", n)
        except Exception as exc:
            logger.warning("workflow_tick failed: %s", exc)

    async def _workflow_scheduled_trigger():
        """Fire any scheduled workflow whose next-due time has passed."""
        try:
            from services.workflows import workflow_executor
            fired = await workflow_executor.trigger_scheduled_workflows()
            if fired:
                logger.info("workflow_scheduled: enqueued %d run(s)", fired)
        except Exception as exc:
            logger.warning("workflow_scheduled failed: %s", exc)

    async def _workflow_pollers():
        """HTTP-poll / RSS / IMAP / file-watch triggers."""
        try:
            from services.workflows import workflow_pollers
            counts = await workflow_pollers.run_all_polls()
            if any(counts.values()):
                logger.info("workflow_pollers: fired %s", counts)
        except Exception as exc:
            logger.warning("workflow_pollers failed: %s", exc)

    async def _auto_topup_sweep():
        """Off-session charge users whose balance fell below their
        configured threshold while they were idle."""
        try:
            from services.billing import auto_topup
            r = await auto_topup.sweep()
            if r.get("topped_up"):
                logger.info("auto_topup sweep: topped up %s of %s candidates",
                            r["topped_up"], r["candidates"])
        except Exception as exc:
            logger.warning("auto_topup sweep failed: %s", exc)

    async def _cost_automation_tick():
        """Daily P&L snapshot + low-balance alert check for operator-side
        providers (OpenAI, Anthropic, Fal, etc.). Writes to
        cost_automation_snapshots + cost_automation_alerts every 30 min."""
        try:
            from services.billing import cost_automation
            snap = await cost_automation.cost_automation_tick()
            if snap.get("low_balance_alerts"):
                logger.warning("cost_automation: %d provider(s) low-balance",
                               len(snap["low_balance_alerts"]))
        except Exception as exc:
            logger.warning("cost_automation tick failed: %s", exc)

    async def _token_quota_renewal_tick():
        """Hourly sweep: for every client whose period_end has passed,
        grant a fresh period's worth of credits (derived from their
        plan_id). Idempotent — safe to run hourly."""
        try:
            from services.billing import token_quota
            r = await token_quota.renew_expired_periods()
            if r.get("renewed"):
                logger.info("token_quota renewal: %d client(s) rolled to new period",
                            r["renewed"])
        except Exception as exc:
            logger.warning("token_quota renewal failed: %s", exc)

    async def _load_routing_table_at_boot():
        try:
            from services import routellm_matrix
            n = await routellm_matrix.load_from_db()
            logger.info("routing_table loaded %d clusters from Mongo", n)
        except Exception as exc:
            logger.info("routing_table boot load skipped: %s", exc)

    _scheduler.add_job(
        _rebuild_scorecards,
        trigger=IntervalTrigger(minutes=15, jitter=30),
        id="maars_scorecards",
        max_instances=1, coalesce=True,
        next_run_time=datetime.now(timezone.utc) + timedelta(seconds=20),
    )
    _scheduler.add_job(
        _rebuild_routing_table,
        trigger=IntervalTrigger(hours=1, jitter=60),
        id="maars_routing_table",
        max_instances=1, coalesce=True,
        next_run_time=datetime.now(timezone.utc) + timedelta(minutes=5),
    )
    _scheduler.add_job(
        _drift_check,
        trigger=IntervalTrigger(hours=6, jitter=120),
        id="maars_drift",
        max_instances=1, coalesce=True,
        next_run_time=datetime.now(timezone.utc) + timedelta(minutes=10),
    )
    _scheduler.add_job(
        _cost_anomaly_scan,
        trigger=IntervalTrigger(minutes=15, jitter=30),
        id="maars_cost_anomaly",
        max_instances=1, coalesce=True,
        next_run_time=datetime.now(timezone.utc) + timedelta(minutes=5),
    )
    _scheduler.add_job(
        _workflow_tick,
        trigger=IntervalTrigger(seconds=20, jitter=3),
        id="maars_workflow_tick",
        max_instances=1, coalesce=True,
        next_run_time=datetime.now(timezone.utc) + timedelta(seconds=5),
    )
    _scheduler.add_job(
        _workflow_scheduled_trigger,
        trigger=IntervalTrigger(seconds=60, jitter=5),
        id="maars_workflow_scheduled",
        max_instances=1, coalesce=True,
        next_run_time=datetime.now(timezone.utc) + timedelta(seconds=15),
    )
    _scheduler.add_job(
        _workflow_pollers,
        trigger=IntervalTrigger(seconds=60, jitter=10),
        id="maars_workflow_pollers",
        max_instances=1, coalesce=True,
        next_run_time=datetime.now(timezone.utc) + timedelta(seconds=25),
    )
    _scheduler.add_job(
        _auto_topup_sweep,
        trigger=IntervalTrigger(minutes=5, jitter=30),
        id="maars_auto_topup",
        max_instances=1, coalesce=True,
        next_run_time=datetime.now(timezone.utc) + timedelta(minutes=1),
    )
    _scheduler.add_job(
        _cost_automation_tick,
        trigger=IntervalTrigger(minutes=30, jitter=60),
        id="maars_cost_automation",
        max_instances=1, coalesce=True,
        next_run_time=datetime.now(timezone.utc) + timedelta(minutes=2),
    )
    _scheduler.add_job(
        _token_quota_renewal_tick,
        trigger=IntervalTrigger(hours=1, jitter=120),
        id="maars_token_quota_renewal",
        max_instances=1, coalesce=True,
        next_run_time=datetime.now(timezone.utc) + timedelta(minutes=3),
    )

    async def _integration_activity_poll():
        """Poll every connected integration for each user with credentials.
        Upserts inbound items (DMs, mentions, comments) into
        `integration_activity` so the /apps/{provider} pages render fresh."""
        try:
            from db import db
            from services import integration_activity
            # Users with at least one stored integration credential
            uids = await db.integration_credentials.distinct("user_id")
            if not uids:
                return
            total_new = 0
            for uid in uids[:100]:     # safety cap per tick
                try:
                    res = await integration_activity.poll_all_connected(uid)
                    total_new += int(res.get("total_new", 0))
                except Exception as exc:
                    logger.info("activity poll failed for %s: %s", uid, exc)
            if total_new:
                logger.info("integration_activity_poll: %d new items across %d users",
                            total_new, len(uids))
        except Exception as exc:
            logger.warning("integration_activity_poll failed: %s", exc)

    _scheduler.add_job(
        _integration_activity_poll,
        trigger=IntervalTrigger(minutes=5, jitter=30),
        id="maars_integration_activity_poll",
        max_instances=1, coalesce=True,
        next_run_time=datetime.now(timezone.utc) + timedelta(minutes=1),
    )

    async def _batch_flush():
        """Bundle queued batch-eligible jobs and submit to provider batch
        APIs at 50% off. Non-realtime work only."""
        try:
            from services import batch_dispatcher
            r = await batch_dispatcher.flush_queue()
            if r.get("jobs"):
                logger.info("batch_flush: %d jobs in %d submissions", r["jobs"], r["submitted"])
        except Exception as exc:
            logger.warning("batch_flush failed: %s", exc)

    async def _batch_poll():
        """Check outstanding batch submissions for completion."""
        try:
            from services import batch_dispatcher
            r = await batch_dispatcher.poll_submissions()
            if r.get("ingested"):
                logger.info("batch_poll: ingested %d completed jobs", r["ingested"])
        except Exception as exc:
            logger.warning("batch_poll failed: %s", exc)

    _scheduler.add_job(
        _batch_flush,
        trigger=IntervalTrigger(minutes=30, jitter=60),
        id="maars_batch_flush",
        max_instances=1, coalesce=True,
        next_run_time=datetime.now(timezone.utc) + timedelta(minutes=5),
    )
    _scheduler.add_job(
        _batch_poll,
        trigger=IntervalTrigger(minutes=15, jitter=30),
        id="maars_batch_poll",
        max_instances=1, coalesce=True,
        next_run_time=datetime.now(timezone.utc) + timedelta(minutes=10),
    )

    async def _agent_training_loop():
        """Daily pass: promote thumbed-up messages into golden examples
        (auto-queued for review; operator approves from the Training tab)
        and flag low-quality agents as retrain candidates for dspy."""
        try:
            from services.agents import agent_performance, golden_examples
            promotions = await agent_performance.top_promote_candidates(n=25, window_days=1)
            queued = 0
            from db import db
            for cand in promotions:
                # Skip if we already queued this message
                existing = await db.agent_training_queue.find_one({
                    "kind": "promote_golden",
                    "message_id": cand.get("message_id"),
                })
                if existing:
                    continue
                await db.agent_training_queue.insert_one({
                    "kind":        "promote_golden",
                    "status":      "pending_review",
                    "agent_id":    cand["agent_id"],
                    "message_id":  cand.get("message_id"),
                    "user_input":  cand.get("user_input"),
                    "ideal_output": cand.get("assistant_output"),
                    "source":      "thumbs_up",
                    "queued_at":   datetime.now(timezone.utc).isoformat(),
                })
                queued += 1
            losers = await agent_performance.retrain_candidates(
                score_floor=5.0, window_days=7, min_reviews=5,
            )
            retrain_queued = 0
            for r in losers:
                existing = await db.agent_training_queue.find_one({
                    "kind": "dspy_rewrite", "agent_id": r["agent_id"],
                    "status": "pending_review",
                })
                if existing:
                    continue
                await db.agent_training_queue.insert_one({
                    "kind":      "dspy_rewrite",
                    "status":    "pending_review",
                    "agent_id":  r["agent_id"],
                    "avg_score": (r.get("quality") or {}).get("avg_score"),
                    "reviews":   (r.get("quality") or {}).get("review_count"),
                    "queued_at": datetime.now(timezone.utc).isoformat(),
                })
                retrain_queued += 1
            logger.info(
                "agent_training_loop: queued %d promotions, %d retrains",
                queued, retrain_queued,
            )
        except Exception as exc:
            logger.warning("agent_training_loop failed: %s", exc)

    _scheduler.add_job(
        _agent_training_loop,
        trigger=IntervalTrigger(hours=24, jitter=300),
        id="maars_agent_training_loop",
        max_instances=1, coalesce=True,
        next_run_time=datetime.now(timezone.utc) + timedelta(minutes=15),
    )

    # One-shot at boot: load any previously-built routing table so the
    # router has data in-memory before the first rebuild runs.
    _scheduler.add_job(
        _load_routing_table_at_boot,
        trigger="date",
        id="maars_routing_boot_load",
        run_date=datetime.now(timezone.utc) + timedelta(seconds=10),
    )

    _scheduler.start()
    logger.info("MAARS scheduler started — queue poller every 30s + 4 gateway intelligence jobs (scorecards/routing-table/drift/cost-anomaly) + 2 workflow jobs (tick/scheduled-trigger)")


async def stop_scheduler() -> None:
    """Stop the scheduler cleanly. Called on FastAPI shutdown."""
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
        _scheduler = None
        logger.info("MAARS scheduler stopped")


def scheduler_status() -> dict[str, Any]:
    """Introspection for /admin/scheduler/status."""
    if not _scheduler:
        return {"running": False, "jobs": []}
    return {
        "running": _scheduler.running,
        "jobs": [
            {
                "id": job.id,
                "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
                "trigger": str(job.trigger),
            }
            for job in _scheduler.get_jobs()
        ],
    }
