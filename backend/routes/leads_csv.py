"""CSV lead import/export — operators with existing lists need this
on day 1. Uploads get normalized into the same shape apollo.search_people
returns, so campaign_orchestrator consumes them transparently.
"""
from __future__ import annotations
import csv
import io
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from auth import get_current_user
from models.schemas import User

router = APIRouter()


# Mapping from common CSV header names → our canonical field.
# Handles exports from Apollo, Hunter, Sales Navigator, Seamless, Lusha.
_HEADER_ALIASES = {
    "email":           "email",
    "email address":   "email",
    "primary email":   "email",
    "work email":      "email",
    "first name":      "first_name",
    "firstname":       "first_name",
    "first":           "first_name",
    "last name":       "last_name",
    "lastname":        "last_name",
    "last":            "last_name",
    "full name":       "name",
    "name":            "name",
    "title":           "title",
    "position":        "title",
    "job title":       "title",
    "company":         "company",
    "company name":    "company",
    "organization":    "company",
    "linkedin":        "linkedin_url",
    "linkedin url":    "linkedin_url",
    "linkedin profile":"linkedin_url",
    "phone":           "phone",
    "phone number":    "phone",
    "mobile":          "phone",
}


def _normalize_row(raw: dict) -> dict:
    """Map arbitrary CSV headers to our canonical schema."""
    out: dict = {}
    for k, v in raw.items():
        key = (k or "").strip().lower()
        canonical = _HEADER_ALIASES.get(key)
        if canonical and v:
            out[canonical] = v.strip() if isinstance(v, str) else v
    # Derive name if only first+last provided
    if "name" not in out and ("first_name" in out or "last_name" in out):
        out["name"] = f"{out.get('first_name','')} {out.get('last_name','')}".strip()
    # Nest company under organization to match apollo shape
    if "company" in out:
        out["organization"] = {"name": out.pop("company")}
    return out


@router.post("/leads/import-csv")
async def import_csv(
    file: UploadFile = File(...),
    list_name: str | None = None,
    current_user: User = Depends(get_current_user),
):
    """Upload a CSV of leads. Returns the parsed + normalized list
    and stores it in `imported_lead_lists` for reuse across campaigns."""
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(400, "CSV required")
    content = (await file.read()).decode("utf-8-sig", errors="replace")
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(413, "CSV too large (max 10MB)")

    reader = csv.DictReader(io.StringIO(content))
    normalized = []
    for row in reader:
        person = _normalize_row(row)
        if person.get("email"):
            normalized.append(person)

    if not normalized:
        raise HTTPException(400, "No rows with email addresses found. Check your CSV headers — we look for 'email' / 'email address' / 'primary email' / 'work email'.")

    from db import db
    list_id = f"leadlist_{uuid.uuid4().hex[:12]}"
    await db.imported_lead_lists.insert_one({
        "list_id": list_id,
        "user_id": current_user.user_id,
        "name": list_name or (file.filename or "Imported list"),
        "row_count": len(normalized),
        "leads": normalized,
        "imported_at": datetime.now(timezone.utc).isoformat(),
        "_id": None,
    })
    return {
        "ok": True,
        "list_id": list_id,
        "row_count": len(normalized),
        "preview": normalized[:3],
    }


@router.get("/leads/lists")
async def list_imported_lists(current_user: User = Depends(get_current_user)):
    from db import db
    docs = await db.imported_lead_lists.find(
        {"user_id": current_user.user_id},
        {"_id": 0, "leads": 0},
    ).sort("imported_at", -1).to_list(100)
    return {"object": "list", "data": docs}


@router.get("/leads/lists/{list_id}/export")
async def export_list(list_id: str, current_user: User = Depends(get_current_user)):
    """Export a stored list as CSV. Returns text/csv with a download
    filename."""
    from db import db
    doc = await db.imported_lead_lists.find_one(
        {"list_id": list_id, "user_id": current_user.user_id},
    )
    if not doc:
        raise HTTPException(404, "not found")
    buf = io.StringIO()
    fieldnames = ["email", "first_name", "last_name", "name", "title", "company", "linkedin_url", "phone"]
    writer = csv.DictWriter(buf, fieldnames=fieldnames)
    writer.writeheader()
    for p in doc.get("leads", []):
        row = {
            "email": p.get("email"),
            "first_name": p.get("first_name"),
            "last_name": p.get("last_name"),
            "name": p.get("name"),
            "title": p.get("title"),
            "company": (p.get("organization") or {}).get("name"),
            "linkedin_url": p.get("linkedin_url"),
            "phone": p.get("phone"),
        }
        writer.writerow(row)
    buf.seek(0)
    return StreamingResponse(
        iter([buf.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{list_id}.csv"'},
    )
