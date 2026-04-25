"""
Phase-4 (final polish) tests — request context propagation, secret scrubbing,
per-IP rate limiter. Pure in-process, no DB needed.
"""
from __future__ import annotations

import logging

import pytest

from services import rate_limit_ip
from services.request_context import (
    SecretScrubbingFilter,
    get_request_id,
    get_user_id,
    install_filters,
    new_request_id,
    scrub_secrets,
    set_context,
    set_user_id,
)


# --------------------------------------------------------------- request context

def test_request_id_round_trip():
    rid = new_request_id()
    set_context(request_id=rid, user_id="user_abc")
    assert get_request_id() == rid
    assert get_user_id() == "user_abc"


def test_set_user_id_independent_of_request_id():
    set_context(request_id="req_static")
    set_user_id("alt_user")
    assert get_request_id() == "req_static"
    assert get_user_id() == "alt_user"


# --------------------------------------------------------------- secret scrubber

@pytest.mark.parametrize("secret,expected_prefix", [
    ("maars_sk_live_abcdef0123456789abcdef", "maars_sk_live_"),
    ("sk-ant-abcdef0123456789abcdef_test", "sk-ant-"),
    ("sk-proj-abcdef0123456789abcdef_test", "sk-proj-"),
    ("sk-0123456789abcdefghij0123456789", "sk-"),
    ("whsec_abcdef0123456789abcdef", "whsec_"),
])
def test_scrub_secrets_redacts_each_shape(secret, expected_prefix):
    scrubbed = scrub_secrets(f"error calling key={secret} failed")
    assert secret not in scrubbed
    assert f"{expected_prefix}<redacted>" in scrubbed


def test_scrub_secrets_preserves_non_secret_text():
    clean = "request completed with user_id=user_abc and status=200"
    assert scrub_secrets(clean) == clean


def test_scrub_filter_rewrites_log_record():
    handler = logging.StreamHandler()
    handler.addFilter(SecretScrubbingFilter())
    buf: list[str] = []
    handler.emit = lambda record: buf.append(record.getMessage())  # type: ignore
    log = logging.getLogger("maars.test.scrub")
    log.handlers = [handler]
    log.setLevel(logging.INFO)
    log.info("outbound call with key=maars_sk_live_0123456789abcdef0123 failed")
    assert "maars_sk_live_0123456789abcdef0123" not in buf[0]
    assert "<redacted>" in buf[0]


def test_install_filters_is_idempotent():
    root = logging.getLogger("maars.test.idem")
    root.handlers = [logging.StreamHandler()]
    install_filters(root)
    install_filters(root)     # second call must not double-attach
    types = [type(f).__name__ for f in root.filters]
    assert types.count("RequestContextFilter") == 1
    assert types.count("SecretScrubbingFilter") == 1


# --------------------------------------------------------------- per-IP rate limit

def test_ip_rate_limit_allows_under_cap():
    rate_limit_ip.reset("203.0.113.1")
    for _ in range(5):
        allowed, _, _ = rate_limit_ip.check("203.0.113.1", rpm=10)
        assert allowed is True


def test_ip_rate_limit_blocks_over_cap():
    rate_limit_ip.reset("203.0.113.2")
    for _ in range(10):
        rate_limit_ip.check("203.0.113.2", rpm=10)
    allowed, count, retry = rate_limit_ip.check("203.0.113.2", rpm=10)
    assert allowed is False
    assert count >= 10
    assert retry >= 1


def test_ip_rate_limit_scopes_per_ip():
    rate_limit_ip.reset_all()
    for _ in range(3):
        rate_limit_ip.check("198.51.100.1", rpm=3)
    # Different IP — own budget.
    allowed, _, _ = rate_limit_ip.check("198.51.100.2", rpm=3)
    assert allowed is True
