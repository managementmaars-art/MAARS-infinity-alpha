# TickTick Open API Reference

Base URL: `https://api.ticktick.com/open/v1`
Auth: `Authorization: Bearer {TICKTICK_TOKEN}`

## Endpoints

### Projects

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/project` | List all projects |
| GET | `/project/{projectId}` | Get project details |
| GET | `/project/{projectId}/data` | Get project + all tasks |
| GET | `/project/inbox/data` | Get inbox tasks (shortcut) |
| POST | `/project` | Create project |
| POST | `/project/{projectId}` | Update project |
| DELETE | `/project/{projectId}` | Delete project |

### Tasks

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/project/{projectId}/task/{taskId}` | Get specific task |
| POST | `/task` | Create task |
| POST | `/task/{taskId}` | Update task |
| POST | `/project/{projectId}/task/{taskId}/complete` | Mark complete |
| DELETE | `/project/{projectId}/task/{taskId}` | Delete task |

## Task Object Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Task ID (required for update) |
| `title` | string | Task title (required) |
| `projectId` | string | Project ID (omit → Inbox) |
| `content` | string | Notes / description |
| `priority` | int | 0=None, 1=Low, 3=Medium, 5=High |
| `dueDate` | string | ISO 8601, e.g. `2026-02-20T10:00:00-03:00` |
| `startDate` | string | ISO 8601 start date |
| `isAllDay` | bool | All-day task (no time) |
| `tags` | string[] | Array of tag strings |
| `timeZone` | string | e.g. `America/Buenos_Aires` |
| `parentId` | string | Parent task ID (for subtasks) |
| `status` | int | 0=pending, 2=completed |
| `kind` | string | `TEXT` (default) |

## Project Object Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Project ID |
| `name` | string | Display name |
| `color` | string | Hex color, e.g. `#4A90E2` |
| `viewMode` | string | `list`, `kanban`, `timeline` |
| `kind` | string | `TASK` (default) |

## Priority Reference

| Label  | Value | Emoji |
|--------|-------|-------|
| None   | 0     | ○     |
| Low    | 1     | 🔵    |
| Medium | 3     | 🟡    |
| High   | 5     | 🔴    |

## Known IDs (JMO)

| Name | ID |
|------|----|
| Inbox | `inbox131039472` |

> Other project IDs: discovered dynamically via `GET /project`

## Date & Timezone

- All dates use ISO 8601 format
- JMO timezone: `America/Buenos_Aires` (ART = UTC-3, no DST)
- ART offset: always `-03:00`
- Example: `"2026-02-20T10:00:00-03:00"` = 10 AM Buenos Aires

## Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success (with body) |
| 204 | Success (no body) — treat as OK |
| 400 | Bad request |
| 401 | Token expired or invalid |
| 404 | Resource not found |

## Error Response Shape

```json
{
  "errorId": "...",
  "errorCode": "client_exception",
  "errorMessage": "..."
}
```

## Subtasks

Create a task with `parentId` set to the parent task's ID. Both tasks must be in the same project.

```json
{
  "title": "Subtask title",
  "projectId": "same-as-parent",
  "parentId": "parent-task-id"
}
```

## Notes

- The `tp_*` personal access token (stored as `TICKTICK_TOKEN`) works directly as a Bearer token — no OAuth flow needed
- Token does not expire (personal access token)
- Inbox special ID: `inbox131039472` (discovered from task responses)
- `GET /open/v1/user/profile` returns 404 with this token type — skip it
- `GET /open/v1/task/{taskId}` (without projectId) returns 405 — always use the project-scoped endpoint
