"""Live multi-modal benchmark. Hits every generation endpoint, measures real wall-time
and derives real fulfillment cost from the known per-unit pricing. Writes a JSON report
to backend/scripts/multimodal_benchmark_report.json.

Usage (PowerShell/bash, from repo root):
    cd backend
    python scripts/multimodal_benchmark.py

Requires the backend to be running at http://localhost:8000 and the caller's JWT to be
exported as BENCH_JWT env var, or passed via --token.
"""
from __future__ import annotations
import argparse, io, json, os, sys, time, base64
from pathlib import Path
from typing import Any
import httpx

BASE = os.environ.get("BENCH_BASE", "http://localhost:8000")
REPORT_PATH = Path(__file__).parent / "multimodal_benchmark_report.json"

# Fulfillment cost (USD) per unit, sourced from provider pricing pages as of 2026-04.
COST = {
    "dall-e-3":              {"unit": "image",   "usd_per_unit": 0.040},
    "gpt-image-1":           {"unit": "image",   "usd_per_unit": 0.020},  # standard quality
    "gemini-3-pro-image":    {"unit": "image",   "usd_per_unit": 0.020},
    "sora-2":                {"unit": "sec",     "usd_per_unit": 0.100},
    "tts-1":                 {"unit": "1k_char", "usd_per_unit": 0.015},
    "elevenlabs_turbo_v25":  {"unit": "1k_char", "usd_per_unit": 0.18},   # Turbo v2.5
    "elevenlabs_multi_v2":   {"unit": "1k_char", "usd_per_unit": 0.30},   # Multilingual v2
    "whisper-1":             {"unit": "minute",  "usd_per_unit": 0.006},
    # Chat (approximate blended per-call for a ~500-tok response)
    "chat_cheap":            {"unit": "call",    "usd_per_unit": 0.0001},  # deepseek/groq-free weighted
    "chat_mid":              {"unit": "call",    "usd_per_unit": 0.002},   # gpt-4o, sonnet
    "chat_flagship":         {"unit": "call",    "usd_per_unit": 0.010},   # gpt-5, opus
}


MAARS_API_KEY = os.environ.get("MAARS_API_KEY", "maars_sk_live_ce90e122f660137026c9de418d470c18a9c348e8")


class Bench:
    def __init__(self, token: str):
        self.token = token
        self.results: list[dict[str, Any]] = []
        # JWT for modality endpoints (/generate/*, /tts/*, /voice/*, /content/*, /vibe/*)
        self.client = httpx.Client(
            base_url=BASE,
            headers={"Authorization": f"Bearer {token}"},
            timeout=900.0,
        )
        # Separate client with MAARS API key for /api/v1/chat/completions
        self.v1_client = httpx.Client(
            base_url=BASE,
            headers={"Authorization": f"Bearer {MAARS_API_KEY}"},
            timeout=60.0,
        )

    def record(self, modality: str, model: str, cost_unit: float, units: float,
               wall_s: float, ok: bool, meta: dict | None = None):
        usd = round(cost_unit * units, 6)
        row = {
            "modality": modality,
            "model": model,
            "units": units,
            "unit_kind": COST.get(model, {}).get("unit", "n/a"),
            "usd_per_unit": cost_unit,
            "real_cost_usd": usd,
            "real_cost_credits": round(usd * 1000, 3),  # 1 credit = $0.001
            "wall_s": round(wall_s, 2),
            "ok": ok,
            "meta": meta or {},
        }
        self.results.append(row)
        print(f"  [{modality:10s}] {model:24s} | {units} {row['unit_kind']:7s} | "
              f"${usd:8.4f} = {row['real_cost_credits']:7.2f} credits | "
              f"{wall_s:6.1f}s | {'OK' if ok else 'FAIL'}")

    # ------------------------------------------------------------------ chat
    def bench_chat(self):
        print("\n=== Chat (via v1 gateway) ===")
        prompts = [
            ("What is the capital of France? One word.", "chat_cheap"),
            ("Write a 200-word blog intro about renewable energy.", "chat_mid"),
            ("Explain quantum entanglement in 3 paragraphs for a 12-year-old.", "chat_mid"),
            ("List 5 marketing taglines for a coffee shop.", "chat_cheap"),
            ("Generate Python code for a binary search tree with insert and search.", "chat_mid"),
        ]
        for prompt, tier in prompts:
            t = time.time()
            try:
                r = self.v1_client.post("/api/v1/chat/completions", json={
                    "model": "maars/auto",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 500,
                })
                ok = r.status_code == 200
                body = r.json() if r.headers.get("content-type","").startswith("application/json") else {}
                model = body.get("model", "unknown") if ok else f"err_{r.status_code}"
                # Internal cost tracked by gateway metadata (if available)
                usage = (body.get("usage") or {}) if ok else {}
                meta = {"status": r.status_code, "prompt_tokens": usage.get("prompt_tokens"),
                        "completion_tokens": usage.get("completion_tokens"),
                        "body_preview": str(body)[:200] if not ok else None}
            except Exception as e:
                ok, model, meta = False, f"exc_{type(e).__name__}", {"err": str(e)[:200]}
            self.record("chat", model if ok else tier, COST[tier]["usd_per_unit"], 1, time.time()-t, ok, meta=meta)

    # ----------------------------------------------------------------- image
    def bench_image(self):
        print("\n=== Image gen (via router) ===")
        for quality in ["standard", "premium"]:
            t = time.time()
            try:
                r = self.client.post("/api/generate/image", json={
                    "prompt": "A minimalist logo of a mountain and sun, modern design",
                    "quality": quality,
                })
                ok = r.status_code == 200
                body = r.json() if ok else {}
                meta = body.get("router", {}) if ok else {"status": r.status_code, "body": r.text[:200]}
                actual_model = meta.get("model", f"unknown_{quality}")
                actual_cost = meta.get("cost_usd", 0.02)
            except Exception as e:
                ok, actual_model, actual_cost, meta = False, quality, 0.02, {"err": str(e)[:200]}
            self.record("image", actual_model, actual_cost, 1, time.time()-t, ok, meta=meta)

    # ----------------------------------------------------------------- video
    def bench_video(self):
        print("\n=== Video gen (Sora-2 via router) — slow, may take 3-10 min ===")
        for dur in [4]:
            t = time.time()
            try:
                r = self.client.post("/api/generate/video", json={
                    "prompt": "A sunset over calm ocean waves, cinematic",
                    "size": "1280x720",
                    "duration": dur,
                }, timeout=900)
                ok = r.status_code == 200
                body = r.json() if ok else {}
                meta = body.get("router", {}) if ok else {"status": r.status_code, "body": r.text[:300]}
                cost_usd = meta.get("cost_usd", COST["sora-2"]["usd_per_unit"] * dur)
            except Exception as e:
                ok, cost_usd, meta = False, COST["sora-2"]["usd_per_unit"] * dur, {"err": str(e)[:200]}
                print(f"    exception: {type(e).__name__}: {str(e)[:120]}")
            self.record("video", "sora-2", cost_usd, 1, time.time()-t, ok, meta=meta)

    # ------------------------------------------------------------------- tts
    def bench_tts(self):
        print("\n=== TTS (standard tier — OpenAI tts-1 via router) ===")
        samples = [
            ("Hello, welcome to MAARS.", "short"),
            ("The quick brown fox jumps over the lazy dog. " * 5, "medium"),  # ~220 chars
            ("MAARS is a universal AI gateway. " * 30, "long"),  # ~990 chars
        ]
        for text, label in samples:
            t = time.time()
            try:
                r = self.client.post("/api/tts/generate", json={"text": text, "voice": "nova", "tier": "standard"})
                ok = r.status_code == 200
                body = r.json() if ok else {}
                meta = body.get("router", {}) if ok else {"status": r.status_code, "body": r.text[:200]}
                actual_model = meta.get("model", "tts-1")
                actual_cost = meta.get("cost_usd", COST["tts-1"]["usd_per_unit"] * len(text)/1000)
            except Exception as e:
                ok, actual_model = False, "tts-1"
                actual_cost = COST["tts-1"]["usd_per_unit"] * len(text)/1000
                meta = {"err": str(e)[:200]}
            chars = len(text)
            meta["chars"] = chars; meta["label"] = label
            self.record("tts", actual_model, actual_cost, 1, time.time()-t, ok, meta=meta)

    # ----------------------------------------------------------- voice_over
    def bench_voice_over(self):
        print("\n=== Voice-over (premium tier — ElevenLabs via router) ===")
        text = "Welcome to MAARS Command. Your universal AI gateway. " * 3
        t = time.time()
        try:
            r = self.client.post("/api/tts/generate",
                                 json={"text": text, "voice": "rachel", "tier": "premium"})
            ok = r.status_code == 200
            body = r.json() if ok else {}
            meta = body.get("router", {}) if ok else {"status": r.status_code, "body": r.text[:200]}
            actual_model = meta.get("model", "eleven_turbo_v2_5")
            actual_cost = meta.get("cost_usd", 0.18 * len(text)/1000)
        except Exception as e:
            ok, actual_model, actual_cost = False, "eleven_turbo_v2_5", 0.18 * len(text)/1000
            meta = {"err": str(e)[:200]}
        meta["chars"] = len(text)
        self.record("voice_over", actual_model, actual_cost, 1, time.time()-t, ok, meta=meta)

    # ------------------------------------------------------------ vibe gen
    def bench_vibe(self):
        print("\n=== Vibe Coding (full HTML app gen) ===")
        t = time.time()
        try:
            r = self.client.post("/api/vibe/projects",
                                 json={"description": "A simple todo list with add/delete and localStorage"},
                                 timeout=300)
            ok = r.status_code == 200
            body = r.json() if ok else {}
            files = body.get("project", {}).get("files", []) if isinstance(body, dict) else []
            total_chars = sum(len(f.get("content", "")) for f in files) if files else 0
            # Estimate: output tokens ~= chars / 4
            out_tokens = total_chars / 4
            # At gpt-5.2 rate $10/1M output → $0.01 per 1k tokens
            cost_usd = (out_tokens / 1000) * 0.010
        except Exception:
            ok, total_chars, cost_usd = False, 0, 0.02
        wall = time.time() - t
        self.results.append({
            "modality": "vibe_coding",
            "model": "gpt-5.2 (default)",
            "units": total_chars,
            "unit_kind": "html_chars",
            "real_cost_usd": round(cost_usd, 6),
            "real_cost_credits": round(cost_usd * 1000, 3),
            "wall_s": round(wall, 2),
            "ok": ok,
            "meta": {"chars_generated": total_chars, "file_count": len(files) if ok else 0},
        })
        print(f"  [vibe_coding] gpt-5.2                   | {total_chars:,} html_chars | "
              f"${cost_usd:7.4f} = {cost_usd*1000:6.2f} credits | {wall:5.1f}s | {'OK' if ok else 'FAIL'}")

    # -------------------------------------------------------------- content
    def bench_content(self):
        print("\n=== Content gen (social post) ===")
        t = time.time()
        try:
            r = self.client.post("/api/content/generate", json={
                "content_type": "social_post",
                "prompt": "Announcing our new product launch — a universal AI gateway",
                "length": "short",
            })
            ok = r.status_code == 200
            body = r.json() if ok else {}
            content_len = len(body.get("content", "")) if isinstance(body, dict) else 0
            out_tokens = content_len / 4
            cost_usd = (out_tokens / 1000) * 0.010
        except Exception:
            ok, content_len, cost_usd = False, 0, 0.001
        wall = time.time() - t
        self.results.append({
            "modality": "content",
            "model": "gpt-5.2",
            "units": content_len,
            "unit_kind": "chars",
            "real_cost_usd": round(cost_usd, 6),
            "real_cost_credits": round(cost_usd * 1000, 3),
            "wall_s": round(wall, 2),
            "ok": ok,
            "meta": {"chars": content_len},
        })
        print(f"  [content]    gpt-5.2                   | {content_len:,} chars       | "
              f"${cost_usd:7.4f} = {cost_usd*1000:6.2f} credits | {wall:5.1f}s | {'OK' if ok else 'FAIL'}")

    # --------------------------------------------------------------- social
    def bench_social(self):
        """Benchmark social post CREATION. A non-connected platform correctly
        returns HTTP 400 'not connected' — that's the expected shape when the
        caller hasn't OAuth'd with the platform yet. Treat that as OK for
        the benchmark (the endpoint's working; the account just isn't linked)."""
        print("\n=== Social post creation (expects 'not connected' when no OAuth) ===")
        t = time.time()
        try:
            r = self.client.post("/api/social/post", json={
                "platform": "linkedin",
                "content": "Excited to announce MAARS Command — the universal AI gateway.",
                "schedule_at": None,
            }, timeout=30)
            # 200 = posted, 400 with "not connected" = endpoint working, account not linked
            body_text = r.text.lower() if r.text else ""
            ok = r.status_code in (200, 201, 202) or (
                r.status_code == 400 and "not connected" in body_text
            )
        except Exception:
            ok = False
        wall = time.time() - t
        self.results.append({
            "modality": "social_post",
            "model": "queue (no LLM)",
            "units": 1,
            "unit_kind": "post",
            "real_cost_usd": 0.0,
            "real_cost_credits": 0.0,
            "wall_s": round(wall, 2),
            "ok": ok,
            "meta": {"note": "queued, no external cost; caller-supplied content"},
        })
        print(f"  [social]     queue                     | 1 post          | "
              f"$0.0000 =   0.00 credits | {wall:5.1f}s | {'OK' if ok else 'FAIL'}")

    # =========================================================== summarize
    def summarize(self):
        by_modality: dict[str, list] = {}
        for r in self.results:
            by_modality.setdefault(r["modality"], []).append(r)
        summary = {}
        for mod, rows in by_modality.items():
            ok_rows = [r for r in rows if r["ok"]]
            summary[mod] = {
                "calls": len(rows),
                "ok": len(ok_rows),
                "avg_cost_usd": round(sum(r["real_cost_usd"] for r in ok_rows)/max(len(ok_rows),1), 6),
                "avg_cost_credits": round(sum(r["real_cost_credits"] for r in ok_rows)/max(len(ok_rows),1), 3),
                "avg_wall_s": round(sum(r["wall_s"] for r in ok_rows)/max(len(ok_rows),1), 2),
            }
        return summary


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--token", default=os.environ.get("BENCH_JWT", ""))
    ap.add_argument("--skip-video", action="store_true")
    ap.add_argument("--only", help="comma-separated modalities to run (chat,image,video,tts,voice_over,vibe,content,social)")
    args = ap.parse_args()
    if not args.token:
        print("ERROR: pass --token or set BENCH_JWT env", file=sys.stderr)
        sys.exit(2)

    b = Bench(args.token)
    runners = {
        "chat": b.bench_chat,
        "image": b.bench_image,
        "video": b.bench_video,
        "tts": b.bench_tts,
        "voice_over": b.bench_voice_over,
        "vibe": b.bench_vibe,
        "content": b.bench_content,
        "social": b.bench_social,
    }
    order = ["chat", "image", "tts", "voice_over", "content", "social", "vibe", "video"]
    if args.only:
        order = [m.strip() for m in args.only.split(",")]
    if args.skip_video and "video" in order:
        order.remove("video")

    for name in order:
        try:
            runners[name]()
        except Exception as e:
            print(f"  [{name}] FATAL: {type(e).__name__}: {str(e)[:200]}")

    summary = b.summarize()
    report = {
        "results": b.results,
        "summary": summary,
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2))
    print(f"\nReport written to {REPORT_PATH}")
    print("\n=== Summary ===")
    for mod, s in summary.items():
        print(f"  {mod:12s}  calls={s['calls']:2d} ok={s['ok']:2d}  "
              f"avg_cost=${s['avg_cost_usd']:7.4f} ({s['avg_cost_credits']:7.2f} credits)  "
              f"avg_wall={s['avg_wall_s']:6.1f}s")


if __name__ == "__main__":
    main()
