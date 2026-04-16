---
name: symdex-code-search
description: |
  This skill should be used when finding, tracing, or understanding code in a repository
  with SymDex available. Trigger it for requests like "where is this defined?", "who
  calls this?", "what route handles this path?", "show me the file outline", "search
  this codebase by intent", or any task that would otherwise rely on broad Read/Grep/Glob
  exploration.
---

# SymDex Code Search

Use SymDex before broad file browsing.
Use it to save tokens by retrieving the exact code the agent needs instead of scanning whole files.
SymDex currently covers 16 language surfaces, including Python, Go, Kotlin, Dart, Swift, and Vue script blocks.

## Start Here

1. If the SymDex CLI reports a newer release, prefer upgrading before long sessions.
2. Confirm the repo id.
3. If the repo id is already known, pass `repo` on every scoped tool call.
4. If the repo id is unknown, call `list_repos` and match the current worktree.
5. Check freshness with `get_index_status(repo)`.
6. If the current worktree is not indexed, call `index_folder(path=".")`.
7. If the workspace already has `.symdex`, treat it as the intended local SymDex state and reuse it.
8. Reuse the returned `repo` id for the rest of the task.

If SymDex is unavailable or indexing fails, say so clearly and fall back to normal file reads only as needed.

## Core Rules

- Search first.
- Pass `repo` whenever you know it.
- Prefer `get_symbol` or `get_file_outline` over full-file reads.
- Use call graph and route tools before manual tracing.
- Re-check `get_index_status` after major edits or worktree switches.
- Read full files only when editing, reviewing unsupported or generated content, or when SymDex cannot answer.
- Optimize for lower-token retrieval, not broad context loading.
- If a search tool returns `roi` or `roi_summary`, mention the approximate token savings briefly in your response.
- If the repo uses workspace-local SymDex state (`./.symdex`), stay inside that workspace so the same index is auto-discovered.

## Tool Selection

| Need | Tool |
|------|------|
| Index the current worktree | `index_folder` |
| Register and index a repo explicitly | `index_repo` |
| Find a function, class, or method by name | `search_symbols` |
| Find code by intent or behavior | `semantic_search` |
| Find literal text or regex matches | `search_text` |
| Read exact source for one symbol | `get_symbol` |
| Get a file outline before reading | `get_file_outline` |
| Get a repo map or summary | `get_repo_outline` or `get_file_tree` |
| Trace who calls a symbol | `get_callers` |
| Trace what a symbol calls | `get_callees` |
| Find HTTP routes | `search_routes` |
| Check repo freshness | `get_index_status` |
| Get code metrics and language mix | `get_repo_stats` |
| List indexes | `list_repos` |
| Clean deleted-worktree indexes | `gc_stale_indexes` |

## Typical Flow

1. Confirm the repo id and freshness.
2. Index with `index_folder` if needed.
3. Start with `search_symbols`, `semantic_search`, or `search_text`.
4. Narrow to `get_symbol` or `get_file_outline`.
5. Use `get_callers`, `get_callees`, `search_routes`, or `get_repo_stats` for deeper analysis.
6. Fall back to direct file reads only when SymDex cannot answer precisely enough.

## Decision Guide

- "Where is X defined?" -> `search_symbols`
- "What does this do?" -> `semantic_search`, then `get_symbol`
- "Who uses this?" -> `get_callers`
- "What does this call?" -> `get_callees`
- "Where is the endpoint?" -> `search_routes`
- "Show me the file structure first" -> `get_file_outline`
- "Give me a repo-level picture" -> `get_repo_outline` or `get_repo_stats`
- "Is the index current?" -> `get_index_status`

## Good Trigger Phrases

- "Find the function that validates JWTs"
- "Who calls this route handler?"
- "Show me the outline of this file"
- "Search for the code that parses webhook payloads"
- "Find the HTTP route for `/api/checkout`"
- "Give me the repo summary before I edit anything"

## Editing

When you need to edit code:

1. Use SymDex to find the exact symbol or file location.
2. Read only that file or symbol slice.
3. Make the smallest change needed.

## Use Normal Browsing Only When Needed

- SymDex is unavailable.
- The repo is not indexed and cannot be indexed in the current environment.
- The target file type is unsupported or generated.
- You need surrounding context that the symbol-level response does not provide.

## Output Checklist

- [ ] Repo id confirmed or derived
- [ ] Index freshness checked
- [ ] SymDex tool chosen before broad file reads
- [ ] Exact symbol or file outline used before whole-file reads when possible
- [ ] Direct file reads used only when SymDex could not answer cleanly
