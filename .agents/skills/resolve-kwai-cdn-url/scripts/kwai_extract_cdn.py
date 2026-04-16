#!/usr/bin/env python3
"""Extract Kuaishou CDN URL from a share link."""

import argparse
import json
import random
import re
import sys
import time
from typing import Any, Dict, Iterable, List, Optional, Tuple
from urllib.parse import parse_qs, urlparse

import tls_client

from kwai_common import classify_bad_cdn_url, load_cookie_value

DEFAULT_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

MOBILE_UA = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 "
    "Mobile/15E148 Safari/604.1"
)

DEFAULT_ENDPOINTS = [
    "https://www.kuaishou.com/graphql",
    "https://live.kuaishou.com/m_graphql",
]

VISION_VIDEO_DETAIL_QUERY = (
    "query visionVideoDetail($photoId: String) {"
    "  visionVideoDetail(photoId: $photoId) {"
    "    photo {"
    "      photoUrl"
    "      mainNoWatermarkUrl"
    "      mainUrl"
    "      videoResource {"
    "        h265 { adaptSetRepresentation }"
    "        h264 { adaptSetRepresentation }"
    "      }"
    "      manifest"
    "    }"
    "  }"
    "}"
)

URL_FIELD_HINTS = (
    "photoUrl",
    "mainNoWatermarkUrl",
    "mainUrl",
    "playUrl",
    "srcNoMark",
    "videoUrl",
)

DOMAIN_HINTS = (
    "kuaishou",
    "kwaicdn",
    "ks-cdn",
    "ksyuncdn",
    "gifshow",
)


PHOTO_ID_RE = re.compile(r"/(?:photo|short-video)/([^/?#]+)")


def extract_first_url(text: str) -> Optional[str]:
    match = re.search(r"https?://[^\s\"'<>]+", text)
    if not match:
        return None
    return match.group(0).rstrip(").,;]}")


def _collect_urls(obj: Any, out: List[str]) -> None:
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str):
                if v.startswith("http"):
                    out.append(v)
            else:
                _collect_urls(v, out)
    elif isinstance(obj, list):
        for item in obj:
            _collect_urls(item, out)


def _rank_url(url: str) -> Tuple[int, int]:
    score = 0
    if any(h in url for h in DOMAIN_HINTS):
        score += 10
    if url.endswith(".mp4"):
        score += 5
    return (score, len(url))


def _pick_best_url(urls: Iterable[str]) -> Optional[str]:
    unique = list(
        dict.fromkeys(
            u for u in urls if u.startswith("http") and not classify_bad_cdn_url(u)
        )
    )
    if not unique:
        return None
    return sorted(unique, key=_rank_url, reverse=True)[0]


def _extract_photo_id(url: str) -> Optional[str]:
    match = PHOTO_ID_RE.search(url)
    if match:
        return match.group(1)
    parsed = urlparse(url)
    if parsed.path:
        parts = [p for p in parsed.path.split("/") if p]
        if parts:
            if parts[-1] and len(parts[-1]) >= 6:
                if parts[-2:] and parts[-2] in {"short-video", "photo", "video"}:
                    return parts[-1]
    qs = parse_qs(parsed.query)
    for key in ("photoId", "shareObjectId", "videoId", "shortVideoId"):
        if key in qs and qs[key]:
            return qs[key][0]
    return None


def _resolve_url(
    session: tls_client.Session,
    url: str,
    timeout: int = 10,
    proxy: Optional[str] = None,
) -> str:
    try:
        resp = session.get(
            url,
            allow_redirects=True,
            timeout_seconds=timeout,
            proxy=proxy,
        )
        return resp.url
    except Exception:
        return url


def _parse_init_state(html: str) -> Optional[Dict[str, Any]]:
    marker = "window.INIT_STATE="
    idx = html.find(marker)
    if idx < 0:
        return None
    start = idx + len(marker)
    depth = 0
    end = None
    for i in range(start, len(html)):
        ch = html[i]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    if end is None:
        return None
    payload = html[start:end]
    try:
        return json.loads(payload)
    except Exception:
        return None


def _search_dict_by_key(obj: Any, key: str) -> Iterable[Any]:
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == key:
                yield v
            if isinstance(v, dict) or isinstance(v, list):
                yield from _search_dict_by_key(v, key)
    elif isinstance(obj, list):
        for item in obj:
            yield from _search_dict_by_key(item, key)


def _extract_from_init_state(html: str) -> Optional[str]:
    state = _parse_init_state(html)
    if not state:
        return None
    reps = list(_search_dict_by_key(state, "representation"))
    if not reps:
        return None
    best = None
    best_score = -1
    for rep_list in reps:
        if not isinstance(rep_list, list):
            continue
        for rep in rep_list:
            if not isinstance(rep, dict):
                continue
            candidate = rep.get("url") or rep.get("cdnUrl") or rep.get("downloadUrl")
            if not candidate:
                continue
            size = rep.get("fileSize") or 0
            if size > best_score:
                best_score = size
                best = candidate
    return best


def _graphql_fetch(
    session: tls_client.Session,
    endpoint: str,
    photo_id: str,
    timeout: int,
    proxy: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    payload = {
        "operationName": "visionVideoDetail",
        "query": VISION_VIDEO_DETAIL_QUERY,
        "variables": {"photoId": photo_id},
    }
    try:
        resp = session.post(
            endpoint,
            json=payload,
            timeout_seconds=timeout,
            proxy=proxy,
        )
        if resp.status_code != 200:
            return None
        return resp.json()
    except Exception:
        return None


def _extract_from_graphql_payload(payload: Dict[str, Any]) -> Optional[str]:
    if not payload:
        return None
    data = payload.get("data") or {}
    detail = data.get("visionVideoDetail") or data.get("VisionVideoDetail") or {}
    photo = detail.get("photo") or detail.get("Photo") or {}
    urls: List[str] = []

    for field in URL_FIELD_HINTS:
        value = photo.get(field)
        if isinstance(value, str):
            urls.append(value)
        elif isinstance(value, list):
            urls.extend([v for v in value if isinstance(v, str)])

    if not urls:
        _collect_urls(payload, urls)

    return _pick_best_url(urls)


def _extract_from_html(html: str) -> Optional[str]:
    for pattern in (
        r"__APOLLO_STATE__\s*=\s*({.+?})\s*;",
        r"__NEXT_DATA__\s*=\s*({.+?})\s*</script>",
        r"__INITIAL_STATE__\s*=\s*({.+?})\s*;",
    ):
        match = re.search(pattern, html, re.DOTALL)
        if not match:
            continue
        try:
            data = json.loads(match.group(1))
        except Exception:
            continue
        urls: List[str] = []
        _collect_urls(data, urls)
        best = _pick_best_url(urls)
        if best:
            return best
    return None


def extract_cdn_url_detail(
    share_url: str,
    client_identifier: Optional[str] = None,
    cookie: Optional[str] = None,
    cookie_file: Optional[str] = None,
    proxy: Optional[str] = None,
    endpoints: Optional[List[str]] = None,
    timeout: int = 10,
    jitter: Tuple[float, float] = (0.0, 0.0),
) -> Tuple[Optional[str], str]:
    session_kwargs = {
        "client_identifier": client_identifier or "chrome_120",
        "random_tls_extension_order": True,
    }
    try:
        session = tls_client.Session(**session_kwargs)
    except Exception:
        session = tls_client.Session(
            client_identifier="chrome_120",
            random_tls_extension_order=True,
        )
    session.headers.update(
        {
            "User-Agent": DEFAULT_UA,
            "Referer": "https://www.kuaishou.com/",
            "Origin": "https://www.kuaishou.com",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        }
    )

    cookie = load_cookie_value(cookie=cookie, cookie_file=cookie_file)
    if cookie:
        session.headers["Cookie"] = cookie

    raw_url = extract_first_url(share_url) or share_url
    if jitter and (jitter[0] or jitter[1]):
        time.sleep(random.uniform(jitter[0], jitter[1]))

    resolved = _resolve_url(session, raw_url, timeout=timeout, proxy=proxy)
    photo_id = _extract_photo_id(resolved)
    if not photo_id:
        photo_id = _extract_photo_id(raw_url)
    if not photo_id:
        return None, "photoId not found"

    for endpoint in (endpoints or DEFAULT_ENDPOINTS):
        payload = _graphql_fetch(session, endpoint, photo_id, timeout, proxy=proxy)
        url = _extract_from_graphql_payload(payload or {})
        if url:
            bad_reason = classify_bad_cdn_url(url)
            if bad_reason:
                return None, bad_reason
            return url, ""

    try:
        mobile_url = f"https://m.kuaishou.com/fw/photo/{photo_id}"
        resp = session.get(
            mobile_url,
            headers={
                "User-Agent": MOBILE_UA,
                "Referer": "https://m.kuaishou.com/",
            },
            timeout_seconds=timeout,
            proxy=proxy,
            allow_redirects=True,
        )
        if resp.status_code == 200:
            url = _extract_from_init_state(resp.text)
            if url:
                bad_reason = classify_bad_cdn_url(url)
                if bad_reason:
                    return None, bad_reason
                return url, ""
    except Exception:
        pass

    try:
        resp = session.get(resolved, timeout_seconds=timeout, proxy=proxy)
        if resp.status_code == 200:
            url = _extract_from_html(resp.text)
            if url:
                bad_reason = classify_bad_cdn_url(url)
                if bad_reason:
                    return None, bad_reason
                return url, ""
    except Exception:
        pass

    return None, "cdn url not found"


def extract_cdn_url(
    share_url: str,
    client_identifier: Optional[str] = None,
    cookie: Optional[str] = None,
    cookie_file: Optional[str] = None,
    proxy: Optional[str] = None,
    endpoints: Optional[List[str]] = None,
    timeout: int = 10,
) -> Optional[str]:
    url, _ = extract_cdn_url_detail(
        share_url,
        client_identifier=client_identifier,
        cookie=cookie,
        cookie_file=cookie_file,
        proxy=proxy,
        endpoints=endpoints,
        timeout=timeout,
    )
    return url


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract Kuaishou CDN URL from a share link")
    parser.add_argument("url", help="Kuaishou share URL")
    parser.add_argument("--cookie", default=None, help="Raw Cookie header value")
    parser.add_argument(
        "--cookie-file",
        default=None,
        help="Path to a cookie.txt file or JSON cookie array",
    )
    parser.add_argument(
        "--proxy",
        default=None,
        help="Proxy URL, e.g. http://user:pass@host:port",
    )
    parser.add_argument(
        "--endpoint",
        action="append",
        default=None,
        help="GraphQL endpoint override (can be provided multiple times)",
    )
    parser.add_argument(
        "--jitter",
        default="0,0",
        help="Sleep between requests as min,max seconds (e.g., 1,3)",
    )
    parser.add_argument("--timeout", type=int, default=10, help="Request timeout (seconds)")
    args = parser.parse_args()

    jitter_vals = (0.0, 0.0)
    try:
        parts = [p.strip() for p in args.jitter.split(",")]
        if len(parts) == 2:
            jitter_vals = (float(parts[0]), float(parts[1]))
    except Exception:
        jitter_vals = (0.0, 0.0)

    url, err = extract_cdn_url_detail(
        args.url,
        cookie=args.cookie,
        cookie_file=args.cookie_file,
        proxy=args.proxy,
        endpoints=args.endpoint,
        timeout=args.timeout,
        jitter=jitter_vals,
    )

    if not url:
        print("", end="")
        return 2

    print(url)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
