---
name: gws-tasks
description: Google Tasks API — task lists, tasks, due dates, completion status, ordering
---

# Google Tasks API — MAARS Reference

## Quick Start
```python
from googleapiclient.discovery import build
service = build("tasks", "v1", credentials=creds)
```

## Key Operations
```python
# List task lists
task_lists = service.tasklists().list().execute()

# Create task list
tasklist = service.tasklists().insert(body={"title": "Project Tasks"}).execute()

# Add task
task = service.tasks().insert(tasklist=tasklist["id"], body={"title": "Complete report", "due": "2025-06-01T00:00:00.000Z", "notes": "Important deadline"}).execute()

# List tasks
tasks = service.tasks().list(tasklist=tasklist["id"]).execute()

# Complete task
service.tasks().patch(tasklist=tasklist["id"], task=task["id"], body={"status": "completed"}).execute()

# Reorder task
service.tasks().move(tasklist=tasklist["id"], task=task["id"], previous=prev_task_id).execute()
```

## Common Patterns
- Due dates must be in RFC 3339 format
- Subtasks via `parent` parameter on insert
- `status`: `needsAction` or `completed`
