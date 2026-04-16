# Case File Format Specification

Complete specification for E2E test case YAML files.

## Quick Reference

```yaml
# Minimal case structure
id: case-name
title: Human readable title
category: foundation | flow | composition

steps:
  - desc: Step description
    commands:
      - agent-browser open {{env.base_url}}
      - agent-browser click {{role: button, name: "Submit"}}
    expect:
      - element_visible: {{role: heading, name: "Success"}}

# Semantic selectors
{{role: button, name: "Submit"}}              # Basic
{{role: textbox, name: /Email|Username/}}     # Regex
{{role: button, name: "Delete", index: 0}}    # First match

# Common roles: button, link, textbox, heading, navigation, alert, dialog

# Environment variables
parameters:
  base_url: http://localhost:3000
# Use as: {{env.base_url}}
```

---

## File Lean Principle

**Keep test case files focused on execution, not exploration history.**

### What Belongs in Test Case YAML

✅ **Execution essentials**:

- Case metadata (id, title, category, tags)
- Parameters and configuration
- Steps with commands
- Expectations
- Composability info (provides, composable_with)
- **Minimal** exploration metadata (status, timestamp, link to session log)

❌ **What does NOT belong** (put in exploration session files):

- Detailed element discovery notes
- All discovered elements with refs
- Exploration attempts and iterations
- Screenshots and snapshot paths
- Timing observations
- Fallback strategies tested
- "Next steps" planning

### Before/After Example

**Before (bloated - 183 lines)**:

```yaml
id: agent-login
# ... 30 lines of steps ...
exploration:
  status: validated
  discovered_elements: # ❌ 50+ lines
    login_page: [...]
    password_page: [...]
  exploration_notes: | # ❌ 30+ lines
    Full exploration history...
  screenshots: [...] # ❌ Metadata clutter
```

**After (lean - 60 lines)**:

```yaml
id: agent-login
# ... 30 lines of steps ...
exploration:
  status: validated
  explored_by: username
  explored_at: 2026-01-28T10:00:00Z
  session_log: docs/exploration/EXPLORATION_SESSION_agent-login_20260128.md
```

**Exploration details** → `docs/exploration/EXPLORATION_SESSION_agent-login_20260128.md`

---

## Single Case Structure

### Minimal Format (Recommended)

Agent-focused structure with only execution essentials:

```yaml
id: case-name                    # Must match filename
title: Human-readable title
category: foundation | flow | composition

description: |
  What this case does and when to use it.
  Agent reads this to understand context.

parameters:
  param_name: default_value      # Simple key-value with inline comments
  environment: qa                # qa | dev | staging | prod

steps:
  - desc: Step description
    commands:
      - agent-browser open {{env.URL}} --headed
      - agent-browser fill {{role: textbox, name: "Email"}} "{{env.EMAIL}}"
    expect:                      # Optional
      - url_contains: /dashboard
      - element_visible: {{role: heading, name: "Dashboard"}}
    optional: true               # Optional - step can be skipped

exploration:
  status: validated              # draft | explored | validated | stable
  session_log: docs/exploration/EXPLORATION_SESSION_*.md
```

### What We Removed (Over-engineered)

❌ **Removed fields** (not needed for agent execution):

- `priority` - Project management, not execution
- `tags` - Search/categorization metadata
- `parameters.type/options/description` - Over-structured, agent understands from context
- `provides` - Abstract metadata, agent knows from description
- `composable_with` - Discovery feature, not execution
- `examples` - Documentation, agent already has parameters
- `exploration.explored_by/explored_at/environment` - Only need status and log link

✅ **Kept essentials** (agent needs these):

- `id/title/category` - Identity and classification
- `description` - Context for agent
- `parameters` - Simple defaults with inline comments
- `steps` - The actual execution instructions
- `exploration.status/session_log` - Validation status and reference

### Extended Format (Only When Needed)

For complex compositions with multi-session scenarios:

```yaml
id: composition-name
title: Multi-step scenario
category: composition
dependencies: [case1, case2] # Required cases

composed_of:
  - ref: foundations/agent-login
    as: agent1_login
    with: # Override parameters
      environment: staging

sessions:
  - name: agent1
    lifecycle: persistent # persistent | ephemeral | restartable

session_scope: composition # case | composition | explicit

steps:
  - desc: Both agents login
    parallel: # Run in parallel
      - run: agent1_login
        session: agent1
```

## Semantic Selector Syntax

### Basic Format

```yaml
{ { property: value } }
```

### Common Properties

| Property      | Description       | Example                          |
| ------------- | ----------------- | -------------------------------- |
| `role`        | ARIA role         | `{{role: button}}`               |
| `name`        | Accessible name   | `{{name: "Submit"}}`             |
| `placeholder` | Input placeholder | `{{placeholder: "Enter email"}}` |
| `aria-label`  | ARIA label        | `{{aria-label: "Close dialog"}}` |
| `type`        | Input type        | `{{type: "email"}}`              |

### Single Property

```yaml
{{role: button}}
{{name: "Submit"}}
{{placeholder: "Search..."}}
```

### Multiple Properties (AND logic)

```yaml
# All properties must match
{{role: textbox, name: "Email", type: "email"}}
{{role: button, name: "Submit", type: "submit"}}
```

### Fallback Chain (OR logic)

```yaml
# Try first selector, fall back to second if not found
{{role: button, name: "Sign In"}} | {{role: button, name: "Login"}}

# Chain multiple fallbacks
{{name: "Submit"}} | {{role: button, type: "submit"}} | {{aria-label: "Submit form"}}
```

### Regex Matching

```yaml
# Case-insensitive match
{{role: link, name: /SDK/i}}

# Pattern matching
{{role: button, name: /^Submit|Send$/}}
```

### Indexing (when multiple matches)

```yaml
# First match
{{role: link, name: "Product", index: 0}}

# Third match
{{role: button, name: "Delete", index: 2}}
```

## Resolution Workflow

**At exploration time:**

```bash
agent-browser snapshot -i --json
# Returns: @e42 [button role="button" name="Submit" type="submit"]
```

**Store in YAML:**

```yaml
commands:
  - agent-browser click {{role: button, name: "Submit"}}
```

**At execution time:**

```bash
1. agent-browser snapshot -i --json
2. Match {{role: button, name: "Submit"}} to current refs
3. Found: @e67 [button role="button" name="Submit"]
4. Execute: agent-browser click @e67
```

## Why NOT These Selectors

```yaml
# ❌ BAD - Implementation details, unstable
{{dataTestId: "submit-btn"}}      # Changes with refactor
{{class: "btn-primary"}}          # Changes with styling
{{id: "login-form"}}              # Changes with markup
{{css: ".auth-form button"}}      # Fragile selector

# ✅ GOOD - User-visible behavior, stable
{{role: button, name: "Submit"}}
{{role: form, name: "Login"}}
{{placeholder: "Enter email"}}
```

## Environment Variables

Use `{{env.VAR}}` for configuration:

```yaml
steps:
  - desc: Navigate to login
    commands:
      - agent-browser open {{env.LOGIN_URL}} --headed

  - desc: Enter credentials
    commands:
      - agent-browser fill {{role: textbox, name: "Email"}} "{{env.AGENT_EMAIL}}"
      - agent-browser fill {{role: textbox, name: "Password"}} "{{env.AGENT_PASSWORD}}"
```

**Environment file** (`.env.e2e`):

```bash
LOGIN_URL=https://app.zoom.us/login
AGENT_EMAIL=agent1@zoom.us
AGENT_PASSWORD=secret123
AGENT2_EMAIL=agent2@zoom.us
```

## Expectations

```yaml
expect:
  # URL checks
  - url_contains: /dashboard
  - url_equals: https://app.zoom.us/dashboard
  - url_matches: /dashboard\?.*$/

  # Element checks
  - element_visible: { { role: heading, name: "Dashboard" } }
  - element_exists: { { role: button, name: "Logout" } }
  - element_not_visible: { { role: alert, name: "Error" } }

  # Text checks
  - text_contains: "Welcome"
  - text_equals: "Login successful"

  # State checks
  - session_active: true
  - cookies_set: [session_token]
```

## Provides Section

Declare what this case provides for composition:

```yaml
provides:
  # Boolean flags
  - agent_authenticated: true
  - session_active: true

  # Values
  - agent_id: "{{result.agent_id}}"
  - call_id: "{{result.call_id}}"

  # Objects
  - agent:
      id: "{{result.agent_id}}"
      email: "{{env.AGENT_EMAIL}}"
      status: "Available"
```

## Composable With

List cases that can follow this one:

```yaml
composable_with:
  - agent-logout # Can logout after login
  - make-call # Can make call after login
  - receive-call # Can receive call after login
```

## Composition Structure

```yaml
id: composition-name
title: Multi-step scenario
category: composition

# Reference other cases
composed_of:
  - ref: foundations/agent-login
    as: agent1_login # Alias for this instance

  - ref: foundations/agent-login
    as: agent2_login
    with: # Override variables
      env.AGENT_EMAIL: "{{env.AGENT2_EMAIL}}"

  - ref: flows/voice/make-call
    as: initiate_call

# Session declarations
sessions:
  - name: agent1
    lifecycle: persistent # Lives for whole composition
  - name: agent2
    lifecycle: ephemeral # Short-lived
    close_after: transfer_complete
  - name: customer
    lifecycle: restartable # Survives restart
    profile: ./profiles/customer

# Orchestration
steps:
  - desc: Both agents login
    parallel: # Run in parallel
      - run: agent1_login
        session: agent1
      - run: agent2_login
        session: agent2

  - desc: Agent1 makes call
    run: initiate_call
    session: agent1
    with: # Pass variables
      target: customer
```

## Session Declaration

```yaml
sessions:
  # Persistent - stays open
  - name: agent1
    lifecycle: persistent

  # Ephemeral - auto-closes
  - name: temp_agent
    lifecycle: ephemeral
    close_after: step_name # Close after this step

  # Restartable - uses profile
  - name: agent_persistent
    lifecycle: restartable
    profile: ./profiles/agent1 # Browser profile path
```

## Session Scope

```yaml
# Case-level (default for single cases)
session_scope: case
# Closes all sessions at end of case

# Composition-level (for multi-step scenarios)
session_scope: composition
# Closes at end of composition

# Explicit (manual control)
session_scope: explicit
# Agent decides when to close
```

## Step with Session Control

```yaml
steps:
  - desc: Agent1 transfers to Agent2
    sessions_used: [agent1, agent2] # Which sessions are active
    run: transfer_call
    on_complete:
      close: [agent1] # Close these sessions after step
      save_state: [agent2] # Save state for these sessions
```

## Parallel Execution

```yaml
steps:
  - desc: Multiple agents login
    parallel:
      - run: agent1_login
        session: agent1
      - run: agent2_login
        session: agent2
      - run: agent3_login
        session: agent3
```

## Variable Overrides

```yaml
# In composed_of
composed_of:
  - ref: foundations/agent-login
    as: agent2_login
    with:
      env.AGENT_EMAIL: "{{env.AGENT2_EMAIL}}"
      env.AGENT_PASSWORD: "{{env.AGENT2_PASSWORD}}"

# In steps
steps:
  - run: make_call
    with:
      target_number: "+1234567890"
      call_type: "direct"
```

## Exploration Metadata

**Keep test case files lean.** Detailed exploration notes go in `docs/exploration/` session files.

### Minimal Format (Recommended)

```yaml
exploration:
  status: validated
  explored_by: username
  explored_at: 2026-01-28T10:00:00Z
  session_log: docs/exploration/EXPLORATION_SESSION_agent-login_20260128.md
```

### Extended Format (Only if Needed)

Use only for critical discoveries that affect test execution:

```yaml
exploration:
  status: validated
  explored_at: 2026-01-28T10:00:00Z
  notes: |
    Critical: Post-login prompt appears ~30% of time.
    Must handle optional step.
```

### What Goes Where

**In test case YAML** (minimal):

- Execution status (draft/validated/stable)
- Timestamp and explorer name
- Link to detailed exploration session

**In exploration session file** (detailed):

- All discovered elements with refs
- Exploration notes and attempts
- Screenshots and snapshots
- Timing observations
- Fallback strategies tested

See "Document" section in SKILL.md for exploration session format.

## Complete Example: Foundation Case

```yaml
id: agent-login
title: Agent login to CCI system
category: foundation
tags: [auth, prerequisite, foundation]
dependencies: []

description: |
  Login to the CCI agent workspace with credentials.
  This is a foundation case used by many other flows.

steps:
  - desc: Navigate to login page
    commands:
      - agent-browser open {{env.LOGIN_URL}} --headed
      - agent-browser wait --load networkidle

  - desc: Enter credentials
    commands:
      - agent-browser fill {{role: textbox, name: "Email"}} "{{env.AGENT_EMAIL}}"
      - agent-browser fill {{role: textbox, name: "Password"}} "{{env.AGENT_PASSWORD}}"

  - desc: Submit login
    commands:
      - agent-browser click {{role: button, name: "Sign In"}}
      - agent-browser wait --load networkidle
    expect:
      - url_contains: /dashboard
      - element_visible: {{role: heading, name: "Dashboard"}}

provides:
  - agent_authenticated: true
  - session: active
  - agent_id: "{{result.agent_id}}"

composable_with: [agent-logout, make-call, receive-call, change-status]

exploration:
  status: validated
  explored_by: username
  explored_at: 2026-01-28T10:00:00Z
  session_log: docs/exploration/EXPLORATION_SESSION_agent-login_20260128.md
```

## Complete Example: Composition

```yaml
id: warm-transfer-flow
title: Warm transfer between two agents
category: composition
tags: [voice, transfer, multi-agent]

description: |
  Agent1 receives call, initiates warm transfer to Agent2,
  speaks with Agent2, then completes transfer.

composed_of:
  - ref: foundations/agent-login
    as: agent1_login
  - ref: foundations/agent-login
    as: agent2_login
    with:
      env.AGENT_EMAIL: "{{env.AGENT2_EMAIL}}"
      env.AGENT_PASSWORD: "{{env.AGENT2_PASSWORD}}"
  - ref: flows/voice/receive-call
    as: initial_call
  - ref: flows/voice/initiate-warm-transfer
    as: start_transfer

sessions:
  - name: agent1
    lifecycle: persistent
  - name: agent2
    lifecycle: ephemeral
    close_after: transfer_complete
  - name: customer
    lifecycle: persistent

session_scope: composition

steps:
  - desc: Both agents login
    parallel:
      - run: agent1_login
        session: agent1
      - run: agent2_login
        session: agent2

  - desc: Agent1 receives call from customer
    sessions_used: [agent1, customer]
    run: initial_call
    session: agent1

  - desc: Agent1 initiates warm transfer
    sessions_used: [agent1, agent2, customer]
    run: start_transfer
    session: agent1
    with:
      target_agent: agent2

  - desc: Transfer completes
    sessions_used: [agent2, customer]
    on_complete:
      close: [agent1]
      save_state: [agent2, customer]

provides:
  - transfer_completed: true
  - agent2_has_customer: true

exploration:
  status: validated
  explored_by: username
  explored_at: 2026-01-28T10:00:00Z
  session_log: docs/exploration/EXPLORATION_SESSION_warm-transfer_20260128.md
```
