"""Per-provider smoke test — hit every provider with `hello` via the gateway.

Reports: OK / FAIL + reason for each configured provider. Writes a status map
so the frontend can show a green/red pass-fail badge per provider card.
"""
from __future__ import annotations
import asyncio
import json
import time
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).parent.parent.parent
load_dotenv(ROOT / ".env")

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

REPORT_PATH = Path(__file__).parent / "provider_smoke_report.json"

# One representative model per provider — smallest/fastest current IDs.
# Historical IDs that 404'd have been updated to their replacements.
FIRST_MODEL = {
    "openai":      "gpt-4o-mini",
    "anthropic":   "claude-haiku-4-5-20251001",      # was 20250929 (wrong date)
    "gemini":      "gemini-2.5-flash",
    "xai":         "grok-3-mini",
    "deepseek":    "deepseek-chat",
    "mistral":     "mistral-small-latest",
    "perplexity":  "sonar",
    "cohere":      "command-r-plus-08-2024",         # was command-r (retired)
    "groq":        "llama-3.1-8b-instant",
    "cerebras":    "llama3.1-8b",                    # Cerebras slug (not llama-3.1-8b)
    "together":    "meta-llama/Llama-3.3-70B-Instruct-Turbo",
    "fireworks":   "accounts/fireworks/models/deepseek-v3p1",  # account has this deployed
    "ai21":        "jamba-mini",                     # was jamba-mini-1.7 (doesn't exist)
    "sambanova":   "Meta-Llama-3.3-70B-Instruct",
    "nvidia":      "meta/llama-3.1-8b-instruct",
    "novita":      "meta-llama/llama-3.1-8b-instruct",
    "hyperbolic":  "meta-llama/Llama-3.3-70B-Instruct",
    "upstage":     "solar-pro",
    "amazon":      "us.amazon.nova-micro-v1:0",       # inference profile ID — what Converse actually accepts (plain modelId returns "Operation not allowed" in us-east-1)
    "huggingface": "meta-llama/Llama-3.1-8B-Instruct",
    "openrouter":  "openai/gpt-oss-120b:free",  # free tier — most reliable upstream (OpenAI direct)
    "moonshot":    "kimi-k2-turbo-preview",        # intl free tier
    "qwen":        "qwen-turbo",
    "zhipu":       "glm-4.5-flash",                  # Z.ai intl free-tier model
    "doubao":      "doubao-pro-128k",
    "minimax":     "MiniMax-Text-01",
    "yi":          "yi-lightning",
    "writer":      "palmyra-x5",
    "arcee":       "trinity-mini",
    "inception":   "mercury-2",
    "llama":       "Llama-3.3-70B-Instruct",
    "lambda":      "hermes-3-405b",
    "bytez":       "microsoft/DialoGPT-small",  # Bytez free tier only supports `sm` models
    "lepton":      "llama3-1-405b",
    # Media-only providers (can't chat-test — skip)
    "elevenlabs":  None,
}


async def smoke_provider(provider: str, model: str, api_key: str) -> dict:
    """Try call_direct_llm with a tiny prompt; 12s default, 30s for cold-start providers."""
    from services.llm_service import call_direct_llm
    # Bytez free-tier `sm` models cold-start on first call; Cohere v2 sometimes
    # TLS-stalls in Windows' httpx stack. Give them a longer budget.
    timeout = 30 if provider in ("bytez", "cohere", "zhipu", "openrouter", "fireworks") else 12
    t0 = time.time()
    try:
        resp = await asyncio.wait_for(
            call_direct_llm(provider, model, "Reply with just OK.", "hi", [], api_key),
            timeout=timeout,
        )
        wall = round((time.time() - t0) * 1000)
        ok = bool(resp and resp.strip())
        return {"provider": provider, "model": model, "ok": ok,
                "wall_ms": wall, "preview": (resp or "").strip()[:80]}
    except asyncio.TimeoutError:
        return {"provider": provider, "model": model, "ok": False,
                "wall_ms": int((time.time() - t0) * 1000), "error": f"timeout_{timeout}s"}
    except Exception as e:
        msg = str(e)[:240]
        return {"provider": provider, "model": model, "ok": False,
                "wall_ms": int((time.time() - t0) * 1000),
                "error": f"{type(e).__name__}: {msg}"}


async def main():
    from shared.utils import get_api_keys
    keys = await get_api_keys()

    results = []
    for provider, model in FIRST_MODEL.items():
        if model is None:
            results.append({"provider": provider, "ok": None, "note": "media-only"})
            continue
        api_key = keys.get(provider, "")
        if not api_key:
            results.append({"provider": provider, "ok": None, "note": "no_key"})
            continue
        r = await smoke_provider(provider, model, api_key)
        results.append(r)
        status = "OK  " if r.get("ok") else "FAIL"
        tail = r.get("preview") or r.get("error", "")
        print(f"  [{status}] {provider:15s} {model:50s} {r.get('wall_ms'):>5}ms  {tail[:80]}")

    report = {
        "results": results,
        "summary": {
            "total": len(results),
            "ok":     sum(1 for r in results if r.get("ok") is True),
            "fail":   sum(1 for r in results if r.get("ok") is False),
            "no_key": sum(1 for r in results if r.get("note") == "no_key"),
            "media":  sum(1 for r in results if r.get("note") == "media-only"),
        },
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2))
    print()
    print(json.dumps(report["summary"], indent=2))
    print(f"\nReport: {REPORT_PATH}")


if __name__ == "__main__":
    asyncio.run(main())
