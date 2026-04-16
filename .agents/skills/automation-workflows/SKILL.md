---
name: automation-workflows
cluster: community
description: "General workflow automation: IFTTT-style triggers, webhook chains, data transformation pipelines"
tags: ["automation","workflow","webhook","integration"]
dependencies: []
composes: []
similar_to: []
called_by: []
authorization_required: false
scope: general
model_hint: claude-sonnet
embedding_hint: "workflow automation ifttt trigger webhook chain transform pipeline"
---

# automation-workflows

## Purpose
This skill automates workflows using IFTTT-style triggers (e.g., event-based or time-based), chains webhooks for service integration, and builds data transformation pipelines to process and route data efficiently.

## When to Use
Use this skill for automating repetitive tasks like syncing data between apps, responding to web events (e.g., API calls or file changes), or creating custom pipelines for data processing. It's ideal for integrations in development, IoT, or business automation where triggers and actions need chaining.

## Key Capabilities
- Define triggers via simple configs, e.g., JSON files with formats like {"trigger": "http-post", "url": "https://example.com/hook"}.
- Chain webhooks to sequence actions, such as triggering a script on a GitHub event then posting to Slack.
- Build data pipelines for transformations, e.g., using built-in functions like JSON.parse() or custom JS snippets for data mapping.
- Support conditional logic in workflows, e.g., if-then rules based on payload data.
- Handle asynchronous operations, like scheduling tasks with cron-like expressions (e.g., "0 0 * * *" for daily runs).

## Usage Patterns
To set up a workflow, first define it in a YAML config file (e.g., workflow.yaml with keys for triggers, actions, and transforms). Load it via CLI or API, then test by simulating triggers. For ongoing use, schedule workflows with system cron or the skill's built-in scheduler. Always use environment variables for sensitive data, like $WORKFLOW_API_KEY in configs. Monitor execution logs for debugging, and chain multiple workflows by referencing outputs as inputs.

## Common Commands/API
Use the OpenClaw CLI for most operations; authenticate with $WORKFLOW_API_KEY via env var. Key commands:
- Create a workflow: `claw workflow create --file workflow.yaml --key $WORKFLOW_API_KEY`
- Run a workflow: `claw workflow run --id 123 --trigger manual`
- List workflows: `claw workflow list --cluster community`
API endpoints under https://api.openclaw.com/workflows:
- POST /workflows to create: Send JSON body like {"name": "my-flow", "trigger": {"type": "webhook", "url": "https://hook.example.com"}}.
- GET /workflows/{id} to retrieve details.
Code snippet for API call in Python:
```python
import requests; import os
key = os.environ.get('WORKFLOW_API_KEY')
response = requests.post('https://api.openclaw.com/workflows', json={"name": "test"}, headers={'Authorization': f'Bearer {key}'})
print(response.json())
```
For data transformations, use inline JS in configs: e.g., {"transform": "return data.map(item => item * 2);"} to process arrays.

## Integration Notes
Integrate by exposing webhooks via the skill's server (e.g., run `claw server start --port 8080` to listen on a port). For external services, include auth in configs, like {"action": "webhook", "url": "https://api.service.com/endpoint", "headers": {"Authorization": "Bearer $SERVICE_API_KEY"}}. Use JSON for payload formats, e.g., {"event": "push", "data": {...}}. Chain integrations by referencing previous outputs, such as piping a GitHub webhook to a database insert. Ensure services support HTTP callbacks; test with tools like Postman.

## Error Handling
Always check API responses for status codes (e.g., if response.status_code != 200, log error). In CLI commands, use --debug flag for verbose output, e.g., `claw workflow run --id 123 --debug`. Handle common errors like invalid keys by validating env vars first (e.g., in scripts: if not os.environ.get('WORKFLOW_API_KEY'): raise ValueError("Key missing")). For workflows, define error handlers in configs, like {"onError": "retry 3 times"} or {"onError": "notify slack"}. Code snippet for error wrapping:
```python
try:
    response = requests.post(url, headers=headers)
    response.raise_for_status()
except requests.exceptions.HTTPError as e:
    print(f"Error: {e} - Retrying...")
```
Log all failures to a file or service for auditing.

## Graph Relationships
- Related to: integration (shares webhook handling), automation (common triggers), workflow-management in community cluster.
- Depends on: webhook-services for external triggers.
- Connected to: data-pipelines skill for advanced transformations.
