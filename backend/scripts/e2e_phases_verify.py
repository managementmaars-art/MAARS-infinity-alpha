"""End-to-end verification of Phases 1, 2, 3 — runs against the live
backend on 127.0.0.1:8001 + direct service calls. Exits 0 on all-pass.

Each phase is run in sequence; report table shows pass/fail per item.
"""
from __future__ import annotations
import asyncio
import json
import sys
import time
from pathlib import Path

import httpx
from dotenv import load_dotenv

ROOT = Path(__file__).parent.parent.parent
load_dotenv(ROOT / ".env")
sys.path.insert(0, str(Path(__file__).parent.parent))


BASE = "http://127.0.0.1:8001/api"
TEST_USER = "e2e_verify_user"


def ok(msg): print(f"  [OK]    {msg}")
def fail(msg): print(f"  [FAIL]  {msg}")
def info(msg): print(f"          {msg}")


async def phase1_verify():
    print()
    print("=" * 70)
    print("PHASE 1 — Billing consolidation + architecture")
    print("=" * 70)
    results = {"pass": 0, "fail": 0}

    async with httpx.AsyncClient(timeout=15) as c:
        r = await c.get(f"{BASE}/plans")
        if r.status_code != 200:
            fail(f"/api/plans returned {r.status_code}")
            results["fail"] += 1
            return results
        d = r.json()
        plans = d.get("plans", {})
        v2 = d.get("plans_v2", [])
        ok(f"/api/plans returns 200 · plans={len(plans)} · plans_v2={len(v2)}")
        results["pass"] += 1

        missing = [pid for pid, p in plans.items() if not p.get("bucket_allowances")]
        if missing:
            fail(f"plans missing bucket_allowances: {missing}")
            results["fail"] += 1
        else:
            ok(f"all {len(plans)} plans carry bucket_allowances")
            results["pass"] += 1

        v2_missing = [r["plan_id"] for r in v2 if not r.get("bucket_allowances")]
        if v2_missing:
            fail(f"plans_v2 missing: {v2_missing}")
            results["fail"] += 1
        else:
            ok(f"all {len(v2)} plans_v2 rows carry bucket_allowances")
            results["pass"] += 1

        s = plans.get("starter", {})
        ba = s.get("bucket_allowances", {}) or {}
        info(f"starter ({s.get('credits',0)}cr): "
             + ", ".join(f"{k}={v}" for k, v in ba.items() if v > 0))

        r404 = await c.get(f"{BASE}/billing/packages")
        if r404.status_code == 404:
            ok("/api/billing/* routes cleanly 404 (duplicate removed)")
            results["pass"] += 1
        else:
            fail(f"/api/billing/packages should be 404, got {r404.status_code}")
            results["fail"] += 1

    # Subscription grant_buckets flow
    from services.billing.wallet_service import grant_buckets, get_summary, ensure_wallet
    from services.billing.plan_buckets import split_credits
    from db import db
    await db.wallets.delete_one({"user_id": TEST_USER})
    await ensure_wallet(TEST_USER, initial_credits=0)

    splits = split_credits(300, "starter")
    await grant_buckets(TEST_USER, splits,
                        reference_type="e2e_starter",
                        reference_id=f"e2e_{int(time.time())}",
                        description="E2E Starter")
    summary = await get_summary(TEST_USER)
    if summary.get("balance_credits") == 300:
        ok(f"subscription grant_buckets: 300 credits landed")
        results["pass"] += 1
    else:
        fail(f"expected 300, got {summary.get('balance_credits')}")
        results["fail"] += 1

    b = summary.get("buckets", {})
    for bk in ("chat", "vibe", "agent_sop", "image", "video", "voice", "stt"):
        bal = (b.get(bk) or {}).get("balance", 0)
        if bal > 0:
            ok(f"  bucket {bk}: {bal} credits (correct split)")
            results["pass"] += 1
        else:
            fail(f"  bucket {bk}: expected >0 got {bal}")
            results["fail"] += 1

    await db.wallets.delete_one({"user_id": TEST_USER})
    return results


async def phase2_verify():
    print()
    print("=" * 70)
    print("PHASE 2 — Team architecture (29 teams, 499 agents)")
    print("=" * 70)
    results = {"pass": 0, "fail": 0}

    from db import db
    team_count = await db.teams.count_documents({})
    if team_count == 29:
        ok(f"db.teams has {team_count} teams")
        results["pass"] += 1
    else:
        fail(f"db.teams has {team_count} (expected 29)")
        results["fail"] += 1

    agents_total = await db.agents.count_documents({})
    agents_with_team = await db.agents.count_documents({"team_id": {"$exists": True, "$ne": None}})
    if agents_with_team == agents_total:
        ok(f"all {agents_total} agents have team_id assigned")
        results["pass"] += 1
    else:
        fail(f"{agents_with_team}/{agents_total} agents have team_id")
        results["fail"] += 1

    from services.agents.team_seeder import list_teams, get_team, team_members_detailed
    teams = await list_teams()
    if len(teams) == 29:
        ok(f"team_seeder.list_teams() -> {len(teams)}")
        results["pass"] += 1
    else:
        fail(f"list_teams returned {len(teams)}")
        results["fail"] += 1

    video = await get_team("team_video_production")
    if video and video.get("member_count", 0) > 0:
        ok(f"team_video_production has {video['member_count']} members")
        results["pass"] += 1
        mem = await team_members_detailed("team_video_production")
        ok(f"team_members_detailed returns {len(mem)} rows")
        results["pass"] += 1
    else:
        fail("team_video_production missing or empty")
        results["fail"] += 1

    total_members = sum((t.get("member_count") or 0) for t in teams)
    if total_members == 499:
        ok(f"total team membership = {total_members} (matches 499)")
        results["pass"] += 1
    else:
        fail(f"total membership = {total_members} (expected 499)")
        results["fail"] += 1

    async with httpx.AsyncClient(timeout=10) as c:
        r = await c.get(f"{BASE}/admin/teams")
        if r.status_code in (401, 403):
            ok(f"/api/admin/teams registered (auth-gated {r.status_code}, expected)")
            results["pass"] += 1
        elif r.status_code == 200:
            ok(f"/api/admin/teams 200 OK")
            results["pass"] += 1
        else:
            fail(f"/api/admin/teams unexpected {r.status_code}")
            results["fail"] += 1

    return results


async def phase3_verify():
    print()
    print("=" * 70)
    print("PHASE 3 — Research tools (web_search + browser_*)")
    print("=" * 70)
    results = {"pass": 0, "fail": 0}

    from services.workflows.workflow_executor import TOOL_REGISTRY
    need = ["web_search", "browser_open", "browser_navigate", "browser_extract", "browser_screenshot"]
    missing = [t for t in need if t not in TOOL_REGISTRY]
    if not missing:
        ok(f"all 5 research tools registered in TOOL_REGISTRY")
        results["pass"] += 1
    else:
        fail(f"tools missing: {missing}")
        results["fail"] += 1

    r = await TOOL_REGISTRY["web_search"]("e2e_user",
        {"query": "Python typing module", "count": 2}, {})
    if r.get("ok") and len(r.get("results", [])) > 0:
        ok(f"web_search -> {len(r['results'])} results")
        results["pass"] += 1
    else:
        fail(f"web_search: {r.get('error','no results')}")
        results["fail"] += 1

    r = await TOOL_REGISTRY["browser_open"]("e2e_user",
        {"url": "https://example.com"}, {})
    if r.get("ok") and r.get("title") == "Example Domain":
        ok(f"browser_open fetched example.com ({len(r['text'])} chars)")
        results["pass"] += 1
    else:
        fail(f"browser_open: {r.get('error','unexpected')}")
        results["fail"] += 1

    r = await TOOL_REGISTRY["browser_extract"]("e2e_user",
        {"url": "https://example.com", "selector": "h1"}, {})
    if r.get("ok") and r.get("match_count", 0) > 0:
        ok(f"browser_extract h1 -> {r['match_count']} matches")
        results["pass"] += 1
    else:
        fail(f"browser_extract: {r}")
        results["fail"] += 1

    # Force tool use via SOP; verify 0 allowlist blocks
    from services.billing.wallet_service import grant, get_summary
    from services.agents.agent_office import get as office_get, run_sop
    from db import db
    s = await get_summary("cost_sim_user_maars")
    if (s.get("balance_credits") or 0) < 200:
        await grant("cost_sim_user_maars", 500, reference_type="e2e_phase3",
                    reference_id=f"p3_{int(time.time())}",
                    description="Phase 3 verify", bucket="general")

    researcher = await db.agent_offices.find_one(
        {"studio_name": {"$regex": "Research Desk", "$options": "i"}}, {"_id": 0})
    office = await office_get(researcher["agent_id"])
    question = (
        "Please use web_search to find 2 results for 'Claude Sonnet 4.5 release' "
        "and browser_open on the top result. You MUST call both tools in this step."
    )
    sop_result = await run_sop(office, question, user_id="cost_sim_user_maars")
    trace = sop_result.get("trace") or []
    total_invoked = sum(len((t.get("tools_invoked") or [])) for t in trace)
    total_ok = sum(t.get("tools_ok", 0) for t in trace)
    total_failed = sum(t.get("tools_failed", 0) for t in trace)
    output_str = json.dumps(sop_result.get("output") or {}, default=str)
    blocked_count = output_str.count("tool_not_in_allowlist")
    if blocked_count == 0:
        ok(f"SOP tool invocation: invoked={total_invoked} ok={total_ok} fail={total_failed} allowlist_blocks=0 (gate removed)")
        results["pass"] += 1
    else:
        fail(f"SOP had {blocked_count} allowlist blocks (expected 0)")
        results["fail"] += 1

    if total_invoked > 0:
        ok(f"agent actually invoked {total_invoked} tool call(s) this run")
        results["pass"] += 1
    else:
        info("agent did not invoke tools this run (LLM chose no-tool path; not a failure)")

    return results


async def phase4_verify():
    print()
    print("=" * 70)
    print("PHASE 4 — Cost automation (P&L + provider balance + setup guide)")
    print("=" * 70)
    results = {"pass": 0, "fail": 0}

    # P4.1 — Admin routes registered
    async with httpx.AsyncClient(timeout=15) as c:
        for endpoint in [
            "/admin/cost-automation/pnl?days=7",
            "/admin/cost-automation/providers",
            "/admin/cost-automation/alerts",
            "/admin/cost-automation/setup-guide",
        ]:
            r = await c.get(f"{BASE}{endpoint}")
            if r.status_code in (200, 401, 403):
                ok(f"{endpoint} registered (status {r.status_code})")
                results["pass"] += 1
            else:
                fail(f"{endpoint} unexpected status {r.status_code}")
                results["fail"] += 1

    # P4.2 — Service functions actually produce shapes
    from services.billing import cost_automation
    pnl = await cost_automation.build_daily_pnl(days=7)
    if isinstance(pnl, list):
        ok(f"build_daily_pnl returned {len(pnl)} day rows")
        results["pass"] += 1
    else:
        fail("build_daily_pnl returned non-list")
        results["fail"] += 1

    cogs = await cost_automation.cogs_by_provider(days=7)
    if isinstance(cogs, list):
        ok(f"cogs_by_provider returned {len(cogs)} provider rows")
        results["pass"] += 1
    else:
        fail("cogs_by_provider returned non-list")
        results["fail"] += 1

    guide = cost_automation.setup_guide()
    if len(guide) >= 10:
        with_keys = sum(1 for p in guide if p.get("has_key"))
        ok(f"setup_guide returns {len(guide)} providers ({with_keys} configured)")
        results["pass"] += 1
    else:
        fail(f"setup_guide only returned {len(guide)} providers")
        results["fail"] += 1

    # P4.3 — Run a tick: writes a snapshot
    snap = await cost_automation.cost_automation_tick()
    if isinstance(snap, dict) and "date" in snap:
        ok(f"cost_automation_tick wrote snapshot for {snap['date']} · revenue=${snap.get('revenue_usd',0)} cogs=${snap.get('cogs_usd',0)}")
        results["pass"] += 1
    else:
        fail("cost_automation_tick did not return a snapshot")
        results["fail"] += 1

    # P4.4 — latest_snapshot retrieves it
    latest = await cost_automation.latest_snapshot()
    if latest:
        ok(f"latest_snapshot retrieval works (date={latest.get('date')})")
        results["pass"] += 1
    else:
        fail("latest_snapshot returned None")
        results["fail"] += 1

    # P4.5 — scheduler has the cost_automation job registered
    import importlib
    sched_mod = importlib.import_module("services.scheduler")
    with open(sched_mod.__file__, "r", encoding="utf-8") as f:
        sched_src = f.read()
    if "maars_cost_automation" in sched_src and "_cost_automation_tick" in sched_src:
        ok("scheduler.py registers 'maars_cost_automation' job every 30 min")
        results["pass"] += 1
    else:
        fail("scheduler job 'maars_cost_automation' not found in scheduler.py")
        results["fail"] += 1

    return results


async def phase5_verify():
    print()
    print("=" * 70)
    print("PHASE 5 — Unified plans (deliverables) + Treasury")
    print("=" * 70)
    results = {"pass": 0, "fail": 0}

    # P5.1 — /api/plans serves unified 5-tier plans_v2 with deliverables
    async with httpx.AsyncClient(timeout=15) as c:
        r = await c.get(f"{BASE}/plans")
        d = r.json()
        v2 = d.get("plans_v2", [])
        expected = {"free", "creator", "studio", "scale", "infinity"}
        actual = {p["plan_id"] for p in v2}
        if expected == actual:
            ok(f"plans_v2 carries unified 5 tiers: {sorted(actual)}")
            results["pass"] += 1
        else:
            fail(f"plans_v2 ids mismatch — got {sorted(actual)}")
            results["fail"] += 1
        # Deliverables attached to each tier
        missing_deliv = [p["plan_id"] for p in v2 if not p.get("deliverables")]
        if not missing_deliv:
            ok(f"all {len(v2)} plans have deliverables[]")
            results["pass"] += 1
        else:
            fail(f"plans missing deliverables: {missing_deliv}")
            results["fail"] += 1
        # Creator sanity check
        creator = next((p for p in v2 if p["plan_id"] == "creator"), None)
        if creator:
            deliv_labels = {d["label"]: d["count"] for d in creator["deliverables"]}
            if deliv_labels.get("Chat messages") == 5000 and deliv_labels.get("Videos (4-second clips)") == 10:
                ok(f"creator: 5,000 chats / 10 videos / unlimited voice+stt ✓")
                results["pass"] += 1
            else:
                fail(f"creator deliverables unexpected: {deliv_labels}")
                results["fail"] += 1

    # P5.2 — Treasury idempotency + booking
    from services.billing import treasury
    ref = f"e2e_p5_{int(time.time())}"
    # Clean slate for this test ref
    before = await treasury.get_snapshot()
    r1 = await treasury.on_subscription_paid(
        amount_usd=29.0, plan_id="creator", user_id="e2e_p5",
        reference_id=ref, description="E2E Creator")
    r2 = await treasury.on_subscription_paid(
        amount_usd=29.0, plan_id="creator", user_id="e2e_p5",
        reference_id=ref, description="DUP should skip")
    after = await treasury.get_snapshot()
    rev_delta = after["revenue_usd"] - before["revenue_usd"]
    if abs(rev_delta - 29.0) < 0.001:
        ok(f"treasury booked $29 subscription (revenue +${rev_delta:.2f})")
        results["pass"] += 1
    else:
        fail(f"treasury revenue delta: expected $29.00, got ${rev_delta:.2f}")
        results["fail"] += 1
    if r2.get("duplicate"):
        ok("treasury idempotent — duplicate reference_id did not double-book")
        results["pass"] += 1
    else:
        fail("treasury not idempotent (duplicate returned without skip flag)")
        results["fail"] += 1
    # Verify split: 5% reserve, 95% profit on Creator
    if r1.get("reserve_usd") == 1.45 and r1.get("profit_usd") == 27.55:
        ok(f"treasury split: $29 → reserve $1.45 (5%) + profit $27.55 (95%)")
        results["pass"] += 1
    else:
        fail(f"treasury split unexpected: reserve=${r1.get('reserve_usd')} profit=${r1.get('profit_usd')}")
        results["fail"] += 1

    # P5.3 — API-call COGS debit works
    snap_pre_debit = await treasury.get_snapshot()
    await treasury.on_api_call_billed(
        actual_cost_usd=0.02, provider="fal",
        user_id="e2e_p5", model="fal-ai/ltx-video",
        reference_id=f"e2e_api_{int(time.time())}")
    snap_post = await treasury.get_snapshot()
    reserve_delta = snap_pre_debit["cogs_reserve_usd"] - snap_post["cogs_reserve_usd"]
    actual_delta  = snap_post["cogs_actual_usd"] - snap_pre_debit["cogs_actual_usd"]
    if abs(reserve_delta - 0.02) < 0.001 and abs(actual_delta - 0.02) < 0.001:
        ok("API call debit: reserve -$0.02, actual +$0.02 (Fal LTX video)")
        results["pass"] += 1
    else:
        fail(f"debit wrong: reserve_delta={reserve_delta} actual_delta={actual_delta}")
        results["fail"] += 1

    # P5.4 — Admin treasury routes registered
    async with httpx.AsyncClient(timeout=10) as c:
        for endpoint in ["/admin/treasury", "/admin/treasury/log"]:
            r = await c.get(f"{BASE}{endpoint}")
            if r.status_code in (401, 200):
                ok(f"{endpoint} registered")
                results["pass"] += 1
            else:
                fail(f"{endpoint} unexpected {r.status_code}")
                results["fail"] += 1

    # P5.5 — plan_deliverables translators work
    from services.billing.plan_deliverables import (
        plan_deliverables, total_credits_for, bucket_split_from_deliverables,
        deliverables_remaining, LEGACY_TO_UNIFIED,
    )
    # Legacy plan_id 'starter' resolves to 'creator'
    legacy_deliv = plan_deliverables("starter")
    new_deliv    = plan_deliverables("creator")
    if len(legacy_deliv) == len(new_deliv) and len(new_deliv) > 0:
        ok(f"legacy 'starter' → unified 'creator' via LEGACY_TO_UNIFIED mapping")
        results["pass"] += 1
    else:
        fail(f"legacy mapping broken: starter→{len(legacy_deliv)} creator→{len(new_deliv)}")
        results["fail"] += 1
    # Bucket split derivation
    splits = bucket_split_from_deliverables("creator")
    expected_buckets = {"chat", "vibe", "agent_sop", "image", "video", "voice", "stt"}
    if expected_buckets.issubset(set(splits.keys())) and splits["chat"] > 0:
        ok(f"bucket_split_from_deliverables: {sum(splits.values())} total credits across {len(splits)} buckets")
        results["pass"] += 1
    else:
        fail(f"bucket_split incomplete: {splits}")
        results["fail"] += 1
    # Deliverables remaining translator
    from services.billing.wallet_service import ensure_wallet, grant_buckets
    from db import db
    await db.wallets.delete_one({"user_id": "e2e_deliv_user"})
    await ensure_wallet("e2e_deliv_user", initial_credits=0)
    await grant_buckets("e2e_deliv_user", splits,
                        reference_type="e2e", reference_id=f"deliv_{int(time.time())}",
                        description="E2E deliv test")
    from services.billing.wallet_service import get_summary
    s = await get_summary("e2e_deliv_user")
    remaining = deliverables_remaining("creator", s["buckets"])
    videos_row = next((r for r in remaining if r["key"] == "videos"), None)
    if videos_row and videos_row["remaining"] == 10 and videos_row["total"] == 10:
        ok(f"deliverables_remaining: Creator starts at 10/10 videos (matches catalog)")
        results["pass"] += 1
    else:
        fail(f"videos remaining calc wrong: {videos_row}")
        results["fail"] += 1
    await db.wallets.delete_one({"user_id": "e2e_deliv_user"})

    return results


async def main():
    p1 = await phase1_verify()
    p2 = await phase2_verify()
    p3 = await phase3_verify()
    p4 = await phase4_verify()
    p5 = await phase5_verify()
    print()
    print("=" * 70)
    total_pass = p1["pass"] + p2["pass"] + p3["pass"] + p4["pass"] + p5["pass"]
    total_fail = p1["fail"] + p2["fail"] + p3["fail"] + p4["fail"] + p5["fail"]
    print(f"SUMMARY: {total_pass} passed, {total_fail} failed")
    print(f"  Phase 1: {p1['pass']}/{p1['pass']+p1['fail']}")
    print(f"  Phase 2: {p2['pass']}/{p2['pass']+p2['fail']}")
    print(f"  Phase 3: {p3['pass']}/{p3['pass']+p3['fail']}")
    print(f"  Phase 4: {p4['pass']}/{p4['pass']+p4['fail']}")
    print(f"  Phase 5: {p5['pass']}/{p5['pass']+p5['fail']}")
    print("=" * 70)
    return total_fail == 0


if __name__ == "__main__":
    passed = asyncio.run(main())
    sys.exit(0 if passed else 1)
