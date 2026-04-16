# Troubleshooting Guide

Diagnostic procedures for common Chrome integration issues.

## Extension Not Detected

**Symptom:**
```
Error: Chrome extension not detected
Unable to communicate with Claude in Chrome
```

**Diagnostic steps:**

1. **Verify extension installed**
   - Open Chrome → chrome://extensions/
   - Search for "Claude in Chrome"
   - Check version >= 1.0.36

2. **Verify extension enabled**
   - Toggle switch should be ON (blue)
   - If disabled, click to enable
   - Refresh browser

3. **Verify Claude Code version**
   ```bash
   claude --version
   # Should be >= 2.0.73
   ```

4. **Check Chrome is running**
   - Chrome must be open (not just running in background)
   - Open visible Chrome window

5. **Reconnect extension**
   ```bash
   # In Claude Code session:
   /chrome
   # Select: "Reconnect extension"
   ```

6. **Restart both**
   - Quit Chrome completely
   - Exit Claude Code (Ctrl+D)
   - Start Claude Code: `claude --chrome`
   - Open Chrome

7. **Check native messaging host**
   - First-time setup installs messaging host
   - On macOS: `~/Library/Application Support/Google/Chrome/NativeMessagingHosts/`
   - If permission errors, restart Chrome

**Resolution:**
99% of cases resolve with step 5 (reconnect) or step 6 (restart both).

## Browser Not Responding

**Symptom:**
```
Commands sent but browser doesn't respond
Navigation/clicks don't execute
```

**Diagnostic steps:**

1. **Check for modal dialogs**
   - Look for JavaScript alert/confirm/prompt
   - These BLOCK all browser events
   - Manually dismiss dialog
   - Tell Claude: "Dialog dismissed, continue"

2. **Check if tab crashed**
   - Tab shows "Aw, Snap!" or "He's Dead, Jim"
   - Create new tab: `tabs_create_mcp()`
   - Navigate to fresh URL

3. **Check if page loading**
   - Look for loading spinner
   - Wait 5-10 seconds
   - Use: `computer(action="wait", duration=5, tabId=<id>)`

4. **Check console for errors**
   ```
   read_console_messages(tabId=<id>, onlyErrors=true)
   ```
   - Script errors can block interaction
   - Report errors to user

5. **Create fresh tab**
   ```
   tabs_create_mcp()
   navigate(url="<url>", tabId=<new-id>)
   ```

6. **Restart extension**
   - Chrome → chrome://extensions/
   - Toggle "Claude in Chrome" OFF then ON
   - Retry operation

**Resolution:**
Modal dialogs (step 1) cause 80% of "not responding" issues.

## Console/Network Requests Not Appearing

**Symptom:**
```
read_console_messages returns empty
read_network_requests returns empty
Even though errors visible in browser DevTools
```

**Diagnostic steps:**

1. **Verify page fully loaded**
   ```
   navigate(url="...", tabId=<id>)
   computer(action="wait", duration=3, tabId=<id>)  ← CRITICAL
   read_console_messages(tabId=<id>)
   ```
   - Console logs accumulate during page load
   - Wait 2-3 seconds after navigation

2. **Check filter patterns**
   ```
   # Too restrictive?
   read_console_messages(
     tabId=<id>,
     pattern="very-specific-error"  ← May not match
   )

   # Try without filter first
   read_console_messages(tabId=<id>)
   ```

3. **Check URL pattern**
   ```
   # Too specific?
   read_network_requests(
     tabId=<id>,
     urlPattern="/api/v1/specific/endpoint"  ← May miss variations
   )

   # Try broader pattern
   read_network_requests(tabId=<id>, urlPattern="/api/")
   ```

4. **Check status filter**
   ```
   # Missing successful requests?
   read_network_requests(
     tabId=<id>,
     filterStatus=[500]  ← Only server errors
   )

   # Try without filter
   read_network_requests(tabId=<id>)
   ```

5. **Trigger action that generates logs**
   ```
   # Console may be empty if no errors yet
   navigate(url="...", tabId=<id>)
   computer(action="left_click", ref="submit", tabId=<id>)  ← Trigger
   computer(action="wait", duration=2, tabId=<id>)
   read_console_messages(tabId=<id>)
   ```

6. **Check if logs cleared**
   - Some SPAs clear console on navigation
   - Read console immediately after event
   - Don't wait too long between action and reading

**Resolution:**
90% caused by not waiting after navigation (step 1) or overly restrictive filters (steps 2-4).

## Form Input Not Working

**Symptom:**
```
form_input executes but field remains empty
No error but value not entered
```

**Diagnostic steps:**

1. **Verify element reference**
   ```
   # Find element first
   find(selector="#email-field", tabId=<id>)
   # Use returned ref in form_input
   form_input(ref="<ref>", value="test@example.com", tabId=<id>)
   ```

2. **Try clicking into field first**
   ```
   computer(action="left_click", ref="email-field", tabId=<id>)
   computer(action="wait", duration=0.5, tabId=<id>)
   form_input(ref="email-field", value="test@example.com", tabId=<id>)
   ```

3. **Use type instead of form_input**
   ```
   # form_input may not work with custom inputs
   computer(action="left_click", ref="email-field", tabId=<id>)
   computer(action="type", text="test@example.com", tabId=<id>)
   ```

4. **Check if field is contenteditable**
   ```
   # Rich text editors require type, not form_input
   computer(action="left_click", ref="editor", tabId=<id>)
   computer(action="type", text="Content here", tabId=<id>)
   ```

5. **Verify field is visible**
   ```
   # Field may be hidden or off-screen
   computer(action="scroll", direction="down", amount=200, tabId=<id>)
   form_input(ref="field", value="...", tabId=<id>)
   ```

6. **Check for JavaScript validation**
   ```
   # Some fields validate on blur
   form_input(ref="email", value="test@example.com", tabId=<id>)
   computer(action="left_click", ref="next-field", tabId=<id>)  ← Trigger blur
   ```

**Resolution:**
Use `computer(action="type")` for rich text editors and custom inputs (step 3).
Use `form_input` for standard HTML form elements.

## Authentication Issues

**Symptom:**
```
Redirected to login page
Cannot access authenticated content
Session appears logged out
```

**Diagnostic steps:**

1. **Verify user is logged in**
   - Check current tab URL
   - If on login page, user must log in manually
   - Claude NEVER handles passwords

2. **Ask user to log in**
   ```
   Assistant: "I see you're on the login page. Please log in manually in
               the browser, then let me know when you're ready to continue."
   User: "I'm logged in"
   Assistant: [Continue workflow]
   ```

3. **Check session cookies**
   - Chrome extension uses browser's cookie jar
   - If logged out in normal browsing, also logged out in automation
   - User must have active session

4. **Handle 2FA/CAPTCHA**
   ```
   navigate(url="https://app.example.com", tabId=<id>)
   # If 2FA appears:
   Assistant: "I see a two-factor authentication prompt. Please complete
               the 2FA challenge, then let me know when you're past it."
   User: "Done"
   Assistant: [Continue]
   ```

5. **Verify correct domain**
   ```
   # Wrong subdomain?
   navigate(url="https://app.example.com", tabId=<id>)  ← Authenticated
   # vs
   navigate(url="https://www.example.com", tabId=<id>)  ← Public site
   ```

6. **Check extension permissions**
   ```
   # In Claude Code:
   /chrome
   # Check "Site permissions"
   # Verify domain is allowed
   ```

**Resolution:**
User must log in manually (steps 1-2). Claude pauses workflow and resumes after authentication complete.

## Tab Context Issues

**Symptom:**
```
Error: No tab context available
Invalid tabId
```

**Diagnostic steps:**

1. **Call tabs_context_mcp first**
   ```
   # WRONG - Missing tab context
   navigate(url="...", tabId=123)  ← Where did tabId come from?

   # CORRECT
   tabs_context_mcp(createIfEmpty=true)
   # Returns: { tabId: 456, url: "...", title: "..." }
   navigate(url="...", tabId=456)
   ```

2. **Use createIfEmpty parameter**
   ```
   tabs_context_mcp(createIfEmpty=true)
   # Creates new tab if none exist
   ```

3. **Store tabId from response**
   ```
   response = tabs_context_mcp()
   tabId = response.tabId
   navigate(url="...", tabId=tabId)
   ```

4. **Create explicit new tab**
   ```
   response = tabs_create_mcp()
   newTabId = response.tabId
   navigate(url="...", tabId=newTabId)
   ```

5. **Don't reuse closed tab IDs**
   ```
   browser_close(tabId=123)
   navigate(url="...", tabId=123)  ← ERROR: Tab closed

   # Get fresh tab:
   tabs_context_mcp(createIfEmpty=true)
   ```

**Resolution:**
ALWAYS call `tabs_context_mcp()` before any browser operation. This is non-negotiable.

## GIF Recording Issues

**Symptom:**
```
GIF appears empty
GIF has no frames
GIF export fails
```

**Diagnostic steps:**

1. **Verify screenshot after start**
   ```
   # WRONG
   gif_creator(action="start_recording", tabId=<id>)
   [actions]  ← Missing first frame!
   gif_creator(action="stop_recording", tabId=<id>)

   # CORRECT
   gif_creator(action="start_recording", tabId=<id>)
   computer(action="screenshot", tabId=<id>)  ← REQUIRED
   [actions]
   computer(action="screenshot", tabId=<id>)  ← REQUIRED
   gif_creator(action="stop_recording", tabId=<id>)
   ```

2. **Check recording duration**
   ```
   # Too short (< 5 seconds) may have encoding issues
   # Too long (> 90 seconds) creates huge files
   # Optimal: 30-60 seconds
   ```

3. **Verify export options**
   ```
   gif_creator(
     action="export",
     tabId=<id>,
     download=true,  ← Must be true to save
     filename="tutorial.gif",
     options={ quality: 10 }
   )
   ```

4. **Check file size**
   ```
   # quality=5 (low) → Larger files
   # quality=10 (medium) → Balanced
   # quality=20+ (high) → Smaller files but slow encoding
   ```

5. **Wait for encoding**
   ```
   # High quality settings take time
   # quality=30 with 60-second recording may take 30+ seconds
   # Be patient, don't cancel
   ```

**Resolution:**
Missing screenshot calls (step 1) cause 95% of empty GIF issues.

## Network Request Filtering

**Symptom:**
```
Expected network request not in results
Filtered too many requests
```

**Diagnostic steps:**

1. **Start with no filters**
   ```
   # Get ALL requests first
   all_requests = read_network_requests(tabId=<id>)
   # Examine results
   # Then add filters incrementally
   ```

2. **Check URL pattern is regex**
   ```
   # WRONG (not a regex)
   read_network_requests(tabId=<id>, urlPattern="api/users")

   # CORRECT (regex)
   read_network_requests(tabId=<id>, urlPattern="/api/users")
   read_network_requests(tabId=<id>, urlPattern=".*api.*users")
   ```

3. **Verify status codes**
   ```
   # filterStatus is array, not single value
   read_network_requests(
     tabId=<id>,
     filterStatus=[401, 403]  ← Array
   )
   ```

4. **Check request timing**
   ```
   # Requests only captured while monitoring
   # If request happened before read_network_requests, won't appear

   # Solution: Read before and after action
   navigate(url="...", tabId=<id>)
   computer(action="left_click", ref="submit", tabId=<id>)
   computer(action="wait", duration=2, tabId=<id>)  ← Let request complete
   read_network_requests(tabId=<id>)
   ```

5. **Check for preflight requests**
   ```
   # CORS preflight (OPTIONS) appears as separate request
   # Look for both OPTIONS and actual request
   read_network_requests(tabId=<id>, urlPattern="/api/")
   # May return:
   # - OPTIONS /api/users (preflight)
   # - POST /api/users (actual request)
   ```

**Resolution:**
Start with no filters, examine results, then refine (step 1).

## Performance Issues

**Symptom:**
```
Browser operations very slow
Commands take 10+ seconds
```

**Diagnostic steps:**

1. **Check network latency**
   ```
   # Slow page loads affect all operations
   read_network_requests(tabId=<id>)
   # Check timing.waiting (time to first byte)
   # > 5000ms indicates slow server/network
   ```

2. **Reduce console log volume**
   ```
   # Reading 1000s of logs is slow
   read_console_messages(
     tabId=<id>,
     onlyErrors=true  ← Filter at source
   )
   ```

3. **Filter network requests**
   ```
   # Reading all requests is slow on heavy pages
   read_network_requests(
     tabId=<id>,
     urlPattern="/api/"  ← Limit to API calls
   )
   ```

4. **Wait for page load**
   ```
   # Operating on loading page is slow
   navigate(url="...", tabId=<id>)
   computer(action="wait", duration=3, tabId=<id>)  ← Critical
   [operations]
   ```

5. **Close unused tabs**
   ```
   # Too many open tabs slow down Chrome
   browser_close(tabId=<old-id>)
   ```

6. **Check browser extensions**
   - Other Chrome extensions may conflict
   - Try disabling other extensions temporarily

**Resolution:**
Filter logs/requests at source (steps 2-3) and wait for page loads (step 4).

## Complete Diagnostic Checklist

When user reports "Chrome isn't working":

- [ ] Extension installed and enabled (chrome://extensions/)
- [ ] Claude Code version >= 2.0.73 (`claude --version`)
- [ ] Chrome is running with visible window
- [ ] `/chrome` status shows "Connected"
- [ ] `tabs_context_mcp()` returns valid tabId
- [ ] No modal dialogs blocking page
- [ ] Page fully loaded (waited 2-3 seconds)
- [ ] Filters not too restrictive (tested without filters)
- [ ] Correct input method (form_input vs type)
- [ ] User authenticated if accessing private content

## When to Escalate

If ALL diagnostic steps fail:

1. **Capture diagnostics**
   ```
   claude --version
   /chrome  # Screenshot status
   read_console_messages(tabId=<id>)  # Any errors?
   ```

2. **Try minimal reproduction**
   ```
   tabs_context_mcp(createIfEmpty=true)
   navigate(url="https://example.com", tabId=<id>)
   computer(action="screenshot", tabId=<id>)
   ```
   - If this fails, fundamental connection issue
   - If this works, issue is specific to target site

3. **Check known limitations**
   - WSL not supported
   - Only Google Chrome (not Brave, Arc, etc.)
   - Modal dialogs block automation
   - CAPTCHAs require manual handling

4. **Report to user**
   ```
   "I've completed full diagnostics. The issue appears to be [specific finding].

    Attempted:
    - Extension reconnection
    - Fresh tab creation
    - Minimal reproduction

    Limitation encountered:
    - [WSL not supported / CAPTCHA blocking / etc.]

    Recommendation:
    - [Specific next step]"
   ```
