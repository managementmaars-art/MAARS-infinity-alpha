# Chrome Form Filler - Technical Reference

## Chrome MCP Tools Deep Dive

### tabs_context_mcp

**Purpose:** Get or create tab group context for MCP operations

**Parameters:**
- `createIfEmpty` (boolean): Creates new tab group if none exists

**Returns:**
```json
{
  "tabIds": [123, 124, 125],
  "activeTabId": 123
}
```

**Usage Pattern:**
```javascript
// Always call first to ensure valid tab context
tabs_context_mcp(createIfEmpty=true)
// Extract tabId from response for subsequent calls
```

**Error Handling:**
- No tab group exists and createIfEmpty=false → Error
- Chrome not running → Error
- Extension not installed → Error

### read_page

**Purpose:** Get accessibility tree representation of page elements

**Parameters:**
- `tabId` (number, required): Tab to read from
- `filter` (string): "interactive" or "all" (default: "all")
- `depth` (number): Max tree depth (default: 15)
- `ref_id` (string): Focus on specific element

**Returns:** Accessibility tree with ref IDs for elements

**Usage for Forms:**
```javascript
// Get all interactive elements (inputs, buttons, selects)
read_page(tabId, filter="interactive")

// Focus on specific form section
read_page(tabId, ref_id="ref_5", depth=10)
```

**Form Field Information Extracted:**
- Element type (input, select, textarea, button)
- Input type (text, email, tel, password, etc.)
- Label text
- Placeholder text
- Current value
- Required attribute
- Disabled/readonly state
- Aria attributes

### find

**Purpose:** Find elements using natural language queries

**Parameters:**
- `tabId` (number, required): Tab to search in
- `query` (string, required): Natural language description

**Returns:** Up to 20 matching elements with ref IDs

**Usage Examples:**
```javascript
// Find by purpose
find(tabId, query="email address input field")
find(tabId, query="submit button")
find(tabId, query="phone number field")

// Find by label text
find(tabId, query="First Name")
find(tabId, query="Agree to terms checkbox")

// Find by position
find(tabId, query="first text input")
find(tabId, query="submit button at bottom of form")
```

**Best Practices:**
- Be specific with field purpose
- Include field type when ambiguous
- Use label text from read_page when available

### form_input

**Purpose:** Set values in form elements using ref ID

**Parameters:**
- `tabId` (number, required): Tab containing form
- `ref` (string, required): Element reference ID from read_page/find
- `value` (string/boolean/number, required): Value to set

**Supported Element Types:**

| Element | Value Type | Example |
|---------|-----------|---------|
| Text input | string | `"John Smith"` |
| Email input | string | `"user@example.com"` |
| Tel input | string | `"(555) 123-4567"` |
| Textarea | string | `"Long text content"` |
| Select | string | Option value or text |
| Checkbox | boolean | `true` or `false` |
| Radio | boolean | `true` (to select) |
| Number input | number | `42` |
| Date input | string | `"2024-12-20"` |

**Usage Pattern:**
```javascript
// 1. Find element
find(tabId, query="email input field")
// Returns: ref_3

// 2. Set value
form_input(tabId, ref="ref_3", value="user@example.com")

// 3. Verify (read back)
read_page(tabId, ref_id="ref_3")
// Check value matches
```

**Common Issues:**
- Value doesn't match expected format → Field validation error
- Element disabled/readonly → form_input fails silently
- Dynamic field (appears after interaction) → Re-run find

### computer

**Purpose:** Mouse/keyboard interactions

**Parameters:**
- `tabId` (number, required): Tab to interact with
- `action` (string, required): Action type
- Additional parameters based on action

**Actions for Form Filling:**

**Click (focus field):**
```javascript
computer(tabId, action="left_click", ref="ref_5")
```

**Type text:**
```javascript
computer(tabId, action="type", text="John Smith")
```

**Press key (Tab, Enter, etc.):**
```javascript
computer(tabId, action="key", text="Tab")
computer(tabId, action="key", text="Enter")
```

**Wait (for page updates):**
```javascript
computer(tabId, action="wait", duration=2)
```

**Fallback Strategy:**
When form_input fails, use computer:
1. Click to focus field
2. Clear existing value (Ctrl+A, Delete)
3. Type new value
4. Tab to next field (triggers validation)

### update_plan

**Purpose:** Present approach to user for approval

**Parameters:**
- `domains` (array of strings, required): Domains to be accessed
- `approach` (array of strings, required): High-level steps

**Usage Pattern:**
```javascript
update_plan(
  domains=["example.com"],
  approach=[
    "Identify all form fields on registration page",
    "Fill 8 non-sensitive fields with provided data",
    "Verify each field after filling",
    "Request approval before form submission",
    "Submit form and verify confirmation page"
  ]
)
```

**Best Practices:**
- Call BEFORE reading page or taking actions
- List actual domain from URL
- Keep approach items to 3-7 high-level steps
- Focus on outcomes, not implementation
- User must approve before proceeding

### screenshot

**Purpose:** Capture visual state for verification

**Parameters:**
- `tabId` (number, required): Tab to screenshot

**Usage for Form Filling:**
- Capture filled form before submission
- Document error states
- Verify confirmation pages
- Debug field visibility issues

## Form Field Type Specifications

### Text Input Types

**Detected via input type attribute:**

| Type | Purpose | Validation | Example |
|------|---------|-----------|---------|
| text | General text | None | Name, address |
| email | Email addresses | Email format | user@example.com |
| tel | Phone numbers | Varies by region | (555) 123-4567 |
| url | URLs | URL format | https://example.com |
| search | Search queries | None | "product search" |
| password | Passwords | **NEVER AUTO-FILL** | ******** |
| number | Numeric values | Number range | 42 |
| date | Date values | Date format | 2024-12-20 |
| time | Time values | Time format | 14:30 |
| datetime-local | Date+time | DateTime format | 2024-12-20T14:30 |

### Sensitive Field Detection

**NEVER auto-fill these fields:**

**By input type:**
- `type="password"`

**By name attribute (case-insensitive regex):**
- `/password/i`
- `/pwd/i`
- `/cc/i` (credit card)
- `/card/i`
- `/cvv/i`
- `/ssn/i`
- `/social/i`
- `/bank/i`
- `/account.*number/i`
- `/routing/i`

**By label text:**
- Contains "password"
- Contains "credit card"
- Contains "CVV" or "CVC"
- Contains "SSN" or "Social Security"
- Contains "bank account"
- Contains "PIN"

**By autocomplete attribute:**
- `autocomplete="cc-number"`
- `autocomplete="cc-exp"`
- `autocomplete="cc-csc"`
- `autocomplete="current-password"`
- `autocomplete="new-password"`

### Select Dropdowns

**Setting values:**

**Option 1: By value attribute**
```javascript
// <select><option value="us">United States</option></select>
form_input(tabId, ref="ref_country", value="us")
```

**Option 2: By visible text**
```javascript
form_input(tabId, ref="ref_country", value="United States")
```

**Verification:**
Read back selected option text or value.

### Checkboxes and Radio Buttons

**Checkboxes:**
```javascript
// Check a checkbox
form_input(tabId, ref="ref_terms", value=true)

// Uncheck a checkbox
form_input(tabId, ref="ref_terms", value=false)
```

**Radio buttons:**
```javascript
// Select a radio button
form_input(tabId, ref="ref_option_a", value=true)

// Or click with computer tool
computer(tabId, action="left_click", ref="ref_option_a")
```

**Verification:**
Check `checked` attribute or aria-checked state.

### Textarea

**Multi-line text input:**
```javascript
form_input(tabId, ref="ref_message", value="Line 1\nLine 2\nLine 3")
```

**Character limits:**
- Check `maxlength` attribute
- Truncate value if needed
- Report to user if content exceeds limit

## Permission Workflow Patterns

### Five-Phase Permission Model

**Phase 1: Plan Approval**
```
Tool: update_plan
User Action: Approve approach
Gate: Cannot proceed without approval
```

**Phase 2: Field Mapping Approval**
```
Present: All fields to be filled
Present: Which data maps to which field
Present: Sensitive fields requiring manual entry
User Action: Approve or request changes
Gate: Cannot fill without approval
```

**Phase 3: Incremental Filling**
```
For each field:
  Fill → Verify → Report
No additional approval per field
User can interrupt at any time
```

**Phase 4: Pre-Submission Review**
```
Present: Complete form state
Present: All filled values
Present: Empty sensitive fields
User Action: Approve, edit, or cancel
Gate: Cannot submit without approval
```

**Phase 5: Post-Submission Verification**
```
Verify: Success or failure
Report: Confirmation details or errors
No user action required (informational)
```

### Progressive Disclosure Pattern

**Initial Request:**
Show only summary (field count, form name)

**After Plan Approval:**
Show all fields with mapping

**During Filling:**
Show only current field status

**Before Submission:**
Show complete form state

**After Submission:**
Show confirmation or error details

### Error Recovery Permission

**Field Filling Error:**
```
Report: "Failed to fill [field name]: [reason]"
Ask: "Try alternative method? (yes/retry/skip)"
Wait: User decision
```

**Validation Error After Submission:**
```
Report: "Form rejected: [error messages]"
Present: Fields needing correction
Ask: "Correct and resubmit? (yes/edit/cancel)"
Wait: User decision
```

## Error Handling Strategies

### Field Filling Failures

**Failure: Element not found**
```
Cause: Dynamic page, element hidden, incorrect query
Recovery:
  1. Re-scan page (read_page)
  2. Try broader find query
  3. Ask user to describe field location
  4. Use screenshot to debug
```

**Failure: Value not accepted**
```
Cause: Format validation, disabled field, readonly
Recovery:
  1. Check field attributes (disabled, readonly, pattern)
  2. Validate value format
  3. Try alternative format
  4. Report to user for manual entry
```

**Failure: Verification mismatch**
```
Cause: Value transformed (formatting), race condition
Recovery:
  1. Wait briefly (computer wait)
  2. Re-read value
  3. Accept close matches (phone formatting)
  4. Retry fill if significantly different
```

### Submission Failures

**Failure: Submit button not found**
```
Recovery:
  1. Search for common patterns: "submit", "send", "continue"
  2. Look for button with type="submit"
  3. Find form element, press Enter
  4. Ask user to describe button
```

**Failure: Form validation errors appear**
```
Recovery:
  1. Read error messages
  2. Map errors to specific fields
  3. Report to user with field names
  4. Request corrected values
  5. Re-fill and re-verify
  6. Request submission approval again
```

**Failure: Network error during submission**
```
Recovery:
  1. Wait for page to stabilize
  2. Check if form still present
  3. Verify values still filled
  4. Offer retry to user
  5. If values lost, offer re-fill
```

### Verification Failures

**Failure: Confirmation page not detected**
```
Recovery:
  1. Wait longer (page may be slow)
  2. Read current page
  3. Look for common patterns:
     - "thank you"
     - "confirmation"
     - "success"
     - "submitted"
  4. Check URL change
  5. Ask user if submission succeeded
```

**Failure: Error message appears**
```
Recovery:
  1. Extract error text
  2. Present to user
  3. Determine if correctable
  4. Offer to retry or abort
```

## Validation Checklist Templates

### Pre-Fill Validation

```
Field Discovery Complete:
- [ ] All visible fields identified
- [ ] Field types correctly detected
- [ ] Labels extracted or inferred
- [ ] Required fields marked
- [ ] Sensitive fields flagged

Data Mapping Ready:
- [ ] User data available for all required fields
- [ ] Data formats validated
- [ ] Sensitive fields excluded from automation
- [ ] Optional fields handling decided

User Approvals Obtained:
- [ ] update_plan approved
- [ ] Field mapping approved
- [ ] User aware of sensitive field exclusions
```

### Per-Field Validation

```
For each field:
- [ ] Element reference obtained
- [ ] Value set successfully
- [ ] Verification read performed
- [ ] Value matches expected
- [ ] No error messages appeared
- [ ] Field visual state correct (not red/error)
```

### Pre-Submission Validation

```
Form Complete Check:
- [ ] All required fields filled
- [ ] All values verified correct
- [ ] No error messages on page
- [ ] Submit button visible and enabled
- [ ] User reviewed complete form state
- [ ] User approved submission

Sensitive Field Check:
- [ ] Sensitive fields identified
- [ ] User informed of manual requirement
- [ ] User confirmed sensitive fields complete
```

### Post-Submission Validation

```
Submission Verification:
- [ ] Page navigated or updated
- [ ] No error messages present
- [ ] Confirmation indicator found
- [ ] Confirmation details extracted
- [ ] User informed of outcome
```

## Common Field Patterns

### Name Fields

**Variations:**
- Single "Full Name" field
- Separate "First Name" + "Last Name"
- "First" + "Middle" + "Last"
- "Title" + "First" + "Last"

**Strategy:**
- Detect by label text
- Split full name if needed
- Handle optional middle name

### Address Fields

**Common Structure:**
- Street Address (line 1)
- Apartment/Suite (line 2, optional)
- City
- State/Province (select or text)
- Zip/Postal Code
- Country (select, often)

**Strategy:**
- Identify by label keywords
- Handle optional address line 2
- State: check if select (dropdown) or text
- Country: use value or text matching

### Contact Fields

**Email:**
- Type: email
- Validation: required format
- Common labels: "Email", "Email Address"

**Phone:**
- Type: tel
- Format: varies (allow any format)
- Common labels: "Phone", "Phone Number", "Mobile"

**Strategy:**
- Validate email format before filling
- Accept any phone format (let field validate)

### Consent Fields

**Common Patterns:**
- "I agree to Terms and Conditions" (checkbox)
- "Subscribe to newsletter" (checkbox)
- "I am over 18" (checkbox)

**Strategy:**
- Identify by checkbox + label text
- ALWAYS get user approval for consent
- Default to unchecked unless user specifies

### Multi-Step Forms

**Detection:**
- "Step 1 of 3" indicator
- "Next" or "Continue" buttons (not "Submit")
- Progress bar
- Tabs or sections

**Strategy:**
- Treat each step as separate workflow
- Click "Next" after step completion
- Re-run field discovery on new step
- Track progress for user

## Integration Patterns

### With Form Data Sources

**From User Message:**
```
User: "Fill with: Name=John, Email=john@example.com"
Parse into key-value mapping
```

**From Structured Data:**
```
User provides JSON/CSV with field mappings
Parse and map to form fields
```

**From Previous Interaction:**
```
Reference data from earlier in conversation
Ask user to confirm still valid
```

### With Multi-Page Workflows

**Pattern:**
```
Page 1: Personal Info
  → Fill, verify, click "Next"
Page 2: Address Info
  → Fill, verify, click "Next"
Page 3: Confirmation
  → Review, click "Submit"
```

**Implementation:**
```
For each page:
  1. read_page to identify fields
  2. Map data to fields
  3. Fill and verify
  4. Find and click "Next/Continue"
  5. Wait for navigation
  6. Repeat until final submit
```

### With Dynamic Forms

**Conditional Fields:**
```
Example: "Do you have a company?" → Yes reveals "Company Name" field

Strategy:
1. Fill trigger field first
2. Wait for page update
3. Re-scan for new fields
4. Fill conditional fields
5. Verify all visible fields
```

**Auto-Complete/Search Fields:**
```
Example: Address autocomplete, search-as-you-type

Strategy:
1. Type partial value
2. Wait for suggestions
3. Use computer tool to select from dropdown
4. Verify final value
```
