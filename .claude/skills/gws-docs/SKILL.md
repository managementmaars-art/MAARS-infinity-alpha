---
name: gws-docs
description: Google Docs API — create, edit, format documents, insert content, structured data
---

# Google Docs API — MAARS Reference

## Quick Start
```python
from googleapiclient.discovery import build
service = build("docs", "v1", credentials=creds)
```

## Key Operations
```python
# Create document
doc = service.documents().create(body={"title": "My Document"}).execute()
doc_id = doc["documentId"]

# Read document content
doc = service.documents().get(documentId=doc_id).execute()
content = doc.get("body", {}).get("content", [])

# Insert text
requests = [{"insertText": {"location": {"index": 1}, "text": "Hello, World!\n"}}]
service.documents().batchUpdate(documentId=doc_id, body={"requests": requests}).execute()

# Format text (bold)
requests = [{"updateTextStyle": {"range": {"startIndex": 1, "endIndex": 6}, "textStyle": {"bold": True}, "fields": "bold"}}]
service.documents().batchUpdate(documentId=doc_id, body={"requests": requests}).execute()

# Insert table
requests = [{"insertTable": {"rows": 3, "columns": 3, "location": {"index": 1}}}]
service.documents().batchUpdate(documentId=doc_id, body={"requests": requests}).execute()
```

## Common Patterns
- Index 1 = beginning of document
- All mutations via `batchUpdate` with request objects
- Use Drive API to export as PDF/DOCX
