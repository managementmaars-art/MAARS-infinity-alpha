# Memos REST API Reference

> API version: v1 (gRPC-gateway). Base path: `/api/v1/`.
> All authenticated endpoints require `Authorization: Bearer $MEMOS_TOKEN`.

## Common Patterns

- **Update mask**: PATCH requests specify fields to update via `?updateMask=field1&updateMask=field2` query params.
- **Pagination**: `?pageSize=N&pageToken=TOKEN` → response includes `nextPageToken`.
- **Filtering**: `?filter=expression` using CEL-like syntax.
- **Resource names**: `{collection}/{id}` (e.g. `memos/JbqdMXPwv5KKzgexJnDHqE`, `users/roy`).
- **Error format**: `{"code": N, "message": "...", "details": []}` where code 3=invalid, 5=not found, 16=unauthenticated.

---

## MemoService

### List Memos
```
GET /api/v1/memos?pageSize=N&pageToken=TOKEN&filter=EXPR&state=NORMAL|ARCHIVED
Authorization: Bearer $TOKEN (optional for public memos)
```
Filter examples:
- `filter=creator=="users/roy"` — by creator
- `filter=content.contains("keyword")` — by content
- `filter=tag in ["tag1","tag2"]` — by tags
- `filter=visibility in ["PUBLIC","PRIVATE"]` — by visibility
- `filter=create_time>"2024-01-01T00:00:00Z"` — by date
- `filter=has_link==true` or `filter=has_task_list==true` — by property
- `order_by=create_time desc` or `display_time desc`

Response:
```json
{
  "memos": [
    {
      "name": "memos/UID",
      "uid": "UID",
      "state": "NORMAL",
      "creator": "users/roy",
      "content": "markdown content",
      "visibility": "PRIVATE",
      "tags": ["tag1"],
      "pinned": false,
      "createTime": "2024-...",
      "updateTime": "2024-...",
      "displayTime": "2024-...",
      "property": {"hasLink": false, "hasTaskList": false, "hasCode": false, "hasIncompleteTasks": false},
      "snippet": "plain text preview",
      "location": null,
      "attachments": [],
      "relations": [],
      "reactions": []
    }
  ],
  "nextPageToken": "..."
}
```

### Create Memo
```
POST /api/v1/memos
Authorization: Bearer $TOKEN
Content-Type: application/json

{
  "content": "markdown content with #tags",
  "visibility": "PRIVATE|PROTECTED|PUBLIC"
}
```

### Get Memo
```
GET /api/v1/memos/{uid}
Authorization: Bearer $TOKEN (optional for public)
```

### Update Memo
```
PATCH /api/v1/memos/{uid}?updateMask=content&updateMask=visibility
Authorization: Bearer $TOKEN
Content-Type: application/json

{
  "content": "new content",
  "visibility": "PUBLIC"
}
```
Updatable fields: `content`, `visibility`, `state`, `pinned`, `displayTime`, `location`.

### Delete Memo
```
DELETE /api/v1/memos/{uid}
Authorization: Bearer $TOKEN
```

### Pin/Unpin Memo
```
PATCH /api/v1/memos/{uid}?updateMask=pinned
Authorization: Bearer $TOKEN
Content-Type: application/json

{"pinned": true}
```

### Archive/Restore Memo
```
PATCH /api/v1/memos/{uid}?updateMask=state
Authorization: Bearer $TOKEN
Content-Type: application/json

{"state": "ARCHIVED"}
```
Use `"state": "NORMAL"` to restore.

---

### Memo Comments
```
# List comments
GET /api/v1/memos/{uid}/comments

# Create comment (creates a new memo as comment)
POST /api/v1/memos/{uid}/comments
Authorization: Bearer $TOKEN
Content-Type: application/json

{"comment": {"content": "comment text"}}
```

### Memo Relations
```
# List relations
GET /api/v1/memos/{uid}/relations

# Set relations (replaces all)
PATCH /api/v1/memos/{uid}/relations
Authorization: Bearer $TOKEN
Content-Type: application/json

{
  "relations": [
    {"relatedMemo": "memos/OTHER_UID", "type": "REFERENCE"}
  ]
}
```
Relation types: `REFERENCE`, `COMMENT`.

### Memo Reactions
```
# List reactions
GET /api/v1/memos/{uid}/reactions

# Add reaction
POST /api/v1/memos/{uid}/reactions
Authorization: Bearer $TOKEN
Content-Type: application/json

{"reactionType": "👍"}

# Delete reaction
DELETE /api/v1/memos/{uid}/reactions/{reactionId}
Authorization: Bearer $TOKEN
```

### Memo Attachments
```
# List attachments
GET /api/v1/memos/{uid}/attachments

# Set attachments (replaces all)
PATCH /api/v1/memos/{uid}/attachments
Authorization: Bearer $TOKEN
Content-Type: application/json

{
  "attachments": ["attachments/ATTACHMENT_UID"]
}
```

---

## UserService

### List Users
```
GET /api/v1/users
Authorization: Bearer $TOKEN
```

### Get User
```
GET /api/v1/users/{username}
```

### Create User
```
POST /api/v1/users
Authorization: Bearer $TOKEN (admin only)
Content-Type: application/json

{
  "username": "newuser",
  "password": "password123",
  "role": "USER|ADMIN",
  "email": "user@example.com",
  "displayName": "Display Name"
}
```

### Update User
```
PATCH /api/v1/users/{username}?updateMask=displayName&updateMask=email
Authorization: Bearer $TOKEN
Content-Type: application/json

{"displayName": "New Name", "email": "new@email.com"}
```

### Delete User
```
DELETE /api/v1/users/{username}
Authorization: Bearer $TOKEN (admin only)
```

### User Stats
```
# All users stats
GET /api/v1/users:stats

# Single user stats
GET /api/v1/users/{username}:getStats
```

### User Settings
```
GET /api/v1/users/{username}/settings
Authorization: Bearer $TOKEN
```

### User Webhooks
```
# List
GET /api/v1/users/{username}/webhooks
Authorization: Bearer $TOKEN

# Create
POST /api/v1/users/{username}/webhooks
Authorization: Bearer $TOKEN
Content-Type: application/json

{"url": "https://example.com/hook", "creator": "users/{username}"}
```

---

## AttachmentService

### List Attachments
```
GET /api/v1/attachments
Authorization: Bearer $TOKEN
```

### Create Attachment
```
POST /api/v1/attachments
Authorization: Bearer $TOKEN
Content-Type: application/json

{
  "filename": "image.png",
  "content": "base64-encoded-content",
  "type": "image/png"
}
```

### Get Attachment
```
GET /api/v1/attachments/{uid}
Authorization: Bearer $TOKEN
```

### Update Attachment
```
PATCH /api/v1/attachments/{uid}?updateMask=filename
Authorization: Bearer $TOKEN
Content-Type: application/json

{"filename": "renamed.png"}
```

### Delete Attachment
```
DELETE /api/v1/attachments/{uid}
Authorization: Bearer $TOKEN
```

### Batch Delete Attachments
```
POST /api/v1/attachments:batchDelete
Authorization: Bearer $TOKEN
Content-Type: application/json

{"names": ["attachments/uid1", "attachments/uid2"]}
```

---

## InstanceService

### Get Instance Profile (no auth)
```
GET /api/v1/instance/profile
```
Response: `{"owner": "users/roy", "version": "0.27.0", ...}`

### Get Instance Setting
```
GET /api/v1/instance/settings/{name}
Authorization: Bearer $TOKEN
```
Setting names: `GENERAL`, `STORAGE`, `MEMO_RELATED`.

### Update Instance Setting
```
PATCH /api/v1/instance/settings/{name}
Authorization: Bearer $TOKEN (admin only)
Content-Type: application/json

{
  "generalSetting": {
    "disallowUserRegistration": true,
    "disallowPasswordAuth": false,
    "instanceUrl": "https://memos.example.com"
  }
}
```

---

## ShortcutService

User-scoped saved filters.

```
# List shortcuts
GET /api/v1/users/{username}/shortcuts
Authorization: Bearer $TOKEN

# Create shortcut
POST /api/v1/users/{username}/shortcuts
Authorization: Bearer $TOKEN
Content-Type: application/json

{"title": "My Filter", "filter": "tag in [\"work\"]"}
```

---

## IdentityProviderService

OAuth2/SSO identity provider management (admin only).

```
# List providers
GET /api/v1/identity-providers

# Create provider
POST /api/v1/identity-providers
Authorization: Bearer $TOKEN
Content-Type: application/json

{
  "title": "GitHub",
  "type": "OAUTH2",
  "config": {
    "oauth2": {
      "clientId": "...",
      "clientSecret": "...",
      "authUrl": "https://github.com/login/oauth/authorize",
      "tokenUrl": "https://github.com/login/oauth/access_token",
      "userInfoUrl": "https://api.github.com/user",
      "scopes": ["user"],
      "fieldMapping": {"identifier": "login", "displayName": "name", "email": "email"}
    }
  }
}
```
