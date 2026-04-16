# Common Patterns & Examples

Practical patterns and examples for building Claude Code components.

## Overview

This guide provides real-world patterns for common use cases. Each pattern includes:

- Use case description
- Complete component examples
- Benefits and trade-offs
- When to use this pattern

## Agent Patterns

### Pattern 1: Read-Only Exploration Agent

**Use Case**: Safe codebase exploration without modification risk

**Example**:

```yaml
---
name: codebase-explorer
description: Explores codebase to find information. Use when researching code structure or finding specific implementations.
tools: Read, Grep, Glob
model: haiku
permissionMode: plan
---

# Codebase Explorer

You are a codebase exploration specialist focused on quickly finding and analyzing code.

## Your Expertise

- Finding files and functions efficiently
- Understanding code structure and dependencies
- Analyzing implementation patterns
- Tracing code execution flows

## Workflow

1. **Understand the question**: Parse what user is looking for
2. **Search strategically**: Use Grep/Glob to locate relevant code
3. **Read and analyze**: Examine found files for answers
4. **Synthesize findings**: Provide clear, actionable summary

## Guidelines

- Start broad (Glob), then narrow (Grep), then deep (Read)
- Don't make assumptions - verify with actual code
- Cite file paths and line numbers in responses
- Suggest related areas to explore when relevant
```

**Benefits**:

- Fast (haiku model for quick searches)
- Safe (read-only tools prevent accidental changes)
- Structured (plan mode shows search strategy)
- Efficient (focused on exploration only)

**When to Use**:

- Need to understand unfamiliar codebase
- Looking for specific implementations
- Want to trace code dependencies
- Researching patterns or conventions

---

### Pattern 2: High-Permission Editor Agent

**Use Case**: Trusted automated editing with pre-approved changes

**Example**:

```yaml
---
name: code-formatter
description: Formats code according to style guidelines. Use when code needs formatting or style fixes.
tools: Read, Edit, Bash(prettier:*,eslint:*)
model: sonnet
permissionMode: acceptEdits
---

# Code Formatter

You are an automated code formatting specialist that ensures consistent code style.

## Your Expertise

- Running formatters (prettier, eslint)
- Applying style fixes automatically
- Maintaining code consistency
- Handling multiple file types

## Workflow

1. **Identify files**: Determine which files need formatting
2. **Read current state**: Check file content before formatting
3. **Apply formatters**: Run appropriate formatter for each file type
4. **Verify changes**: Ensure formatting succeeded
5. **Report results**: Summarize what was formatted

## Guidelines

- Only format, never change logic
- Use project's existing formatter configuration
- Format all affected files, not just one
- Report if any files failed to format
- Preserve file encoding and line endings
```

**Benefits**:

- Efficient (auto-approves edit operations)
- Safe (restricted to formatting tools only)
- Fast (no permission prompts for edits)
- Controlled (Bash restricted to specific commands)

**When to Use**:

- Automated code formatting workflows
- Pre-commit style fixes
- Bulk formatting operations
- Trusted repetitive editing

---

### Pattern 3: Multi-Skill Specialist Agent

**Use Case**: Domain expert with comprehensive loaded knowledge

**Example**:

```yaml
---
name: api-developer
description: Develops REST APIs following best practices. Use when creating or modifying API endpoints, routes, or controllers.
tools: Read, Write, Edit, Bash(npm:*), Grep, Glob
model: sonnet
skills: api-design-patterns, openapi-spec, security-best-practices
permissionMode: default
---

# API Developer

You are an expert API developer specializing in RESTful API design and implementation.

## Your Expertise

- RESTful API design principles (from api-design-patterns skill)
- OpenAPI specification (from openapi-spec skill)
- API security best practices (from security-best-practices skill)
- Backend development patterns
- API documentation

## Workflow

1. **Understand requirements**: What endpoints are needed?
2. **Design API**: Apply REST principles and security patterns
3. **Implement endpoints**: Write clean, secure code
4. **Add documentation**: Document with OpenAPI/comments
5. **Test**: Verify endpoints work correctly

## Guidelines

- Follow RESTful conventions (from api-design-patterns)
- Always validate input (from security-best-practices)
- Document all endpoints with OpenAPI (from openapi-spec)
- Use appropriate HTTP methods and status codes
- Handle errors gracefully
- Consider pagination for list endpoints
```

**Benefits**:

- Expert knowledge immediately available
- Consistent application of patterns
- Security built-in from loaded skills
- Documentation standards enforced

**When to Use**:

- Complex domain requiring multiple knowledge areas
- Need consistent application of standards
- Want to ensure best practices followed
- Domain expertise needs to be codified

**Trade-offs**:

- Larger context window usage
- More tokens consumed
- Slower startup (skills loaded at start)

---

### Pattern 4: Validation Agent with Hooks

**Use Case**: Pre-flight checks and automated validation

**Example**:

```yaml
---
name: safe-deployer
description: Deploys code to production with automated validation checks. Use when deploying to any environment.
tools: Read, Bash
model: sonnet
permissionMode: plan
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/pre-deploy-validation.sh $TOOL_INPUT"
        - type: prompt
          prompt: "Remember: All deploys require approval from security team."
  Stop:
    - hooks:
        - type: command
          command: "./scripts/post-deploy-notification.sh"
---

# Safe Deployer

You are a deployment specialist focused on safe, validated deployments.

## Your Expertise

- Deployment validation and checks
- Environment configuration
- Rollback procedures
- Monitoring deployment health

## Workflow

1. **Pre-deployment checks** (automated via hooks):
   - Code tests passing
   - Security scan clean
   - Dependencies updated
   - Configuration valid

2. **Plan deployment**:
   - Generate deployment plan
   - Show what will be deployed
   - Get user confirmation

3. **Execute deployment**:
   - Deploy to target environment
   - Monitor for errors
   - Verify health checks

4. **Post-deployment** (automated via hooks):
   - Notify team via Slack
   - Log deployment details
   - Update deployment tracker

## Guidelines

- Never skip validation checks
- Always show deployment plan first
- Require confirmation for production
- Have rollback plan ready
- Monitor deployment closely
```

**Benefits**:

- Automatic validation prevents errors
- Consistent deployment process
- Audit trail via notifications
- Safety through planning mode

**When to Use**:

- Critical operations requiring validation
- Need automated safety checks
- Want audit logging
- Require consistent process

---

## Skill Patterns

### Pattern 1: Domain Terminology Skill

**Use Case**: Industry-specific vocabulary and concepts

**Example**:

```markdown
---
name: kubernetes-terminology
description: Kubernetes architecture and terminology. Use when working with K8s deployments, configs, or troubleshooting.
---

# Kubernetes Terminology

## Core Concepts

**Pod**: Smallest deployable unit. Contains one or more containers that share network and storage.

**Deployment**: Manages replica sets and rolling updates. Declaratively manages pod lifecycle.

**Service**: Stable network endpoint for pods. Types: ClusterIP (internal), NodePort (node-level), LoadBalancer (external).

**Ingress**: HTTP/HTTPS routing to services. Manages external access with path-based routing.

**ConfigMap**: Non-sensitive configuration data. Mounted as files or environment variables.

**Secret**: Sensitive data (passwords, tokens). Base64 encoded, mounted securely.

## Architecture
```

Client → Ingress → Service → Pod(s) → Container(s)

````

## Quick Reference

### Common kubectl Commands

- `kubectl get pods` - List pods
- `kubectl describe pod <name>` - Pod details
- `kubectl logs <pod>` - View pod logs
- `kubectl apply -f <file>` - Apply configuration
- `kubectl delete <resource> <name>` - Delete resource

### Resource Limits

```yaml
resources:
  requests:
    memory: "64Mi"
    cpu: "250m"
  limits:
    memory: "128Mi"
    cpu: "500m"
````

## Best Practices

1. **Use namespaces** for environment separation
2. **Set resource limits** to prevent resource exhaustion
3. **Use liveness/readiness probes** for health checks
4. **Store configs in ConfigMaps** not in images
5. **Use secrets** for sensitive data, never hardcode

## Common Patterns

### Deployment with Service

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-server
spec:
  replicas: 3
  selector:
    matchLabels:
      app: api-server
  template:
    metadata:
      labels:
        app: api-server
    spec:
      containers:
        - name: api
          image: api-server:latest
          ports:
            - containerPort: 8080
---
apiVersion: v1
kind: Service
metadata:
  name: api-service
spec:
  selector:
    app: api-server
  ports:
    - port: 80
      targetPort: 8080
```

```

**Benefits**:
- Quick terminology lookup
- Consistent usage of terms
- Common patterns readily available
- Best practices embedded

---

### Pattern 2: Progressive Disclosure Skill

**Use Case**: Large knowledge domain split for efficiency

**Example Structure**:

```

api-documentation-generator/
├── SKILL.md # Main overview (< 500 lines)
├── openapi-spec.md # OpenAPI 3.0 specification details
├── examples.md # Real-world examples
└── scripts/
└── generate.py # Generation utility

````

**SKILL.md**:

```markdown
---
name: api-documentation-generator
description: Generates API documentation from source code. Use when creating or updating API docs.
allowed-tools: Read, Bash(python:*)
---

# API Documentation Generator

## Overview

This skill helps generate comprehensive API documentation from source code using multiple documentation formats.

## Quick Start

1. Analyze source code for API endpoints
2. Extract route definitions and parameters
3. Generate documentation in requested format
4. Validate documentation completeness

## Supported Formats

- **OpenAPI/Swagger**: See [openapi-spec.md](openapi-spec.md) for details
- **Markdown**: Standard markdown format
- **HTML**: Interactive documentation

## Core Process

### 1. Discovery

Scan code for API endpoints:
- Route definitions
- HTTP methods
- Parameters (path, query, body)
- Response structures

### 2. Analysis

Extract details:
- Request/response schemas
- Authentication requirements
- Example requests/responses
- Error codes

### 3. Generation

Create documentation:
- Choose format (OpenAPI, Markdown, etc.)
- Apply templates
- Validate completeness
- Generate output file

## Quick Reference

### Common Patterns

```python
# FastAPI endpoint
@app.get("/users/{user_id}")
def get_user(user_id: int) -> User:
    """Get user by ID"""
    pass

# OpenAPI equivalent
paths:
  /users/{user_id}:
    get:
      summary: Get user by ID
      parameters:
        - name: user_id
          in: path
          required: true
          schema:
            type: integer
````

## Detailed References

- **OpenAPI Specification**: [openapi-spec.md](openapi-spec.md) - Complete OpenAPI 3.0 details
- **Examples**: [examples.md](examples.md) - Real-world documentation examples
- **Generator Script**: `python scripts/generate.py --help` - Utility for generation

## Best Practices

1. Document all endpoints, even internal ones
2. Include example requests and responses
3. Document error codes and their meanings
4. Keep docs in sync with code
5. Version your API documentation

````

**Benefits**:
- Main file stays focused and fast to load
- Detailed information available when needed
- Separation of concerns (overview vs details)
- Scripts available but not loaded into context

---

## Command Patterns

### Pattern 1: Simple Direct Command

**Use Case**: Command executes work directly

**Example**:

```markdown
---
description: Format code in current directory
allowed-tools: Read, Write, Bash(prettier:*)
---

# Format Code

## Parse Arguments

Optional file pattern: `$1` (defaults to "**/*.{js,ts,jsx,tsx}")

## Your Task

1. **Determine Files**
   - If $1 provided, use as file pattern
   - Otherwise, use default pattern for JS/TS files

2. **Run Formatter**
   - Execute: `npx prettier --write <pattern>`
   - Capture output showing which files changed

3. **Report Results**
   - List formatted files
   - Show any files that had errors
   - Provide summary count

## Examples

**/format** → Formats all JS/TS files

**/format src/\*.ts** → Formats TypeScript files in src/

**/format "**/*.jsx"** → Formats all JSX files
````

---

### Pattern 2: Subagent Delegation Command

**Use Case**: Command delegates complex work to agent

**Example**:

```markdown
---
description: Review code for quality and security issues
allowed-tools: Task(code-reviewer), Grep, Glob
argument-hint: [file-or-directory]
---

# Review Code

## Parse Arguments

Optional target: `$1` (file, directory, or blank for changed files)

## Your Task

1. **Determine Scope**
   - If $1 is provided: Review that file/directory
   - If $1 is blank: Find files changed in git (use Grep/Glob)

2. **Prepare Context**
   - Get list of files to review
   - Read file sizes (for context planning)
   - Prepare review prompt with all context

3. **Invoke Reviewer**
   - Use Task tool to invoke code-reviewer agent
   - Provide prompt: "Review these files: [list]. Check for:
     - Security vulnerabilities
     - Code quality issues
     - Performance problems
     - Best practice violations"

4. **Present Results**
   - Show review findings organized by severity
   - Highlight critical issues first
   - Provide actionable recommendations

## Examples

**/review** → Reviews all changed files in current branch

**/review src/auth.ts** → Reviews specific authentication file

**/review src/** → Reviews all files in src directory
```

---

### Pattern 3: Multi-Step Workflow Command

**Use Case**: Command orchestrates complex multi-agent workflow

**Example**:

```markdown
---
description: Run full CI/CD pipeline (test, build, deploy)
allowed-tools: Task(test-runner), Task(builder), Task(deployer), Bash
argument-hint: <environment> [service]
---

# CI/CD Pipeline

## Parse Arguments

Required environment: `$1` (staging, production)
Optional service: `$2` (defaults to all services)

## Your Task

### Step 1: Validation

- Check environment is valid (staging or production)
- If production, confirm with user: "Deploy to PRODUCTION? (yes/no)"
- Verify service exists (if specified)

### Step 2: Run Tests

- Invoke test-runner agent with Task tool
- Wait for completion
- If tests fail: STOP and report failures
- If tests pass: Continue to build

### Step 3: Build

- Invoke builder agent with Task tool
- Build for target environment
- If build fails: STOP and report errors
- If build succeeds: Continue to deploy

### Step 4: Deploy

- Invoke deployer agent with Task tool
- Deploy to specified environment
- Monitor deployment progress
- If deployment fails: Trigger rollback

### Step 5: Verification

- Run health checks with Bash
- Verify services are healthy
- Run smoke tests
- Report final status

### Step 6: Notification

- Send notification to team (Slack/email)
- Update deployment tracker
- Log deployment details

## Examples

**/ci-cd staging** → Deploy all services to staging

**/ci-cd staging api-server** → Deploy api-server to staging

**/ci-cd production** → Deploy to production (with confirmation)
```

---

## Hook Patterns

### Pattern 1: Pre-Flight Validation

**Use Case**: Validate before dangerous operations

**Example**:

```yaml
hooks:
  PreToolUse:
    - matcher: 'Bash'
      hooks:
        - type: command
          command: |
            #!/bin/bash
            # Validate bash command safety
            COMMAND="$TOOL_INPUT"

            # Block dangerous patterns
            if echo "$COMMAND" | grep -qE "rm -rf /|sudo rm|format|mkfs"; then
              echo "ERROR: Dangerous command blocked: $COMMAND"
              exit 1
            fi

            # Warn on production operations
            if echo "$COMMAND" | grep -qi "production"; then
              echo "WARNING: Production operation detected"
              echo "Please confirm this is intended"
            fi

            exit 0
```

---

### Pattern 2: Automatic Backup

**Use Case**: Backup files before modification

**Example**:

```yaml
hooks:
  PreToolUse:
    - matcher: 'Write|Edit'
      hooks:
        - type: command
          command: |
            #!/bin/bash
            # Backup file before modification
            FILE="$TOOL_INPUT"
            BACKUP_DIR=".backups"

            if [ -f "$FILE" ]; then
              mkdir -p "$BACKUP_DIR"
              TIMESTAMP=$(date +%Y%m%d_%H%M%S)
              cp "$FILE" "$BACKUP_DIR/$(basename $FILE).$TIMESTAMP.bak"
              echo "Backed up: $FILE"
            fi

            exit 0
```

---

### Pattern 3: Post-Processing

**Use Case**: Automatic formatting after edits

**Example**:

```yaml
hooks:
  PostToolUse:
    - matcher: 'Write|Edit'
      hooks:
        - type: command
          command: |
            #!/bin/bash
            # Format code after modification
            FILE="$TOOL_INPUT"

            # Format based on file type
            if [[ "$FILE" == *.js || "$FILE" == *.ts ]]; then
              npx prettier --write "$FILE"
              echo "Formatted: $FILE"
            elif [[ "$FILE" == *.py ]]; then
              black "$FILE"
              echo "Formatted: $FILE"
            fi

            exit 0
```

---

## Integration Patterns

### Pattern: Command → Agent → Skills

**Use Case**: User command delegates to specialized agent with loaded skills

**Structure**:

```
User invokes: /translate "Hello world" --lang ja
    ↓
Command: translate.md
    ↓
Delegates to: Task(translator)
    ↓
Agent: translator.md (with skills: translation-expertise, terminology)
    ↓
Performs: Translation with expert knowledge loaded
    ↓
Returns: Translated result to user
```

**Command (translate.md)**:

```markdown
---
description: Translate text between English, Japanese, and Chinese
argument-hint: [--lang <en|ja|cn>] <text>
allowed-tools: Task(translator)
---

# Translate Command

## Parse Arguments

Arguments: `$ARGUMENTS`

Extract:

- Target language: Look for `--lang <value>` (default: auto-detect)
- Text to translate: Remaining content after flags

## Your Task

1. Parse target language and text
2. Invoke translator agent with Task tool:
   - Provide text to translate
   - Specify target language
   - Request professional translation
3. Return translated text to user

## Examples

**/translate Hello world --lang ja** → Translates to Japanese
**/translate こんにちは --lang en** → Translates to English
```

**Agent (translator.md)**:

```yaml
---
name: translator
description: Professional translator for English, Japanese, and Chinese. Use when user requests translation.
tools: Read, Write
model: opus
skills: translation-expertise, engineering-terminology
permissionMode: default
---
# Professional Translator

You are an expert translator with deep knowledge of English, Japanese, and Chinese.

[Agent system prompt...]
```

**Skills**:

- `translation-expertise`: Translation methodology and best practices
- `engineering-terminology`: Technical term translations

**Benefits**:

- User-friendly interface via command
- Expert translation via specialized agent
- Domain knowledge via loaded skills
- Clean separation of concerns

---

## Related Documentation

- [Agent Creation Guide](agents-guide.md) - Detailed agent development
- [Skills Creation Guide](skills-guide.md) - Detailed skill development
- [Commands Creation Guide](commands-guide.md) - Detailed command development
- [Hooks Reference Guide](hooks-guide.md) - Complete hooks documentation

For official documentation, see [SKILL.md](SKILL.md#official-documentation).
