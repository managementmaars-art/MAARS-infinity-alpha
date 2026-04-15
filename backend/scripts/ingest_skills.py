"""MAARS Skill Ingestion Script.

Fetches EVERY agent from MongoDB (all 458+ default + all custom),
dynamically matches skills and provider knowledge to each one using
keyword matching on role/description/capabilities/network, and upserts
into the `knowledge_chunks` collection.

The existing RAG pipeline in routes/chats.py automatically picks up
these chunks — no other changes needed for agent skill retrieval.

Usage:
    cd backend
    python scripts/ingest_skills.py [--force] [--agents-only] [--providers-only]

Flags:
    --force           Re-ingest even if chunks already exist for an agent
    --agents-only     Skip provider knowledge ingestion
    --providers-only  Skip skill ingestion, only ingest provider knowledge
"""

import asyncio
import sys
import logging
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).parent.parent))

from db import db
from services.skills_service import (
    ensure_agent_skills,
    ensure_provider_skills,
    match_skills_for_agent,
    match_providers_for_agent,
)
from data.provider_skills import PROVIDER_SKILLS

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("ingest_skills")


async def ingest_global_provider_docs() -> int:
    """Store a global copy of every provider guide under agent_id='__provider__'.

    chats.py uses this for fast O(1) runtime lookup by provider name.
    """
    import re, hashlib
    from services.skills_service import _chunk_markdown, _doc_id

    now = datetime.now(timezone.utc)
    total = 0

    await db.knowledge_chunks.delete_many({
        "agent_id": "__provider__",
        "source":   "provider_skill",
    })

    for provider_name, entry in PROVIDER_SKILLS.items():
        knowledge = entry.get("knowledge", "").strip()
        if not knowledge:
            continue
        chunks = _chunk_markdown(knowledge)
        doc_id = _doc_id("provider", provider_name)
        docs = [
            {
                "agent_id":      "__provider__",
                "doc_id":        doc_id,
                "doc_title":     f"Provider Guide: {entry['display_name']}",
                "chunk_index":   i,
                "text":          chunk,
                "source":        "provider_skill",
                "provider_name": provider_name,
                "pages":         [1],
                "created_at":    now,
            }
            for i, chunk in enumerate(chunks)
        ]
        if docs:
            await db.knowledge_chunks.insert_many(docs)
            total += len(docs)
        log.info(f"  provider  {provider_name:20s} → {len(docs)} global chunks")

    return total


async def main():
    force         = "--force"          in sys.argv
    agents_only   = "--agents-only"    in sys.argv
    providers_only= "--providers-only" in sys.argv

    repo_root   = Path(__file__).parent.parent.parent
    # Canonical skills source (.agents/skills/) — surfaced to 30+ AI tools via
    # per-tool symlink dirs (.claude, .continue, .windsurf, .augment, etc.).
    # Ingest from the real directory so we capture the full document set per
    # skill, not just SKILL.md.
    skills_root = repo_root / ".agents" / "skills"
    if not skills_root.exists():
        skills_root = repo_root / ".claude" / "skills"  # legacy fallback

    if not skills_root.exists():
        log.error(f"Skills root not found: {skills_root}")
        sys.exit(1)

    available_skills = {
        d.name for d in skills_root.iterdir()
        if (d / "SKILL.md").exists()
    }
    log.info(f"Skills available: {len(available_skills)}")

    # ── Fetch all agents ───────────────────────────────────────────────────
    log.info("Fetching all agents from MongoDB…")
    all_agents = await db.agents.find(
        {"is_active": {"$ne": False}},
        {
            "_id": 0,
            "agent_id": 1, "name": 1, "role": 1,
            "description": 1, "capabilities": 1,
            "network": 1, "tags": 1, "system_prompt": 1,
        }
    ).to_list(None)
    log.info(f"Agents loaded: {len(all_agents)}")

    # ── Print matching preview ─────────────────────────────────────────────
    skill_match_counts: dict[str, int] = {}
    provider_match_counts: dict[str, int] = {}
    zero_skill_agents = []
    for agent in all_agents:
        skills = match_skills_for_agent(agent)
        provs  = match_providers_for_agent(agent)
        for s in skills:
            skill_match_counts[s] = skill_match_counts.get(s, 0) + 1
        for p in provs:
            provider_match_counts[p] = provider_match_counts.get(p, 0) + 1
        if not skills:
            zero_skill_agents.append(
                f"{agent.get('agent_id','?')} ({agent.get('role','?')})"
            )

    log.info("\n── Skill match preview ───────────────────────────────────────────")
    for skill, count in sorted(skill_match_counts.items(), key=lambda x: -x[1]):
        log.info(f"  {skill:40s} → {count} agents")

    if zero_skill_agents:
        log.warning(
            f"\n  {len(zero_skill_agents)} agents matched NO skills "
            f"(will still get provider knowledge):"
        )
        for a in zero_skill_agents[:10]:
            log.warning(f"    {a}")
        if len(zero_skill_agents) > 10:
            log.warning(f"    … and {len(zero_skill_agents)-10} more")

    # ── Ingest per-agent skill chunks ──────────────────────────────────────
    if not providers_only:
        log.info("\n── Ingesting skill knowledge chunks ──────────────────────────────")
        skill_total = 0
        for i, agent in enumerate(all_agents, 1):
            agent_id = agent.get("agent_id", "")
            if not force:
                existing = await db.knowledge_chunks.count_documents({
                    "agent_id": agent_id,
                    "source":   "skill",
                })
                if existing > 0:
                    continue
            inserted = await ensure_agent_skills(agent, db, skills_root)
            skill_total += inserted
            if i % 50 == 0:
                log.info(f"  … processed {i}/{len(all_agents)} agents")
        log.info(f"  Skills total chunks inserted: {skill_total}")

    # ── Ingest per-agent provider knowledge ───────────────────────────────
    if not agents_only:
        log.info("\n── Ingesting provider knowledge chunks ───────────────────────────")
        prov_total = 0
        for agent in all_agents:
            agent_id = agent.get("agent_id", "")
            if not force:
                existing = await db.knowledge_chunks.count_documents({
                    "agent_id": agent_id,
                    "source":   "provider_skill",
                })
                if existing > 0:
                    continue
            inserted = await ensure_provider_skills(agent, db)
            prov_total += inserted
        log.info(f"  Provider total chunks inserted: {prov_total}")

        # Always refresh global provider docs
        log.info("\n── Refreshing global provider docs (__provider__) ────────────────")
        global_total = await ingest_global_provider_docs()
        log.info(f"  Global provider chunks: {global_total}")

    # ── Final stats ────────────────────────────────────────────────────────
    log.info("\n── DB Summary ────────────────────────────────────────────────────")
    total       = await db.knowledge_chunks.count_documents({})
    skill_count = await db.knowledge_chunks.count_documents({"source": "skill"})
    prov_count  = await db.knowledge_chunks.count_documents({"source": "provider_skill"})
    other_count = total - skill_count - prov_count
    unique_agents = len(await db.knowledge_chunks.distinct("agent_id"))
    log.info(f"  Total chunks   : {total:,}")
    log.info(f"  Skill chunks   : {skill_count:,}")
    log.info(f"  Provider chunks: {prov_count:,}")
    log.info(f"  Other (user KB): {other_count:,}")
    log.info(f"  Agents covered : {unique_agents:,}")
    log.info("\n✅ Ingestion complete.")


if __name__ == "__main__":
    asyncio.run(main())
