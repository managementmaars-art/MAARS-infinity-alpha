"""Provider Onboarding — operator-driven signup + API-key capture.

Activates dormant providers by opening their signup page in the in-app
BrowserPanel, letting the operator sign in / accept ToS / enter payment
themselves, then auto-navigating to the API-keys dashboard and
extracting the key via DOM to save into credential_vault.

Why operator-driven:
  • Unattended signup would bind the operator to ToS they didn't review.
  • Providers require 2FA / payment / captchas that automation can't
    solve reliably.
  • Account creation relationships are legal entities; the human must
    click "I agree".

What IS automated:
  • Opening the right signup URL in one click.
  • Once signed in, navigating to the API-keys dashboard.
  • DOM-scraping the displayed key.
  • Writing it to credential_vault + .env so it shows LIVE in the
    model-activation report within seconds.

The provider-specific metadata below is best-effort — DOM selectors
drift as providers redesign their dashboards. If extraction fails the
operator can paste the key manually via the same UI.
"""
from __future__ import annotations
import logging
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class OnboardingProvider:
    provider: str
    display_name: str
    signup_url: str               # where operator signs up / signs in
    api_keys_url: str             # dashboard page with API keys
    supports_google_oauth: bool   # whether "Sign in with Google" is available
    needs_credit_card: bool       # if True, key gating before usage
    env_var: str                  # .env variable name the key is written to
    key_selector: Optional[str] = None      # CSS selector to DOM-scrape key
    key_text_fallback: Optional[str] = None # regex pattern on page body
    signup_notes: str = ""        # hints for the operator (2FA, region lock, etc.)
    aliases: list[str] = field(default_factory=list)


# ── Provider onboarding registry ─────────────────────────────────────
#
# Focused on the 7 unconfigured providers flagged by the model-activation
# report. URLs current as of 2026-04; if a provider redesigns, update here.

PROVIDERS: dict[str, OnboardingProvider] = {
    "writer": OnboardingProvider(
        provider="writer",
        display_name="Writer",
        signup_url="https://app.writer.com/signup",
        api_keys_url="https://app.writer.com/aistudio/organization/api-keys",
        supports_google_oauth=True,
        needs_credit_card=False,
        env_var="WRITER_API_KEY",
        key_selector='[data-testid="api-key-value"]',
        signup_notes="Free tier available. Google OAuth supported.",
    ),
    "reka": OnboardingProvider(
        provider="reka",
        display_name="Reka",
        signup_url="https://platform.reka.ai/signup",
        api_keys_url="https://platform.reka.ai/api-keys",
        supports_google_oauth=True,
        needs_credit_card=True,
        env_var="REKA_API_KEY",
        key_selector='code.api-key',
        signup_notes="Free $5 credit on signup. Google OAuth supported.",
    ),
    "arcee": OnboardingProvider(
        provider="arcee",
        display_name="Arcee AI",
        signup_url="https://conductor.arcee.ai/signup",
        api_keys_url="https://conductor.arcee.ai/settings/api-keys",
        supports_google_oauth=True,
        needs_credit_card=True,
        env_var="ARCEE_API_KEY",
        signup_notes="Enterprise-focused. Google OAuth supported. Credit card required for API access.",
    ),
    "lepton": OnboardingProvider(
        provider="lepton",
        display_name="Lepton AI",
        signup_url="https://dashboard.lepton.ai/signup",
        api_keys_url="https://dashboard.lepton.ai/settings/api-tokens",
        supports_google_oauth=True,
        needs_credit_card=True,
        env_var="LEPTON_API_KEY",
        signup_notes="Recently acquired by NVIDIA. Google OAuth + GitHub OAuth available.",
    ),
    "minimax": OnboardingProvider(
        provider="minimax",
        display_name="MiniMax",
        signup_url="https://www.minimaxi.com/register",
        api_keys_url="https://www.minimaxi.com/user-center/basic-information/interface-key",
        supports_google_oauth=False,
        needs_credit_card=False,
        env_var="MINIMAX_API_KEY",
        signup_notes="China-based. Email + phone verification required. No Google OAuth. Chinese phone may be required.",
    ),
    "upstage": OnboardingProvider(
        provider="upstage",
        display_name="Upstage",
        signup_url="https://console.upstage.ai/signup",
        api_keys_url="https://console.upstage.ai/api-keys",
        supports_google_oauth=True,
        needs_credit_card=False,
        env_var="UPSTAGE_API_KEY",
        signup_notes="Free $10 credit on signup. Google OAuth supported.",
    ),
    "qwen": OnboardingProvider(
        provider="qwen",
        display_name="Qwen (DashScope)",
        signup_url="https://dashscope.console.aliyun.com/",
        api_keys_url="https://dashscope.console.aliyun.com/apiKey",
        supports_google_oauth=False,
        needs_credit_card=False,
        env_var="DASHSCOPE_API_KEY",
        signup_notes="Requires Alibaba Cloud account. International version available. No Google OAuth.",
    ),
    "yi": OnboardingProvider(
        provider="yi",
        display_name="Yi (01.AI)",
        signup_url="https://platform.01.ai/signup",
        api_keys_url="https://platform.01.ai/keys",
        supports_google_oauth=True,
        needs_credit_card=False,
        env_var="YI_API_KEY",
        signup_notes="Free trial credits. Google OAuth recently enabled.",
    ),
    "zhipu": OnboardingProvider(
        provider="zhipu",
        display_name="Zhipu AI (BigModel)",
        signup_url="https://open.bigmodel.cn/",
        api_keys_url="https://open.bigmodel.cn/usercenter/apikeys",
        supports_google_oauth=False,
        needs_credit_card=False,
        env_var="ZHIPU_API_KEY",
        signup_notes="Chinese provider. Chinese phone usually required for verification.",
    ),
    "doubao": OnboardingProvider(
        provider="doubao",
        display_name="Doubao (Volcengine)",
        signup_url="https://console.volcengine.com/auth/login",
        api_keys_url="https://console.volcengine.com/iam/keymanage",
        supports_google_oauth=False,
        needs_credit_card=False,
        env_var="DOUBAO_API_KEY",
        signup_notes="ByteDance cloud account required. No Google OAuth.",
    ),
    "bedrock": OnboardingProvider(
        provider="bedrock",
        display_name="AWS Bedrock",
        signup_url="https://aws.amazon.com/bedrock/",
        api_keys_url="https://console.aws.amazon.com/iam/home#/security_credentials",
        supports_google_oauth=False,
        needs_credit_card=True,
        env_var="AWS_ACCESS_KEY_ID",
        signup_notes="AWS account required. IAM access key (20-char + 40-char secret). Enable Bedrock model access in console after creating account.",
        aliases=["amazon", "aws"],
    ),
    "inception": OnboardingProvider(
        provider="inception",
        display_name="Inception Labs",
        signup_url="https://platform.inceptionlabs.ai/signup",
        api_keys_url="https://platform.inceptionlabs.ai/api-keys",
        supports_google_oauth=True,
        needs_credit_card=True,
        env_var="INCEPTION_API_KEY",
        signup_notes="Diffusion LLMs. Google OAuth available.",
    ),
    "bytez": OnboardingProvider(
        provider="bytez",
        display_name="Bytez",
        signup_url="https://app.bytez.com/signup",
        api_keys_url="https://app.bytez.com/profile",
        supports_google_oauth=True,
        needs_credit_card=False,
        env_var="BYTEZ_API_KEY",
        signup_notes="Free tier 100 req/day. Google OAuth supported. Exposes 2000+ models via unified API.",
    ),
    "meta_llama_api": OnboardingProvider(
        provider="meta_llama_api",
        display_name="Meta Llama API",
        signup_url="https://llama.developer.meta.com/",
        api_keys_url="https://llama.developer.meta.com/api-keys",
        supports_google_oauth=False,
        needs_credit_card=False,
        env_var="LLAMA_API_KEY",
        signup_notes="Requires Meta / Facebook developer account. Limited availability.",
    ),
}


def list_providers(unconfigured_only: bool = True) -> list[dict]:
    """Return onboarding metadata for the admin UI. If unconfigured_only,
    filter to providers whose env var isn't yet set in the environment."""
    import os
    out = []
    for p in PROVIDERS.values():
        live = bool(os.environ.get(p.env_var))
        if unconfigured_only and live:
            continue
        out.append({
            "provider":              p.provider,
            "display_name":          p.display_name,
            "signup_url":            p.signup_url,
            "api_keys_url":          p.api_keys_url,
            "supports_google_oauth": p.supports_google_oauth,
            "needs_credit_card":     p.needs_credit_card,
            "env_var":               p.env_var,
            "signup_notes":          p.signup_notes,
            "status":                "live" if live else "needs_key",
        })
    return out


async def start_session(provider: str, user_id: str) -> dict:
    """Open a BrowserPanel session at the provider's signup URL so the
    operator can sign in in-app (cookies persist across sessions)."""
    p = PROVIDERS.get(provider)
    if not p:
        return {"ok": False, "error": f"unknown_provider: {provider}"}
    from services.browser_service import get_browser_pool
    pool = get_browser_pool()
    session = await pool.open(
        user_id=user_id,
        agent_id="provider_onboarding",
        start_url=p.signup_url,
    )
    # Hand the session to the operator — they'll enter credentials, accept
    # ToS, complete 2FA, etc. The session cookies persist so when they
    # click "Grab key" later, we reuse the signed-in state.
    session.take_control("user")
    return {
        "ok":         True,
        "provider":   provider,
        "session_id": session.session_id,
        "signup_url": p.signup_url,
        "api_keys_url": p.api_keys_url,
        "next_step":  "Sign in, accept ToS, then click 'Grab API key'.",
    }


async def grab_key(provider: str, user_id: str, session_id: str) -> dict:
    """After the operator is signed in, navigate the same session to the
    provider's API-keys page and extract the key via DOM. Saves to
    credential_vault + writes to .env so it shows LIVE immediately."""
    p = PROVIDERS.get(provider)
    if not p:
        return {"ok": False, "error": f"unknown_provider: {provider}"}
    from services.browser_service import get_browser_pool
    pool = get_browser_pool()
    session = pool.get(session_id)
    if not session:
        return {"ok": False, "error": "session_not_found"}
    try:
        await session.navigate(p.api_keys_url, caller="system")
    except Exception as exc:
        return {"ok": False, "error": f"navigate_failed: {exc}"}

    extracted: str | None = None
    # Try CSS selector extraction first.
    if p.key_selector:
        try:
            extracted = await session.extract_text(p.key_selector)
            if extracted:
                extracted = extracted.strip()
        except Exception:
            pass
    # Fallback: regex on page body for typical API-key shapes.
    if not extracted:
        try:
            body = await session.extract_text("body")
            import re
            patterns = [
                r"sk-[A-Za-z0-9_\-]{32,}",       # OpenAI-style
                r"[A-Za-z0-9]{32,64}",           # generic long hex/alnum
            ]
            for pat in patterns:
                m = re.search(pat, body or "")
                if m:
                    extracted = m.group(0)
                    break
        except Exception:
            pass

    if not extracted:
        return {
            "ok": False,
            "error": "key_not_found",
            "hint": "Provider UI may have changed. Copy the key manually and submit via /admin/providers/onboarding/paste.",
            "api_keys_url": p.api_keys_url,
        }

    return await save_key(provider, user_id, extracted)


async def save_key(provider: str, user_id: str, api_key: str) -> dict:
    """Persist an API key to the credential vault + write to .env so
    the gateway picks it up immediately. Used by both DOM-extraction and
    the paste-in fallback."""
    p = PROVIDERS.get(provider)
    if not p:
        return {"ok": False, "error": f"unknown_provider: {provider}"}
    api_key = (api_key or "").strip()
    if len(api_key) < 10:
        return {"ok": False, "error": "key_too_short"}
    try:
        from services import credential_vault
        await credential_vault.put(credential_vault.Credential(
            scope="user",
            scope_id=user_id,
            provider=p.provider,
            kind="api_key",
            secret=api_key,
            public={"display_name": p.display_name},
            metadata={"source": "onboarding_flow", "env_var": p.env_var},
        ))
    except Exception as exc:
        logger.warning("credential_vault.put failed for %s: %s", provider, exc)

    # Write to .env so llm_gateway + provider catalog pick it up without
    # a restart (most adapters read from env on call).
    try:
        from services import env_writer
        env_writer.upsert({p.env_var: api_key})
        env_writer.sync_os({p.env_var: api_key})
    except Exception as exc:
        logger.warning("env_writer failed for %s: %s", provider, exc)

    return {
        "ok":           True,
        "provider":     provider,
        "env_var":      p.env_var,
        "key_preview":  api_key[:6] + "…" + api_key[-4:] if len(api_key) > 12 else "****",
        "status":       "live",
    }
