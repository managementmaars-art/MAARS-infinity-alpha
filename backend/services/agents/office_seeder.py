"""Bulk-seed agent offices from the live agents collection.

Called once at migration time (or on-demand from admin UI). Reads the
canonical agents list, materializes an office per agent based on the
department template for their network, and upserts into
`agent_offices`. Safe to re-run — existing offices are updated
rather than duplicated.
"""
from __future__ import annotations
import logging
from typing import Any

from .agent_office import AgentOffice, SOPStep, SkillWorkflow, put, get
from .office_templates import (
    template_for_network, materialize_office,
    CREATIVE_BRAND,
)
from .role_templates import detect_role_template, materialize_from_role

logger = logging.getLogger(__name__)


# ── Special-case offices that override the template ──────────────────
# Commander Orion and the Video Content Creator get fully custom SOPs.
# Everyone else inherits from the department template.

def _commander_office(agent_row: dict) -> AgentOffice:
    """Commander Orion's unique office — system-wide orchestrator."""
    return AgentOffice(
        agent_id=agent_row["agent_id"],
        agent_name=agent_row.get("name", "Commander Orion"),
        network=agent_row.get("network", "core_team"),
        department="Core Leadership",
        studio_name="Commander's Bridge",
        mission="Orchestrate every MAARS capability into coordinated, verified action "
                "on behalf of the operator. Never act without a measurable objective "
                "and never ship without quality verification.",
        sop=[
            SOPStep(
                name="classify",
                description="Classify the incoming goal: one-shot task vs. multi-step "
                            "program vs. standing policy. Decompose into a task graph.",
                expected_output="Task graph with dependencies + acceptance criteria per node.",
            ),
            SOPStep(
                name="delegate",
                description="Assign each task-graph node to the right agent(s) based on "
                            "network + autonomy tier. Pass context + deadline + budget. "
                            "Use delegate_to_agent to run another agent's FULL SOP "
                            "(their research+produce+verify pipeline), not just a single "
                            "LLM call. The child agent returns a structured result which "
                            "you then feed into supervise + verify.",
                tools=["query_agent_history", "create_task", "update_task",
                       "delegate_to_agent"],
                expected_output="Delegations recorded in tasks collection with owners. "
                               "Each delegated agent returns their SOP output.",
            ),
            SOPStep(
                name="supervise",
                description="Monitor every delegated node. Intervene on stalls, errors, "
                            "or quality regressions. Provide additional context when an "
                            "agent is stuck.",
                tools=["query_agent_history", "query_tasks", "send_slack"],
                expected_output="Status log for every node; interventions recorded.",
            ),
            SOPStep(
                name="verify",
                description="Cross-check delegated outputs against original acceptance "
                            "criteria. Never approve an unverified artifact for real-world "
                            "execution.",
                tools=["analyze_data"],
                expected_output="Pass/fail verdict per node.",
            ),
            SOPStep(
                name="execute",
                description="Hand verified artifacts to Secretary (Nadia Kessler) for "
                            "real-world action: send email, post content, move money, etc.",
                tools=["send_slack", "update_task", "webhook_action"],
                expected_output="Real-world actions dispatched + confirmation received.",
            ),
            SOPStep(
                name="report",
                description="Produce operator-facing summary: what was done, what was "
                            "found, what needs attention, what's next.",
                tools=["send_slack", "send_email"],
                expected_output="Executive summary ≤ 200 words.",
            ),
        ],
        studio_tools=agent_row.get("tools") or [],
        skills_library=[],                # Commander has no skills — he delegates
        quality_rules=[],                 # Commander enforces every other agent's rules
        reference_memory_tags=["commander", "orchestration", "governance"],
        monthly_budget_credits=agent_row.get("monthly_budget_credits") or 100_000,
        languages_supported=["en", "es", "fr", "de", "pt", "ja", "zh", "ar", "hi"],
    )


def _video_creator_office(agent_row: dict) -> AgentOffice:
    """The flagship example office from the operator's request:
    'the video content creator should have his own studio, he should do a
    thorough websearch, go through every existing pictures and videos of
    the product from every angle then generate a perfect content with
    appropriate voice over (in any language requested).'"""
    return AgentOffice(
        agent_id=agent_row["agent_id"],
        agent_name=agent_row.get("name", "Video Content Creator"),
        network=agent_row.get("network", "core_team"),
        department="Creative & Marketing",
        studio_name="Video Production Studio",
        mission="Deliver polished product videos (ads, demos, explainers, shorts) from "
                "a product name + brief, by researching every existing reference of the "
                "product, designing a storyboard, generating footage + voiceover in any "
                "requested language, and compositing a ready-to-ship video.",
        sop=[
            SOPStep(
                name="understand",
                description="Parse the client brief: product name, desired tone "
                            "(lifestyle/demo/comparison/social-short), duration "
                            "(6s / 15s / 30s / 60s), aspect ratio, target audience, "
                            "call-to-action, target language for voiceover, brand "
                            "guidelines URL if any.",
                expected_output="Structured brief JSON ready for research step.",
            ),
            SOPStep(
                name="research_web",
                description="Web-search the product from every angle: official brand "
                            "page, Amazon/e-commerce listings, YouTube reviews + demos, "
                            "social posts (Instagram/TikTok/X), blog reviews, press "
                            "releases. Collect 20+ reference items.",
                tools=["web_search", "browser_open", "browser_navigate",
                       "browser_extract", "browser_screenshot"],
                expected_output="Reference dossier: URLs + extracted imagery + key "
                               "product facts + brand voice examples.",
            ),
            SOPStep(
                name="analyze_references",
                description="Run vision LLM across every collected image/video thumbnail. "
                            "Extract: product angles captured, color palette, setting "
                            "conventions, typical production style, visual motifs of "
                            "the brand.",
                tools=["analyze_data", "enhance_prompt"],
                expected_output="Visual analysis doc: dominant colors, angle coverage, "
                               "brand motifs, what's overdone vs. underexplored.",
            ),
            SOPStep(
                name="script",
                description="Write the script / voiceover narration using research context. "
                            "Match tone from brief. Keep within duration (rough: 150 "
                            "words/min). Translate to client's requested language if "
                            "not English — use a native-speaker style, not literal "
                            "translation.",
                expected_output="Final script with scene-by-scene timing markers.",
            ),
            SOPStep(
                name="storyboard",
                description="Generate 1 still keyframe per scene matching the analyzed "
                            "brand visual style. Each keyframe should fit the script "
                            "beat and the product's established look.",
                tools=["generate_image", "enhance_prompt"],
                expected_output="N keyframes (N = duration_seconds / 5) as URLs or blobs.",
            ),
            SOPStep(
                name="produce_video",
                description="Generate video clips from keyframes using image-to-video "
                            "model (Sora for Basic+/premium tiers, Pika/Runway for "
                            "lower tiers). Each clip ≤ 5s; stitch in composite step. "
                            "Ensure visual continuity across clips.",
                tools=["generate_video"],
                expected_output="Video clip URLs keyed to scene index.",
            ),
            SOPStep(
                name="produce_voiceover",
                description="Generate voiceover in client's requested language. Use "
                            "ElevenLabs multilingual for paid tiers, OpenAI tts-1-hd "
                            "fallback. Match pacing to script timing.",
                tools=["generate_voiceover", "generate_tts"],
                expected_output="Voiceover audio file URL + transcript timing.",
            ),
            SOPStep(
                name="composite",
                description="Stitch clips in order, overlay voiceover track, optionally "
                            "burn subtitles in requested language, add music bed if brief "
                            "allows. Render final MP4/MOV at spec (aspect ratio, "
                            "resolution, duration).",
                tools=["webhook_action"],     # ffmpeg backend called via webhook
                expected_output="Final composited video URL + thumbnail URL.",
            ),
            SOPStep(
                name="verify",
                description="Check: duration matches brief ±5%, audio synced to video, "
                            "no copyrighted frames reproduced verbatim, voiceover "
                            "language correct (sample-check a few sentences), brand "
                            "colors present.",
                expected_output="Quality report (pass/fail per rule) + suggested fixes.",
            ),
            SOPStep(
                name="deliver",
                description="Return signed URL for the final video + internal memory "
                            "entry tagged with product + campaign + brand so future "
                            "videos reuse analysis + assets.",
                tools=["send_email", "send_slack", "update_task"],
                expected_output="Client-facing delivery package.",
            ),
        ],
        studio_tools=[
            "web_search", "browser_open", "browser_navigate", "browser_extract",
            "browser_screenshot", "analyze_data", "enhance_prompt",
            "generate_image", "generate_video", "generate_voiceover", "generate_tts",
            "webhook_action", "send_email", "send_slack", "update_task",
        ],
        skills_library=[
            SkillWorkflow(
                skill_id="product_ad_30s",
                name="30-Second Product Ad",
                description="Full product-ad workflow — research → storyboard → 30s video + VO.",
                trigger_keywords=("30 sec ad", "30-second ad", "thirty second ad",
                                  "short product ad", "commercial 30s"),
                steps=[],   # uses default SOP
                avg_credits=3700,
            ),
            SkillWorkflow(
                skill_id="product_demo_60s",
                name="60-Second Product Demo",
                description="Longer-form demo with feature walkthrough + voiceover.",
                trigger_keywords=("60 second demo", "product demo video",
                                  "demo video", "walkthrough video"),
                steps=[],
                avg_credits=6000,
            ),
            SkillWorkflow(
                skill_id="social_short_15s",
                name="15-Second Social Short",
                description="Vertical 9:16 short for TikTok/Reels/Shorts.",
                trigger_keywords=("tiktok", "reels", "short form", "15 second",
                                  "vertical video", "social short"),
                steps=[],
                avg_credits=1800,
            ),
        ],
        quality_rules=list(CREATIVE_BRAND["quality_rules"]) + [
            # Video-specific quality rules on top of Creative defaults
        ],
        reference_memory_tags=["video", "creative", "brand", "product_ad"],
        monthly_budget_credits=agent_row.get("monthly_budget_credits") or 20_000,
        languages_supported=[
            "en", "es", "fr", "de", "pt", "ja", "zh", "ar", "hi", "it",
            "nl", "pl", "ru", "tr", "id", "vi", "ko",
        ],
    )


# ── Video-creator detector ──────────────────────────────────────────

def _is_video_creator(agent_row: dict) -> bool:
    name = (agent_row.get("name") or "").lower()
    role = (agent_row.get("role") or "").lower()
    desc = (agent_row.get("description") or "").lower()
    agent_id = (agent_row.get("agent_id") or "").lower()
    blob = f"{name} {role} {desc} {agent_id}"
    return ("video" in blob) and any(k in blob for k in (
        "creator", "producer", "director", "editor", "animator",
        "specialist", "content", "production",
    ))


# ── Main seeder ──────────────────────────────────────────────────────

async def seed_all_offices(force_rebuild: bool = False) -> dict[str, Any]:
    """Iterate every agent in `agents` collection, materialize its office,
    upsert into `agent_offices`. If force_rebuild=False, skip agents that
    already have an office (fast re-run)."""
    from db import db
    agents = await db.agents.find({}, {"_id": 0}).to_list(10_000)
    created = 0
    updated = 0
    skipped = 0
    errors: list[str] = []
    # Coverage map — which training path each agent landed on.
    coverage: dict[str, int] = {
        "commander": 0, "video_creator": 0, "role_family": 0, "department": 0,
    }
    role_family_counts: dict[str, int] = {}

    for agent in agents:
        try:
            aid = agent.get("agent_id")
            if not aid:
                continue
            existing = None
            if not force_rebuild:
                existing = await get(aid)
                if existing:
                    skipped += 1
                    continue

            # Priority order:
            #   1. Commander — system orchestrator SOP
            #   2. Video Creator — flagship hand-authored 10-step SOP
            #   3. Role-family template (designer/writer/sdr/developer/etc.)
            #   4. Department template fallback
            role_lower = (agent.get("role") or "").lower()
            name_lower = (agent.get("name") or "").lower()
            is_commander_like = (
                agent.get("is_commander")
                or aid == "agent_commander"
                or role_lower == "commander"
                or "commander orion" in name_lower
            )
            if is_commander_like:
                office = _commander_office(agent)
                coverage["commander"] += 1
            elif _is_video_creator(agent):
                office = _video_creator_office(agent)
                coverage["video_creator"] += 1
            else:
                role_tpl = detect_role_template(agent)
                if role_tpl is not None:
                    office = materialize_from_role(agent, role_tpl)
                    coverage["role_family"] += 1
                    fam = role_tpl.get("role_family", "unknown")
                    role_family_counts[fam] = role_family_counts.get(fam, 0) + 1
                else:
                    office = materialize_office(agent)
                    coverage["department"] += 1

            await put(office)
            if existing:
                updated += 1
            else:
                created += 1
        except Exception as exc:
            errors.append(f"{agent.get('agent_id')}: {type(exc).__name__}: {exc}")
            if len(errors) > 20:
                break

    return {
        "agents_scanned": len(agents),
        "offices_created": created,
        "offices_updated": updated,
        "skipped_existing": skipped,
        "training_coverage": coverage,
        "role_family_distribution": role_family_counts,
        "errors":           errors,
    }
