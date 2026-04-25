"""Phone-number discovery — free/cheaper sources, no Apollo.

Apollo's direct-dial database is the single feature nobody replaces
cleanly for free. The honest strategy:

  1. LinkedIn "Contact info" section if we're logged in (user has
     to accept a connection request OR be 1st/2nd degree). ~20% of
     profiles expose a phone.
  2. Company website contact / about page scrape — pulls the main
     switchboard number + sometimes exec direct dials.
  3. NumVerify (apilayer) free tier — VALIDATE an already-guessed
     number. 100 requests/mo free, no card required. Won't DISCOVER,
     but confirms a phone is real + tells you carrier + line type
     (mobile vs landline — critical for B2C cold call compliance).
  4. Common patterns — if you know the switchboard number and the
     extension pattern, we can construct candidate direct dials. Low
     hit rate but costs zero.

What this WON'T do (honest): find mobile direct-dials for strangers.
That's Apollo's moat and there's no free substitute.

Public API:
  async discover_phone(first, last, company, linkedin_url=None, user_id=None)
    → {"phone": "+1...", "kind": "main"|"direct"|"mobile", "source": ...,
       "verified": bool, "confidence": 0-1}
"""
from __future__ import annotations
import asyncio
import logging
import os
import re
from typing import Any

logger = logging.getLogger(__name__)


# ── Strategy 1: LinkedIn "Contact info" modal ────────────────────────

async def _from_linkedin_contact_info(user_id: str, linkedin_url: str) -> str | None:
    """Navigate to the profile, click "Contact info", parse the modal."""
    from services.browser_service import get_browser_pool
    pool = get_browser_pool()
    session = await pool.open(user_id=user_id, agent_id="phone_discovery")
    try:
        await session.navigate(linkedin_url.rstrip("/") + "/overlay/contact-info/")
        await asyncio.sleep(2)
        html = await session.evaluate("document.documentElement.outerHTML")
    except Exception:
        return None
    # LinkedIn labels the phone row with "pv-contact-info__contact-type ci-phone"
    m = re.search(
        r'ci-phone.*?<span[^>]*>\s*([\d\s\+\-\(\)\.]{7,})\s*<',
        html or "", re.DOTALL,
    )
    if not m: return None
    raw = m.group(1).strip()
    return _normalize_e164(raw)


# ── Strategy 2: company website contact / about page ────────────────

async def _from_company_site(domain: str) -> str | None:
    """Scan the company's contact-style pages for a phone number."""
    try:
        from services.http_client import get_client
        client = await get_client()
    except Exception:
        return None
    for path in ("/contact", "/contact-us", "/about", "/about-us", "/company", "/"):
        try:
            r = await client.get(f"https://{domain}{path}", timeout=10)
            if r.status_code >= 400: continue
            text = r.text
        except Exception:
            continue
        # Phones in plain text + `tel:` hrefs.
        for pat in (
            r'tel:([\+\d][\d\s\-\(\)\.]{6,})',
            r'\+?\d{1,3}[\s\-\.]?\(?\d{2,4}\)?[\s\-\.]?\d{3}[\s\-\.]?\d{3,4}',
            r'\(?\d{3}\)?[\s\-\.]?\d{3}[\s\-\.]?\d{4}',
        ):
            for m in re.finditer(pat, text):
                candidate = m.group(1) if "(" in pat else m.group(0)
                e164 = _normalize_e164(candidate)
                if e164: return e164
    return None


# ── Strategy 3: NumVerify free-tier validation ──────────────────────

async def verify_with_numverify(phone: str) -> dict[str, Any] | None:
    """Validate a phone (from any source) via NumVerify. Returns
    {valid, country_code, line_type, carrier, e164} or None on error."""
    key = os.environ.get("NUMVERIFY_API_KEY")
    if not key:
        return None
    try:
        from services.http_client import get_client
        client = await get_client()
        r = await client.get(
            "http://apilayer.net/api/validate",
            params={"access_key": key, "number": phone, "format": "1"},
            timeout=10,
        )
        r.raise_for_status()
        d = r.json()
    except Exception as exc:
        logger.info("numverify failed: %s", exc)
        return None
    if not d.get("valid"):
        return {"valid": False}
    return {
        "valid":        True,
        "country_code": d.get("country_code"),
        "line_type":    d.get("line_type"),
        "carrier":      d.get("carrier"),
        "e164":         "+" + str(d.get("international_format", "")).lstrip("+"),
    }


# ── Normalization ────────────────────────────────────────────────────

def _normalize_e164(raw: str) -> str | None:
    """Best-effort E.164. If the number starts with + keep it; else if
    it looks like US (10 digits or 11 starting with 1), prefix +1.
    Everything else: return as-is with digits only."""
    if not raw: return None
    digits = re.sub(r"\D", "", raw)
    if raw.strip().startswith("+"):
        return "+" + digits
    if len(digits) == 10:           # US domestic
        return "+1" + digits
    if len(digits) == 11 and digits.startswith("1"):
        return "+" + digits
    if 8 <= len(digits) <= 15:      # international shape
        return "+" + digits
    return None


# ── Public API ───────────────────────────────────────────────────────

async def discover_phone(
    *, first: str = "", last: str = "",
    company: str | None = None,
    company_domain: str | None = None,
    linkedin_url: str | None = None,
    user_id: str = "system",
) -> dict[str, Any]:
    """Try every cheap source. First successful lookup wins. Returns
    {phone, kind, source, verified, confidence} or {phone: None} on
    total miss."""
    # 1) LinkedIn contact info
    if linkedin_url:
        try:
            p = await _from_linkedin_contact_info(user_id, linkedin_url)
            if p:
                nv = await verify_with_numverify(p)
                verified = bool(nv and nv.get("valid"))
                return {
                    "phone":      (nv or {}).get("e164") or p,
                    "kind":       (nv or {}).get("line_type") or "direct",
                    "source":     "linkedin_contact_info",
                    "verified":   verified,
                    "confidence": 0.85 if verified else 0.6,
                    "carrier":    (nv or {}).get("carrier"),
                }
        except Exception as exc:
            logger.info("linkedin contact-info scrape failed: %s", exc)

    # 2) Company website
    domain = company_domain
    if not domain and company:
        try:
            from services.lead_research.native import _company_domain_from_website
            domain = await _company_domain_from_website(company)
        except Exception:
            domain = None
    if domain:
        try:
            p = await _from_company_site(domain)
            if p:
                nv = await verify_with_numverify(p)
                verified = bool(nv and nv.get("valid"))
                return {
                    "phone":      (nv or {}).get("e164") or p,
                    "kind":       (nv or {}).get("line_type") or "main",
                    "source":     f"{domain}/contact",
                    "verified":   verified,
                    "confidence": 0.55 if verified else 0.4,
                    "note":       "main/switchboard; ask for person by name",
                    "carrier":    (nv or {}).get("carrier"),
                }
        except Exception as exc:
            logger.info("company-site phone scrape failed: %s", exc)

    return {"phone": None, "confidence": 0.0,
            "note": "no phone found via free/cheap sources"}
