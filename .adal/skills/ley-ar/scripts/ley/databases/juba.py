from __future__ import annotations

import re
from typing import Any

import httpx

BASE_URL = "https://juba.scba.gov.ar"
SEARCH_URL = f"{BASE_URL}/Buscar.aspx"


class JubaError(Exception):
    pass


def _extract_tokens(html: str) -> dict[str, str]:
    out = {}
    for key in ("__VIEWSTATE", "__VIEWSTATEGENERATOR", "__EVENTVALIDATION"):
        m = re.search(rf'id="{key}"\s+value="([^"]*)"', html)
        if m:
            out[key] = m.group(1)
    return out


def _clean_html(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", text)).strip()


def search(query: str, limit: int = 10, timeout: float = 30.0) -> list[dict[str, Any]]:
    headers = {"User-Agent": "Mozilla/5.0 (ley-ar/0.1.0)"}
    try:
        with httpx.Client(timeout=timeout, follow_redirects=True, headers=headers) as client:
            r1 = client.get(SEARCH_URL)
            r1.raise_for_status()
            tokens = _extract_tokens(r1.text)
            form = {
                **tokens,
                "__EVENTTARGET": "",
                "__EVENTARGUMENT": "",
                "ctl00$cphMainContent$txtExpresionBusquedaRapida": query,
                "ctl00$cphMainContent$ddlMateria": "Todos",
                "ctl00$cphMainContent$btnUnicaBusqueda": "Buscar",
                "ctl00$cphMainContent$txtPrimeraCarga": "SI",
                "ctl00$cphMainContent$solapaMostrada": "",
            }
            r2 = client.post(SEARCH_URL, data=form)
            r2.raise_for_status()
            html = r2.text
    except Exception as e:
        raise JubaError(str(e)) from e

    paragraphs = [_clean_html(p) for p in re.findall(r"<p[^>]*>(.*?)</p>", html, re.S)]
    paragraphs = [p for p in paragraphs if p]
    out: list[dict[str, Any]] = []
    for i, p in enumerate(paragraphs):
        if p.startswith("Resultado:") and i + 2 < len(paragraphs):
            rid = paragraphs[i + 1]
            voces = paragraphs[i + 2]
            snippet = paragraphs[i + 3] if i + 3 < len(paragraphs) else ""
            out.append({"db": "juba", "id": rid, "title": voces[:120], "snippet": snippet[:350], "date": "", "url": SEARCH_URL})
            if len(out) >= limit:
                break
    return out
