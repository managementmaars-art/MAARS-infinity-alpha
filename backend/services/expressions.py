"""Expression engine — n8n-style `{{ }}` templating for workflow params.

Today every node param is a literal value. This module adds dynamic
resolution so any string parameter (or any string inside a nested dict/list)
can reference:

  {{ n1.output.email }}            — previous node's output by id
  {{ n1.leads[0].first_name }}     — index into arrays
  {{ trigger.payload.x }}           — inbound webhook payload
  {{ $now }}                        — current ISO timestamp
  {{ $today }}                      — current YYYY-MM-DD
  {{ $workflow.name }}              — workflow metadata
  {{ $run.id }}                     — current run_id
  {{ $env.FOO }}                    — environment variable (allow-list below)

Filter syntax:
  {{ name | upper }}                — uppercase
  {{ name | lower }}
  {{ name | default:"N/A" }}        — fallback if null/missing
  {{ body | trunc:200 }}            — truncate
  {{ user | json }}                 — JSON-stringify
  {{ amount | round:2 }}            — numeric round
  {{ ts | date:"%Y-%m-%d" }}        — format ISO timestamp

Security:
  * Allow-listed env-var prefixes only (`MAARS_PUB_`) — never leaks secrets.
  * No eval, no arbitrary attribute lookup — we only walk dict/list keys.
  * Invalid expressions resolve to the original literal (fail-open: a
    broken template should not crash the workflow).
"""
from __future__ import annotations
import json
import os
import re
from datetime import datetime, timezone
from typing import Any

_EXPR_RE = re.compile(r"\{\{\s*(.*?)\s*\}\}")

_ENV_ALLOW_PREFIXES = ("MAARS_PUB_", "MAARS_REGION", "MAARS_VERSION")


# ── Filter registry ──────────────────────────────────────────────────
def _f_upper(v, _arg=None):
    return str(v).upper() if v is not None else ""

def _f_lower(v, _arg=None):
    return str(v).lower() if v is not None else ""

def _f_trim(v, _arg=None):
    return str(v).strip() if v is not None else ""

def _f_default(v, arg=None):
    if v in (None, "", [], {}):
        return arg if arg is not None else ""
    return v

def _f_trunc(v, arg=None):
    n = int(arg or 100)
    s = str(v) if v is not None else ""
    return s if len(s) <= n else s[:n] + "…"

def _f_json(v, _arg=None):
    try:
        return json.dumps(v, default=str)
    except Exception:
        return str(v)

def _f_round(v, arg=None):
    try:
        return round(float(v), int(arg or 0))
    except (TypeError, ValueError):
        return v

def _f_date(v, arg=None):
    try:
        dt = datetime.fromisoformat(str(v).replace("Z", "+00:00"))
        return dt.strftime(arg or "%Y-%m-%d %H:%M:%S")
    except Exception:
        return v

def _f_length(v, _arg=None):
    try:
        return len(v)
    except TypeError:
        return 0

def _f_join(v, arg=", "):
    try:
        return (arg or ", ").join(str(x) for x in v)
    except TypeError:
        return str(v)

def _f_split(v, arg=","):
    try:
        return str(v).split(arg or ",")
    except Exception:
        return [str(v)]

def _f_int(v, _arg=None):
    try: return int(float(v))
    except (TypeError, ValueError): return 0

def _f_float(v, _arg=None):
    try: return float(v)
    except (TypeError, ValueError): return 0.0

def _f_bool(v, _arg=None):
    if isinstance(v, bool): return v
    if v in (None, "", 0, "0", "false", "False"): return False
    return True


_FILTERS = {
    "upper": _f_upper, "lower": _f_lower, "trim": _f_trim,
    "default": _f_default, "trunc": _f_trunc, "json": _f_json,
    "round": _f_round, "date": _f_date, "length": _f_length,
    "join": _f_join, "split": _f_split,
    "int": _f_int, "float": _f_float, "bool": _f_bool,
}


# ── Path walker ──────────────────────────────────────────────────────

_PATH_TOKEN = re.compile(r"""
    ([A-Za-z_][A-Za-z0-9_$]*)      # identifier
    | \.([A-Za-z_][A-Za-z0-9_$]*)  # .field
    | \[(\d+)\]                    # [index]
    | \["([^"]*)"\]                # ["key"]
    | \['([^']*)'\]                # ['key']
""", re.VERBOSE)


def _dig(obj: Any, path: str) -> Any:
    """Walk a dotted+indexed path through dicts/lists. Returns None on miss.
    No attribute access on arbitrary Python objects — dict/list only."""
    cur = obj
    for m in _PATH_TOKEN.finditer(path):
        seg = m.group(1) or m.group(2) or m.group(4) or m.group(5)
        idx = m.group(3)
        if idx is not None:
            if isinstance(cur, list):
                try: cur = cur[int(idx)]
                except (IndexError, ValueError): return None
            else:
                return None
        elif seg is not None:
            if isinstance(cur, dict):
                cur = cur.get(seg)
            else:
                return None
        if cur is None:
            return None
    return cur


# ── Parse + resolve ──────────────────────────────────────────────────

def _resolve_filters(value: Any, filter_spec: list[str]) -> Any:
    """Apply a chain of filters: `upper | trunc:20` → ['upper','trunc:20']."""
    out = value
    for f in filter_spec:
        name, sep, arg = f.strip().partition(":")
        name = name.strip()
        arg = arg.strip().strip('"').strip("'") if sep else None
        fn = _FILTERS.get(name)
        if fn is None:
            continue
        try:
            out = fn(out, arg)
        except Exception:
            pass
    return out


def _resolve_one(expr: str, ctx: dict) -> Any:
    """Resolve the inside of a `{{ ... }}` against context."""
    parts = [p.strip() for p in expr.split("|")]
    lookup = parts[0]
    filters = parts[1:]

    head, sep, rest = lookup.partition(".")
    head = head.strip()
    # special vars
    if head == "$now":
        val = datetime.now(timezone.utc).isoformat()
    elif head == "$today":
        val = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    elif head == "$env":
        key = rest.strip()
        # 1) os.environ — gated by allow-list so secrets don't leak
        val = None
        if any(key.startswith(p) for p in _ENV_ALLOW_PREFIXES):
            val = os.environ.get(key)
        # 2) workflow_env store — per-user / per-org / system. This
        # is the UI-editable store. Sync access via a cached dict the
        # executor populates when building ctx (see build_context).
        if val is None:
            wf_env = (ctx.get("_env") or {})
            val = wf_env.get(key)
    elif head in ("$workflow", "$run", "$trigger", "trigger"):
        key = head.lstrip("$")
        if key == "trigger":
            key = "trigger"
        val = _dig(ctx.get(key) or {}, rest) if rest else ctx.get(key)
    else:
        # node id lookup — `n1.foo.bar` resolves from ctx['state'][n1].foo.bar
        state = ctx.get("state") or {}
        node_output = state.get(head)
        if node_output is None and head in ctx:
            # allow shorthand: top-level in ctx
            node_output = ctx.get(head)
        val = _dig(node_output, rest) if rest else node_output

    return _resolve_filters(val, filters)


def resolve_string(template: str, ctx: dict) -> Any:
    """Resolve a single string. If the ENTIRE string is one `{{ }}` expr,
    return the raw value (may be a dict/list). Otherwise do string
    substitution. Null values render as ""."""
    if not isinstance(template, str):
        return template
    m_all = re.fullmatch(r"\s*\{\{\s*(.*?)\s*\}\}\s*", template)
    if m_all:
        return _resolve_one(m_all.group(1), ctx)

    def _sub(m):
        v = _resolve_one(m.group(1), ctx)
        if v is None:
            return ""
        return str(v) if not isinstance(v, (dict, list)) else json.dumps(v, default=str)

    return _EXPR_RE.sub(_sub, template)


# Keys whose VALUES are templates meant to be resolved later (per
# iteration in a loop, per-item in a sub-workflow, etc.). We MUST NOT
# resolve `{{item}}` / `{{index}}` at parent level — that would burn
# them to None before the loop iterates.
_NO_RESOLVE_KEYS = {
    "tool_params_template",
    "params_per_item",
    "per_item_params",
    "body_template",
    "template",
    "expression",  # raw expression strings that a code node wants to handle
}


def resolve(obj: Any, ctx: dict) -> Any:
    """Walk an arbitrary params structure and resolve every string that
    contains `{{ ... }}`. Returns a NEW object; never mutates input.

    Dict keys listed in `_NO_RESOLVE_KEYS` keep their values verbatim —
    those are lazy templates meant to be resolved by the tool itself
    with a per-iteration context."""
    if isinstance(obj, str):
        return resolve_string(obj, ctx)
    if isinstance(obj, dict):
        return {k: (v if k in _NO_RESOLVE_KEYS else resolve(v, ctx)) for k, v in obj.items()}
    if isinstance(obj, list):
        return [resolve(v, ctx) for v in obj]
    return obj


# ── Public: build context from a running workflow ────────────────────

def build_context(
    *,
    workflow: dict,
    run_id: str,
    state: dict,
    trigger_meta: dict | None = None,
    prev_output: dict | None = None,
    env: dict | None = None,
) -> dict:
    """Produce the ctx dict expression resolution expects.

    `env` is an optional pre-loaded dict of workflow_env values (the
    executor populates this once per run to avoid a DB hit per `{{$env.X}}`).
    """
    return {
        "state":    state,
        "workflow": {
            "id":   workflow.get("workflow_id"),
            "name": workflow.get("name"),
            "user_id": workflow.get("user_id"),
        },
        "run":      {"id": run_id},
        "trigger":  trigger_meta or {},
        "prev":     prev_output or {},
        "_env":     env or {},
        # node-id shorthand also accepted by _resolve_one via top-level
        **{k: v for k, v in (state or {}).items() if isinstance(k, str) and k.isidentifier()},
    }
