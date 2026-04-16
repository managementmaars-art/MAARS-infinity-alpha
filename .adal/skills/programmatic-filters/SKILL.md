---
name: programmatic-filters
description: Control which data each viewer sees in an embedded Domo dashboard/card via server-side programmatic filters and dataset switching. Covers the OAuth → embed token flow, standard filters, SQL filters (OR/BETWEEN/LIKE), per-dataset targeting, datasetRedirects for multi-tenant architectures, and token size limits. Use for any per-viewer, per-role, or per-tenant data restrictions at embed time. Not for client-side JS API filtering (use jsapi-filters).
---

# Domo Programmatic Filtering

Control what data each viewer sees in embedded Domo content via server-side filters and dataset switching. Enforced by Domo — end users can't bypass. For client-side filtering, see `jsapi-filters`.

## How It Works

A proxy user (service account) acts on behalf of all viewers. Your server:

1. Authenticates with Domo (OAuth client credentials → **access token**)
2. Requests an **embed token** with viewer-specific filters
3. Returns the token to the client, which POSTs it to an iframe

## Prerequisites

- Domo API client with `CLIENT_ID` and `CLIENT_SECRET` (developer.domo.com > My Account > New Client)
- Embed ID (5-char ID from the embed dialog, not the page URL)
- Dataset column names/IDs for filtering

**All auth must happen server-side** (CORS restrictions). Never expose credentials client-side.

## The Embed Token Flow

### Step 1: Get an Access Token

```
POST https://api.domo.com/oauth/token?grant_type=client_credentials&scope=data%20audit%20user%20dashboard
Authorization: Basic base64(CLIENT_ID:CLIENT_SECRET)
```

**Node.js:**
```typescript
const credentials = Buffer.from(`${CLIENT_ID}:${CLIENT_SECRET}`).toString('base64')

const response = await fetch(
  'https://api.domo.com/oauth/token?grant_type=client_credentials&scope=data%20audit%20user%20dashboard',
  {
    method: 'GET',
    headers: { Authorization: `Basic ${credentials}` }
  }
)

const { access_token } = await response.json()
```

**Python:**
```python
import requests
from base64 import b64encode

credentials = b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()

response = requests.get(
    "https://api.domo.com/oauth/token",
    params={"grant_type": "client_credentials", "scope": "data audit user dashboard"},
    headers={"Authorization": f"Basic {credentials}"}
)

access_token = response.json()["access_token"]
```

### Step 2: Request an Embed Token with Filters

Use the access token to request an embed token, including your filters in the `authorizations` payload:

**For dashboards:**
```
POST https://api.domo.com/v1/stories/embed/auth
Authorization: Bearer {access_token}
Content-Type: application/json
```

**For cards:**
```
POST https://api.domo.com/v1/cards/embed/auth
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Payload structure:**
```json
{
  "sessionLength": 1440,
  "authorizations": [
    {
      "token": "<embed_id>",
      "permissions": ["READ", "FILTER", "EXPORT"],
      "filters": [],
      "policies": []
    }
  ]
}
```

- `sessionLength`: Token validity in minutes (1440 = 24 hours)
- `token`: The embed ID for the dashboard or card
- `permissions`: Array of granted permissions — `READ`, `FILTER`, `EXPORT`
- `filters`: Array of standard filter objects (see below)
- `policies`: Array of PDP policy IDs to apply (optional)

The response includes an `authentication` property containing the embed token.

### Step 3: Render the Embed

Submit via hidden POST form targeting an iframe. Dashboard: `https://public.domo.com/embed/pages/{embed_id}`, Card: `https://public.domo.com/cards/{embed_id}`

```html
<iframe id="domo-embed" name="domo-embed" width="100%" height="600"></iframe>

<form id="embed-form" action="https://public.domo.com/embed/pages/{embed_id}" method="POST" target="domo-embed">
  <input type="hidden" name="embedToken" value="{embed_token}" />
</form>

<script>document.getElementById('embed-form').submit();</script>
```

POST submission prevents the token from appearing in URLs or browser history.

---

## Filter Types

Two types: **standard filters** and **SQL filters**, both in the embed token request.

### Standard Filters

```json
{
  "column": "Region",
  "operator": "IN",
  "values": ["West", "East"]
}
```

**Required properties:**

| Property | Type | Description |
|----------|------|-------------|
| `column` | string | The exact column name in the dataset |
| `operator` | string | The comparison operator (see table below) |
| `values` | array | Values to filter against |

**Optional properties:**

| Property | Type | Description |
|----------|------|-------------|
| `datasourceId` | string (UUID) | Restrict filter to a specific dataset. Without this, the filter applies to all datasets in the embed that have a matching column name. |

#### Operators

| Operator | Description | Typical Use |
|----------|-------------|-------------|
| `IN` | Column value is in the list | Multi-value match |
| `NOT_IN` | Column value is not in the list | Exclusion |
| `EQUALS` | Column value equals | Single-value exact match |
| `NOT_EQUALS` | Column value does not equal | Single-value exclusion |
| `GREATER_THAN` | Column value is greater than | Numeric/date range |
| `GREATER_THAN_EQUALS_TO` | Column value is greater than or equal | Numeric/date range |
| `LESS_THAN` | Column value is less than | Numeric/date range |
| `LESS_THAN_EQUALS_TO` | Column value is less than or equal | Numeric/date range |

#### Standard Filter Examples

**Single filter — show only West region:**
```json
{
  "filters": [
    {
      "column": "Region",
      "operator": "IN",
      "values": ["West"]
    }
  ]
}
```

**Multiple filters — West region, revenue over 10000:**
```json
{
  "filters": [
    {
      "column": "Region",
      "operator": "IN",
      "values": ["West"]
    },
    {
      "column": "Revenue",
      "operator": "GREATER_THAN",
      "values": [10000]
    }
  ]
}
```

**Dataset-specific filter — only apply to one dataset in a multi-dataset dashboard:**
```json
{
  "filters": [
    {
      "column": "Region",
      "operator": "IN",
      "values": ["West"],
      "datasourceId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
    }
  ]
}
```

### SQL Filters

For complex logic (OR, BETWEEN, LIKE, nested expressions), use SQL WHERE syntax via `sqlFilters` (sibling to `filters`, not nested).

```json
{
  "authorizations": [
    {
      "token": "<embed_id>",
      "permissions": ["READ", "FILTER", "EXPORT"],
      "filters": [],
      "sqlFilters": [
        {
          "sqlFilter": "`Region` IN ('West', 'East') AND `Revenue` > 10000",
          "datasourceIds": ["xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"]
        }
      ]
    }
  ]
}
```

**Required properties:**

| Property | Type | Description |
|----------|------|-------------|
| `sqlFilter` | string | SQL WHERE clause syntax |

**Optional properties:**

| Property | Type | Description |
|----------|------|-------------|
| `datasourceIds` | string[] | Array of dataset UUIDs to apply the filter to |

#### Syntax Rules

Column names in **backticks**, strings in **single quotes**, numerics unquoted. Supports: `IN`, `NOT IN`, `BETWEEN`, `LIKE`, `AND`, `OR`, `IS NULL`, `IS NOT NULL`. Use parentheses for grouping.

#### SQL Filter Examples

**OR condition (not possible with standard filters alone):**
```json
{
  "sqlFilter": "`Region` = 'West' OR `Department` = 'Sales'"
}
```

**BETWEEN for date ranges:**
```json
{
  "sqlFilter": "`Order Date` BETWEEN '2024-01-01' AND '2024-12-31'"
}
```

**LIKE for partial matching:**
```json
{
  "sqlFilter": "`Product Name` LIKE '%Pro%'"
}
```

**Complex nested logic:**
```json
{
  "sqlFilter": "(`Region` IN ('West', 'East') AND `Revenue` > 10000) OR `Priority` = 'Critical'"
}
```

**Targeting specific datasets:**
```json
{
  "sqlFilter": "`Status` = 'Active'",
  "datasourceIds": [
    "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy"
  ]
}
```

### Combining Standard and SQL Filters

Both can coexist in one authorization. Standard filters apply first, then SQL filters narrow further:

```json
{
  "token": "<embed_id>",
  "permissions": ["READ", "FILTER", "EXPORT"],
  "filters": [
    {
      "column": "Region",
      "operator": "IN",
      "values": ["West"]
    }
  ],
  "sqlFilters": [
    {
      "sqlFilter": "`Revenue` > 10000 OR `Priority` = 'Critical'"
    }
  ]
}
```

---

## Common Patterns

### Per-User Filtering

Store user-to-filter mappings in your database, look up at embed time:

```typescript
// Pseudocode — adapt to your framework and data layer
async function getEmbedTokenForUser(userId: string, embedId: string) {
  const user = await getUser(userId)
  const dashboard = user.dashboards.find(d => d.embedId === embedId)

  const filters = dashboard.filters.map(f => ({
    column: f.column,
    operator: f.operator,
    values: f.values
  }))

  const accessToken = await getDomoAccessToken()
  const embedToken = await getDomoEmbedToken(accessToken, embedId, filters)

  return embedToken
}
```

### Role-Based Filtering

Apply different filters based on user role rather than individual assignments:

```typescript
function getFiltersForRole(role: string): Filter[] {
  switch (role) {
    case 'regional-manager':
      return [{ column: 'Region', operator: 'IN', values: [user.region] }]
    case 'executive':
      return [] // No filters — sees everything
    case 'analyst':
      return [{ column: 'Department', operator: 'EQUALS', values: [user.department] }]
    default:
      return [{ column: 'Public', operator: 'EQUALS', values: ['true'] }]
  }
}
```

---

## Dataset Switching

Redirect the underlying dataset of an embedded dashboard at embed time — useful for multi-tenant architectures where each customer has their own dataset with the same schema.

### How It Works

Pass `datasetRedirects` in the authorization object (original dataset ID → target dataset ID):

```json
{
  "sessionLength": 1440,
  "authorizations": [
    {
      "token": "<embed_id>",
      "permissions": ["READ", "FILTER", "EXPORT"],
      "filters": [],
      "datasetRedirects": {
        "original-dataset-uuid-1": "target-dataset-uuid-1",
        "original-dataset-uuid-2": "target-dataset-uuid-2"
      }
    }
  ]
}
```

Target datasets must match the original schema (column names and types).

### Combining with Filters

Redirects apply first, then filters run against the swapped dataset:

```json
{
  "sessionLength": 1440,
  "authorizations": [
    {
      "token": "<embed_id>",
      "permissions": ["READ", "FILTER", "EXPORT"],
      "datasetRedirects": {
        "a19d0ef1-ca31-4bfd-b168-018b93109671": "a19d0ef1-ca31-4bfd-b168-018b93109672"
      },
      "filters": [
        { "column": "Color", "operator": "IN", "values": ["Red"] },
        { "column": "Model", "operator": "IN", "values": ["Mountain", "Road", "Commuter"] }
      ]
    }
  ]
}
```

### Per-User Dataset Switching

Map each tenant to their dataset IDs:

```typescript
function getDatasetRedirects(tenant: Tenant): Record<string, string> {
  // The template dashboard was built on these "original" datasets
  const templateDatasets = {
    sales: 'aaaa-bbbb-cccc-dddd',
    inventory: 'eeee-ffff-gggg-hhhh'
  }

  // Each tenant has their own copies
  return {
    [templateDatasets.sales]: tenant.salesDatasetId,
    [templateDatasets.inventory]: tenant.inventoryDatasetId
  }
}
```

### Important Notes

- **Schema must match** — column names and types must be identical (cards, filters, and calculated fields reference by name)
- **Partial redirects OK** — redirect all, some, or none of a dashboard's datasets
- **Compatible with all filter types** — redirects apply first, then standard/SQL/PDP filters

---

## Gotchas and Best Practices

- **JWT size limit (~8KB):** Long value lists hit this. Solutions: aggregate columns in Domo, use SQL filters, or split with `datasourceId` targeting.
- **Column name matching:** Exact spelling and case required. Without `datasourceId`, filters apply to all datasets with a matching column.
- **Token refresh:** Cache access tokens, refresh before expiry. Generate embed tokens per-request.
- **Empty filters:** `[]` means no filtering (user sees everything). Always include the `filters` key — don't omit it.
- **Filter validation:** `values` must be an array (even for `EQUALS`). Numerics must be numbers, not strings. Operator names are exact (`GREATER_THAN_EQUALS_TO`, not `GREATER_THAN_OR_EQUAL`).
- **Security:** Never generate tokens client-side. Validate embed ID authorization and filter values server-side. Use minimum `permissions` (omit `EXPORT` if not needed).

---

## TypeScript Type Definitions

```typescript
type FilterOperator =
  | 'IN'
  | 'NOT_IN'
  | 'EQUALS'
  | 'NOT_EQUALS'
  | 'GREATER_THAN'
  | 'GREATER_THAN_EQUALS_TO'
  | 'LESS_THAN'
  | 'LESS_THAN_EQUALS_TO'

interface StandardFilter {
  column: string
  operator: FilterOperator
  values: (string | number)[]
  datasourceId?: string
}

interface SqlFilter {
  sqlFilter: string
  datasourceIds?: string[]
}

type EmbedPermission = 'READ' | 'FILTER' | 'EXPORT'

interface EmbedAuthorization {
  token: string
  permissions: EmbedPermission[]
  filters: StandardFilter[]
  sqlFilters?: SqlFilter[]
  policies?: string[]
  datasetRedirects?: Record<string, string>  // originalDatasetId → targetDatasetId
}

interface EmbedTokenRequest {
  sessionLength: number
  authorizations: EmbedAuthorization[]
}
```

---

## Quick Reference

Read `references/api-endpoints.md` for the complete list of Domo API endpoints used in programmatic filtering.
