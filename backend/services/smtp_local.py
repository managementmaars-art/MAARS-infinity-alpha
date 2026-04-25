"""Self-hosted SMTP send — the zero-per-email path.

When the operator runs Postfix (or any SMTP relay) with warmed-up IPs
and DKIM/SPF/DMARC in place, this adapter sends via a direct SMTP
connection, $0 per email. On any error (not configured, auth failed,
connection refused, 5xx) it raises and the email_sender chain falls
through to SendGrid/Resend.

Required env for self-host:
  MAARS_SMTP_HOST      smtp.yourdomain.com
  MAARS_SMTP_PORT      465 (TLS) or 587 (STARTTLS)
  MAARS_SMTP_USER      postmaster@yourdomain.com   (if auth required)
  MAARS_SMTP_PASSWORD  ****
  MAARS_SMTP_FROM      hello@yourdomain.com
  MAARS_SMTP_FROM_NAME "Your Brand"
  MAARS_SMTP_USE_TLS   "1" for implicit TLS on 465 (default for 465)
  MAARS_SMTP_STARTTLS  "1" for STARTTLS on 587 (default for 587)

DKIM signing is done at the Postfix level (opendkim milter) — the
adapter sends the raw message, Postfix signs on the way out. This
avoids having to carry DKIM keys in Python.

Compliance headers (List-Unsubscribe one-click, Message-ID, Precedence)
are set on every message so Gmail + Yahoo bulk-sender requirements
(Feb 2024) are met.
"""
from __future__ import annotations
import email.utils
import logging
import os
import ssl
import time
import uuid
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

logger = logging.getLogger(__name__)


class SMTPUnavailable(RuntimeError):
    """Raised when self-host SMTP isn't configured or the connection
    failed. email_sender treats this as 'skip to next provider'."""


def is_configured() -> bool:
    return bool(os.environ.get("MAARS_SMTP_HOST"))


async def send_local(
    *,
    to: str,
    subject: str,
    body_html: str = "",
    body_text: str | None = None,
    from_email: str | None = None,
    from_name: str | None = None,
    reply_to: str | None = None,
    unsubscribe_url: str | None = None,
    custom_headers: dict[str, str] | None = None,
) -> dict:
    """Send via direct SMTP. Returns {ok, provider, message_id}.

    Prefers aiosmtplib (async-native); falls back to stdlib smtplib in a
    thread. If neither works or creds are bad, raises SMTPUnavailable so
    email_sender can fall through to SendGrid / Resend."""
    if not is_configured():
        raise SMTPUnavailable("MAARS_SMTP_HOST not set — local SMTP not configured")

    host = os.environ["MAARS_SMTP_HOST"]
    port = int(os.environ.get("MAARS_SMTP_PORT", "465"))
    user = os.environ.get("MAARS_SMTP_USER")
    pw   = os.environ.get("MAARS_SMTP_PASSWORD")
    from_email = from_email or os.environ.get("MAARS_SMTP_FROM")
    from_name  = from_name  or os.environ.get("MAARS_SMTP_FROM_NAME", "")
    if not from_email:
        raise SMTPUnavailable("MAARS_SMTP_FROM missing")

    use_tls  = os.environ.get("MAARS_SMTP_USE_TLS", "1" if port == 465 else "0") == "1"
    starttls = os.environ.get("MAARS_SMTP_STARTTLS", "1" if port == 587 else "0") == "1"

    # Build MIME with compliance headers.
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = email.utils.formataddr((from_name or "", from_email))
    msg["To"]      = to
    msg["Date"]    = email.utils.formatdate(localtime=False)
    msg_id = email.utils.make_msgid(domain=host)
    msg["Message-ID"] = msg_id
    if reply_to:
        msg["Reply-To"] = reply_to
    if unsubscribe_url:
        # Gmail + Yahoo bulk-sender compliance (Feb 2024 onwards).
        msg["List-Unsubscribe"] = f"<{unsubscribe_url}>"
        msg["List-Unsubscribe-Post"] = "List-Unsubscribe=One-Click"
    msg["Precedence"] = "bulk"
    for k, v in (custom_headers or {}).items():
        msg[k] = v

    text_part = body_text or _html_to_text(body_html)
    msg.attach(MIMEText(text_part, "plain", "utf-8"))
    if body_html:
        msg.attach(MIMEText(body_html, "html", "utf-8"))

    raw = msg.as_string()

    # Prefer async SMTP.
    try:
        import aiosmtplib
        ssl_ctx = ssl.create_default_context() if (use_tls or starttls) else None
        await aiosmtplib.send(
            msg, hostname=host, port=port,
            username=user, password=pw,
            use_tls=use_tls, start_tls=starttls and not use_tls,
            tls_context=ssl_ctx,
            timeout=30,
        )
        return {"ok": True, "provider": "smtp_local", "message_id": msg_id,
                "host": host, "cost_usd": 0.0}
    except ImportError:
        # Fall back to sync smtplib on a thread.
        import asyncio, smtplib
        def _send_sync():
            if use_tls:
                s = smtplib.SMTP_SSL(host, port, timeout=30)
            else:
                s = smtplib.SMTP(host, port, timeout=30)
                if starttls:
                    s.starttls(context=ssl.create_default_context())
            if user and pw:
                s.login(user, pw)
            s.sendmail(from_email, [to], raw)
            s.quit()
        try:
            await asyncio.to_thread(_send_sync)
            return {"ok": True, "provider": "smtp_local", "message_id": msg_id,
                    "host": host, "cost_usd": 0.0}
        except Exception as exc:
            raise SMTPUnavailable(f"smtplib send failed: {exc}") from exc
    except Exception as exc:
        raise SMTPUnavailable(f"aiosmtplib send failed: {exc}") from exc


def _html_to_text(html: str) -> str:
    """Minimal HTML→text for the plaintext MIME part. No external dep."""
    import re
    if not html: return ""
    t = re.sub(r"<br\s*/?>", "\n", html, flags=re.IGNORECASE)
    t = re.sub(r"</(p|div|li|tr|h[1-6])>", "\n", t, flags=re.IGNORECASE)
    t = re.sub(r"<[^>]+>", "", t)
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()
