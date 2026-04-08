---
name: gws-people
description: Google People API — contacts, profiles, directory, connections, search, create contacts
---

# Google People API — MAARS Reference

## Quick Start
```python
from googleapiclient.discovery import build
service = build("people", "v1", credentials=creds)
```

## Key Operations
```python
# List connections (personal contacts)
results = service.people().connections().list(
    resourceName="people/me", pageSize=100,
    personFields="names,emailAddresses,phoneNumbers"
).execute()

# Get own profile
profile = service.people().get(resourceName="people/me", personFields="names,emailAddresses,photos").execute()

# Create contact
contact = service.people().createContact(body={
    "names": [{"givenName": "John", "familyName": "Doe"}],
    "emailAddresses": [{"value": "john@example.com", "type": "work"}],
    "phoneNumbers": [{"value": "+1-555-0100", "type": "mobile"}],
}).execute()

# Update contact
service.people().updateContact(
    resourceName=contact["resourceName"],
    updatePersonFields="names,emailAddresses",
    body={"names": [{"givenName": "John", "familyName": "Smith"}], "emailAddresses": [{"value": "john.smith@example.com"}]}
).execute()

# Search contacts
results = service.people().searchContacts(query="John", readMask="names,emailAddresses").execute()

# Search directory (org-wide)
results = service.people().searchDirectoryPeople(query="engineering", readMask="names,emailAddresses", sources=["DIRECTORY_SOURCE_TYPE_DOMAIN_PROFILE"]).execute()
```

## Common Patterns
- `personFields` is required for all GET requests
- Directory people = org contacts (requires Workspace admin)
- Rate limit: 90 requests/minute per user
- `otherContacts` resource for suggested contacts
