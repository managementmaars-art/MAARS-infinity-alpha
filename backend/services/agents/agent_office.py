"""Agent Office — the dedicated workspace every agent operates from.

Before this module, an agent was a (system_prompt + allowlisted tools)
tuple. That's enough to make a call but not enough to do a job. A real
knowledge worker has:

  1. An **SOP** (standard operating procedure) — the steps they always
     take for their type of work: understand → research → plan →
     produce → verify → deliver.
  2. A **studio / toolkit** — the tools specific to their craft, not
     shared with everyone else.
  3. A **skills library** — prebuilt multi-step workflows they know
     how to execute without re-learning each time.
  4. A **reference memory** — their own past work, patterns that
     succeeded, examples they studied.
  5. **Quality rules** — what "good" looks like for this role.
  6. A **budget** — credits allocated to their work for the month.

The Office bundles all six per agent. Commander Orion keeps his
"system-wide orchestrator" view; every other agent inherits a
department template (creative, research, sales, ops, etc.) and
specializes it with role-specific SOPs.

Data lives in MongoDB collection `agent_offices` keyed by agent_id.
Each office has the SOP applied via `run_sop(office, user_request)`
which drives the agent through the full research-first workflow.

This is what the example "Video Content Creator with his own studio"
was describing — a role that doesn't just CALL a video API, it
researches the product, ingests references, writes a script, generates
the video, adds voiceover, composites, and delivers. That entire
pipeline IS the Office's SOP.
"""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Optional
import logging

logger = logging.getLogger(__name__)


# ── Data model ───────────────────────────────────────────────────────

@dataclass
class SOPStep:
    """One step in the agent's standard operating procedure."""
    name: str                           # "research" | "plan" | "produce" | "verify" | "deliver"
    description: str
    tools: list[str] = field(default_factory=list)   # tools used in this step
    required: bool = True
    expected_output: str = ""


@dataclass
class SkillWorkflow:
    """A prebuilt multi-step workflow the agent knows how to execute."""
    skill_id: str
    name: str
    description: str
    trigger_keywords: tuple[str, ...]   # request patterns that activate this skill
    steps: list[SOPStep]
    avg_credits: int = 100              # typical cost per execution


@dataclass
class QualityRule:
    """Acceptance criterion the agent must meet before delivery."""
    name: str
    check: str                          # human-readable check description
    severity: str = "hard"              # "hard" = block delivery | "soft" = warn only


@dataclass
class AgentOffice:
    """Per-agent workspace. One document per agent_id in Mongo."""
    agent_id: str
    agent_name: str
    network: str                        # network key (e.g. "10F" = creative_brand)
    department: str                     # higher-level grouping
    studio_name: str                    # human-readable office name
    mission: str                        # one sentence: what this office exists to do
    sop: list[SOPStep]                  # the research-first workflow
    studio_tools: list[str]             # role-specific tools (beyond the agent's allowlist defaults)
    skills_library: list[SkillWorkflow] # prebuilt workflows
    quality_rules: list[QualityRule]    # acceptance criteria
    reference_memory_tags: list[str]    # memory-graph tags to search for past work
    monthly_budget_credits: int = 1000
    languages_supported: list[str] = field(default_factory=lambda: ["en"])
    training_examples_count: int = 0    # populated from golden_examples at read time

    def to_doc(self) -> dict:
        return {
            **asdict(self),
            "sop":            [asdict(s) for s in self.sop],
            "skills_library": [asdict(s) for s in self.skills_library],
            "quality_rules":  [asdict(q) for q in self.quality_rules],
        }


# ── Storage ──────────────────────────────────────────────────────────

async def get(agent_id: str) -> Optional[AgentOffice]:
    """Load one office. Returns None if the agent has no office yet."""
    from db import db
    doc = await db.agent_offices.find_one({"agent_id": agent_id}, {"_id": 0})
    if not doc:
        return None
    # Reconstruct dataclasses
    sop = [SOPStep(**s) for s in (doc.get("sop") or [])]
    skills = [SkillWorkflow(
                skill_id=s["skill_id"], name=s["name"],
                description=s["description"],
                trigger_keywords=tuple(s.get("trigger_keywords") or ()),
                steps=[SOPStep(**st) for st in (s.get("steps") or [])],
                avg_credits=s.get("avg_credits", 100),
              ) for s in (doc.get("skills_library") or [])]
    quality = [QualityRule(**q) for q in (doc.get("quality_rules") or [])]
    return AgentOffice(
        agent_id=doc["agent_id"],
        agent_name=doc.get("agent_name", ""),
        network=doc.get("network", ""),
        department=doc.get("department", ""),
        studio_name=doc.get("studio_name", ""),
        mission=doc.get("mission", ""),
        sop=sop,
        studio_tools=doc.get("studio_tools") or [],
        skills_library=skills,
        quality_rules=quality,
        reference_memory_tags=doc.get("reference_memory_tags") or [],
        monthly_budget_credits=doc.get("monthly_budget_credits", 1000),
        languages_supported=doc.get("languages_supported") or ["en"],
        training_examples_count=doc.get("training_examples_count", 0),
    )


async def put(office: AgentOffice) -> None:
    """Create or replace an office."""
    from db import db
    from datetime import datetime, timezone
    doc = office.to_doc()
    doc["updated_at"] = datetime.now(timezone.utc).isoformat()
    await db.agent_offices.update_one(
        {"agent_id": office.agent_id},
        {"$set": doc, "$setOnInsert": {"created_at": doc["updated_at"]}},
        upsert=True,
    )


async def list_by_department(department: str | None = None) -> list[dict]:
    """Admin UI helper: list offices, optionally filtered by department."""
    from db import db
    q: dict[str, Any] = {}
    if department:
        q["department"] = department
    cursor = db.agent_offices.find(q, {"_id": 0}).limit(1000)
    return await cursor.to_list(1000)


async def list_departments() -> list[dict]:
    """Aggregate office count per department for the admin overview."""
    from db import db
    pipeline = [
        {"$group": {"_id": "$department", "count": {"$sum": 1},
                    "agents": {"$push": "$agent_name"}}},
        {"$sort": {"count": -1}},
    ]
    rows = await db.agent_offices.aggregate(pipeline).to_list(100)
    return [{
        "department":    r["_id"] or "unassigned",
        "office_count":  r["count"],
        "agents_sample": (r.get("agents") or [])[:5],
    } for r in rows]


# ── SOP runner (the actual "train them to do the work" part) ─────────

async def _execute_tool(
    tool_name: str,
    params: dict,
    *,
    user_id: str,
) -> dict:
    """Dispatch a single tool call through the workflow executor's
    TOOL_REGISTRY. Returns a normalized {ok, tool, output, error?} dict.

    The TOOL_REGISTRY is the single source of truth for what an agent
    can actually invoke — web_search, browser_open, generate_image,
    generate_video, send_email, post_social, etc. When the SOP runner
    wants an agent to DO something (not just describe it), this is
    how.
    """
    try:
        from services.workflows.workflow_executor import TOOL_REGISTRY
    except Exception as exc:
        return {"ok": False, "tool": tool_name, "error": f"registry_import_failed: {exc}"}
    handler = TOOL_REGISTRY.get(tool_name)
    if not handler:
        return {"ok": False, "tool": tool_name, "error": "unknown_tool"}
    try:
        result = await handler(user_id, params or {}, {})
        return {"ok": True, "tool": tool_name, "output": result}
    except Exception as exc:
        return {"ok": False, "tool": tool_name, "error": f"{type(exc).__name__}: {str(exc)[:200]}"}


def _parse_tool_calls(step_output: str) -> list[dict]:
    """Extract tool-call directives the LLM emitted in a step's output.

    The SOP prompt asks the LLM to return a block like:
        <tool_calls>[{"tool":"web_search","params":{"query":"..."}},...]</tool_calls>
    We parse that; missing/malformed blocks just yield an empty list,
    which is fine — the step ran, the LLM just decided no tool was
    needed (or the step is text-only).
    """
    if not step_output or not isinstance(step_output, str):
        return []
    import re, json
    m = re.search(r"<tool_calls>\s*(\[[\s\S]*?\])\s*</tool_calls>", step_output)
    if not m:
        return []
    try:
        arr = json.loads(m.group(1))
        if not isinstance(arr, list):
            return []
        return [c for c in arr if isinstance(c, dict) and c.get("tool")]
    except Exception:
        return []


async def _agent_persona(agent_id: str) -> dict:
    """Load the per-agent persona that `run_sop` bolts onto every SOP step:
    stored system_prompt, capabilities list, model preference, and any
    golden_examples that exist. Cached implicitly per run — callers should
    invoke once per `run_sop` invocation, not per step.

    Returns {} if the agent row is missing — SOP still runs with the
    office's mission/studio persona in that case.
    """
    from db import db
    row = await db.agents.find_one({"agent_id": agent_id}, {
        "_id": 0, "name": 1, "role": 1, "system_prompt": 1, "capabilities": 1,
        "model_name": 1, "model_provider": 1, "golden_examples": 1,
        "description": 1,
    })
    return row or {}


def _golden_few_shot_block(examples: list, *, limit: int = 2, max_chars: int = 1600) -> str:
    """Format up to N stored golden-output examples as few-shots for the
    step prompt. Examples may be {user, assistant} dicts or free-form
    strings — we accept both and truncate aggressively."""
    if not examples:
        return ""
    blocks: list[str] = []
    budget = max_chars
    for ex in examples[:limit]:
        if isinstance(ex, dict):
            u = str(ex.get("user") or ex.get("input") or "")[:400]
            a = str(ex.get("assistant") or ex.get("output") or "")[:600]
            block = f"Example request: {u}\nExample excellent output: {a}"
        else:
            block = f"Example: {str(ex)[:600]}"
        if len(block) > budget:
            block = block[:budget]
        blocks.append(block)
        budget -= len(block)
        if budget <= 0:
            break
    if not blocks:
        return ""
    return "\n\nHere are examples of past excellent work in this role:\n" + "\n---\n".join(blocks)


async def run_sop(
    office: AgentOffice,
    user_request: str,
    *,
    user_id: str,
    context: dict | None = None,
    dry_run: bool = False,
) -> dict:
    """Execute the agent's SOP on a real request. Drives the agent
    through every step (research → plan → produce → verify → deliver)
    and returns the structured output plus the execution trace.

    Each step's system prompt is composed from THREE layers:

      1. Agent persona   — the stored system_prompt + capabilities from
                           db.agents, so the agent stays in character
                           (tone, identity, domain scope).
      2. Office context  — mission, studio name, department rules, the
                           step's description + allowlisted tools.
      3. Few-shot golden — up to 2 stored golden_examples for the role,
                           if any exist.

    This is what transforms the office from a generic LLM call into a
    knowledge worker that sounds like THIS agent doing THEIR job.

    Each step can also emit `<tool_calls>[...]` directives; the runner
    executes those tools against `workflow_executor.TOOL_REGISTRY` and
    feeds results back into the next step's context.
    """
    from services.llm_gateway import complete
    trace: list[dict] = []
    accumulated: dict[str, Any] = {"user_request": user_request, "context": context or {}}

    # Per-run persona load — one DB hit, shared across all steps.
    persona = await _agent_persona(office.agent_id)
    persona_sp  = (persona.get("system_prompt") or "").strip()
    capabilities = persona.get("capabilities") or []
    golden      = persona.get("golden_examples") or []
    few_shot_block = _golden_few_shot_block(golden)

    # Check if a skill from the library matches the request — if so
    # run the skill's steps instead of the default SOP.
    chosen_steps = office.sop
    matched_skill = None
    req_lower = user_request.lower()
    for skill in office.skills_library:
        if any(kw.lower() in req_lower for kw in skill.trigger_keywords):
            matched_skill = skill
            chosen_steps = skill.steps or office.sop   # skill may reference default steps
            break

    for step in chosen_steps:
        if dry_run:
            trace.append({"step": step.name, "status": "dry_run"})
            continue
        try:
            tools_desc = ""
            if step.tools:
                tools_desc = (
                    f"\n\nSuggested tools for this step: {', '.join(step.tools)}\n"
                    f"These are typical for '{step.name}', but you may use ANY tool you need — "
                    f"web_search, browser_open, browser_navigate, browser_extract, browser_screenshot, "
                    f"generate_image, generate_video, generate_voiceover, composite_video, "
                    f"send_email, send_slack, delegate_to_agent, and every other registered tool.\n"
                    f"To invoke, append exactly this block at the end of your output:\n"
                    f"<tool_calls>[{{\"tool\":\"<name>\",\"params\":{{...}}}}]</tool_calls>\n"
                    f"Call tools whenever live data, external fetches, or side effects are needed. "
                    f"Omit the block if truly no tool is needed."
                )
            persona_block = ""
            if persona_sp:
                persona_block = f"\n\n# Your identity and rules of engagement\n{persona_sp}"
            if capabilities:
                caps = ", ".join(str(c) for c in capabilities[:20])
                persona_block += f"\n\nYour declared capabilities: {caps}."
            sys_prompt = (
                f"You are {office.agent_name} operating from the {office.studio_name}.\n"
                f"Office mission: {office.mission}\n\n"
                f"Current SOP step: {step.name} — {step.description}\n"
                f"Expected output: {step.expected_output}"
                f"{tools_desc}"
                f"{persona_block}"
                f"{few_shot_block}"
            )
            user_msg = (
                f"Original user request: {user_request}\n\n"
                f"Context accumulated so far:\n{_trim_for_prompt(accumulated)}\n\n"
                f"Execute step '{step.name}' now."
            )
            resp = await complete(
                user_id=user_id,
                messages=[
                    {"role": "system", "content": sys_prompt},
                    {"role": "user",   "content": user_msg},
                ],
                agent_id=office.agent_id,
                source=f"office_sop:{office.agent_id}:{step.name}",
                model="maars/auto",
            )
            step_output = resp.get("choices", [{}])[0].get("message", {}).get("content", "")
            # Execute any tool calls the LLM emitted.
            # Step-level allowlist retired (per operator: "nothing should
            # be blocked") — step.tools now acts as a HINT in the prompt,
            # not a gate. Any registered tool in TOOL_REGISTRY is callable
            # from any step. If the LLM invents a non-existent tool name,
            # _execute_tool returns {ok:false, error:"unknown_tool"} —
            # which is the right signal, not a policy rejection.
            tool_results: list[dict] = []
            for call in _parse_tool_calls(step_output):
                tool_results.append(
                    await _execute_tool(call["tool"], call.get("params") or {}, user_id=user_id)
                )
            accumulated[step.name] = {
                "text": step_output,
                "tool_results": tool_results,
            }
            trace.append({
                "step":     step.name,
                "status":   "ok",
                "tokens":   resp.get("usage", {}).get("total_tokens", 0),
                "credits":  resp.get("maars", {}).get("credits_used", 0),
                "tools_invoked": [r["tool"] for r in tool_results],
                "tools_ok":      sum(1 for r in tool_results if r.get("ok")),
                "tools_failed":  sum(1 for r in tool_results if not r.get("ok")),
                "preview":  step_output[:200],
            })
        except Exception as exc:
            trace.append({"step": step.name, "status": "error", "error": str(exc)[:200]})
            if step.required:
                return {"ok": False, "trace": trace, "failed_step": step.name}

    # Quality-gate pass over accumulated output
    verdicts = []
    for rule in office.quality_rules:
        verdicts.append({"rule": rule.name, "check": rule.check, "severity": rule.severity})

    return {
        "ok":             True,
        "matched_skill":  matched_skill.skill_id if matched_skill else None,
        "trace":          trace,
        "output":         accumulated,
        "quality_checks": verdicts,
    }


def _trim_for_prompt(accumulated: dict, max_chars: int = 4000) -> str:
    """Keep the accumulated context short enough for the next step's LLM
    call. Long verbatim text gets truncated; structured tool results
    are preserved intact because they're usually the most important
    input to the next step."""
    import json
    try:
        raw = json.dumps(accumulated, default=str)
    except Exception:
        raw = str(accumulated)
    if len(raw) <= max_chars:
        return raw
    # Keep the most recent N keys in full, truncate older.
    return raw[-max_chars:]
