"""MAARS — Intelligence: Citation & Provenance Engine."""

from datetime import datetime, timezone
from db import db

CITATION_COLLECTION = "citations"


async def create_citation(claim: str, sources: list, confidence: float, verified: bool = False):
    """Create a citation record linking a claim to its sources."""
    citation = {
        "claim": claim,
        "sources": sources,
        "confidence": confidence,
        "verified": verified,
        "status": "verified" if verified else "unverified",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db[CITATION_COLLECTION].insert_one(citation)
    citation.pop("_id", None)
    return citation


async def get_citations(verified_only: bool = False, limit: int = 50):
    """Retrieve citations."""
    query = {}
    if verified_only:
        query["verified"] = True
    cursor = db[CITATION_COLLECTION].find(query, {"_id": 0}).sort("created_at", -1).limit(limit)
    return await cursor.to_list(length=limit)
