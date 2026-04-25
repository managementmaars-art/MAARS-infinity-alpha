"""Apollo.io lead research adapter.

Apollo is the cheapest high-quality B2B contact DB — $49/mo gets 10K
credits (1 credit = 1 person lookup with verified email). Alternative:
Hunter.io ($34/mo, smaller dataset) — keep this interface narrow so
we can swap without touching callers.

Setup:
  1. Sign up at apollo.io → Settings → API → Create API key.
  2. Add to .env:
        APOLLO_API_KEY=...
  3. (Optional) whitelist the calling IP in Apollo's security settings
     if you enable IP allow-listing.

Usage pattern: an agent receives "find me 50 SaaS founders in North America
with 10-50 employees" → maps to search_people() params → returns a list
of {name, title, email, company, linkedin_url} which the agent then feeds
into a cold-email campaign or LinkedIn outreach sequence.

Compliance: Apollo data IS public scraped. BUT cold-email CAN-SPAM /
GDPR / CASL compliance is on YOU — you must honor unsubscribe requests
and have a legitimate business interest basis (GDPR Art. 6(1)(f)) for
sending. The email_sender module stamps the required headers; that's
transport compliance. Basis-for-processing is legal territory.
"""
from __future__ import annotations
import logging
import os
from typing import Any

import httpx

logger = logging.getLogger(__name__)

_APOLLO_BASE = "https://api.apollo.io/v1"


def is_configured() -> bool:
    return bool(os.environ.get("APOLLO_API_KEY"))


async def _post(path: str, body: dict) -> dict:
    """Authenticated POST to Apollo. Normalizes the result shape."""
    key = os.environ.get("APOLLO_API_KEY")
    if not key:
        return {
            "ok": False,
            "error": "APOLLO_API_KEY not set. Sign up at apollo.io and add the key to .env.",
        }
    headers = {
        "Cache-Control": "no-cache",
        "Content-Type": "application/json",
        "X-Api-Key": key,
    }
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(f"{_APOLLO_BASE}{path}", headers=headers, json=body)
            if resp.status_code in (200, 201):
                return {"ok": True, **resp.json()}
            return {
                "ok": False,
                "error": f"Apollo {resp.status_code}: {resp.text[:300]}",
                "status_code": resp.status_code,
            }
    except httpx.TimeoutException:
        return {"ok": False, "error": "Apollo timeout (30s)"}
    except Exception as exc:
        logger.exception("Apollo call failed")
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}"}


async def search_people(
    *,
    titles: list[str] | None = None,
    seniorities: list[str] | None = None,
    industries: list[str] | None = None,
    locations: list[str] | None = None,
    employee_ranges: list[str] | None = None,
    keywords: str | None = None,
    page: int = 1,
    per_page: int = 25,
) -> dict:
    """Search Apollo's 275M+ person database.

    Common filter shapes:
      titles       = ["CEO", "Founder", "Head of Marketing"]
      seniorities  = ["founder", "c_suite", "vp"]      (Apollo-defined)
      industries   = ["software", "marketing services"]
      locations    = ["United States", "Canada"]        (country / state / city)
      employee_ranges = ["11,50", "51,200"]              (min,max)

    Returns Apollo's response under {"ok": True, "people": [...],
    "pagination": {...}}.
    """
    body: dict[str, Any] = {
        "page": page,
        "per_page": min(per_page, 100),
    }
    if titles:         body["person_titles"] = titles
    if seniorities:    body["person_seniorities"] = seniorities
    if industries:     body["organization_industries"] = industries
    if locations:      body["person_locations"] = locations
    if employee_ranges:body["organization_num_employees_ranges"] = employee_ranges
    if keywords:       body["q_keywords"] = keywords

    result = await _post("/mixed_people/search", body)
    if result.get("ok"):
        return {
            "ok": True,
            "people": result.get("people", []),
            "pagination": result.get("pagination", {}),
            "breadcrumbs": result.get("breadcrumbs", []),
        }
    return result


async def enrich_person(
    *,
    email: str | None = None,
    linkedin_url: str | None = None,
    first_name: str | None = None,
    last_name: str | None = None,
    organization_name: str | None = None,
) -> dict:
    """Look up one person by email OR LinkedIn URL OR name + company.
    Returns verified contact with job title, company, location, socials."""
    body: dict[str, Any] = {}
    if email:             body["email"] = email
    if linkedin_url:      body["linkedin_url"] = linkedin_url
    if first_name:        body["first_name"] = first_name
    if last_name:         body["last_name"] = last_name
    if organization_name: body["organization_name"] = organization_name
    if not body:
        return {"ok": False, "error": "Provide at least one of email / linkedin_url / name+company."}
    result = await _post("/people/match", body)
    if result.get("ok"):
        return {"ok": True, "person": result.get("person")}
    return result


async def search_organizations(
    *,
    industries: list[str] | None = None,
    locations: list[str] | None = None,
    employee_ranges: list[str] | None = None,
    technologies: list[str] | None = None,
    keywords: str | None = None,
    page: int = 1,
    per_page: int = 25,
) -> dict:
    """Search companies — useful for "find all B2B SaaS companies in NA
    running HubSpot" type queries. Returns list of orgs with website,
    employee count, industry, revenue band, tech stack."""
    body: dict[str, Any] = {"page": page, "per_page": min(per_page, 100)}
    if industries:         body["organization_industries"] = industries
    if locations:          body["organization_locations"] = locations
    if employee_ranges:    body["organization_num_employees_ranges"] = employee_ranges
    if technologies:       body["currently_using_any_of_technology_uids"] = technologies
    if keywords:           body["q_organization_keyword_tags"] = keywords
    result = await _post("/mixed_companies/search", body)
    if result.get("ok"):
        return {
            "ok": True,
            "organizations": result.get("organizations", []),
            "pagination": result.get("pagination", {}),
        }
    return result
