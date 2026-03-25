"""MAARS — Memory: Semantic Memory Layer.
Bridges episodic memory and the knowledge graph to provide
contextual, relationship-aware memory retrieval for agents.

Semantic memory answers: "What do I know about X?"
- Combines episodic events (what happened) with knowledge graph entities (what exists)
- Provides relevance-scored context for agent task execution
- Supports concept association and cross-agent learning
"""

from datetime import datetime, timezone
from db import db

SEM_COLLECTION = "memory_semantic"
SEM_CONCEPTS = "semantic_concepts"


async def store_concept(
    concept: str,
    concept_type: str,
    description: str,
    source_agent: str = "system",
    related_entities: list = None,
    confidence: float = 1.0,
    tags: list = None,
):
    """Store or update a semantic concept — a high-level understanding derived
    from episodic events and knowledge graph entities."""
    now = datetime.now(timezone.utc).isoformat()
    await db[SEM_CONCEPTS].update_one(
        {"concept": concept},
        {
            "$set": {
                "concept_type": concept_type,
                "description": description,
                "source_agent": source_agent,
                "related_entities": related_entities or [],
                "confidence": confidence,
                "tags": tags or [],
                "access_count": 0,
                "updated_at": now,
            },
            "$setOnInsert": {"created_at": now},
            "$inc": {"version": 1},
        },
        upsert=True,
    )
    return {
        "concept": concept,
        "concept_type": concept_type,
        "status": "stored",
    }


async def query_semantic(
    query: str,
    agent_id: str = None,
    concept_type: str = None,
    limit: int = 10,
):
    """Query semantic memory — searches concepts, episodic memories,
    and knowledge graph entities for the most relevant context."""
    results = {"concepts": [], "episodes": [], "entities": [], "relevance_summary": ""}

    # 1. Search semantic concepts
    concept_filter = {"$or": [
        {"concept": {"$regex": query, "$options": "i"}},
        {"description": {"$regex": query, "$options": "i"}},
        {"tags": {"$regex": query, "$options": "i"}},
    ]}
    if concept_type:
        concept_filter["concept_type"] = concept_type
    concepts = await db[SEM_CONCEPTS].find(concept_filter, {"_id": 0}).sort("confidence", -1).limit(limit).to_list(length=limit)
    results["concepts"] = concepts

    # Bump access count for retrieved concepts
    concept_names = [c["concept"] for c in concepts]
    if concept_names:
        await db[SEM_CONCEPTS].update_many(
            {"concept": {"$in": concept_names}},
            {"$inc": {"access_count": 1}},
        )

    # 2. Search episodic memory
    ep_filter = {"$or": [
        {"event_data": {"$regex": query, "$options": "i"}},
        {"lessons_learned": {"$regex": query, "$options": "i"}},
    ]}
    if agent_id:
        ep_filter["agent_id"] = agent_id
    episodes = await db["memory_episodic"].find(ep_filter, {"_id": 0}).sort("timestamp", -1).limit(limit).to_list(length=limit)
    results["episodes"] = episodes

    # 3. Search knowledge graph entities
    kg_filter = {"$or": [
        {"entity": {"$regex": query, "$options": "i"}},
        {"entity_type": {"$regex": query, "$options": "i"}},
    ]}
    entities = await db["knowledge_graph"].find(kg_filter, {"_id": 0}).limit(limit).to_list(length=limit)
    results["entities"] = entities

    results["relevance_summary"] = (
        f"Found {len(concepts)} concepts, {len(episodes)} episodes, "
        f"{len(entities)} entities for query '{query}'"
    )
    return results


async def build_agent_context(agent_id: str, task_description: str, limit: int = 5):
    """Build a rich semantic context for an agent about to execute a task.
    This is the primary integration point with the 13-step runtime loop."""

    # Semantic concepts related to task
    sem_results = await query_semantic(task_description, agent_id=agent_id, limit=limit)

    # Agent's own lessons
    agent_lessons = await db["memory_episodic"].find(
        {"agent_id": agent_id, "lessons_learned": {"$ne": ""}},
        {"_id": 0},
    ).sort("timestamp", -1).limit(3).to_list(length=3)

    # Cross-agent lessons for similar tasks
    cross_lessons = await db["memory_episodic"].find(
        {"lessons_learned": {"$regex": task_description[:30], "$options": "i"}},
        {"_id": 0},
    ).sort("timestamp", -1).limit(2).to_list(length=2)

    context_parts = []
    if sem_results["concepts"]:
        top = sem_results["concepts"][:3]
        context_parts.append(
            "Relevant concepts: " + "; ".join(c["description"][:100] for c in top)
        )
    if agent_lessons:
        lessons = [e["lessons_learned"] for e in agent_lessons if e.get("lessons_learned")]
        if lessons:
            context_parts.append("Past lessons: " + "; ".join(lessons[:2]))
    if cross_lessons:
        cross = [e["lessons_learned"] for e in cross_lessons if e.get("lessons_learned")]
        if cross:
            context_parts.append("Cross-agent insights: " + "; ".join(cross[:2]))
    if sem_results["entities"]:
        ents = [e["entity"] for e in sem_results["entities"][:3]]
        context_parts.append("Related entities: " + ", ".join(ents))

    return {
        "semantic_context": " | ".join(context_parts) if context_parts else "No prior semantic context",
        "concepts_found": len(sem_results["concepts"]),
        "episodes_found": len(sem_results["episodes"]),
        "entities_found": len(sem_results["entities"]),
        "agent_lessons": len(agent_lessons),
        "cross_agent_lessons": len(cross_lessons),
    }


async def extract_concepts_from_execution(
    agent_id: str,
    task_description: str,
    output: str,
    model_used: str,
    tags: list = None,
):
    """After an agent execution, extract and store semantic concepts.
    Called during the memory update step of the runtime loop."""
    # Derive a concept name from the task
    concept_name = task_description[:80].strip()
    concept_type = "task_knowledge"

    await store_concept(
        concept=concept_name,
        concept_type=concept_type,
        description=f"Executed by {agent_id} using {model_used}. Output preview: {output[:200]}",
        source_agent=agent_id,
        related_entities=[agent_id, model_used],
        confidence=0.8,
        tags=tags or [],
    )
    return {"concept": concept_name, "stored": True}


async def get_concept(concept: str):
    """Get a single concept by name."""
    doc = await db[SEM_CONCEPTS].find_one({"concept": concept}, {"_id": 0})
    return doc


async def get_semantic_stats():
    """Get semantic memory statistics."""
    total_concepts = await db[SEM_CONCEPTS].count_documents({})
    type_pipeline = [
        {"$group": {"_id": "$concept_type", "count": {"$sum": 1}}},
        {"$project": {"_id": 0, "type": "$_id", "count": 1}},
    ]
    types = await db[SEM_CONCEPTS].aggregate(type_pipeline).to_list(length=50)
    top_accessed = await db[SEM_CONCEPTS].find(
        {}, {"_id": 0, "concept": 1, "access_count": 1, "concept_type": 1}
    ).sort("access_count", -1).limit(5).to_list(length=5)

    return {
        "total_concepts": total_concepts,
        "concept_types": types,
        "top_accessed": top_accessed,
    }
