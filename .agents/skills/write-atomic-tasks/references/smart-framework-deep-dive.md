# SMART+ Framework Deep Dive

This reference provides detailed guidance on each component of the SMART+ framework for writing precise, autonomous-execution-ready tasks.

## Table of Contents

1. S - Specific
2. M - Measurable
3. A - Actionable
4. R - Referenced
5. T - Testable
6. + - Context (Optional)
7. Framework Application Workflow
8. Anti-Patterns and Corrections

---

## 1. S - Specific

**Definition:** The task clearly states WHAT needs to be done, WHERE it needs to be done, and WHO (which component) is affected.

### Elements of Specificity

| Element | Description | Example |
|---------|-------------|---------|
| **Action Verb** | Precise verb (Create, Add, Modify, Remove, Extract) | "Add" not "Update" |
| **Target** | Exact class/function/file | "ClaudeAgentClient.query()" not "the client" |
| **Scope** | Boundaries of the change | "Add retry logic" not "Improve reliability" |

### Good Specific Tasks

```markdown
✅ "Add exponential backoff retry logic to ClaudeAgentClient.query()"
✅ "Extract daemon lifecycle methods from main.py into DaemonManager class"
✅ "Remove deprecated `legacy_timeout` parameter from AgentSettings"
```

### Bad Non-Specific Tasks

```markdown
❌ "Add retry logic" (where?)
❌ "Refactor the code" (what code? what refactoring?)
❌ "Fix the client" (which client? what's broken?)
```

### How to Make Tasks Specific

1. **Identify the target**: What file/class/function is affected?
2. **Use precise verbs**: Prefer Create/Add/Modify/Remove/Extract over Update/Fix/Improve
3. **Add constraints**: If only certain cases are affected, state them

---

## 2. M - Measurable

**Definition:** The task has clear, objective success criteria that anyone can verify.

### Types of Measurement

| Type | Description | Example |
|------|-------------|---------|
| **Binary** | Pass/fail | "Tests pass" |
| **Quantitative** | Numeric target | "Reduce latency from 500ms to <100ms" |
| **Behavioral** | Observable outcome | "CLI shows error message when config missing" |
| **Quality Gates** | Tool-based checks | "mypy --strict passes with 0 errors" |

### Good Measurable Criteria

```markdown
✅ "Verify: pytest tests/unit/agent/ passes with 100% coverage"
✅ "Verify: mypy --strict shows 0 errors"
✅ "Verify: GET /api/status returns 200 with {status: 'healthy'}"
✅ "Verify: Latency reduced from 2.5s to <500ms (pytest-benchmark)"
```

### Bad Non-Measurable Criteria

```markdown
❌ "Verify: Code works" (how do you know it works?)
❌ "Verify: Everything passes" (what is everything?)
❌ "Verify: Performance is better" (how much better?)
❌ "Verify: Looks good" (subjective)
```

### How to Make Tasks Measurable

1. **Specify the verification command**: Exact command to run
2. **Include expected output**: What does success look like?
3. **Use quality gates**: Leverage mypy, pytest, linters
4. **Set quantitative targets**: For performance, use actual numbers

---

## 3. A - Actionable

**Definition:** The task has a clear first step that can be taken immediately without additional research or decisions.

### Elements of Actionability

| Element | Description | Example |
|---------|-------------|---------|
| **First Step** | What to do first | "Create file src/temet_run/agent/retry.py" |
| **Dependencies Clear** | What must exist first | "Requires Task 2 (ConversationTurn model) complete" |
| **No Ambiguity** | No open questions | Specific approach, not "figure out how to..." |

### Good Actionable Tasks

```markdown
✅ "Create file src/temet_run/agent/errors.py with ConversationError exception hierarchy"
✅ "Add max_retries: int = Field(default=3) to AgentSettings in config/settings.py"
✅ "Modify ClaudeAgentClient.__init__ to accept optional retry_config: RetryConfig parameter"
```

### Bad Non-Actionable Tasks

```markdown
❌ "Research best retry strategies" (research tasks are not implementation tasks)
❌ "Decide on error handling approach" (decision tasks need separate ADR/spike)
❌ "Figure out how to implement caching" (too vague, needs research first)
```

### How to Make Tasks Actionable

1. **Start with action verbs**: Create, Add, Modify, Remove
2. **Specify the first action**: What file to create/edit first
3. **Separate research from implementation**: Research tasks are different from implementation tasks
4. **Make decisions before task creation**: Use ADRs for architectural decisions

---

## 4. R - Referenced

**Definition:** The task includes all necessary references: file paths, class names, function signatures, line numbers, external resources.

### Types of References

| Type | Format | Example |
|------|--------|---------|
| **File Path** | From project root | `src/temet_run/agent/client.py` |
| **Class/Function** | Fully qualified | `ClaudeAgentClient.query` |
| **Line Number** | file:line | `daemon.py:45` |
| **External Resource** | URL or ADR | "See ADR-016 for context" |
| **Related Tasks** | Task ID | "Depends on Task 2" |

### Good Referenced Tasks

```markdown
✅ Location: src/temet_run/agent/client.py:ClaudeAgentClient.query
✅ Update: tests/unit/agent/test_client.py (add test_query_retry_logic)
✅ Context: ADR-016 conversation persistence requires session management
✅ Depends on: Task 2 (ConversationRepository protocol must exist)
```

### Bad Non-Referenced Tasks

```markdown
❌ Location: the client file (which one?)
❌ Update: some tests (where?)
❌ Context: We need this (why?)
❌ Depends on: the data model (which model?)
```

### How to Make Tasks Referenced

1. **Always include file paths**: Full path from project root
2. **Use qualified names**: module.Class.method, not just "the method"
3. **Link to context**: ADRs, issues, parent tasks
4. **Specify test locations**: Where are the tests for this?

---

## 5. T - Testable

**Definition:** The task includes explicit test criteria, success conditions, and (ideally) the specific tests to write or run.

### Elements of Testability

| Element | Description | Example |
|---------|-------------|---------|
| **Test Cases** | Specific scenarios to test | "Test: valid role, invalid role, empty content" |
| **Test Type** | Unit/Integration/E2E | "Unit test with mocked dependencies" |
| **Coverage Target** | Percentage or lines | "100% coverage on new code" |
| **Test Location** | Where tests go | `tests/unit/agent/test_retry.py` |

### Good Testable Tasks

```markdown
✅ Test cases:
   - test_retry_on_connection_error: Retries 3 times
   - test_retry_backoff: Uses exponential backoff (1s, 2s, 4s)
   - test_retry_exhausted: Raises AgentConnectionError after 3 failures
   Location: tests/unit/agent/test_client_retry.py
   Verify: pytest tests/unit/agent/test_client_retry.py passes, 100% coverage
```

### Bad Non-Testable Tasks

```markdown
❌ "Add tests for the feature" (what tests?)
❌ "Make sure it works" (how?)
❌ "Test manually" (not reproducible)
```

### How to Make Tasks Testable

1. **Enumerate test cases**: List all scenarios to test
2. **Specify test type**: Unit, integration, or e2e
3. **Include test location**: Where will the tests live?
4. **Define success criteria**: What coverage percentage? What assertions?

---

## 6. + - Context (Optional)

**Definition:** Additional information about WHY this task matters, what problem it solves, or how it fits into the bigger picture.

### When to Include Context

| Scenario | Example |
|----------|---------|
| **Links to ADR** | "Needed for ADR-016 conversation persistence" |
| **Solves User Problem** | "Users report daemon crashes on network timeouts" |
| **Technical Motivation** | "Current approach causes memory leaks under load" |
| **Dependencies** | "Unblocks Task 5 (CLI integration)" |

### Good Context

```markdown
✅ Context: ADR-016 requires conversation history persistence
✅ Context: Fixes #342 - daemon crashes when network unavailable
✅ Context: Enables parallel task execution (unblocks coordination module)
✅ Context: Reduces memory usage from 500MB to <100MB
```

### Bad Context

```markdown
❌ Context: Good to have (not helpful)
❌ Context: Makes things better (vague)
❌ Context: For the future (when? why?)
```

### How to Add Context

1. **Link to issues/ADRs**: Reference the decision or problem
2. **State the user impact**: What problem does this solve?
3. **Show dependencies**: What does this unblock?
4. **Quantify improvement**: If it's an optimization, include metrics

---

## 7. Framework Application Workflow

### Step 1: Start with User Need
```
User request: "Add retry logic to the agent"
```

### Step 2: Apply SMART+ Questions

| Question | Answer |
|----------|--------|
| **Specific:** What exactly? | Add retry logic to ClaudeAgentClient.query() method |
| **Measurable:** How to verify? | Tests pass, mypy clean |
| **Actionable:** First step? | Create retry.py file with RetryConfig dataclass |
| **Referenced:** Where? | src/temet_run/agent/client.py:ClaudeAgentClient.query |
| **Testable:** What tests? | Test retry on connection error, backoff timing, exhaustion |
| **Context:** Why? | Fixes #342 - daemon crashes on network issues |

### Step 3: Write Precise Task

```markdown
- [ ] Task 1: Add exponential backoff retry logic to ClaudeAgentClient.query()
      - Create RetryConfig dataclass: max_retries=3, base_delay=1.0, max_delay=60.0
      - Wrap query logic in retry loop with exponential backoff
      - Retry on: ConnectionError, TimeoutError
      - After retries exhausted: raise AgentConnectionError
      - Log each retry attempt at warning level
      Location: src/temet_run/agent/client.py:ClaudeAgentClient.query
      Tests: tests/unit/agent/test_client_retry.py
      Test cases:
        - test_retry_connection_error: Retries 3 times on ConnectionError
        - test_exponential_backoff: Delays are 1s, 2s, 4s
        - test_retry_exhausted: Raises AgentConnectionError after 3 failures
        - test_no_retry_on_validation_error: Does NOT retry ValueError
      Verify: pytest tests/unit/agent/test_client_retry.py passes (100% coverage)
      Context: Fixes #342 - daemon crashes when network unavailable
```

### Step 4: Validate Against Checklist

- [x] Specific: ClaudeAgentClient.query() - exact target
- [x] Measurable: pytest passes, 100% coverage
- [x] Actionable: Create RetryConfig dataclass first
- [x] Referenced: Full file path, test path
- [x] Testable: 4 test cases enumerated
- [x] Context: Links to issue #342

---

## 8. Anti-Patterns and Corrections

### Anti-Pattern 1: Generic Action Verbs

❌ **Bad:**
```markdown
- [ ] Fix the bug in the client
```

✅ **Good:**
```markdown
- [ ] Add None check for config parameter in daemon.py:start_daemon() (line 45)
```

**Why:** "Fix" is vague. Specific problem and solution are clear.

---

### Anti-Pattern 2: Missing Verification

❌ **Bad:**
```markdown
- [ ] Add logging to the coordinator
      Location: coordination/coordinator.py
```

✅ **Good:**
```markdown
- [ ] Add structlog logging to AgentCoordinator.coordinate_task()
      Events: task_started (info), task_completed (info), task_failed (error)
      Location: coordination/coordinator.py:AgentCoordinator.coordinate_task
      Verify: pytest tests/unit/coordination/test_logging.py passes
```

**Why:** Without verification, you can't confirm the task is complete.

---

### Anti-Pattern 3: Mixing Concerns

❌ **Bad:**
```markdown
- [ ] Implement ConversationTurn model, write tests, add CLI command, and integrate with daemon
```

✅ **Good (Decomposed):**
```markdown
- [ ] Task 1: Implement ConversationTurn dataclass
      Location: types/conversation.py
      Verify: mypy passes

- [ ] Task 2: Write unit tests for ConversationTurn
      Location: tests/unit/types/test_conversation.py
      Verify: pytest passes, 100% coverage

- [ ] Task 3: Add CLI history command
      Location: main.py (agents group)
      Verify: `temet-run agents history --help` works

- [ ] Task 4: Integration test for history workflow
      Location: tests/integration/test_history.py
      Verify: pytest passes
```

**Why:** Each task is independently completable and verifiable.

---

### Anti-Pattern 4: Implicit Dependencies

❌ **Bad:**
```markdown
- [ ] Task 1: Add history command to CLI
- [ ] Task 2: Create ConversationRepository
```

✅ **Good:**
```markdown
- [ ] Task 1: Create ConversationRepository protocol
      Location: domain/repositories.py
      Verify: mypy passes

- [ ] Task 2: Add history command to CLI (depends on Task 1)
      Location: main.py
      Verify: `temet-run agents history --help` works
```

**Why:** Dependencies must be explicit for correct execution order.

---

### Anti-Pattern 5: Subjective Success Criteria

❌ **Bad:**
```markdown
- [ ] Improve performance of the query
      Verify: It should be faster
```

✅ **Good:**
```markdown
- [ ] Reduce ConversationRepository.get_turns() latency from 2.5s to <500ms
      Approach: Add LRU cache (maxsize=1000)
      Verify: pytest-benchmark shows <500ms for 10k turn queries
```

**Why:** Quantitative targets are measurable and objective.

---

## Summary: SMART+ Checklist

Before finalizing any task, verify:

- [ ] **Specific:** Exact file, class, function, line number
- [ ] **Measurable:** Clear verification command with expected output
- [ ] **Actionable:** First step is obvious, no blocking decisions
- [ ] **Referenced:** All file paths, related tasks, ADRs included
- [ ] **Testable:** Test cases enumerated, test location specified
- [ ] **Context:** Why this matters (optional but recommended)

**When all 6 elements are present, the task is ready for autonomous execution.**
