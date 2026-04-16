# Team Lead Heartbeat

Check the Kanban board for tasks needing attention.

## Steps

### 1. Review Tasks in Review
```bash
curl "http://localhost:8080/api/tasks?status=review"
```

If tasks found:
- Review deliverables
- Approve or add feedback
- Mark `done` when approved:
```bash
curl -X PATCH "http://localhost:8080/api/tasks/{ID}" \
  -H "Content-Type: application/json" \
  -d '{"status": "done"}'
```

### 2. Check for Blocked Tasks
```bash
curl "http://localhost:8080/api/tasks?status=in_progress"
```

Look for `blocked` log entries. Help unblock if needed.

### 3. Prioritize Backlog
```bash
curl "http://localhost:8080/api/tasks?status=backlog"
```

Move ready tasks to `todo`:
```bash
curl -X PATCH "http://localhost:8080/api/tasks/{ID}" \
  -H "Content-Type: application/json" \
  -d '{"status": "todo"}'
```

### 4. Check Your @Mentions
```bash
curl "http://localhost:8080/api/mentions?agent=lead"
```

If mentions found:
- Review and respond
- Mark as read when done:
```bash
curl -X POST "http://localhost:8080/api/mentions/read" \
  -H "Content-Type: application/json" \
  -d '{"agent": "lead", "all": true}'
```

## Response

If no action needed: **HEARTBEAT_OK**
If work done: Summarize what you reviewed/approved
