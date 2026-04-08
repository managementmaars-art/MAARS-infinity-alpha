---
name: gws-workflow
description: Google Workspace automation — Apps Script triggers, approval workflows, GCP Workflows orchestration
---

# Google Workspace Workflow Automation — MAARS Reference

## Apps Script Triggers
```javascript
// Time-driven trigger (daily report)
function setupDailyReport() {
  ScriptApp.newTrigger("generateDailyReport")
    .timeBased().everyDays(1).atHour(8).create();
}

function generateDailyReport() {
  const sheet = SpreadsheetApp.openById("SPREADSHEET_ID").getSheetByName("Data");
  const data = sheet.getDataRange().getValues();
  const report = data.slice(1).map(row => `${row[0]}: ${row[1]}`).join("\n");
  GmailApp.sendEmail("manager@company.com", "Daily Report", report);
}

// Form submission -> Approval email workflow
function onFormSubmit(e) {
  const response = e.namedValues;
  const approvalUrl = `https://script.google.com/macros/s/SCRIPT_ID/exec?action=approve&id=${e.range.getRow()}`;
  const denyUrl = `https://script.google.com/macros/s/SCRIPT_ID/exec?action=deny&id=${e.range.getRow()}`;
  GmailApp.sendEmail("approver@company.com", "Approval Required",
    `Request from ${response["Name"][0]}`,
    {htmlBody: `<a href="${approvalUrl}">Approve</a> | <a href="${denyUrl}">Deny</a>`}
  );
}
```

## Spreadsheet Edit Trigger
```javascript
function onEdit(e) {
  const sheet = e.source.getActiveSheet();
  const range = e.range;
  // Trigger when Status column changes to "Ready"
  if (sheet.getName() === "Orders" && range.getColumn() === 5 && range.getValue() === "Ready") {
    notifyFulfillment(range.getRow());
  }
}
```

## GCP Workflows (Serverless Orchestration)
```yaml
# workflow.yaml — call multiple Google APIs in sequence
main:
  steps:
    - getSheetData:
        call: http.get
        args:
          url: https://sheets.googleapis.com/v4/spreadsheets/${spreadsheet_id}/values/Sheet1
          auth:
            type: OAuth2
        result: sheetData
    - processEachRow:
        for:
          value: row
          in: ${sheetData.body.values}
          steps:
            - sendNotification:
                call: http.post
                args:
                  url: https://chat.googleapis.com/v1/spaces/${space_id}/messages
                  auth:
                    type: OAuth2
                  body:
                    text: ${"Processing: " + row[0]}
    - done:
        return: "Workflow complete"
```

## Common Patterns
- Form -> Sheets -> Gmail approval -> Calendar event
- Webhook receiver -> Apps Script web app -> update Sheet
- Scheduled exports: Sheets -> Drive PDF -> email
