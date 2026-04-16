# Linear Integration

This guide covers how to interact with Linear from within your Replicas workspace.

## Prerequisites

Check if the `LINEAR_ACCESS_TOKEN` environment variable is set:

```bash
echo "${LINEAR_ACCESS_TOKEN:+set}"
```

- If **set**: Your workspace has Linear access. You can use the Linear GraphQL API as described below.
- If **not set**: Linear has not been configured for this workspace. The user needs to connect Linear in the [Replicas dashboard](https://replicas.dev) under their organization's integration settings. Let the user know and do not attempt Linear operations.

## Using the Linear API

Linear uses a GraphQL API at `https://api.linear.app/graphql`. All requests use the `$LINEAR_ACCESS_TOKEN` for authentication.

### Fetching an Issue

If you encounter a Linear issue link (e.g. `https://linear.app/team/issue/ENG-123`), the identifier is the last path segment (`ENG-123`).

```bash
curl -s -X POST https://api.linear.app/graphql \
  -H "Authorization: Bearer $LINEAR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "query { issues(filter: { identifier: { eq: \"ENG-123\" } }) { nodes { id identifier title description state { name } assignee { name } parent { identifier title description } } } }"
  }'
```

### Updating Issue State

```bash
curl -s -X POST https://api.linear.app/graphql \
  -H "Authorization: Bearer $LINEAR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "mutation { issueUpdate(id: \"ISSUE_UUID\", input: { stateId: \"STATE_UUID\" }) { success issue { identifier state { name } } } }"
  }'
```

To find available states, query: `query { workflowStates { nodes { id name } } }`

### Adding a Comment

```bash
curl -s -X POST https://api.linear.app/graphql \
  -H "Authorization: Bearer $LINEAR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "mutation { commentCreate(input: { issueId: \"ISSUE_UUID\", body: \"Your comment here\" }) { success comment { id } } }"
  }'
```

### Searching Issues

```bash
curl -s -X POST https://api.linear.app/graphql \
  -H "Authorization: Bearer $LINEAR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "query { issueSearch(query: \"search terms\", first: 10) { nodes { identifier title state { name } } } }"
  }'
```

### Other Operations

The Linear GraphQL API supports creating issues, managing projects, labels, cycles, and more. For the full schema and documentation, see: https://developers.linear.app/docs/graphql/working-with-the-graphql-api
