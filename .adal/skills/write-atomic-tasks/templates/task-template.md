# Task Template

Use this template when writing new tasks to ensure all SMART+ components are included.

## Basic Task Template

```markdown
- [ ] Task N: [ACTION VERB] [SPECIFIC TARGET] [SUCCESS CRITERIA]
      Location: [full/path/from/project/root/file.py:Class.method]
      Verify: [command to run] (expected outcome)
```

## Detailed Task Template (Recommended)

```markdown
- [ ] Task N: [ACTION VERB] [SPECIFIC TARGET] [DETAILED BEHAVIOR]
      [OPTIONAL: Additional implementation details as bullet points]
      - Detail 1
      - Detail 2
      Location: [full/path/from/project/root/file.py:Class.method]
      Tests: [path/to/test/file.py]
      Test cases:
        - test_case_1: Description
        - test_case_2: Description
      Verify: [command to run] (expected outcome)
      Context: [WHY this task matters - link to ADR/issue/parent task]
```

## Complete Example (Copy-Paste Ready)

```markdown
- [ ] Task 1: Add ConnectionError retry logic to ClaudeAgentClient.query()
      - Retry 3 times with exponential backoff (1s, 2s, 4s)
      - Raise AgentConnectionError after retries exhausted
      - Log retry attempts at warning level
      Location: src/temet_run/agent/client.py:ClaudeAgentClient.query
      Tests: tests/unit/agent/test_client_retry.py
      Test cases:
        - test_retry_connection_error: Retries 3 times on ConnectionError
        - test_exponential_backoff: Delays are 1s, 2s, 4s
        - test_retry_exhausted: Raises AgentConnectionError after max retries
      Verify: pytest tests/unit/agent/test_client_retry.py passes (100% coverage)
      Context: Fixes #342 - daemon crashes on network timeouts
```

## Field Explanations

### Task N: [Title Line]

**Format:** `Task N: [ACTION VERB] [SPECIFIC TARGET] [SUCCESS CRITERIA]`

**Action Verbs (use these):**
- **Create** - Make new file/class/function
- **Add** - Add new functionality to existing code
- **Modify** - Change existing behavior
- **Remove** - Delete code/functionality
- **Rename** - Change names (variables, functions, files)
- **Extract** - Pull logic out into separate component
- **Move** - Relocate code to different file/module

**Examples:**
- ✅ `Task 1: Add retry logic to ClaudeAgentClient.query()`
- ✅ `Task 2: Create ConversationTurn dataclass in types/conversation.py`
- ✅ `Task 3: Extract daemon lifecycle into DaemonManager class`

**Avoid:**
- ❌ `Task 1: Fix the bug` (too vague)
- ❌ `Task 2: Update the code` (what code?)
- ❌ `Task 3: Implement the feature` (which feature?)

---

### Location: [file paths]

**Format:** `Location: path/from/project/root/file.py:Class.method`

**Examples:**
- ✅ `Location: src/temet_run/agent/client.py:ClaudeAgentClient.query`
- ✅ `Location: tests/unit/agent/test_client.py`
- ✅ `Location: src/temet_run/main.py (agents command group, line 145)`

**Multiple Locations:**
```markdown
Location:
  - src/temet_run/agent/client.py:ClaudeAgentClient.__init__
  - src/temet_run/config/settings.py:AgentSettings (add retry_config field)
```

---

### Tests: [test file path]

**Format:** `Tests: path/to/test_file.py`

**Examples:**
- ✅ `Tests: tests/unit/agent/test_client_retry.py`
- ✅ `Tests: tests/integration/test_daemon_lifecycle.py`

**When to include:**
- Always include for implementation tasks
- Specify new test file if tests don't exist yet
- Specify existing test file if adding to existing tests

---

### Test cases: [list]

**Format:** List of test functions with brief description

**Example:**
```markdown
Test cases:
  - test_valid_construction: User and assistant roles both work
  - test_invalid_role: Role="invalid" raises ValueError
  - test_immutability: Frozen dataclass prevents modification
  - test_serialization: to_dict() returns correct structure
```

**When to include:**
- Required for new functionality
- Optional for simple changes (like renaming)
- List all major test scenarios

---

### Verify: [command and expected outcome]

**Format:** `Verify: [exact command to run] ([expected result])`

**Examples:**
- ✅ `Verify: pytest tests/unit/agent/test_client.py passes`
- ✅ `Verify: mypy src/ --strict (0 errors)`
- ✅ `Verify: uv run temet-run agents history --help (shows usage)`
- ✅ `Verify: pytest-benchmark shows <500ms for 10k queries`

**Multiple Verification Steps:**
```markdown
Verify:
  - pytest tests/unit/agent/test_retry.py passes (100% coverage)
  - mypy src/temet_run/agent/ (0 errors)
  - Manual: uv run temet-run -a talky (daemon starts successfully)
```

---

### Context: [why this matters]

**Format:** `Context: [Brief explanation or link]`

**Examples:**
- ✅ `Context: Fixes #342 - daemon crashes on network timeouts`
- ✅ `Context: Required for ADR-016 conversation persistence`
- ✅ `Context: Enables parallel task execution (unblocks coordination module)`
- ✅ `Context: Reduces memory usage from 500MB to <100MB`

**When to include:**
- Link to issues/bugs being fixed
- Reference ADRs for architectural context
- Explain performance improvements with metrics
- Show dependencies (what this unblocks)

---

## Quick Validation Checklist

Before considering a task complete, verify:

- [ ] **Action verb is precise** (Create/Add/Modify/Remove, not Fix/Update)
- [ ] **Target is specific** (exact file, class, function)
- [ ] **Location includes full path** from project root
- [ ] **Verification command is exact** (can copy-paste and run)
- [ ] **Expected outcome is clear** (what does success look like?)
- [ ] **Test cases are enumerated** (if applicable)
- [ ] **No forbidden vague patterns** (see SKILL.md Section 6)

---

## Templates by Task Type

### New Feature Template

```markdown
- [ ] Task N: [Create/Add] [feature name] [in component]
      - [Implementation detail 1]
      - [Implementation detail 2]
      Location: [file path]
      Tests: [test file path]
      Test cases:
        - test_[scenario_1]: [description]
        - test_[scenario_2]: [description]
      Verify: pytest [test path] passes (100% coverage)
      Context: [User need or ADR reference]
```

### Bug Fix Template

```markdown
- [ ] Task N: Fix [error type] in [component]:[location]
      Root cause: [brief explanation]
      Current behavior: [what happens now]
      Expected behavior: [what should happen]
      Fix approach: [how to fix it]
      Location: [file path]:[line number]
      Tests: [test file path]
      Test cases:
        - test_[bug_scenario]: Reproduces the bug, verifies fix
      Verify: pytest [test path] passes
      Context: Fixes #[issue number] - [brief description]
```

### Refactoring Template

```markdown
- [ ] Task N: Extract [logic] from [source] into [destination]
      Motivation: [why refactor - file too long, better separation, etc.]
      Extract:
        - [function/class 1]
        - [function/class 2]
      Location:
        - New file: [new file path]
        - Update: [existing file path]
      Verify:
        - pytest passes (all existing tests still pass)
        - mypy passes
        - [quantifiable improvement - e.g., file size reduced]
      Context: [why this improves the codebase]
```

### Performance Improvement Template

```markdown
- [ ] Task N: Reduce [operation] latency from [current] to [target]
      Current: [measured baseline with tool]
      Root cause: [performance bottleneck]
      Approach: [optimization strategy]
      Location: [file path]:[function]
      Tests: [test file path]
      Verify:
        - [benchmark tool] shows [target performance]
        - pytest passes (behavior unchanged)
        - Memory usage < [limit]
      Context: [user impact or system constraint]
```

### Configuration Change Template

```markdown
- [ ] Task N: Add [setting name] to [Config class]
      Field:
        - [field_name]: [type] = Field(default=[value], [validation])
        - Description: "[help text]"
      Location: [config file path]:[class name]
      Update: [env file, if applicable]
      Tests: [test file path]
      Test cases:
        - test_default_value: Loads with default
        - test_from_env: Reads from environment variable
        - test_validation: Invalid values raise ValidationError
      Verify: pytest [test path] passes
      Context: [why this config is needed]
```

---

## Tips for Using Templates

1. **Start with the template** - Copy the relevant template above
2. **Fill in placeholders** - Replace [bracketed text] with specifics
3. **Run validation checklist** - Ensure all SMART+ components present
4. **Ask for review** - If unsure, ask another agent or user to validate
5. **Iterate** - Update tasks when requirements change

## Related Resources

- **SKILL.md** - Main skill documentation
- **examples/transformation-examples.md** - Real-world vague → precise examples
- **references/smart-framework-deep-dive.md** - Detailed SMART+ explanation
