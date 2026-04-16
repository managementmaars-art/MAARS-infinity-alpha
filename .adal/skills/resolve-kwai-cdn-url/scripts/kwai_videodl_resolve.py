#!/usr/bin/env python3
"""
Resolve Kuaishou share links to CDN URLs using videodl (videofetch).
Output JSONL: {"url": "...", "cdn_url": "...", "error_msg": "..."}
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import signal
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Iterable, List, Optional, Sequence, Tuple
from urllib.parse import urlparse

import requests
from videodl import videodl as videodl_lib

from kwai_common import classify_bad_cdn_url, clean_output_jsonl, load_cookie_value, load_resume_success_urls

UA_MOBILE = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1"
)
UA_DESKTOP = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

_INTERRUPTED = False


def _handle_sigint(signum, frame) -> None:
    del signum, frame
    global _INTERRUPTED
    _INTERRUPTED = True
    signal.signal(signal.SIGINT, signal.SIG_IGN)


def extract_first_url(text: str) -> Optional[str]:
    match = re.search(r"https?://[^\s]+", text)
    if not match:
        return None
    url = match.group(0)
    return url.strip(" \t\r\n\"'<>[](){}，。；;:!?")

def build_proxies(proxy: Optional[str]) -> Optional[dict]:
    if not proxy:
        return None
    scheme = urlparse(proxy).scheme.lower()
    if scheme == "http":
        return {"http": proxy}
    if scheme == "https":
        return {"https": proxy}
    return {"http": proxy, "https": proxy}


def resolve_short_url(url: str, timeout: float, proxy: Optional[str]) -> str:
    if "v.kuaishou.com" not in url:
        return url
    try:
        proxies = build_proxies(proxy)
        resp = requests.get(
            url,
            allow_redirects=True,
            timeout=timeout,
            headers={"User-Agent": UA_MOBILE},
            proxies=proxies,
        )
        return resp.url or url
    except requests.RequestException:
        return url


def fetch_anonymous_cookie(
    timeout: float, proxy: Optional[str]
) -> Optional[str]:
    proxies = build_proxies(proxy)
    session = requests.Session()
    headers = {
        "User-Agent": UA_DESKTOP,
        "Referer": "https://www.kuaishou.com/",
        "Origin": "https://www.kuaishou.com",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    }
    try:
        session.get(
            "https://www.kuaishou.com/",
            timeout=timeout,
            headers=headers,
            proxies=proxies,
        )
    except requests.RequestException:
        return None
    if not session.cookies:
        return None
    pairs = [f"{c.name}={c.value}" for c in session.cookies]
    return "; ".join(pairs) if pairs else None


def detect_unavailable_reason(
    url: str, timeout: float, proxy: Optional[str]
) -> Optional[str]:
    try:
        proxies = build_proxies(proxy)
        resp = requests.get(
            url,
            allow_redirects=True,
            timeout=timeout,
            headers={"User-Agent": UA_MOBILE},
            proxies=proxies,
        )
    except requests.RequestException as exc:
        return f"http error: {exc}"
    if not resp.text:
        return None
    text = resp.text
    keywords = [
        ("找不到该作品", "not found: removed or unavailable"),
        ("作品已失效", "not found: removed or unavailable"),
        ("该作品已被删除", "deleted by author"),
        ("已下架", "removed from shelf"),
        ("内容不可见", "content not visible"),
        ("内容不存在", "content not found"),
    ]
    for needle, message in keywords:
        if needle in text:
            return message
    return None


def pick_download_url(info: dict) -> Optional[str]:
    for key in ("download_url", "download_urls", "url", "urls"):
        val = info.get(key)
        if isinstance(val, str) and val:
            return val
        if isinstance(val, list):
            for item in val:
                if isinstance(item, str) and item:
                    return item
                if isinstance(item, dict):
                    for subkey in ("download_url", "download_urls", "url", "urls"):
                        subval = item.get(subkey)
                        if isinstance(subval, str) and subval:
                            return subval
                        if isinstance(subval, list):
                            for subitem in subval:
                                if isinstance(subitem, str) and subitem:
                                    return subitem
    return None


def resolve_cdn_url(url: str, request_overrides: Optional[dict]) -> str:
    video_client = videodl_lib.VideoClient(
        allowed_video_sources=["KuaishouVideoClient"],
        requests_overrides={"KuaishouVideoClient": request_overrides or {}},
    )
    video_infos = video_client.parsefromurl(url)
    if not video_infos:
        return ""
    for info in video_infos:
        cdn = pick_download_url(info)
        if cdn:
            return cdn
    return ""


def process_one(
    text: str,
    timeout: float,
    proxy: Optional[str],
    cookie: Optional[str],
    cookie_file: Optional[str],
    anonymous_cookie: Optional[str],
) -> dict:
    raw = text.strip()
    result = {"url": "", "cdn_url": "", "error_msg": ""}
    if not raw:
        result["error_msg"] = "empty input"
        return result

    url = extract_first_url(raw) or raw
    result["url"] = url
    if not url.startswith("http"):
        result["error_msg"] = "no http/https url found"
        return result

    resolved = resolve_short_url(url, timeout=timeout, proxy=proxy)
    request_overrides = {"timeout": timeout}
    if proxy:
        request_overrides["proxies"] = build_proxies(proxy)
    headers = dict(request_overrides.get("headers") or {})
    headers.setdefault("User-Agent", UA_MOBILE)
    headers.setdefault("Referer", "https://www.kuaishou.com/")
    headers.setdefault("Origin", "https://www.kuaishou.com")
    headers.setdefault("Accept-Language", "zh-CN,zh;q=0.9,en;q=0.8")
    cookie_value = load_cookie_value(cookie=cookie, cookie_file=cookie_file)
    if not cookie_value and anonymous_cookie:
        cookie_value = anonymous_cookie
    if cookie_value:
        headers["Cookie"] = cookie_value
    if headers:
        request_overrides["headers"] = headers
    try:
        cdn_url = resolve_cdn_url(resolved, request_overrides)
        if not cdn_url:
            reason = detect_unavailable_reason(
                resolved, timeout=timeout, proxy=proxy
            )
            result["error_msg"] = reason or "cdn url not found in videodl response"
        else:
            bad_reason = classify_bad_cdn_url(cdn_url)
            if bad_reason:
                result["error_msg"] = bad_reason
            else:
                result["cdn_url"] = cdn_url
    except Exception as exc:  # pylint: disable=broad-except
        result["error_msg"] = str(exc)

    return result


def load_inputs(input_text: Optional[str]) -> List[str]:
    items: List[str] = []
    if input_text:
        items.append(input_text)
    return items


def write_jsonl(
    items: Iterable[dict], output_path: Optional[str], append: bool = False
) -> None:
    if output_path:
        mode = "a" if append else "w"
        out = open(output_path, mode, encoding="utf-8")
    else:
        out = sys.stdout
    try:
        for item in items:
            out.write(json.dumps(item, ensure_ascii=False) + "\n")
    finally:
        if output_path:
            out.close()


def load_csv_rows(
    csv_path: str,
    url_field: str,
) -> Tuple[List[dict], List[str], str]:
    with open(csv_path, "r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle)
        try:
            header = next(reader)
        except StopIteration:
            return [], [], url_field

        header = [col.strip() for col in header]
        kept_indices = [idx for idx, col in enumerate(header) if col]
        kept_headers = [header[idx] for idx in kept_indices]
        if not kept_headers:
            return [], [], url_field

        url_lookup = {name.lower(): name for name in kept_headers}
        if url_field not in kept_headers:
            mapped = url_lookup.get(url_field.lower())
            if mapped:
                url_field = mapped
            else:
                raise ValueError(f"URL field '{url_field}' not found in CSV header")

        rows: List[dict] = []
        for row in reader:
            if not row or not any(cell.strip() for cell in row):
                continue
            record: dict = {}
            for idx, name in zip(kept_indices, kept_headers):
                record[name] = row[idx].strip() if idx < len(row) else ""
            rows.append(record)

    return rows, kept_headers, url_field


def process_batch(
    batch: List[str],
    timeout: float,
    proxy: Optional[str],
    cookie: Optional[str],
    cookie_file: Optional[str],
    workers: int,
    progress_every: int,
    completed_offset: int,
    total: int,
    anonymous_cookie: Optional[str],
) -> List[dict]:
    global _INTERRUPTED
    if workers <= 1 or len(batch) == 1:
        results = []
        for idx, item in enumerate(batch, start=1):
            if _INTERRUPTED:
                break
            results.append(
                process_one(
                    item,
                    timeout=timeout,
                    proxy=proxy,
                    cookie=cookie,
                    cookie_file=cookie_file,
                    anonymous_cookie=anonymous_cookie,
                )
            )
            if progress_every > 0 and idx % progress_every == 0:
                done = completed_offset + idx
                print(f"progress: {done}/{total}", file=sys.stderr)
        if _INTERRUPTED:
            for item in batch[len(results) :]:
                results.append(
                    {"url": item, "cdn_url": "", "error_msg": "interrupted"}
                )
        return results

    results: List[Optional[dict]] = [None] * len(batch)
    completed = 0
    executor = ThreadPoolExecutor(max_workers=workers)
    try:
        future_map = {
            executor.submit(
                process_one,
                item,
                timeout,
                proxy,
                cookie,
                cookie_file,
                anonymous_cookie,
            ): idx
            for idx, item in enumerate(batch)
        }
        for future in as_completed(future_map):
            if _INTERRUPTED:
                break
            idx = future_map[future]
            try:
                results[idx] = future.result()
            except Exception as exc:  # pylint: disable=broad-except
                results[idx] = {
                    "url": batch[idx],
                    "cdn_url": "",
                    "error_msg": str(exc),
                }
            completed += 1
            if progress_every > 0 and completed % progress_every == 0:
                done = completed_offset + completed
                print(f"progress: {done}/{total}", file=sys.stderr)
    except KeyboardInterrupt:
        _INTERRUPTED = True
    finally:
        executor.shutdown(wait=False, cancel_futures=True)

    if _INTERRUPTED:
        for idx, item in enumerate(results):
            if item is None:
                results[idx] = {
                    "url": batch[idx],
                    "cdn_url": "",
                    "error_msg": "interrupted",
                }

    return [item for item in results if item is not None]


def build_csv_output_rows(
    rows: Sequence[dict],
    headers: Sequence[str],
    results: Sequence[dict],
) -> List[dict]:
    output: List[dict] = []
    for row, result in zip(rows, results):
        record = {name: row.get(name, "") for name in headers}
        record["CDNURL"] = result.get("cdn_url", "")
        record["error_msg"] = result.get("error_msg", "")
        output.append(record)
    return output


def main() -> int:
    signal.signal(signal.SIGINT, _handle_sigint)
    parser = argparse.ArgumentParser(
        description="Resolve Kuaishou share links to CDN URLs and output JSONL."
    )
    parser.add_argument("input", nargs="?", help="Share text or URL")
    parser.add_argument("--input-csv", help="CSV file with URL field and other columns")
    parser.add_argument(
        "--csv-url-field",
        default="URL",
        help="CSV column name containing the share URL",
    )
    parser.add_argument("--output", help="Write JSONL to this file (default: stdout)")
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Skip URLs already resolved in output JSONL (CSV mode only)",
    )
    parser.add_argument(
        "--proxy",
        default=None,
        help="Proxy URL, e.g. http://user:pass@host:port",
    )
    parser.add_argument("--cookie", default=None, help="Raw Cookie header value")
    parser.add_argument(
        "--cookie-file",
        default=None,
        help="Path to a cookie.txt file or JSON cookie array",
    )
    parser.add_argument("--workers", type=int, default=5, help="Concurrent workers")
    parser.add_argument("--timeout", type=float, default=15.0, help="HTTP timeout (s)")
    parser.add_argument(
        "--batch-size", type=int, default=10, help="Batch size for append output"
    )
    parser.add_argument(
        "--progress-every",
        type=int,
        default=1,
        help="Print progress every N items (stderr)",
    )
    args = parser.parse_args()

    if not args.input and not args.input_csv:
        parser.error("Provide input text/URL or --input-csv")
    if args.input_csv and args.input:
        parser.error("Use only one input source: --input-csv or text")
    if args.resume and not args.input_csv:
        parser.error("--resume is only supported with --input-csv")

    anonymous_cookie = None
    if not args.cookie and not args.cookie_file:
        anonymous_cookie = fetch_anonymous_cookie(args.timeout, args.proxy)

    if args.input_csv:
        if args.resume and (not args.output or args.output == "-"):
            parser.error("--resume requires --output file")
        try:
            rows, headers, url_field = load_csv_rows(
                args.input_csv, args.csv_url_field
            )
        except ValueError as exc:
            parser.error(str(exc))
        if not rows:
            parser.error("No usable CSV rows found")

        skipped = 0
        total = len(rows)
        if args.resume:
            kept, removed = clean_output_jsonl(
                args.output,
                cdn_field="CDNURL",
                error_field="error_msg",
            )
            if removed:
                print(f"resume: removed {removed} failed rows", file=sys.stderr)
            resume_urls = load_resume_success_urls(
                args.output,
                url_field,
                cdn_field="CDNURL",
                error_field="error_msg",
            )
            if resume_urls:
                rows = [
                    row
                    for row in rows
                    if row.get(url_field, "").strip() not in resume_urls
                ]
                skipped = total - len(rows)
                if skipped:
                    print(
                        f"resume: skipped {skipped} already resolved",
                        file=sys.stderr,
                    )
            if not rows:
                print("resume: all rows already resolved", file=sys.stderr)
                return 0

        total_remaining = len(rows)
        batch_size = max(1, args.batch_size)
        completed = skipped
        first_write = not args.resume
        for start in range(0, total_remaining, batch_size):
            batch_rows = rows[start : start + batch_size]
            batch_inputs = [row.get(url_field, "") for row in batch_rows]
            results = process_batch(
                batch=batch_inputs,
                timeout=args.timeout,
                proxy=args.proxy,
                cookie=args.cookie,
                cookie_file=args.cookie_file,
                workers=args.workers,
                progress_every=args.progress_every,
                completed_offset=completed,
                total=total,
                anonymous_cookie=anonymous_cookie,
            )
            output_rows = build_csv_output_rows(batch_rows, headers, results)
            write_jsonl(output_rows, args.output, append=not first_write)
            first_write = False
            completed += len(batch_rows)
            if args.progress_every > 0:
                print(f"progress: {completed}/{total}", file=sys.stderr)
            if _INTERRUPTED:
                print("Interrupted by user, exiting gracefully.", file=sys.stderr)
                return 130
        return 0

    inputs = load_inputs(args.input)
    if not inputs:
        parser.error("No usable input lines found")

    batch_size = max(1, args.batch_size)
    total = len(inputs)
    completed = 0
    first_write = True
    for start in range(0, total, batch_size):
        batch = inputs[start : start + batch_size]
        results = process_batch(
            batch=batch,
            timeout=args.timeout,
            proxy=args.proxy,
            cookie=args.cookie,
            cookie_file=args.cookie_file,
            workers=args.workers,
            progress_every=args.progress_every,
            completed_offset=completed,
            total=total,
            anonymous_cookie=anonymous_cookie,
        )
        write_jsonl(results, args.output, append=not first_write)
        first_write = False
        completed += len(batch)
        if args.progress_every > 0:
            print(f"progress: {completed}/{total}", file=sys.stderr)
        if _INTERRUPTED:
            print("Interrupted by user, exiting gracefully.", file=sys.stderr)
            return 130
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
