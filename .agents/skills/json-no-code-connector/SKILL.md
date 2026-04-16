---
name: json-no-code-connector
description: Domo JSON (no-code) connector via Product API — accounts, streams, executions for REST/JSON API ingestion into Domo.
---

# Domo JSON Connector — Product API Reference

> **Primary data ingestion path for REST/JSON APIs.** Always try the JSON connector first when the source is a REST API. If it fails (auth, parsing, or pagination issues), fall back to the Java CLI (`domo-data-upload` skill). See that skill's guide for the two-path fallback pattern.

## Overview

The Domo JSON (No Code) connector uses `dataProviderType: "json5"`. It is managed via the Product API:

```
POST /api/data/v1/accounts          Create an account
GET  /api/data/v1/accounts           List all accounts
GET  /api/data/v1/accounts/{id}      Get a specific account
POST /api/data/v1/streams                      Create a connector (stream)
GET  /api/data/v1/streams                      List all streams
GET  /api/data/v1/streams?limit=500            List streams (paginated)
POST /api/data/v1/streams/{id}/executions      Run a stream
```

Authentication to the API itself uses the `X-Domo-Developer-Token` header.

## Workflow

Creating a JSON connector requires four steps in order:

1. **Inspect the API** — fetch the target URL and examine the JSON structure to determine the correct parsing rules.
2. **Create an account** (`POST /api/data/v1/accounts`) — defines the authentication method (none, basic auth, or API key) for the target API.
3. **Create a stream** (`POST /api/data/v1/streams`) — defines the connector configuration (URL, paging, parsing) and links it to the account created in step 2.
4. **Run the stream** (`POST /api/data/v1/streams/{id}/executions`) — triggers the connector to fetch data and populate the dataset.

You must create the account before the stream, because the stream requires an `accountId` reference.

### Step 1: Inspect the API and plan parsing

Before creating the connector, fetch the API URL and examine the JSON response to determine the correct `jsonParsing` rules. The goal is to flatten nested JSON into a tabular structure (rows and columns).

```bash
curl -s "https://api.example.com/v1/data" | python3 -m json.tool | head -50
```

Identify the response shape and choose the right pattern:

#### Pattern A: Top-level flat array — no parsing needed

If the response is already a flat array of objects, no parsing rules are required. Each array element becomes a row, each key becomes a column.

```json
[
  { "id": 1, "title": "...", "body": "...", "userId": 1 },
  { "id": 2, "title": "...", "body": "...", "userId": 1 }
]
```

Parsing: `{"parsing": ""}`

Result columns: `id`, `title`, `body`, `userId`

**Tested with:** JSONPlaceholder (`/posts`) → 100 rows, 4 columns. Jokes API (`/jokes/ten`) → 10 rows, 4 columns (`type`, `setup`, `punchline`, `id`).

#### Pattern B: Object wrapping an array — use `expandRow`

If the response is an object with a nested array of records, use `expandRow` to turn each array element into a row.

```json
{
  "current_page": 1,
  "total": 332,
  "data": [
    { "fact": "Cats sleep 70% of their lives.", "length": 30 },
    { "fact": "A group of cats is called a clowder.", "length": 38 }
  ]
}
```

Parsing: `{"parsing": "0.1:expandRow(data)\n"}`

Result columns: `data_fact`, `data_length`, plus all top-level fields (`current_page`, `total`, `per_page`, etc.) repeated on every row.

**Important:** After `expandRow`, the nested fields are prefixed with the array name. So `data[].fact` becomes `data_fact`.

**Tested with:** Cat Facts (`catfact.ninja/facts`) → 100 rows. The `data` array was expanded, and each fact became a row with the parent metadata repeated.

#### Pattern C: Top-level array with nested objects — use `flattenObject`

If the response is a top-level array but each element contains nested objects, use `flattenObject` to promote the nested keys to top-level columns.

```json
[
  {
    "name": { "common": "France", "official": "French Republic" },
    "capital": ["Paris"],
    "region": "Europe",
    "population": 67390000
  }
]
```

Parsing: `{"parsing": "0.0:flattenObject(name)\n"}`

Result columns: `name_common`, `name_official`, `capital`, `region`, `population`. The `nativeName` sub-object (deeper nesting) remains as a JSON string unless further flattened.

**Depth notation:** For top-level arrays, use `0.0` (first object in array). For nested arrays after `expandRow`, the depth increases (e.g. `0.1.0`).

**Tested with:** REST Countries → 250 rows. `flattenObject(name)` produced `name_common` and `name_official` as separate columns. The deeper `nativeName` stayed as a JSON string.

#### Pattern D: Single object with nested objects — use multiple `flattenObject`

If the response is a single object (1 row) with nested objects, flatten each nested object separately.

```json
{
  "latitude": 40.76,
  "longitude": -111.89,
  "current_weather": {
    "temperature": 11.6,
    "windspeed": 2.2,
    "winddirection": 270
  },
  "current_weather_units": {
    "temperature": "°C",
    "windspeed": "km/h"
  }
}
```

Parsing: `{"parsing": "0.0:flattenObject(current_weather)\n0.0:flattenObject(current_weather_units)\n"}`

Result columns: `latitude`, `longitude`, `current_weather_temperature`, `current_weather_windspeed`, `current_weather_winddirection`, `current_weather_units_temperature`, `current_weather_units_windspeed`, etc.

**Multiple `flattenObject` rules can share the same depth** (`0.0`) when they operate on sibling objects at the same level.

**Tested with:** Open-Meteo Weather API → 1 row, 21 columns. Both `current_weather` and `current_weather_units` were flattened with prefixed column names.

#### Pattern E: Object with array + nested objects — combine `expandRow` + `flattenObject`

For complex responses like GeoJSON, chain operations. The `expandRow` runs first, then `flattenObject` operates on the expanded results.

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": { "event": "Flood Warning", "severity": "Moderate" },
      "geometry": { ... }
    }
  ]
}
```

Parsing:
```
0.1:expandRow(features)
0.1.0:flattenObject(features_properties)
```

**Key detail:** After `expandRow(features)`, the nested field `properties` is referenced as `features_properties` (prefixed with the array name).

**Tested with:** NWS Weather Alerts API → expanded features array into rows, then flattened properties into individual columns.

#### Parsing rules reference

| Operation | Syntax | When to use |
|---|---|---|
| `expandRow(field)` | `depth:expandRow(arrayField)` | Object contains an array that should become rows |
| `flattenObject(field)` | `depth:flattenObject(objectField)` | Record contains a nested object whose keys should become columns |

**Depth notation:**
- `0.0` — top-level (first element of array, or root object)
- `0.1` — one level in (e.g. a field within the root object)
- `0.1.0` — two levels in (e.g. after an `expandRow`, within each expanded element)

**Rules for field names after operations:**
- After `expandRow(data)`, child fields are prefixed: `data.fact` → `data_fact`
- After `flattenObject(name)`, child fields are prefixed: `name.common` → `name_common`
- Deeper nesting that isn't explicitly flattened remains as a JSON string in the column

## Authentication Types

The JSON connector supports multiple `credentialsType` values that control how the connector authenticates to the target API.

### No Auth

Use `credentialsType: "fields"` with `authentication` set to `"none"`. For public APIs that require no credentials.

```bash
curl -X POST "https://{instance}.domo.com/api/data/v1/accounts" \
  -H "X-Domo-Developer-Token: {devToken}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Public API Account",
    "displayName": "My Public API Account",
    "type": "data",
    "allowExternalUse": true,
    "dataProviderType": "json5",
    "credentialsType": "fields",
    "configurations": {
      "authentication": "none"
    }
  }'
```

### Basic Auth (username/password)

Use `credentialsType: "fields"` with `username` and `password` in configurations.

```bash
curl -X POST "https://{instance}.domo.com/api/data/v1/accounts" \
  -H "X-Domo-Developer-Token: {devToken}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Basic Auth Account",
    "displayName": "My Basic Auth Account",
    "type": "data",
    "allowExternalUse": true,
    "dataProviderType": "json5",
    "credentialsType": "fields",
    "configurations": {
      "username": "user@example.com",
      "password": "yourPassword"
    }
  }'
```

### API Key in Header

Use `credentialsType: "apikey_header"` with `apiKey` in configurations.

```bash
curl -X POST "https://{instance}.domo.com/api/data/v1/accounts" \
  -H "X-Domo-Developer-Token: {devToken}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My API Key Account",
    "displayName": "My API Key Account",
    "type": "data",
    "allowExternalUse": true,
    "dataProviderType": "json5",
    "credentialsType": "apikey_header",
    "configurations": {
      "apiKey": "your-api-key-here"
    }
  }'
```

## Response

The API returns the created account object. Note:

- `configurations` will be returned as `{}` (empty) — credentials are not echoed back for security.
- `valid` may show `false` in the response but the account is functional on the front-end.
- `createdAt` / `modifiedAt` may be `null` in the initial response.

### Example response

```json
{
  "id": 117,
  "userId": 149955692,
  "name": "My API Key Account",
  "displayName": "My API Key Account",
  "type": "data",
  "valid": false,
  "allowExternalUse": true,
  "dataProviderType": "json5",
  "credentialsType": "apikey_header",
  "createdAt": null,
  "createdBy": 149955692,
  "modifiedAt": null,
  "modifiedBy": 149955692,
  "secretManagerAccountId": null,
  "secretId": null,
  "configurations": {},
  "accountId": 117,
  "accountTemplateId": null,
  "accountTemplateAuthorizationId": null
}
```

## Creating a Connector (Stream)

Use `POST /api/data/v1/streams` to create a fully configured JSON connector with a linked account.

### Required fields

| Field | Description |
|---|---|
| `transport` | Must include `type: "CONNECTOR"`, `description: "com.domo.connector.json.customparsing"`, `version: "4"` |
| `updateMethod` | `"REPLACE"` or `"APPEND"` |
| `dataProvider` | `{ "key": "json5" }` |
| `account` | `{ "id": <accountId>, "accountId": <accountId> }` — reference a previously created account |
| `dataSource` | `{ "name": "...", "description": "..." }` — creates the dataset |
| `configuration` | Array of `{ category, name, type, value }` metadata objects (see below) |

### Configuration array

Each entry is a `METADATA` object with a stringified JSON `value`. The key entries:

| `name` | Purpose |
|---|---|
| `jsonSelection` | URL, HTTP method, headers, query params, date filters, connection method |
| `jsonPaging` | Pagination config: type (offset/token/etc.), limit, base URL |
| `jsonParsing` | Parsing rules (e.g. `flattenObject(owner)`) |
| `schema` | `{"automatedSchema": true}` for auto-detect |
| `cloud` | Cloud identifier (e.g. `"domo"`) |
| `_description_` | Dataset description (can be empty string) |

### Full example

```bash
curl -X POST "https://{instance}.domo.com/api/data/v1/streams" \
  -H "X-Domo-Developer-Token: {devToken}" \
  -H "Content-Type: application/json" \
  -d '{
  "transport": {
    "type": "CONNECTOR",
    "description": "com.domo.connector.json.customparsing",
    "version": "4"
  },
  "updateMethod": "REPLACE",
  "dataProvider": {
    "key": "json5"
  },
  "account": {
    "id": 116,
    "accountId": 116
  },
  "dataSource": {
    "name": "My JSON Connector",
    "description": "Created via API"
  },
  "configuration": [
    {
      "category": "METADATA",
      "name": "jsonSelection",
      "type": "string",
      "value": "{\"connectionMethod\":\"Advanced\",\"jsonUrl\":\"https://api.example.com/v1/data\",\"httpMethod\":\"GET\",\"jsonLineReader\":\"false\",\"escapeBackslash\":\"false\",\"httpsHeaders\":[],\"body\":\"\",\"queryParameters\":[],\"dynamicSetup\":[{}],\"useDateFilter\":false,\"dateSelection\":{\"dateType\":\"date_range\",\"startDate\":{\"type\":\"relative\",\"offset\":0},\"endDate\":{\"type\":\"relative\",\"offset\":0}},\"dateQueryParamsFormat\":\"yyyy-MM-dd\",\"certificateInputType\":\"NoCertificate\",\"encodeParameterKey\":true,\"encodeParameterValue\":true,\"datasetType\":\"static\",\"dateParameter\":{\"dateType\":\"single_date\",\"dateFrom\":\"relative\",\"dateFromOffset\":1,\"dateTo\":\"relative\",\"dateToOffset\":0,\"date\":\"relative\",\"dateOffset\":1},\"useBody\":false,\"dynamicValuesType\":\"enter\",\"rateLimitSelection\":\"false\",\"timeUnit\":\"second\",\"dateParameterType\":\"separate\",\"useDateAtMidnight\":false}"
    },
    {
      "category": "METADATA",
      "name": "jsonPaging",
      "type": "string",
      "value": "{\"baseUrl\":\"https://api.example.com/v1/data\",\"tokenType\":\"path\",\"pagingType\":\"offset\",\"parsing\":\"\",\"total\":\"false\",\"pageLimitValue\":\"50\",\"startPage\":\"1\",\"encodeParameterValue\":true,\"encodeParameterKey\":true,\"offsetParameter\":\"offset\",\"pageLimitParameter\":\"limit\"}"
    },
    {
      "category": "METADATA",
      "name": "jsonParsing",
      "type": "string",
      "value": "{\"parsing\":\"\"}"
    },
    {
      "category": "METADATA",
      "name": "schema",
      "type": "string",
      "value": "{\"automatedSchema\":true}"
    },
    {
      "category": "METADATA",
      "name": "cloud",
      "type": "string",
      "value": "domo"
    },
    {
      "category": "METADATA",
      "name": "_description_",
      "type": "string",
      "value": ""
    }
  ]
}'
```

### Stream response notes

- The response includes the full `dataProvider` with `authenticationSchemeConfiguration` showing all available credential fields.
- `dataSource.id` in the response is the new dataset UUID.
- `account.valid` will show `true` if the account was created with credentials.
- Default schedule is `MANUAL`. Set `advancedScheduleJson` for automated runs (e.g. `{"type":"DAY","at":"06:00 AM","timezone":"America/Denver"}`).

## Running a Stream (Execution)

After creating a stream, trigger it to run with `POST /api/data/v1/streams/{streamId}/executions`.

```bash
curl -X POST "https://{instance}.domo.com/api/data/v1/streams/{streamId}/executions" \
  -H "X-Domo-Developer-Token: {devToken}" \
  -H "Content-Type: application/json"
```

### Example response

```json
{
  "streamId": 561,
  "executionId": 2,
  "startedAt": 1774666802.49,
  "endedAt": null,
  "updateMethod": "REPLACE",
  "currentState": "ACTIVE",
  "rowsInserted": 0,
  "bytesInserted": 0,
  "startedBy": "149955692",
  "errors": []
}
```

### Execution notes

- `currentState` will be `"ACTIVE"` while running, then `"SUCCESS"` or `"ERROR"` when complete.
- No request body is needed — just POST to the endpoint.
- After creating a stream, always trigger an execution so data is populated immediately.

## HubSpot CRM Pattern

HubSpot's CRM API (`/crm/v3/objects/{type}`) wraps records in a `results` array, and each record has a nested `properties` object. Use Pattern E (expandRow + flattenObject):

**Response shape:**
```json
{
  "results": [
    { "id": "123", "properties": { "email": "...", "firstname": "..." } }
  ],
  "paging": { "next": { "after": "124" } }
}
```

**Parsing rules:**
```
0.1:expandRow(results)
0.1.0:flattenObject(results_properties)
```

**Auth:** Use `credentialsType: "fields"` / `authentication: "none"` for the account, and inject the Bearer token in `jsonSelection.httpsHeaders`:
```json
"httpsHeaders": [{"name": "Authorization", "value": "Bearer pat-na2-..."}]
```

**Result columns:** `results_id`, `results_properties_email`, `results_properties_firstname`, etc.

## Important Notes

- The `PUT` and `PATCH` methods are **not supported** on `/api/data/v1/accounts/{id}` — returns 405. To change credentials, create a new account.
- The `authType` field is **not a valid configuration** for `json5` — using it returns a 400 error: `"Data provider 'json5' does not have 'authType' authentication scheme configuration"`.
- Always set `type: "data"` for data connector accounts.
- The `configuration` array values must be **stringified JSON** — not nested objects.
