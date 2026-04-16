from __future__ import annotations

import json
from typing import Any
from urllib.parse import quote

import httpx

BASE_URL = "https://eje.juscaba.gob.ar/iol-api/api/public"


class JuscabaError(Exception):
    pass


def search(query: str, limit: int = 10, timeout: float = 30.0) -> list[dict[str, Any]]:
    info = json.dumps({
        "filter": json.dumps({"identificador": query}),
        "tipoBusqueda": "PAR",
        "page": 0,
        "size": max(1, min(limit, 50)),
    })
    payload = f"info={quote(info)}"
    headers = {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"}
    try:
        with httpx.Client(timeout=timeout) as client:
            r = client.post(f"{BASE_URL}/expedientes/lista", content=payload, headers=headers)
            r.raise_for_status()
            data = r.json()
    except Exception as e:
        raise JuscabaError(str(e)) from e

    content = data.get("content", []) if isinstance(data, dict) else []
    out: list[dict[str, Any]] = []
    for item in content[:limit]:
        out.append(
            {
                "db": "juscaba",
                "id": item.get("expId") or item.get("id"),
                "title": item.get("caratula") or item.get("identificador") or "Expediente",
                "snippet": (item.get("objeto") or item.get("estado") or "")[:350],
                "date": "",
                "url": "https://eje.juscaba.gob.ar",
            }
        )
    return out
