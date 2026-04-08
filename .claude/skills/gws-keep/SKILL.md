---
name: gws-keep
description: Google Keep API — notes, list notes, labels, archive, reminders, color coding
---

# Google Keep API — MAARS Reference

## Quick Start
```python
from googleapiclient.discovery import build
service = build("keep", "v1", credentials=creds)
# Scope: https://www.googleapis.com/auth/keep
```

## Key Operations
```python
# Create text note
note = service.notes().create(body={
    "title": "Meeting Notes",
    "body": {"text": {"text": "Discussed Q2 roadmap and budget allocation"}}
}).execute()

# Create checklist note
checklist = service.notes().create(body={
    "title": "Shopping List",
    "body": {"list": {"listItems": [
        {"text": {"text": "Milk"}, "checked": False},
        {"text": {"text": "Eggs"}, "checked": False},
        {"text": {"text": "Bread"}, "checked": True},
    ]}}
}).execute()

# List notes (not trashed)
notes = service.notes().list(filter="NOT trashed").execute()
for note in notes.get("notes", []):
    print(note["name"], note.get("title", ""))

# Get specific note
note = service.notes().get(name="notes/NOTE_ID").execute()

# Delete (trash) note
service.notes().delete(name=note["name"]).execute()

# Create label
label = service.labels().create(body={"name": "Work"}).execute()

# List labels
labels = service.labels().list().execute()
```

## Common Patterns
- Notes identified by `name` field like `notes/1abc2def3`
- Keep API limited to basic CRUD — advanced features via Apps Script
- Color and pinning require direct UI or internal APIs
