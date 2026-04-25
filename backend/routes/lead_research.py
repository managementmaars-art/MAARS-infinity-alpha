"""Lead-research endpoints — the API surface agents call to find prospects.

Today's provider: Apollo.io. The file is structured so swapping to
Hunter / Clearbit / ZoomInfo is a one-line change in _get_adapter().

All endpoints require auth + charge credits (1 credit per person returned,
so a "find 25 SaaS CEOs" call = 25 credits). That cost is logged to
gateway_usage_logs with source="lead_research" so the operator sees
lead-gen spend alongside LLM spend in the Universal Gateway dashboard.
"""
from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from auth import get_current_user
from models.schemas import User

router = APIRouter()


def _get_adapter():
    """Return the native BrowserAgent-powered lead research adapter.

    By design there is NO fallback to Apollo / Hunter. MAARS runs its
    own scrape via Playwright against LinkedIn Sales Navigator, the
    LinkedIn public people-search, and Google-indexed LinkedIn
    profiles. Zero external provider spend.

    Three sourcing strategies live inside the native adapter itself
    and are tried in order per request — that's internal resilience,
    not a fallback to paid services.
    """
    from services.lead_research import native
    return native


class PeopleSearch(BaseModel):
    titles: list[str] | None = None
    seniorities: list[str] | None = None
    industries: list[str] | None = None
    locations: list[str] | None = None
    employee_ranges: list[str] | None = None
    keywords: str | None = None
    page: int = 1
    per_page: int = 25


class OrgSearch(BaseModel):
    industries: list[str] | None = None
    locations: list[str] | None = None
    employee_ranges: list[str] | None = None
    technologies: list[str] | None = None
    keywords: str | None = None
    page: int = 1
    per_page: int = 25


class EnrichRequest(BaseModel):
    email: str | None = None
    linkedin_url: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    organization_name: str | None = None


@router.get("/leads/status")
async def leads_status(_: User = Depends(get_current_user)):
    """Is the MAARS lead-research engine configured? Clients hit this
    before showing the 'Find Leads' UI.

    Response is brand-neutral — never reveals Apollo/Hunter/whoever is
    the backend. Clients see only 'ready' / 'not ready'."""
    adapter = _get_adapter()
    return {
        "engine": "maars_leads",
        "ready": adapter.is_configured(),
    }


def _scrub_lead_result(result: dict) -> dict:
    """Strip provider-identifying fields from any adapter response
    before returning to a client. Keeps every business field (names,
    emails, titles, companies) untouched — just removes the metadata
    that would reveal Apollo vs Hunter vs future providers."""
    from shared.response_scrubber import scrub
    # The "breadcrumbs" + "pagination" + optional "status_code" are the
    # adapter-identifying fields. Strip them, keep the rest.
    if not isinstance(result, dict):
        return result
    cleaned = {k: v for k, v in result.items() if k not in ("breadcrumbs", "status_code")}
    return scrub(cleaned)


@router.post("/leads/search-people")
async def leads_search_people(
    body: PeopleSearch,
    current_user: User = Depends(get_current_user),
):
    """Find people matching the filters through the MAARS lead engine.
    Each returned person = 1 credit."""
    adapter = _get_adapter()
    if not adapter.is_configured():
        raise HTTPException(503, "Lead research not configured")
    args = body.model_dump(exclude_none=True)
    # Map the route's per_page to the native adapter's page_size
    if "per_page" in args:
        args["page_size"] = args.pop("per_page")
    args.pop("page", None)  # native scraper doesn't paginate via int
    args.pop("employee_ranges", None)
    args["user_id"] = current_user.user_id
    result = await adapter.search_people(**args)
    if not result.get("ok"):
        # Surface a neutral error — never leak the backend's name
        raise HTTPException(502, "Lead search failed")
    return _scrub_lead_result(result)


@router.post("/leads/enrich")
async def leads_enrich(
    body: EnrichRequest,
    current_user: User = Depends(get_current_user),
):
    """Enrich one contact — takes email OR linkedin_url OR name+company."""
    adapter = _get_adapter()
    if not adapter.is_configured():
        raise HTTPException(503, "Lead research not configured")
    args = body.model_dump(exclude_none=True)
    args["user_id"] = current_user.user_id
    result = await adapter.enrich_person(**args)
    if not result.get("ok"):
        raise HTTPException(502, "Enrichment failed")
    return _scrub_lead_result(result)


@router.post("/leads/search-companies")
async def leads_search_companies(
    body: OrgSearch,
    current_user: User = Depends(get_current_user),
):
    """Find companies matching filters — tech stack, employee count, etc."""
    adapter = _get_adapter()
    if not adapter.is_configured():
        raise HTTPException(503, "Lead research not configured")
    args = body.model_dump(exclude_none=True)
    if "per_page" in args:
        args["page_size"] = args.pop("per_page")
    args.pop("page", None)
    args.pop("employee_ranges", None)
    args.pop("locations", None)
    args.pop("technologies", None)
    args.pop("keywords", None)  # fold into q if caller provides one
    args["user_id"] = current_user.user_id
    result = await adapter.search_organizations(**args)
    if not result.get("ok"):
        raise HTTPException(502, "Company search failed")
    return _scrub_lead_result(result)


class FunnelBody(BaseModel):
    """One-call funnel: search → personalize → schedule → send.

    search_filters : same filter shape as /leads/search-people
    name           : campaign name (required for audit trail)
    persona        : your company context for personalization
    subject_template : supports {first_name}, {company}, {title}
    email_template   : supports {first_name}, {company}, {title}, {industry}
    lead_count       : how many prospects to enroll (default 25)
    send_window_days : stagger sends across this many days (default 5)
    daily_send_cap   : max sends per day (default 30)
    """
    search_filters: dict
    name: str
    persona: dict = {}
    subject_template: str
    email_template: str
    lead_count: int = 25
    send_window_days: int = 5
    daily_send_cap: int = 30


@router.post("/leads/funnel")
async def leads_funnel(
    body: FunnelBody,
    current_user: User = Depends(get_current_user),
):
    """Single-call chain: find prospects via lead_research → personalize
    with LLM → schedule with the campaign orchestrator → return
    campaign_id. The scheduler drives actual sends.

    Replaces the three-step: /leads/search-people → (manual) →
    /campaigns/run.
    """
    adapter = _get_adapter()
    if not adapter.is_configured():
        raise HTTPException(503, "Lead research not configured")

    # Step 1: pull leads
    found = await adapter.search_people(**body.search_filters)
    if not found.get("ok"):
        raise HTTPException(502, "Lead search failed")
    leads = (found.get("data") or found.get("people") or found.get("leads") or [])[: body.lead_count]
    if not leads:
        return {"ok": False, "error": "no leads returned for those filters"}

    # Step 2 + 3: hand off to the campaign orchestrator. Its
    # run_campaign will personalize + schedule per its existing logic,
    # using the leads we pre-fetched rather than re-querying.
    from services import campaign_orchestrator
    try:
        result = await campaign_orchestrator.run_campaign(
            user_id=current_user.user_id,
            name=body.name,
            persona=body.persona,
            subject_template=body.subject_template,
            email_template=body.email_template,
            lead_count=body.lead_count,
            send_window_days=body.send_window_days,
            daily_send_cap=body.daily_send_cap,
            prefetched_leads=leads,   # allow orchestrator to skip its own search
        )
    except TypeError:
        # orchestrator doesn't yet accept prefetched_leads — it'll search again.
        result = await campaign_orchestrator.run_campaign(
            user_id=current_user.user_id,
            name=body.name,
            persona=body.persona,
            subject_template=body.subject_template,
            email_template=body.email_template,
            lead_count=body.lead_count,
            send_window_days=body.send_window_days,
            daily_send_cap=body.daily_send_cap,
        )

    if not result.get("ok"):
        raise HTTPException(400, result.get("error", "Campaign launch failed"))
    return {"ok": True, "leads_found": len(leads), **result}
