"""Admin endpoints for Agent Offices.

Surfaces: list offices by department, read a single office, trigger a
full-seed, run an office SOP against a sample request.
"""
from __future__ import annotations
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from auth import require_admin
from models.schemas import User

router = APIRouter()


@router.get("/admin/offices/departments")
async def offices_by_department(_: User = Depends(require_admin)):
    """High-level overview: offices per department + sample agents."""
    from services.agents.agent_office import list_departments
    return {"departments": await list_departments()}


@router.get("/admin/offices")
async def list_offices(
    department: Optional[str] = None,
    _: User = Depends(require_admin),
):
    """List every office, optionally filtered by department."""
    from services.agents.agent_office import list_by_department
    return {"offices": await list_by_department(department)}


@router.get("/admin/offices/{agent_id}")
async def get_office(agent_id: str, _: User = Depends(require_admin)):
    """Read one office in full."""
    from services.agents.agent_office import get
    from db import db
    office = await get(agent_id)
    if not office:
        raise HTTPException(404, f"no office for agent {agent_id}")
    # Count training examples from golden_examples for this agent
    golden_count = await db.agent_golden_examples.count_documents(
        {"scope_value": agent_id}
    )
    doc = office.to_doc()
    doc["training_examples_count"] = golden_count
    return doc


class _SeedBody(BaseModel):
    force_rebuild: bool = False


@router.post("/admin/offices/seed")
async def seed_offices(body: _SeedBody, _: User = Depends(require_admin)):
    """Bulk-seed offices for every agent. Safe to run repeatedly —
    existing offices are skipped unless force_rebuild=True."""
    from services.agents.office_seeder import seed_all_offices
    res = await seed_all_offices(force_rebuild=body.force_rebuild)
    return {"ok": True, **res}


class _RunSopBody(BaseModel):
    agent_id: str
    user_request: str
    context: dict | None = None
    dry_run: bool = False


@router.post("/admin/offices/run-sop")
async def run_sop(body: _RunSopBody, current: User = Depends(require_admin)):
    """Exercise an office's SOP on a sample request. Useful for testing
    agent training before the operator ships the agent to a client."""
    from services.agents.agent_office import get, run_sop
    office = await get(body.agent_id)
    if not office:
        raise HTTPException(404, f"no office for agent {body.agent_id}")
    res = await run_sop(
        office, body.user_request,
        user_id=current.user_id,
        context=body.context,
        dry_run=body.dry_run,
    )
    return res
