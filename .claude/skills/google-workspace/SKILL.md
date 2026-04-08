---
name: google-workspace
description: Google Workspace APIs for Drive, Sheets, Gmail, Calendar, Docs, and Admin SDK with service account and OAuth authentication.
---

# Google Workspace APIs

## Overview

Google Workspace APIs provide programmatic access to Drive, Sheets, Gmail, Calendar, Docs, and Admin directory services. Authentication uses OAuth 2.0 or service accounts for server-to-server access.

## Authentication Setup

```python
# pip install google-auth google-auth-oauthlib google-api-python-client
from google.oauth2.service_account import Credentials
from google.oauth2.credentials import Credentials as UserCredentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import os
import json

# Service Account (server-to-server, no user interaction)
def get_service_account_creds(scopes: list[str]) -> Credentials:
    return Credentials.from_service_account_file(
        "service-account.json",
        scopes=scopes,
    )

# Domain-wide delegation (impersonate workspace users)
def get_delegated_creds(user_email: str, scopes: list[str]) -> Credentials:
    creds = get_service_account_creds(scopes)
    return creds.with_subject(user_email)

# OAuth 2.0 for user authorization
SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/gmail.readonly",
]

def get_user_creds() -> UserCredentials:
    creds = None
    if os.path.exists("token.json"):
        creds = UserCredentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as f:
            f.write(creds.to_json())

    return creds
```

## Google Drive API

```python
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import io

drive_service = build("drive", "v3", credentials=creds)

# List files with query
def list_files(folder_id: str = None, query: str = "") -> list:
    q_parts = ["trashed = false"]
    if folder_id:
        q_parts.append(f"'{folder_id}' in parents")
    if query:
        q_parts.append(f"name contains '{query}'")

    results = drive_service.files().list(
        q=" and ".join(q_parts),
        pageSize=100,
        fields="nextPageToken, files(id, name, mimeType, size, modifiedTime, parents)",
        orderBy="modifiedTime desc",
    ).execute()

    return results.get("files", [])

# Upload file
def upload_file(file_path: str, folder_id: str = None, mime_type: str = None) -> dict:
    file_name = os.path.basename(file_path)
    metadata = {"name": file_name}
    if folder_id:
        metadata["parents"] = [folder_id]

    media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)
    file = drive_service.files().create(
        body=metadata,
        media_body=media,
        fields="id, name, webViewLink",
    ).execute()
    return file

# Download file
def download_file(file_id: str, output_path: str):
    request = drive_service.files().get_media(fileId=file_id)
    with open(output_path, "wb") as f:
        downloader = MediaIoBaseDownload(f, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
            print(f"Download {int(status.progress() * 100)}%")

# Share file
def share_file(file_id: str, email: str, role: str = "reader"):
    permission = {"type": "user", "role": role, "emailAddress": email}
    drive_service.permissions().create(
        fileId=file_id,
        body=permission,
        sendNotificationEmail=True,
    ).execute()

# Create folder
def create_folder(name: str, parent_id: str = None) -> str:
    metadata = {
        "name": name,
        "mimeType": "application/vnd.google-apps.folder",
    }
    if parent_id:
        metadata["parents"] = [parent_id]

    folder = drive_service.files().create(body=metadata, fields="id").execute()
    return folder["id"]
```

## Google Sheets API

```python
sheets_service = build("sheets", "v4", credentials=creds)

SPREADSHEET_ID = "your-spreadsheet-id"

# Read data
def read_range(range_notation: str) -> list[list]:
    result = sheets_service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=range_notation,
        valueRenderOption="UNFORMATTED_VALUE",
        dateTimeRenderOption="FORMATTED_STRING",
    ).execute()
    return result.get("values", [])

# Write data
def write_range(range_notation: str, values: list[list]):
    body = {"values": values}
    sheets_service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=range_notation,
        valueInputOption="USER_ENTERED",
        body=body,
    ).execute()

# Append rows
def append_rows(sheet_name: str, rows: list[list]):
    body = {"values": rows}
    sheets_service.spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=f"{sheet_name}!A1",
        valueInputOption="USER_ENTERED",
        insertDataOption="INSERT_ROWS",
        body=body,
    ).execute()

# Batch read multiple ranges
def batch_read(ranges: list[str]) -> dict:
    result = sheets_service.spreadsheets().values().batchGet(
        spreadsheetId=SPREADSHEET_ID,
        ranges=ranges,
    ).execute()
    return {vr["range"]: vr.get("values", []) for vr in result["valueRanges"]}

# Create a new spreadsheet
def create_spreadsheet(title: str) -> str:
    spreadsheet = sheets_service.spreadsheets().create(
        body={
            "properties": {"title": title},
            "sheets": [{"properties": {"title": "Sheet1"}}],
        }
    ).execute()
    return spreadsheet["spreadsheetId"]

# Format cells
def format_header_row(sheet_id: int):
    requests = [{
        "repeatCell": {
            "range": {"sheetId": sheet_id, "startRowIndex": 0, "endRowIndex": 1},
            "cell": {
                "userEnteredFormat": {
                    "backgroundColor": {"red": 0.2, "green": 0.4, "blue": 0.8},
                    "textFormat": {"bold": True, "foregroundColor": {"red": 1, "green": 1, "blue": 1}},
                }
            },
            "fields": "userEnteredFormat(backgroundColor,textFormat)",
        }
    }]
    sheets_service.spreadsheets().batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body={"requests": requests},
    ).execute()
```

## Gmail API

```python
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

gmail_service = build("gmail", "v1", credentials=creds)

# List messages
def list_messages(query: str = "", max_results: int = 50) -> list:
    result = gmail_service.users().messages().list(
        userId="me",
        q=query,            # Gmail search syntax: "from:user@example.com is:unread"
        maxResults=max_results,
    ).execute()
    return result.get("messages", [])

# Get full message
def get_message(message_id: str) -> dict:
    message = gmail_service.users().messages().get(
        userId="me",
        id=message_id,
        format="full",
    ).execute()

    headers = {h["name"]: h["value"] for h in message["payload"]["headers"]}
    body = ""

    def extract_body(payload):
        if payload.get("mimeType") == "text/html":
            data = payload.get("body", {}).get("data", "")
            return base64.urlsafe_b64decode(data).decode("utf-8")
        for part in payload.get("parts", []):
            result = extract_body(part)
            if result:
                return result
        return ""

    return {
        "id": message["id"],
        "subject": headers.get("Subject", ""),
        "from": headers.get("From", ""),
        "date": headers.get("Date", ""),
        "body": extract_body(message["payload"]),
    }

# Send email
def send_email(to: str, subject: str, html_body: str, cc: str = None):
    message = MIMEMultipart("alternative")
    message["to"] = to
    message["subject"] = subject
    if cc:
        message["cc"] = cc

    message.attach(MIMEText(html_body, "html"))

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    gmail_service.users().messages().send(
        userId="me",
        body={"raw": raw},
    ).execute()
```

## Google Calendar API

```python
from datetime import datetime, timezone

calendar_service = build("calendar", "v3", credentials=creds)

# List upcoming events
def list_events(calendar_id: str = "primary", days_ahead: int = 7) -> list:
    now = datetime.now(timezone.utc).isoformat()
    end = datetime(2099, 1, 1, tzinfo=timezone.utc).isoformat()

    events_result = calendar_service.events().list(
        calendarId=calendar_id,
        timeMin=now,
        maxResults=50,
        singleEvents=True,
        orderBy="startTime",
    ).execute()

    return events_result.get("items", [])

# Create event
def create_event(title: str, start: datetime, end: datetime, attendees: list[str] = None) -> dict:
    event = {
        "summary": title,
        "start": {"dateTime": start.isoformat(), "timeZone": "UTC"},
        "end": {"dateTime": end.isoformat(), "timeZone": "UTC"},
        "reminders": {"useDefault": True},
    }
    if attendees:
        event["attendees"] = [{"email": e} for e in attendees]
        event["sendUpdates"] = "all"

    return calendar_service.events().insert(
        calendarId="primary",
        body=event,
    ).execute()
```

## Admin SDK (Directory)

```python
# Manage Google Workspace users and groups
admin_service = build("admin", "directory_v1", credentials=delegated_creds)

# List users in domain
def list_users(domain: str, max_results: int = 500) -> list:
    results = admin_service.users().list(
        domain=domain,
        maxResults=max_results,
        orderBy="email",
    ).execute()
    return results.get("users", [])

# Create user
def create_user(email: str, first_name: str, last_name: str, password: str):
    admin_service.users().insert(body={
        "primaryEmail": email,
        "name": {"givenName": first_name, "familyName": last_name},
        "password": password,
        "changePasswordAtNextLogin": True,
    }).execute()

# Add user to group
def add_to_group(group_email: str, user_email: str, role: str = "MEMBER"):
    admin_service.members().insert(
        groupKey=group_email,
        body={"email": user_email, "role": role},
    ).execute()
```

## Key Patterns

- **Service accounts** for server-to-server; **OAuth 2.0** for user-delegated access
- **Domain-wide delegation** lets service accounts act as any user in the workspace
- **Batch requests** reduce API calls — use `batchGet` for Sheets, `batch` for Drive
- **Quota limits**: Sheets API has 300 req/min/project; Drive 1000 req/100 sec/user
- **`fields` parameter** reduces response size — only request what you need
- **Exponential backoff** for rate limit errors (HTTP 429)

## Models to Use

- **claude-opus-4-5**: Complex automation workflows, multi-API pipelines, Admin SDK operations
- **claude-sonnet-4-5**: Standard CRUD operations, Sheets data processing, email automation
- **claude-haiku-3-5**: Simple reads, event creation, file listing
