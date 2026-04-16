#!/usr/bin/env python3
"""Shared helpers for Kwai/Kuaishou CSV+JSONL tooling."""

from __future__ import annotations

import json
import os
import tempfile
from typing import Dict, Optional, Set, Tuple

def classify_bad_cdn_url(url: str) -> Optional[str]:
    if not url:
        return None
    lower = url.strip().lower()
    if lower.startswith("https://live.kuaishou.com") or lower.startswith(
        "http://live.kuaishou.com"
    ):
        return "live.kuaishou.com is not a CDN url"
    if lower.startswith("https://captcha.zt.kuaishou.com") or lower.startswith(
        "http://captcha.zt.kuaishou.com"
    ):
        return f"captcha url is not a CDN url: {url}"
    return None


def is_success_record(
    item: Dict[str, object],
    cdn_field: str = "CDNURL",
    error_field: Optional[str] = "error_msg",
) -> bool:
    cdn = item.get(cdn_field) or item.get("CDNURL") or item.get("cdn_url") or item.get("cdnUrl")
    err = ""
    if error_field:
        err = item.get(error_field, "")
    elif "error_msg" in item:
        err = item.get("error_msg", "")
    if err is None:
        err = ""
    if isinstance(err, str):
        err = err.strip()
    return bool(isinstance(cdn, str) and cdn.strip()) and not err


def extract_url_from_record(item: Dict[str, object], url_field: str) -> str:
    for key in (url_field, "URL", "url"):
        val = item.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
    return ""


def load_resume_success_urls(
    output_path: str,
    url_field: str,
    cdn_field: str = "CDNURL",
    error_field: Optional[str] = "error_msg",
) -> Set[str]:
    resolved: Set[str] = set()
    try:
        with open(output_path, "r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    item = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if not isinstance(item, dict):
                    continue
                if not is_success_record(item, cdn_field=cdn_field, error_field=error_field):
                    continue
                url = extract_url_from_record(item, url_field)
                if url:
                    resolved.add(url)
    except FileNotFoundError:
        return set()
    return resolved


def clean_output_jsonl(
    output_path: str,
    cdn_field: str = "CDNURL",
    error_field: Optional[str] = "error_msg",
) -> Tuple[int, int]:
    kept = 0
    removed = 0
    try:
        with open(output_path, "r", encoding="utf-8") as handle:
            dir_name = os.path.dirname(output_path) or "."
            with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", delete=False, dir=dir_name
            ) as tmp:
                for line in handle:
                    raw = line.strip()
                    if not raw:
                        continue
                    try:
                        item = json.loads(raw)
                    except json.JSONDecodeError:
                        removed += 1
                        continue
                    if not isinstance(item, dict):
                        removed += 1
                        continue
                    if is_success_record(item, cdn_field=cdn_field, error_field=error_field):
                        tmp.write(json.dumps(item, ensure_ascii=False) + "\n")
                        kept += 1
                    else:
                        removed += 1
        os.replace(tmp.name, output_path)
    except FileNotFoundError:
        return (0, 0)
    return (kept, removed)


def load_cookie_value(
    cookie: Optional[str] = None,
    cookie_file: Optional[str] = None,
) -> Optional[str]:
    if cookie_file:
        try:
            cookie_text = open(cookie_file, "r", encoding="utf-8").read().strip()
        except Exception:
            cookie_text = ""
        if cookie_text:
            try:
                data = json.loads(cookie_text)
            except Exception:
                data = None
            if isinstance(data, dict) and "cookies" in data:
                data = data["cookies"]
            if isinstance(data, list):
                pairs = []
                for item in data:
                    if not isinstance(item, dict):
                        continue
                    name = item.get("name")
                    value = item.get("value")
                    if isinstance(name, str) and isinstance(value, str) and name:
                        pairs.append(f"{name}={value}")
                return "; ".join(pairs) if pairs else None
            return cookie_text
        return None
    return cookie
