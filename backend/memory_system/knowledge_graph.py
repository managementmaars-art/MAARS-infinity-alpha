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


async def traverse_graph(start_entity: str, max_depth: int = 3, relationship_filter: str = None):
    """Traverse the knowledge graph from a starting entity, exploring relationships up to max_depth."""
    visited = set()
    result = {"root": start_entity, "nodes": [], "edges": [], "depth_reached": 0}

    async def _traverse(entity_name, depth):
        if depth > max_depth or entity_name in visited:
            return
        visited.add(entity_name)
        result["depth_reached"] = max(result["depth_reached"], depth)

        doc = await db[KG_COLLECTION].find_one({"entity": entity_name}, {"_id": 0})
        if not doc:
            return

        result["nodes"].append({
            "entity": doc["entity"], "entity_type": doc.get("entity_type", "unknown"),
            "attributes": doc.get("attributes", {}), "depth": depth,
        })

        for rel in doc.get("relationships", []):
            if relationship_filter and rel["relationship_type"] != relationship_filter:
                continue
            result["edges"].append({
                "source": entity_name, "target": rel["target"],
                "relationship": rel["relationship_type"], "weight": rel.get("weight", 1.0),
            })
            await _traverse(rel["target"], depth + 1)

    await _traverse(start_entity, 0)
    return result


async def search_entities(query: str, limit: int = 20):
    """Search entities by name or attribute values (fuzzy text matching)."""
    pipeline = [
        {"$match": {"$or": [
            {"entity": {"$regex": query, "$options": "i"}},
            {"entity_type": {"$regex": query, "$options": "i"}},
        ]}},
        {"$project": {"_id": 0}},
        {"$limit": limit},
    ]
    results = await db[KG_COLLECTION].aggregate(pipeline).to_list(length=limit)
    return results


async def find_paths(source: str, target: str, max_depth: int = 4):
    """Find paths between two entities in the graph."""
    paths = []

    async def _dfs(current, target_name, visited, path):
        if current == target_name:
            paths.append(list(path))
            return
        if len(path) > max_depth:
            return
        doc = await db[KG_COLLECTION].find_one({"entity": current}, {"_id": 0})
        if not doc:
            return
        for rel in doc.get("relationships", []):
            next_entity = rel["target"]
            if next_entity not in visited:
                visited.add(next_entity)
                path.append({"entity": next_entity, "via": rel["relationship_type"]})
                await _dfs(next_entity, target_name, visited, path)
                path.pop()
                visited.discard(next_entity)

    await _dfs(source, target, {source}, [{"entity": source, "via": "start"}])
    return {"source": source, "target": target, "paths": paths[:10], "paths_found": len(paths)}
