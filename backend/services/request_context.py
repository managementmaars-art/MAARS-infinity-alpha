"""
Per-request correlation context + log scrubbing.

`request_id` and `user_id` live in `contextvars` so any service called inside
a request handler can stamp them into its log records without being passed
explicitly. A `RequestContextFilter` installed on the root logger attaches
them to every line; a companion `SecretScrubbingFilter` redacts API keys
and JWT tokens that slipped into error messages.

Kept deliberately small — this is infrastructure, not a feature.
"""
from __future__ import annotations

import logging
import re
import uuid
from contextvars import ContextVar
from typing import Optional

# ------------------------------------------------------------------- contextvars

_REQUEST_ID: ContextVar[str] = ContextVar("maars_request_id", default="")
_USER_ID: ContextVar[str] = ContextVar("maars_user_id", default="")


def new_request_id() -> str:
    return f"req_{uuid.uuid4().hex[:16]}"


def set_context(*, request_id: str, user_id: Optional[str] = None) -> None:
    _REQUEST_ID.set(request_id)
    if user_id is not None:
        _USER_ID.set(user_id)


def set_user_id(user_id: str) -> None:
    _USER_ID.set(user_id)


def get_request_id() -> str:
    return _REQUEST_ID.get()


def get_user_id() -> str:
    return _USER_ID.get()


def snapshot() -> dict[str, str]:
    return {"request_id": _REQUEST_ID.get(), "user_id": _USER_ID.get()}


# ------------------------------------------------------------------- logging filter

class RequestContextFilter(logging.Filter):
    """Attach request_id + user_id to every LogRecord so structured sinks capture them."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = _REQUEST_ID.get() or "-"
        record.user_id = _USER_ID.get() or "-"
        return True


# ------------------------------------------------------------------- secret scrubber

_SECRET_PATTERNS = [
    re.compile(r"(maars_sk_live_)[A-Za-z0-9]{20,}", re.IGNORECASE),
    re.compile(r"(maars-sk-)[A-Za-z0-9]{20,}", re.IGNORECASE),
    re.compile(r"(sk-ant-)[A-Za-z0-9_-]{20,}", re.IGNORECASE),
    re.compile(r"(sk-proj-)[A-Za-z0-9_-]{20,}", re.IGNORECASE),
    re.compile(r"(sk-)[A-Za-z0-9]{20,}"),
    re.compile(r"(whsec_)[A-Za-z0-9_-]{20,}"),
    re.compile(r"(Bearer )[A-Za-z0-9_\-\.]{16,}"),
    re.compile(r"(eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{5,})"),  # JWT
]


def scrub_secrets(text: str) -> str:
    """Replace the body of any known API-key / JWT shape with '<redacted>'."""
    if not text:
        return text
    out = text
    for pat in _SECRET_PATTERNS:
        out = pat.sub(lambda m: f"{m.group(1) if m.lastindex else ''}<redacted>", out)
    return out


class SecretScrubbingFilter(logging.Filter):
    """Scrub secret shapes from every log line before it leaves the process."""

    def filter(self, record: logging.LogRecord) -> bool:
        try:
            if isinstance(record.msg, str):
                record.msg = scrub_secrets(record.msg)
            if record.args:
                record.args = tuple(
                    scrub_secrets(a) if isinstance(a, str) else a for a in record.args
                )
        except Exception:
            pass
        return True


def install_filters(root_logger: Optional[logging.Logger] = None) -> None:
    """Attach both filters to the root logger + every existing handler. Idempotent."""
    root = root_logger or logging.getLogger()
    ctx = RequestContextFilter()
    scrub = SecretScrubbingFilter()
    existing_types = {type(f) for f in getattr(root, "filters", [])}
    if RequestContextFilter not in existing_types:
        root.addFilter(ctx)
    if SecretScrubbingFilter not in existing_types:
        root.addFilter(scrub)
    for h in root.handlers:
        h_types = {type(f) for f in getattr(h, "filters", [])}
        if RequestContextFilter not in h_types:
            h.addFilter(ctx)
        if SecretScrubbingFilter not in h_types:
            h.addFilter(scrub)
