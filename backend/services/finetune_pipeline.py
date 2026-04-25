"""Fine-tuning pipeline scaffold.

Exports MAARS training data (golden examples + validated SME corrections
+ thumbs-up conversations) to the OpenAI/Unsloth JSONL format so you
can kick off a LoRA training job when you have enough traffic.

Deliberately a SCAFFOLD:
- Actual training runs on external infra (Unsloth notebook / RunPod /
  Modal). This module just prepares the dataset.
- Per the operator's "revisit at 50+ clients" memory, the pipeline
  isn't auto-triggered — it's manual via the admin endpoint.

Output format (JSONL — one JSON object per line):
    {"messages": [{"role":"system","content":"..."},
                  {"role":"user","content":"..."},
                  {"role":"assistant","content":"..."}]}

Sources combined:
  1. `agent_golden_examples`             — curated ideal user→agent pairs
  2. `sme_corrections` (status=validated) — corrections the SME approved
  3. `messages` (feedback=up)             — user-thumbed chat turns
     (joined with chats to find the preceding user message)

Public API:
    export_dataset(agent_id=None, min_examples=20, include_sources=[...])
    preview_dataset(agent_id=None, limit=10)
"""
from __future__ import annotations
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


async def _collect_golden(agent_id: str | None) -> list[dict]:
    from db import db
    q = {}
    if agent_id:
        q = {"$or": [
            {"scope": "agent",   "scope_value": agent_id},
            {"scope": "network", "scope_value": None},   # no-op; just documents intent
            {"scope": "role",    "scope_value": None},
        ]}
        q = {"scope": "agent", "scope_value": agent_id}
    cursor = db.agent_golden_examples.find(q, {
        "_id": 0, "user_input": 1, "ideal_output": 1, "scope": 1,
    })
    return [
        {"user": d.get("user_input", ""), "assistant": d.get("ideal_output", ""),
         "source": "golden"}
        async for d in cursor
        if d.get("user_input") and d.get("ideal_output")
    ]


async def _collect_sme(agent_id: str | None) -> list[dict]:
    from db import db
    q = {"status": "validated"}
    if agent_id:
        q["agent_id"] = agent_id
    cursor = db.sme_corrections.find(q, {
        "_id": 0, "query": 1, "corrected_response": 1, "original_response": 1,
    })
    out = []
    async for d in cursor:
        answer = d.get("corrected_response") or d.get("original_response")
        if d.get("query") and answer:
            out.append({"user": d["query"], "assistant": answer, "source": "sme"})
    return out


async def _collect_thumbed_up(agent_id: str | None) -> list[dict]:
    """Join chat-level agent_id with thumbed-up assistant messages + the
    preceding user prompt."""
    from db import db
    # Find all thumbed-up assistant messages
    q = {"feedback": "up", "role": "assistant"}
    assistants = await db.messages.find(q, {
        "_id": 0, "message_id": 1, "chat_id": 1, "content": 1, "created_at": 1,
    }).limit(2000).to_list(length=2000)

    out: list[dict] = []
    for a in assistants:
        chat = await db.chats.find_one({"chat_id": a["chat_id"]}, {"agent_id": 1, "_id": 0})
        if not chat:
            continue
        if agent_id and chat.get("agent_id") != agent_id:
            continue
        # Preceding user message
        prior = await db.messages.find({
            "chat_id": a["chat_id"], "role": "user",
            "created_at": {"$lt": a.get("created_at")},
        }, {"_id": 0, "content": 1}).sort("created_at", -1).limit(1).to_list(length=1)
        if not prior:
            continue
        out.append({
            "user":      prior[0].get("content", ""),
            "assistant": a.get("content", ""),
            "source":    "thumbed_up",
        })
    return out


async def _collect_system_prompt(agent_id: str | None) -> str:
    if not agent_id:
        return ""
    from db import db
    agent = await db.agents.find_one({"agent_id": agent_id}, {"system_prompt": 1, "_id": 0})
    return (agent or {}).get("system_prompt") or ""


async def export_dataset(
    *, agent_id: str | None = None,
    min_examples: int = 20,
    include_sources: list[str] | None = None,
    output_dir: str = "training_datasets",
) -> dict[str, Any]:
    """Merge all sources, dedupe, write to JSONL. Returns summary."""
    sources = include_sources or ["golden", "sme", "thumbed_up"]
    data: list[dict] = []
    if "golden" in sources:
        data.extend(await _collect_golden(agent_id))
    if "sme" in sources:
        data.extend(await _collect_sme(agent_id))
    if "thumbed_up" in sources:
        data.extend(await _collect_thumbed_up(agent_id))

    # Dedupe on user prompt
    seen: set[str] = set()
    dedup: list[dict] = []
    for d in data:
        key = d["user"].strip().lower()[:300]
        if key in seen:
            continue
        seen.add(key)
        dedup.append(d)

    if len(dedup) < min_examples:
        return {
            "ok":              False,
            "error":           f"only {len(dedup)} examples; need >= {min_examples}",
            "dataset_size":    len(dedup),
            "min_required":    min_examples,
            "source_counts":   {
                s: sum(1 for d in dedup if d["source"] == s)
                for s in sources
            },
        }

    # Build JSONL with per-agent system prompt
    sys_prompt = await _collect_system_prompt(agent_id)
    now = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    filename = f"finetune_{agent_id or 'all'}_{now}.jsonl"
    path = out_dir / filename

    with path.open("w", encoding="utf-8") as f:
        for d in dedup:
            messages = []
            if sys_prompt:
                messages.append({"role": "system", "content": sys_prompt})
            messages.append({"role": "user",      "content": d["user"]})
            messages.append({"role": "assistant", "content": d["assistant"]})
            f.write(json.dumps({"messages": messages}, ensure_ascii=False) + "\n")

    # Record the export in Mongo so admin can list past exports
    from db import db
    await db.finetune_exports.insert_one({
        "agent_id":      agent_id,
        "exported_at":   datetime.now(timezone.utc).isoformat(),
        "example_count": len(dedup),
        "source_counts": {s: sum(1 for d in dedup if d["source"] == s) for s in sources},
        "path":          str(path),
        "system_prompt_hash": None if not sys_prompt else f"len={len(sys_prompt)}",
    })

    return {
        "ok":            True,
        "path":          str(path),
        "dataset_size":  len(dedup),
        "source_counts": {s: sum(1 for d in dedup if d["source"] == s) for s in sources},
        "notes": (
            "Upload the JSONL to Unsloth (LoRA), OpenAI fine-tuning, or "
            "HuggingFace TRL for SFT. For GRPO-style reasoning RL, pair "
            "with a reward function that scores model outputs against "
            "the `assistant` field as the reference."
        ),
    }


async def preview_dataset(
    *, agent_id: str | None = None, limit: int = 10,
) -> list[dict]:
    data: list[dict] = []
    data.extend(await _collect_golden(agent_id))
    data.extend(await _collect_sme(agent_id))
    data.extend(await _collect_thumbed_up(agent_id))
    return data[:limit]
