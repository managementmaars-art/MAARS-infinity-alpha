---
name: replicas-agent
description: Guide for background coding agents running inside Replicas cloud workspaces
---

# Replicas Agent

You are a background coding agent running inside a Replicas cloud workspace (a remote VM). This skill covers capabilities and best practices specific to this environment.

## Capabilities

This skill provides detailed guides for the following capabilities. **Read the relevant reference file before performing any of these actions.**

### Previews
Expose locally running services (web apps, APIs, databases) as public preview URLs so humans can interact with them directly.

**Reference:** `references/PREVIEWS.md`

Use this when:
- You need to start a service that a human should view or interact with
- The task involves UI work that benefits from human review
- You are verifying frontend/backend integrations visually

### Slack
Send messages, read threads, search conversations, and upload files via the Slack Web API.

**Reference:** `references/SLACK.md`

Use this when:
- You need to send a message to a Slack channel or thread
- You need to read or fetch a Slack conversation
- You encounter a Slack message link and need to retrieve its content
- The task asks you to notify, update, or communicate via Slack

### Linear
Fetch issues, update state, add comments, and search via the Linear GraphQL API.

**Reference:** `references/LINEAR.md`

Use this when:
- You encounter a Linear issue link and need to understand the task
- You need to update an issue's state (e.g. mark as done)
- You need to comment on or search for Linear issues

### GitHub
Use the pre-authenticated `gh` CLI for pull requests, issues, actions, and API calls.

**Reference:** `references/GITHUB.md`

Use this when:
- You need to create, review, or manage pull requests
- You need to interact with GitHub issues or actions
- You need to use the GitHub API for advanced operations
- You need to include images in PR descriptions
