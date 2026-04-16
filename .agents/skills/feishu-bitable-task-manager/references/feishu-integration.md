# Feishu API Interaction (Reference)

Minimal Feishu API calls needed to fetch and update tasks from Bitable while staying compatible with the task table schema.

## 1) Auth (tenant access token)

- Endpoint: `POST /open-apis/auth/v3/tenant_access_token/internal`
- Body:
  - `app_id`: from `FEISHU_APP_ID`
  - `app_secret`: from `FEISHU_APP_SECRET`
- Response:
  - `tenant_access_token` (use as `Authorization: Bearer <token>`)

## 2) Bitable identity resolution

### Standard Bitable URL
- Extract `app_token`, `table_id`, optional `view_id` from the URL.
- `table_id` is required and lives in the query string (e.g. `?table=tblxxx`).

### Wiki-based Bitable URL
- If the URL only has `wiki_token`, resolve `app_token` with:
  - Endpoint: `GET /open-apis/wiki/v2/spaces/get_node?token=<wiki_token>`
  - Expect `data.node.obj_type == "bitable"`
  - Use `data.node.obj_token` as the bitable app token.

## 3) Task fetch via Bitable search

- Endpoint:
  - `POST /open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/search`
- Query params:
  - `page_size` (1~500)
  - `page_token` (optional)
- Body:
  - `view_id` (optional, unless ignoring view)
  - `filter` (table filter; see next section)
- Response (core fields):
  - `data.items[]` (records with `record_id` + `fields`)
  - `data.has_more` (bool)
  - `data.page_token` (next page token)

## 4) Table filter

Build filter with conjunction `and` and the following conditions:
- `App` is `<app>`
- `Scene` is `<scene>`
- `Status` is `<status>` (default `pending`)
- `Date` is `Today` / `Yesterday` / `Any`
  - `Any` means no date constraint.

Example filter payload:

```json
{
  "conjunction": "and",
  "conditions": [
    {"field_name": "App", "operator": "is", "value": ["com.smile.gifmaker"]},
    {"field_name": "Scene", "operator": "is", "value": ["个人页搜索"]},
    {"field_name": "Status", "operator": "is", "value": ["pending"]},
    {"field_name": "Date", "operator": "is", "value": ["Today"]}
  ]
}
```

## 5) Field mapping

Treat task table columns as configurable. Use `TASK_FIELD_*` env vars to override column names when your schema differs.

Key fields:
- TaskID, BizTaskID, ParentTaskID
- App, Scene, Params, ItemID
- BookID, URL, UserID, UserName
- Date, Status, Logs, LastScreenShot
- GroupID, DeviceSerial, DispatchedDevice, DispatchedAt
- StartAt, EndAt, ElapsedSeconds, ItemsCollected, Extra, RetryCount

## 6) Validation rules

Keep only rows with:
- `TaskID != 0`
- At least one of `Params`, `ItemID`, `BookID`, `URL`, `UserID`, `UserName`

## 7) Task updates (single record)

- Endpoint:
  - `PUT /open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/{record_id}`
- Body:
  - `fields`: map of column name → value
- Response:
  - `{code: 0}` on success

Example payload:

```json
{
  "fields": {
    "Status": "running",
    "DispatchedDevice": "1fa20bb",
    "DispatchedAt": 1769502565740
  }
}
```

## 8) Task updates (batch)

- Endpoint:
  - `POST /open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/batch_update`
- Body:
  - `records`: list of `{record_id, fields}`
- Response:
  - `data.records` list when successful

Example payload:

```json
{
  "records": [
    {
      "record_id": "recv9uh3a5va06",
      "fields": {"Status": "success", "ElapsedSeconds": 16}
    },
    {
      "record_id": "recv9uh3SYCfhZ",
      "fields": {"Status": "failed", "Logs": "s3://bucket/log.txt"}
    }
  ]
}
```

## 9) Task create (single record)

- Endpoint:
  - `POST /open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records`
- Body:
  - `fields`: map of column name → value
- Response:
  - `{code: 0}` on success

Example payload:

```json
{
  "fields": {
    "TaskID": 180413,
    "App": "com.smile.gifmaker",
    "Scene": "综合页搜索",
    "Status": "pending",
    "Date": "2026-01-27"
  }
}
```

## 10) Task create (batch)

- Endpoint:
  - `POST /open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/batch_create`
- Body:
  - `records`: list of `{fields}`
- Response:
  - `data.records` list when successful

Example payload:

```json
{
  "records": [
    {
      "fields": {"TaskID": 180413, "Status": "pending"}
    },
    {
      "fields": {"TaskID": 180414, "Status": "pending"}
    }
  ]
}
```
