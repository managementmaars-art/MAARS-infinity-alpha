---
name: gws-drive
description: Google Drive API — files, folders, permissions, sharing, search, exports
---

# Google Drive API — MAARS Reference

## Quick Start
```python
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

creds = Credentials.from_authorized_user_file("token.json", ["https://www.googleapis.com/auth/drive"])
service = build("drive", "v3", credentials=creds)
```

## Key Operations
```python
# List files
results = service.files().list(
    pageSize=10, fields="files(id, name, mimeType, size)"
).execute()

# Upload file
from googleapiclient.http import MediaFileUpload
media = MediaFileUpload("file.pdf", mimetype="application/pdf")
file = service.files().create(body={"name": "file.pdf", "parents": [folder_id]}, media_body=media, fields="id").execute()

# Share file
service.permissions().create(fileId=file_id, body={"type": "user", "role": "writer", "emailAddress": "user@example.com"}).execute()

# Search files
results = service.files().list(q="name contains 'report' and mimeType='application/pdf'").execute()

# Export Google Doc as PDF
content = service.files().export(fileId=doc_id, mimeType="application/pdf").execute()
```

## Common Patterns
- Use `fields` parameter to limit response size
- Folder = mimeType `application/vnd.google-apps.folder`
- Export Google Docs: `application/vnd.google-apps.document` → PDF/DOCX
- Batch requests for bulk operations
