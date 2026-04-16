---
name: standards
description: >
  Lists and applies engineering standards to the current project.
  Use when user says "apply standards", "what standards apply",
  "check conventions", or invokes /standards.
license: MIT
compatibility: Works with Claude Code, OpenCode, Codex CLI, Copilot, and any Agent Skills-compatible tool.
metadata:
  author: nirabo
  version: "1.0"
  user-invocable: "true"
---

# /standards — Engineering Standards Reference

You help the user understand which engineering standards apply to their project and how to follow them.

## Process

### Step 1: Detect Project Stack

Scan the project root for:

| File | Stack |
|------|-------|
| `pyproject.toml` or `setup.py` | Python → load python.md, testing.md |
| `package.json` | JavaScript/TypeScript → load testing.md |
| `Dockerfile` | Docker → load docker.md |
| `.git` | Git → load git.md |
| `Makefile` | Build system → load makefile.md |
| FastAPI in dependencies | FastAPI → load fastapi.md |

### Step 2: Report Applicable Standards

List which standards apply and summarize key rules for each. Highlight any gaps between the project's current state and the standards.

### Step 3: Offer Actions

Suggest concrete actions:
- "Your Makefile is missing a `check` target — want me to add it?"
- "No .gitignore found — want me to create one following git standards?"
- "Tests exist but no coverage configuration — want me to set up pytest-cov?"

Only suggest actions that are relevant to what the project is missing.
