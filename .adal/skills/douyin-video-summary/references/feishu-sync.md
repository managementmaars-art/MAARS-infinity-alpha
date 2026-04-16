# Feishu (Lark) Document Sync

Sync video summaries to a Feishu document using the Open API.

## Authentication

Get tenant access token:

```bash
curl -X POST 'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal' \
  -H 'Content-Type: application/json' \
  -d '{"app_id":"YOUR_APP_ID","app_secret":"YOUR_APP_SECRET"}'
```

## Document Structure

Use heading levels for auto-generated sidebar navigation:
- **H1 (block_type: 3):** Date category (e.g., "2026-02-09")
- **H2 (block_type: 4):** Video title (e.g., "大哥的亲子教育 | 童年录播姬")
- **Text (block_type: 2):** Summary content
- **Divider (block_type: 22):** Between videos

## Append Content

POST to `/open-apis/docx/v1/documents/{doc_id}/blocks/{doc_id}/children`:

```json
{
  "children": [
    {
      "block_type": 4,
      "heading2": {
        "elements": [{"text_run": {"content": "Video Title | Author"}}]
      }
    },
    {
      "block_type": 2,
      "text": {
        "elements": [{"text_run": {"content": "Summary text", "text_element_style": {"bold": false}}}],
        "style": {"align": 1}
      }
    }
  ],
  "index": -1
}
```

## Delete Blocks

Batch delete by index range:

```
DELETE /open-apis/docx/v1/documents/{doc_id}/blocks/{doc_id}/children/batch_delete
Body: {"start_index": 0, "end_index": N}
```

## Required Permissions

- `docx:document` — read/write documents
- `drive:drive` — manage file permissions (optional, for sharing)

## Tips

- Write in batches of 5-8 blocks to avoid API errors
- Add `time.sleep(0.8)` between batches for rate limiting
- Use `document_revision_id: -1` for latest revision when deleting
- Bold text: set `"bold": true` in `text_element_style`
