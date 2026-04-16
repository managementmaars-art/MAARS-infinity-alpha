# Chrome Auth Recorder - Troubleshooting

Common issues and solutions when recording authenticated workflows.

## Recording Issues

### Issue: Recording doesn't capture clicks

**Symptoms:**
- GIF exports but shows no click indicators
- Actions not visible in playback

**Causes:**
1. Options disabled during export
2. Actions happened too fast between frames
3. Browser tab not in focus

**Solutions:**
```javascript
// Ensure all annotations enabled
gif_creator(
  action="export",
  options={
    showClickIndicators: true,  // Must be true
    showActionLabels: true,     // Must be true
    showProgressBar: true,
    showWatermark: true
  }
)

// Slow down actions
computer(action="left_click", ...)
computer(action="wait", duration=1)  // Add pauses
computer(action="left_click", ...)
```

---

### Issue: GIF file too large (>10MB)

**Symptoms:**
- Export takes very long
- File difficult to share/embed

**Causes:**
1. Recording too long (>90 seconds)
2. Too many frames captured
3. Quality setting too high

**Solutions:**
```javascript
// Split into multiple GIFs
Part 1: 0-60s → export → clear
Part 2: 60-120s → export

// Reduce quality (slightly)
options={ quality: 8 }  // Instead of 10+

// Fewer frames = smaller file
- Slow down user actions
- Add waits between steps
- Avoid rapid clicking
```

---

### Issue: First/last frames missing

**Symptoms:**
- GIF starts mid-action
- GIF ends abruptly

**Cause:**
- Forgot to screenshot after start/before stop

**Solution:**
```javascript
// ALWAYS follow this pattern
gif_creator(action="start_recording", tabId)
computer(action="screenshot", tabId)  // REQUIRED first frame

[Execute workflow]

computer(action="screenshot", tabId)  // REQUIRED last frame
gif_creator(action="stop_recording", tabId)
```

---

## Authentication Issues

### Issue: User not authenticated

**Symptoms:**
- Browser shows login page
- API calls return 401 Unauthorized

**Causes:**
1. Session expired
2. Wrong tab selected
3. User logged out

**Solutions:**
```
1. Check current URL before recording
2. Ask user to login/refresh session
3. Verify authentication state:
   - Look for user avatar/name on page
   - Check for "Login" vs "Logout" button
4. Try tab refresh if session stale
```

---

### Issue: Recording captures sensitive data

**Symptoms:**
- Password visible in GIF frames
- API keys shown in console

**Prevention:**
```javascript
// Pause before sensitive entry
Assistant: "I'll pause recording while you enter your password"
gif_creator(action="stop_recording", tabId)

[User enters sensitive data]Assistant: "Recording resumed, continue with next step"
gif_creator(action="start_recording", tabId)
```

---

## Monitoring Issues

### Issue: Console errors not detected

**Symptoms:**
- Workflow fails but no errors reported
- User reports bug but no evidence

**Causes:**
1. Pattern filter too restrictive
2. Errors cleared before reading
3. Timing - checked before error occurred

**Solutions:**
```javascript
// Broader pattern
read_console_messages(
  pattern="error|warn|fail|exception|denied"  // Cast wider net
)

// Don't clear until end
clear=false  // Keep messages for full workflow

// Check at key moments
- After form submit
- After API calls
- After page navigation
- At workflow end
```

---

### Issue: Network requests not showing

**Symptoms:**
- API calls happened but not detected
- Empty results from read_network_requests

**Causes:**
1. Requests completed before monitoring started
2. URL pattern too specific
3. Requests cleared

**Solutions:**
```javascript
// Monitor from start of workflow
read_network_requests(tabId)  // Check what's there

// Broader URL pattern
urlPattern="/api/"  // Not "/api/specific/endpoint"

// Check at right time
- Immediately after action that triggers API
- Wait 1-2 seconds for request to complete
```

---

## Browser Compatibility

### Issue: Tab context not found

**Symptoms:**
- tabs_context_mcp returns empty
- "No MCP tab group found"

**Solutions:**
```javascript
// Always use createIfEmpty
tabs_context_mcp(createIfEmpty=true)

// This creates new tab group if needed
// User's existing tabs preserved
```

---

### Issue: Screenshots not capturing

**Symptoms:**
- computer(action="screenshot") fails
- GIF missing frames

**Causes:**
1. Tab not visible/focused
2. Browser minimized
3. Privacy/permission issue

**Solutions:**
```
1. Ask user to ensure browser window visible
2. Check browser permissions for screenshots
3. Try refreshing page
4. Verify tabId is correct
```

---

## Workflow Execution Issues

### Issue: Actions happen too fast

**Symptoms:**
- GIF skips steps
- Hard to follow tutorial

**Solution:**
```javascript
// Add strategic waits
computer(action="left_click", ...)
computer(action="wait", duration=2)  // Let user see result
computer(action="type", text="...")
computer(action="wait", duration=1)  // See what was typed
computer(action="left_click", ...)
```

---

### Issue: Page elements not found

**Symptoms:**
- Automated clicks fail
- form_input returns error

**Causes:**
1. Page not fully loaded
2. Element reference stale
3. Dynamic content changed

**Solutions:**
```javascript
// Wait after navigation
navigate(url="...", tabId)
computer(action="wait", duration=3)  // Let page load

// Re-read page if elements change
read_page(tabId)  // Get fresh element refs

// Use find for dynamic content
find(query="submit button", tabId)  // Semantic search
```

---

## Export Issues

### Issue: Export fails silently

**Symptoms:**
- No error message
- No GIF downloaded

**Causes:**
1. No frames recorded
2. Download blocked by browser
3. Disk space insufficient

**Solutions:**
```
1. Verify recording started successfully
2. Check browser Downloads settings
3. Check available disk space
4. Try shorter recording
```

---

### Issue: Downloaded GIF corrupted

**Symptoms:**
- GIF won't open
- Incomplete playback

**Causes:**
1. Export interrupted
2. Browser crash during export
3. Quality setting too extreme

**Solutions:**
```javascript
// Use safe quality setting
options={ quality: 10 }  // Not 1 or 30

// Ensure workflow completes
- Don't close browser during export
- Wait for download confirmation
```

---

## Quick Diagnostics Checklist

When recording fails, check:

- [ ] `tabs_context_mcp(createIfEmpty=true)` called first
- [ ] `update_plan` presented and user approved
- [ ] Screenshot taken immediately after `start_recording`
- [ ] Screenshot taken immediately before `stop_recording`
- [ ] Console checked with `onlyErrors=true, clear=true`
- [ ] Network checked with appropriate `urlPattern`
- [ ] All export options enabled (click indicators, labels)
- [ ] Descriptive filename provided
- [ ] Download confirmed successful
- [ ] User on correct page before recording
- [ ] No sensitive data visible in frames

---

## Getting Help

If issue persists after troubleshooting:

1. **Capture error details:**
   - Exact error message
   - Console messages output
   - Network requests output
   - Workflow steps attempted

2. **Provide context:**
   - Which platform (GitHub, Notion, etc.)
   - User-Guided or Automated mode
   - Recording duration
   - Browser version

3. **Try minimal workflow:**
   - Record simplest possible action
   - If that works, gradually add complexity
   - Identify where failure occurs

4. **Check MCP status:**
   - Verify Chrome MCP integration active
   - Check for browser extension updates
   - Restart browser if needed
