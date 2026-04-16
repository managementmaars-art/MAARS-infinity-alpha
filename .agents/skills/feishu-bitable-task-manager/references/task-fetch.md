# Task Fetch Notes

Use these behaviors when pulling tasks from Feishu Bitable to stay compatible with the task table schema.

## Filter behavior

Build the filter with these columns:
- `App` is `is <app>`
- `Scene` is `is <scene>`
- `Status` is `is <status>` (default `pending`)
- `Date` is `is <preset>` where preset is `Today`/`Yesterday`/`Any`
  - `Any` skips the date constraint.

Direct fetch overrides:
- If `--task-id` is provided, fetch by `TaskID` only (no other params required).
- If `--biz-task-id` is provided, fetch by `BizTaskID` only (no other params required).

Relevant date presets:
- `TaskDateToday = "Today"`
- `TaskDateYesterday = "Yesterday"`
- `TaskDateAny = "Any"`

## Pagination and query options

- Always ignore view filtering unless explicitly requested.
- `Limit` caps the total rows returned.
- `PageToken` + `MaxPages = 1` enables incremental scanning.
- Use `has_more` + `page_token` to continue scans.
- Use `--raw` when you need `record_id` or original field payloads for debugging.

## Validation rules (decoded tasks)

Discard rows that:
- Have `TaskID == 0`.
- Are missing all of: `Params`, `ItemID`, `BookID`, `URL`, `UserID`, `UserName`.

## TASK_BITABLE_URL task status table fields

Use `TASK_FIELD_*` env vars to override column names when the task table schema differs.

Core identifiers:
- `TaskID`: primary task ID (integer, required for selection).
- `BizTaskID`: external/business task identifier (optional).
- `ParentTaskID`: parent task ID for grouped tasks (optional).

Task routing:
- `App`: app/package name for filtering (e.g. `com.smile.gifmaker`).
- `Scene`: task scene/category (e.g. 综合页搜索/个人页搜索/单个链接采集).
- `Params`: task payload (keyword or serialized params).
- `ItemID`: single-item identifier (scene-specific).
- `BookID`: drama/collection identifier (scene-specific).
- `URL`: target share URL for single-link tasks.
- `UserID`: account/user identifier (optional).
- `UserName`: account/user display name (optional).

Scheduling & state:
- `Date`: scheduling preset string (`Today`/`Yesterday`/`Any` or a raw date string).
- `Status`: task lifecycle status (pending/running/success/failed/error/etc.).
- `RetryCount`: retry counter (integer).

Execution metadata:
- `GroupID`: group key for related tasks.
- `DeviceSerial`: preferred device serial (optional).
- `DispatchedDevice`: actual dispatched device serial.
- `DispatchedAt`: dispatch timestamp (epoch ms or string).
- `StartAt`: execution start timestamp.
- `EndAt`: execution end timestamp.
- `ElapsedSeconds`: execution duration in seconds.
- `ItemsCollected`: number of items collected for this task run.

Reporting:
- `Logs`: log path or log identifier.
- `LastScreenShot`: attachment field for the last screenshot.
- `Extra`: JSON blob for additional metadata.
