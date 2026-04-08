---
name: gws-sheets
description: Google Sheets API — read/write cells, formulas, charts, pivot tables, batch updates
---

# Google Sheets API — MAARS Reference

## Quick Start
```python
from googleapiclient.discovery import build
service = build("sheets", "v4", credentials=creds)
spreadsheet_id = "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgVE2upms"
```

## Key Operations
```python
# Read range
result = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range="Sheet1!A1:D10").execute()
values = result.get("values", [])

# Write range
body = {"values": [["Name", "Score"], ["Alice", 95], ["Bob", 87]]}
service.spreadsheets().values().update(spreadsheetId=spreadsheet_id, range="Sheet1!A1", valueInputOption="RAW", body=body).execute()

# Batch update
service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheet_id, body={
    "valueInputOption": "USER_ENTERED",
    "data": [{"range": "Sheet1!A1", "values": [[1, 2, 3]]}, {"range": "Sheet2!B2", "values": [["hello"]]}]
}).execute()

# Append rows
service.spreadsheets().values().append(spreadsheetId=spreadsheet_id, range="Sheet1", valueInputOption="RAW", body={"values": [["new", "row"]]}).execute()

# Format cells
service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body={"requests": [{"repeatCell": {"range": {"sheetId": 0, "startRowIndex": 0, "endRowIndex": 1}, "cell": {"userEnteredFormat": {"textFormat": {"bold": True}}}, "fields": "userEnteredFormat.textFormat.bold"}}]}).execute()
```

## Common Patterns
- Use `USER_ENTERED` for formulas, `RAW` for literal values
- A1 notation: `Sheet1!A1:C10`
- Pagination via `nextPageToken` for large sheets
