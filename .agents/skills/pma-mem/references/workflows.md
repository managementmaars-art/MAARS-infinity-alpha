# Memos Common Workflows

> Assumes `$MEMOS_URL` and `$MEMOS_TOKEN` are set.
> All `curl` commands use `-s -H "Authorization: Bearer $MEMOS_TOKEN"`.

## Auth Header Shorthand

```bash
AUTH="Authorization: Bearer $MEMOS_TOKEN"
API="$MEMOS_URL/api/v1"
```

---

## Daily Capture

### Quick memo
```bash
curl -s -X POST -H "$AUTH" -H 'Content-Type: application/json' \
  "$API/memos" \
  -d "{\"content\":\"$(date +%Y-%m-%d) quick note here\",\"visibility\":\"PRIVATE\"}" | jq
```

### Memo with tags (inline in content)
Tags are extracted from `#tag` syntax in the memo content.
```bash
curl -s -X POST -H "$AUTH" -H 'Content-Type: application/json' \
  "$API/memos" \
  -d '{"content":"#project Meeting notes: discussed roadmap #meeting","visibility":"PRIVATE"}' | jq
```

---

## Search & Filter

### By content keyword
```bash
curl -s -H "$AUTH" \
  "$API/memos?filter=content.contains(\"keyword\")" | jq '.memos[].content'
```

### By tag
```bash
curl -s -H "$AUTH" \
  "$API/memos?filter=tag+in+[\"work\",\"project\"]" | jq '.memos[].content'
```

### By creator
```bash
curl -s -H "$AUTH" \
  "$API/memos?filter=creator==\"users/roy\"" | jq '.memos[].content'
```

### By date range
```bash
curl -s -H "$AUTH" \
  "$API/memos?filter=create_time>\"2024-01-01T00:00:00Z\"+%26%26+create_time<\"2024-02-01T00:00:00Z\"" | jq
```

### By visibility
```bash
curl -s -H "$AUTH" \
  "$API/memos?filter=visibility+in+[\"PUBLIC\"]" | jq
```

### Pinned memos only
```bash
curl -s -H "$AUTH" \
  "$API/memos?filter=pinned==true" | jq
```

### With pagination
```bash
# First page
RESP=$(curl -s -H "$AUTH" "$API/memos?pageSize=5")
echo "$RESP" | jq '.memos[].snippet'
NEXT=$(echo "$RESP" | jq -r '.nextPageToken // empty')

# Next page
if [ -n "$NEXT" ]; then
  curl -s -H "$AUTH" "$API/memos?pageSize=5&pageToken=$NEXT" | jq '.memos[].snippet'
fi
```

---

## Bulk Operations

### Export all memos as JSON
```bash
ALL_MEMOS=""
PAGE_TOKEN=""
while true; do
  RESP=$(curl -s -H "$AUTH" "$API/memos?pageSize=50&pageToken=$PAGE_TOKEN")
  MEMOS=$(echo "$RESP" | jq '.memos')
  ALL_MEMOS=$(echo "$ALL_MEMOS$MEMOS" | jq -s 'add')
  PAGE_TOKEN=$(echo "$RESP" | jq -r '.nextPageToken // empty')
  [ -z "$PAGE_TOKEN" ] && break
done
echo "$ALL_MEMOS" | jq '.' > memos_export.json
echo "Exported $(echo "$ALL_MEMOS" | jq 'length') memos"
```

### Batch archive by tag
```bash
UIDS=$(curl -s -H "$AUTH" \
  "$API/memos?filter=tag+in+[\"old-project\"]&pageSize=100" \
  | jq -r '.memos[].uid')
for UID in $UIDS; do
  curl -s -X PATCH -H "$AUTH" -H 'Content-Type: application/json' \
    "$API/memos/$UID?updateMask=state" \
    -d '{"state":"ARCHIVED"}' | jq -r '.name'
done
```

### Batch delete archived memos
```bash
UIDS=$(curl -s -H "$AUTH" \
  "$API/memos?state=ARCHIVED&pageSize=100" \
  | jq -r '.memos[].uid')
for UID in $UIDS; do
  curl -s -X DELETE -H "$AUTH" "$API/memos/$UID" | jq
done
```

---

## Comments & Discussions

### Add comment to memo
```bash
curl -s -X POST -H "$AUTH" -H 'Content-Type: application/json' \
  "$API/memos/{uid}/comments" \
  -d '{"comment":{"content":"This is a follow-up thought"}}' | jq
```

### List comments
```bash
curl -s "$API/memos/{uid}/comments" | jq '.memos[].content'
```

---

## Reactions

### Add reaction
```bash
curl -s -X POST -H "$AUTH" -H 'Content-Type: application/json' \
  "$API/memos/{uid}/reactions" \
  -d '{"reactionType":"👍"}' | jq
```

### List reactions
```bash
curl -s "$API/memos/{uid}/reactions" | jq '.reactions[]'
```

---

## Relations (Linking Memos)

### Link two memos
```bash
curl -s -X PATCH -H "$AUTH" -H 'Content-Type: application/json' \
  "$API/memos/{uid}/relations" \
  -d '{"relations":[{"relatedMemo":"memos/OTHER_UID","type":"REFERENCE"}]}' | jq
```

### List related memos
```bash
curl -s "$API/memos/{uid}/relations" | jq '.relations[]'
```

---

## Attachments

### Upload attachment (base64)
```bash
B64=$(base64 -w0 < file.png)
ATTACHMENT=$(curl -s -X POST -H "$AUTH" -H 'Content-Type: application/json' \
  "$API/attachments" \
  -d "{\"filename\":\"file.png\",\"content\":\"$B64\",\"type\":\"image/png\"}" | jq)
ATT_NAME=$(echo "$ATTACHMENT" | jq -r '.name')
echo "Created: $ATT_NAME"
```

### Attach to memo
```bash
curl -s -X PATCH -H "$AUTH" -H 'Content-Type: application/json' \
  "$API/memos/{uid}/attachments" \
  -d "{\"attachments\":[\"$ATT_NAME\"]}" | jq
```

### List memo attachments
```bash
curl -s "$API/memos/{uid}/attachments" | jq '.attachments[]'
```

---

## Tag Management

Tags are embedded in memo content using `#tag` syntax. There is no separate tag API.

### List all tags (extract from memos)
```bash
curl -s -H "$AUTH" "$API/memos?pageSize=200" \
  | jq '[.memos[].tags[]] | unique | sort'
```

### Find memos by tag
```bash
curl -s -H "$AUTH" \
  "$API/memos?filter=tag+in+[\"mytag\"]" | jq '.memos[]|{uid,snippet}'
```

### Rename tag (update all memos containing it)
```bash
MEMOS=$(curl -s -H "$AUTH" \
  "$API/memos?filter=tag+in+[\"old-tag\"]&pageSize=200" \
  | jq -r '.memos[] | "\(.uid)\t\(.content)"')
echo "$MEMOS" | while IFS=$'\t' read -r UID CONTENT; do
  NEW_CONTENT=$(echo "$CONTENT" | sed 's/#old-tag/#new-tag/g')
  curl -s -X PATCH -H "$AUTH" -H 'Content-Type: application/json' \
    "$API/memos/$UID?updateMask=content" \
    -d "{\"content\":$(echo "$NEW_CONTENT" | jq -Rs .)}" | jq -r '.name'
done
```

---

## User Stats & Activity

### Get memo count and activity
```bash
curl -s "$API/users/{username}:getStats" | jq
```

### List all users
```bash
curl -s -H "$AUTH" "$API/users" | jq '.users[]|{username,role,state}'
```

---

## Instance Administration

### Check instance info
```bash
curl -s "$API/instance/profile" | jq
```

### Get instance settings
```bash
curl -s -H "$AUTH" "$API/instance/settings/GENERAL" | jq
curl -s -H "$AUTH" "$API/instance/settings/STORAGE" | jq
curl -s -H "$AUTH" "$API/instance/settings/MEMO_RELATED" | jq
```

