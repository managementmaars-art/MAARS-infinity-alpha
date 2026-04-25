"""Real-usage cost simulation — measures ACTUAL COGS per modality bucket.

Runs realistic workloads against live router + providers, reads the
actual usd spent from gateway_usage_logs / router meta, and produces
the per-modality base cost the operator needs to size plan allowances.

Modality buckets measured:
  1. chat_short      — routine chat messages (hey, how, what)
  2. chat_long       — analysis + reasoning prompts
  3. agent_sop       — full 6-step Office SOP runs
  4. vibe_create     — "build me an app" (single big generation)
  5. vibe_chat       — "change this file" (big context + big output)
  6. image           — image generation chain
  7. video_clip      — 4-second video clip via cheapest chain
  8. voiceover       — TTS with multilingual fallback
  9. stt             — STT (synthetic 5-sec audio)

Output: backend/scripts/cost_simulation_report.json + stdout table.

IMPORTANT: this script COSTS REAL MONEY per run. It defaults to small
iteration counts so a full pass stays under ~$1. Scale via ITERATIONS
env var only if you need tighter variance.
"""
from __future__ import annotations
import asyncio
import json
import os
import sys
import time
import uuid
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).parent.parent.parent
load_dotenv(ROOT / ".env")
sys.path.insert(0, str(Path(__file__).parent.parent))

REPORT_PATH = Path(__file__).parent / "cost_simulation_report.json"
USER_ID = os.environ.get("SIM_USER_ID", "cost_sim_user_maars")

# Per-bucket iteration counts. Thorough mode — sized for ≤5% variance.
# Media capped lower because each call costs real money.
ITER_CHAT_SHORT   = int(os.environ.get("ITER_CHAT_SHORT",   80))
ITER_CHAT_LONG    = int(os.environ.get("ITER_CHAT_LONG",    40))
ITER_AGENT_SOP    = int(os.environ.get("ITER_AGENT_SOP",    20))
ITER_VIBE_CREATE  = int(os.environ.get("ITER_VIBE_CREATE",  10))
ITER_VIBE_CHAT    = int(os.environ.get("ITER_VIBE_CHAT",    10))
ITER_IMAGE        = int(os.environ.get("ITER_IMAGE",        20))
ITER_VIDEO        = int(os.environ.get("ITER_VIDEO",         8))
ITER_TTS          = int(os.environ.get("ITER_TTS",          18))
ITER_STT          = int(os.environ.get("ITER_STT",           6))


# ── Workload fixtures ────────────────────────────────────────────────

CHAT_SHORT_PROMPTS = [
    "What are three ways to reduce customer churn?",
    "Explain retrieval-augmented generation in 2 sentences.",
    "Draft a 60-word reply to a customer asking about refund eligibility.",
    "Give me a 1-sentence value prop for a B2B SaaS analytics tool.",
    "Summarize the difference between OKRs and KPIs.",
    "Write a one-line LinkedIn opener for a cold SDR outreach.",
    "Name 5 well-known productivity tools.",
    "What's a good weekly cadence for a product standup?",
    "Give me 3 metrics every PLG startup should track.",
    "Explain idempotency in 30 words.",
]

CHAT_LONG_PROMPTS = [
    "Our SaaS has $40k MRR at 8% monthly churn and a $150 CAC. We sell to small agencies. "
    "Should we focus next quarter on onboarding, expansion, or reducing churn? Give me "
    "a reasoned answer with the math to back each option.",
    "Compare Postgres vs. MongoDB for a multi-tenant analytics platform that ingests 50M "
    "events/day and serves dashboards with sub-second latency. Discuss tradeoffs in schema "
    "flexibility, query performance, ops burden, and cost at scale.",
    "A series-A startup wants to hire either one senior SRE or three junior full-stack "
    "engineers for the same budget. Walk through the decision framework for each stage of "
    "scale (series A, B, C) and recommend.",
    "Design a promotion for a fitness app's Black Friday campaign that targets existing "
    "free users to convert. Include the offer mechanics, messaging, channels, and the "
    "metric to track success.",
    "Review this product roadmap critique: 'too many horizontal features, not enough "
    "depth.' How do you determine if that's right without a rewrite? What data do you "
    "gather, what interviews do you run, and how do you synthesize the output?",
]

VIBE_CREATE_BRIEFS = [
    "A daily mood-tracker app: user picks an emoji + writes a one-line note, sees the last 30 days in a simple calendar.",
    "A Pomodoro timer with tag-based stats: user starts a 25-min timer with a tag, sees totals by tag + a 7-day bar chart.",
    "A quick-note app that persists in localStorage, with tag filtering, search, and a dark-mode toggle.",
]

VIBE_CHAT_MODS = [
    "Add dark-mode toggle and persist the preference.",
    "Add an export-to-CSV button for the mood history.",
    "Change the tag colors to pastel and add a delete-with-confirm dialog.",
]

IMAGE_PROMPTS = [
    "A premium-looking matte-black packaging box for a wellness tea brand, soft studio lighting, minimalist.",
    "A hero illustration of a modern city skyline at sunset, purple-orange gradient, digital art.",
    "A flat-design icon set of 6 fitness activities (run, swim, cycle, yoga, lift, hike) in monochrome.",
    "A lifestyle product photo of a ceramic water bottle on a wooden kitchen counter, morning light.",
    "A 3D render of a rose-gold smartwatch floating on a pastel gradient background.",
    "An isometric illustration of a small home office desk with plants and a laptop.",
]

VIDEO_PROMPTS = [
    "A cup of steaming green tea on a wooden desk, slow dolly-in, 4 seconds, soft morning light.",
    "A premium serum bottle rotating on a pastel pink background, product-ad style, 4 seconds.",
    "A flat-lay of healthy breakfast items (oats, berries, coffee) with subtle camera pan, 4 seconds.",
]

TTS_SAMPLES = [
    ("Welcome to MAARS. Your AI team is ready to get to work. Let's begin.", "en", "rachel"),
    ("Bienvenido a MAARS. Tu equipo de inteligencia artificial está listo.", "es", "rachel"),
    ("Bienvenue chez MAARS. Votre équipe d'IA est prête à commencer.",        "fr", "rachel"),
    ("Willkommen bei MAARS. Ihr KI-Team ist bereit, loszulegen.",             "de", "rachel"),
    ("MAARSへようこそ。AIチームは仕事を始める準備ができています。",                "ja", "rachel"),
    ("مرحبا بك في مارس. فريق الذكاء الاصطناعي الخاص بك جاهز للعمل.",            "ar", "rachel"),
]


# ── Helpers ──────────────────────────────────────────────────────────

async def _ensure_wallet() -> None:
    from services.billing.wallet_service import grant, get_summary
    try:
        s = await get_summary(USER_ID)
        if (s.get("balance") or 0) < 10_000:
            await grant(USER_ID, amount=50_000,
                        reference_type="cost_simulation",
                        reference_id=f"sim_{int(time.time())}",
                        description="Cost simulation top-up")
    except Exception as exc:
        print(f"[sim] wallet ensure skipped: {exc}")


async def _run_chat_many(prompts: list[str], *, source_tag: str, iterations: int,
                         max_tokens: int = 400, temperature: float = 0.4) -> None:
    from services.llm_gateway import complete_text
    for i in range(iterations):
        prompt = prompts[i % len(prompts)]
        try:
            await complete_text(
                user_id=USER_ID,
                system_prompt="You are a helpful assistant.",
                user_prompt=prompt,
                model="maars/auto",
                max_tokens=max_tokens,
                temperature=temperature,
                source=source_tag,
                enable_cache=False,  # real cost per call, not cache-warmed
            )
        except Exception as exc:
            print(f"[sim][{source_tag}] iter {i}: {type(exc).__name__}: {str(exc)[:120]}")


async def _run_vibe_create_many(briefs: list[str], *, iterations: int) -> None:
    from services.llm_gateway import complete_text
    system_msg = (
        "You are a senior full-stack developer. Return a SINGLE HTML file "
        "with inline CSS + JS (Tailwind via CDN). Reply with JSON only: "
        '{\"title\": \"...\", \"files\": [{\"name\":\"index.html\",\"content\":\"...\"}]}'
    )
    for i in range(iterations):
        brief = briefs[i % len(briefs)]
        try:
            await complete_text(
                user_id=USER_ID,
                system_prompt=system_msg,
                user_prompt=f"Build this app: {brief}",
                model="maars/auto",
                max_tokens=4000,        # vibe-create returns a big file
                temperature=0.3,
                source="sim.vibe_create",
                enable_cache=False,
            )
        except Exception as exc:
            print(f"[sim][vibe_create] iter {i}: {type(exc).__name__}: {str(exc)[:120]}")


async def _run_vibe_chat_many(mods: list[str], *, iterations: int) -> None:
    from services.llm_gateway import complete_text
    # Simulate a ~3k-char file context (typical of real apps).
    existing_file = (
        "<!DOCTYPE html><html><head><title>Notes</title></head>"
        "<body><div id='app'></div><script>"
        + ("// dummy state + handlers placeholder line\n" * 60)
        + "</script></body></html>"
    )
    system_msg = (
        "You are modifying an existing web app. Current file:\n\n"
        f"--- index.html ---\n{existing_file}\n\n"
        "The user wants a change. Return JSON with the full updated file."
    )
    for i in range(iterations):
        mod = mods[i % len(mods)]
        try:
            await complete_text(
                user_id=USER_ID,
                system_prompt=system_msg,
                user_prompt=mod,
                model="maars/auto",
                max_tokens=4000,
                temperature=0.3,
                source="sim.vibe_chat",
                enable_cache=False,
            )
        except Exception as exc:
            print(f"[sim][vibe_chat] iter {i}: {type(exc).__name__}: {str(exc)[:120]}")


async def _run_agent_sop(iterations: int) -> None:
    """Run the Office SOP runner so every agent step hits the router with
    source=office_sop:<agent>. Pick 3 different role families to avoid
    over-sampling one.
    """
    from db import db
    from services.agents.agent_office import get as office_get, run_sop

    # Pull 3 distinct offices (different role families).
    picked: list[dict] = []
    seen_depts: set = set()
    async for doc in db.agent_offices.find({}, {"_id": 0}).limit(200):
        d = doc.get("department", "?")
        if d in seen_depts:
            continue
        seen_depts.add(d)
        picked.append(doc)
        if len(picked) >= 3:
            break
    if not picked:
        return

    briefs = [
        "Write a 150-word summary of why we should launch in Europe this quarter.",
        "Draft a 3-step plan for improving weekly customer onboarding.",
        "Give me a structured answer to 'what's the highest-ROI change we can make in product next month?'",
    ]
    for i in range(iterations):
        target = picked[i % len(picked)]
        office = await office_get(target["agent_id"])
        if not office:
            continue
        try:
            await run_sop(office, briefs[i % len(briefs)], user_id=USER_ID)
        except Exception as exc:
            print(f"[sim][agent_sop] iter {i}: {type(exc).__name__}: {str(exc)[:120]}")


async def _run_images(prompts: list[str], *, iterations: int) -> list[dict]:
    from services.media_router import route_image
    results: list[dict] = []
    for i in range(iterations):
        prompt = prompts[i % len(prompts)]
        try:
            _, meta = await route_image(
                prompt=prompt, quality="standard",
                user_id=USER_ID, enhance=False,  # don't double-charge on enhancement call
            )
            results.append({
                "ok": True, "provider": meta.get("provider"),
                "model": meta.get("model"), "cost_usd": float(meta.get("cost_usd") or 0.0),
                "wall_s": meta.get("wall_s"),
            })
        except Exception as exc:
            results.append({"ok": False, "error": f"{type(exc).__name__}: {str(exc)[:120]}"})
    return results


async def _run_videos(prompts: list[str], *, iterations: int) -> list[dict]:
    from services.media_router import route_video
    results: list[dict] = []
    for i in range(iterations):
        prompt = prompts[i % len(prompts)]
        try:
            _, meta = await route_video(
                prompt=prompt, duration=4, user_id=USER_ID, enhance=False,
            )
            results.append({
                "ok": True, "provider": meta.get("provider"),
                "model": meta.get("model"), "cost_usd": float(meta.get("cost_usd") or 0.0),
                "wall_s": meta.get("wall_s"),
            })
        except Exception as exc:
            results.append({"ok": False, "error": f"{type(exc).__name__}: {str(exc)[:120]}"})
    return results


async def _run_tts(samples: list[tuple[str, str, str]], *, iterations: int) -> list[dict]:
    from services.media_router import route_tts
    results: list[dict] = []
    for i in range(iterations):
        text, lang, voice = samples[i % len(samples)]
        try:
            _, meta = await route_tts(text=text, voice=voice, language=lang, tier="premium")
            results.append({
                "ok": True, "provider": meta.get("provider"),
                "model": meta.get("model"), "cost_usd": float(meta.get("cost_usd") or 0.0),
                "chars": len(text), "language": lang,
            })
        except Exception as exc:
            results.append({"ok": False, "error": f"{type(exc).__name__}: {str(exc)[:120]}"})
    return results


async def _run_stt(iterations: int) -> list[dict]:
    """Generate a short synthetic audio via TTS, then transcribe it.
    This keeps the sim self-contained (no need for a real audio asset).
    """
    from services.media_router import route_tts, route_stt
    # Pre-generate one short clip we can reuse across iterations.
    clip, _ = await route_tts(
        text="Hello, this is a MAARS cost simulation test.",
        voice="nova", tier="standard",
    )
    results: list[dict] = []
    for i in range(iterations):
        try:
            _, meta = await route_stt(
                audio_bytes=clip, filename="sim.mp3", duration_seconds=5.0,
            )
            results.append({
                "ok": True, "provider": meta.get("provider"),
                "model": meta.get("model"), "cost_usd": float(meta.get("cost_usd") or 0.0),
            })
        except Exception as exc:
            results.append({"ok": False, "error": f"{type(exc).__name__}: {str(exc)[:120]}"})
    return results


async def _aggregate_llm_costs(source_tag: str, *, since_ts: int = 0) -> dict:
    """Pull ALL usage-log rows for this source tag + user. The gateway
    appends tier suffixes (`_cheap`, `_premium`, `_economy`, `_standard`)
    to the source, so match with a regex anchor, not exact.
    """
    from db import db
    # Escape the caller's tag so dots in `sim.chat_short` don't become
    # wildcards, then anchor and allow any tier suffix.
    import re as _re
    anchored = f"^{_re.escape(source_tag)}(_cheap|_premium|_economy|_standard)?$"
    query: dict = {
        "user_id": USER_ID,
        "source":  {"$regex": anchored},
    }
    rows = await db.gateway_usage_logs.find(
        query, {"_id": 0}
    ).sort([("ts", -1)]).to_list(10_000)
    # Time-filter in Python — some rows use `ts` (int), some `created_at` (iso).
    if since_ts:
        import datetime as _dt
        rows_filtered = []
        for r in rows:
            ts = r.get("ts")
            if isinstance(ts, (int, float)) and ts >= since_ts:
                rows_filtered.append(r); continue
            ca = r.get("created_at")
            if isinstance(ca, str):
                try:
                    epoch = _dt.datetime.fromisoformat(ca.replace("Z","+00:00")).timestamp()
                    if epoch >= since_ts:
                        rows_filtered.append(r)
                except Exception:
                    rows_filtered.append(r)
            else:
                rows_filtered.append(r)
        rows = rows_filtered
    total_usd = 0.0
    total_credits = 0
    calls = 0
    providers: dict[str, int] = {}
    models: dict[str, int] = {}
    per_call: list[float] = []
    for r in rows:
        calls += 1
        usd = float(r.get("cost_usd") or r.get("provider_cost_usd") or 0.0)
        total_usd += usd
        per_call.append(usd)
        total_credits += int(r.get("credits_charged") or 0)
        p = r.get("provider") or "?"
        m = r.get("model") or "?"
        providers[p] = providers.get(p, 0) + 1
        models[m] = models.get(m, 0) + 1
    per_call.sort()
    def _pct(p: float) -> float:
        if not per_call: return 0.0
        idx = min(len(per_call) - 1, int(len(per_call) * p))
        return round(per_call[idx], 6)
    return {
        "calls":         calls,
        "total_usd":     round(total_usd, 6),
        "per_call_usd":  round(total_usd / max(calls, 1), 6),
        "per_call_p50":  _pct(0.50),
        "per_call_p95":  _pct(0.95),
        "per_call_max":  round(max(per_call) if per_call else 0.0, 6),
        "total_credits": total_credits,
        "providers":     providers,
        "models":        models,
    }


# Providers we know are free (operator pays nothing real even if the
# router's cost_fn returns a fallback estimate). Used to produce an
# `actual_cost_usd` alongside the catalog estimate so the operator sees
# real COGS, not a placeholder.
FREE_MEDIA_PROVIDERS = frozenset({
    "pollinations",   # Free Flux — unlimited, no key
    "edge",           # Microsoft Edge TTS — unlimited, no key
    "local",          # Self-hosted — operator's box, no per-call cost
})


def _aggregate_media(results: list[dict]) -> dict:
    ok = [r for r in results if r.get("ok")]
    fail = [r for r in results if not r.get("ok")]
    # Catalog estimate (what router._tts_cost_usd etc. reports).
    total_catalog_usd = sum(float(r.get("cost_usd") or 0) for r in ok)
    # Real cost — zero out free providers.
    total_actual_usd = sum(
        0.0 if (r.get("provider") or "") in FREE_MEDIA_PROVIDERS
        else float(r.get("cost_usd") or 0)
        for r in ok
    )
    providers: dict[str, int] = {}
    models: dict[str, int] = {}
    per_call: list[float] = []
    for r in ok:
        p = r.get("provider") or "?"
        m = r.get("model") or "?"
        providers[p] = providers.get(p, 0) + 1
        models[m] = models.get(m, 0) + 1
        per_call.append(
            0.0 if p in FREE_MEDIA_PROVIDERS else float(r.get("cost_usd") or 0)
        )
    per_call.sort()
    def _pct(p: float) -> float:
        if not per_call: return 0.0
        idx = min(len(per_call) - 1, int(len(per_call) * p))
        return round(per_call[idx], 6)
    return {
        "calls":             len(results),
        "ok_calls":          len(ok),
        "fail_calls":        len(fail),
        "total_usd_catalog": round(total_catalog_usd, 6),
        "total_usd_actual":  round(total_actual_usd, 6),
        "per_call_usd":      round(total_actual_usd / max(len(ok), 1), 6),
        "per_call_p50":      _pct(0.50),
        "per_call_p95":      _pct(0.95),
        "per_call_max":      round(max(per_call) if per_call else 0.0, 6),
        "providers":         providers,
        "models":            models,
        "failure_samples":   [r.get("error") for r in fail[:3]],
    }


# ── Main ─────────────────────────────────────────────────────────────

def _stage(msg: str) -> None:
    """Live-flushed progress line — keeps stdout usable while the sim runs."""
    print(f"[sim] {msg}", flush=True)


async def main() -> None:
    t0 = time.time()
    await _ensure_wallet()
    _stage(f"starting cost simulation for user={USER_ID} at ts={int(t0)}")

    # Kick off workloads. Keep chat/SOP/vibe sequential so the free-tier
    # quota tracker isn't hammered in parallel (which would skew costs).
    _stage(f"chat_short × {ITER_CHAT_SHORT} ...")
    await _run_chat_many(CHAT_SHORT_PROMPTS, source_tag="sim.chat_short",
                         iterations=ITER_CHAT_SHORT, max_tokens=250)

    _stage(f"chat_long × {ITER_CHAT_LONG} ...")
    await _run_chat_many(CHAT_LONG_PROMPTS, source_tag="sim.chat_long",
                         iterations=ITER_CHAT_LONG, max_tokens=1200)

    _stage(f"vibe_create × {ITER_VIBE_CREATE} ...")
    await _run_vibe_create_many(VIBE_CREATE_BRIEFS, iterations=ITER_VIBE_CREATE)

    _stage(f"vibe_chat × {ITER_VIBE_CHAT} ...")
    await _run_vibe_chat_many(VIBE_CHAT_MODS, iterations=ITER_VIBE_CHAT)

    _stage(f"agent_sop × {ITER_AGENT_SOP} ...")
    await _run_agent_sop(ITER_AGENT_SOP)

    _stage(f"images × {ITER_IMAGE} ...")
    img_results = await _run_images(IMAGE_PROMPTS, iterations=ITER_IMAGE)

    _stage(f"videos × {ITER_VIDEO} (LTX first, expect slow) ...")
    vid_results = await _run_videos(VIDEO_PROMPTS, iterations=ITER_VIDEO)

    _stage(f"tts × {ITER_TTS} ...")
    tts_results = await _run_tts(TTS_SAMPLES, iterations=ITER_TTS)

    _stage(f"stt × {ITER_STT} ...")
    stt_results = await _run_stt(ITER_STT)

    # Give usage logs a moment to flush
    await asyncio.sleep(2)

    # Aggregate by modality bucket
    report = {
        "sim_version": 1,
        "started_at":  int(t0),
        "finished_at": int(time.time()),
        "wall_s":      round(time.time() - t0, 1),
        "user_id":     USER_ID,
        "iterations":  {
            "chat_short":   ITER_CHAT_SHORT,
            "chat_long":    ITER_CHAT_LONG,
            "agent_sop":    ITER_AGENT_SOP,
            "vibe_create":  ITER_VIBE_CREATE,
            "vibe_chat":    ITER_VIBE_CHAT,
            "image":        ITER_IMAGE,
            "video":        ITER_VIDEO,
            "tts":          ITER_TTS,
            "stt":          ITER_STT,
        },
        "buckets": {
            "chat_short":   await _aggregate_llm_costs("sim.chat_short",  since_ts=int(t0)),
            "chat_long":    await _aggregate_llm_costs("sim.chat_long",   since_ts=int(t0)),
            "vibe_create":  await _aggregate_llm_costs("sim.vibe_create", since_ts=int(t0)),
            "vibe_chat":    await _aggregate_llm_costs("sim.vibe_chat",   since_ts=int(t0)),
            # SOP source is office_sop:<agent>:<step> — aggregate all
            "agent_sop":    await _aggregate_sop_bucket(since_ts=int(t0)),
            "image":        _aggregate_media(img_results),
            "video":        _aggregate_media(vid_results),
            "tts":          _aggregate_media(tts_results),
            "stt":          _aggregate_media(stt_results),
        },
    }

    REPORT_PATH.write_text(json.dumps(report, indent=2, default=str))

    # Pretty stdout — defensive against empty buckets (earlier run crashed on max([])).
    print(flush=True)
    print("=" * 92, flush=True)
    print(f"{'BUCKET':<14} {'CALLS':>6} {'USD_TOT':>10} {'USD_AVG':>11} {'USD_P50':>11} {'USD_P95':>11} {'USD_MAX':>11} TOP", flush=True)
    print("-" * 92, flush=True)
    for bucket, stats in report["buckets"].items():
        provs = stats.get("providers") or {}
        top_prov = (max(provs.items(), key=lambda x: x[1])[0] if provs else "—")
        # For media buckets, prefer the actual-cost total (zeroed for free providers).
        total = stats.get("total_usd_actual")
        if total is None:
            total = stats.get("total_usd", 0)
        print(
            f"{bucket:<14} {stats.get('calls',0):>6} "
            f"{total:>10.6f} {stats.get('per_call_usd',0):>11.6f} "
            f"{stats.get('per_call_p50',0):>11.6f} {stats.get('per_call_p95',0):>11.6f} "
            f"{stats.get('per_call_max',0):>11.6f} {top_prov}",
            flush=True,
        )
    print("=" * 92, flush=True)
    print(f"Report: {REPORT_PATH}", flush=True)
    print(f"Wall time: {report['wall_s']}s", flush=True)


async def _aggregate_sop_bucket(*, since_ts: int = 0) -> dict:
    """Agent SOP steps use source `office_sop:<agent>:<step>` (with tier
    suffix). Aggregate for this run only, filtering by timestamp."""
    from db import db
    rows = await db.gateway_usage_logs.find({
        "user_id": USER_ID,
        "source":  {"$regex": "^office_sop:"},
    }, {"_id": 0}).sort([("ts", -1)]).to_list(10_000)
    if since_ts:
        import datetime as _dt
        keep: list[dict] = []
        for r in rows:
            ts = r.get("ts")
            if isinstance(ts, (int, float)) and ts >= since_ts:
                keep.append(r); continue
            ca = r.get("created_at")
            if isinstance(ca, str):
                try:
                    if _dt.datetime.fromisoformat(ca.replace("Z","+00:00")).timestamp() >= since_ts:
                        keep.append(r)
                except Exception:
                    keep.append(r)
        rows = keep
    total_usd = sum(float(r.get("cost_usd") or 0) for r in rows)
    total_credits = sum(int(r.get("credits_charged") or 0) for r in rows)
    providers: dict[str, int] = {}
    per_call: list[float] = []
    for r in rows:
        p = r.get("provider") or "?"
        providers[p] = providers.get(p, 0) + 1
        per_call.append(float(r.get("cost_usd") or 0))
    per_call.sort()
    def _pct(p: float) -> float:
        if not per_call: return 0.0
        idx = min(len(per_call) - 1, int(len(per_call) * p))
        return round(per_call[idx], 6)
    return {
        "calls":         len(rows),
        "total_usd":     round(total_usd, 6),
        "per_call_usd":  round(total_usd / max(len(rows), 1), 6),
        "per_call_p50":  _pct(0.50),
        "per_call_p95":  _pct(0.95),
        "per_call_max":  round(max(per_call) if per_call else 0.0, 6),
        "total_credits": total_credits,
        "providers":     providers,
    }


if __name__ == "__main__":
    asyncio.run(main())
