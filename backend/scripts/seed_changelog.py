"""Seed real changelog entries.

Run: python backend/scripts/seed_changelog.py

Upserts by `slug` so re-running is idempotent. Entries reflect actual
shipped features — change when you ship something material. Each
row has: slug, title, summary, body (markdown), tag, published,
published_at.
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from datetime import datetime, timezone


ENTRIES = [
    {
        "slug": "2026-04-21-ops-admin-tab",
        "title": "New Operations admin tab + public status page",
        "summary": "One glance at scheduler health, queue depth, deliverability, and readiness — plus a public /api/status trust signal.",
        "body": (
            "The Operations tab in the admin panel now shows a live view of the background scheduler, active outbound campaigns with inline pause/resume, 30-day email deliverability (delivered / opened / clicked / bounced / complained), and product readiness (what's live vs. what's waiting on credentials).\n\n"
            "A public `/api/status` endpoint returns component-level health (database, automation engine, AI inference, email delivery) so you can link customers to proof that things are running."
        ),
        "tag": "feature",
        "published_at": "2026-04-21T20:00:00Z",
    },
    {
        "slug": "2026-04-21-customer-dashboard",
        "title": "Customer usage dashboard with savings estimate",
        "summary": "/me/usage shows credits, campaigns, emails, media, and a conservative 'what this would cost DIY' delta.",
        "body": (
            "Users now see their own activity in one endpoint: credits remaining, campaigns active, emails sent/opened/clicked, images + videos generated. "
            "A savings estimator compares what they paid MAARS vs industry per-unit pricing (conservative — we understate rather than inflate) so retention shows its receipts."
        ),
        "tag": "feature",
        "published_at": "2026-04-21T19:30:00Z",
    },
    {
        "slug": "2026-04-21-annual-billing",
        "title": "Annual plans with 20% discount + 2 bonus credit-months",
        "summary": "Every plan now has an annual option; /api/plans returns both monthly and annual with savings math baked in.",
        "body": (
            "Subscribing annually saves 20% on price and adds 2 extra months of credits beyond the 12× monthly total — so an annual commit is ~+37% more value at ~-20% spend. Stripe interval set to `year` when the annual path is chosen. Monthly remains the default."
        ),
        "tag": "feature",
        "published_at": "2026-04-21T19:00:00Z",
    },
    {
        "slug": "2026-04-21-gdpr-compliance",
        "title": "GDPR data export + deletion endpoints",
        "summary": "Art. 15 (access) and Art. 17 (erasure) are live. Privacy Policy, Terms of Service, and cookie consent banner all shipped.",
        "body": (
            "Users can download a complete JSON export of every record tied to their account and request deletion (30-day soft grace, with confirm-immediate option). "
            "New pages: `/privacy`, `/terms`. A GDPR-aware cookie consent banner appears for EU/UK visitors (detected via timezone) and persists choice. Transactional email flows (welcome, low-credit, payment success/failure, trial-ending, referral-reward, weekly digest) all live."
        ),
        "tag": "compliance",
        "published_at": "2026-04-21T18:00:00Z",
    },
    {
        "slug": "2026-04-21-prompt-library",
        "title": "Prompt library + CSV lead import",
        "summary": "Save, tag, and share prompts across a workspace. Upload any CSV of leads — we normalize Apollo / Hunter / Sales Nav / Seamless / Lusha headers.",
        "body": (
            "Prompts persist across sessions with use-count ranking so the most-effective ones bubble up. "
            "CSV import auto-detects common export headers (email, first/last name, title, company, LinkedIn, phone) and normalizes them into the same shape the campaign orchestrator consumes — so an imported list plugs directly into `run_campaign`."
        ),
        "tag": "feature",
        "published_at": "2026-04-21T17:30:00Z",
    },
    {
        "slug": "2026-04-21-workflow-builder",
        "title": "Workflow builder data model + execution queue",
        "summary": "Define multi-step automations (find leads → enrich → draft → wait → follow-up) as DAGs that the scheduler executes.",
        "body": (
            "Workflows are stored as typed-node graphs. Each node is an action (`search_leads`, `draft_email`, `send_email`, `wait`, etc.) with next-pointers that form a DAG. "
            "CRUD + run endpoints are live; execution engine walks the DAG through the same services agents already use. Full drag-drop UI lands next release."
        ),
        "tag": "feature",
        "published_at": "2026-04-21T17:00:00Z",
    },
    {
        "slug": "2026-04-21-more-free-providers",
        "title": "More free-first routing: Edge voice, Pollinations images, Deepgram STT, Brave search",
        "summary": "Premium quality on zero budget. 400+ neural voices, unlimited Flux images, 45K transcription minutes/mo, 2K search queries/mo.",
        "body": (
            "The router now defaults to the highest-quality free tier for each modality before paying anyone: Microsoft Edge neural voices (400+ premium options, $0), Pollinations Flux for images (unlimited, $0), Deepgram Nova-2 for transcription (45K minutes/mo free), Brave Search for web results (2K queries/mo free). Paid providers remain in the chain as quality-verified fallbacks."
        ),
        "tag": "improvement",
        "published_at": "2026-04-21T16:30:00Z",
    },
    {
        "slug": "2026-04-21-agent-quality",
        "title": "Agent quality upgrade + client-opacity rules",
        "summary": "Every agent now carries MAARS operating standards, tool-usage hints, and a strict rule against naming backend providers.",
        "body": (
            "A runtime prompt enhancer wraps each agent's base `system_prompt` with 6 mandatory sections: QUALITY FLOOR, BRAND VOICE, PLATFORM INTEGRITY, COMPLIANCE BASELINE, ESCALATE TO HUMAN, TOOL AWARENESS. Infrastructure provider names are stripped from every client-facing response (image, video, voice, leads, email). 29/29 quality tests passing; CI-ready."
        ),
        "tag": "improvement",
        "published_at": "2026-04-21T16:00:00Z",
    },
    {
        "slug": "2026-04-21-campaigns",
        "title": "Outbound campaigns — leads to inbox, fully automated",
        "summary": "Define a persona, MAARS finds prospects, drafts personalized emails, schedules across days, handles compliance.",
        "body": (
            "`POST /api/campaigns/run` takes a persona + subject/body template, pulls matching leads, personalizes via free-tier LLM, spreads sends across your `send_window_days` at your `daily_send_cap`, and the background scheduler fires them with compliance headers and suppression checks. Pause / resume any time. Customer-facing webhooks fire at `campaign.started`, `email.sent`, `email.bounced`, etc."
        ),
        "tag": "feature",
        "published_at": "2026-04-21T15:00:00Z",
    },
    {
        "slug": "2026-04-21-referrals-webhooks",
        "title": "Referral program + customer webhooks",
        "summary": "20% lifetime credit rewards for referrers + HMAC-signed event webhooks customers can subscribe their own backends to.",
        "body": (
            "Public referral links at `/r/<code>` with 30-day attribution cookies. Referrer gets 20% of the referred user's first payment as credits (operator-configurable). "
            "Customer webhooks: subscribe to any of 10 event types (`campaign.started`, `email.opened`, `credit.topped_up`, etc.) with HMAC-SHA256 signatures and 3-retry delivery — the standard SaaS integration surface."
        ),
        "tag": "feature",
        "published_at": "2026-04-21T14:00:00Z",
    },
]


async def main():
    from db import db
    count_new, count_updated = 0, 0
    for entry in ENTRIES:
        res = await db.changelog_entries.update_one(
            {"slug": entry["slug"]},
            {"$set": {
                **entry,
                "published": True,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }},
            upsert=True,
        )
        if res.upserted_id:
            count_new += 1
        elif res.modified_count:
            count_updated += 1
    print(f"Changelog seeded: {count_new} new, {count_updated} updated, {len(ENTRIES)} total.")


if __name__ == "__main__":
    asyncio.run(main())
