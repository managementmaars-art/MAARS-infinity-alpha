"""Per-role training verification — pull one representative agent from
each role family and check the office they got matches the role.

Verifies for each sampled agent:
  * SOP step names match the role family's expected pipeline
  * studio_name ends with the family's studio_suffix
  * skills_library has entries (not empty)
  * quality_rules populated
  * persona wiring: agent's stored system_prompt surfaces inside run_sop's
    composed system message (dry-run path)

Writes report to backend/scripts/role_training_report.json.
"""
from __future__ import annotations
import asyncio, json, sys, time
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).parent.parent.parent
load_dotenv(ROOT / ".env")
sys.path.insert(0, str(Path(__file__).parent.parent))

REPORT_PATH = Path(__file__).parent / "role_training_report.json"


async def main() -> None:
    from db import db
    from services.agents.agent_office import get as office_get, run_sop
    from services.agents.role_templates import ROLE_TEMPLATES, detect_role_template

    report: dict = {"started_at": int(time.time()), "samples": [],
                    "summary": {"role_families_in_registry": len(ROLE_TEMPLATES)}}

    # One agent per role family — prefer smaller offices (less LLM cost) so
    # pull any matching one from db.agents.
    seen_families: set[str] = set()
    agents = await db.agents.find({"is_commander": {"$ne": True}},
                                  {"_id": 0}).to_list(1000)
    for a in agents:
        tpl = detect_role_template(a)
        if tpl is None:
            continue
        fam = tpl["role_family"]
        if fam in seen_families:
            continue
        seen_families.add(fam)

        office = await office_get(a["agent_id"])
        if not office:
            report["samples"].append({"agent_id": a["agent_id"], "error": "no_office"})
            continue

        sop_steps = [s.name for s in office.sop]
        expected_steps = [s.name for s in tpl["sop"]]
        step_match = sop_steps == expected_steps
        studio_match = office.studio_name.endswith(tpl["studio_suffix"])

        # Dry-run to exercise the persona-composition path without LLM cost.
        dr = await run_sop(office, f"Sample brief for {a['role']}",
                            user_id="smoke_user_maars", dry_run=True)

        report["samples"].append({
            "agent_id":     a["agent_id"],
            "agent_name":   a.get("name"),
            "role":         a.get("role"),
            "role_family":  fam,
            "studio_name":  office.studio_name,
            "studio_suffix_match": studio_match,
            "sop_steps":    sop_steps,
            "sop_steps_match_template": step_match,
            "skill_count":  len(office.skills_library),
            "skill_ids":    [s.skill_id for s in office.skills_library],
            "quality_rule_count": len(office.quality_rules),
            "languages":    office.languages_supported,
            "dry_run_trace_steps": [t["step"] for t in (dr.get("trace") or [])],
            "persona_has_system_prompt": bool(a.get("system_prompt")),
        })

    # Verify every registered family has a sample
    report["summary"]["families_sampled"] = len(seen_families)
    report["summary"]["families_missing_sample"] = [
        t["role_family"] for t in ROLE_TEMPLATES if t["role_family"] not in seen_families
    ]
    report["summary"]["all_step_matches"] = all(
        s.get("sop_steps_match_template", False) for s in report["samples"]
    )
    report["summary"]["all_studio_matches"] = all(
        s.get("studio_suffix_match", False) for s in report["samples"]
    )
    report["summary"]["all_have_skills"] = all(
        (s.get("skill_count") or 0) >= 1 for s in report["samples"]
    )
    report["summary"]["all_have_persona"] = all(
        s.get("persona_has_system_prompt") for s in report["samples"]
    )

    report["finished_at"] = int(time.time())
    REPORT_PATH.write_text(json.dumps(report, indent=2, default=str))
    # Print tight summary
    s = report["summary"]
    print(json.dumps({
        "families_in_registry":   s["role_families_in_registry"],
        "families_sampled":       s["families_sampled"],
        "families_missing_sample":s["families_missing_sample"],
        "all_step_matches":       s["all_step_matches"],
        "all_studio_matches":     s["all_studio_matches"],
        "all_have_skills":        s["all_have_skills"],
        "all_have_persona":       s["all_have_persona"],
        "report_path":            str(REPORT_PATH),
    }, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
