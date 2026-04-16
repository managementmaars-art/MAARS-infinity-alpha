---
name: security-scan
description: Analyze code changes for security vulnerabilities using STRIDE patterns and repository context. Use when the user wants a security scan of staged changes, a pull request, a branch diff, or a commit range.
user-invocable: false
---

# Security Scan

Analyze code changes using LLM reasoning plus a repository threat model.

## Prerequisites

This skill expects:

- `.agent-security/threat-model.md`
- `.agent-security/security-config.json`

If either is missing, generate them first with the `threat-model` skill.

## Input

If the user does not specify a scope, default to staged changes.

Supported scopes:

- Pull request
- Commit
- Commit range
- Staged changes
- Uncommitted changes
- Branch comparison

## Workflow

### 1. Resolve the Scan Scope

Use `git diff`, `git show`, or `gh pr diff` as appropriate.

### 2. Load Security Context

Read:

- `.agent-security/threat-model.md`
- `.agent-security/security-config.json`

### 3. Inspect the Changed Files

For each changed file, check for STRIDE patterns including:

- auth and session flaws
- injection
- XSS
- path traversal
- insecure deserialization
- secret exposure
- missing authorization
- denial-of-service risks

### 4. Record Findings

Write findings to:

- `.agent-security/findings.json`

Each finding should include:

- file
- line or code region
- category
- severity
- explanation
- suggested fix

### 5. Summarize for the User

Report the highest-signal findings first. Separate confirmed issues from weaker suspicions.

## Gotchas

- Read full file context before flagging a sink.
- Framework defaults may already neutralize some classes of bugs.
- Diff-only review is not enough when the sink and source live in different files.
