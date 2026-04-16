from __future__ import annotations

import html as html_mod
import json
import re
from typing import Any

import httpx

BASE_URL = "https://sjconsulta.csjn.gov.ar/sjconsulta"
CONSULTA_URL = f"{BASE_URL}/consultaSumarios/consulta.html"
BUSCAR_URL = f"{BASE_URL}/consultaSumarios/buscar.html"
PAGINAR_URL = f"{BASE_URL}/consultaSumarios/paginarSumarios.html"


class CsjnError(Exception):
    pass


def _strip(text: str) -> str:
    return html_mod.unescape(re.sub(r"<[^>]+>", "", text or "")).strip()


def search(query: str, limit: int = 10, timeout: float = 30.0) -> list[dict[str, Any]]:
    headers = {"User-Agent": "Mozilla/5.0 (ley-ar/0.1.0)"}
    try:
        with httpx.Client(timeout=timeout, follow_redirects=True, headers=headers) as client:
            client.get(CONSULTA_URL).raise_for_status()
            form = {
                "filter.fullText": query,
                "filter.autos": "",
                "filter.fechaExacta": "",
                "filter.fechaDesde": "",
                "filter.fechaHasta": "",
            }
            r = client.post(BUSCAR_URL, data=form, headers={"Referer": CONSULTA_URL})
            r.raise_for_status()
            m = re.search(r'totalResultados\s*=\s*"(\d+)"', r.text)
            total = int(m.group(1)) if m else 0
            if total == 0:
                return []
            p = client.get(PAGINAR_URL, params={"startIndex": 0}, headers={"X-Requested-With": "XMLHttpRequest"})
            p.raise_for_status()
            data = json.loads(p.text)
    except Exception as e:
        raise CsjnError(str(e)) from e

    out: list[dict[str, Any]] = []
    for item in data[:limit]:
        out.append(
            {
                "db": "csjn",
                "id": item.get("id"),
                "title": item.get("autos") or item.get("caratulaWeb") or "Sin carátula",
                "snippet": _strip(item.get("texto", ""))[:350],
                "date": item.get("fechaString") or "",
                "url": "https://sjconsulta.csjn.gov.ar/sjconsulta/consultaSumarios/consulta.html",
            }
        )
    return out
