# Message Grouping Test Fixtures

Test fixtures for the message grouping algorithm (`group_messages_for_export()`).

## Fixtures

### claude_session.jsonl

Real Claude Code JSONL format with tool calls and results.

**Content:**
- User request to read README and check structure
- Assistant response with Read tool call
- Tool result
- Assistant with multiple parallel tool calls (Glob, Bash)
- Multiple tool results
- Final assistant summary
- Follow-up user request
- Bash tool call that fails
- Error handling response

**Expected Groups:** 5 groups
1. User group (initial request)
2. Assistant group with 1 tool call + result
3. Assistant group with 2 tool calls + results
4. User group (follow-up)
5. Assistant group with 1 failed tool call

### codex_session.jsonl

Codex CLI format with function_call structure.

**Content:**
- Session metadata
- User request to list Python files
- Function call (shell command)
- Function result
- Assistant summary
- User follow-up (run tests)
- Function call
- Function result (tests pass)
- Final assistant message

**Expected Groups:** 4 groups
1. User group (list files)
2. Assistant group with shell function call + result
3. User group (run tests)
4. Assistant group with shell function call + result

### cursor_session.jsonl

Cursor/generic format with top-level `type: "tool"` messages.

**Content:**
- User question about main function
- Tool (Read) with result embedded
- Assistant explanation
- Follow-up question
- Tool (Grep) with result
- Final explanation

**Expected Groups:** 4 groups
1. User group + tool result attached
2. Assistant group
3. User group + tool result attached
4. Assistant group

### opencode_session.jsonl

OpenCode format with tool_calls arrays.

**Content:**
- User request for auth function
- Assistant with Write tool call
- Tool result
- Assistant explanation
- User follow-up (JWT)
- Assistant with multiple tool calls
- Multiple tool results
- Final summary

**Expected Groups:** 4 groups
1. User group
2. Assistant group with 1 tool call + result
3. User group
4. Assistant group with 2 tool calls + results

### edge_cases.jsonl

Special cases for robustness testing.

**Cases covered:**
- Empty user message (should be skipped)
- Tool-only assistant message (no text content)
- Orphan tool result (no matching call)
- Tool call without result (missing/pending)
- System message (standalone group)
- Unicode and emoji content
- Nested JSON in tool input
- Empty assistant response
- HTML/XSS special characters
- Many parallel tool calls (8 - tests overflow)
- Multiple results with mixed success/error

**Expected Groups:** ~8 groups (some messages filtered)

## Validation

Run the validation script to ensure all fixtures are valid JSONL:

```bash
./scripts/validate_fixtures.sh
```

## Usage in Tests

```rust
use std::fs;

fn load_fixture(name: &str) -> Vec<serde_json::Value> {
    let content = fs::read_to_string(
        format!("tests/fixtures/message_grouping/{}.jsonl", name)
    ).unwrap();

    content
        .lines()
        .filter(|l| !l.trim().is_empty())
        .map(|l| serde_json::from_str(l).unwrap())
        .collect()
}

#[test]
fn test_claude_grouping() {
    let messages = load_fixture("claude_session");
    let groups = group_messages_for_export(messages);
    assert_eq!(groups.len(), 5);
}
```
