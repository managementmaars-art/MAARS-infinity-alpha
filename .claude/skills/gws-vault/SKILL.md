---
name: gws-vault
description: Google Vault API — eDiscovery, legal holds, matter management, exports, audit
---

# Google Vault API — MAARS Reference

## Quick Start
```python
from googleapiclient.discovery import build
service = build("vault", "v1", credentials=creds)
# Requires Vault privilege in Google Workspace Admin
```

## Matter Management
```python
# Create matter
matter = service.matters().create(body={
    "name": "Legal Case 2025-001",
    "description": "Employment litigation hold",
    "state": "OPEN",
}).execute()
matter_id = matter["matterId"]

# Add collaborator
service.matters().addPermissions(matterId=matter_id, body={
    "matterPermission": {"accountId": user_account_id, "role": "COLLABORATOR"},
    "sendEmails": True,
}).execute()

# List matters
matters = service.matters().list(state="OPEN").execute()
```

## Legal Holds
```python
# Create email hold
hold = service.matters().holds().create(matterId=matter_id, body={
    "name": "Executive Email Hold",
    "corpus": "MAIL",
    "query": {"mailQuery": {"terms": "subject:acquisition OR subject:merger"}},
    "accounts": [{"accountId": user_account_id}],
    "startTime": "2024-01-01T00:00:00Z",
}).execute()

# Hold entire org unit
hold = service.matters().holds().create(matterId=matter_id, body={
    "name": "Finance OU Hold",
    "corpus": "DRIVE",
    "orgUnit": {"orgUnitId": ou_id},
}).execute()
```

## Exports
```python
# Create email export
export = service.matters().exports().create(matterId=matter_id, body={
    "name": "Q1 Email Export",
    "corpus": "MAIL",
    "query": {
        "mailQuery": {"terms": "from:ceo@company.com after:2024/01/01"},
        "searchMethod": "ACCOUNT",
        "accountInfo": {"emails": ["ceo@company.com"]},
        "startTime": "2024-01-01T00:00:00Z",
        "endTime": "2024-03-31T00:00:00Z",
    },
    "exportOptions": {"mailOptions": {"exportFormat": "MBOX", "showConfidentialModeContent": True}},
}).execute()

# Poll export status
import time
while True:
    export = service.matters().exports().get(matterId=matter_id, exportId=export["id"]).execute()
    if export["status"] in ("COMPLETED", "FAILED"):
        break
    time.sleep(30)

# Download from Cloud Storage bucket in export["cloudStorageSink"]
```

## Corpus Types
- `MAIL`, `DRIVE`, `GROUPS`, `HANGOUTS_CHAT`, `VOICE`
- Holds prevent deletion even after account deletion
- Exports stored in Google Cloud Storage
