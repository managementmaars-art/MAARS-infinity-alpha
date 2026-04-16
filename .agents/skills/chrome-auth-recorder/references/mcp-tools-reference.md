# MCP Chrome Tools Reference

Detailed reference for Chrome MCP tools used in authenticated session recording.

## Core Tools Overview

| Tool | Purpose | When to Use |
|------|---------|-------------|
| `tabs_context_mcp` | Get/create tab context | Always first step |
| `update_plan` | Present plan for approval | Before recording starts |
| `gif_creator` | Control GIF recording | Start/stop/export workflow |
| `computer` | Browser interaction | Screenshots, clicks, typing |
| `read_console_messages` | Monitor JS console | Error detection |
| `read_network_requests` | Monitor HTTP traffic | API verification |

---

## tabs_context_mcp

**Purpose:** Access existing tab or create new MCP tab group.

**Parameters:**
- `createIfEmpty` (boolean): Create new tab group if none exists

**Returns:**
```json
{
  "tabIds": [101, 102],
  "currentTabId": 101,
  "url": "https://github.com/dashboard"
}
```

**Usage Pattern:**
```javascript
// Always call first to get tab context
tabs_context_mcp(createIfEmpty=true)

// Use returned tabId for all subsequent operations
```

**Best Practices:**
- Always call with `createIfEmpty=true` at workflow start
- Store returned `tabId` for use in other tools
- Verify URL matches expected domain before recording

---

## update_plan

**Purpose:** Present recording plan to user for explicit approval.

**Parameters:**
- `domains` (array): List of domains to be accessed
- `approach` (array): High-level steps (3-7 items)

**Example:**
```javascript
update_plan(
  domains=["github.com", "api.github.com"],
  approach=[
    "Record repository creation workflow",
    "Capture form interactions",
    "Monitor API calls for errors",
    "Export annotated GIF tutorial"
  ]
)
```

**Best Practices:**
- Keep approach items high-level (outcomes, not implementation)
- List ALL domains that will appear during workflow
- Wait for explicit "yes" or "proceed" from user
- Never start recording without approval

---

## gif_creator

**Purpose:** Control GIF recording lifecycle.

**Actions:**

### start_recording
```javascript
gif_creator(
  action="start_recording",
  tabId=101
)
```
**Effect:** Begins capturing browser actions as GIF frames
**Next Step:** Immediately take screenshot for first frame

### stop_recording
```javascript
gif_creator(
  action="stop_recording",
  tabId=101
)
```
**Effect:** Stops capturing (frames preserved)
**Next Step:** Export with annotations

### export
```javascript
gif_creator(
  action="export",
  tabId=101,
  download=true,
  filename="workflow-tutorial.gif",
  options={
    showClickIndicators: true,    // Orange circles at clicks
    showActionLabels: true,        // Black text labels
    showProgressBar: true,         // Bottom progress bar
    showWatermark: true,           // Claude logo
    quality: 10                    // 1-30 (10=balanced)
  }
)
```
**Effect:** Generates and downloads annotated GIF
**Output:** Downloaded to browser's Downloads folder

### clear
```javascript
gif_creator(
  action="clear",
  tabId=101
)
```
**Effect:** Discards all frames without exporting
**Use Case:** Restart after error

**Critical Pattern:**
```
1. gif_creator(action="start_recording")
2. computer(action="screenshot")  ← First frame
3. [Execute workflow]
4. computer(action="screenshot")  ← Last frame
5. gif_creator(action="stop_recording")
6. gif_creator(action="export", download=true)
```

---

## computer

**Purpose:** Interact with browser page.

**Actions:**

### screenshot
```javascript
computer(
  action="screenshot",
  tabId=101
)
```
**Returns:** Image ID for captured screenshot
**Use:** First/last frames, debugging, verification

### left_click
```javascript
computer(
  action="left_click",
  coordinate=[850, 120],  // [x, y] from top-left
  tabId=101
)
```
**Alternative with ref:**
```javascript
computer(
  action="left_click",
  ref="ref_1",  // From read_page or find
  tabId=101
)
```

### type
```javascript
computer(
  action="type",
  text="repository-name",
  tabId=101
)
```

### wait
```javascript
computer(
  action="wait",
  duration=2,  // seconds (max 30)
  tabId=101
)
```

**Best Practices:**
- Use screenshots for first/last GIF frames
- Wait after navigation before next action
- Use ref over coordinates when available
- Type slowly for better visual capture

---

## read_console_messages

**Purpose:** Monitor JavaScript console for errors.

**Parameters:**
- `tabId` (required): Tab to monitor
- `pattern` (string): Regex filter (e.g., "error|exception")
- `onlyErrors` (boolean): Show only error-level messages
- `limit` (number): Max messages to return (default 100)
- `clear` (boolean): Clear after reading (avoid duplicates)

**Example:**
```javascript
read_console_messages(
  tabId=101,
  pattern="error|failed|exception",
  onlyErrors=true,
  clear=true
)
```

**Returns:**
```json
[
  {
    "level": "error",
    "text": "Uncaught TypeError: Cannot read property 'value' of null",
    "source": "app.js:234",
    "timestamp": "2025-12-20T10:30:45Z"
  }
]
```

**Best Practices:**
- Always provide pattern to filter noise
- Use `onlyErrors=true` for workflow monitoring
- Set `clear=true` to avoid duplicate messages
- Check after critical actions (form submit, API calls)

---

## read_network_requests

**Purpose:** Monitor HTTP network traffic.

**Parameters:**
- `tabId` (required): Tab to monitor
- `urlPattern` (string): Filter by URL substring (e.g., "/api/")
- `limit` (number): Max requests to return (default 100)
- `clear` (boolean): Clear after reading

**Example:**
```javascript
read_network_requests(
  tabId=101,
  urlPattern="/api/",
  clear=true
)
```

**Returns:**
```json
[
  {
    "url": "https://api.github.com/repos",
    "method": "POST",
    "status": 201,
    "statusText": "Created",
    "timestamp": "2025-12-20T10:30:50Z"
  },
  {
    "url": "https://api.github.com/user",
    "method": "GET",
    "status": 200,
    "statusText": "OK"
  }
]
```

**Best Practices:**
- Filter with `urlPattern` to reduce noise
- Check after API-triggering actions
- Look for 4xx/5xx status codes
- Verify expected API calls occurred

---

## Workflow Integration Patterns

### Pattern 1: Error-Monitored Recording
```
1. Start recording
2. Take screenshot (first frame)
3. Execute action
4. read_console_messages (check for errors)
5. read_network_requests (verify API)
6. If errors → report to user
7. Take screenshot (last frame)
8. Stop recording
9. Export with error context
```

### Pattern 2: Privacy-Aware Recording
```
1. Start recording
2. Guide user through safe steps
3. STOP recording before sensitive data
4. User enters credentials
5. RESUME recording
6. Continue workflow
7. Export (no sensitive data in frames)
```

### Pattern 3: Long-Form Workflow
```
1. Start recording
2. Execute part 1 (0-60s)
3. Stop + export: "workflow-part1.gif"
4. Clear frames
5. Start new recording
6. Execute part 2 (60-120s)
7. Stop + export: "workflow-part2.gif"
```

---

## Common Pitfalls

1. **Missing First/Last Frames**
   - Always screenshot immediately after start_recording
   - Always screenshot before stop_recording

2. **Recording Without Approval**
   - Always call update_plan first
   - Wait for explicit user confirmation

3. **Ignoring Errors**
   - Check console_messages after critical actions
   - Verify network_requests for API failures

4. **Vague Filenames**
   - Use descriptive names: "github-create-repo.gif"
   - Not generic: "recording.gif"

5. **Large File Sizes**
   - Keep recordings <90 seconds
   - Use quality=10 for balance
   - Split long workflows into multiple GIFs

6. **Missing Annotations**
   - Always set showClickIndicators=true
   - Always set showActionLabels=true
   - Include progress bar for context

7. **Not Clearing Messages/Requests**
   - Set clear=true to avoid duplicates
   - Otherwise same errors appear on every read
