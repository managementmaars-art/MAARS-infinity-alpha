"""Live end-to-end smoke test for the Office SOP runner.

Exercises the full pipeline:
  1. Loads an agent's office from Mongo.
  2. Runs `run_sop()` on a realistic request — not dry_run.
  3. Captures the trace + any tool invocations.
  4. If a Video Creator office is present, runs the 'social_short_15s'
     skill path so research + storyboard + voiceover + composite all
     fire through TOOL_REGISTRY.
  5. If Commander Orion office is present, asks him to `delegate_to_agent`
     so cross-agent delegation is verified end-to-end.

Writes a JSON report to backend/scripts/office_sop_smoke_report.json.
Safe to re-run — all outputs are non-destructive (TTS/image/video
artifacts go to /files/ and are reclaimable).

Usage: `python backend/scripts/office_sop_smoke.py`
"""
from __future__ import annotations
import asyncio
import json
import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).parent.parent.parent
load_dotenv(ROOT / ".env")
sys.path.insert(0, str(Path(__file__).parent.parent))

REPORT_PATH = Path(__file__).parent / "office_sop_smoke_report.json"
TEST_USER_ID = os.environ.get("SMOKE_USER_ID", "smoke_user_maars")


async def _pick_agent(department_hint: str | None = None) -> dict | None:
    from db import db
    q: dict = {}
    if department_hint:
        q["department"] = department_hint
    doc = await db.agent_offices.find_one(q, {"_id": 0})
    return doc


async def _run_and_time(label: str, coro):
    t0 = time.time()
    try:
        out = await coro
        return {"label": label, "ok": True, "ms": int((time.time() - t0) * 1000), "result": out}
    except Exception as exc:
        return {"label": label, "ok": False, "ms": int((time.time() - t0) * 1000),
                "error": f"{type(exc).__name__}: {str(exc)[:400]}"}


async def main() -> None:
    from services.agents.agent_office import get as office_get, run_sop
    from services.workflows.workflow_executor import TOOL_REGISTRY

    # Ensure the smoke user has enough credits for real LLM calls.
    try:
        from services.billing.wallet_service import grant, get_summary
        summary = await get_summary(TEST_USER_ID)
        if (summary.get("balance") or 0) < 200:
            await grant(
                TEST_USER_ID, amount=500,
                reference_type="smoke_test",
                reference_id=f"sop_smoke_{int(time.time())}",
                description="Office SOP smoke test top-up",
            )
    except Exception as exc:
        print(f"[smoke] wallet top-up skipped: {exc}")

    report: dict = {
        "started_at": int(time.time()),
        "user_id":    TEST_USER_ID,
        "tools_registered": sorted(list(TOOL_REGISTRY.keys())),
    }

    # 1. Pick any office in Creative & Marketing for the default SOP test
    creative = await _pick_agent("Creative & Marketing")
    if not creative:
        # Any office will do; tests below verify the pipeline, not dept-specific logic.
        creative = await _pick_agent(None)

    if not creative:
        report["error"] = "no_offices_in_db — run POST /admin/offices/seed first"
        REPORT_PATH.write_text(json.dumps(report, indent=2, default=str))
        print(json.dumps(report, indent=2, default=str))
        return

    office = await office_get(creative["agent_id"])
    report["agent_under_test"] = {
        "agent_id":     office.agent_id,
        "agent_name":   office.agent_name,
        "studio_name":  office.studio_name,
        "department":   office.department,
        "sop_steps":    [s.name for s in office.sop],
        "skill_count":  len(office.skills_library),
        "languages":    office.languages_supported,
    }

    # 2. Run a realistic brief through the agent's SOP (DRY-RUN first so we
    #    verify trace structure without spending credits, then a live run).
    dry = await _run_and_time(
        f"sop_dry_run[{office.agent_id}]",
        run_sop(office, "Write a 400-word blog intro about sustainable packaging.",
                user_id=TEST_USER_ID, dry_run=True),
    )
    report["dry_run"] = dry

    live = await _run_and_time(
        f"sop_live[{office.agent_id}]",
        run_sop(office, "Write a 250-word blog intro about sustainable packaging "
                        "for a premium wellness brand. No filler, specific claims.",
                user_id=TEST_USER_ID),
    )
    report["live_run"] = live

    # 3. Video Creator: if the flagship office is present, run the social-short skill.
    video = await _pick_agent(None)
    video_office = None
    from db import db
    async for doc in db.agent_offices.find(
        {"studio_name": {"$regex": "Video", "$options": "i"}}, {"_id": 0}
    ).limit(1):
        video_office = doc
    if video_office:
        vo = await office_get(video_office["agent_id"])
        vid = await _run_and_time(
            f"video_creator_social_short[{vo.agent_id}]",
            run_sop(vo,
                    "Make a 15-second TikTok short for 'Ember Sleep Tea'. "
                    "Vertical 9:16, voiceover in English, cozy nighttime tone.",
                    user_id=TEST_USER_ID),
        )
        report["video_creator"] = vid

    # 4. Commander Orion delegation chain (if he exists)
    commander = await db.agent_offices.find_one(
        {"agent_id": "agent_commander"}, {"_id": 0}
    )
    if commander and "delegate_to_agent" in TOOL_REGISTRY:
        from services.workflows.workflow_executor import _t_delegate_to_agent
        deleg = await _run_and_time(
            f"delegate_commander_to[{office.agent_id}]",
            _t_delegate_to_agent(
                TEST_USER_ID,
                {"agent_id": office.agent_id,
                 "user_request": "Write a 100-word product hook for sustainable packaging."},
                {},
            ),
        )
        report["delegation_chain"] = deleg

    report["finished_at"] = int(time.time())
    REPORT_PATH.write_text(json.dumps(report, indent=2, default=str))
    # Print a compact summary to stdout
    print(json.dumps({
        "agent_under_test": report["agent_under_test"]["agent_id"],
        "dry_run_ok":       report["dry_run"]["ok"],
        "live_run_ok":      report["live_run"]["ok"],
        "video_ok":         (report.get("video_creator") or {}).get("ok"),
        "delegation_ok":    (report.get("delegation_chain") or {}).get("ok"),
        "report_path":      str(REPORT_PATH),
    }, indent=2, default=str))


if __name__ == "__main__":
    asyncio.run(main())
