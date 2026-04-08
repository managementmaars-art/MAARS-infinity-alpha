---
name: gws-admin
description: Google Workspace Admin SDK — users, groups, org units, domains, devices, audit reports
---

# Google Workspace Admin SDK — MAARS Reference

## Quick Start
```python
from googleapiclient.discovery import build
# Requires service account with domain-wide delegation
service = build("admin", "directory_v1", credentials=delegated_creds)
```

## User Management
```python
# List all users
users = service.users().list(domain="company.com", maxResults=500, orderBy="email").execute()

# Create user
user = service.users().insert(body={
    "primaryEmail": "newuser@company.com",
    "name": {"givenName": "New", "familyName": "User"},
    "password": "TempPassword123!",
    "changePasswordAtNextLogin": True,
    "orgUnitPath": "/Engineering",
}).execute()

# Suspend/unsuspend user
service.users().update(userKey="user@company.com", body={"suspended": True}).execute()

# Reset password
service.users().update(userKey="user@company.com", body={"password": "NewPass!", "changePasswordAtNextLogin": True}).execute()

# Delete user
service.users().delete(userKey="user@company.com").execute()
```

## Group Management
```python
# Create group
group = service.groups().insert(body={"email": "engineering@company.com", "name": "Engineering Team"}).execute()

# Add member
service.members().insert(groupKey="engineering@company.com", body={"email": "dev@company.com", "role": "MEMBER"}).execute()

# List group members
members = service.members().list(groupKey="engineering@company.com").execute()
```

## Org Units and Reports
```python
# Create org unit
service.orgunits().insert(customerId="my_customer", body={"name": "Engineering", "parentOrgUnitPath": "/"}).execute()

# Audit login activity
reports = build("admin", "reports_v1", credentials=creds)
activities = reports.activities().list(userKey="all", applicationName="login", maxResults=100).execute()

# Usage report
report = reports.userUsageReport().get(userKey="all", date="2025-01-01").execute()
```

## Common Patterns
- `my_customer` = alias for your Workspace customer ID
- `customerId` from Admin console > Account > Profile
- Domain-wide delegation needed for service account impersonation
- Batch user provisioning: loop + `service.new_batch_http_request()`
