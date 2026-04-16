from __future__ import annotations

import json
from typing import Any

import httpx

BASE_URL = "https://www.saij.gob.ar"


class SaijError(Exception):
    pass


def _safe(v: Any) -> str:
    if isinstance(v, dict):
        return str(v.get("texto") or v.get("descripcion") or "")
    return str(v or "")


def search(query: str, limit: int = 10, timeout: float = 20.0) -> list[dict[str, Any]]:
    params = {
        "r": f"+titulo: {query}",
        "o": 0,
        "p": max(1, min(limit, 25)),
        "f": "Total|Tipo de Documento|Fecha|Tribunal|Jurisdicción",
        "v": "colapsada",
    }
    try:
        with httpx.Client(timeout=timeout) as client:
            res = client.get(f"{BASE_URL}/busqueda", params=params, headers={"Accept": "application/json"})
            res.raise_for_status()
            data = res.json()
    except Exception as e:
        raise SaijError(str(e)) from e

    items = data.get("searchResults", {}).get("documentResultList", [])
    out: list[dict[str, Any]] = []
    for item in items[:limit]:
        try:
            abstract = json.loads(item.get("documentAbstract", "{}"))
            doc = abstract.get("document", {})
            meta = doc.get("metadata", {})
            content = doc.get("content", {})
            out.append(
                {
                    "db": "saij",
                    "id": content.get("id-infojus") or meta.get("uuid"),
                    "title": _safe(content.get("titulo") or content.get("actor")),
                    "snippet": _safe(content.get("texto"))[:350],
                    "date": _safe(content.get("fecha")),
                    "url": f"{BASE_URL}/busqueda?o=0&p=1&r=id-infojus:{content.get('id-infojus','')}" if content.get("id-infojus") else "",
                }
            )
        except Exception:
            continue
    return out
