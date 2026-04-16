---
name: vuln-validate
description: Validate security findings by assessing reachability, exploitability, and existing mitigations. Use after a security scan when the user wants to separate real vulnerabilities from false positives.
user-invocable: false
---

# Vulnerability Validation

Validate whether a reported security finding is actually exploitable in this codebase.

## Prerequisites

Expected inputs:

- `.agent-security/findings.json`
- `.agent-security/threat-model.md`

## Workflow

### 1. Load the Findings

Read the current findings file and determine which issues need validation.

### 2. Check Reachability

For each finding, determine:

- Can an external user reach the code path?
- What entry point leads to it?
- Is authentication required?

### 3. Check Attacker Control

Trace the data flow from source to sink and decide how much of the input is attacker-controlled.

### 4. Check Existing Mitigations

Look for:

- validation and sanitization
- framework protections
- auth gates
- rate limits
- CSP, ORM parameterization, or other platform guards

### 5. Assign Exploitability

Classify each issue as:

- easy
- medium
- hard
- not exploitable

### 6. Produce a Validated Findings File

Write:

- `.agent-security/validated-findings.json`

Include reasoning, exploitability, and remediation priority.

## Gotchas

- A pattern match is not a vulnerability until reachability is proven.
- A real code smell may still be non-exploitable in context.
- Do not generate sensational findings without concrete attack paths.
