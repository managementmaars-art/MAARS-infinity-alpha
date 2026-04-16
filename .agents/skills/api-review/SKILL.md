---
name: api-review
description: Review API design for best practices, consistency, and common issues
allowed-tools: Read, Glob, Grep, Task
argument-hint: "[spec-file-or-pattern]"
---

# API Review Command

Review an API design for best practices, consistency, and potential issues.

## Usage

```text
/sd:api-review [spec-file-or-pattern]
```

## Arguments

- `spec-file-or-pattern` (optional): Path to OpenAPI spec, API file, or glob pattern
  - If provided: Review the specified file(s)
  - If omitted: Search for common API spec files (openapi.yaml, swagger.json, etc.)

## Examples

```text
/sd:api-review openapi.yaml
/sd:api-review src/api/**/*.ts
/sd:api-review
```

## Workflow

1. **Locate API Definitions**
   - If spec file provided, read it
   - Otherwise, search for: `openapi.yaml`, `openapi.json`, `swagger.yaml`, `swagger.json`, `*.graphql`, `*.proto`
   - Also look for route/endpoint definitions in code

2. **Spawn API Reviewer Agent**
   Use the `api-reviewer` agent to analyze the API design. The agent will:
   - Identify the API type (REST, GraphQL, gRPC)
   - Apply best practices from loaded skills
   - Generate a structured review report

3. **Present Findings**
   Display the review organized by:
   - Critical issues (must fix)
   - Warnings (should address)
   - Suggestions (nice to have)
   - Positive observations

## What Gets Reviewed

### REST APIs

- Resource naming and URL structure
- HTTP method usage
- Status codes
- Error response format
- Pagination patterns

### GraphQL APIs

- Schema design
- Query complexity
- N+1 prevention
- Error handling

### gRPC APIs

- Message design
- Service patterns
- Backward compatibility

### Cross-Cutting

- Versioning strategy
- Rate limiting
- Idempotency
- Security patterns
- Documentation quality

## Output

The command produces a structured review report with:

- Summary of the API and overall assessment
- Issues categorized by severity
- Specific recommendations with examples
- Positive patterns to reinforce
