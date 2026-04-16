# Tool Contracts

## Search

Goal: Find the right entity before taking action.

Recommended functions:

```text
search_entities(app, entity_type, filters, query, limit=20)
get_entity(app, entity_type, id, fields)
list_related(app, entity_type, id, relation_type, filters)
```

Output pattern:

```json
[
  {"id":"...", "title":"...", "updated_at":"...", "snippet":"...", "score":0.92}
]
```

Notes:

- Return candidates first for disambiguation.
- Keep default result size small (`5-20`) and paginate.

## Summarize

Goal: Convert long context into executable information.

Recommended functions:

```text
summarize(content, schema, citations=true)
summarize_entity(app, entity_type, id, schema, citations=true)
```

Required output sections:

- conclusion
- evidence/citations
- next actions
- risks
- open questions

Rules:

- Every key claim should map to source ids/links.
- Never invent missing fields (for example amount, date, owner).

## Draft

Goal: Generate actionable drafts without auto-submitting.

Recommended functions:

```text
draft_reply(context, tone, constraints, required_points)
draft_doc(template, inputs, sections)
draft_variants(n, style_tags)
```

Rules:

- Include hard constraints: must include, must avoid, legal/SLA limits.
- Default to draft/internal-note state.

## Update

Goal: Write decisions back into SaaS safely.

Recommended functions:

```text
add_comment(entity, text, visibility)
set_status(entity, status)
assign_owner(entity, owner_id)
set_fields(entity, patch)
add_tags(entity, tags)
remove_tags(entity, tags)
link_entities(a, b, relation_type)
```

Rules:

- Require idempotency key for mutating calls.
- Use field allowlist; reject unrestricted patch updates.

## Notify

Goal: Ensure stakeholders know what to do next.

Recommended functions:

```text
notify(channel, recipients, message, severity, links, attachments)
create_task(app, title, description, assignee, due_date)
escalate(entity, reason, to_team)
```

Notification minimum:

- object link
- short summary (`3-5` lines)
- proposed next step and owner
- approval action path if needed

## Approve

Goal: Gate high-risk operations with human confirmation.

Recommended functions:

```text
request_approval(action, payload, risk_level, approvers, expiry)
execute_approved(approval_id)
```

Rules:

- Re-validate state and permissions before execution.
- Expire stale approvals and force re-request.
