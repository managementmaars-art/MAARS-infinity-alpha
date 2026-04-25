# Router strategy inventory

MAARS has 5 routing-related modules. Only one is in the hot path today.

| Module | Role | Status | Import count |
|---|---|---|---|
| `routes/v1_gateway.py::_resolve_maars_alias` | **Canonical.** Alias → (provider, model) selection for `maars/auto`, `maars/code`, `maars/reasoning`, etc. | **PRODUCTION** | hot path |
| `services/bandit_router.py` | Thompson-sampling posterior update after each call. Feedback loop only — doesn't select, just records. | **PRODUCTION** | `llm_gateway.complete` |
| `services/smart_router.py` | Early free-first cascade logic. Mostly subsumed by `_resolve_maars_alias`. | Legacy — keep for reference | 0 runtime |
| `services/confidence_router.py` | Experimental: route by predicted confidence. | **Experimental** | 0 |
| `services/pareto_router.py` | Experimental: multi-objective (cost × quality × latency). | **Experimental** | 1 (`speculative.py`) |

## What to do

- **Adding a new routing signal?** Update `_resolve_maars_alias` in `routes/v1_gateway.py` — that's the single place the hot path consults.
- **Recording post-call feedback?** Use `bandit_router.record(arm, success, latency_ms, credits)`.
- **Don't add a new `*_router.py`** — consolidate existing signals instead. New files here create drift.

## Deletion criteria

The three experimental/legacy files can be deleted if:
1. 30 days pass with zero commits touching them AND
2. No `git grep` hit for `from services.<name>_router` anywhere in the codebase.

Currently `pareto_router` still has 1 caller in `speculative.py` — that would need to move to `bandit_router` first.
