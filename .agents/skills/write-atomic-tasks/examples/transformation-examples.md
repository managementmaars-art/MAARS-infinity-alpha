# Vague → Precise Task Transformation Examples

This file contains comprehensive examples of transforming vague task descriptions into precise, autonomous-execution-ready tasks using the SMART+ framework.

## Example 1: Error Handling

### ❌ VAGUE
```markdown
- [ ] Add error handling
```

**Problems:**
- Which component needs error handling?
- What errors to handle?
- What behavior on error?
- No verification specified

### ✅ PRECISE
```markdown
- [ ] Task 1: Add ConnectionError and TimeoutError handling to ClaudeAgentClient.query()
      - Retry 3 times with exponential backoff (1s, 2s, 4s)
      - Raise AgentConnectionError after retries exhausted
      - Log retry attempts with structlog at warning level
      - Location: src/temet_run/agent/client.py:ClaudeAgentClient.query
      - Verify: pytest tests/unit/agent/test_client.py::test_query_retry_logic passes
```

**What makes it precise:**
- Specific class and method (ClaudeAgentClient.query)
- Exact error types (ConnectionError, TimeoutError)
- Detailed behavior (3 retries, exponential backoff with timings)
- Failure behavior (raise AgentConnectionError)
- File path from project root
- Specific test to verify

---

## Example 2: Data Model Implementation

### ❌ VAGUE
```markdown
- [ ] Implement the data model
```

**Problems:**
- Which data model?
- What fields?
- What validation rules?
- Where does it live?

### ✅ PRECISE
```markdown
- [ ] Task 2: Implement ConversationTurn dataclass in types/conversation.py
      - Fields:
        * id: UUID (auto-generated)
        * timestamp: datetime (auto-set to utcnow)
        * role: Literal["user", "assistant"]
        * content: str (non-empty)
        * session_id: str
        * metadata: dict[str, Any] (default empty dict)
      - Use frozen=True dataclass (immutable)
      - Add __post_init__ validation: role must be user/assistant, content non-empty
      - Location: src/temet_run/types/conversation.py
      - Verify: mypy --strict passes, pytest tests/unit/types/test_conversation.py passes
```

**What makes it precise:**
- Specific dataclass name and file
- All fields with types listed
- Validation rules explicit
- Immutability requirement (frozen=True)
- Type checking requirement (--strict)
- Test location specified

---

## Example 3: Test Writing

### ❌ VAGUE
```markdown
- [ ] Add tests
```

**Problems:**
- Tests for what?
- What test cases?
- Unit or integration?
- What coverage target?

### ✅ PRECISE
```markdown
- [ ] Task 3: Write unit tests for ConversationTurn dataclass
      Test cases:
      - test_valid_construction: User and assistant roles both work
      - test_immutability: Attempt to modify fields raises FrozenInstanceError
      - test_invalid_role: Role="system" raises ValueError
      - test_empty_content: content="" raises ValueError
      - test_serialization: to_dict() returns correct JSON-serializable dict
      - test_uuid_generation: id field auto-generates unique UUID4
      Location: tests/unit/types/test_conversation.py
      Verify: pytest tests/unit/types/test_conversation.py passes with 100% coverage
```

**What makes it precise:**
- Specific class being tested (ConversationTurn)
- All test cases enumerated with names
- Test type specified (unit)
- Coverage requirement (100%)
- Exact file path for tests
- Specific pytest command to verify

---

## Example 4: Bug Fix

### ❌ VAGUE
```markdown
- [ ] Fix the bug
```

**Problems:**
- Which bug?
- What's the symptom?
- What's the root cause?
- How to know it's fixed?

### ✅ PRECISE
```markdown
- [ ] Task 4: Fix TypeError in daemon.py:start_daemon() when config is None
      Root cause: Line 45 calls config.timeout without None check
      Current behavior: TypeError: 'NoneType' object has no attribute 'timeout'
      Expected behavior: Raise ConfigError with message "Configuration required"
      Fix approach:
      - Add early validation at function start
      - `if config is None: raise ConfigError("Configuration required for daemon start")`
      - Import ConfigError from temet_run.config.errors
      Location: src/temet_run/daemon/daemon.py:45
      Verify: pytest tests/unit/daemon/test_daemon.py::test_start_daemon_no_config passes
```

**What makes it precise:**
- Specific error type and location (TypeError, daemon.py:45)
- Root cause identified (missing None check)
- Current vs expected behavior explicit
- Fix approach detailed
- Imports specified
- Test that will verify the fix

---

## Example 5: Feature Addition

### ❌ VAGUE
```markdown
- [ ] Add conversation history command
```

**Problems:**
- What format?
- What data to show?
- CLI or API?
- How to test?

### ✅ PRECISE (Decomposed into 4 tasks)
```markdown
- [ ] Task 5.1: Create ConversationRepository protocol in domain layer
      Methods:
      - get_turns(session_id: str, limit: int | None) -> list[ConversationTurn]
      - search_content(agent_name: str, query: str) -> list[ConversationTurn]
      Location: src/temet_run/domain/repositories.py
      Verify: mypy passes, protocol is runtime checkable

- [ ] Task 5.2: Implement JsonlConversationRepository
      Reads from ~/.temet/agents/{agent-name}/conversation.jsonl
      Implements ConversationRepository protocol
      Uses ijson for streaming large files
      Location: src/temet_run/infrastructure/repositories/conversation.py
      Verify: pytest tests/unit/infrastructure/test_conversation_repo.py passes (100% coverage)

- [ ] Task 5.3: Add `agents history` subcommand to CLI
      Usage: `temet-run agents history <agent-name> [--limit N]`
      Output: Table with columns: timestamp, role, message preview (50 chars)
      Use rich.Table for formatting
      Location: src/temet_run/main.py (add to agents group)
      Verify: `uv run temet-run agents history --help` shows usage, mypy passes

- [ ] Task 5.4: Integration test for history command
      Test: Create temp agent, write 3 turns, run history, verify output
      Test: --limit flag correctly limits output to N turns
      Location: tests/integration/test_cli_history.py
      Verify: pytest tests/integration/test_cli_history.py passes
```

**What makes it precise:**
- Large feature broken into 4 independent tasks
- Each task has clear dependencies (5.3 depends on 5.1, 5.2)
- Specific technologies (ijson, rich.Table)
- CLI usage pattern documented
- File paths for everything
- Verification per task

---

## Example 6: Refactoring

### ❌ VAGUE
```markdown
- [ ] Refactor the code
```

**Problems:**
- What code?
- Why refactor?
- What pattern to use?
- How to ensure no breakage?

### ✅ PRECISE
```markdown
- [ ] Task 6: Extract daemon lifecycle logic from main.py into DaemonManager class
      Motivation: main.py is 450 lines, DaemonManager enables better testing
      Extract these functions into DaemonManager:
      - start_daemon() -> DaemonManager.start()
      - stop_daemon() -> DaemonManager.stop()
      - get_daemon_status() -> DaemonManager.status()
      New file: src/temet_run/daemon/manager.py
      Update: src/temet_run/main.py to use DaemonManager
      Verify:
      - pytest passes (all existing tests still pass)
      - mypy passes
      - main.py reduced to <300 lines
      - Integration test: `uv run temet-run -a talky` still works
```

**What makes it precise:**
- Specific files and functions to refactor
- Motivation explained (file too long)
- New class and file named
- All extracted methods listed
- Line count target (quantifiable improvement)
- Verification includes regression check (existing tests pass)
- Integration test to prevent breakage

---

## Example 7: Performance Improvement

### ❌ VAGUE
```markdown
- [ ] Improve performance
```

**Problems:**
- Performance of what?
- How slow is it now?
- What's the target?
- How to measure?

### ✅ PRECISE
```markdown
- [ ] Task 7: Reduce ConversationRepository.get_turns() query time from 2.5s to <500ms
      Current: Reading 10k turns takes 2.5s (measured with pytest-benchmark)
      Root cause: Full file parse on every query (no indexing)
      Approach: Add in-memory LRU cache (maxsize=1000) using functools.lru_cache
      Location: src/temet_run/infrastructure/repositories/conversation.py:JsonlConversationRepository.get_turns
      Verify:
      - pytest-benchmark shows <500ms for 10k turn queries
      - Memory usage stays <100MB (measure with memory_profiler)
      - pytest passes (behavior unchanged)
```

**What makes it precise:**
- Specific function and metric (get_turns, 2.5s → <500ms)
- Baseline measured and documented
- Root cause identified (no indexing)
- Specific optimization approach (LRU cache with size)
- Multiple verification criteria (speed, memory, correctness)
- Tools for measurement specified (pytest-benchmark, memory_profiler)

---

## Example 8: Logging Addition

### ❌ VAGUE
```markdown
- [ ] Add logging
```

**Problems:**
- Log what?
- What level?
- Where?
- What format?

### ✅ PRECISE
```markdown
- [ ] Task 8: Add structlog logging to AgentCoordinator task lifecycle
      Events to log:
      - task_started (info): log task_id, agent_name, task_type
      - task_progress (debug): log task_id, completion_percentage
      - task_completed (info): log task_id, duration_ms, success=True
      - task_failed (error): log task_id, error_type, error_message, stack_trace
      Use structlog.get_logger(__name__)
      Location: src/temet_run/coordination/coordinator.py:AgentCoordinator.coordinate_task
      Verify:
      - pytest tests/unit/coordination/test_logging.py passes
      - Manual: Run task, check logs contain all 4 event types with correct fields
```

**What makes it precise:**
- Specific class and method (AgentCoordinator.coordinate_task)
- All log events enumerated with levels
- Fields for each event specified
- Library specified (structlog)
- Location precise
- Verification includes both automated test and manual check

---

## Example 9: Documentation

### ❌ VAGUE
```markdown
- [ ] Document the code
```

**Problems:**
- Document what?
- What format?
- What sections?
- Where does it go?

### ✅ PRECISE
```markdown
- [ ] Task 9: Add Google-style docstring to ClaudeAgentClient.query() method
      Sections to include:
      - Summary: One-line description of what query() does
      - Args: message (str), session_id (str | None)
      - Returns: AsyncIterator[str] yielding response chunks
      - Raises: AgentConnectionError, TimeoutError
      - Example: Show basic usage with async for loop
      Follow Google Python Style Guide docstring format
      Location: src/temet_run/agent/client.py:ClaudeAgentClient.query (line 85)
      Verify:
      - pydocstyle passes on client.py
      - Docstring appears in generated API docs (sphinx-build)
```

**What makes it precise:**
- Specific method to document (ClaudeAgentClient.query)
- All docstring sections enumerated
- Style guide specified (Google Python Style Guide)
- Exact line number
- Verification via pydocstyle and doc generation

---

## Example 10: Configuration Change

### ❌ VAGUE
```markdown
- [ ] Update the config
```

**Problems:**
- Which config?
- What setting?
- What value?
- Why change it?

### ✅ PRECISE
```markdown
- [ ] Task 10: Add `max_retries` setting to AgentSettings config
      New field:
      - max_retries: int = Field(default=3, ge=0, le=10)
      - Description: "Maximum retry attempts for transient failures"
      Update AgentSettings class with new field
      Update .env.example with AGENT_MAX_RETRIES=3
      Location: src/temet_run/config/settings.py:AgentSettings
      Verify:
      - mypy passes
      - pydantic validation: max_retries=-1 raises ValidationError
      - pydantic validation: max_retries=11 raises ValidationError
      - Settings loads from env: AGENT_MAX_RETRIES=5 sets max_retries=5
```

**What makes it precise:**
- Specific config class (AgentSettings)
- Field name, type, default, and validation rules
- Documentation string
- Example env file update
- Verification includes validation boundary testing

---

## Common Patterns Summary

### Pattern 1: Error Handling Tasks
**Required elements:**
- Which errors to catch
- Retry logic (if applicable)
- Failure behavior
- Logging requirements

### Pattern 2: Data Model Tasks
**Required elements:**
- All fields with types
- Validation rules
- Immutability requirements
- Serialization needs

### Pattern 3: Test Tasks
**Required elements:**
- What's being tested
- All test cases enumerated
- Coverage target
- Test type (unit/integration/e2e)

### Pattern 4: Bug Fix Tasks
**Required elements:**
- Current behavior (symptom)
- Root cause
- Expected behavior
- Fix approach

### Pattern 5: Feature Tasks
**Required elements:**
- Break into subtasks (if >30 min)
- CLI usage pattern
- Data flow
- Integration points

### Pattern 6: Refactoring Tasks
**Required elements:**
- What's being extracted/moved
- Why (motivation)
- Destination
- Regression verification

### Pattern 7: Performance Tasks
**Required elements:**
- Current performance (measured)
- Target performance
- Measurement methodology
- Optimization approach

### Pattern 8: Logging Tasks
**Required elements:**
- What events to log
- Log levels
- Fields in each event
- Logging library

### Pattern 9: Documentation Tasks
**Required elements:**
- What to document
- Format/style guide
- Required sections
- Verification (linter, doc generation)

### Pattern 10: Configuration Tasks
**Required elements:**
- Config class and field
- Type and validation
- Default value
- Environment variable mapping
