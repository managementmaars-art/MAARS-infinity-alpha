---
name: gws-calendar
description: Google Calendar API — events, invites, availability, recurring events, rooms
---

# Google Calendar API — MAARS Reference

## Quick Start
```python
from googleapiclient.discovery import build
service = build("calendar", "v3", credentials=creds)
```

## Key Operations
```python
# List upcoming events
events = service.events().list(calendarId="primary", timeMin="2025-01-01T00:00:00Z", maxResults=10, singleEvents=True, orderBy="startTime").execute()

# Create event
event = {
    "summary": "Team Meeting",
    "start": {"dateTime": "2025-06-01T10:00:00", "timeZone": "America/New_York"},
    "end": {"dateTime": "2025-06-01T11:00:00", "timeZone": "America/New_York"},
    "attendees": [{"email": "colleague@company.com"}],
    "conferenceData": {"createRequest": {"requestId": "unique-id", "conferenceSolutionKey": {"type": "hangoutsMeet"}}},
}
service.events().insert(calendarId="primary", body=event, conferenceDataVersion=1, sendUpdates="all").execute()

# Check availability (freebusy)
body = {"timeMin": "2025-06-01T00:00:00Z", "timeMax": "2025-06-02T00:00:00Z", "items": [{"id": "user@example.com"}]}
freebusy = service.freebusy().query(body=body).execute()
```

## Common Patterns
- `calendarId="primary"` for main calendar
- Use `conferenceDataVersion=1` to auto-create Meet links
- Recurring events: `recurrence: ["RRULE:FREQ=WEEKLY;BYDAY=MO"]`
