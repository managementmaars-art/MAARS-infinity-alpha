"""Structured output — force JSON-schema-conformant responses.

Every provider offers some flavor of "return JSON that matches this
schema." OpenAI has `response_format={"type":"json_schema",...}`,
Anthropic does it via tools (force a single-tool call), Gemini via
`responseMimeType: application/json` + `responseSchema`.

If we DON'T use these knobs, we get free-text JSON that sometimes
looks right and sometimes has a trailing comma. Every call that asks
for "respond in JSON" without schema enforcement wastes money on the
retry.

This module:

  1. Translates a JSON schema dict into the right provider-specific
     parameter bag.
  2. Validates response against the schema on the way back and — if
     invalid — issues one repair call ("The previous response failed
     validation because X. Fix it.") before giving up.

Usage from llm_gateway / caller:

    params = structured_output.build_params(schema, provider="openai")
    params["model"] = "gpt-4o"
    # dispatch with these params; caller handles the response.
"""
from __future__ import annotations
import json
import logging
from typing import Any

logger = logging.getLogger(__name__)


def build_params(schema: dict, *, provider: str, model: str = "") -> dict[str, Any]:
    """Return provider-specific request fields to force schema-conformant output."""
    provider = (provider or "").lower()
    if provider == "openai":
        return {
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": schema.get("title", "response"),
                    "strict": True,
                    "schema": schema,
                },
            },
        }
    if provider in ("gemini", "google"):
        return {
            "generationConfig": {
                "responseMimeType": "application/json",
                "responseSchema": schema,
            },
        }
    if provider == "anthropic":
        # Anthropic enforces via single-tool forcing.
        return {
            "tools": [{
                "name": schema.get("title", "respond"),
                "description": schema.get("description", "Structured response"),
                "input_schema": schema,
            }],
            "tool_choice": {"type": "tool", "name": schema.get("title", "respond")},
        }
    if provider in ("groq", "cerebras", "fireworks", "together", "nvidia", "nvidia_nim"):
        # These speak OpenAI-compat; many support json_object but not strict schema.
        return {"response_format": {"type": "json_object"}}
    # Unknown provider → best-effort: ask for json via the system prompt (caller handles).
    return {}


def validate(response_text: str, schema: dict) -> tuple[bool, str]:
    """Return (ok, reason). Uses `jsonschema` if installed; otherwise a
    minimal shape check (required keys exist).
    """
    try:
        obj = json.loads(response_text)
    except json.JSONDecodeError as exc:
        return False, f"invalid_json: {exc}"

    try:
        import jsonschema
        try:
            jsonschema.validate(obj, schema)
            return True, "ok"
        except jsonschema.ValidationError as exc:
            return False, f"schema_violation: {exc.message[:200]}"
    except ImportError:
        pass

    required = schema.get("required") or []
    if isinstance(obj, dict):
        missing = [k for k in required if k not in obj]
        if missing:
            return False, f"missing_keys: {missing}"
        return True, "ok"
    if schema.get("type") == "array" and isinstance(obj, list):
        return True, "ok"
    return False, "type_mismatch"


async def enforce(
    *,
    complete_fn,
    user_id: str,
    messages: list[dict],
    schema: dict,
    model: str = "maars/auto",
    source: str = "structured_output",
) -> dict[str, Any]:
    """One-shot with repair: call, validate, if invalid issue a repair call.
    Returns the final parsed JSON on success; raises ValueError on double
    failure. Caller gets the full response dict in `_response`.
    """
    # Inject schema hint into system prompt as belt-and-braces.
    schema_hint = (
        "You MUST respond with ONLY JSON that matches this schema:\n"
        f"{json.dumps(schema, indent=2)}"
    )
    primed = [*messages]
    if primed and primed[0].get("role") == "system":
        primed[0] = {**primed[0], "content": primed[0]["content"] + "\n\n" + schema_hint}
    else:
        primed.insert(0, {"role": "system", "content": schema_hint})

    # First attempt.
    r = await complete_fn(
        user_id, messages=primed, model=model,
        temperature=0.0, max_tokens=2048,
        source=source, enable_cache=False, verify_injection=False,
    )
    text = r["choices"][0]["message"]["content"]
    ok, reason = validate(text, schema)
    if ok:
        r.setdefault("maars", {})["structured"] = {"validated": True}
        return {"parsed": json.loads(text), "_response": r}

    # Repair.
    repair_messages = [
        *primed,
        {"role": "assistant", "content": text},
        {"role": "user", "content": f"Your previous JSON was invalid: {reason}. Return ONLY corrected JSON."},
    ]
    r2 = await complete_fn(
        user_id, messages=repair_messages, model=model,
        temperature=0.0, max_tokens=2048,
        source=f"{source}_repair", enable_cache=False, verify_injection=False,
    )
    text2 = r2["choices"][0]["message"]["content"]
    ok2, reason2 = validate(text2, schema)
    if ok2:
        r2.setdefault("maars", {})["structured"] = {"validated": True, "repaired": True}
        return {"parsed": json.loads(text2), "_response": r2}
    raise ValueError(f"structured_output repair failed: {reason} → {reason2}")
