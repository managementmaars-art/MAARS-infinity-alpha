"""Transactional emails — polished, premium-feeling templates.

Every email the platform sends that isn't a cold campaign. These are
the lifecycle touches that make users feel like a real SaaS is serving
them instead of a script.

Design system (inline-only because email clients strip <head><style>):
  - Logo-topped card on a light-grey page (Gmail/Outlook friendly)
  - 16px type, 1.6 line-height
  - Single-color CTA button with 10px radius + 14px padding
  - One CTA per email (critical for clickthrough)
  - Pre-header text (first line shown in inbox preview)
  - Polite, human footer with clear unsubscribe context
  - Mobile-first: max-width 520px, works down to 320px

Every send goes through services.email_sender so the compliance
headers (List-Unsubscribe, Message-ID) + suppression-list checks +
provider fallback are applied uniformly.
"""
from __future__ import annotations
import logging
import os

logger = logging.getLogger(__name__)

_BRAND = "MAARS Command"
_FROM_NAME = "MAARS"
_FROM_EMAIL = os.environ.get("MAARS_FROM_EMAIL", f"hello@{os.environ.get('MAARS_EMAIL_DOMAIN', 'maarscommand.com')}")
_PUBLIC_URL = os.environ.get("MAARS_PUBLIC_URL", "https://maarscommand.com")
_LOGO_URL = os.environ.get("MAARS_LOGO_URL", f"{_PUBLIC_URL}/branding/maars-logo.jpeg")

# Design tokens — kept here so a future redesign is a one-line change.
_T = {
    "bg_page":     "#f6f7f9",
    "bg_card":     "#ffffff",
    "text":        "#0f172a",
    "text_muted":  "#475569",
    "text_fade":   "#94a3b8",
    "border":      "#e2e8f0",
    "brand_start": "#4fd1c5",   # teal
    "brand_end":   "#7c3aed",   # violet
    "accent":      "#0f172a",
    "success":     "#059669",
    "danger":      "#dc2626",
    "warn":        "#d97706",
}


def _button(href: str, label: str, *, style: str = "primary") -> str:
    """Render a single CTA button. `style` picks the visual weight."""
    bg_map = {
        "primary":   f"linear-gradient(135deg, {_T['brand_start']}, {_T['brand_end']})",
        "secondary": _T["accent"],
        "danger":    _T["danger"],
        "success":   _T["success"],
    }
    color = "#030712" if style == "primary" else "#ffffff"
    bg = bg_map.get(style, bg_map["primary"])
    return (
        f'<table role="presentation" cellspacing="0" cellpadding="0" border="0" '
        f'style="margin:20px 0;">'
        f'<tr><td style="border-radius:10px;background:{bg};">'
        f'<a href="{href}" target="_blank" '
        f'style="display:inline-block;padding:13px 26px;font-weight:700;'
        f'font-size:14px;color:{color};text-decoration:none;border-radius:10px;'
        f'font-family:-apple-system,BlinkMacSystemFont,\'Segoe UI\',Roboto,Arial,sans-serif;">'
        f'{label}</a></td></tr></table>'
    )


def _wrap(body_inner: str, preheader: str = "") -> str:
    """Responsive, inline-styled email shell. Works in Gmail, Outlook,
    Apple Mail, iOS/Android mail apps."""
    logo_block = (
        f'<img src="{_LOGO_URL}" width="32" height="32" alt="" '
        f'style="border-radius:8px;vertical-align:middle;margin-right:10px;">'
        if _LOGO_URL else ""
    )
    return f"""<!doctype html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{_BRAND}</title></head>
<body style="margin:0;padding:0;background:{_T['bg_page']};font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Arial,sans-serif;color:{_T['text']};-webkit-font-smoothing:antialiased;">
<!-- Pre-header (shown in inbox list, never on screen) -->
<span style="display:none;max-height:0;overflow:hidden;color:transparent;font-size:1px;line-height:1px;mso-hide:all;">{preheader}</span>
<span style="display:none;max-height:0;overflow:hidden;color:transparent;font-size:1px;line-height:1px;mso-hide:all;">&#847;&zwnj;&nbsp;&#8199;&#65279;&#847;&zwnj;&nbsp;&#8199;&#65279;&#847;&zwnj;&nbsp;&#8199;&#65279;&#847;&zwnj;&nbsp;&#8199;&#65279;</span>

<table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="background:{_T['bg_page']};padding:32px 16px;">
  <tr><td align="center">
    <table role="presentation" width="520" cellspacing="0" cellpadding="0" border="0" style="max-width:520px;background:{_T['bg_card']};border-radius:14px;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,0.04),0 4px 24px rgba(0,0,0,0.03);">

      <!-- Header bar -->
      <tr><td style="padding:24px 32px 4px 32px;border-bottom:1px solid {_T['border']};">
        <div style="display:inline-block;">
          {logo_block}
          <span style="font-family:Outfit,-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;font-weight:700;font-size:18px;color:{_T['text']};vertical-align:middle;">{_BRAND}</span>
        </div>
      </td></tr>

      <!-- Body -->
      <tr><td style="padding:28px 32px;color:{_T['text']};font-size:15px;line-height:1.65;">
        {body_inner}
      </td></tr>

      <!-- Footer -->
      <tr><td style="padding:20px 32px 24px 32px;border-top:1px solid {_T['border']};color:{_T['text_fade']};font-size:11px;line-height:1.6;">
        Sent to you as a transactional notice from your {_BRAND} account.
        Manage your preferences at <a href="{_PUBLIC_URL}/settings" style="color:#3b82f6;text-decoration:none;">your settings</a>.
        <br><br>
        <strong style="color:{_T['text_muted']};">MAARS Global Corporation</strong> &nbsp;·&nbsp;
        <a href="{_PUBLIC_URL}/privacy" style="color:#3b82f6;text-decoration:none;">Privacy</a> &nbsp;·&nbsp;
        <a href="{_PUBLIC_URL}/terms" style="color:#3b82f6;text-decoration:none;">Terms</a>
      </td></tr>
    </table>
  </td></tr>
</table>
</body></html>"""


async def _send(to: str, subject: str, body_inner: str, preheader: str = "") -> dict:
    """Route through the shared email_sender."""
    from services.email_sender import send_email
    return await send_email(
        to=to,
        subject=subject,
        body_html=_wrap(body_inner, preheader),
        from_email=_FROM_EMAIL,
        from_name=_FROM_NAME,
    )


def _h1(text: str) -> str:
    return (
        f'<h1 style="font-family:Outfit,-apple-system,BlinkMacSystemFont,\'Segoe UI\',sans-serif;'
        f'font-weight:800;font-size:24px;line-height:1.25;color:{_T["text"]};'
        f'margin:0 0 12px 0;">{text}</h1>'
    )


def _lede(text: str) -> str:
    return f'<p style="font-size:16px;color:{_T["text_muted"]};line-height:1.6;margin:0 0 18px 0;">{text}</p>'


def _p(text: str) -> str:
    return f'<p style="margin:0 0 14px 0;font-size:15px;color:{_T["text"]};line-height:1.65;">{text}</p>'


def _muted(text: str) -> str:
    return f'<p style="margin:16px 0 0 0;font-size:12px;color:{_T["text_fade"]};line-height:1.55;">{text}</p>'


def _stat_row(label: str, value: str, emphasis: bool = False) -> str:
    value_color = _T["text"] if not emphasis else _T["brand_end"]
    return (
        f'<tr><td style="padding:10px 14px;color:{_T["text_muted"]};font-size:13px;">{label}</td>'
        f'<td align="right" style="padding:10px 14px;color:{value_color};font-weight:700;font-size:14px;">{value}</td></tr>'
    )


def _stat_table(rows_html: str) -> str:
    return (
        f'<table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" '
        f'style="margin:12px 0 18px 0;background:#f8fafc;border-radius:10px;border:1px solid {_T["border"]};">'
        f'{rows_html}</table>'
    )


def _alert(kind: str, body: str) -> str:
    colors = {
        "info":    ("#eff6ff", "#bfdbfe", "#1e40af"),
        "success": ("#ecfdf5", "#a7f3d0", "#065f46"),
        "warn":    ("#fffbeb", "#fde68a", "#92400e"),
        "danger":  ("#fef2f2", "#fecaca", "#991b1b"),
    }
    bg, border, fg = colors.get(kind, colors["info"])
    return (
        f'<div style="padding:12px 14px;margin:14px 0;border-radius:10px;'
        f'background:{bg};border:1px solid {border};color:{fg};font-size:13px;line-height:1.55;">'
        f'{body}</div>'
    )


# ──────────────────────────────────────────────────────────────────
# Lifecycle emails — one per business event
# ──────────────────────────────────────────────────────────────────

async def send_welcome(user: dict) -> dict:
    """First email after signup. The single most important transactional
    email in a SaaS — first-5-minutes activation drives 50%+ of retention."""
    name = (user.get("name") or "there").split()[0]
    body = (
        _h1(f"Welcome to MAARS, {name}.")
        + _lede("Your AI workforce is live. You're set up with starter credits and every agent is ready to work.")
        + _p("Three ways to see value in the next hour:")
        + (
            '<ol style="margin:0 0 18px 20px;padding:0;font-size:15px;color:' + _T["text"] + ';line-height:1.9;">'
            + '<li><strong>Tell Commander Orion a goal</strong> — one sentence. It delegates to the right specialist from 458+ agents.</li>'
            + f'<li><a href="{_PUBLIC_URL}/dashboard?launch=image" style="color:#3b82f6;text-decoration:none;font-weight:600;">Generate your first image</a> — premium quality is the default, not an upsell.</li>'
            + f'<li><a href="{_PUBLIC_URL}/dashboard?launch=campaign" style="color:#3b82f6;text-decoration:none;font-weight:600;">Run a cold-email campaign</a> — find leads, draft personalized messages, schedule across days. All automated.</li>'
            + '</ol>'
        )
        + _button(f"{_PUBLIC_URL}/dashboard", "Open your dashboard")
        + _muted("Reply to this email with any question — real humans read every response, usually back within a few hours.")
    )
    return await _send(
        user["email"],
        f"You're in, {name}. Here's how to see value today.",
        body,
        "Your AI workforce is live. Three ways to see value in the next hour.",
    )


async def send_low_credit_warning(user: dict, credits_remaining: int, plan_credits: int) -> dict:
    """Threshold crossing (usually 75% and 95%). Called by the scheduler."""
    pct_used = round((1 - credits_remaining / max(plan_credits, 1)) * 100)
    critical = pct_used >= 90
    kind = "danger" if critical else "warn"
    headline = "Almost out of credits" if critical else "Credits are running low"
    body = (
        _h1(headline)
        + _lede(f"You've used <strong>{pct_used}% of this cycle's credits</strong>. If you don't top up, agent runs will queue until reset.")
        + _stat_table(
            _stat_row("Plan credits", f"{plan_credits:,}")
            + _stat_row("Used this cycle", f"{plan_credits - credits_remaining:,}")
            + _stat_row("Remaining", f"{credits_remaining:,}", emphasis=critical)
        )
        + _alert(kind, "Top up now to avoid any interruption to your scheduled campaigns and agent runs.")
        + _button(f"{_PUBLIC_URL}/pricing", "Top up or upgrade")
        + _muted(f'Tip: annual plans include 20% more credits plus a 2-month bonus. See <a href="{_PUBLIC_URL}/pricing?billing=annual" style="color:#3b82f6;">annual pricing</a>.')
    )
    return await _send(
        user["email"],
        f"{credits_remaining:,} credits left — top up?" if critical else f"Heads up: {pct_used}% of credits used",
        body,
        f"{credits_remaining:,} of {plan_credits:,} credits remaining this cycle.",
    )


async def send_payment_success(user: dict, amount_usd: float, plan_name: str, credits: int, receipt_url: str | None = None) -> dict:
    body = (
        _h1("Payment confirmed")
        + _lede(f"Thanks — your credits are live. Here's your receipt for your records.")
        + _stat_table(
            _stat_row("Plan", plan_name)
            + _stat_row("Credits added", f"{credits:,}", emphasis=True)
            + _stat_row("Amount charged", f"${amount_usd:,.2f} USD")
        )
        + (_button(receipt_url, "View full Stripe receipt", style="secondary") if receipt_url else "")
        + _button(f"{_PUBLIC_URL}/dashboard", "Open dashboard")
        + _muted("Credits are available immediately and never expire while your subscription is active.")
    )
    return await _send(
        user["email"],
        f"Receipt: ${amount_usd:,.2f} — {credits:,} credits added",
        body,
        f"Payment received. {credits:,} credits now available.",
    )


async def send_payment_failed(user: dict, attempt: int = 1, next_retry_at: str | None = None) -> dict:
    """Stripe said a charge failed. 7-day grace by default. Tell the
    user the second we hear about it so they can fix it."""
    body = (
        _h1("Payment didn't go through")
        + _lede(f"We couldn't process your most recent charge. This is attempt <strong>#{attempt}</strong>; service continues for 7 days while we retry, then your workspace pauses.")
        + _p("Most common fixes:")
        + (
            '<ul style="margin:0 0 14px 20px;padding:0;font-size:14px;color:' + _T["text"] + ';line-height:1.8;">'
            + '<li>Your card expired — update it in billing.</li>'
            + "<li>Your bank flagged the transaction — reply to their notification, then retry.</li>"
            + "<li>Billing address on file doesn't match the card — fix it in billing.</li>"
            + '</ul>'
        )
        + _button(f"{_PUBLIC_URL}/settings/billing", "Update payment method", style="danger")
        + (_muted(f"Next automatic retry: {next_retry_at}") if next_retry_at else _muted("We'll retry automatically. Update your card now to skip the wait."))
    )
    return await _send(
        user["email"],
        "Action needed: your payment didn't go through",
        body,
        "Update your payment method to keep your workspace running.",
    )


async def send_trial_ending(user: dict, days_left: int, plan_name: str) -> dict:
    body = (
        _h1(f"Your trial ends in {days_left} day{'s' if days_left != 1 else ''}")
        + _lede(f"To keep {plan_name} running past that date, choose a plan now. Nothing locks in until the trial actually ends — cancel anytime.")
        + _alert("info", "<strong>Annual plans save 20%</strong> and include 2 bonus credit-months. That's ~37% more value for ~20% less spend.")
        + _button(f"{_PUBLIC_URL}/pricing", "Choose a plan")
        + _muted("Not sure yet? Reply to this email — a human (not a bot) will help you pick.")
    )
    return await _send(
        user["email"],
        f"Your trial ends in {days_left} day{'s' if days_left != 1 else ''}",
        body,
        f"Pick a plan now to keep {plan_name} running.",
    )


async def send_referral_reward(user: dict, credits_earned: int, referred_user_label: str = "A new user") -> dict:
    body = (
        _h1(f"+{credits_earned:,} credits — a referral paid off")
        + _lede(f"{referred_user_label} just became a paying MAARS customer using your link. You've been credited instantly.")
        + _stat_table(
            _stat_row("Credits earned", f"+{credits_earned:,}", emphasis=True)
            + _stat_row("Referred user", referred_user_label)
        )
        + _button(f"{_PUBLIC_URL}/settings/referrals", "See your referral stats", style="secondary")
        + _muted("Every successful referral compounds. The more you share, the more you earn — there's no cap.")
    )
    return await _send(
        user["email"],
        f"+{credits_earned:,} credits earned",
        body,
        "Your MAARS referral converted. Credits are live.",
    )


async def send_weekly_digest(user: dict, stats: dict) -> dict:
    """Optional weekly engagement pull. Makes active users feel productive,
    surfaces inactive ones into the product."""
    first = (user.get("name") or "there").split()[0]
    sent = int(stats.get("emails_sent", 0))
    opened = int(stats.get("opens", 0))
    clicks = int(stats.get("clicks", 0))
    leads = int(stats.get("leads_found", 0))
    images = int(stats.get("images_generated", 0))
    videos = int(stats.get("videos_generated", 0))
    credits_used = int(stats.get("credits_used", 0))
    credits_remaining = int(stats.get("credits_remaining", 0))
    plan_total = credits_used + credits_remaining
    pct = round((credits_used / plan_total * 100)) if plan_total else 0

    body = (
        _h1(f"Your week on MAARS, {first}")
        + _lede("Here's what your AI workforce shipped this week.")
        + _stat_table(
            _stat_row("📧  Emails sent", f"{sent:,}")
            + _stat_row("👁️  Opens", f"{opened:,}")
            + _stat_row("🖱️  Clicks", f"{clicks:,}")
            + _stat_row("🎯  Leads found", f"{leads:,}")
            + _stat_row("🎨  Images generated", f"{images:,}")
            + _stat_row("🎬  Videos generated", f"{videos:,}")
            + _stat_row("⚡  Credits used this cycle", f"{credits_used:,} / {plan_total:,} ({pct}%)",
                        emphasis=pct >= 75)
        )
        + _button(f"{_PUBLIC_URL}/dashboard", "Open dashboard")
        + _muted('Prefer not to get this weekly? <a href="' + _PUBLIC_URL + '/settings/notifications" style="color:#3b82f6;">Change notification preferences</a>.')
    )
    preheader = f"{sent} emails · {leads} leads · {images} images this week."
    return await _send(user["email"], "Your week on MAARS", body, preheader)
