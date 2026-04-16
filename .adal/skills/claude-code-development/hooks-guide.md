# Hooks Reference Guide

Complete guide for configuring and using Claude Code hooks.

## Overview

Hooks are scripts that run automatically on tool events. They provide:

- **Automated Validation**: Pre-execution checks
- **Post-Processing**: Cleanup and logging after operations
- **Lifecycle Management**: Setup and teardown
- **Event-Driven Automation**: React to specific tool usage

## Hook Configuration

Hooks can be configured in two places:

1. **Global Configuration**: In `.claude/settings.json` (applies to all components)
2. **Component Configuration**: In frontmatter of agents, skills, or commands (scoped to that component)

### Global Hooks (settings.json)

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "./scripts/validate-bash.sh $TOOL_INPUT",
            "once": false
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "./scripts/lint.sh"
          }
        ]
      }
    ]
  }
}
```

### Component Hooks (Frontmatter)

```yaml
---
name: component-name
description: Component description
hooks:
  PreToolUse:
    - matcher: 'Bash'
      hooks:
        - type: command
          command: './scripts/validate.sh $TOOL_INPUT'
          once: true
  PostToolUse:
    - matcher: 'Write|Edit'
      hooks:
        - type: command
          command: './scripts/format.sh'
  Stop:
    - hooks:
        - type: command
          command: './scripts/cleanup.sh'
---
```

## Hook Events

### PreToolUse

Runs **before** a tool is executed.

**Matcher**: Tool name (e.g., "Bash", "Write", "Edit", "Write|Edit")
**Use cases**:

- Validate input before execution
- Check permissions
- Create backups
- Block unsafe operations

**Special variables**:

- `$TOOL_INPUT`: The input being passed to the tool
- `$TOOL_NAME`: Name of the tool being invoked

**Exit codes**:

- 0: Allow operation to proceed
- Non-zero: Block operation and show error

Example:

```yaml
PreToolUse:
  - matcher: 'Bash'
    hooks:
      - type: command
        command: './scripts/validate-bash-command.sh $TOOL_INPUT'
```

### PermissionRequest

Runs when the user is shown a permission dialog.

**Matcher**: Tool name (same as PreToolUse)
**Use cases**:

- Auto-approve specific operations
- Auto-deny dangerous operations on behalf of user
- Modify tool inputs before approval
- Custom permission logic

**Special variables**:

- `$TOOL_INPUT`: The input being passed to the tool
- `$TOOL_NAME`: Name of the tool being requested

**Exit codes**:

- 0: Normal processing (use JSON output for decision control)
- Non-zero: Error handling

Example:

```yaml
PermissionRequest:
  - matcher: 'Bash'
    hooks:
      - type: command
        command: './scripts/permission-handler.sh $TOOL_INPUT'
```

### PostToolUse

Runs **after** a tool is executed successfully.

**Matcher**: Tool name (e.g., "Bash", "Write", "Edit")
**Use cases**:

- Format code after editing
- Run linters
- Update indexes
- Log operations
- Notify external systems

**Special variables**:

- `$TOOL_OUTPUT`: The output from the tool
- `$TOOL_NAME`: Name of the tool that was invoked

**Exit codes**:

- Exit codes don't block operations (tool already ran)
- Non-zero codes are logged but don't fail the operation

Example:

```yaml
PostToolUse:
  - matcher: 'Write|Edit'
    hooks:
      - type: command
        command: './scripts/lint-file.sh'
```

### SubagentStart

Runs when a **subagent begins** execution.

**Matcher**: Agent name (e.g., "translator", "code-reviewer")
**Use cases**:

- Setup environment for agent
- Load configuration
- Initialize resources
- Log agent invocation

**Special variables**:

- `$AGENT_NAME`: Name of the starting agent

Example:

```yaml
SubagentStart:
  - matcher: 'translator'
    hooks:
      - type: command
        command: './scripts/setup-translation-env.sh'
```

### SubagentStop

Runs when a **subagent completes** execution.

**Matcher**: Agent name (e.g., "translator", "code-reviewer")
**Use cases**:

- Cleanup agent resources
- Save state
- Generate reports
- Log completion

**Special variables**:

- `$AGENT_NAME`: Name of the stopping agent

Example:

```yaml
SubagentStop:
  - matcher: 'translator'
    hooks:
      - type: command
        command: './scripts/cleanup-translation-env.sh'
```

### Stop

Runs when a **component completes** execution (main agent finished responding, not on user interrupt).

**Matcher**: None (no matcher field)
**Use cases**:

- Final cleanup
- Generate summary
- Save results
- Notify completion
- Intelligently decide if Claude should continue working

**Special variables**: None

Example:

```yaml
Stop:
  - hooks:
      - type: command
        command: './scripts/final-cleanup.sh'
```

### Notification

Runs when Claude Code sends notifications.

**Matcher**: Notification type (e.g., `permission_prompt`, `idle_prompt`, `auth_success`, `elicitation_dialog`)
**Use cases**:

- Alert on permission requests
- Monitor idle states
- Track authentication events
- Custom notification handling

**Special variables**:

- `$NOTIFICATION_TYPE`: Type of notification

Example:

```yaml
Notification:
  - matcher: 'permission_prompt'
    hooks:
      - type: command
        command: './scripts/permission-alert.sh'
  - matcher: 'idle_prompt'
    hooks:
      - type: command
        command: './scripts/idle-notification.sh'
```

### UserPromptSubmit

Runs when the user submits a prompt, before Claude processes it.

**Matcher**: None (no matcher field)
**Use cases**:

- Add additional context based on prompt
- Validate prompts
- Block certain types of prompts
- Inject dynamic information

**Special variables**: None (prompt is in hook input JSON)

Example:

```yaml
UserPromptSubmit:
  - hooks:
      - type: command
        command: './scripts/prompt-validator.py'
```

### PreCompact

Runs before Claude Code is about to run a compact operation.

**Matcher**: Compact trigger type (`manual` or `auto`)
**Use cases**:

- Prepare for compaction
- Save state before compact
- Add context before history is summarized

**Special variables**: None

Example:

```yaml
PreCompact:
  - matcher: 'manual'
    hooks:
      - type: command
        command: './scripts/pre-compact-manual.sh'
  - matcher: 'auto'
    hooks:
      - type: command
        command: './scripts/pre-compact-auto.sh'
```

### SessionStart

Runs when Claude Code starts a new session or resumes an existing session.

**Matcher**: Session source type (`startup`, `resume`, `clear`, `compact`)
**Use cases**:

- Load development context
- Install dependencies
- Set up environment variables
- Initialize resources

**Special variables**:

- `$CLAUDE_ENV_FILE`: File path for persisting environment variables (SessionStart only)

**Persisting environment variables**:

SessionStart hooks can write to `$CLAUDE_ENV_FILE` to make environment variables available in all subsequent bash commands:

```bash
#!/bin/bash

if [ -n "$CLAUDE_ENV_FILE" ]; then
  echo 'export NODE_ENV=production' >> "$CLAUDE_ENV_FILE"
  echo 'export API_KEY=your-api-key' >> "$CLAUDE_ENV_FILE"
fi

exit 0
```

Example:

```yaml
SessionStart:
  - matcher: 'startup'
    hooks:
      - type: command
        command: './scripts/session-setup.sh'
  - matcher: 'resume'
    hooks:
      - type: command
        command: './scripts/session-resume.sh'
```

### SessionEnd

Runs when a Claude Code session ends.

**Matcher**: None (no matcher field)
**Use cases**:

- Cleanup tasks
- Log session statistics
- Save session state
- Final notifications

**Special variables**: None (reason is in hook input JSON)

**Session end reasons**:

- `clear`: Session cleared with /clear command
- `logout`: User logged out
- `prompt_input_exit`: User exited while prompt input was visible
- `other`: Other exit reasons

Example:

```yaml
SessionEnd:
  - hooks:
      - type: command
        command: './scripts/session-cleanup.sh'
```

## Hook Types

### Command Hook

Executes a shell command.

**Type**: `command`
**Fields**:

- `command` (required): Shell command to execute
- `once` (optional): Run only once per session (default: false). After first successful execution, hook is removed
- `timeout` (optional): How long a hook should run, in seconds, before canceling that specific hook

Example:

```yaml
hooks:
  - type: command
    command: './scripts/validate.sh $TOOL_INPUT'
    once: false
    timeout: 30
```

**Command execution**:

- Runs in shell context
- Can use all shell features (pipes, redirects, etc.)
- Has access to environment variables
- Working directory is repository root

**Exit behavior**:

- PreToolUse hooks: Non-zero exits block the operation
- PostToolUse hooks: Non-zero exits are logged only
- Stop hooks: Non-zero exits are logged only

### Prompt Hook

Injects text into the conversation context or uses an LLM to evaluate whether to allow/block an action.

**Type**: `prompt`
**Fields**:

- `prompt` (required): Text to inject or prompt to send to LLM for evaluation
- `once` (optional): Inject/run only once per session (default: false)
- `timeout` (optional): Timeout in seconds for LLM evaluation (default: 30 seconds)

**Two modes of operation**:

1. **Context injection** (for most hook events): Injects text into conversation
2. **LLM evaluation** (for Stop, SubagentStop, etc.): Uses LLM to make intelligent decisions

**Example (context injection)**:

```yaml
hooks:
  - type: prompt
    prompt: 'Remember to follow security best practices.'
    once: true
```

**Example (LLM evaluation for Stop hook)**:

```yaml
hooks:
  - type: prompt
    prompt: 'Evaluate if Claude should stop: $ARGUMENTS. Check if all tasks are complete.'
    timeout: 30
```

**Use cases**:

- Add reminders and guidelines
- Inject context dynamically
- Make context-aware permission decisions
- Intelligently decide if work is complete

**LLM evaluation response schema** (for Stop, SubagentStop, etc.):

```json
{
  "ok": true | false,
  "reason": "Explanation for the decision"
}
```

- `ok: true` allows the action
- `ok: false` prevents it (reason is required)

## Matchers

Matchers determine when hooks trigger. They use regex patterns.

### Tool Matchers (PreToolUse, PostToolUse)

Match tool names:

**Single tool**:

```yaml
matcher: 'Bash'
```

**Multiple tools (OR)**:

```yaml
matcher: 'Write|Edit'
```

**Pattern matching**:

```yaml
matcher: 'Write|Edit|NotebookEdit'
```

**All tools**:

```yaml
matcher: '.*'
```

### Agent Matchers (SubagentStart, SubagentStop)

Match agent names:

**Single agent**:

```yaml
matcher: 'translator'
```

**Multiple agents (OR)**:

```yaml
matcher: 'translator|code-reviewer'
```

**Pattern matching**:

```yaml
matcher: '.*-reviewer' # Matches any agent ending with -reviewer
```

### No Matcher (Stop)

Stop hooks don't use matchers:

```yaml
Stop:
  - hooks:
      - type: command
        command: './cleanup.sh'
```

## Hook Scope

### Global Hooks

Defined in `.claude/settings.json`:

- Apply to entire project
- Active for all sessions
- Persist across restarts
- Useful for project-wide policies

Example use cases:

- Code formatting on all edits
- Bash command validation
- Logging all tool usage

### Component Hooks

Defined in component frontmatter:

- Scoped to that component's execution
- Automatically cleaned up when component completes
- Don't affect other components
- Useful for component-specific behavior

Example use cases:

- Agent-specific setup/teardown
- Command-specific validation
- Skill-specific tooling

## Advanced Features

### Once Flag

Run hook only once per session:

```yaml
hooks:
  - type: command
    command: './scripts/expensive-setup.sh'
    once: true
```

**Use cases**:

- One-time environment setup
- Initial configuration loading
- Session initialization
- First-run checks

**Behavior**:

- First trigger: Hook runs normally
- Subsequent triggers: Hook is skipped
- Reset: On session restart

**Important**: The `once` option is currently only supported for skills and slash commands, not for agents. For agents, hooks will run every time they are triggered.

### Environment Variables

Hooks can access environment variables:

```yaml
hooks:
  - type: command
    command: './scripts/deploy.sh $DEPLOYMENT_ENV'
```

**Available variables**:

- All system environment variables
- `$TOOL_INPUT`: Input to tool (PreToolUse only)
- `$TOOL_OUTPUT`: Output from tool (PostToolUse only)
- `$TOOL_NAME`: Name of tool being used
- `$AGENT_NAME`: Name of agent (SubagentStart/Stop only)

### Chaining Hooks

Multiple hooks can be chained:

```yaml
PreToolUse:
  - matcher: 'Write'
    hooks:
      - type: command
        command: './scripts/backup.sh $TOOL_INPUT'
      - type: command
        command: './scripts/validate.sh $TOOL_INPUT'
      - type: prompt
        prompt: 'Remember to review changes carefully.'
```

**Execution order**:

- Hooks run in the order defined
- If any PreToolUse hook fails, operation is blocked
- All hooks in the chain must succeed

### Conditional Execution

Hooks can include conditional logic in scripts:

```bash
#!/bin/bash
# scripts/conditional-hook.sh

if [ "$TOOL_NAME" = "Bash" ]; then
  # Bash-specific validation
  ./validate-bash.sh "$TOOL_INPUT"
elif [ "$TOOL_NAME" = "Write" ]; then
  # Write-specific validation
  ./validate-write.sh "$TOOL_INPUT"
fi
```

## Best Practices

### Performance

1. **Keep hooks fast**: They run on every matching event
2. **Use `once: true`** for expensive operations
3. **Avoid network calls** in hot-path hooks
4. **Cache results** when possible
5. **Profile hook execution** if slowdowns occur

### Security

1. **Validate input**: Don't trust `$TOOL_INPUT` blindly
2. **Use PreToolUse hooks** to block dangerous operations
3. **Escape shell variables**: Prevent injection attacks
4. **Limit permissions**: Hook scripts should have minimal access
5. **Log security events**: Track blocked operations

### Reliability

1. **Handle errors gracefully**: Don't crash on unexpected input
2. **Provide clear error messages**: Help users understand failures
3. **Test hook scripts independently**: Unit test before integration
4. **Use exit codes correctly**: 0 for success, non-zero for failure
5. **Log hook execution**: Aid debugging

### Maintainability

1. **Document hooks**: Explain what and why
2. **Use descriptive script names**: Clear purpose
3. **Keep scripts simple**: One responsibility per hook
4. **Version control hook scripts**: Track changes
5. **Test on updates**: Verify hooks still work

### Scope Appropriately

1. **Use component hooks** for component-specific behavior
2. **Use global hooks** for project-wide policies
3. **Prefer narrow matchers**: Be specific about what triggers
4. **Avoid overlapping hooks**: Multiple hooks for same event can conflict
5. **Clean up automatically**: Let component hooks handle their cleanup

## Common Patterns

### Pre-Flight Validation

Validate before dangerous operations:

```yaml
hooks:
  PreToolUse:
    - matcher: 'Bash'
      hooks:
        - type: command
          command: |
            if echo "$TOOL_INPUT" | grep -q "rm -rf"; then
              echo "Dangerous rm command blocked"
              exit 1
            fi
```

### Automatic Formatting

Format code after editing:

```yaml
hooks:
  PostToolUse:
    - matcher: 'Write|Edit'
      hooks:
        - type: command
          command: './scripts/format-code.sh'
```

### Backup Before Modification

Create backups before changing files:

```yaml
hooks:
  PreToolUse:
    - matcher: 'Write|Edit'
      hooks:
        - type: command
          command: './scripts/backup.sh $TOOL_INPUT'
```

### Environment Setup/Teardown

Setup and cleanup for agents:

```yaml
hooks:
  SubagentStart:
    - matcher: 'deployment-agent'
      hooks:
        - type: command
          command: './scripts/setup-deploy-env.sh'
          once: true
  SubagentStop:
    - matcher: 'deployment-agent'
      hooks:
        - type: command
          command: './scripts/cleanup-deploy-env.sh'
```

### Logging and Monitoring

Track tool usage:

```yaml
hooks:
  PostToolUse:
    - matcher: '.*'
      hooks:
        - type: command
          command: './scripts/log-tool-usage.sh $TOOL_NAME'
```

### Conditional Reminders

Inject context-aware reminders:

```yaml
hooks:
  PreToolUse:
    - matcher: 'Bash'
      hooks:
        - type: prompt
          prompt: 'Double-check bash commands for safety.'
    - matcher: 'Write|Edit'
      hooks:
        - type: prompt
          prompt: 'Remember to maintain code style consistency.'
```

### Git Operations

Auto-stage changes:

```yaml
hooks:
  PostToolUse:
    - matcher: 'Write|Edit'
      hooks:
        - type: command
          command: 'git add $TOOL_INPUT'
```

## Troubleshooting

### Hook Not Triggering

**Symptoms**: Hook doesn't run when expected

**Solutions**:

1. Check matcher pattern matches tool/agent name exactly
2. Verify hook is in correct event section (PreToolUse vs PostToolUse)
3. Ensure script path is correct (relative to repo root)
4. Check script has execute permissions: `chmod +x script.sh`
5. Test hook script independently
6. Check for YAML syntax errors in configuration

### Hook Blocking Operations

**Symptoms**: Tool usage fails unexpectedly

**Solutions**:

1. Check PreToolUse hook exit codes (non-zero blocks)
2. Review hook script for errors
3. Check hook script has proper error handling
4. Verify `$TOOL_INPUT` is being parsed correctly
5. Add debug logging to hook script
6. Test hook script with sample input

### Hook Running Multiple Times

**Symptoms**: Hook executes more than expected

**Solutions**:

1. Add `once: true` if hook should run once per session
2. Check if multiple matchers are triggering hook
3. Verify hook isn't defined in both global and component configs
4. Review matcher pattern for unintended matches
5. Check if hook is being chained unintentionally

### Hook Performance Issues

**Symptoms**: Operations slow when hooks enabled

**Solutions**:

1. Profile hook execution time
2. Add caching to expensive operations
3. Use `once: true` for setup operations
4. Optimize hook scripts
5. Move slow operations to PostToolUse if possible
6. Consider disabling hooks for specific components

### Script Path Issues

**Symptoms**: Hook fails with "command not found"

**Solutions**:

1. Use paths relative to repository root
2. Ensure script has execute permissions
3. Use absolute paths if needed
4. Check script exists at specified path
5. Test script path manually: `./scripts/hook.sh`

### Environment Variable Issues

**Symptoms**: Hook script can't access variables

**Solutions**:

1. Verify environment variables are set
2. Check variable names are correct ($TOOL_INPUT, etc.)
3. Quote variables in scripts: `"$TOOL_INPUT"`
4. Test script with sample environment variables
5. Check shell script has proper shebang: `#!/bin/bash`

## Hook Script Examples

### Validation Script

```bash
#!/bin/bash
# scripts/validate-bash-command.sh

COMMAND="$1"

# Block dangerous patterns
if echo "$COMMAND" | grep -qE "rm -rf /|sudo rm"; then
  echo "ERROR: Dangerous command blocked: $COMMAND"
  exit 1
fi

# Check for unquoted variables
if echo "$COMMAND" | grep -qE '\$[A-Za-z_]+[^"]'; then
  echo "WARNING: Unquoted variable detected"
  exit 1
fi

exit 0
```

### Backup Script

```bash
#!/bin/bash
# scripts/backup.sh

FILE="$1"
BACKUP_DIR=".backups"

if [ -f "$FILE" ]; then
  mkdir -p "$BACKUP_DIR"
  TIMESTAMP=$(date +%Y%m%d_%H%M%S)
  cp "$FILE" "$BACKUP_DIR/$(basename $FILE).$TIMESTAMP"
  echo "Backed up $FILE"
fi

exit 0
```

### Formatting Script

```bash
#!/bin/bash
# scripts/format-code.sh

# Find files that were just modified
CHANGED_FILES=$(git diff --name-only --cached)

for FILE in $CHANGED_FILES; do
  if [[ $FILE == *.js || $FILE == *.ts ]]; then
    prettier --write "$FILE"
    echo "Formatted $FILE"
  fi
done

exit 0
```

### Environment Setup Script

```bash
#!/bin/bash
# scripts/setup-env.sh

echo "Setting up environment..."

# Load configuration
export API_KEY=$(cat .env | grep API_KEY | cut -d= -f2)
export ENV="staging"

# Initialize tools
npm install --silent

echo "Environment ready"
exit 0
```

## Related Documentation

- [Agent Creation Guide](agents-guide.md) - Using hooks in agents
- [Skills Creation Guide](skills-guide.md) - Using hooks in skills
- [Commands Creation Guide](commands-guide.md) - Using hooks in commands
- [Common Patterns & Examples](patterns-examples.md) - More hook examples

For official documentation, see [SKILL.md](SKILL.md#official-documentation).
