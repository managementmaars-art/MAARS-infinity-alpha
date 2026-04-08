"""MAARS Skills Service.

Dynamic skill + provider matching engine.
Works for ALL agents — the 458 default agents, any custom-built agent —
by matching skill keywords against the agent's role, description,
capabilities, and network fields.

Key public API
--------------
match_skills_for_agent(agent_doc)   → [skill_name, ...]
match_providers_for_agent(agent_doc)→ [provider_name, ...]  (ordered best→ok)
ensure_agent_skills(agent_doc, db, skills_root) → chunks inserted (int)
"""

import re
import hashlib
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)

# ── Skill → domain keyword sets ─────────────────────────────────────────────
# ANY agent whose combined text (role + description + capabilities + network)
# contains ≥1 of these words will receive this skill as knowledge.
SKILL_KEYWORDS: dict[str, list[str]] = {

    # ── Development / Engineering ────────────────────────────────────────────
    "python-patterns": [
        "developer", "engineer", "programmer", "coder", "fullstack", "backend",
        "automation", "data", "devops", "ml", "machine learning", "ai", "platform",
        "api", "software", "python", "script", "technical", "infrastructure",
        "architect", "sre", "site reliability", "cloud", "microservice",
    ],
    "python-testing": [
        "developer", "engineer", "qa", "quality assurance", "test", "automation",
        "backend", "data", "devops", "reliability", "sre",
    ],
    "postgres-patterns": [
        "developer", "engineer", "data", "analyst", "database", "dba",
        "backend", "sql", "postgres", "bi", "business intelligence", "warehouse",
    ],
    "database-migrations": [
        "developer", "engineer", "data", "database", "dba", "backend",
        "devops", "architect", "platform",
    ],
    "api-design": [
        "developer", "engineer", "backend", "fullstack", "api", "rest",
        "integration", "platform", "architect", "product", "automation",
    ],
    "backend-patterns": [
        "developer", "engineer", "backend", "fullstack", "platform", "sre",
        "architect", "cloud", "microservice", "infrastructure", "devops",
    ],
    "docker-patterns": [
        "developer", "engineer", "devops", "sre", "cloud", "infrastructure",
        "automation", "platform", "architect", "deployment", "container",
    ],
    "deployment-patterns": [
        "developer", "engineer", "devops", "sre", "cloud", "deployment",
        "infrastructure", "automation", "platform", "release", "operations",
    ],
    "git-workflow": [
        "developer", "engineer", "devops", "project manager", "lead",
        "technical", "cto", "architect", "team", "collaboration",
    ],
    "tdd-workflow": [
        "developer", "engineer", "qa", "quality", "test", "backend",
        "fullstack", "reliability",
    ],
    "webapp-testing": [
        "developer", "engineer", "qa", "quality", "frontend", "web",
        "ux", "product", "test",
    ],
    "security-review": [
        "security", "cyber", "compliance", "legal", "auditor", "risk",
        "infrastructure", "devops", "developer", "engineer", "gdpr",
        "privacy", "protection", "infosec", "penetration", "vulnerability",
    ],
    "claude-api": [
        "developer", "engineer", "ai", "ml", "llm", "integration", "platform",
        "backend", "automation", "chatbot", "agent", "nlp", "data",
    ],
    "mcp-builder": [
        "developer", "engineer", "ai", "platform", "integration", "backend",
        "automation", "tool", "orchestration", "agent",
    ],

    # ── Frontend / Design ─────────────────────────────────────────────────────
    "frontend-patterns": [
        "frontend", "web", "ui", "ux", "designer", "developer", "fullstack",
        "react", "vue", "angular", "javascript", "product", "mobile",
    ],
    "frontend-design": [
        "designer", "ui", "ux", "web", "frontend", "brand", "visual",
        "creative", "product", "motion", "graphic", "art director",
    ],
    "design-system": [
        "designer", "ui", "ux", "brand", "visual", "product", "frontend",
        "design system", "component", "style guide", "creative",
    ],
    "ui-ux-pro-max": [
        "designer", "ui", "ux", "web", "product", "creative", "visual",
        "frontend", "brand", "experience", "interface", "graphic",
    ],
    "ui-styling": [
        "designer", "ui", "ux", "frontend", "web", "visual", "css",
        "style", "brand", "creative",
    ],
    "design": [
        "designer", "creative", "visual", "brand", "graphic", "art",
        "marketing", "product", "ux", "ui",
    ],
    "vercel-react-best-practices": [
        "frontend", "developer", "web", "react", "javascript", "fullstack",
        "ui", "product",
    ],
    "vercel-web-design-guidelines": [
        "designer", "ui", "ux", "web", "frontend", "product", "developer",
        "creative",
    ],
    "vercel-composition-patterns": [
        "frontend", "developer", "web", "react", "javascript", "fullstack",
        "ui",
    ],
    "vercel-react-view-transitions": [
        "frontend", "developer", "designer", "web", "animation", "motion",
        "react", "ui", "creative",
    ],
    "vercel-deploy": [
        "developer", "devops", "engineer", "deployment", "frontend",
        "fullstack", "operations",
    ],

    # ── AI / Agentic ──────────────────────────────────────────────────────────
    "agentic-engineering": [
        "ai", "agent", "automation", "orchestration", "developer", "engineer",
        "llm", "commander", "platform", "workflow",
    ],
    "mcp-server-patterns": [
        "ai", "agent", "developer", "engineer", "platform", "tool",
        "integration", "orchestration", "llm",
    ],
    "continuous-agent-loop": [
        "ai", "agent", "automation", "orchestration", "commander", "workflow",
        "llm", "autonomous",
    ],
    "cost-aware-llm-pipeline": [
        "ai", "llm", "finance", "optimization", "engineer", "platform",
        "budget", "cost", "efficiency", "operations",
    ],
    "token-budget-advisor": [
        "ai", "llm", "optimization", "engineer", "platform", "budget",
        "cost", "operations",
    ],
    "context-budget": [
        "ai", "llm", "optimization", "engineer", "platform", "context",
        "memory",
    ],
    "safety-guard": [
        "safety", "ethics", "compliance", "risk", "governance", "legal",
        "ai", "security", "trust", "policy", "agent", "commander",
    ],
    "skill-creator": [
        "ai", "agent", "developer", "engineer", "platform", "automation",
        "commander", "optimization",
    ],
}


# ── Provider → domain keywords ────────────────────────────────────────────────
# Maps providers to the agent domain keywords they best serve.
# Matching: agent text contains ≥1 keyword → provider is recommended.
PROVIDER_KEYWORDS: dict[str, list[str]] = {
    "anthropic": [
        "write", "writing", "legal", "compliance", "content", "copy",
        "strategy", "research", "analysis", "analyst", "ethics", "policy",
        "counsel", "advisor", "consultant", "editorial", "narrative",
    ],
    "openai": [
        # General purpose — match everything as a base provider
        "general", "assistant", "manager", "specialist", "officer",
        "director", "executive", "coordinator", "lead",
    ],
    "gemini": [
        "multimodal", "video", "visual", "design", "creative", "3d",
        "image", "media", "graphic", "art", "animation", "production",
    ],
    "perplexity": [
        "research", "analyst", "seo", "intelligence", "market", "competitive",
        "journalist", "reporter", "news", "monitor", "insight",
    ],
    "deepseek": [
        "developer", "engineer", "code", "data", "math", "technical",
        "ml", "machine learning", "ai", "algorithm", "database",
    ],
    "xai": [
        "social", "media", "trend", "viral", "community", "growth",
        "influencer", "twitter", "x platform",
    ],
    "mistral": [
        "european", "gdpr", "france", "german", "spanish", "italian",
        "multilingual", "localization", "international",
    ],
    "cohere": [
        "knowledge", "search", "document", "enterprise", "customer",
        "support", "rag", "retrieval", "helpdesk",
    ],
    "groq": [
        "realtime", "speed", "fast", "live", "interactive", "streaming",
        "latency",
    ],
    "writer": [
        "brand", "copy", "copywriter", "content", "editorial", "pr",
        "communication", "marketing write", "campaign",
    ],
    "qwen": [
        "chinese", "china", "mandarin", "cantonese", "cjk", "asian",
        "localization", "translation", "multilingual",
    ],
    "amazon": [
        "aws", "cloud", "compliance", "enterprise", "hipaa", "healthcare",
        "government", "regulated",
    ],
    "nvidia": [
        "ml", "machine learning", "gpu", "model", "training", "inference",
        "deep learning", "neural",
    ],
}

# These providers are recommended for EVERY agent as base fallbacks
BASE_PROVIDERS = ["openai", "anthropic", "gemini"]


# ── Text extraction ───────────────────────────────────────────────────────────
def _agent_text(agent: dict) -> str:
    """Build a lowercase searchable text blob from all agent metadata fields."""
    parts = [
        agent.get("role", ""),
        agent.get("description", ""),
        agent.get("name", ""),
        agent.get("network", ""),
        " ".join(agent.get("capabilities", [])),
        " ".join(agent.get("tags", [])),
        agent.get("system_prompt", "")[:500],   # first 500 chars of system prompt
    ]
    return " ".join(p for p in parts if p).lower()


# ── Core matching ─────────────────────────────────────────────────────────────
def match_skills_for_agent(agent: dict) -> list[str]:
    """Return list of skill names that apply to this agent.

    Matching is purely keyword-based against the agent's metadata text —
    works for any agent_id, including custom agents built at runtime.
    """
    text = _agent_text(agent)
    matched = []
    for skill_name, keywords in SKILL_KEYWORDS.items():
        for kw in keywords:
            if kw in text:
                matched.append(skill_name)
                break
    return matched


def match_providers_for_agent(agent: dict) -> list[str]:
    """Return ordered list of recommended providers for this agent.

    Always includes BASE_PROVIDERS; prepends domain-specific providers
    that match the agent's role/description keywords.
    """
    text = _agent_text(agent)
    domain_providers = []
    for provider, keywords in PROVIDER_KEYWORDS.items():
        if provider in BASE_PROVIDERS:
            continue
        for kw in keywords:
            if kw in text:
                domain_providers.append(provider)
                break

    # Domain matches first, then base providers (deduped)
    seen: set[str] = set()
    result = []
    for p in domain_providers + BASE_PROVIDERS:
        if p not in seen:
            seen.add(p)
            result.append(p)
    return result


# ── Chunking helper ───────────────────────────────────────────────────────────
def _chunk_markdown(text: str, chunk_size: int = 350, overlap: int = 60) -> list[str]:
    # Strip YAML frontmatter
    if text.startswith("---"):
        end = text.find("---", 3)
        if end != -1:
            text = text[end + 3:].lstrip()

    paragraphs = re.split(r"\n{2,}", text)
    chunks, current = [], ""
    for para in paragraphs:
        words_in = len(para.split())
        if len(current.split()) + words_in > chunk_size and current:
            chunks.append(current.strip())
            overlap_words = current.split()[-overlap:]
            current = " ".join(overlap_words) + "\n\n" + para
        else:
            current += ("\n\n" if current else "") + para
    if current.strip():
        chunks.append(current.strip())
    return [c for c in chunks if len(c.split()) > 10]


def _doc_id(source: str, name: str) -> str:
    return hashlib.md5(f"{source}:{name}".encode()).hexdigest()[:16]


# ── ensure_agent_skills ───────────────────────────────────────────────────────
async def ensure_agent_skills(agent: dict, db: Any, skills_root: Path) -> int:
    """Upsert skill knowledge chunks for a single agent.

    Idempotent — safe to call on agent creation, on demand, or during
    bulk re-ingestion.  Returns number of new chunks inserted.
    """
    agent_id = agent.get("agent_id", "")
    if not agent_id:
        return 0

    matched_skills = match_skills_for_agent(agent)
    if not matched_skills:
        logger.debug(f"  {agent_id}: no skills matched")
        return 0

    now = datetime.now(timezone.utc)
    total_inserted = 0

    for skill_name in matched_skills:
        skill_md = skills_root / skill_name / "SKILL.md"
        if not skill_md.exists():
            continue

        content = skill_md.read_text(encoding="utf-8", errors="ignore")
        chunks = _chunk_markdown(content)
        if not chunks:
            continue

        doc_id = _doc_id("skill", skill_name)

        # Upsert: remove old, insert fresh
        await db.knowledge_chunks.delete_many({"agent_id": agent_id, "doc_id": doc_id})

        docs = [
            {
                "agent_id":    agent_id,
                "doc_id":      doc_id,
                "doc_title":   f"Skill: {skill_name}",
                "chunk_index": i,
                "text":        chunk_text,
                "source":      "skill",
                "skill_name":  skill_name,
                "pages":       [1],
                "created_at":  now,
            }
            for i, chunk_text in enumerate(chunks)
        ]
        await db.knowledge_chunks.insert_many(docs)
        total_inserted += len(docs)

    logger.info(
        f"  {agent_id}: {len(matched_skills)} skills → {total_inserted} chunks"
        f"  (role={agent.get('role','?')[:40]})"
    )
    return total_inserted


# ── ensure_provider_skills ────────────────────────────────────────────────────
async def ensure_provider_skills(agent: dict, db: Any) -> int:
    """Upsert provider knowledge chunks for a single agent based on its domain."""
    from data.provider_skills import PROVIDER_SKILLS

    agent_id = agent.get("agent_id", "")
    if not agent_id:
        return 0

    recommended_providers = match_providers_for_agent(agent)
    now = datetime.now(timezone.utc)
    total_inserted = 0

    for provider_name in recommended_providers:
        entry = PROVIDER_SKILLS.get(provider_name)
        if not entry:
            continue

        knowledge = entry.get("knowledge", "").strip()
        if not knowledge:
            continue

        doc_id = _doc_id("provider", provider_name)
        chunks = _chunk_markdown(knowledge)
        if not chunks:
            continue

        await db.knowledge_chunks.delete_many({
            "agent_id": agent_id,
            "doc_id":   doc_id,
            "source":   "provider_skill",
        })

        docs = [
            {
                "agent_id":      agent_id,
                "doc_id":        doc_id,
                "doc_title":     f"Provider Guide: {entry['display_name']}",
                "chunk_index":   i,
                "text":          chunk_text,
                "source":        "provider_skill",
                "provider_name": provider_name,
                "pages":         [1],
                "created_at":    now,
            }
            for i, chunk_text in enumerate(chunks)
        ]
        await db.knowledge_chunks.insert_many(docs)
        total_inserted += len(docs)

    return total_inserted
