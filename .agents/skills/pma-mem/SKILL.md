---
name: pma-mem
description: Operate a Memos instance over its REST API. Use when the user wants to create, search, update, or delete memos, manage tags, attachments, or user settings through a reachable Memos server.
---

# Memos

Operate Memos by sending HTTP requests to `$MEMOS_URL` (default `http://memos:5230`).
Authenticate with a Personal Access Token stored in `$MEMOS_TOKEN`.

Keep this entry file small. Load only the references needed for the current turn.

## Always-On Rules

1. Confirm `$MEMOS_URL` and `$MEMOS_TOKEN` before making any request. If missing, ask the user for them.
2. Prefer `curl -s` piped to `jq` so results are easy to inspect.
3. All authenticated requests must include `-H "Authorization: Bearer $MEMOS_TOKEN"`.
4. API base path is `/api/v1/`. There is no v2 API.
5. PATCH requests use `updateMask` as a **query parameter**, not in the body.
6. Resource names follow `{collection}/{id}` format (e.g. `memos/abc123`, `users/roy`).
7. Pagination uses `pageSize` + `pageToken` / `nextPageToken`.
8. Error responses are gRPC-style: `{"code": N, "message": "...", "details": []}`.
9. Memo visibility values: `PRIVATE`, `PROTECTED` (logged-in users), `PUBLIC`.
10. Memo state values: `NORMAL`, `ARCHIVED`.

## Quick Start

```bash
# Health check (no auth needed)
curl -s "$MEMOS_URL/api/v1/instance/profile" | jq

# List memos
curl -s -H "Authorization: Bearer $MEMOS_TOKEN" \
  "$MEMOS_URL/api/v1/memos?pageSize=10" | jq

# Create memo
curl -s -X POST -H "Authorization: Bearer $MEMOS_TOKEN" \
  -H 'Content-Type: application/json' \
  "$MEMOS_URL/api/v1/memos" \
  -d '{"content":"Hello from CLI","visibility":"PRIVATE"}' | jq

# Search memos by content filter
curl -s -H "Authorization: Bearer $MEMOS_TOKEN" \
  "$MEMOS_URL/api/v1/memos?filter=content.contains(\"keyword\")" | jq

# Update memo content
curl -s -X PATCH -H "Authorization: Bearer $MEMOS_TOKEN" \
  -H 'Content-Type: application/json' \
  "$MEMOS_URL/api/v1/memos/{uid}?updateMask=content" \
  -d '{"content":"Updated content"}' | jq

# Delete memo
curl -s -X DELETE -H "Authorization: Bearer $MEMOS_TOKEN" \
  "$MEMOS_URL/api/v1/memos/{uid}" | jq

# Archive memo
curl -s -X PATCH -H "Authorization: Bearer $MEMOS_TOKEN" \
  -H 'Content-Type: application/json' \
  "$MEMOS_URL/api/v1/memos/{uid}?updateMask=state" \
  -d '{"state":"ARCHIVED"}' | jq
```

## Reference Packs

Load only what the current task needs:

- `references/rest-api.md`
  Full API endpoint reference: MemoService, UserService, AttachmentService, InstanceService, AuthService, ShortcutService.
- `references/workflows.md`
  Common workflows: bulk operations, tag management, memo relations, comments, reactions, search patterns, and attachment handling.

## Quick Routing

Choose references by intent:

- Single memo CRUD or API details: load `references/rest-api.md`.
- Bulk operations, search, tag workflows, or attachments: load `references/workflows.md`.
- Full understanding of all endpoints: load both.
