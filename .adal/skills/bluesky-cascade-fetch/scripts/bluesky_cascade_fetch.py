#!/usr/bin/env python3
"""Fetch Bluesky posts and reply cascades with retries, throttling, and schema checks."""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any
from urllib import parse, request
from urllib.error import HTTPError, URLError

ENV_BASE_URL = "BLUESKY_BASE_URL"
ENV_AUTH_SERVICE_URL = "BLUESKY_AUTH_SERVICE_URL"
ENV_IDENTIFIER = "BLUESKY_IDENTIFIER"
ENV_APP_PASSWORD = "BLUESKY_APP_PASSWORD"
ENV_TIMEOUT_SECONDS = "BLUESKY_TIMEOUT_SECONDS"
ENV_MAX_RETRIES = "BLUESKY_MAX_RETRIES"
ENV_RETRY_BACKOFF_SECONDS = "BLUESKY_RETRY_BACKOFF_SECONDS"
ENV_RETRY_BACKOFF_MULTIPLIER = "BLUESKY_RETRY_BACKOFF_MULTIPLIER"
ENV_MIN_REQUEST_INTERVAL_SECONDS = "BLUESKY_MIN_REQUEST_INTERVAL_SECONDS"
ENV_PAGE_SIZE = "BLUESKY_PAGE_SIZE"
ENV_MAX_PAGES_PER_RUN = "BLUESKY_MAX_PAGES_PER_RUN"
ENV_MAX_POSTS_PER_RUN = "BLUESKY_MAX_POSTS_PER_RUN"
ENV_MAX_THREADS_PER_RUN = "BLUESKY_MAX_THREADS_PER_RUN"
ENV_THREAD_DEPTH = "BLUESKY_THREAD_DEPTH"
ENV_THREAD_PARENT_HEIGHT = "BLUESKY_THREAD_PARENT_HEIGHT"
ENV_MAX_RETRY_AFTER_SECONDS = "BLUESKY_MAX_RETRY_AFTER_SECONDS"
ENV_USER_AGENT = "BLUESKY_USER_AGENT"

DEFAULT_BASE_URL = "https://public.api.bsky.app"
FALLBACK_PUBLIC_READ_BASE_URL = "https://api.bsky.app"
DEFAULT_AUTH_SERVICE_URL = "https://bsky.social"
DEFAULT_TIMEOUT_SECONDS = 45
DEFAULT_MAX_RETRIES = 4
DEFAULT_RETRY_BACKOFF_SECONDS = 1.5
DEFAULT_RETRY_BACKOFF_MULTIPLIER = 2.0
DEFAULT_MIN_REQUEST_INTERVAL_SECONDS = 0.4
DEFAULT_PAGE_SIZE = 25
DEFAULT_MAX_PAGES_PER_RUN = 20
DEFAULT_MAX_POSTS_PER_RUN = 300
DEFAULT_MAX_THREADS_PER_RUN = 80
DEFAULT_THREAD_DEPTH = 8
DEFAULT_THREAD_PARENT_HEIGHT = 5
DEFAULT_MAX_RETRY_AFTER_SECONDS = 120
DEFAULT_USER_AGENT = "bluesky-cascade-fetch/1.0"

MAX_API_PAGE_SIZE = 100
MAX_THREAD_DEPTH = 1000
MAX_THREAD_PARENT_HEIGHT = 1000
RETRIABLE_HTTP_CODES = {429, 500, 502, 503, 504}

SOURCE_MODE_SEARCH = "search"
SOURCE_MODE_AUTHOR_FEED = "author-feed"
SOURCE_MODE_FEED = "feed"
SOURCE_MODE_LIST_FEED = "list-feed"
SOURCE_MODES = (
    SOURCE_MODE_SEARCH,
    SOURCE_MODE_AUTHOR_FEED,
    SOURCE_MODE_FEED,
    SOURCE_MODE_LIST_FEED,
)
AUTHOR_FEED_FILTERS = (
    "posts_with_replies",
    "posts_no_replies",
    "posts_with_media",
    "posts_and_author_threads",
    "posts_with_video",
)

XRPC_SEARCH_POSTS = "/xrpc/app.bsky.feed.searchPosts"
XRPC_GET_AUTHOR_FEED = "/xrpc/app.bsky.feed.getAuthorFeed"
XRPC_GET_FEED = "/xrpc/app.bsky.feed.getFeed"
XRPC_GET_LIST_FEED = "/xrpc/app.bsky.feed.getListFeed"
XRPC_GET_POST_THREAD = "/xrpc/app.bsky.feed.getPostThread"
XRPC_CREATE_SESSION = "/xrpc/com.atproto.server.createSession"

THREAD_VIEW_TYPE = "app.bsky.feed.defs#threadViewPost"
THREAD_NOT_FOUND_TYPE = "app.bsky.feed.defs#notFoundPost"
THREAD_BLOCKED_TYPE = "app.bsky.feed.defs#blockedPost"
MISSING_THREAD_NODE_TYPES = {THREAD_NOT_FOUND_TYPE, THREAD_BLOCKED_TYPE}

SEARCH_SORT_LATEST = "latest"


@dataclass(frozen=True)
class RuntimeConfig:
    api_base_url: str
    auth_service_url: str
    identifier: str
    app_password: str
    timeout_seconds: int
    max_retries: int
    retry_backoff_seconds: float
    retry_backoff_multiplier: float
    min_request_interval_seconds: float
    page_size: int
    max_pages_per_run: int
    max_posts_per_run: int
    max_threads_per_run: int
    thread_depth: int
    thread_parent_height: int
    max_retry_after_seconds: int
    user_agent: str


@dataclass(frozen=True)
class AuthSession:
    did: str
    handle: str
    access_jwt: str


@dataclass(frozen=True)
class HttpJsonResponse:
    url: str
    status_code: int
    headers: dict[str, str]
    payload: dict[str, Any]
    byte_length: int


@dataclass(frozen=True)
class SeedFetchResult:
    seeds: list[dict[str, Any]]
    page_trace: list[dict[str, Any]]
    stop_reason: str
    hits_total: int | None
    issue_count: int
    issues: list[dict[str, Any]]
    skipped_outside_window: int
    skipped_no_timestamp: int
    duplicate_seed_count: int


@dataclass(frozen=True)
class ThreadFetchResult:
    threads: list[dict[str, Any]]
    issue_count: int
    issues: list[dict[str, Any]]
    success_count: int
    failure_count: int
    skipped_count: int


def env_or_default(name: str, default: str) -> str:
    value = os.environ.get(name, "").strip()
    return value or default


def parse_positive_int(name: str, raw: str) -> int:
    try:
        value = int(raw)
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer, got: {raw!r}") from exc
    if value <= 0:
        raise ValueError(f"{name} must be > 0, got: {value}")
    return value


def parse_non_negative_int(name: str, raw: str) -> int:
    try:
        value = int(raw)
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer, got: {raw!r}") from exc
    if value < 0:
        raise ValueError(f"{name} must be >= 0, got: {value}")
    return value


def parse_positive_float(name: str, raw: str) -> float:
    try:
        value = float(raw)
    except ValueError as exc:
        raise ValueError(f"{name} must be a number, got: {raw!r}") from exc
    if value <= 0:
        raise ValueError(f"{name} must be > 0, got: {value}")
    return value


def parse_non_negative_float(name: str, raw: str) -> float:
    try:
        value = float(raw)
    except ValueError as exc:
        raise ValueError(f"{name} must be a number, got: {raw!r}") from exc
    if value < 0:
        raise ValueError(f"{name} must be >= 0, got: {value}")
    return value


def normalize_base_url(value: str, *, field_name: str) -> str:
    normalized = value.strip().rstrip("/")
    if not normalized:
        raise ValueError(f"{field_name} cannot be empty.")
    if not normalized.startswith("http://") and not normalized.startswith("https://"):
        raise ValueError(
            f"{field_name} must start with http:// or https://, got: {normalized!r}"
        )
    return normalized


def ensure_page_size(value: int, *, field_name: str) -> int:
    if value < 1 or value > MAX_API_PAGE_SIZE:
        raise ValueError(f"{field_name} must be between 1 and {MAX_API_PAGE_SIZE}, got: {value}")
    return value


def ensure_thread_depth(value: int, *, field_name: str) -> int:
    if value < 0 or value > MAX_THREAD_DEPTH:
        raise ValueError(f"{field_name} must be between 0 and {MAX_THREAD_DEPTH}, got: {value}")
    return value


def ensure_thread_parent_height(value: int, *, field_name: str) -> int:
    if value < 0 or value > MAX_THREAD_PARENT_HEIGHT:
        raise ValueError(
            f"{field_name} must be between 0 and {MAX_THREAD_PARENT_HEIGHT}, got: {value}"
        )
    return value


def mask_secret(value: str) -> str:
    if not value:
        return ""
    if len(value) <= 8:
        return "*" * len(value)
    return f"{value[:4]}...{value[-4:]}"


def parse_datetime_flexible(value: str) -> datetime | None:
    text = value.strip()
    if not text:
        return None

    candidates = [text]
    if text.endswith("Z"):
        candidates.append(text[:-1] + "+00:00")

    for candidate in candidates:
        try:
            dt = datetime.fromisoformat(candidate)
        except ValueError:
            continue
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)

    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
        try:
            dt = datetime.strptime(text, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
        return dt

    try:
        dt = datetime.strptime(text, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        return dt
    except ValueError:
        return None


def parse_datetime_utc(raw: str, *, field_name: str, is_end: bool) -> datetime:
    text = raw.strip()
    if not text:
        raise ValueError(f"{field_name} cannot be empty.")

    dt = parse_datetime_flexible(text)
    if dt is None:
        raise ValueError(
            f"{field_name} is invalid: {raw!r}. Use ISO-8601 datetime, for example 2026-03-10T00:00:00Z."
        )

    if len(text) == 10 and text.count("-") == 2 and is_end:
        return dt + timedelta(days=1)
    return dt


def to_rfc3339_z(value: datetime) -> str:
    return value.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def within_window(
    timestamp: datetime | None, start_dt: datetime | None, end_dt: datetime | None
) -> bool:
    if start_dt is None and end_dt is None:
        return True
    if timestamp is None:
        return False
    if start_dt is not None and timestamp < start_dt:
        return False
    if end_dt is not None and timestamp >= end_dt:
        return False
    return True


def to_int_if_valid(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.strip():
        try:
            return int(value)
        except ValueError:
            return None
    return None


def add_issue(
    issues: list[dict[str, Any]],
    issue_count: int,
    max_issues: int,
    issue: dict[str, Any],
) -> int:
    new_count = issue_count + 1
    if len(issues) < max_issues:
        issues.append(issue)
    return new_count


def extend_issue_samples(
    target: list[dict[str, Any]], source: list[dict[str, Any]], max_issues: int
) -> None:
    if max_issues <= len(target):
        return
    remaining = max_issues - len(target)
    target.extend(source[:remaining])


def build_runtime_config(args: argparse.Namespace) -> RuntimeConfig:
    api_base_url = normalize_base_url(
        (
            args.base_url
            if getattr(args, "base_url", "").strip()
            else env_or_default(ENV_BASE_URL, DEFAULT_BASE_URL)
        ),
        field_name="API base URL",
    )
    auth_service_url = normalize_base_url(
        (
            args.auth_service_url
            if getattr(args, "auth_service_url", "").strip()
            else env_or_default(ENV_AUTH_SERVICE_URL, DEFAULT_AUTH_SERVICE_URL)
        ),
        field_name="Auth service URL",
    )
    identifier = (
        args.identifier
        if getattr(args, "identifier", "") is not None and args.identifier.strip()
        else env_or_default(ENV_IDENTIFIER, "")
    ).strip()
    app_password = (
        args.app_password
        if getattr(args, "app_password", "") is not None and args.app_password.strip()
        else env_or_default(ENV_APP_PASSWORD, "")
    ).strip()
    if bool(identifier) != bool(app_password):
        raise ValueError(
            "BLUESKY_IDENTIFIER and BLUESKY_APP_PASSWORD must be set together (or both unset)."
        )

    timeout_seconds = parse_positive_int(
        "--timeout-seconds",
        str(
            args.timeout_seconds
            if getattr(args, "timeout_seconds", None) is not None
            else env_or_default(ENV_TIMEOUT_SECONDS, str(DEFAULT_TIMEOUT_SECONDS))
        ),
    )
    max_retries = parse_non_negative_int(
        "--max-retries",
        str(
            args.max_retries
            if getattr(args, "max_retries", None) is not None
            else env_or_default(ENV_MAX_RETRIES, str(DEFAULT_MAX_RETRIES))
        ),
    )
    retry_backoff_seconds = parse_positive_float(
        "--retry-backoff-seconds",
        str(
            args.retry_backoff_seconds
            if getattr(args, "retry_backoff_seconds", None) is not None
            else env_or_default(ENV_RETRY_BACKOFF_SECONDS, str(DEFAULT_RETRY_BACKOFF_SECONDS))
        ),
    )
    retry_backoff_multiplier = parse_positive_float(
        "--retry-backoff-multiplier",
        str(
            args.retry_backoff_multiplier
            if getattr(args, "retry_backoff_multiplier", None) is not None
            else env_or_default(
                ENV_RETRY_BACKOFF_MULTIPLIER, str(DEFAULT_RETRY_BACKOFF_MULTIPLIER)
            )
        ),
    )
    min_request_interval_seconds = parse_non_negative_float(
        "--min-request-interval-seconds",
        str(
            args.min_request_interval_seconds
            if getattr(args, "min_request_interval_seconds", None) is not None
            else env_or_default(
                ENV_MIN_REQUEST_INTERVAL_SECONDS, str(DEFAULT_MIN_REQUEST_INTERVAL_SECONDS)
            )
        ),
    )
    page_size = ensure_page_size(
        parse_positive_int(
            "--page-size",
            str(
                args.page_size
                if getattr(args, "page_size", None) is not None
                else env_or_default(ENV_PAGE_SIZE, str(DEFAULT_PAGE_SIZE))
            ),
        ),
        field_name="page size",
    )
    max_pages_per_run = parse_positive_int(
        "--max-pages-per-run",
        str(
            args.max_pages_per_run
            if getattr(args, "max_pages_per_run", None) is not None
            else env_or_default(ENV_MAX_PAGES_PER_RUN, str(DEFAULT_MAX_PAGES_PER_RUN))
        ),
    )
    max_posts_per_run = parse_positive_int(
        "--max-posts-per-run",
        str(
            args.max_posts_per_run
            if getattr(args, "max_posts_per_run", None) is not None
            else env_or_default(ENV_MAX_POSTS_PER_RUN, str(DEFAULT_MAX_POSTS_PER_RUN))
        ),
    )
    max_threads_per_run = parse_positive_int(
        "--max-threads-per-run",
        str(
            args.max_threads_per_run
            if getattr(args, "max_threads_per_run", None) is not None
            else env_or_default(ENV_MAX_THREADS_PER_RUN, str(DEFAULT_MAX_THREADS_PER_RUN))
        ),
    )
    thread_depth = ensure_thread_depth(
        parse_non_negative_int(
            "--thread-depth",
            str(
                args.thread_depth
                if getattr(args, "thread_depth", None) is not None
                else env_or_default(ENV_THREAD_DEPTH, str(DEFAULT_THREAD_DEPTH))
            ),
        ),
        field_name="thread depth",
    )
    thread_parent_height = ensure_thread_parent_height(
        parse_non_negative_int(
            "--thread-parent-height",
            str(
                args.thread_parent_height
                if getattr(args, "thread_parent_height", None) is not None
                else env_or_default(ENV_THREAD_PARENT_HEIGHT, str(DEFAULT_THREAD_PARENT_HEIGHT))
            ),
        ),
        field_name="thread parent height",
    )
    max_retry_after_seconds = parse_non_negative_int(
        "--max-retry-after-seconds",
        str(
            args.max_retry_after_seconds
            if getattr(args, "max_retry_after_seconds", None) is not None
            else env_or_default(
                ENV_MAX_RETRY_AFTER_SECONDS, str(DEFAULT_MAX_RETRY_AFTER_SECONDS)
            )
        ),
    )
    user_agent = (
        args.user_agent
        if getattr(args, "user_agent", "") is not None and args.user_agent.strip()
        else env_or_default(ENV_USER_AGENT, DEFAULT_USER_AGENT)
    ).strip()
    if not user_agent:
        raise ValueError("User-Agent cannot be empty.")

    return RuntimeConfig(
        api_base_url=api_base_url,
        auth_service_url=auth_service_url,
        identifier=identifier,
        app_password=app_password,
        timeout_seconds=timeout_seconds,
        max_retries=max_retries,
        retry_backoff_seconds=retry_backoff_seconds,
        retry_backoff_multiplier=retry_backoff_multiplier,
        min_request_interval_seconds=min_request_interval_seconds,
        page_size=page_size,
        max_pages_per_run=max_pages_per_run,
        max_posts_per_run=max_posts_per_run,
        max_threads_per_run=max_threads_per_run,
        thread_depth=thread_depth,
        thread_parent_height=thread_parent_height,
        max_retry_after_seconds=max_retry_after_seconds,
        user_agent=user_agent,
    )


def build_logger(level: str, log_file: str) -> logging.Logger:
    logger = logging.getLogger("bluesky-cascade-fetch")
    logger.handlers.clear()
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    formatter = logging.Formatter(
        fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S%z",
    )

    stream_handler = logging.StreamHandler(sys.stderr)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    if log_file.strip():
        log_path = Path(log_file).expanduser().resolve()
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    logger.propagate = False
    return logger


class RetryableHttpClient:
    def __init__(self, config: RuntimeConfig, logger: logging.Logger) -> None:
        self._cfg = config
        self._logger = logger
        self._last_request_monotonic: float | None = None

    def _throttle(self) -> None:
        if self._last_request_monotonic is None:
            return
        gap = time.monotonic() - self._last_request_monotonic
        sleep_seconds = self._cfg.min_request_interval_seconds - gap
        if sleep_seconds > 0:
            self._logger.debug("throttle-sleep=%.3fs", sleep_seconds)
            time.sleep(sleep_seconds)

    @staticmethod
    def _parse_retry_after(value: str | None) -> float | None:
        if not value:
            return None
        text = value.strip()
        if not text:
            return None
        try:
            seconds = float(text)
        except ValueError:
            try:
                retry_time = parsedate_to_datetime(text)
            except (TypeError, ValueError, IndexError):
                return None
            if retry_time.tzinfo is None:
                retry_time = retry_time.replace(tzinfo=timezone.utc)
            delta = (retry_time - datetime.now(timezone.utc)).total_seconds()
            return max(0.0, delta)
        return seconds if seconds >= 0 else None

    @staticmethod
    def _format_http_error_message(code: int, body: bytes) -> str:
        if not body:
            return f"HTTP {code}"
        try:
            text = body.decode("utf-8", errors="replace")
        except Exception:
            return f"HTTP {code}"
        try:
            payload = json.loads(text)
        except json.JSONDecodeError:
            return text.strip()
        if isinstance(payload, dict):
            error = payload.get("error")
            message = payload.get("message")
            if isinstance(error, str) and isinstance(message, str):
                return f"{error}: {message}"
            if isinstance(error, str):
                return error
            if isinstance(message, str):
                return message
        return text.strip()

    def request_json(
        self,
        *,
        method: str,
        url: str,
        headers: dict[str, str] | None = None,
        body_json: dict[str, Any] | None = None,
    ) -> HttpJsonResponse:
        attempts = self._cfg.max_retries + 1
        payload_bytes = None
        if body_json is not None:
            payload_bytes = json.dumps(body_json, ensure_ascii=False).encode("utf-8")

        for attempt in range(1, attempts + 1):
            self._throttle()

            req = request.Request(url, method=method.upper())
            req.add_header("Accept", "application/json")
            req.add_header("User-Agent", self._cfg.user_agent)
            if headers:
                for key, value in headers.items():
                    req.add_header(key, value)
            if payload_bytes is not None:
                req.add_header("Content-Type", "application/json")

            self._logger.debug(
                "http-request attempt=%s/%s method=%s url=%s",
                attempt,
                attempts,
                req.get_method(),
                url,
            )
            try:
                with request.urlopen(req, data=payload_bytes, timeout=self._cfg.timeout_seconds) as resp:
                    body = resp.read()
                    self._last_request_monotonic = time.monotonic()
                    response_headers = {k.lower(): v for k, v in resp.headers.items()}
                    status_code = getattr(resp, "status", 200)
            except HTTPError as exc:
                self._last_request_monotonic = time.monotonic()
                body = b""
                try:
                    body = exc.read()
                except Exception:
                    body = b""
                is_retriable = exc.code in RETRIABLE_HTTP_CODES and attempt < attempts
                if is_retriable:
                    retry_after = self._parse_retry_after(exc.headers.get("Retry-After"))
                    if (
                        retry_after is not None
                        and retry_after > float(self._cfg.max_retry_after_seconds)
                    ):
                        raise RuntimeError(
                            f"Retry-After {retry_after:.3f}s exceeds cap {self._cfg.max_retry_after_seconds}s "
                            f"for {url}"
                        ) from exc
                    wait_seconds = (
                        retry_after
                        if retry_after is not None
                        else self._cfg.retry_backoff_seconds
                        * (self._cfg.retry_backoff_multiplier ** (attempt - 1))
                    )
                    self._logger.warning(
                        "http-retry status=%s attempt=%s/%s wait=%.3fs url=%s",
                        exc.code,
                        attempt,
                        attempts,
                        wait_seconds,
                        url,
                    )
                    time.sleep(wait_seconds)
                    continue
                message = self._format_http_error_message(exc.code, body)
                raise RuntimeError(f"HTTP {exc.code} for {url}: {message}") from exc
            except (URLError, TimeoutError) as exc:
                self._last_request_monotonic = time.monotonic()
                if attempt >= attempts:
                    raise RuntimeError(f"Request failed for {url}: {exc}") from exc
                wait_seconds = self._cfg.retry_backoff_seconds * (
                    self._cfg.retry_backoff_multiplier ** (attempt - 1)
                )
                self._logger.warning(
                    "network-retry attempt=%s/%s wait=%.3fs url=%s error=%s",
                    attempt,
                    attempts,
                    wait_seconds,
                    url,
                    exc,
                )
                time.sleep(wait_seconds)
                continue

            content_type = response_headers.get("content-type", "")
            if "json" not in content_type.lower():
                raise RuntimeError(
                    f"Unexpected content-type {content_type!r} for {url}. Expected JSON."
                )
            try:
                text = body.decode("utf-8")
            except UnicodeDecodeError as exc:
                raise RuntimeError(f"Response is not UTF-8 for {url}") from exc
            try:
                payload = json.loads(text)
            except json.JSONDecodeError as exc:
                raise RuntimeError(f"Response JSON decode failed for {url}") from exc
            if not isinstance(payload, dict):
                raise RuntimeError(f"Response payload must be a JSON object for {url}")

            return HttpJsonResponse(
                url=url,
                status_code=status_code,
                headers=response_headers,
                payload=payload,
                byte_length=len(body),
            )

        raise RuntimeError(f"Request exhausted retries for {url}")


class BlueskyApiClient:
    def __init__(self, config: RuntimeConfig, logger: logging.Logger) -> None:
        self._cfg = config
        self._logger = logger
        self._http = RetryableHttpClient(config, logger)
        self._session: AuthSession | None = None

    @staticmethod
    def _build_url(base_url: str, path: str, query: dict[str, Any] | None = None) -> str:
        encoded = ""
        if query:
            encoded = parse.urlencode(query, doseq=True)
        if encoded:
            return f"{base_url.rstrip('/')}{path}?{encoded}"
        return f"{base_url.rstrip('/')}{path}"

    def authenticate(self) -> AuthSession:
        if self._session is not None:
            return self._session
        if not self._cfg.identifier or not self._cfg.app_password:
            raise RuntimeError("Missing identifier/app-password for authenticated mode.")

        url = self._build_url(self._cfg.auth_service_url, XRPC_CREATE_SESSION)
        response = self._http.request_json(
            method="POST",
            url=url,
            body_json={
                "identifier": self._cfg.identifier,
                "password": self._cfg.app_password,
            },
        )
        access_jwt = response.payload.get("accessJwt")
        handle = response.payload.get("handle")
        did = response.payload.get("did")
        if not isinstance(access_jwt, str) or not access_jwt.strip():
            raise RuntimeError("Auth response missing accessJwt.")
        if not isinstance(handle, str) or not handle.strip():
            raise RuntimeError("Auth response missing handle.")
        if not isinstance(did, str) or not did.strip():
            raise RuntimeError("Auth response missing did.")

        self._session = AuthSession(
            did=did.strip(),
            handle=handle.strip(),
            access_jwt=access_jwt.strip(),
        )
        self._logger.info("auth-session-created handle=%s did=%s", self._session.handle, self._session.did)
        return self._session

    def query(
        self,
        *,
        path: str,
        query: dict[str, Any],
    ) -> HttpJsonResponse:
        use_authenticated_proxy = self._session is not None
        base_url = self._cfg.auth_service_url if use_authenticated_proxy else self._cfg.api_base_url
        url = self._build_url(base_url, path, query)
        headers: dict[str, str] = {}
        if self._session is not None:
            headers["Authorization"] = f"Bearer {self._session.access_jwt}"
        try:
            return self._http.request_json(method="GET", url=url, headers=headers)
        except RuntimeError as exc:
            if (
                not use_authenticated_proxy
                and normalize_base_url(base_url, field_name="base-url") == DEFAULT_BASE_URL
                and "HTTP 403" in str(exc)
            ):
                fallback_url = self._build_url(FALLBACK_PUBLIC_READ_BASE_URL, path, query)
                self._logger.warning(
                    "public-read-route-forbidden retry_with_base_url=%s path=%s",
                    FALLBACK_PUBLIC_READ_BASE_URL,
                    path,
                )
                return self._http.request_json(method="GET", url=fallback_url, headers=headers)
            raise


def parse_key_value(raw: str, *, field_name: str) -> tuple[str, str]:
    if "=" not in raw:
        raise ValueError(f"{field_name} must use key=value format, got: {raw!r}")
    key, value = raw.split("=", 1)
    key = key.strip()
    value = value.strip()
    if not key:
        raise ValueError(f"{field_name} key cannot be empty.")
    return key, value


def normalize_post_view(
    post: dict[str, Any],
    *,
    source_mode: str,
    page_number: int | None,
    item_index: int | None,
) -> tuple[dict[str, Any], datetime | None]:
    uri = post.get("uri")
    uri_value = uri.strip() if isinstance(uri, str) else ""

    author = post.get("author")
    author_did = None
    author_handle = None
    if isinstance(author, dict):
        did = author.get("did")
        handle = author.get("handle")
        if isinstance(did, str) and did.strip():
            author_did = did.strip()
        if isinstance(handle, str) and handle.strip():
            author_handle = handle.strip()

    indexed_at = post.get("indexedAt")
    indexed_at_value = indexed_at.strip() if isinstance(indexed_at, str) else None

    text = ""
    created_at_value = None
    root_uri = None
    parent_uri = None
    record = post.get("record")
    if isinstance(record, dict):
        raw_text = record.get("text")
        if isinstance(raw_text, str):
            text = raw_text
        created_at = record.get("createdAt")
        if isinstance(created_at, str) and created_at.strip():
            created_at_value = created_at.strip()
        reply = record.get("reply")
        if isinstance(reply, dict):
            root = reply.get("root")
            parent = reply.get("parent")
            if isinstance(root, dict):
                root_uri_raw = root.get("uri")
                if isinstance(root_uri_raw, str) and root_uri_raw.strip():
                    root_uri = root_uri_raw.strip()
            if isinstance(parent, dict):
                parent_uri_raw = parent.get("uri")
                if isinstance(parent_uri_raw, str) and parent_uri_raw.strip():
                    parent_uri = parent_uri_raw.strip()

    timestamp_source = None
    timestamp_raw = None
    timestamp_dt: datetime | None = None

    if created_at_value:
        timestamp_dt = parse_datetime_flexible(created_at_value)
        if timestamp_dt is not None:
            timestamp_source = "record.createdAt"
            timestamp_raw = created_at_value
    if timestamp_dt is None and indexed_at_value:
        timestamp_dt = parse_datetime_flexible(indexed_at_value)
        if timestamp_dt is not None:
            timestamp_source = "indexedAt"
            timestamp_raw = indexed_at_value

    normalized: dict[str, Any] = {
        "uri": uri_value or None,
        "cid": post.get("cid") if isinstance(post.get("cid"), str) else None,
        "source_mode": source_mode,
        "page_number": page_number,
        "item_index": item_index,
        "author": {
            "did": author_did,
            "handle": author_handle,
        },
        "created_at": created_at_value,
        "indexed_at": indexed_at_value,
        "timestamp_source": timestamp_source,
        "timestamp_raw": timestamp_raw,
        "timestamp_utc": to_rfc3339_z(timestamp_dt) if timestamp_dt is not None else None,
        "text": text,
        "reply_count": to_int_if_valid(post.get("replyCount")),
        "repost_count": to_int_if_valid(post.get("repostCount")),
        "like_count": to_int_if_valid(post.get("likeCount")),
        "quote_count": to_int_if_valid(post.get("quoteCount")),
        "langs": post.get("langs") if isinstance(post.get("langs"), list) else [],
        "reply_root_uri": root_uri,
        "reply_parent_uri": parent_uri,
    }
    return normalized, timestamp_dt


def validate_fetch_args(args: argparse.Namespace) -> None:
    if args.source_mode == SOURCE_MODE_SEARCH:
        if not args.query.strip():
            raise ValueError("--query is required when --source-mode=search.")
    elif args.source_mode == SOURCE_MODE_AUTHOR_FEED:
        if not args.actor.strip():
            raise ValueError("--actor is required when --source-mode=author-feed.")
    elif args.source_mode == SOURCE_MODE_FEED:
        if not args.feed_uri.strip():
            raise ValueError("--feed-uri is required when --source-mode=feed.")
    elif args.source_mode == SOURCE_MODE_LIST_FEED:
        if not args.list_uri.strip():
            raise ValueError("--list-uri is required when --source-mode=list-feed.")
    else:
        raise ValueError(f"Unsupported source mode: {args.source_mode}")

    if args.max_pages <= 0:
        raise ValueError("--max-pages must be > 0.")
    if args.max_posts <= 0:
        raise ValueError("--max-posts must be > 0.")
    if args.skip_threads:
        if args.max_threads < 0:
            raise ValueError("--max-threads must be >= 0 when --skip-threads is set.")
    else:
        if args.max_threads <= 0:
            raise ValueError("--max-threads must be > 0.")
    ensure_page_size(args.page_size, field_name="--page-size")
    ensure_thread_depth(args.thread_depth, field_name="--thread-depth")
    ensure_thread_parent_height(args.thread_parent_height, field_name="--thread-parent-height")
    if args.max_validation_issues <= 0:
        raise ValueError("--max-validation-issues must be > 0.")


def resolve_source_request(
    *,
    args: argparse.Namespace,
    start_dt: datetime | None,
    end_dt: datetime | None,
    cursor: str | None,
) -> tuple[str, dict[str, Any]]:
    if args.source_mode == SOURCE_MODE_SEARCH:
        query: dict[str, Any] = {
            "q": args.query.strip(),
            "sort": args.search_sort,
            "limit": args.page_size,
        }
        if args.search_author.strip():
            query["author"] = args.search_author.strip()
        if args.search_mentions.strip():
            query["mentions"] = args.search_mentions.strip()
        if args.search_lang.strip():
            query["lang"] = args.search_lang.strip()
        if args.search_domain.strip():
            query["domain"] = args.search_domain.strip()
        if args.search_url.strip():
            query["url"] = args.search_url.strip()
        if args.search_tag:
            query["tag"] = [tag.strip() for tag in args.search_tag if tag.strip()]
        if not args.disable_server_time_filter:
            if start_dt is not None:
                query["since"] = to_rfc3339_z(start_dt)
            if end_dt is not None:
                query["until"] = to_rfc3339_z(end_dt)
        if cursor:
            query["cursor"] = cursor
        return XRPC_SEARCH_POSTS, query

    if args.source_mode == SOURCE_MODE_AUTHOR_FEED:
        query = {
            "actor": args.actor.strip(),
            "limit": args.page_size,
            "filter": args.author_feed_filter,
            "includePins": "true" if args.include_pins else "false",
        }
        if cursor:
            query["cursor"] = cursor
        return XRPC_GET_AUTHOR_FEED, query

    if args.source_mode == SOURCE_MODE_FEED:
        query = {
            "feed": args.feed_uri.strip(),
            "limit": args.page_size,
        }
        if cursor:
            query["cursor"] = cursor
        return XRPC_GET_FEED, query

    if args.source_mode == SOURCE_MODE_LIST_FEED:
        query = {
            "list": args.list_uri.strip(),
            "limit": args.page_size,
        }
        if cursor:
            query["cursor"] = cursor
        return XRPC_GET_LIST_FEED, query

    raise ValueError(f"Unsupported source mode: {args.source_mode}")


def extract_posts_from_payload(
    payload: dict[str, Any],
    *,
    source_mode: str,
    page_number: int,
    issue_count: int,
    issues: list[dict[str, Any]],
    max_issues: int,
) -> tuple[list[dict[str, Any]], str | None, int]:
    if source_mode == SOURCE_MODE_SEARCH:
        posts = payload.get("posts")
        if not isinstance(posts, list):
            issue_count = add_issue(
                issues,
                issue_count,
                max_issues,
                {
                    "scope": "seed-fetch",
                    "type": "response_shape_error",
                    "message": "searchPosts response missing posts[]",
                    "page_number": page_number,
                },
            )
            return [], None, issue_count
        cursor = payload.get("cursor")
        cursor_value = cursor if isinstance(cursor, str) and cursor.strip() else None
        return [post for post in posts if isinstance(post, dict)], cursor_value, issue_count

    feed = payload.get("feed")
    if not isinstance(feed, list):
        issue_count = add_issue(
            issues,
            issue_count,
            max_issues,
            {
                "scope": "seed-fetch",
                "type": "response_shape_error",
                "message": "feed response missing feed[]",
                "page_number": page_number,
            },
        )
        return [], None, issue_count

    posts: list[dict[str, Any]] = []
    for idx, item in enumerate(feed):
        if not isinstance(item, dict):
            issue_count = add_issue(
                issues,
                issue_count,
                max_issues,
                {
                    "scope": "seed-fetch",
                    "type": "feed_item_not_object",
                    "page_number": page_number,
                    "item_index": idx,
                },
            )
            continue
        post = item.get("post")
        if not isinstance(post, dict):
            issue_count = add_issue(
                issues,
                issue_count,
                max_issues,
                {
                    "scope": "seed-fetch",
                    "type": "feed_item_missing_post",
                    "page_number": page_number,
                    "item_index": idx,
                },
            )
            continue
        posts.append(post)

    cursor = payload.get("cursor")
    cursor_value = cursor if isinstance(cursor, str) and cursor.strip() else None
    return posts, cursor_value, issue_count


def source_is_desc_time(args: argparse.Namespace) -> bool:
    if args.source_mode in {SOURCE_MODE_AUTHOR_FEED, SOURCE_MODE_FEED, SOURCE_MODE_LIST_FEED}:
        return True
    return args.source_mode == SOURCE_MODE_SEARCH and args.search_sort == SEARCH_SORT_LATEST


def fetch_seed_posts(
    *,
    client: BlueskyApiClient,
    args: argparse.Namespace,
    start_dt: datetime | None,
    end_dt: datetime | None,
    logger: logging.Logger,
) -> SeedFetchResult:
    seeds: list[dict[str, Any]] = []
    page_trace: list[dict[str, Any]] = []
    issues: list[dict[str, Any]] = []
    issue_count = 0
    skipped_outside_window = 0
    skipped_no_timestamp = 0
    duplicate_seed_count = 0
    seen_uris: set[str] = set()
    cursor: str | None = None
    stop_reason = "max_pages_reached"
    hits_total: int | None = None

    for page_number in range(1, args.max_pages + 1):
        path, query = resolve_source_request(
            args=args,
            start_dt=start_dt,
            end_dt=end_dt,
            cursor=cursor,
        )
        try:
            response = client.query(path=path, query=query)
        except RuntimeError as exc:
            message = str(exc)
            if (
                args.source_mode == SOURCE_MODE_SEARCH
                and cursor is not None
                and "HTTP 403" in message
            ):
                issue_count = add_issue(
                    issues,
                    issue_count,
                    args.max_validation_issues,
                    {
                        "scope": "seed-fetch",
                        "type": "cursor_forbidden",
                        "message": message,
                        "page_number": page_number,
                    },
                )
                stop_reason = "cursor_forbidden"
                logger.warning("search cursor request blocked; stop pagination page=%s", page_number)
                break
            raise

        if args.source_mode == SOURCE_MODE_SEARCH:
            hits_total_candidate = to_int_if_valid(response.payload.get("hitsTotal"))
            if hits_total_candidate is not None:
                hits_total = hits_total_candidate

        posts, next_cursor, issue_count = extract_posts_from_payload(
            response.payload,
            source_mode=args.source_mode,
            page_number=page_number,
            issue_count=issue_count,
            issues=issues,
            max_issues=args.max_validation_issues,
        )

        page_kept = 0
        page_timestamps: list[datetime] = []
        for item_index, post in enumerate(posts):
            normalized, timestamp_dt = normalize_post_view(
                post,
                source_mode=args.source_mode,
                page_number=page_number,
                item_index=item_index,
            )
            uri = normalized.get("uri")
            if not isinstance(uri, str) or not uri:
                issue_count = add_issue(
                    issues,
                    issue_count,
                    args.max_validation_issues,
                    {
                        "scope": "seed-fetch",
                        "type": "missing_post_uri",
                        "page_number": page_number,
                        "item_index": item_index,
                    },
                )
                continue
            if uri in seen_uris:
                duplicate_seed_count += 1
                continue
            seen_uris.add(uri)

            if timestamp_dt is not None:
                page_timestamps.append(timestamp_dt)

            if start_dt is not None or end_dt is not None:
                if timestamp_dt is None:
                    skipped_no_timestamp += 1
                    issue_count = add_issue(
                        issues,
                        issue_count,
                        args.max_validation_issues,
                        {
                            "scope": "seed-fetch",
                            "type": "missing_timestamp_for_window_filter",
                            "uri": uri,
                        },
                    )
                    continue
                if not within_window(timestamp_dt, start_dt, end_dt):
                    skipped_outside_window += 1
                    continue

            seeds.append(normalized)
            page_kept += 1

            if len(seeds) >= args.max_posts:
                stop_reason = "max_posts_reached"
                break

        page_trace.append(
            {
                "page_number": page_number,
                "request_url": response.url,
                "status_code": response.status_code,
                "response_bytes": response.byte_length,
                "input_post_count": len(posts),
                "kept_post_count": page_kept,
                "cursor_in_response": next_cursor is not None,
            }
        )
        logger.info(
            "seed-page page=%s input=%s kept=%s total_kept=%s",
            page_number,
            len(posts),
            page_kept,
            len(seeds),
        )

        if len(seeds) >= args.max_posts:
            break

        if start_dt is not None and source_is_desc_time(args) and page_timestamps:
            oldest_timestamp = min(page_timestamps)
            if oldest_timestamp < start_dt:
                stop_reason = "oldest_before_start_window"
                break

        if not next_cursor:
            stop_reason = "cursor_exhausted"
            break
        cursor = next_cursor
    else:
        stop_reason = "max_pages_reached"

    return SeedFetchResult(
        seeds=seeds,
        page_trace=page_trace,
        stop_reason=stop_reason,
        hits_total=hits_total,
        issue_count=issue_count,
        issues=issues,
        skipped_outside_window=skipped_outside_window,
        skipped_no_timestamp=skipped_no_timestamp,
        duplicate_seed_count=duplicate_seed_count,
    )


def flatten_thread_tree(
    *,
    root_node: dict[str, Any],
    requested_uri: str,
    max_issues: int,
) -> tuple[list[dict[str, Any]], int, list[dict[str, Any]]]:
    nodes: list[dict[str, Any]] = []
    issues: list[dict[str, Any]] = []
    issue_count = 0
    visited_uris: set[str] = set()

    stack: list[tuple[dict[str, Any], str | None, int]] = [(root_node, None, 0)]
    while stack:
        node, parent_uri, depth = stack.pop()
        if not isinstance(node, dict):
            issue_count = add_issue(
                issues,
                issue_count,
                max_issues,
                {
                    "scope": "thread",
                    "type": "non_object_thread_node",
                    "requested_uri": requested_uri,
                    "depth": depth,
                },
            )
            continue

        node_type_raw = node.get("$type")
        node_type = node_type_raw if isinstance(node_type_raw, str) else ""
        is_thread_view = node_type == THREAD_VIEW_TYPE or (
            not node_type and isinstance(node.get("post"), dict)
        )

        if is_thread_view:
            post = node.get("post")
            if not isinstance(post, dict):
                issue_count = add_issue(
                    issues,
                    issue_count,
                    max_issues,
                    {
                        "scope": "thread",
                        "type": "thread_node_missing_post",
                        "requested_uri": requested_uri,
                        "depth": depth,
                    },
                )
                continue

            normalized_post, _ = normalize_post_view(
                post,
                source_mode="thread",
                page_number=None,
                item_index=None,
            )
            uri = normalized_post.get("uri")
            if isinstance(uri, str) and uri:
                if uri in visited_uris:
                    issue_count = add_issue(
                        issues,
                        issue_count,
                        max_issues,
                        {
                            "scope": "thread",
                            "type": "duplicate_thread_uri",
                            "requested_uri": requested_uri,
                            "uri": uri,
                        },
                    )
                    continue
                visited_uris.add(uri)

            nodes.append(
                {
                    "uri": uri if isinstance(uri, str) and uri else None,
                    "parent_uri": parent_uri,
                    "depth": depth,
                    "node_type": THREAD_VIEW_TYPE,
                    "author": normalized_post["author"],
                    "created_at": normalized_post["created_at"],
                    "indexed_at": normalized_post["indexed_at"],
                    "timestamp_source": normalized_post["timestamp_source"],
                    "timestamp_utc": normalized_post["timestamp_utc"],
                    "text": normalized_post["text"],
                    "reply_count": normalized_post["reply_count"],
                    "repost_count": normalized_post["repost_count"],
                    "like_count": normalized_post["like_count"],
                    "quote_count": normalized_post["quote_count"],
                    "is_missing": False,
                }
            )

            replies = node.get("replies")
            if replies is None:
                replies = []
            if not isinstance(replies, list):
                issue_count = add_issue(
                    issues,
                    issue_count,
                    max_issues,
                    {
                        "scope": "thread",
                        "type": "invalid_replies_shape",
                        "requested_uri": requested_uri,
                        "uri": uri,
                    },
                )
                continue

            for child in reversed(replies):
                if isinstance(child, dict):
                    child_parent = uri if isinstance(uri, str) and uri else parent_uri
                    stack.append((child, child_parent, depth + 1))
                else:
                    issue_count = add_issue(
                        issues,
                        issue_count,
                        max_issues,
                        {
                            "scope": "thread",
                            "type": "non_object_reply_node",
                            "requested_uri": requested_uri,
                            "uri": uri,
                        },
                    )
            continue

        if node_type in MISSING_THREAD_NODE_TYPES:
            missing_uri = node.get("uri")
            nodes.append(
                {
                    "uri": missing_uri if isinstance(missing_uri, str) and missing_uri.strip() else None,
                    "parent_uri": parent_uri,
                    "depth": depth,
                    "node_type": node_type,
                    "author": None,
                    "created_at": None,
                    "indexed_at": None,
                    "timestamp_source": None,
                    "timestamp_utc": None,
                    "text": "",
                    "reply_count": None,
                    "repost_count": None,
                    "like_count": None,
                    "quote_count": None,
                    "is_missing": True,
                }
            )
            continue

        issue_count = add_issue(
            issues,
            issue_count,
            max_issues,
            {
                "scope": "thread",
                "type": "unknown_thread_node_type",
                "requested_uri": requested_uri,
                "node_type": node_type or None,
                "depth": depth,
            },
        )

    return nodes, issue_count, issues


def validate_thread_nodes(
    *,
    requested_uri: str,
    nodes: list[dict[str, Any]],
    max_issues: int,
) -> dict[str, Any]:
    issues: list[dict[str, Any]] = []
    issue_count = 0
    uri_set = {
        node["uri"] for node in nodes if isinstance(node.get("uri"), str) and node["uri"]
    }

    branch_count: dict[str, int] = {}
    max_depth = 0
    orphan_count = 0
    missing_node_count = 0

    for node in nodes:
        depth = node.get("depth")
        if isinstance(depth, int) and depth > max_depth:
            max_depth = depth
        if node.get("is_missing") is True:
            missing_node_count += 1

        uri = node.get("uri")
        parent_uri = node.get("parent_uri")
        if isinstance(parent_uri, str) and parent_uri:
            branch_count[parent_uri] = branch_count.get(parent_uri, 0) + 1
            if parent_uri not in uri_set:
                orphan_count += 1
                issue_count = add_issue(
                    issues,
                    issue_count,
                    max_issues,
                    {
                        "scope": "thread",
                        "type": "orphan_node",
                        "requested_uri": requested_uri,
                        "uri": uri,
                        "parent_uri": parent_uri,
                    },
                )

    max_branching = max(branch_count.values()) if branch_count else 0

    root_uri = None
    if nodes:
        first_uri = nodes[0].get("uri")
        if isinstance(first_uri, str) and first_uri:
            root_uri = first_uri

    if requested_uri not in uri_set:
        issue_count = add_issue(
            issues,
            issue_count,
            max_issues,
            {
                "scope": "thread",
                "type": "requested_root_missing",
                "requested_uri": requested_uri,
            },
        )

    return {
        "root_uri": root_uri,
        "max_depth": max_depth,
        "max_branching_factor": max_branching,
        "orphan_count": orphan_count,
        "missing_node_count": missing_node_count,
        "issue_count": issue_count,
        "issues": issues,
    }


def fetch_threads(
    *,
    client: BlueskyApiClient,
    seeds: list[dict[str, Any]],
    args: argparse.Namespace,
    logger: logging.Logger,
) -> ThreadFetchResult:
    issues: list[dict[str, Any]] = []
    issue_count = 0
    threads: list[dict[str, Any]] = []
    success_count = 0
    failure_count = 0
    skipped_count = 0

    seeds_for_threads = seeds[: args.max_threads]
    for idx, seed in enumerate(seeds_for_threads, start=1):
        requested_uri = seed.get("uri")
        if not isinstance(requested_uri, str) or not requested_uri:
            skipped_count += 1
            issue_count = add_issue(
                issues,
                issue_count,
                args.max_validation_issues,
                {
                    "scope": "thread-fetch",
                    "type": "seed_missing_uri",
                    "seed_index": idx,
                },
            )
            continue

        query = {
            "uri": requested_uri,
            "depth": args.thread_depth,
            "parentHeight": args.thread_parent_height,
        }
        try:
            response = client.query(path=XRPC_GET_POST_THREAD, query=query)
        except RuntimeError as exc:
            failure_count += 1
            issue_count = add_issue(
                issues,
                issue_count,
                args.max_validation_issues,
                {
                    "scope": "thread-fetch",
                    "type": "thread_request_failed",
                    "requested_uri": requested_uri,
                    "message": str(exc),
                },
            )
            logger.warning(
                "thread-fetch-failed seed_index=%s uri=%s error=%s",
                idx,
                requested_uri,
                exc,
            )
            continue

        thread_obj = response.payload.get("thread")
        if not isinstance(thread_obj, dict):
            failure_count += 1
            issue_count = add_issue(
                issues,
                issue_count,
                args.max_validation_issues,
                {
                    "scope": "thread-fetch",
                    "type": "thread_payload_missing_thread",
                    "requested_uri": requested_uri,
                },
            )
            continue

        thread_nodes, flatten_issue_count, flatten_issues = flatten_thread_tree(
            root_node=thread_obj,
            requested_uri=requested_uri,
            max_issues=args.max_validation_issues,
        )
        thread_validation = validate_thread_nodes(
            requested_uri=requested_uri,
            nodes=thread_nodes,
            max_issues=args.max_validation_issues,
        )

        local_issue_count = flatten_issue_count + thread_validation["issue_count"]
        local_issue_samples: list[dict[str, Any]] = []
        extend_issue_samples(local_issue_samples, flatten_issues, args.max_validation_issues)
        extend_issue_samples(
            local_issue_samples,
            thread_validation["issues"],
            args.max_validation_issues,
        )

        issue_count += local_issue_count
        extend_issue_samples(issues, local_issue_samples, args.max_validation_issues)

        threads.append(
            {
                "requested_uri": requested_uri,
                "http_status": response.status_code,
                "request_url": response.url,
                "node_count": len(thread_nodes),
                "root_uri": thread_validation["root_uri"],
                "max_depth": thread_validation["max_depth"],
                "max_branching_factor": thread_validation["max_branching_factor"],
                "orphan_count": thread_validation["orphan_count"],
                "missing_node_count": thread_validation["missing_node_count"],
                "issue_count": local_issue_count,
                "issue_samples": local_issue_samples,
                "nodes": thread_nodes,
            }
        )
        success_count += 1
        logger.info(
            "thread-fetched index=%s uri=%s nodes=%s issues=%s",
            idx,
            requested_uri,
            len(thread_nodes),
            local_issue_count,
        )

    return ThreadFetchResult(
        threads=threads,
        issue_count=issue_count,
        issues=issues,
        success_count=success_count,
        failure_count=failure_count,
        skipped_count=skipped_count,
    )


def write_json_file(path: Path, payload: Any, *, pretty: bool) -> None:
    serialized = json.dumps(
        payload,
        ensure_ascii=False,
        indent=2 if pretty else None,
        separators=None if pretty else (",", ":"),
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(serialized + "\n", encoding="utf-8")


def write_jsonl_file(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fp:
        for record in records:
            fp.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")))
            fp.write("\n")


def enforce_run_caps(args: argparse.Namespace, config: RuntimeConfig) -> None:
    if args.max_pages > config.max_pages_per_run:
        raise ValueError(
            f"--max-pages {args.max_pages} exceeds BLUESKY_MAX_PAGES_PER_RUN "
            f"{config.max_pages_per_run}."
        )
    if args.max_posts > config.max_posts_per_run:
        raise ValueError(
            f"--max-posts {args.max_posts} exceeds BLUESKY_MAX_POSTS_PER_RUN "
            f"{config.max_posts_per_run}."
        )
    if not args.skip_threads and args.max_threads > config.max_threads_per_run:
        raise ValueError(
            f"--max-threads {args.max_threads} exceeds BLUESKY_MAX_THREADS_PER_RUN "
            f"{config.max_threads_per_run}."
        )


def command_check_config(args: argparse.Namespace) -> int:
    try:
        config = build_runtime_config(args)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    payload = {
        "ok": True,
        "api_base_url": config.api_base_url,
        "auth_service_url": config.auth_service_url,
        "auth_configured": bool(config.identifier and config.app_password),
        "identifier_masked": mask_secret(config.identifier),
        "timeout_seconds": config.timeout_seconds,
        "max_retries": config.max_retries,
        "retry_backoff_seconds": config.retry_backoff_seconds,
        "retry_backoff_multiplier": config.retry_backoff_multiplier,
        "min_request_interval_seconds": config.min_request_interval_seconds,
        "page_size": config.page_size,
        "max_pages_per_run": config.max_pages_per_run,
        "max_posts_per_run": config.max_posts_per_run,
        "max_threads_per_run": config.max_threads_per_run,
        "thread_depth": config.thread_depth,
        "thread_parent_height": config.thread_parent_height,
        "max_retry_after_seconds": config.max_retry_after_seconds,
        "user_agent": config.user_agent,
        "env_keys": [
            ENV_BASE_URL,
            ENV_AUTH_SERVICE_URL,
            ENV_IDENTIFIER,
            ENV_APP_PASSWORD,
            ENV_TIMEOUT_SECONDS,
            ENV_MAX_RETRIES,
            ENV_RETRY_BACKOFF_SECONDS,
            ENV_RETRY_BACKOFF_MULTIPLIER,
            ENV_MIN_REQUEST_INTERVAL_SECONDS,
            ENV_PAGE_SIZE,
            ENV_MAX_PAGES_PER_RUN,
            ENV_MAX_POSTS_PER_RUN,
            ENV_MAX_THREADS_PER_RUN,
            ENV_THREAD_DEPTH,
            ENV_THREAD_PARENT_HEIGHT,
            ENV_MAX_RETRY_AFTER_SECONDS,
            ENV_USER_AGENT,
        ],
    }
    print(
        json.dumps(
            payload,
            ensure_ascii=False,
            indent=2 if args.pretty else None,
            separators=None if args.pretty else (",", ":"),
        )
    )
    return 0


def command_fetch(args: argparse.Namespace) -> int:
    try:
        config = build_runtime_config(args)
        if args.page_size is None:
            args.page_size = config.page_size
        if args.thread_depth is None:
            args.thread_depth = config.thread_depth
        if args.thread_parent_height is None:
            args.thread_parent_height = config.thread_parent_height
        validate_fetch_args(args)
        enforce_run_caps(args, config)
        start_dt = (
            parse_datetime_utc(args.start_datetime, field_name="--start-datetime", is_end=False)
            if args.start_datetime.strip()
            else None
        )
        end_dt = (
            parse_datetime_utc(args.end_datetime, field_name="--end-datetime", is_end=True)
            if args.end_datetime.strip()
            else None
        )
        if start_dt is not None and end_dt is not None and start_dt >= end_dt:
            raise ValueError("--start-datetime must be earlier than --end-datetime.")
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    logger = build_logger(args.log_level, args.log_file)
    run_started = datetime.now(timezone.utc)

    dry_run_payload = {
        "ok": True,
        "dry_run": True,
        "source_mode": args.source_mode,
        "start_datetime_utc": to_rfc3339_z(start_dt) if start_dt is not None else None,
        "end_datetime_utc": to_rfc3339_z(end_dt) if end_dt is not None else None,
        "max_pages": args.max_pages,
        "max_posts": args.max_posts,
        "max_threads": args.max_threads,
        "thread_depth": args.thread_depth,
        "thread_parent_height": args.thread_parent_height,
        "skip_threads": args.skip_threads,
        "auth_configured": bool(config.identifier and config.app_password),
        "api_base_url": config.api_base_url,
        "auth_service_url": config.auth_service_url,
    }
    if args.dry_run:
        print(
            json.dumps(
                dry_run_payload,
                ensure_ascii=False,
                indent=2 if args.pretty else None,
                separators=None if args.pretty else (",", ":"),
            )
        )
        return 0

    try:
        client = BlueskyApiClient(config, logger)
        auth_session = None
        if config.identifier and config.app_password:
            auth_session = client.authenticate()
        elif args.require_auth:
            raise ValueError(
                "--require-auth is set, but BLUESKY_IDENTIFIER/BLUESKY_APP_PASSWORD are not configured."
            )

        seed_result = fetch_seed_posts(
            client=client,
            args=args,
            start_dt=start_dt,
            end_dt=end_dt,
            logger=logger,
        )
        thread_result = ThreadFetchResult(
            threads=[],
            issue_count=0,
            issues=[],
            success_count=0,
            failure_count=0,
            skipped_count=0,
        )
        if not args.skip_threads and seed_result.seeds:
            thread_result = fetch_threads(
                client=client,
                seeds=seed_result.seeds,
                args=args,
                logger=logger,
            )
    except (RuntimeError, ValueError) as exc:
        logger.error("fetch-failed error=%s", exc)
        print(str(exc), file=sys.stderr)
        return 2

    issue_samples: list[dict[str, Any]] = []
    extend_issue_samples(issue_samples, seed_result.issues, args.max_validation_issues)
    extend_issue_samples(issue_samples, thread_result.issues, args.max_validation_issues)
    total_issue_count = seed_result.issue_count + thread_result.issue_count

    fetch_finished = datetime.now(timezone.utc)
    duration_seconds = round((fetch_finished - run_started).total_seconds(), 3)

    payload: dict[str, Any] = {
        "ok": True,
        "dry_run": False,
        "source_mode": args.source_mode,
        "window": {
            "start_datetime_utc": to_rfc3339_z(start_dt) if start_dt is not None else None,
            "end_datetime_utc": to_rfc3339_z(end_dt) if end_dt is not None else None,
        },
        "auth": {
            "used_session": auth_session is not None,
            "did": auth_session.did if auth_session is not None else None,
            "handle": auth_session.handle if auth_session is not None else None,
        },
        "request_caps": {
            "max_pages": args.max_pages,
            "max_posts": args.max_posts,
            "max_threads": args.max_threads,
            "thread_depth": args.thread_depth,
            "thread_parent_height": args.thread_parent_height,
            "page_size": args.page_size,
        },
        "seed_fetch": {
            "stop_reason": seed_result.stop_reason,
            "hits_total": seed_result.hits_total,
            "page_count": len(seed_result.page_trace),
            "seed_count": len(seed_result.seeds),
            "duplicate_seed_count": seed_result.duplicate_seed_count,
            "skipped_outside_window_count": seed_result.skipped_outside_window,
            "skipped_no_timestamp_count": seed_result.skipped_no_timestamp,
            "page_trace": seed_result.page_trace,
        },
        "thread_fetch": {
            "enabled": not args.skip_threads,
            "thread_count": len(thread_result.threads),
            "success_count": thread_result.success_count,
            "failure_count": thread_result.failure_count,
            "skipped_count": thread_result.skipped_count,
        },
        "validation_summary": {
            "total_issue_count": total_issue_count,
            "issue_samples": issue_samples,
        },
        "runtime": {
            "started_at_utc": to_rfc3339_z(run_started),
            "finished_at_utc": to_rfc3339_z(fetch_finished),
            "duration_seconds": duration_seconds,
        },
        "seed_posts": seed_result.seeds,
        "threads": thread_result.threads,
        "artifacts": {},
    }

    if args.output_dir.strip():
        output_dir = Path(args.output_dir).expanduser().resolve()
        output_dir.mkdir(parents=True, exist_ok=True)

        seed_path = output_dir / "seed_posts.json"
        threads_path = output_dir / "threads.json"
        write_json_file(seed_path, seed_result.seeds, pretty=args.pretty)
        write_json_file(threads_path, thread_result.threads, pretty=args.pretty)

        payload["artifacts"]["seed_posts_json"] = str(seed_path)
        payload["artifacts"]["threads_json"] = str(threads_path)

        if not args.skip_threads:
            nodes_path = output_dir / "thread_nodes.jsonl"
            jsonl_records: list[dict[str, Any]] = []
            for thread in thread_result.threads:
                requested_uri = thread.get("requested_uri")
                root_uri = thread.get("root_uri")
                nodes = thread.get("nodes")
                if not isinstance(nodes, list):
                    continue
                for node in nodes:
                    if not isinstance(node, dict):
                        continue
                    record = dict(node)
                    record["requested_uri"] = requested_uri
                    record["thread_root_uri"] = root_uri
                    jsonl_records.append(record)
            write_jsonl_file(nodes_path, jsonl_records)
            payload["artifacts"]["thread_nodes_jsonl"] = str(nodes_path)

    if args.output.strip():
        output_path = Path(args.output).expanduser().resolve()
        write_json_file(output_path, payload, pretty=args.pretty)
        payload["artifacts"]["full_payload_json"] = str(output_path)

    print(
        json.dumps(
            payload,
            ensure_ascii=False,
            indent=2 if args.pretty else None,
            separators=None if args.pretty else (",", ":"),
        )
    )
    return 0


def add_runtime_overrides(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--base-url", default="", help=f"API base URL (default env {ENV_BASE_URL}).")
    parser.add_argument(
        "--auth-service-url",
        default="",
        help=f"Auth service URL for createSession/proxied requests (default env {ENV_AUTH_SERVICE_URL}).",
    )
    parser.add_argument("--identifier", default="", help=f"Account handle/DID (or env {ENV_IDENTIFIER}).")
    parser.add_argument(
        "--app-password",
        default="",
        help=f"App password (or env {ENV_APP_PASSWORD}).",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=int,
        default=None,
        help=f"HTTP timeout seconds (default env {ENV_TIMEOUT_SECONDS}).",
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=None,
        help=f"Retry count (default env {ENV_MAX_RETRIES}).",
    )
    parser.add_argument(
        "--retry-backoff-seconds",
        type=float,
        default=None,
        help=f"Initial backoff seconds (default env {ENV_RETRY_BACKOFF_SECONDS}).",
    )
    parser.add_argument(
        "--retry-backoff-multiplier",
        type=float,
        default=None,
        help=f"Exponential backoff multiplier (default env {ENV_RETRY_BACKOFF_MULTIPLIER}).",
    )
    parser.add_argument(
        "--min-request-interval-seconds",
        type=float,
        default=None,
        help=f"Minimum interval between requests (default env {ENV_MIN_REQUEST_INTERVAL_SECONDS}).",
    )
    parser.add_argument(
        "--max-pages-per-run",
        type=int,
        default=None,
        help=f"Safety cap for --max-pages (default env {ENV_MAX_PAGES_PER_RUN}).",
    )
    parser.add_argument(
        "--max-posts-per-run",
        type=int,
        default=None,
        help=f"Safety cap for --max-posts (default env {ENV_MAX_POSTS_PER_RUN}).",
    )
    parser.add_argument(
        "--max-threads-per-run",
        type=int,
        default=None,
        help=f"Safety cap for --max-threads (default env {ENV_MAX_THREADS_PER_RUN}).",
    )
    parser.add_argument(
        "--max-retry-after-seconds",
        type=int,
        default=None,
        help=f"Maximum Retry-After accepted for auto-wait (default env {ENV_MAX_RETRY_AFTER_SECONDS}).",
    )
    parser.add_argument(
        "--user-agent",
        default="",
        help=f"User-Agent header (default env {ENV_USER_AGENT}).",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Fetch Bluesky posts and thread cascades with retries and validation."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    check = sub.add_parser("check-config", help="Validate effective runtime configuration.")
    add_runtime_overrides(check)
    check.add_argument("--page-size", type=int, default=None, help=f"Default page size (env {ENV_PAGE_SIZE}).")
    check.add_argument(
        "--thread-depth",
        type=int,
        default=None,
        help=f"Default thread depth (env {ENV_THREAD_DEPTH}).",
    )
    check.add_argument(
        "--thread-parent-height",
        type=int,
        default=None,
        help=f"Default thread parent height (env {ENV_THREAD_PARENT_HEIGHT}).",
    )
    check.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")

    fetch = sub.add_parser("fetch", help="Fetch seed posts and expand reply cascades.")
    add_runtime_overrides(fetch)
    fetch.add_argument(
        "--source-mode",
        choices=SOURCE_MODES,
        default=SOURCE_MODE_SEARCH,
        help="Seed source mode.",
    )
    fetch.add_argument("--query", default="", help="Search query string (required for source-mode=search).")
    fetch.add_argument(
        "--search-sort",
        choices=("latest", "top"),
        default="latest",
        help="searchPosts ranking order (search mode only).",
    )
    fetch.add_argument("--search-author", default="", help="searchPosts author filter.")
    fetch.add_argument("--search-mentions", default="", help="searchPosts mentions filter.")
    fetch.add_argument("--search-lang", default="", help="searchPosts language filter.")
    fetch.add_argument("--search-domain", default="", help="searchPosts domain filter.")
    fetch.add_argument("--search-url", default="", help="searchPosts URL filter.")
    fetch.add_argument(
        "--search-tag",
        action="append",
        default=[],
        help="searchPosts tag filter (repeat for AND matching).",
    )
    fetch.add_argument(
        "--disable-server-time-filter",
        action="store_true",
        help="Do not pass since/until to searchPosts; apply time window client-side only.",
    )

    fetch.add_argument("--actor", default="", help="Actor handle or DID (author-feed mode).")
    fetch.add_argument(
        "--author-feed-filter",
        choices=AUTHOR_FEED_FILTERS,
        default="posts_with_replies",
        help="getAuthorFeed filter value (author-feed mode).",
    )
    fetch.add_argument(
        "--include-pins",
        action="store_true",
        help="Include pinned posts in getAuthorFeed (author-feed mode).",
    )
    fetch.add_argument("--feed-uri", default="", help="Feed generator AT-URI (feed mode).")
    fetch.add_argument("--list-uri", default="", help="List AT-URI (list-feed mode).")

    fetch.add_argument(
        "--start-datetime",
        default="",
        help="Inclusive UTC start. ISO-8601 preferred, e.g. 2026-03-10T00:00:00Z.",
    )
    fetch.add_argument(
        "--end-datetime",
        default="",
        help="Exclusive UTC end. ISO-8601 preferred, e.g. 2026-03-11T00:00:00Z.",
    )
    fetch.add_argument(
        "--page-size",
        type=int,
        default=None,
        help=f"Page size per API request (1..{MAX_API_PAGE_SIZE}).",
    )
    fetch.add_argument("--max-pages", type=int, default=5, help="Maximum pages for seed fetch.")
    fetch.add_argument("--max-posts", type=int, default=120, help="Maximum kept seed posts.")
    fetch.add_argument(
        "--max-threads",
        type=int,
        default=40,
        help="Maximum threads expanded from seed posts.",
    )
    fetch.add_argument(
        "--thread-depth",
        type=int,
        default=None,
        help=f"getPostThread depth (0..{MAX_THREAD_DEPTH}).",
    )
    fetch.add_argument(
        "--thread-parent-height",
        type=int,
        default=None,
        help=f"getPostThread parentHeight (0..{MAX_THREAD_PARENT_HEIGHT}).",
    )
    fetch.add_argument(
        "--skip-threads",
        action="store_true",
        help="Only fetch seed posts and skip getPostThread expansion.",
    )
    fetch.add_argument(
        "--max-validation-issues",
        type=int,
        default=50,
        help="Maximum issue samples kept in output.",
    )
    fetch.add_argument(
        "--require-auth",
        action="store_true",
        help="Fail if auth credentials are not configured.",
    )
    fetch.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate arguments/config and print execution plan without remote calls.",
    )
    fetch.add_argument("--output-dir", default="", help="Directory to write seed/thread artifacts.")
    fetch.add_argument("--output", default="", help="Optional path for full JSON payload.")
    fetch.add_argument(
        "--log-level",
        default="INFO",
        choices=("DEBUG", "INFO", "WARNING", "ERROR"),
        help="Log level for stderr/file logs.",
    )
    fetch.add_argument("--log-file", default="", help="Optional log file path.")
    fetch.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if args.command == "check-config":
        return command_check_config(args)
    if args.command == "fetch":
        return command_fetch(args)
    parser.print_help(sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
