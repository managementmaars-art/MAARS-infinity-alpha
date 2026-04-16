# Commands Creation Guide

Complete guide for creating and configuring Claude Code slash commands.

## Overview

Slash commands are user-invocable prompts that provide reusable workflows. They provide:

- **User Interface**: Easy access via `/command-name` syntax
- **Argument Handling**: Structured input parsing
- **Workflow Automation**: Reusable task sequences
- **Subagent Delegation**: Orchestrate complex operations

## File Structure

**File Format**: Markdown with YAML frontmatter
**Location**: `.claude/commands/[command-name].md`

```markdown
---
description: Brief description shown in /help
argument-hint: [--option <value>] <content>
allowed-tools: Task(agent-name), Read, Write
model: sonnet
disable-model-invocation: false
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/validate.sh"
---

# Command Name

## Parse Arguments

Command arguments: `$ARGUMENTS`

Extract needed values from arguments.

## Your Task

1. Parse arguments
2. Validate inputs
3. Perform work or delegate to subagent
4. Return results

## Examples

**Example 1**: `/command arg1 arg2`
→ [What happens]

**Example 2**: `/command @file.md`
→ [What happens]
```

## Frontmatter Fields

### Required Fields

**description** (string)

- Brief description of what the command does
- Shown in `/help` menu
- Should be user-facing and clear
- Examples:
  - "Translate text between English, Japanese, and Chinese"
  - "Review code changes for quality and security issues"
  - "Generate API documentation from source code"

### Optional Fields

**argument-hint** (string)

- The arguments expected for the slash command
- Shown to the user when auto-completing the slash command in `/help` menu
- Use square brackets for optional: `[--option]`
- Use angle brackets for required: `<text>`
- Examples:
  - `[--lang <en|ja|cn>] <text>`
  - `<source-file> [output-file]`
  - `[--format <json|yaml>] <input>`
  - `add [tagId] | remove [tagId] | list`

**allowed-tools** (array or comma-separated string)

- Tools the command can use
- Common pattern: `Task(agent-name)` for delegation
- Can include: Read, Write, Edit, Bash, Grep, Glob, etc.
- Syntax: `allowed-tools: Task(translator), Read`

**model** (string)

- Model to use for this command
- Can be a model alias (`sonnet`, `opus`, `haiku`) or specific model string
- Default: inherits from parent context
- Most commands use default (sonnet)

**disable-model-invocation** (boolean)

- Prevent Skill tool from calling this command
- Default: `false`
- Set to `true` for commands only users should invoke
- Use when command requires interactive input

**hooks** (object)

- Lifecycle hooks scoped to this command's execution
- Supports `PreToolUse`, `PostToolUse`, and `Stop` events
- See [Hooks Reference Guide](hooks-guide.md) for details
- Useful for validation and cleanup
- Automatically cleaned up after command completes

## Command Structure

### Basic Command Template

```markdown
---
description: Clear description for /help menu
argument-hint: [options] <required>
allowed-tools: Task(agent-name)
---

# Command Name

## Parse Arguments

Command arguments: `$ARGUMENTS`

Parse the arguments:

- Extract options: `--flag`, `--option value`
- Extract positional arguments: `$1`, `$2`, etc.
- Handle file references: `@filename`

## Your Task

1. **Validate Input**
   - Check required arguments present
   - Validate argument formats
   - If missing, ask user with AskUserQuestion

2. **Process Request**
   - Perform the task directly, OR
   - Delegate to subagent with Task tool

3. **Return Results**
   - Format output clearly
   - Provide feedback to user
   - Handle errors gracefully

## Examples

### Example 1: Basic Usage

**Input**: `/command arg1 arg2`

**Output**: [Expected result]

### Example 2: With Options

**Input**: `/command --option value arg1`

**Output**: [Expected result]

### Example 3: With File Reference

**Input**: `/command @file.md`

**Output**: [Expected result]
```

### Argument Parsing

Commands receive arguments via special variables:

**`$ARGUMENTS`** - All arguments as single string

```markdown
Command: /translate --lang ja Hello world
$ARGUMENTS: "--lang ja Hello world"
```

**Positional variables** - `$1`, `$2`, `$3`, etc.

```markdown
Command: /deploy staging api-server
$1: "staging"
$2: "api-server"
```

**Parsing patterns**:

```markdown
## Parse Arguments

Command arguments: `$ARGUMENTS`

Extract:

- Language flag: Look for `--lang <value>` in $ARGUMENTS
- Text content: Everything after flags
- File reference: Look for `@filename` pattern

Example parsing:

- If $ARGUMENTS contains "--lang ja", set language to Japanese
- If $ARGUMENTS starts with "@", read file content
- Remaining text is the content to process
```

### File References

Support `@filename` syntax for file inputs:

```markdown
## Parse Arguments

If $ARGUMENTS starts with "@":

1. Extract filename after "@"
2. Use Read tool to get file content
3. Process the file content

Example:

- `/command @document.txt` → Read document.txt and process
```

## Command Patterns

### Pattern 1: Simple Direct Command

Command does work directly without delegation:

```markdown
---
description: Format code in current directory
allowed-tools: Read, Write, Bash(prettier:*)
---

# Format Code

## Parse Arguments

Optional file pattern: `$1` (defaults to all files)

## Your Task

1. Find files matching pattern (or all files)
2. Run prettier on each file
3. Report which files were formatted

## Example

**/format** → Formats all files
**/format src/\*.ts** → Formats TypeScript files in src/
```

### Pattern 2: Subagent Delegation

Command delegates complex work to specialized agent:

```markdown
---
description: Review code for quality and security issues
allowed-tools: Task(code-reviewer)
---

# Review Code

## Parse Arguments

Optional file or directory: `$1` (defaults to changed files)

## Your Task

1. Determine which files to review
2. Invoke code-reviewer subagent with Task tool:
   - subagent_type: "code-reviewer"
   - prompt: "Review these files: [file list]. Check for security issues, code quality, and best practices."
3. Present the review findings to user

## Examples

**/review** → Reviews all changed files
**/review src/auth.ts** → Reviews specific file
```

### Pattern 3: Multi-Step Workflow

Command orchestrates multiple operations:

```markdown
---
description: Deploy application to specified environment
allowed-tools: Task(deployment-agent), Bash
---

# Deploy Application

## Parse Arguments

Required environment: `$1` (staging, production)
Optional service: `$2` (defaults to all services)

## Your Task

1. **Validate Environment**
   - Ensure environment is valid
   - Check permissions for that environment
   - If production, confirm with user

2. **Pre-Deployment Checks**
   - Run tests with Task(deployment-agent)
   - Verify dependencies
   - Check configuration

3. **Deploy**
   - Delegate to deployment-agent
   - Monitor deployment progress
   - Report status

4. **Post-Deployment**
   - Verify deployment health
   - Run smoke tests
   - Notify team

## Examples

**/deploy staging** → Deploy all services to staging
**/deploy production api-server** → Deploy api-server to production
```

### Pattern 4: Interactive Command

Command asks for additional input if needed:

```markdown
---
description: Generate API documentation
allowed-tools: Read, Write, Task(doc-generator)
---

# Generate API Documentation

## Parse Arguments

Optional output format: `$1` (markdown, html, pdf)
Optional output path: `$2`

## Your Task

1. **Check Arguments**
   - If format not specified, ask user: "What format? (markdown/html/pdf)"
   - If output path not specified, ask: "Where should I save the documentation?"

2. **Generate Documentation**
   - Delegate to doc-generator agent
   - Include format and path in prompt

3. **Confirm Completion**
   - Show output path
   - Offer to open/preview

## Examples

**/gendocs** → Asks for format and path
**/gendocs markdown** → Asks for path only
**/gendocs markdown docs/api.md** → Generates directly
```

## Development Workflow

### Step 1: Define the Use Case

Ask yourself:

- What user task should this simplify?
- Would users benefit from a shortcut?
- Is this a repeated workflow?
- What arguments make sense?

### Step 2: Design the Syntax

Consider:

- Command name (verb form: `deploy`, `review`, `translate`)
- Required vs optional arguments
- Flags and options
- File reference support
- Default behaviors

### Step 3: Create the File

1. Create `.claude/commands/[name].md`
2. Add frontmatter with description
3. Add argument-hint if arguments are complex
4. Specify allowed-tools

### Step 4: Write the Command Logic

Structure:

1. Argument parsing section
2. Validation logic
3. Main task execution
4. Error handling
5. Examples

### Step 5: Test

1. Run `/help` to verify command appears
2. Test with no arguments
3. Test with partial arguments
4. Test with full arguments
5. Test with file references
6. Test with invalid inputs

### Step 6: Document

Add examples covering:

- Basic usage
- Common options
- Edge cases
- Error scenarios

## Best Practices

### Command Design

1. **User-facing**: Commands are for users, not internal automation
2. **Clear names**: Use verbs, keep short, be descriptive
3. **Intuitive syntax**: Match user expectations
4. **Good defaults**: Work with no arguments when possible
5. **Helpful errors**: Guide user when input is invalid

### Argument Handling

1. **Parse carefully**: Handle all argument formats
2. **Validate early**: Check arguments before heavy work
3. **Ask when needed**: Use AskUserQuestion for missing required args
4. **Support files**: Enable `@filename` pattern where useful
5. **Document syntax**: Use argument-hint for complex arguments

### Delegation Strategy

1. **Use subagents**: Delegate complex work to specialized agents
2. **Clear prompts**: Provide full context to subagents
3. **Handle errors**: Catch and report subagent failures
4. **Show progress**: Keep user informed during long operations

### Error Handling

1. **Validate input**: Check arguments before processing
2. **Provide feedback**: Tell user what went wrong
3. **Suggest fixes**: Help user correct mistakes
4. **Fail gracefully**: Don't leave system in bad state

## Troubleshooting

### Command Not in /help

**Symptoms**: Command doesn't appear in help menu

**Solutions**:

1. Check file location: `.claude/commands/[name].md`
2. Verify frontmatter has `description` field
3. Check for YAML syntax errors
4. Ensure filename ends with `.md`
5. Restart Claude Code session

### Command Fails to Execute

**Symptoms**: Command runs but errors or does nothing

**Solutions**:

1. Check `allowed-tools` includes necessary tools
2. Verify tool names are correct
3. Test argument parsing with simple inputs
4. Check for permission issues
5. Verify subagent names if using Task tool

### Arguments Not Parsed Correctly

**Symptoms**: Command gets wrong values from arguments

**Solutions**:

1. Review argument parsing logic
2. Test with different argument patterns
3. Handle both `$ARGUMENTS` and `$1`, `$2` formats
4. Account for quoted strings
5. Test file reference pattern (`@filename`)

### Subagent Not Found

**Symptoms**: Task tool fails to find agent

**Solutions**:

1. Verify agent exists in `.claude/agents/`
2. Check agent name spelling in `allowed-tools`
3. Ensure agent has valid frontmatter
4. Use exact agent name, case-sensitive
5. Restart session if agent was just created

### Command Behaves Unexpectedly

**Symptoms**: Command does something different than intended

**Solutions**:

1. Review command prompt for clarity
2. Add more specific instructions
3. Include examples of correct behavior
4. Simplify command logic
5. Add validation steps

## Advanced Topics

### Complex Argument Parsing

Handle sophisticated argument patterns:

```markdown
## Parse Arguments

Command arguments: `$ARGUMENTS`

Parse complex syntax:

1. **Extract flags**
   - Look for `--flag` or `--option value` patterns
   - Common flags: `--force`, `--verbose`, `--dry-run`

2. **Extract positional arguments**
   - Get values by position: `$1`, `$2`, etc.
   - Handle optional vs required

3. **Handle file references**
   - Check for `@filename` pattern
   - Support multiple files: `@file1.txt @file2.txt`

4. **Parse key-value pairs**
   - Support syntax like `key=value`
   - Example: `name=api-server env=staging`

Example:
```

/deploy staging api-server --force --verbose
→ env: staging
→ service: api-server
→ force: true
→ verbose: true

```

```

### Multi-Agent Orchestration

Coordinate multiple agents:

```markdown
---
description: Full code quality pipeline
allowed-tools: Task(linter), Task(test-runner), Task(code-reviewer)
---

## Your Task

1. **Lint Code**
   - Invoke linter agent
   - If linting fails, stop and report errors

2. **Run Tests**
   - Invoke test-runner agent
   - If tests fail, stop and report failures

3. **Review Code**
   - Invoke code-reviewer agent
   - Generate comprehensive review report

4. **Summary**
   - Combine all results
   - Provide actionable feedback
```

### Conditional Execution

Execute different paths based on context:

```markdown
## Your Task

1. **Determine Context**
   - Check if in git repository
   - Check current branch
   - Check for uncommitted changes

2. **Choose Path**
   - If on main branch → Warn and require confirmation
   - If uncommitted changes → Ask to stash or commit
   - Otherwise → Proceed normally

3. **Execute**
   - Run appropriate workflow for context
   - Handle errors specific to each path
```

### Progress Reporting

Keep user informed during long operations:

```markdown
## Your Task

1. **Setup**
   - Tell user: "Starting deployment to staging..."

2. **Pre-checks**
   - Tell user: "Running pre-deployment checks..."
   - Run checks
   - Tell user: "Pre-checks passed"

3. **Deployment**
   - Tell user: "Deploying services..."
   - Deploy each service
   - Tell user: "Deployed service X" after each

4. **Verification**
   - Tell user: "Verifying deployment..."
   - Run health checks
   - Tell user: "Deployment complete and verified"
```

### Hook Integration

Add validation and automation:

```markdown
---
description: Safe file operations with validation
allowed-tools: Write, Edit
hooks:
  PreToolUse:
    - matcher: 'Write|Edit'
      hooks:
        - type: command
          command: './scripts/backup.sh $TOOL_INPUT'
        - type: command
          command: './scripts/validate.sh $TOOL_INPUT'
---

## Your Task

File operations are automatically:

1. Backed up before modification (PreToolUse hook)
2. Validated before writing (PreToolUse hook)

Proceed with confidence knowing hooks provide safety.
```

## Common Patterns

### Read-Process-Write Command

```markdown
---
description: Process files with transformation
allowed-tools: Read, Write
---

## Parse Arguments

Input file: `$1`
Output file: `$2` (optional, defaults to input + .out)

## Your Task

1. Read input file
2. Process content (transformation logic)
3. Write to output file
4. Report completion
```

### Search-Report Command

```markdown
---
description: Search codebase and generate report
allowed-tools: Grep, Glob, Write
---

## Parse Arguments

Search term: `$1`
Output file: `$2` (optional, defaults to search-results.md)

## Your Task

1. Use Grep to find all occurrences
2. Organize results by file
3. Generate markdown report
4. Write to output file
5. Show summary statistics
```

### Validation Command

```markdown
---
description: Validate project configuration
allowed-tools: Read, Bash
---

## Your Task

1. Check all required config files exist
2. Validate config file syntax
3. Check for required fields
4. Run validation scripts
5. Generate validation report with pass/fail
```

## Related Documentation

- [Agent Creation Guide](agents-guide.md) - Creating agents for delegation
- [Skills Creation Guide](skills-guide.md) - Loading skills for command use
- [Hooks Reference Guide](hooks-guide.md) - Adding hooks to commands
- [Common Patterns & Examples](patterns-examples.md) - More command examples

For official documentation, see [SKILL.md](SKILL.md#official-documentation).
