"""{{expression}} autocomplete for the workflow editor.

When the user types `{{` into a node param input, the UI calls
`suggest(workflow_id, current_node_id, prefix)` and gets back a ranked
list of paths they could insert.

Two sources:
  1. Upstream node outputs from the most recent successful run of this
     workflow (real shapes, real field names). This beats n8n — they
     only have type hints, we have actual runtime shapes.
  2. Built-in context: $now, $today, $workflow.name, $run.id, trigger.*,
     $env.<allowlisted>.

If there's no prior run, we walk back to the upstream nodes and guess
from their tool's typical output shape (stub — keeps the list non-empty).
"""
from __future__ import annotations
import logging
from typing import Any

logger = logging.getLogger(__name__)


_BUILTIN_SUGGESTIONS = [
    {"path": "$now",            "kind": "builtin", "hint": "ISO timestamp of this execution"},
    {"path": "$today",          "kind": "builtin", "hint": "YYYY-MM-DD"},
    {"path": "$workflow.name",  "kind": "builtin", "hint": "This workflow's name"},
    {"path": "$run.id",         "kind": "builtin", "hint": "Current run_id"},
    {"path": "trigger.payload", "kind": "builtin", "hint": "Inbound webhook body"},
    {"path": "trigger.source",  "kind": "builtin", "hint": "manual|scheduled|webhook|email_reply|..."},
]


def _walk_dict(obj: Any, prefix: str = "", depth: int = 0) -> list[dict]:
    """Flatten a dict/list into leaf paths + their sample value preview."""
    out: list[dict] = []
    if depth > 4:
        return out
    if isinstance(obj, dict):
        for k, v in obj.items():
            p = f"{prefix}.{k}" if prefix else k
            if isinstance(v, (dict, list)) and v:
                out.append({"path": p, "kind": "object" if isinstance(v, dict) else "array",
                            "sample": None})
                out.extend(_walk_dict(v, p, depth + 1))
            else:
                preview = v
                if isinstance(preview, str) and len(preview) > 60:
                    preview = preview[:57] + "..."
                out.append({"path": p, "kind": type(v).__name__, "sample": preview})
    elif isinstance(obj, list) and obj:
        # Represent the first element's shape under [0]
        out.extend(_walk_dict(obj[0], f"{prefix}[0]", depth + 1))
    return out


async def _upstream_node_ids(workflow: dict, current_node_id: str) -> list[str]:
    """Rough upstream set: every node that eventually leads into
    current_node_id. Walks the inverse graph once."""
    nodes = workflow.get("nodes") or []
    by_id = {n["id"]: n for n in nodes}
    # Build inverse edges
    parents: dict[str, set[str]] = {n["id"]: set() for n in nodes}
    for n in nodes:
        for t in (n.get("next") or []):
            if t in parents: parents[t].add(n["id"])
        for t in (n.get("branch_yes") or []):
            if t in parents: parents[t].add(n["id"])
        for t in (n.get("branch_no") or []):
            if t in parents: parents[t].add(n["id"])
        for tl in (n.get("branches") or {}).values():
            for t in (tl or []):
                if t in parents: parents[t].add(n["id"])
    seen: set[str] = set()
    stack = list(parents.get(current_node_id, set()))
    while stack:
        nid = stack.pop()
        if nid in seen:
            continue
        seen.add(nid)
        stack.extend(parents.get(nid, set()))
    return [nid for nid in seen if nid in by_id]


async def suggest(
    workflow_id: str,
    current_node_id: str,
    prefix: str = "",
    user_id: str = "",
) -> list[dict[str, Any]]:
    """Return ranked suggestions for a {{expression}} under current_node_id."""
    from db import db
    workflow = await db.workflows.find_one({"workflow_id": workflow_id}, {"_id": 0})
    if not workflow:
        return []
    upstream = await _upstream_node_ids(workflow, current_node_id)

    # Most recent successful run's state — real runtime shapes
    recent = await db.workflow_runs.find_one(
        {"workflow_id": workflow_id, "status": "completed"},
        {"_id": 0, "state": 1},
        sort=[("finished_at", -1)],
    )
    state = (recent or {}).get("state") or {}

    suggestions: list[dict] = []
    for nid in upstream:
        node_state = state.get(nid)
        if not isinstance(node_state, dict):
            # No data for this node; provide the top-level ref so user can
            # still wire it.
            suggestions.append({"path": nid, "kind": "node", "sample": None,
                                "from_node": nid, "stale": True})
            continue
        for leaf in _walk_dict(node_state, prefix=nid):
            leaf["from_node"] = nid
            leaf["stale"] = False
            suggestions.append(leaf)

    suggestions.extend(_BUILTIN_SUGGESTIONS)

    # Rank: prefix match first, then non-stale, then shorter paths
    p = (prefix or "").strip().lower()

    def _score(s):
        score = 0
        path = s.get("path", "").lower()
        if p and path.startswith(p):
            score -= 100
        elif p and p in path:
            score -= 50
        if s.get("stale"):
            score += 5
        score += len(path) * 0.1
        return score

    suggestions.sort(key=_score)
    return suggestions[:40]
