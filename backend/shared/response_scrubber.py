"""Client-facing response scrubber — keeps infrastructure invisible.

The whole product is sold as "MAARS AI Gateway"; clients should never
see which specific LLM/image/TTS/lead provider actually served them.
This module:

  1. Removes provider names from any dict before it's returned to a
     non-admin client (e.g. `provider: "pollinations"` → gone).
  2. Removes raw USD costs (clients see credits, not dollars).
  3. Neutralizes enhancement metadata that reveals the enhancer model.
  4. Replaces internal provider fields with "maars" so the response
     still has a `provider` key (existing clients may depend on its
     presence) but the value is always the MAARS brand.

Use `scrub(data)` on any response dict before returning from a
client-facing route. Admin routes should NOT use this — operators
need the full picture.

The scrub is intentionally conservative: only masks the specific
fields that identify infrastructure. Business content (names, emails,
generated text, lead data) passes through untouched.
"""
from __future__ import annotations
from typing import Any

# Every key that leaks infrastructure identity. Anything in this set is
# either removed or replaced with the MAARS brand.
_INFRA_KEYS_MASK = {
    # Provider + model names in any casing
    "provider", "model", "model_id", "model_name",
    "provider_slug", "provider_name", "provider_id",
    "platform_provider", "backend_provider",
    "enhancer_model", "routing_reason", "router_reason",
    "llm_provider", "llm_model",
    # Raw costs — clients see credits, not $
    "cost_usd", "cost_usd_raw", "provider_cost_usd",
    "input_cost_usd", "output_cost_usd",
    "cost_per_credit",   # this is the $/credit operator cost basis
    "internal_cost_usd",
    # Internal routing debug signals
    "attempt_count", "attempts", "fallback_chain", "chain",
    "selected_provider", "fallback_from",
}

# Fields we REPLACE (not drop) because existing clients may check for
# their presence. Every replacement is the neutral MAARS brand.
_INFRA_REPLACEMENTS = {
    "provider": "maars",
    "model": "maars/auto",
    "provider_name": "MAARS",
}


def _scrub_value(value: Any) -> Any:
    """Recursively scrub lists and dicts."""
    if isinstance(value, dict):
        return scrub(value)
    if isinstance(value, list):
        return [_scrub_value(v) for v in value]
    return value


def scrub(data: Any, *, keep_keys: set[str] | None = None) -> Any:
    """Return a copy of `data` with infrastructure-identifying fields
    masked. Safe on any shape (dict, list, scalar).

    `keep_keys` is an opt-in escape hatch for routes that need to
    preserve specific fields (e.g. an admin endpoint wrapping a
    shared helper).
    """
    if data is None:
        return None
    if isinstance(data, list):
        return [_scrub_value(v) for v in data]
    if not isinstance(data, dict):
        return data
    keep = keep_keys or set()
    out: dict[str, Any] = {}
    for k, v in data.items():
        if k in keep:
            out[k] = _scrub_value(v)
            continue
        if k in _INFRA_REPLACEMENTS:
            out[k] = _INFRA_REPLACEMENTS[k]
            continue
        if k in _INFRA_KEYS_MASK:
            # drop — client doesn't need this field at all
            continue
        out[k] = _scrub_value(v)
    return out


def scrub_meta(meta: dict) -> dict:
    """Specialized version for media-router meta dicts. Keeps the
    keys clients genuinely use (wall_s, cost_credits, dimensions)
    but drops provider/model/cost_usd/chain."""
    if not isinstance(meta, dict):
        return {}
    allowed = {
        "wall_s", "wall_ms", "duration_s",
        "cost_credits", "credits_charged",
        "width", "height", "size",
        "quality",
        "mime_type", "format",
        "content_type",
    }
    out = {}
    for k, v in meta.items():
        if k in allowed:
            out[k] = v
        elif k == "prompt_enhancement":
            # Preserve the fact that enhancement happened, but drop the
            # enhancer model name. Clients see "enhanced: true" only.
            if isinstance(v, dict):
                # prompt_enhancer writes both `ok` (success) and `enhanced`
                # (legacy). Either truthy means enhancement ran.
                out["enhanced"] = bool(v.get("enhanced") or v.get("ok"))
    return out
