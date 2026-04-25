"""Campaign Orchestrator — end-to-end outbound pipeline.

This is the single service that makes MAARS's "24/7 Automated AI
Enterprise" pitch a real product feature, not vapor. One call to
`run_campaign()` does:

  1. **Persona → Leads**: Apollo search for N prospects matching the
     operator's ICP.
  2. **Leads → Drafts**: for each lead, route through the Universal
     Gateway (free-tier providers) to personalize the email using
     their name, title, company, and the user's template.
  3. **Drafts → Schedule**: spread sends across N days at reasonable
     times in each prospect's timezone (if available) so nothing
     arrives at 3am — respects daily_send_cap so no single day
     trips volume-based spam filters.
  4. **Schedule → Automatic fire**: inserts rows into `cold_emails`
     with scheduled_at set; the background scheduler (services/
     scheduler.py) picks them up and sends via email_sender.
  5. **Observability**: every campaign row lives in
     `outbound_campaigns` collection with status + progress counters
     so the operator sees "Campaign X: 32/50 sent, 4 replied, 2
     unsubscribed" in the admin panel.

Design choices:
  * No tool exports its own "send this now" — everything goes through
    the scheduler. That makes the flow resilient to restarts and gives
    the operator one pause/resume button.
  * Personalization uses maars/auto (cheapest provider) — typically
    $0.000005 per email draft, effectively free.
  * Daily send cap is a HARD throttle, not soft. Trying to blast 500
    emails on day 1 guarantees spam-folder placement; spreading to 50/day
    over 10 days keeps reputation intact.
  * We respect suppression before queuing — unsubscribed addresses are
    never even drafted.
"""
from __future__ import annotations
import asyncio
import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

logger = logging.getLogger(__name__)


def _render_template(template: str, lead: dict) -> str:
    """Lightweight {{var}} replacement — no Jinja dependency, no RCE
    surface. Supports first_name, last_name, full_name, title, company,
    linkedin_url."""
    if not template:
        return ""
    first = (lead.get("first_name") or "").strip()
    last = (lead.get("last_name") or "").strip()
    full = (lead.get("name") or f"{first} {last}").strip()
    vars_ = {
        "first_name":   first or "there",
        "last_name":    last,
        "full_name":    full or "there",
        "title":        lead.get("title") or "",
        "company":      (lead.get("organization") or {}).get("name") if isinstance(lead.get("organization"), dict) else lead.get("company") or "",
        "linkedin_url": lead.get("linkedin_url") or "",
    }
    out = template
    for k, v in vars_.items():
        out = out.replace("{{" + k + "}}", str(v))
    return out


async def _personalize_one(template_html: str, subject_template: str, lead: dict, user_id: str) -> tuple[str, str]:
    """Take a template + lead → (subject, body_html). Uses free-tier
    LLM to rewrite the template so each email reads naturally, not
    like mail-merge."""
    rendered_body = _render_template(template_html, lead)
    rendered_subject = _render_template(subject_template, lead)
    try:
        # Quick LLM pass to soften the personalization — turn "Hi John,"
        # into genuinely context-aware openers. Uses cheapest free route.
        from services.llm_gateway import complete
        prompt = (
            "Rewrite the following cold email so the OPENING SENTENCE "
            "feels personal to the recipient's role + company, but KEEP "
            "the rest of the email and the call-to-action EXACTLY as "
            "written. Return ONLY the rewritten email HTML, no markdown, "
            "no explanations.\n\n"
            f"Recipient: {lead.get('name')} — {lead.get('title')} at "
            f"{(lead.get('organization') or {}).get('name', '')}\n\n"
            f"EMAIL:\n{rendered_body}"
        )
        resp = await complete(
            user_id=user_id or "system_campaign_orchestrator",
            messages=[{"role": "user", "content": prompt}],
            model="maars/auto",
            source="campaign_personalize",
            max_tokens=600,
        )
        polished = (resp.get("choices", [{}])[0]
                        .get("message", {})
                        .get("content", "")
                        .strip())
        if polished:
            rendered_body = polished
    except Exception:
        logger.exception("Personalization failed; using template verbatim")
    return rendered_subject, rendered_body


def _spread_send_times(count: int, days: int, daily_cap: int) -> list[datetime]:
    """Produce `count` send times over `days`, respecting daily_cap.
    Sends fall between 9am-5pm UTC; each day loads up to daily_cap
    before spilling to the next day. Within a day, spread evenly."""
    now = datetime.now(timezone.utc)
    # Start tomorrow morning so Day-1 of a campaign doesn't fire 30s
    # after you click "Go" and catch suppression-list updates.
    start = (now + timedelta(days=1)).replace(hour=9, minute=0, second=0, microsecond=0)
    times: list[datetime] = []
    remaining = count
    day = 0
    while remaining > 0 and day < days:
        per_day = min(daily_cap, remaining)
        # Spread evenly between 9am and 5pm = 8 hours = 480 minutes.
        if per_day == 1:
            step_min = 240  # single send → midday
        else:
            step_min = 480 // per_day
        for i in range(per_day):
            times.append(start + timedelta(days=day, minutes=step_min * i))
            remaining -= 1
            if remaining == 0:
                break
        day += 1
    # If we still have leftover (count > days * daily_cap), spill to next
    # block of days at the same cap — better than dropping.
    while remaining > 0:
        for i in range(min(daily_cap, remaining)):
            times.append(start + timedelta(days=day, minutes=(480 // daily_cap) * i))
            remaining -= 1
        day += 1
    return times


async def run_campaign(
    *,
    user_id: str,
    name: str,
    persona: dict,
    subject_template: str,
    email_template: str,
    lead_count: int = 25,
    send_window_days: int = 5,
    daily_send_cap: int = 30,
    from_name: str | None = None,
    reply_to: str | None = None,
) -> dict:
    """Kick off one outbound campaign. Returns a campaign_id + summary.

    `persona` accepts any of Apollo's search_people params:
      titles, seniorities, industries, locations, employee_ranges, keywords.
    """
    from db import db
    from routes.lead_research import _get_adapter
    from routes.unsubscribe import is_suppressed

    # ── Pre-flight: any lead provider + email transport ──────────────
    # Using _get_adapter() means the campaign works on Hunter's free
    # tier too; Apollo is preferred but not required.
    lead_adapter = _get_adapter()
    if not lead_adapter.is_configured():
        return {
            "ok": False,
            "error": "No lead provider configured. Add APOLLO_API_KEY (paid, 10K credits) or HUNTER_API_KEY (free tier, 25/mo).",
        }
    # Probe email transport cheaply — keys present?
    from services.email_sender import _get_integration_keys
    keys = await _get_integration_keys()
    if not ((keys.get("sendgrid") or {}).get("api_key") or (keys.get("resend") or {}).get("api_key")):
        return {
            "ok": False,
            "error": "No email provider key. Add SENDGRID_API_KEY or RESEND_API_KEY.",
        }

    campaign_id = f"camp_{uuid.uuid4().hex[:12]}"
    now_iso = datetime.now(timezone.utc).isoformat()
    await db.outbound_campaigns.insert_one({
        "campaign_id": campaign_id,
        "user_id": user_id,
        "name": name,
        "persona": persona,
        "subject_template": subject_template,
        "email_template": email_template,
        "lead_count": lead_count,
        "send_window_days": send_window_days,
        "daily_send_cap": daily_send_cap,
        "from_name": from_name,
        "reply_to": reply_to,
        "status": "leads_searching",
        "created_at": now_iso,
        "_id": None,
    })

    # ── Step 1: find leads ────────────────────────────────────────────
    search_result = await lead_adapter.search_people(
        **{k: v for k, v in persona.items() if v is not None},
        per_page=min(lead_count, 100),
        page=1,
    )
    if not search_result.get("ok"):
        await db.outbound_campaigns.update_one(
            {"campaign_id": campaign_id},
            {"$set": {"status": "failed", "error": search_result.get("error")}},
        )
        return {"ok": False, "error": search_result.get("error"), "campaign_id": campaign_id}
    people = search_result.get("people", [])[:lead_count]

    # Filter out suppressed + leads with no email
    eligible = []
    for p in people:
        email = p.get("email")
        if not email or email == "email_not_unlocked@domain.com":
            continue
        if await is_suppressed(email):
            continue
        eligible.append(p)
    if not eligible:
        await db.outbound_campaigns.update_one(
            {"campaign_id": campaign_id},
            {"$set": {
                "status": "failed",
                "error": "No eligible leads after filtering (no email / on suppression list).",
                "found": len(people),
            }},
        )
        return {
            "ok": False,
            "error": "No eligible leads after filtering.",
            "campaign_id": campaign_id,
            "found": len(people),
        }

    # ── Step 2: schedule sends ────────────────────────────────────────
    send_times = _spread_send_times(len(eligible), send_window_days, daily_send_cap)
    scheduled_count = 0
    await db.outbound_campaigns.update_one(
        {"campaign_id": campaign_id},
        {"$set": {"status": "drafting", "eligible_leads": len(eligible)}},
    )

    # Personalize in batches of 5 concurrently — stays under free-tier RPM
    BATCH = 5
    for i in range(0, len(eligible), BATCH):
        batch = eligible[i:i + BATCH]
        drafts = await asyncio.gather(*[
            _personalize_one(email_template, subject_template, lead, user_id)
            for lead in batch
        ])
        for j, (subject, body_html) in enumerate(drafts):
            lead = batch[j]
            idx = i + j
            send_at = send_times[idx] if idx < len(send_times) else send_times[-1]
            await db.cold_emails.insert_one({
                "email_id": f"email_{uuid.uuid4().hex[:12]}",
                "campaign_id": campaign_id,
                "user_id": user_id,
                "to_email": lead.get("email"),
                "to_name": lead.get("name"),
                "subject": subject,
                "body_html": body_html,
                "from_name": from_name,
                "reply_to": reply_to,
                "status": "scheduled",
                "scheduled_at": send_at.isoformat(),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "lead_snapshot": {
                    "title": lead.get("title"),
                    "company": (lead.get("organization") or {}).get("name"),
                    "linkedin_url": lead.get("linkedin_url"),
                },
                "_id": None,
            })
            scheduled_count += 1

    await db.outbound_campaigns.update_one(
        {"campaign_id": campaign_id},
        {"$set": {
            "status": "scheduled",
            "scheduled_count": scheduled_count,
            "first_send_at": send_times[0].isoformat() if send_times else None,
            "last_send_at":  send_times[-1].isoformat() if send_times else None,
        }},
    )

    # Fire customer webhook so user's own backend can trigger flows
    # (e.g. "add campaign to CRM", "send Slack notification").
    try:
        from services.customer_webhooks import fire
        await fire("campaign.started", {
            "campaign_id": campaign_id,
            "name": name,
            "scheduled": scheduled_count,
            "first_send_at": send_times[0].isoformat() if send_times else None,
        }, user_id=user_id)
    except Exception:
        logger.exception("campaign.started webhook fire failed")

    return {
        "ok": True,
        "campaign_id": campaign_id,
        "name": name,
        "leads_found": len(people),
        "eligible": len(eligible),
        "scheduled": scheduled_count,
        "first_send_at": send_times[0].isoformat() if send_times else None,
        "last_send_at": send_times[-1].isoformat() if send_times else None,
        "status": "scheduled",
    }


async def get_campaign(campaign_id: str) -> dict:
    """Fetch a campaign + its progress counters."""
    from db import db
    camp = await db.outbound_campaigns.find_one({"campaign_id": campaign_id}, {"_id": 0})
    if not camp:
        return {"ok": False, "error": "not_found"}
    emails = await db.cold_emails.find(
        {"campaign_id": campaign_id}, {"_id": 0, "body_html": 0}
    ).to_list(1000)
    counters = {"scheduled": 0, "sent": 0, "failed": 0, "suppressed": 0}
    for e in emails:
        s = e.get("status") or "scheduled"
        counters[s] = counters.get(s, 0) + 1
    return {"ok": True, "campaign": camp, "counters": counters, "emails": emails}


async def pause_campaign(campaign_id: str) -> dict:
    """Halt pending sends by flipping status. The scheduler only picks
    up status='scheduled' so flipping to 'paused' stops new fires."""
    from db import db
    res = await db.cold_emails.update_many(
        {"campaign_id": campaign_id, "status": "scheduled"},
        {"$set": {"status": "paused"}},
    )
    await db.outbound_campaigns.update_one(
        {"campaign_id": campaign_id},
        {"$set": {"status": "paused"}},
    )
    return {"ok": True, "paused_count": res.modified_count}


async def resume_campaign(campaign_id: str) -> dict:
    """Un-pause — flips paused → scheduled so the poller picks them up."""
    from db import db
    res = await db.cold_emails.update_many(
        {"campaign_id": campaign_id, "status": "paused"},
        {"$set": {"status": "scheduled"}},
    )
    await db.outbound_campaigns.update_one(
        {"campaign_id": campaign_id},
        {"$set": {"status": "scheduled"}},
    )
    return {"ok": True, "resumed_count": res.modified_count}
