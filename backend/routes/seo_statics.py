"""Public SEO + trust-signal static endpoints.

  /sitemap.xml           — tells Google what to crawl
  /robots.txt            — tells Google what NOT to crawl
  /.well-known/security.txt  — security researcher contact
  /.well-known/dnt-policy.txt — DNT (Do Not Track) statement

All unauthenticated, all cached with long TTL so Googlebot doesn't hammer.
"""
from __future__ import annotations
import os
from datetime import datetime, timezone

from fastapi import APIRouter
from fastapi.responses import PlainTextResponse, Response

router = APIRouter()


def _public_url() -> str:
    return os.environ.get("MAARS_PUBLIC_URL", "https://maarscommand.com").rstrip("/")


# Static pages worth indexing. `lastmod` kept loose — daily freshness
# is fine for marketing pages; Google figures it out.
_SITEMAP_URLS = [
    # Top-level marketing
    ("/",                     "daily",  "1.0"),
    ("/pricing",              "weekly", "0.9"),
    ("/changelog",            "daily",  "0.8"),
    ("/alternatives",         "weekly", "0.7"),
    ("/alternatives/jasper",  "weekly", "0.7"),
    ("/alternatives/copy-ai", "weekly", "0.7"),
    ("/alternatives/cursor",  "weekly", "0.7"),
    ("/alternatives/lovable", "weekly", "0.7"),
    # Legal — stable, low priority
    ("/privacy",              "monthly","0.4"),
    ("/terms",                "monthly","0.4"),
]


@router.get("/sitemap.xml")
async def sitemap_xml():
    base = _public_url()
    today = datetime.now(timezone.utc).date().isoformat()
    urls_xml: list[str] = []
    for path, changefreq, priority in _SITEMAP_URLS:
        urls_xml.append(
            f"  <url>\n"
            f"    <loc>{base}{path}</loc>\n"
            f"    <lastmod>{today}</lastmod>\n"
            f"    <changefreq>{changefreq}</changefreq>\n"
            f"    <priority>{priority}</priority>\n"
            f"  </url>"
        )
    # Include every published changelog entry as an indexable URL
    try:
        from db import db
        entries = await db.changelog_entries.find(
            {"published": True},
            {"_id": 0, "slug": 1, "published_at": 1},
        ).sort("published_at", -1).to_list(200)
        for e in entries:
            slug = e.get("slug")
            if not slug:
                continue
            lastmod = (e.get("published_at") or today)[:10]
            urls_xml.append(
                f"  <url>\n"
                f"    <loc>{base}/changelog#{slug}</loc>\n"
                f"    <lastmod>{lastmod}</lastmod>\n"
                f"    <changefreq>monthly</changefreq>\n"
                f"    <priority>0.5</priority>\n"
                f"  </url>"
            )
    except Exception:
        pass
    body = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(urls_xml) +
        "\n</urlset>\n"
    )
    return Response(body, media_type="application/xml", headers={
        "Cache-Control": "public, max-age=3600",
    })


@router.get("/robots.txt", response_class=PlainTextResponse)
async def robots_txt():
    base = _public_url()
    return (
        f"# MAARS Command robots.txt\n"
        f"User-agent: *\n"
        f"Disallow: /api/\n"
        f"Disallow: /admin/\n"
        f"Disallow: /dashboard\n"
        f"Disallow: /settings\n"
        f"Disallow: /chat/\n"
        f"Disallow: /r/\n"
        f"Allow: /\n"
        f"\n"
        f"# Crawl delay for noisy bots\n"
        f"User-agent: SemrushBot\n"
        f"Crawl-delay: 10\n"
        f"User-agent: AhrefsBot\n"
        f"Crawl-delay: 10\n"
        f"User-agent: MJ12bot\n"
        f"Disallow: /\n"
        f"\n"
        f"Sitemap: {base}/sitemap.xml\n"
    )


@router.get("/.well-known/security.txt", response_class=PlainTextResponse)
async def security_txt():
    base = _public_url()
    # RFC 9116 security.txt format — helps researchers report vulns.
    return (
        f"Contact: mailto:security@marsgc.net\n"
        f"Expires: 2027-01-01T00:00:00.000Z\n"
        f"Preferred-Languages: en\n"
        f"Canonical: {base}/.well-known/security.txt\n"
        f"Policy: {base}/security\n"
        f"# We appreciate responsible disclosure. Please give us 90 days\n"
        f"# before public disclosure for complex issues, 30 for simple.\n"
    )


@router.get("/.well-known/dnt-policy.txt", response_class=PlainTextResponse)
async def dnt_policy():
    # EFF's Do Not Track policy compliance statement.
    return (
        "# MAARS Command honors Do Not Track.\n"
        "# When DNT=1 is set, we do not:\n"
        "#   - Set analytics or marketing cookies\n"
        "#   - Share identifiers with third parties\n"
        "#   - Retain server-side profiling data\n"
        "# Essential cookies (session, auth, security) remain active.\n"
    )
