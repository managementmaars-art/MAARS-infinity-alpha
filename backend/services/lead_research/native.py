"""Native lead research — BrowserAgent scraping, no external providers.

Replaces the Apollo + Hunter adapter path entirely. The client's own
LinkedIn / Sales Navigator session is driven by the MAARS Playwright
browser (already in-process). Email discovery is guess-and-verify via
MX lookup + common patterns.

Public surface mirrors Apollo so callers (routes/lead_research.py,
workflow_executor's `search_leads` tool, campaign_orchestrator) need
no changes:

    is_configured() -> bool
    search_people(q, titles, locations, industries, seniorities, keywords, page_size)
    enrich_person(email=None, linkedin_url=None, name=None, company=None)
    search_organizations(q, industries, employee_counts, page_size)

Three sourcing strategies, cycled in order per request:

  1. LinkedIn Sales Navigator (if credentials stored in vault)
     - Paid LinkedIn account required (Sales Nav adds deeper filters)
     - Rich person + company data behind the login wall
  2. LinkedIn public search fallback
     - Free LinkedIn account works
     - Coarser filters, fewer fields
  3. Google-indexed LinkedIn scrape ("site:linkedin.com/in …")
     - No LinkedIn login required
     - Brittle but zero-cost insurance when the LinkedIn session is
       rate-limited or challenged

For each person we return whatever is available:
  name, title, company, company_domain, linkedin_url, location,
  seniority, email (guessed + MX-verified), confidence, source.

IMPORTANT legal notes:
  - LinkedIn TOS prohibits scraping. hiQ v. LinkedIn (2022) clarified
    the CFAA doesn't apply to public data, but LinkedIn still enforces
    via cease-and-desist and can sue for ToS breach.
  - Use the operator's own LinkedIn account (credentials in vault);
    don't ship without consent.
  - Throttle aggressively: 1-2 requests/min on LinkedIn to avoid
    triggering detection. Sales Nav has higher limits for paid users.
  - Expect intermittent failures and challenge pages. The adapter
    surfaces errors; it does NOT fall through to paid providers.

No fallback to Apollo / Hunter — by design.
"""
from __future__ import annotations
import asyncio
import logging
import os
import re
import time
from typing import Any
from urllib.parse import quote_plus, urlencode

logger = logging.getLogger(__name__)


def is_configured() -> bool:
    """Native adapter is always considered configured — it runs on the
    MAARS-owned BrowserAgent + public web. No API keys required. The
    underlying Playwright install is the only dependency."""
    return True


# ── Session acquisition — pooled account + pooled proxy ─────────────
# Every scraping request opens a BrowserSession stamped with:
#   - a rotating LinkedIn account (from account_pool)
#   - a rotating residential proxy (from proxy_pool)
# Both pools cool down on failure; both are optional (degrades gracefully).

async def _get_browser_session(user_id: str):
    """Returns (session, pool_ctx) where pool_ctx carries
    {account_email, account_creds, proxy_id, proxy} so callers can
    mark success/failure on the right pool entries after the session
    completes."""
    from services.browser_service import get_browser_pool
    from services.lead_research import account_pool, proxy_pool

    pool = get_browser_pool()
    proxy  = await proxy_pool.get_next()
    account = await account_pool.get_available()
    pool_ctx = {
        "account_email": (account or {}).get("id"),
        "account_creds": account,
        "proxy_id":      (proxy or {}).get("id"),
        "proxy":         (proxy or {}).get("playwright"),
    }
    # browser_service.open accepts a proxy kwarg when wired up (below).
    try:
        sess = await pool.open(
            user_id=user_id, agent_id="lead_research",
            proxy=pool_ctx["proxy"],
        )
    except TypeError:
        # older open() signature — no proxy kw; continue without.
        sess = await pool.open(user_id=user_id, agent_id="lead_research")
    return sess, pool_ctx


async def _release_pool_ctx(pool_ctx: dict, *, success: bool) -> None:
    from services.lead_research import account_pool, proxy_pool
    email = pool_ctx.get("account_email")
    proxy_id = pool_ctx.get("proxy_id")
    if email:
        if success:    await account_pool.mark_success(email)
        else:          await account_pool.release(email)
    if proxy_id:
        if success:    await proxy_pool.mark_success(proxy_id)
        else:          await proxy_pool.release(proxy_id)


async def _linkedin_ensure_logged_in(session, pool_ctx: dict) -> bool:
    """Return True if the session has a live LinkedIn login cookie.
    Uses credentials from the pooled account (pool_ctx['account_creds']).

    On challenge page / captcha / bad login, marks the account via
    account_pool so the next request rotates to another account. Never
    falls back to external APIs."""
    from services.lead_research import account_pool
    creds = pool_ctx.get("account_creds")
    if not creds:
        return False

    try:
        page_url = await session.current_url() if hasattr(session, "current_url") else None
        if page_url and "linkedin.com/feed" in page_url:
            return True
    except Exception:
        pass

    try:
        await session.navigate("https://www.linkedin.com/login")
        await session.fill("#username", creds["email"])
        await session.fill("#password", creds["password"])
        await session.click("button[type='submit']")
        await asyncio.sleep(4)
        url = await session.current_url() if hasattr(session, "current_url") else ""
        # Detect LinkedIn challenge / captcha.
        if "/checkpoint/" in url or "/challenge" in url or "captcha" in (url or "").lower():
            await account_pool.mark_challenge(creds["email"], reason="checkpoint")
            return False
        ok = "/feed" in url or "/in/" in url or "/sales/" in url
        if not ok:
            await account_pool.mark_login_failed(
                creds["email"], reason=f"unexpected redirect {url[:120]}",
            )
        return ok
    except Exception as exc:
        await account_pool.mark_login_failed(
            creds.get("email", ""), reason=f"{type(exc).__name__}: {str(exc)[:200]}",
        )
        return False


def _parse_name(full: str) -> tuple[str, str]:
    parts = (full or "").strip().split()
    if not parts: return "", ""
    if len(parts) == 1: return parts[0], ""
    return parts[0], parts[-1]


# ── LinkedIn public-search scraper ───────────────────────────────────

async def _search_linkedin_public(
    *, user_id: str, query: str, titles: list[str] | None,
    locations: list[str] | None, page_size: int,
) -> list[dict]:
    """Logged-in LinkedIn public people-search.

    URL shape:
      https://www.linkedin.com/search/results/people/?keywords=...&title=...&location=...
    """
    session, pool_ctx = await _get_browser_session(user_id)
    try:
        if not await _linkedin_ensure_logged_in(session, pool_ctx):
            await _release_pool_ctx(pool_ctx, success=False)
            return []

        kw = [query or ""]
        if titles: kw.append(" ".join(titles))
        params = {"keywords": " ".join(x for x in kw if x)}
        if locations:
            params["location"] = ",".join(locations)
        url = f"https://www.linkedin.com/search/results/people/?{urlencode(params)}"
        try:
            await session.navigate(url)
        except Exception as exc:
            logger.info("linkedin public nav failed: %s", exc)
            await _release_pool_ctx(pool_ctx, success=False)
            return []
        await asyncio.sleep(2)

        # Scroll to load more results.
        for _ in range(min(5, max(1, page_size // 10))):
            try:
                await session.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await asyncio.sleep(1.5)
            except Exception:
                break

        try:
            html = await session.evaluate("document.documentElement.outerHTML")
        except Exception:
            html = ""
        rows = _parse_linkedin_search_html(html, limit=page_size)
        await _release_pool_ctx(pool_ctx, success=bool(rows))
        return rows
    except Exception:
        await _release_pool_ctx(pool_ctx, success=False)
        raise


def _parse_linkedin_search_html(html: str, *, limit: int) -> list[dict]:
    """Extract people rows from LinkedIn search-results HTML. LinkedIn
    rewrites their SPA constantly; we try multiple selectors in order."""
    if not html: return []
    rows: list[dict] = []

    # Strategy A: entity-result cards (current 2024/2025 layout).
    for m in re.finditer(
        r'href="(/in/[^"?]+)"[^>]*>.*?'
        r'<span[^>]*aria-hidden="true"[^>]*>([^<]+)</span>.*?'
        r'entity-result__primary-subtitle[^>]*>\s*([^<]+)\s*<.*?'
        r'entity-result__secondary-subtitle[^>]*>\s*([^<]+)\s*<',
        html, re.DOTALL,
    ):
        path, name, title, loc = m.group(1), m.group(2), m.group(3), m.group(4)
        first, last = _parse_name(name)
        # Title often carries "Role at Company"
        company = None
        if " at " in title:
            role_part, _, company_part = title.partition(" at ")
            title_clean = role_part.strip()
            company = company_part.strip()
        else:
            title_clean = title.strip()
        rows.append({
            "first_name":   first,
            "last_name":    last,
            "name":         name.strip(),
            "title":        title_clean,
            "company":      company,
            "location":     loc.strip(),
            "linkedin_url": "https://www.linkedin.com" + path,
            "source":       "linkedin_public",
        })
        if len(rows) >= limit:
            break

    return rows


# ── LinkedIn Sales Navigator scraper (paid LinkedIn users) ───────────

async def _search_sales_nav(
    *, user_id: str, query: str, titles: list[str] | None,
    industries: list[str] | None, page_size: int,
) -> list[dict]:
    """Sales Navigator delivers richer filters (seniority, years at
    company, company size). Requires a paid LinkedIn account on file."""
    session, pool_ctx = await _get_browser_session(user_id)
    try:
        if not await _linkedin_ensure_logged_in(session, pool_ctx):
            await _release_pool_ctx(pool_ctx, success=False)
            return []

        terms = [query or ""]
        if titles:     terms.append(" ".join(titles))
        if industries: terms.append(" ".join(industries))
        search = " ".join(t for t in terms if t).strip()
        url = f"https://www.linkedin.com/sales/search/people?keywords={quote_plus(search)}"
        try:
            await session.navigate(url)
        except Exception:
            await _release_pool_ctx(pool_ctx, success=False)
            return []
        await asyncio.sleep(3)

        for _ in range(3):
            try:
                await session.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await asyncio.sleep(1.5)
            except Exception:
                break

        try:
            html = await session.evaluate("document.documentElement.outerHTML")
        except Exception:
            html = ""
        rows = _parse_linkedin_search_html(html, limit=page_size)
        for r in rows: r["source"] = "sales_navigator"
        await _release_pool_ctx(pool_ctx, success=bool(rows))
        return rows
    except Exception:
        await _release_pool_ctx(pool_ctx, success=False)
        raise


# ── Google-indexed LinkedIn fallback (no LinkedIn login) ─────────────

async def _search_via_google(
    *, user_id: str, query: str, titles: list[str] | None,
    locations: list[str] | None, page_size: int,
) -> list[dict]:
    """When LinkedIn rate-limits, Google's index of linkedin.com/in
    profiles still surfaces the same people. Costs nothing, needs no
    LinkedIn account."""
    session, pool_ctx = await _get_browser_session(user_id)
    # Google scrape doesn't need a LinkedIn account — release it.
    try:
        from services.lead_research import account_pool
        if pool_ctx.get("account_email"):
            await account_pool.release(pool_ctx["account_email"])
    except Exception:
        pass

    q_parts = ['site:linkedin.com/in']
    if query: q_parts.append(f'"{query}"')
    if titles:
        q_parts.append("(" + " OR ".join(f'"{t}"' for t in titles) + ")")
    if locations:
        q_parts.append("(" + " OR ".join(f'"{loc}"' for loc in locations) + ")")
    q = " ".join(q_parts)
    url = f"https://www.google.com/search?q={quote_plus(q)}&num={min(page_size, 50)}"

    try:
        await session.navigate(url)
        await asyncio.sleep(2)
        html = await session.evaluate("document.documentElement.outerHTML")
    except Exception:
        await _release_pool_ctx(pool_ctx, success=False)
        return []

    rows: list[dict] = []
    # Google SERP result anchors + titles
    for m in re.finditer(
        r'<a href="(https?://[^"]*linkedin\.com/in/[^"]+)"[^>]*>.*?'
        r'<h3[^>]*>([^<]+)</h3>',
        html, re.DOTALL,
    ):
        link, title_text = m.group(1), m.group(2)
        # Google results list "Name - Title - Company | LinkedIn"
        parts = re.split(r"\s+[-–—]\s+", title_text)
        name = parts[0].strip() if parts else ""
        role = parts[1].strip() if len(parts) > 1 else ""
        company = parts[2].replace("| LinkedIn", "").strip() if len(parts) > 2 else None
        first, last = _parse_name(name)
        rows.append({
            "first_name":   first,
            "last_name":    last,
            "name":         name,
            "title":        role,
            "company":      company,
            "linkedin_url": re.sub(r"\?.*$", "", link),
            "source":       "google_indexed",
        })
        if len(rows) >= page_size:
            break
    await _release_pool_ctx(pool_ctx, success=bool(rows))
    return rows


# ── Email discovery (guess + MX verify) ──────────────────────────────

_COMMON_PATTERNS = [
    "{first}.{last}@{domain}",
    "{first}@{domain}",
    "{f}{last}@{domain}",
    "{first}{last}@{domain}",
    "{first}_{last}@{domain}",
    "{first}-{last}@{domain}",
    "{last}.{first}@{domain}",
    "{last}@{domain}",
]


async def _company_domain_from_website(company_name: str) -> str | None:
    """Quick heuristic: slug the company name into a likely root domain,
    then check if it resolves. More aggressive lookup lives in the
    enrichment path."""
    if not company_name: return None
    slug = re.sub(r"[^a-z0-9]", "", company_name.lower())
    if not slug: return None
    candidates = [f"{slug}.com", f"{slug}.io", f"{slug}.co", f"{slug}.net"]
    for cand in candidates:
        try:
            # Cheap DNS check via socket
            import socket as _sk
            _sk.gethostbyname(cand)
            return cand
        except Exception:
            continue
    return None


async def _mx_check(domain: str) -> bool:
    """Accept-all domains aren't reliable but at least ensure MX exists."""
    try:
        import dns.resolver
        await asyncio.to_thread(dns.resolver.resolve, domain, "MX")
        return True
    except Exception:
        return False


async def discover_email(first: str, last: str, company_domain: str | None = None,
                        company_name: str | None = None) -> dict[str, Any]:
    """Return best-guess email + confidence + MX verified flag."""
    if not (first and (company_domain or company_name)):
        return {"email": None, "confidence": 0.0}
    domain = company_domain or await _company_domain_from_website(company_name or "")
    if not domain:
        return {"email": None, "confidence": 0.0, "reason": "no_domain"}

    mx_ok = await _mx_check(domain)
    f = first.lower().strip()
    l = (last or "").lower().strip()
    initial = f[:1] if f else ""
    vals = {"first": f, "last": l, "f": initial, "domain": domain}

    tried = []
    for pat in _COMMON_PATTERNS:
        try:
            e = pat.format(**vals)
        except KeyError:
            continue
        e = re.sub(r"\.\.", ".", e).replace(".@", "@").replace("_@", "@")
        if "@" not in e: continue
        tried.append(e)

    # We can't verify delivery without paying a validator — but we can
    # return the top 3 guesses and let the caller pick. Top pattern
    # (`first.last@domain`) has ~65-75% accuracy across B2B.
    if not tried:
        return {"email": None, "confidence": 0.0}
    return {
        "email":      tried[0],
        "alternates": tried[1:4],
        "confidence": 0.75 if mx_ok else 0.45,
        "mx_verified": mx_ok,
        "domain":     domain,
    }


# ── Public API (Apollo-compatible shape) ─────────────────────────────

async def search_people(
    q: str = "",
    titles: list[str] | None = None,
    locations: list[str] | None = None,
    industries: list[str] | None = None,
    seniorities: list[str] | None = None,
    keywords: str = "",
    page_size: int = 25,
    user_id: str | None = None,
    **_ignored,
) -> dict[str, Any]:
    """Return {ok, people:[...]} using native scraping only. No
    fallback to paid providers.
    """
    uid = user_id or os.environ.get("MAARS_SCRAPE_USER_ID", "system")
    query = " ".join(x for x in [q, keywords] if x).strip()

    # Strategy 1: Sales Nav if we have paid LinkedIn creds.
    try:
        rows = await _search_sales_nav(
            user_id=uid, query=query, titles=titles,
            industries=industries, page_size=page_size,
        )
        if rows:
            _enrich_inline_emails(rows)
            return {"ok": True, "people": rows, "source": "sales_navigator"}
    except Exception as exc:
        logger.info("sales_nav search failed: %s", exc)

    # Strategy 2: LinkedIn public search (free LinkedIn account works).
    try:
        rows = await _search_linkedin_public(
            user_id=uid, query=query, titles=titles,
            locations=locations, page_size=page_size,
        )
        if rows:
            await _enrich_inline_emails(rows)
            return {"ok": True, "people": rows, "source": "linkedin_public"}
    except Exception as exc:
        logger.info("linkedin_public search failed: %s", exc)

    # Strategy 3: Google-indexed LinkedIn.
    try:
        rows = await _search_via_google(
            user_id=uid, query=query, titles=titles,
            locations=locations, page_size=page_size,
        )
        if rows:
            await _enrich_inline_emails(rows)
            return {"ok": True, "people": rows, "source": "google_indexed"}
    except Exception as exc:
        logger.info("google search failed: %s", exc)

    return {"ok": False, "error": "all scraping strategies failed", "people": []}


async def _enrich_inline_emails(rows: list[dict]) -> None:
    """For each row, attach a guessed email. Runs concurrently to keep
    the search-to-usable-leads path fast."""
    async def _one(r: dict):
        if r.get("email"):
            return
        first = r.get("first_name") or ""
        last  = r.get("last_name")  or ""
        company = r.get("company") or ""
        if not (first and company):
            return
        e = await discover_email(first, last, company_name=company)
        if e.get("email"):
            r["email"] = e["email"]
            r["email_alternates"] = e.get("alternates") or []
            r["email_confidence"] = e.get("confidence", 0.0)
            r["email_mx_verified"] = e.get("mx_verified", False)
    await asyncio.gather(*(_one(r) for r in rows), return_exceptions=True)


async def enrich_person(
    email: str | None = None, linkedin_url: str | None = None,
    name: str | None = None, company: str | None = None,
    user_id: str | None = None, **_ignored,
) -> dict[str, Any]:
    """Pull fuller detail for a known person. Strategy:
      - If linkedin_url: navigate + scrape profile page
      - Else if email: extract domain, scrape company site team page
      - Else if name+company: search + pick top hit + scrape profile
    """
    uid = user_id or os.environ.get("MAARS_SCRAPE_USER_ID", "system")

    if linkedin_url:
        return await _enrich_from_linkedin_url(uid, linkedin_url)
    if email:
        return await _enrich_from_email(uid, email)
    if name and company:
        # Run a targeted search and take the top hit
        s = await search_people(q=name, keywords=company, page_size=1, user_id=uid)
        if s.get("ok") and s.get("people"):
            p = s["people"][0]
            if p.get("linkedin_url"):
                return await _enrich_from_linkedin_url(uid, p["linkedin_url"])
            return {"ok": True, "person": p}

    return {"ok": False, "error": "provide email, linkedin_url, or name+company"}


async def _enrich_from_linkedin_url(user_id: str, url: str) -> dict[str, Any]:
    session, pool_ctx = await _get_browser_session(user_id)
    try:
        if not await _linkedin_ensure_logged_in(session, pool_ctx):
            await _release_pool_ctx(pool_ctx, success=False)
            return {"ok": False, "error": "linkedin session unavailable"}
        try:
            await session.navigate(url)
            await asyncio.sleep(2)
            html = await session.evaluate("document.documentElement.outerHTML")
        except Exception as exc:
            await _release_pool_ctx(pool_ctx, success=False)
            return {"ok": False, "error": f"profile fetch failed: {exc}"}

        def _extract(pattern: str, default: str = "") -> str:
            m = re.search(pattern, html, re.DOTALL)
            return m.group(1).strip() if m else default

        name    = _extract(r'<h1[^>]*>\s*([^<]+)\s*</h1>')
        headline = _extract(r'text-body-medium break-words[^>]*>\s*([^<]+)\s*<')
        location = _extract(r'text-body-small inline[^>]*>\s*([^<]+)\s*<')
        company = _extract(r'pv-text-details__right-panel-item[^>]*>\s*([^<]+)\s*<')

        first, last = _parse_name(name)
        person = {
            "name": name, "first_name": first, "last_name": last,
            "title": headline, "location": location, "company": company,
            "linkedin_url": url, "source": "linkedin_profile",
        }

        if company:
            e = await discover_email(first, last, company_name=company)
            if e.get("email"):
                person["email"] = e["email"]
                person["email_confidence"] = e.get("confidence", 0.0)
                person["email_mx_verified"] = e.get("mx_verified", False)

        # Phone discovery — free sources only (LinkedIn contact info,
        # company site, NumVerify validate). No Apollo.
        try:
            from services.lead_research.phone_discovery import discover_phone
            ph = await discover_phone(
                first=first, last=last, company=company,
                linkedin_url=url, user_id=user_id,
            )
            if ph.get("phone"):
                person["phone"]            = ph["phone"]
                person["phone_kind"]       = ph.get("kind")
                person["phone_source"]     = ph.get("source")
                person["phone_verified"]   = ph.get("verified", False)
                person["phone_confidence"] = ph.get("confidence", 0.0)
        except Exception as pexc:
            logger.info("phone discovery soft-fail: %s", pexc)

        await _release_pool_ctx(pool_ctx, success=True)
        return {"ok": True, "person": person}
    except Exception:
        await _release_pool_ctx(pool_ctx, success=False)
        raise


async def _enrich_from_email(user_id: str, email: str) -> dict[str, Any]:
    """Look up a person starting from an email. We have the domain; we
    try to find the company's team/about page and match the name."""
    domain = email.split("@", 1)[1] if "@" in email else ""
    if not domain:
        return {"ok": False, "error": "invalid email"}

    session, pool_ctx = await _get_browser_session(user_id)
    # Company-site scrape doesn't need LinkedIn creds — release the account.
    try:
        from services.lead_research import account_pool
        if pool_ctx.get("account_email"):
            await account_pool.release(pool_ctx["account_email"])
    except Exception:
        pass

    name_part = email.split("@", 1)[0].replace(".", " ").replace("_", " ").title()
    for path in ("/team", "/about", "/about-us", "/people", "/company"):
        try:
            await session.navigate(f"https://{domain}{path}")
            await asyncio.sleep(1.5)
            html = await session.evaluate("document.documentElement.outerHTML")
        except Exception:
            continue
        if name_part.lower().split(" ")[0] in (html or "").lower():
            first, last = _parse_name(name_part)
            await _release_pool_ctx(pool_ctx, success=True)
            return {"ok": True, "person": {
                "name": name_part, "first_name": first, "last_name": last,
                "email": email, "company_domain": domain,
                "source": f"company_site{path}",
            }}

    await _release_pool_ctx(pool_ctx, success=False)
    # Retry via LinkedIn search — this uses its own session + pool entries.
    s = await search_people(q=name_part, keywords=domain.split(".")[0],
                            page_size=1, user_id=user_id)
    if s.get("ok") and s.get("people"):
        p = s["people"][0]
        p["email"] = email
        return {"ok": True, "person": p}
    return {"ok": False, "error": "no match", "email": email, "domain": domain}


async def search_organizations(
    q: str = "", industries: list[str] | None = None,
    employee_counts: list[str] | None = None, page_size: int = 25,
    user_id: str | None = None, **_ignored,
) -> dict[str, Any]:
    """Find companies. Uses Google search for LinkedIn company pages."""
    uid = user_id or os.environ.get("MAARS_SCRAPE_USER_ID", "system")
    session, pool_ctx = await _get_browser_session(uid)
    try:
        from services.lead_research import account_pool
        if pool_ctx.get("account_email"):
            await account_pool.release(pool_ctx["account_email"])
    except Exception:
        pass

    q_parts = ['site:linkedin.com/company']
    if q: q_parts.append(f'"{q}"')
    if industries:
        q_parts.append("(" + " OR ".join(f'"{i}"' for i in industries) + ")")
    url = f"https://www.google.com/search?q={quote_plus(' '.join(q_parts))}&num={min(page_size, 50)}"

    try:
        await session.navigate(url)
        await asyncio.sleep(2)
        html = await session.evaluate("document.documentElement.outerHTML")
    except Exception as exc:
        await _release_pool_ctx(pool_ctx, success=False)
        return {"ok": False, "error": str(exc)[:200], "organizations": []}

    orgs: list[dict] = []
    for m in re.finditer(
        r'<a href="(https?://[^"]*linkedin\.com/company/[^"]+)"[^>]*>.*?<h3[^>]*>([^<]+)</h3>',
        html, re.DOTALL,
    ):
        link, title_text = m.group(1), m.group(2)
        parts = re.split(r"\s+[-–—|]\s+", title_text)
        name = parts[0].strip()
        industry = parts[1].strip() if len(parts) > 1 else None
        orgs.append({
            "name":         name,
            "industry":     industry,
            "linkedin_url": re.sub(r"\?.*$", "", link),
            "source":       "google_indexed",
        })
        if len(orgs) >= page_size:
            break
    await _release_pool_ctx(pool_ctx, success=bool(orgs))
    return {"ok": True, "organizations": orgs}
