---
name: gws-gmail
description: Gmail API — send, read, labels, filters, drafts, threads, attachments
---

# Gmail API — MAARS Reference

## Quick Start
```python
from googleapiclient.discovery import build
service = build("gmail", "v1", credentials=creds)
```

## Key Operations
```python
import base64
from email.mime.text import MIMEText

# Send email
message = MIMEText("Hello World")
message["to"] = "recipient@example.com"
message["subject"] = "Test"
raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
service.users().messages().send(userId="me", body={"raw": raw}).execute()

# List messages
results = service.users().messages().list(userId="me", q="is:unread label:inbox").execute()

# Read message
msg = service.users().messages().get(userId="me", id=msg_id, format="full").execute()
payload = msg["payload"]

# Create label
service.users().labels().create(userId="me", body={"name": "MyLabel"}).execute()

# Create draft
service.users().drafts().create(userId="me", body={"message": {"raw": raw}}).execute()
```

## Common Patterns
- `userId="me"` refers to authenticated user
- Query syntax: `is:unread`, `from:boss@company.com`, `has:attachment`
- Thread vs message: threads group related emails
- Rate limit: 250 quota units/second
