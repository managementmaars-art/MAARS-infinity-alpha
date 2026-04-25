"""Hunter.io lead research adapter — free-tier fallback.

Hunter's free plan gives 25 email searches + 50 domain searches per
month. Apollo is the heavyweight ($49/mo, 10K credits); Hunter is the
zero-cost fallback that lets you prove out the campaign product
before committing to paid tools.

Setup:
  1. https://hunter.io/users/sign_in — free signup, no credit card.
  2. https://hunter.io/api-keys — copy your API key.
  3. Add to .env:
        HUNTER_API_KEY=...

Shape of our public surface matches apollo.py so the lead_research
router can swap providers via a single env flag (LEAD_PROVIDER=hunter).
"""
from __future__ import annotations
import logging
import os
from typing import Any

import httpx

logger = logging.getLogger(__name__)

_HUNTER_BASE = "https://api.hunter.io/v2"


def is_configured() -> bool:
    return bool(os.environ.get("HUNTER_API_KEY"))


async def _get(path: str, params: dict) -> dict:
    key = os.environ.get("HUNTER_API_KEY")
    if not key:
        return {
            "ok": False,
            "error": "HUNTER_API_KEY not set. Sign up at hunter.io (free 25/mo).",
        }
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(
                f"{_HUNTER_BASE}{path}",
                params={**params, "api_key": key},
            )
            if resp.status_code == 200:
                return {"ok": True, **resp.json()}
            return {
                "ok": False,
                "error": f"Hunter {resp.status_code}: {resp.text[:300]}",
                "status_code": resp.status_code,
            }
    except Exception as exc:
        logger.exception("Hunter call failed")
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}"}


def _normalize_hunter_person(h: dict, company_name: str | None = None) -> dict:
    """Map Hunter's person schema into the same shape Apollo returns so
    campaign_orchestrator and agents can consume either provider."""
    return {
        "email": h.get("value") or h.get("email"),
        "first_name": h.get("first_name"),
        "last_name":  h.get("last_name"),
        "name": f"{h.get('first_name') or ''} {h.get('last_name') or ''}".strip(),
        "title": h.get("position"),
        "linkedin_url": h.get("linkedin"),
        "twitter": h.get("twitter"),
        "phone": h.get("phone_number"),
        "confidence": h.get("confidence"),
        "seniority": h.get("seniority"),
        "department": h.get("department"),
        "organization": {"name": company_name} if company_name else {},
    }


async def search_people(
    *,
    titles: list[str] | None = None,
    seniorities: list[str] | None = None,
    industries: list[str] | None = None,
    locations: list[str] | None = None,
    employee_ranges: list[str] | None = None,
    keywords: str | None = None,
    domain: str | None = None,
    page: int = 1,
    per_page: int = 25,
) -> dict:
    """Hunter's domain-search = find all emails at one company.

    Usage pattern different from Apollo: Hunter works by DOMAIN. If the
    caller passes `keywords='stripe.com'` or `domain='stripe.com'` we
    pull all emails at that domain. Passing `titles` filters server-side.

    Tradeoff vs Apollo:
      Apollo: query by persona (all SaaS CEOs in NA) → returns people
      Hunter: query by company → returns people at that company only

    So Hunter is best for ABM ('find everyone at these 20 target
    accounts') while Apollo is best for cold discovery.
    """
    target_domain = domain or keywords
    if not target_domain:
        return {
            "ok": False,
            "error": "Hunter requires a domain (pass `domain` or `keywords` with a domain like 'stripe.com').",
        }
    # Strip https://, www., trailing slashes
    dom = target_domain.replace("https://", "").replace("http://", "").replace("www.", "").strip("/").split("/")[0]

    params: dict[str, Any] = {
        "domain": dom,
        "limit": min(per_page, 100),
        "offset": (page - 1) * per_page,
    }
    if titles:
        # Hunter accepts a free-text seniority filter — best-effort.
        params["seniority"] = ",".join(titles)
    if seniorities:
        params["seniority"] = ",".join(seniorities)

    result = await _get("/domain-search", params)
    if not result.get("ok"):
        return result
    data = result.get("data") or {}
    emails = data.get("emails", [])
    org_name = (data.get("organization") or "").strip() or dom
    people = [_normalize_hunter_person(e, company_name=org_name) for e in emails]
    # Only return entries with a real email address
    people = [p for p in people if p.get("email")]
    return {
        "ok": True,
        "people": people,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total_entries": data.get("pattern", {}).get("email_count", len(people)),
        },
        "breadcrumbs": [{"label": "Hunter domain-search", "value": dom}],
    }


async def enrich_person(
    *,
    email: str | None = None,
    linkedin_url: str | None = None,
    first_name: str | None = None,
    last_name: str | None = None,
    organization_name: str | None = None,
    domain: str | None = None,
) -> dict:
    """Hunter's email-finder: given first+last+domain OR email, return
    the best-guess verified contact."""
    if email:
        # Use email-verifier for pure enrichment of a known email
        result = await _get("/email-verifier", {"email": email})
        if not result.get("ok"):
            return result
        d = result.get("data") or {}
        return {
            "ok": True,
            "person": {
                "email": d.get("email"),
                "status": d.get("status"),
                "deliverability_score": d.get("score"),
                "first_name": d.get("sources", [{}])[0].get("first_name"),
                "last_name": d.get("sources", [{}])[0].get("last_name"),
            },
        }
    if not (first_name and last_name and (domain or organization_name)):
        return {
            "ok": False,
            "error": "Hunter enrich requires email OR (first_name + last_name + domain).",
        }
    params = {
        "first_name": first_name,
        "last_name": last_name,
        "domain": domain or organization_name.replace(" ", "").lower() + ".com",
    }
    if organization_name:
        params["company"] = organization_name
    result = await _get("/email-finder", params)
    if not result.get("ok"):
        return result
    d = result.get("data") or {}
    return {
        "ok": True,
        "person": {
            "email": d.get("email"),
            "first_name": d.get("first_name"),
            "last_name": d.get("last_name"),
            "title": d.get("position"),
            "linkedin_url": d.get("linkedin_url"),
            "confidence": d.get("score"),
        },
    }


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
    """Hunter doesn't have a company-discovery endpoint. Return a clear
    error so the caller knows to use Apollo for this query type."""
    return {
        "ok": False,
        "error": "Hunter does not support company discovery. Use Apollo (set APOLLO_API_KEY).",
    }
