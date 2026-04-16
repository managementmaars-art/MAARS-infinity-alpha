# MCP Tool Reference

Comprehensive parameter documentation for Claude in Chrome MCP tools.

## Navigation Tools

### navigate
Navigate to a URL in the specified tab.

**Parameters:**
- `url` (string, required) - Full URL including protocol (http:// or https://)
- `tabId` (number, required) - Tab identifier from tabs_context_mcp

**Returns:**
- Navigation success confirmation

**Example:**
```
navigate(
  url="https://example.com/page",
  tabId=123
)
```

**Notes:**
- Always wait 2-3 seconds after navigation for dynamic content to load
- Use `computer(action="wait", duration=2, tabId=<id>)` to pause

### browser_navigate_back
Navigate back in browser history.

**Parameters:**
- `tabId` (number, required)

**Example:**
```
browser_navigate_back(tabId=123)
```

## Interaction Tools

### computer
Perform mouse/keyboard actions in the browser.

**Actions:**

**left_click** - Click an element
- `action`: "left_click"
- `coordinate`: [x, y] OR `ref`: "element-ref"
- `tabId`: number

```
computer(action="left_click", coordinate=[400, 300], tabId=123)
computer(action="left_click", ref="submit-button", tabId=123)
```

**type** - Type text
- `action`: "type"
- `text`: string to type
- `tabId`: number

```
computer(action="type", text="Hello world", tabId=123)
```

**screenshot** - Capture page screenshot
- `action`: "screenshot"
- `tabId`: number

```
computer(action="screenshot", tabId=123)
```

**scroll** - Scroll page
- `action`: "scroll"
- `direction`: "up" | "down"
- `amount`: number (pixels)
- `tabId`: number

```
computer(action="scroll", direction="down", amount=500, tabId=123)
```

**wait** - Pause execution
- `action`: "wait"
- `duration`: number (seconds)
- `tabId`: number

```
computer(action="wait", duration=2, tabId=123)
```

**drag** - Drag from one point to another
- `action`: "drag"
- `start`: [x, y]
- `end`: [x, y]
- `tabId`: number

```
computer(action="drag", start=[100, 200], end=[300, 400], tabId=123)
```

### form_input
Fill form fields (faster than typing).

**Parameters:**
- `ref` (string, required) - Element reference from find
- `value` (string, required) - Value to enter
- `tabId` (number, required)

**Example:**
```
form_input(ref="email-field", value="user@example.com", tabId=123)
```

**Notes:**
- Much faster than computer(action="type")
- Use for standard form inputs
- Use computer(action="type") for rich text editors

### find
Find elements on the page.

**Parameters:**
- `selector` (string, required) - CSS selector or text to find
- `tabId` (number, required)

**Returns:**
- Element reference(s) for use in form_input or computer(action="left_click")

**Example:**
```
find(selector="#submit-button", tabId=123)
find(selector="button:contains('Submit')", tabId=123)
```

## Data Retrieval Tools

### get_page_text
Get all text content from the page.

**Parameters:**
- `tabId` (number, required)

**Returns:**
- Full page text (no HTML tags)

**Example:**
```
get_page_text(tabId=123)
```

**Use cases:**
- Data extraction
- Content verification
- Search result parsing

### read_page
Get page content with structure (includes HTML).

**Parameters:**
- `tabId` (number, required)

**Returns:**
- Structured page content

**Example:**
```
read_page(tabId=123)
```

**Notes:**
- More detailed than get_page_text
- Includes DOM structure information

## Debugging Tools

### read_console_messages
Get browser console logs.

**Parameters:**
- `tabId` (number, required)
- `pattern` (string, optional) - Regex pattern to filter messages
- `onlyErrors` (boolean, optional) - Only return error messages

**Returns:**
- Array of console messages with:
  - `level`: "log" | "warn" | "error" | "info"
  - `message`: string
  - `timestamp`: number
  - `source`: file and line number

**Example:**
```
read_console_messages(
  tabId=123,
  pattern="error|exception|failed",
  onlyErrors=true
)
```

**Common patterns:**
- `"error|exception|failed"` - All errors
- `"TypeError|ReferenceError"` - Specific error types
- `"api|fetch"` - Network-related logs

### read_network_requests
Get network request logs.

**Parameters:**
- `tabId` (number, required)
- `urlPattern` (string, optional) - Regex to filter URLs
- `filterStatus` (array, optional) - HTTP status codes to include

**Returns:**
- Array of network requests with:
  - `url`: string
  - `method`: "GET" | "POST" | "PUT" | "DELETE" | etc.
  - `status`: HTTP status code
  - `statusText`: string
  - `requestHeaders`: object
  - `responseHeaders`: object
  - `timing`: request timing data

**Example:**
```
read_network_requests(
  tabId=123,
  urlPattern="/api/",
  filterStatus=[400, 401, 403, 404, 500, 502, 503]
)
```

**Common filters:**
- `urlPattern="/api/"` - API calls only
- `filterStatus=[401, 403]` - Auth failures
- `filterStatus=[500, 502, 503]` - Server errors

## Tab Management Tools

### tabs_context_mcp
Get current tab information.

**Parameters:**
- `createIfEmpty` (boolean, optional) - Create new tab if none exist

**Returns:**
- `tabId`: number
- `url`: current URL
- `title`: page title

**Example:**
```
tabs_context_mcp(createIfEmpty=true)
```

**Notes:**
- ALWAYS call this first before any other browser operations
- Returns active tab context
- Use createIfEmpty=true to ensure you have a valid tab

### tabs_create_mcp
Create a new browser tab.

**Parameters:**
- None

**Returns:**
- `tabId`: number of new tab

**Example:**
```
tabs_create_mcp()
```

**Use cases:**
- Multi-site workflows
- Parallel data gathering
- Keeping reference pages open

### browser_close
Close a browser tab.

**Parameters:**
- `tabId` (number, required)

**Example:**
```
browser_close(tabId=123)
```

## Recording Tools

### gif_creator
Record and export browser interactions as GIF.

**Actions:**

**start_recording** - Begin recording
- `action`: "start_recording"
- `tabId`: number

```
gif_creator(action="start_recording", tabId=123)
```

**stop_recording** - End recording
- `action`: "stop_recording"
- `tabId`: number

```
gif_creator(action="stop_recording", tabId=123)
```

**export** - Export GIF file
- `action`: "export"
- `tabId`: number
- `download`: boolean (save to downloads folder)
- `filename`: string (output filename)
- `options`: object
  - `showClickIndicators`: boolean (orange circles at clicks)
  - `showDragPaths`: boolean (red arrows for drags)
  - `showActionLabels`: boolean (text labels)
  - `showProgressBar`: boolean (orange bar at bottom)
  - `showWatermark`: boolean (Claude logo)
  - `quality`: number (5-30, higher = better compression but slower)

```
gif_creator(
  action="export",
  tabId=123,
  download=true,
  filename="tutorial-2025-12-24.gif",
  options={
    showClickIndicators: true,
    showActionLabels: true,
    showProgressBar: true,
    showWatermark: false,
    quality: 10
  }
)
```

**Recording workflow:**
1. `gif_creator(action="start_recording", tabId=<id>)`
2. `computer(action="screenshot", tabId=<id>)` ← REQUIRED first frame
3. [Perform workflow actions]
4. `computer(action="screenshot", tabId=<id>)` ← REQUIRED last frame
5. `gif_creator(action="stop_recording", tabId=<id>)`
6. `gif_creator(action="export", ...)`

## Window Management Tools

### browser_resize
Resize browser window.

**Parameters:**
- `width` (number, required) - Window width in pixels
- `height` (number, required) - Window height in pixels
- `tabId` (number, required)

**Example:**
```
browser_resize(width=1280, height=800, tabId=123)
```

**Common sizes:**
- Desktop: 1920x1080, 1280x800
- Tablet: 1024x768, 768x1024
- Mobile: 375x667 (iPhone), 360x640 (Android)

## Plan Management Tools

### update_plan
Present workflow plan to user for approval.

**Parameters:**
- `domains` (array, required) - List of domains to visit
- `approach` (array, required) - Step-by-step approach

**Example:**
```
update_plan(
  domains=["example.com", "api.example.com"],
  approach=[
    "Navigate to login page",
    "Fill credentials",
    "Submit form",
    "Verify dashboard loaded",
    "Check console for errors"
  ]
)
```

**Notes:**
- ALWAYS use before starting browser automation
- Wait for user approval before proceeding
- Required for privacy and permission management

## Upload Tools

### upload_image
Upload an image file to a form.

**Parameters:**
- `ref` (string, required) - File input element reference
- `filePath` (string, required) - Local file path
- `tabId` (number, required)

**Example:**
```
upload_image(
  ref="avatar-upload",
  filePath="/path/to/image.png",
  tabId=123
)
```

## Shortcuts

### shortcuts_list
List available browser shortcuts.

**Parameters:**
- None

**Returns:**
- Array of available shortcuts

**Example:**
```
shortcuts_list()
```

### shortcuts_execute
Execute a browser shortcut.

**Parameters:**
- `shortcut` (string, required) - Shortcut name

**Example:**
```
shortcuts_execute(shortcut="refresh")
```

## Best Practices

**Always check schemas before use:**
```bash
mcp-cli info claude-in-chrome/<tool-name>
```

**Required workflow pattern:**
```
1. tabs_context_mcp(createIfEmpty=true) → Get tabId
2. [Use other tools with tabId]
```

**Error handling:**
- Check console after every navigation
- Monitor network for failed API calls
- Wait for dynamic content to load

**Performance:**
- Filter console logs (use pattern or onlyErrors)
- Filter network requests (use urlPattern)
- Use form_input instead of type for speed

**Privacy:**
- Use update_plan for user approval
- Never ask for passwords
- Handle authentication manually
