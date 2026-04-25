"""Phase 6 end-to-end verification — the unified token-quota model.

Exercises the full happy-path + hard-cap rejection:
  1. Grant a Creator-sized quota (50 credits = 5M tokens)
  2. Reserve 1M tokens — should succeed
  3. Settle 500k actual (half the reserve) — remaining = 4.5M
  4. Reserve 4M tokens — should succeed (total used+reserved = 4.5M)
  5. Reserve another 1M tokens — should FAIL (would exceed 5M cap)
  6. Refund the 4M — remaining = 4.5M
  7. Media call: convert $0.02 cost to equivalent tokens and debit
  8. Renewal: reset_period → tokens_used zeroes, new period_end

All in one script, no dependencies on gateway/Stripe; purely exercises
token_quota.py so we know the core is sound before relying on it.
"""
from __future__ import annotations
import asyncio
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).parent.parent.parent
load_dotenv(ROOT / ".env")
sys.path.insert(0, str(Path(__file__).parent.parent))


def ok(msg): print(f"  [OK]    {msg}")
def fail(msg): print(f"  [FAIL]  {msg}")
def info(msg): print(f"          {msg}")


async def main():
    from services.billing import token_quota
    from db import db

    uid = f"p6_user_{int(time.time())}"
    print()
    print("=" * 70)
    print("PHASE 6 — Token Quota Unified Model")
    print("=" * 70)
    results = {"pass": 0, "fail": 0}

    # Clean slate
    await db.token_quotas.delete_one({"user_id": uid})
    await db.token_quota_ledger.delete_many({"user_id": uid})

    # (1) Grant Creator quota: 50 credits × 100k = 5,000,000 tokens
    creator_credits = 50
    tokens_granted = token_quota.credits_to_tokens(creator_credits)
    assert tokens_granted == 5_000_000, tokens_granted
    r = await token_quota.grant_tokens(
        uid, tokens_granted,
        reference_id=f"seed_{uid}",
        description="Test Creator grant",
        plan_id="creator",
        reset_period=True,
    )
    if r["tokens_quota"] == 5_000_000 and r["credits_quota"] == 50.0:
        ok(f"grant: 50 credits → 5,000,000 tokens (quota={r['tokens_quota']:,}, credits={r['credits_quota']})")
        results["pass"] += 1
    else:
        fail(f"grant off: {r}")
        results["fail"] += 1

    # (2) Reserve 1M tokens
    r = await token_quota.reserve_tokens(uid, 1_000_000, reference_id="call_1")
    if r and r["tokens_reserved"] == 1_000_000 and r["tokens_remaining"] == 4_000_000:
        ok(f"reserve 1M: reserved={r['tokens_reserved']:,}, remaining={r['tokens_remaining']:,}")
        results["pass"] += 1
    else:
        fail(f"reserve 1M returned: {r}")
        results["fail"] += 1

    # (3) Settle with 500k actual
    r = await token_quota.settle_tokens(
        uid, reserved_tokens=1_000_000, actual_tokens=500_000,
        reference_id="call_1", source="chat", provider="groq", model="llama",
        cost_usd=0.0001,
    )
    if r["tokens_used"] == 500_000 and r["tokens_reserved"] == 0 and r["tokens_remaining"] == 4_500_000:
        ok(f"settle 500k actual: used={r['tokens_used']:,}, reserved=0, remaining={r['tokens_remaining']:,}")
        results["pass"] += 1
    else:
        fail(f"settle state off: {r}")
        results["fail"] += 1

    # (4) Reserve 4M — total used+reserved = 4.5M, within 5M
    r = await token_quota.reserve_tokens(uid, 4_000_000, reference_id="call_2")
    if r and r["tokens_reserved"] == 4_000_000 and r["tokens_remaining"] == 500_000:
        ok(f"reserve 4M: tight, remaining={r['tokens_remaining']:,}")
        results["pass"] += 1
    else:
        fail(f"reserve 4M failed unexpectedly: {r}")
        results["fail"] += 1

    # (5) Try to reserve 1M more — should be REJECTED (would exceed 5M)
    r = await token_quota.reserve_tokens(uid, 1_000_000, reference_id="call_3")
    if r is None:
        ok(f"HARD CAP: over-reserve of 1M rejected (would exceed 5M)")
        results["pass"] += 1
    else:
        fail(f"over-reserve should have failed, got: {r}")
        results["fail"] += 1

    # (6) Refund the 4M reservation → remaining back to 4.5M
    r = await token_quota.refund_tokens(uid, reserved_tokens=4_000_000, reference_id="call_2")
    if r["tokens_reserved"] == 0 and r["tokens_remaining"] == 4_500_000:
        ok(f"refund 4M: back to remaining={r['tokens_remaining']:,}")
        results["pass"] += 1
    else:
        fail(f"refund state off: {r}")
        results["fail"] += 1

    # (7) Media call: $0.02 → equivalent tokens → settle
    video_cost_usd = 0.02
    equiv_tokens = token_quota.cost_usd_to_tokens(video_cost_usd)
    info(f"media ($0.02 Fal video) → {equiv_tokens:,} equivalent tokens")
    r = await token_quota.settle_tokens(
        uid, reserved_tokens=equiv_tokens, actual_tokens=equiv_tokens,
        reference_id="video_1", source="media_video",
        provider="fal", model="fal-ai/ltx-video", cost_usd=video_cost_usd,
    )
    # Used should now be 500k + 400k = 900k
    expected_used = 500_000 + equiv_tokens
    if r["tokens_used"] == expected_used:
        ok(f"media debit: used={r['tokens_used']:,} (chat 500k + video {equiv_tokens:,})")
        results["pass"] += 1
    else:
        fail(f"media debit off: used={r['tokens_used']}, expected={expected_used}")
        results["fail"] += 1

    # (8) Renewal: reset period → used goes to 0
    r = await token_quota.grant_tokens(
        uid, tokens_granted,
        reference_id=f"renewal_{uid}",
        description="Monthly renewal",
        plan_id="creator",
        reset_period=True,
    )
    if r["tokens_used"] == 0 and r["tokens_quota"] == 5_000_000 and r["tokens_remaining"] == 5_000_000:
        ok(f"renewal: used reset, fresh 5M quota, total_calls={r['total_calls']}")
        results["pass"] += 1
    else:
        fail(f"renewal state off: {r}")
        results["fail"] += 1

    # (9) Idempotency: grant same reference_id twice
    r1 = await token_quota.grant_tokens(
        uid, 100_000, reference_id="idem_test", description="first",
    )
    r2 = await token_quota.grant_tokens(
        uid, 100_000, reference_id="idem_test", description="dup",
    )
    if r1["tokens_quota"] == r2["tokens_quota"]:
        ok(f"idempotent: duplicate grant didn't double-book ({r2['tokens_quota']:,} tokens)")
        results["pass"] += 1
    else:
        fail(f"idempotency broken: first={r1['tokens_quota']} dup={r2['tokens_quota']}")
        results["fail"] += 1

    # (10) Cross-client isolation: create second user and ensure they don't share pool
    uid2 = f"p6_user_B_{int(time.time())}"
    await db.token_quotas.delete_one({"user_id": uid2})
    await token_quota.grant_tokens(
        uid2, 100_000, reference_id=f"seed_{uid2}", plan_id="free", reset_period=True,
    )
    # Burn all of user A's quota
    a = await token_quota.get_quota(uid)
    await token_quota.settle_tokens(
        uid, reserved_tokens=0, actual_tokens=a["tokens_remaining"],
        reference_id="burn_A",
    )
    # User B should still have their pool
    b = await token_quota.get_quota(uid2)
    if b["tokens_remaining"] == 100_000:
        ok(f"isolation: user A burned their pool, user B still has {b['tokens_remaining']:,}")
        results["pass"] += 1
    else:
        fail(f"cross-client leakage: user B pool unexpectedly at {b['tokens_remaining']}")
        results["fail"] += 1

    # Cleanup
    await db.token_quotas.delete_many({"user_id": {"$in": [uid, uid2]}})
    await db.token_quota_ledger.delete_many({"user_id": {"$in": [uid, uid2]}})

    print()
    print("=" * 70)
    print(f"SUMMARY: {results['pass']} passed, {results['fail']} failed")
    print("=" * 70)
    return results["fail"] == 0


if __name__ == "__main__":
    passed = asyncio.run(main())
    sys.exit(0 if passed else 1)
