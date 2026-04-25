"""Sentry integration — production error monitoring.

Without this, your backend dies silently in production and you only
learn about it when customers complain. Sentry's free tier gives 5K
events/month which covers a typical early-stage SaaS workload.

Setup:
  1. Sign up at https://sentry.io → Create project → FastAPI/Python
  2. Copy the DSN
  3. Add to .env:
        SENTRY_DSN=https://...@o0.ingest.sentry.io/0
        SENTRY_ENVIRONMENT=production          # or staging, dev
        SENTRY_TRACES_SAMPLE_RATE=0.1          # 10% performance traces
  4. Backend startup calls init_sentry() — that's it.

If SENTRY_DSN isn't set, this is a no-op. Zero crash risk in dev.
"""
from __future__ import annotations
import logging
import os

logger = logging.getLogger(__name__)


_initialized = False


def init_sentry() -> bool:
    """Initialize Sentry SDK if DSN is configured. Returns True if
    monitoring is active."""
    global _initialized
    if _initialized:
        return True
    dsn = os.environ.get("SENTRY_DSN", "").strip()
    if not dsn:
        logger.info("Sentry disabled (no SENTRY_DSN). Production error monitoring is OFF.")
        return False
    try:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        from sentry_sdk.integrations.starlette import StarletteIntegration
        sentry_sdk.init(
            dsn=dsn,
            environment=os.environ.get("SENTRY_ENVIRONMENT", "production"),
            traces_sample_rate=float(os.environ.get("SENTRY_TRACES_SAMPLE_RATE", "0.1")),
            send_default_pii=False,  # Don't exfiltrate user PII into Sentry
            integrations=[
                FastApiIntegration(),
                StarletteIntegration(),
            ],
            before_send=_scrub_before_send,
        )
        _initialized = True
        logger.info("Sentry initialized.")
        return True
    except ImportError:
        logger.warning("sentry-sdk not installed. pip install 'sentry-sdk[fastapi]'")
        return False
    except Exception as exc:
        logger.exception("Sentry init failed: %s", exc)
        return False


def _scrub_before_send(event, hint):
    """Strip secrets from events before they leave our server.
    Sentry already redacts obvious patterns; we add belt-and-braces
    scrubbing for our own env-var key names."""
    try:
        sensitive = (
            "api_key", "apikey", "api-key", "secret", "token", "password",
            "authorization", "bearer", "stripe", "sendgrid", "apollo",
            "hunter", "deepgram", "brave", "linkedin", "twilio", "openai",
            "anthropic", "fal_key", "resend", "dsn",
        )
        for k in list((event.get("request") or {}).get("headers", {}).keys()):
            if any(s in k.lower() for s in sensitive):
                event["request"]["headers"][k] = "[redacted]"
        # Scrub query string
        if "request" in event and "query_string" in event["request"]:
            qs = event["request"]["query_string"] or ""
            for s in sensitive:
                if s in qs.lower():
                    event["request"]["query_string"] = "[redacted-has-secret]"
                    break
    except Exception:
        pass
    return event


def capture_exception(exc: Exception, **context) -> None:
    """Manual capture with extra context. No-op if Sentry not configured."""
    if not _initialized:
        return
    try:
        import sentry_sdk
        with sentry_sdk.push_scope() as scope:
            for k, v in context.items():
                scope.set_extra(k, v)
            sentry_sdk.capture_exception(exc)
    except Exception:
        pass


def capture_message(msg: str, level: str = "info", **context) -> None:
    if not _initialized:
        return
    try:
        import sentry_sdk
        with sentry_sdk.push_scope() as scope:
            for k, v in context.items():
                scope.set_extra(k, v)
            sentry_sdk.capture_message(msg, level=level)
    except Exception:
        pass
