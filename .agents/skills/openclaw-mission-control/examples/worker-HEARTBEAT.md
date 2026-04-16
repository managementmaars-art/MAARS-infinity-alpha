# Worker Agent Heartbeat

Check for assigned tasks and execute work.

## Steps

### 1. Get Your Tasks
```bash
curl "http://localhost:8080/api/tasks/mine?agent={{AGENT_ID}}"
```

### 2. Check for @Mentions
```bash
curl "http://localhost:8080/api/mentions?agent={{AGENT_ID}}"
```

If mentions found, review and respond, then mark read:
```bash
curl -X POST "http://localhost:8080/api/mentions/read" \
  -H "Content-Type: application/json" \
  -d '{"agent": "{{AGENT_ID}}", "all": true}'
```

### 3. Work on Tasks

If you have tasks in `todo` status:

**Pick up the task:**
```bash
curl -X POST "http://localhost:8080/api/tasks/{TASK_ID}/pick" \
  -H "Content-Type: application/json" \
  -d '{"agent": "{{AGENT_ID}}"}'
```

**Do the work described in the task.**

**Log progress (optional):**
```bash
curl -X POST "http://localhost:8080/api/tasks/{TASK_ID}/log" \
  -H "Content-Type: application/json" \
  -d '{
    "agent": "{{AGENT_ID}}",
    "action": "progress",
    "note": "Completed research phase, starting implementation"
  }'
```

**Complete the task:**
```bash
curl -X POST "http://localhost:8080/api/tasks/{TASK_ID}/complete" \
  -H "Content-Type: application/json" \
  -d '{
    "agent": "{{AGENT_ID}}",
    "note": "Summary of what was accomplished",
    "deliverables": ["path/to/file1.md", "path/to/file2.md"]
  }'
```

### 4. If Blocked

If you need help:
```bash
curl -X POST "http://localhost:8080/api/tasks/{TASK_ID}/log" \
  -H "Content-Type: application/json" \
  -d '{
    "agent": "{{AGENT_ID}}",
    "action": "blocked",
    "note": "Description of what's blocking you"
  }'
```

Add a comment mentioning the lead:
```bash
curl -X POST "http://localhost:8080/api/tasks/{TASK_ID}/comments" \
  -H "Content-Type: application/json" \
  -d '{
    "author": "{{AGENT_ID}}",
    "content": "@lead I'm blocked on this — need clarification on X"
  }'
```

## Priority Order

Work tasks in this order:
1. `urgent` — Do immediately
2. `high` — Important
3. `medium` — Normal
4. `low` — When time permits

## Response

If no tasks: **HEARTBEAT_OK**
If work completed: Brief summary of what was done
