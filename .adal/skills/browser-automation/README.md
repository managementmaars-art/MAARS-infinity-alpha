# Browser Automation Skill for OpenClaw

A Playwright-based browser automation skill for OpenClaw. Control browsers to navigate, click, fill forms, take screenshots, and more.

## Features

- **Two Connection Modes**:
  - **CDP Mode**: Connect to your existing Chrome (with `--remote-debugging-port=9222`)
  - **Launch Mode**: Automatically launch a new Chromium instance
- **Full Browser Control**: Navigate, click, fill forms, screenshot, execute JS
- **Session Persistence**: Keep login states when using CDP mode
- **No Extension Required**: Works without browser extensions

## Installation

```bash
cd ~/.openclaw/skills
git clone https://github.com/yourusername/openclaw-browser-automation.git browser-automation
cd browser-automation
npm install
```

## Usage

In OpenClaw, simply tell your agent:
- "Open github.com"
- "Click the login button"
- "Fill in the email field"
- "Take a screenshot"

## Available Functions

### Page Operations
- `handleNavigate({url})` - Navigate to URL (reuses current page)
- `handleNewPage({url})` - Open new page
- `handleScreenshot({selector?, fullPage?})` - Take screenshot
- `handleGetContent({selector?})` - Get page HTML
- `handleClose()` - Close current page

### Interactions
- `handleClick({selector})` - Click element
- `handleFill({selector, value})` - Fill form field
- `handleType({selector, text})` - Type text (appends)
- `handleSelect({selector, value})` - Select dropdown option
- `handleCheck({selector, checked?})` - Check/uncheck checkbox

### Waiting & Getting
- `handleWait({selector, timeout?})` - Wait for element
- `handleWaitForNavigation()` - Wait for page navigation
- `handleGetText({selector})` - Get element text
- `handleGetValue({selector})` - Get form value
- `handleGetAttribute({selector, attribute})` - Get attribute

### Advanced
- `handleEvaluate({script})` - Execute JavaScript
- `handleUpload({selector, filePath})` - Upload file
- `handlePress({key})` - Press key
- `handleHover({selector})` - Hover element
- `handleScroll({direction, amount?})` - Scroll page

### Status
- `handleStatus()` - Get browser status
- `handleCloseBrowser()` - Close/disconnect browser

## Selector Syntax

Supports CSS selectors and text selectors:
- CSS: `#login-btn`, `.submit`, `input[name="email"]`
- Text: `text=Login`, `text=Submit`
- Combined: `button:has-text("Submit")`

## CDP Mode Setup

To use your existing Chrome with all login states:

1. Close all Chrome windows
2. Launch Chrome with debug mode:
   ```bash
   # Windows
   chrome.exe --remote-debugging-port=9222

   # Mac
   /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222

   # Linux
   google-chrome --remote-debugging-port=9222
   ```
3. Login to websites you need
4. Agent will automatically connect to this Chrome

## Requirements

- Node.js 18+
- OpenClaw CLI
- Playwright (auto-installed)

## License

MIT
