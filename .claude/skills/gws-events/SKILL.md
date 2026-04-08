---
name: gws-events
description: Google Calendar Events deep-dive — RSVP, attendees, rooms, conferencing, recurring events
---

# Google Calendar Events Deep-Dive — MAARS Reference

## Full Event with All Features
```python
event = {
    "summary": "All-Hands Meeting",
    "location": "Headquarters, Floor 3",
    "description": "Quarterly business review",
    "start": {"dateTime": "2025-06-01T10:00:00", "timeZone": "America/New_York"},
    "end": {"dateTime": "2025-06-01T11:00:00", "timeZone": "America/New_York"},
    "attendees": [
        {"email": "alice@company.com", "optional": False},
        {"email": "bob@company.com", "optional": True},
        {"email": "room-sf-bigroom@company.com", "resource": True},  # Book a room
    ],
    "reminders": {
        "useDefault": False,
        "overrides": [
            {"method": "email", "minutes": 1440},  # 24h before
            {"method": "popup", "minutes": 15},
        ]
    },
    "recurrence": ["RRULE:FREQ=WEEKLY;BYDAY=MO;COUNT=10"],
    "conferenceData": {
        "createRequest": {
            "requestId": "unique-meeting-id",
            "conferenceSolutionKey": {"type": "hangoutsMeet"}
        }
    },
    "colorId": "9",  # Blueberry
    "visibility": "private",
    "guestsCanInviteOthers": False,
}
result = service.events().insert(
    calendarId="primary", body=event,
    conferenceDataVersion=1, sendUpdates="all"
).execute()
```

## RSVP Status Tracking
```python
event = service.events().get(calendarId="primary", eventId=event_id).execute()
for attendee in event.get("attendees", []):
    status = attendee.get("responseStatus")  # accepted/declined/tentative/needsAction
    print(f"{attendee['email']}: {status}")
```

## Modify Single Recurring Occurrence
```python
# Get all instances
instances = service.events().instances(calendarId="primary", eventId=recurring_event_id).execute()
# Modify one instance
service.events().patch(calendarId="primary", eventId=instance_id, body={"summary": "Cancelled - reschedule", "status": "cancelled"}).execute()
```

## Watch for Changes
```python
watch = service.events().watch(calendarId="primary", body={
    "id": "unique-channel-id", "type": "web_hook", "address": "https://your.app/calendar-webhook"
}).execute()
```
