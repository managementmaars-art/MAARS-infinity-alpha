"""MAARS — Memory: Knowledge Graph. Entity-relationship graph with provenance."""

from datetime import datetime, timezone
from db import db

KG_COLLECTION = "knowledge_graph"


async def add_entity(entity: str, entity_type: str, attributes: dict = None, source: str = "system"):
    """Add or update an entity in the knowledge graph."""
    now = datetime.now(timezone.utc).isoformat()
    await db[KG_COLLECTION].update_one(
        {"entity": entity},
        {"$set": {
            "entity_type": entity_type, "attributes": attributes or {},
            "provenance": source, "freshness_score": 1.0,
            "last_verified": now, "updated_at": now,
        }, "$setOnInsert": {"relationships": [], "created_at": now}},
        upsert=True,
    )
    return {"entity": entity, "entity_type": entity_type}


async def add_relationship(entity: str, target: str, relationship_type: str, weight: float = 1.0, source: str = "system"):
    """Add a relationship between two entities."""
    rel = {
        "target": target, "relationship_type": relationship_type,
        "weight": weight, "source": source,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db[KG_COLLECTION].update_one(
        {"entity": entity},
        {"$push": {"relationships": rel}},
    )
    return {"entity": entity, "target": target, "relationship_type": relationship_type}


async def get_entity(entity: str):
    """Get an entity and all its relationships."""
    doc = await db[KG_COLLECTION].find_one({"entity": entity}, {"_id": 0})
    return doc


async def query_graph(entity_type: str = None, relationship_type: str = None, limit: int = 50):
    """Query the knowledge graph."""
    query = {}
    if entity_type:
        query["entity_type"] = entity_type
    if relationship_type:
        query["relationships.relationship_type"] = relationship_type
    cursor = db[KG_COLLECTION].find(query, {"_id": 0}).limit(limit)
    return await cursor.to_list(length=limit)


async def get_graph_stats():
    """Get knowledge graph statistics."""
    total_entities = await db[KG_COLLECTION].count_documents({})
    pipeline = [{"$unwind": "$relationships"}, {"$count": "total"}]
    rel_count = await db[KG_COLLECTION].aggregate(pipeline).to_list(length=1)
    total_rels = rel_count[0]["total"] if rel_count else 0
    type_pipeline = [{"$group": {"_id": "$entity_type", "count": {"$sum": 1}}}, {"$project": {"_id": 0, "type": "$_id", "count": 1}}]
    types = await db[KG_COLLECTION].aggregate(type_pipeline).to_list(length=50)
    return {"total_entities": total_entities, "total_relationships": total_rels, "entity_types": types}
