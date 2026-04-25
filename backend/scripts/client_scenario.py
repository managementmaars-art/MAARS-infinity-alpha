"""Realistic client scenario — a small marketing agency launching a product.

What this simulates:
 1. Chat with Copywriter agent → draft product announcement (via /api/chats)
 2. Chat with Social Media Manager → platform variants
 3. Chat with Graphic Designer → describe logo brief
 4. Chat with Video Content Specialist → storyboard a short clip
 5. Chat with Web Designer → landing page structure
 6. Content-gen endpoint → 1 short blog post draft
 7. Image gen x 3 (logo, hero, product shot)
 8. Video gen — 4-sec Sora clip
 9. TTS x 2 (short welcome + 30-sec ad VO)
10. Vibe coding — build a simple one-pager

Every chat routes through the MAARS smart router (all 499 agents are now auto).
Every image/video/TTS routes through the media router + wallet billing.

Records wallet ledger delta per step so we can compute a REAL blended cost
for a realistic SMB workflow — not just raw per-call.
"""
from __future__ import annotations
import argparse, asyncio, io, json, os, sys, time, wave, struct
from pathlib import Path
from typing import Any

import httpx
from dotenv import load_dotenv

ROOT = Path(__file__).parent.parent.parent
load_dotenv(ROOT / ".env")

BASE = os.environ.get("BENCH_BASE", "http://localhost:8000")
ADMIN_USER = "user_36301191e2cb"
REPORT_PATH = Path(__file__).parent / "client_scenario_report.json"


def mint_token() -> str:
    """Mint a short-lived JWT for the admin benchmark user."""
    import jwt
    from datetime import datetime, timezone, timedelta
    return jwt.encode({
        "user_id": ADMIN_USER,
        "email": "management.maars@marsgc.net",
        "exp": datetime.now(timezone.utc) + timedelta(hours=1),
    }, os.environ["JWT_SECRET"], algorithm="HS256")


async def get_wallet(db) -> dict:
    """Snapshot wallet balance + reserved credits."""
    w = await db.wallets.find_one({"user_id": ADMIN_USER}, {"_id": 0, "balance_credits": 1, "reserved_credits": 1})
    return w or {"balance_credits": 0, "reserved_credits": 0}


async def pick_agent(db, role_substring: str) -> dict | None:
    """Find the first agent whose role contains the substring."""
    a = await db.agents.find_one(
        {"role": {"$regex": role_substring, "$options": "i"}},
        {"_id": 0, "agent_id": 1, "name": 1, "role": 1, "model_provider": 1, "model_name": 1},
    )
    return a


class Scenario:
    def __init__(self, token: str):
        self.token = token
        self.client = httpx.AsyncClient(
            base_url=BASE,
            headers={"Authorization": f"Bearer {token}"},
            timeout=600.0,
        )
        self.results: list[dict] = []

    async def _record(self, step: str, detail: dict, credits_used: int, ok: bool, wall_s: float):
        self.results.append({
            "step": step, "detail": detail, "credits_used": credits_used,
            "ok": ok, "wall_s": round(wall_s, 2),
        })
        status = "OK  " if ok else "FAIL"
        print(f"  [{status}] {step:40s} {credits_used:>5} credits  {wall_s:6.1f}s  {json.dumps(detail)[:120]}")

    # ------------------------------------------------------------ chat-with-agent
    async def chat_with_agent(self, db, role_substring: str, message: str) -> tuple[bool, dict, int, float]:
        t0 = time.time()
        agent = await pick_agent(db, role_substring)
        if not agent:
            return False, {"error": f"no agent for '{role_substring}'"}, 0, 0.0
        agent_id = agent["agent_id"]

        # Create a chat with this agent
        cr = await self.client.post("/api/chats", json={"agent_id": agent_id, "title": f"scenario_{role_substring}"})
        if cr.status_code != 200:
            return False, {"error": f"chat create {cr.status_code}: {cr.text[:200]}"}, 0, time.time() - t0
        chat = cr.json()
        chat_id = chat.get("chat_id")

        wallet_before = await get_wallet(db)

        mr = await self.client.post(f"/api/chats/{chat_id}/messages", json={
            "content": message,
            "model_provider": "auto",  # explicit — force router
        }, timeout=120)

        wall = time.time() - t0
        if mr.status_code != 200:
            return False, {"error": f"send_message {mr.status_code}: {mr.text[:200]}"}, 0, wall

        body = mr.json()
        model_used = body.get("model_used") or body.get("assistant_message", {}).get("model_used") or "?"
        wallet_after = await get_wallet(db)
        credits_used = (wallet_before["balance_credits"] - wallet_after["balance_credits"])

        return True, {
            "agent": agent["name"],
            "role": agent.get("role", ""),
            "model": model_used,
            "response_preview": (body.get("assistant_message", {}).get("content", "") or "")[:160],
        }, credits_used, wall

    # ------------------------------------------------------------ direct-modality helpers
    async def gen_image(self, db, prompt: str, quality: str = "standard") -> tuple[bool, dict, int, float]:
        t0 = time.time()
        wallet_before = await get_wallet(db)
        r = await self.client.post("/api/generate/image", json={"prompt": prompt, "quality": quality}, timeout=180)
        wall = time.time() - t0
        if r.status_code != 200:
            return False, {"error": f"{r.status_code}: {r.text[:200]}"}, 0, wall
        body = r.json()
        wallet_after = await get_wallet(db)
        credits_used = wallet_before["balance_credits"] - wallet_after["balance_credits"]
        return True, {
            "router": body.get("router", {}),
            "billing": body.get("billing", {}),
            "filename": body.get("filename"),
        }, credits_used, wall

    async def gen_video(self, db, prompt: str, duration: int = 4) -> tuple[bool, dict, int, float]:
        t0 = time.time()
        wallet_before = await get_wallet(db)
        r = await self.client.post("/api/generate/video", json={"prompt": prompt, "duration": duration}, timeout=900)
        wall = time.time() - t0
        if r.status_code != 200:
            return False, {"error": f"{r.status_code}: {r.text[:300]}"}, 0, wall
        body = r.json()
        wallet_after = await get_wallet(db)
        credits_used = wallet_before["balance_credits"] - wallet_after["balance_credits"]
        return True, {
            "router": body.get("router", {}),
            "billing": body.get("billing", {}),
            "filename": body.get("filename"),
        }, credits_used, wall

    async def gen_tts(self, db, text: str, voice: str = "nova", tier: str = "standard") -> tuple[bool, dict, int, float]:
        t0 = time.time()
        wallet_before = await get_wallet(db)
        r = await self.client.post("/api/tts/generate", json={"text": text, "voice": voice, "tier": tier}, timeout=60)
        wall = time.time() - t0
        if r.status_code != 200:
            return False, {"error": f"{r.status_code}: {r.text[:200]}"}, 0, wall
        body = r.json()
        wallet_after = await get_wallet(db)
        credits_used = wallet_before["balance_credits"] - wallet_after["balance_credits"]
        return True, {
            "router": body.get("router", {}),
            "billing": body.get("billing", {}),
            "chars": len(text),
        }, credits_used, wall

    async def gen_stt(self, db, audio_bytes: bytes) -> tuple[bool, dict, int, float]:
        t0 = time.time()
        wallet_before = await get_wallet(db)
        files = {"audio_file": ("clip.wav", audio_bytes, "audio/wav")}
        headers = {"Authorization": f"Bearer {self.token}"}
        async with httpx.AsyncClient(timeout=120) as c:
            r = await c.post(f"{BASE}/api/audio/speech-to-text", files=files, headers=headers)
        wall = time.time() - t0
        if r.status_code != 200:
            return False, {"error": f"{r.status_code}: {r.text[:200]}"}, 0, wall
        body = r.json()
        wallet_after = await get_wallet(db)
        credits_used = wallet_before["balance_credits"] - wallet_after["balance_credits"]
        return True, {
            "router": body.get("router", {}),
            "billing": body.get("billing", {}),
            "text_preview": (body.get("text") or "")[:120],
        }, credits_used, wall

    async def gen_content(self, db, prompt: str, content_type: str = "social_post") -> tuple[bool, dict, int, float]:
        t0 = time.time()
        wallet_before = await get_wallet(db)
        r = await self.client.post("/api/content/generate",
                                   json={"prompt": prompt, "content_type": content_type, "length": "short"},
                                   timeout=120)
        wall = time.time() - t0
        if r.status_code != 200:
            return False, {"error": f"{r.status_code}: {r.text[:200]}"}, 0, wall
        body = r.json()
        wallet_after = await get_wallet(db)
        credits_used = wallet_before["balance_credits"] - wallet_after["balance_credits"]
        return True, {"chars": len(body.get("content", "") or ""),
                      "preview": (body.get("content", "") or "")[:160]}, credits_used, wall

    async def gen_vibe(self, db, description: str) -> tuple[bool, dict, int, float]:
        t0 = time.time()
        wallet_before = await get_wallet(db)
        r = await self.client.post("/api/vibe/projects", json={"description": description}, timeout=180)
        wall = time.time() - t0
        if r.status_code != 200:
            return False, {"error": f"{r.status_code}: {r.text[:200]}"}, 0, wall
        body = r.json()
        files = body.get("files", [])
        total_chars = sum(len(f.get("content", "")) for f in files) if files else 0
        wallet_after = await get_wallet(db)
        credits_used = wallet_before["balance_credits"] - wallet_after["balance_credits"]
        return True, {"vibe_id": body.get("vibe_id"), "files": len(files),
                      "total_chars": total_chars, "status": body.get("status")}, credits_used, wall

    # ======================================================================= run
    async def run(self, db):
        print("=" * 80)
        print("REALISTIC CLIENT SCENARIO — small marketing agency launching a product")
        print("=" * 80)

        wallet_start = await get_wallet(db)
        print(f"Wallet at start: {wallet_start['balance_credits']} credits\n")

        steps = []

        # 1. Copywriter — draft product launch
        ok, d, cu, ws = await self.chat_with_agent(
            db, "copywriter",
            "Draft a 100-word product launch announcement for a new cold-brew coffee called 'Nord'. Tone: bold and minimalist.",
        )
        await self._record("1. Copywriter → product launch", d, cu, ok, ws)

        # 2. Social Media Manager — platform variants
        ok, d, cu, ws = await self.chat_with_agent(
            db, "social.*media",
            "Turn the Nord cold brew launch into 4 platform variants: LinkedIn post (professional), Instagram caption (lifestyle), X/Twitter (punchy), TikTok hook (15-sec voice-over script).",
        )
        await self._record("2. Social Manager → 4 platform variants", d, cu, ok, ws)

        # 3. Graphic Designer — logo brief
        ok, d, cu, ws = await self.chat_with_agent(
            db, "designer",
            "Write a 3-line logo brief for 'Nord' cold brew. Style: Scandinavian minimalism. Include palette, typography, and mood.",
        )
        await self._record("3. Graphic Designer → logo brief", d, cu, ok, ws)

        # 4. Video Content Specialist — storyboard
        ok, d, cu, ws = await self.chat_with_agent(
            db, "video",
            "Storyboard a 4-second Sora video for Nord cold brew: opening shot, product reveal, closing tagline.",
        )
        await self._record("4. Video Specialist → 4-sec storyboard", d, cu, ok, ws)

        # 5. Web Designer — landing page spec
        ok, d, cu, ws = await self.chat_with_agent(
            db, "web",
            "Spec a single-page Nord coffee landing: hero, 3-feature grid, testimonial, signup. Keep it under 150 words.",
        )
        await self._record("5. Web Designer → landing page spec", d, cu, ok, ws)

        # 6. Content gen — blog post draft
        ok, d, cu, ws = await self.gen_content(
            db, "Short blog post announcing Nord cold brew — the Scandinavian cold-brew experience.", "blog_article",
        )
        await self._record("6. Content Gen → blog post", d, cu, ok, ws)

        # 7-9. Three images: logo, hero, product shot
        for i, (label, quality, prompt) in enumerate([
            ("logo", "standard", "Minimalist Scandinavian wordmark logo 'NORD', ice-blue on white, clean sans-serif typography, flat design"),
            ("hero", "standard", "A cinematic hero shot of a frosted cold brew bottle labeled NORD on birch wood, soft north-light, minimal composition"),
            ("product", "standard", "Product photography: NORD cold brew bottle isolated on white background, studio lighting, 4K"),
        ]):
            ok, d, cu, ws = await self.gen_image(db, prompt, quality=quality)
            await self._record(f"7+{i}. Image gen → {label}", d, cu, ok, ws)

        # 10. Video — 4-sec clip
        ok, d, cu, ws = await self.gen_video(
            db, "A frosted NORD cold brew bottle on birch wood, slow dolly-in, soft northern light", duration=4,
        )
        await self._record("10. Video gen → 4-sec Sora clip", d, cu, ok, ws)

        # 11-12. TTS: short welcome + 30-sec ad VO
        ok, d, cu, ws = await self.gen_tts(db, "Welcome to Nord. Cold brew, Scandinavian style.", voice="nova", tier="standard")
        await self._record("11. TTS standard → welcome", d, cu, ok, ws)

        ok, d, cu, ws = await self.gen_tts(
            db,
            "Nord cold brew is crafted slow, served cold, and designed bold. "
            "Every bottle holds twelve hours of patient steeping, producing a smooth, "
            "low-acidity coffee with notes of cocoa and citrus. Pure Scandinavian simplicity. "
            "Nord: cold brew, quietly perfected.",
            voice="rachel", tier="premium",
        )
        await self._record("12. TTS premium → 30-sec ad VO", d, cu, ok, ws)

        # 13. Vibe coding — landing page
        ok, d, cu, ws = await self.gen_vibe(
            db, "A single-page landing for 'Nord' cold brew: hero with bottle image placeholder, 3 feature tiles (slow-steeped, low-acid, minimal design), testimonial, email signup form, Scandinavian minimalist style with ice-blue accent.",
        )
        await self._record("13. Vibe coding → landing page", d, cu, ok, ws)

        wallet_end = await get_wallet(db)
        total_credits = wallet_start["balance_credits"] - wallet_end["balance_credits"]

        # ======================================== summary
        print("\n" + "=" * 80)
        print(f"SCENARIO COMPLETE")
        print("=" * 80)
        print(f"Wallet start:     {wallet_start['balance_credits']}")
        print(f"Wallet end:       {wallet_end['balance_credits']}")
        print(f"TOTAL credits:    {total_credits}  (=${total_credits * 0.001:.4f} USD)")
        print(f"Successful steps: {sum(1 for r in self.results if r['ok'])}/{len(self.results)}")
        print()

        # Breakdown by modality
        by_modality = {
            "chat": sum(r["credits_used"] for r in self.results if r["step"].split(".")[1].strip().split()[0] in ("Copywriter","Social","Graphic","Video","Web")),
            "content_gen": sum(r["credits_used"] for r in self.results if "Content" in r["step"]),
            "image_gen": sum(r["credits_used"] for r in self.results if "Image" in r["step"]),
            "video_gen": sum(r["credits_used"] for r in self.results if "Video gen" in r["step"]),
            "tts": sum(r["credits_used"] for r in self.results if "TTS" in r["step"]),
            "vibe_coding": sum(r["credits_used"] for r in self.results if "Vibe" in r["step"]),
        }
        print("Credits by modality:")
        for m, c in by_modality.items():
            pct = (c / total_credits * 100) if total_credits else 0
            print(f"  {m:14s}  {c:>5}  ({pct:>4.1f}%)")

        report = {
            "wallet_start": wallet_start,
            "wallet_end": wallet_end,
            "total_credits": total_credits,
            "total_usd": round(total_credits * 0.001, 6),
            "by_modality": by_modality,
            "steps": self.results,
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        }
        REPORT_PATH.write_text(json.dumps(report, indent=2, default=str))
        print(f"\nReport: {REPORT_PATH}")

        await self.client.aclose()


async def main():
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from db import db as mongo_db

    token = mint_token()
    s = Scenario(token)
    await s.run(mongo_db)


if __name__ == "__main__":
    asyncio.run(main())
