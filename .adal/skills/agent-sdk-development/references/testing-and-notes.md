# Testing and Repository Notes

## Table of Contents

- [Test Scenarios](#test-scenarios)
- [Multi-Model Testing Notes](#multi-model-testing-notes)
- [Repository-Specific Notes](#repository-specific-notes)
- [References](#references)

## Test Scenarios

### Scenario 1: Installing the SDK

**Query:** "How do I install the Claude Agent SDK for TypeScript?"

**Expected Behavior:**

- Skill activates on keywords "install", "SDK", "TypeScript"
- Directs user to query docs-management: "Agent SDK installation"
- docs-management returns official installation guide
- Provides npm package name and installation steps

**Success Criteria:**

- User gets correct npm package: @anthropic-ai/claude-agent-sdk
- Installation commands are from official docs

### Scenario 2: Creating Custom Tools

**Query:** "I need to create a custom tool for my agent"

**Expected Behavior:**

- Skill activates on keywords "custom tool", "agent"
- Directs user to query docs-management: "custom tools SDK", "creating custom tools"
- docs-management returns custom tool documentation
- Provides schema definition and handler implementation guidance

**Success Criteria:**

- User learns tool schema format
- User understands handler implementation pattern
- Both TypeScript and Python examples available

### Scenario 3: Session Resumption Issue

**Query:** "My agent's session resumption isn't working"

**Expected Behavior:**

- Skill activates on keywords "session", "resumption"
- Follows Troubleshooting Pattern
- Directs user to query docs-management: "session resumption", "resume option", "session ID"
- Provides diagnostic steps from official docs

**Success Criteria:**

- User understands session ID capture requirement
- User knows how to pass resume option
- Issue resolution guided by official documentation

### Scenario 4: Multi-Topic Agent Setup

**Query:** "I want to build an agent with sessions, custom tools, and cost tracking"

**Expected Behavior:**

- Skill activates on multiple keywords
- Follows Multi-Topic Query Pattern
- Directs user to query docs-management for each topic
- Synthesizes guidance from multiple official docs

**Success Criteria:**

- All three topics addressed
- No conflicting guidance
- References to official docs for each topic

### Scenario 5: Production Hosting Decision

**Query:** "Should I use ephemeral or persistent sessions for my production agent?"

**Expected Behavior:**

- Skill activates on keywords "hosting", "sessions", "production"
- Directs user to query docs-management: "hosting Agent SDK", "ephemeral sessions", "persistent sessions"
- Provides comparison of hosting patterns from official docs

**Success Criteria:**

- User understands both patterns
- Decision criteria clearly explained
- User can choose based on their requirements

## Multi-Model Testing Notes

**Model Compatibility:**

This skill uses a pure delegation pattern with keyword-based queries, which is model-agnostic. The skill has been designed to work across all Claude models.

**Testing Approach by Model Family:**

- **Sonnet** (Primary) - Designed and validated with this model family
  - Delegation patterns verified
  - Keyword registry enables efficient queries
  - Pure delegation architecture minimizes context load

- **Haiku** (Recommended for simple queries)
  - Expected: Excellent performance due to minimal skill context
  - Pure delegation means SKILL.md is the only context load
  - Keyword registry enables targeted, efficient docs-management queries

- **Opus** (Recommended for complex SDK scenarios)
  - Expected: Excellent performance with advanced reasoning
  - Complex multi-topic queries supported
  - Can synthesize guidance from multiple official docs

**Performance Expectations:**

- Pure delegation pattern works excellently across all models
- Minimal context load (~2,000 tokens for SKILL.md)
- All complexity offloaded to docs-management queries
- Keyword registry ensures targeted queries regardless of model

**Last Tested:** Pending verification across model families

## Repository-Specific Notes

This repository does not currently use the Agent SDK programmatically. The Agent SDK documentation is relevant for:

- Understanding how Claude Code skills/hooks/subagents work (same underlying architecture)
- Building custom agents that integrate with this repository's documentation
- Understanding the relationship between Claude Code and Agent SDK features

When working with Agent SDK topics, always use the docs-management skill to access official documentation.

## References

**Official Documentation (via docs-management skill):**

- Primary: "agent-sdk" documentation (overview, typescript, python, sessions, custom-tools, etc.)
- Related: "mcp", "hooks", "skills", "sub-agents"

**External Resources:**

- TypeScript SDK GitHub: anthropics/claude-agent-sdk-typescript
- Python SDK GitHub: anthropics/claude-agent-sdk-python
