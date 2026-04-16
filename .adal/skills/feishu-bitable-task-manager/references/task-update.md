# Task Update Notes

Use these behaviors when reporting task status updates to the task table.

## Update targets

- Updates are applied by `record_id`.
- If only `TaskID` is available, resolve `record_id` by searching the task table where `TaskID is <id>`.
- If only `BizTaskID` is available, resolve `record_id` by searching the task table where `BizTaskID is <id>`.
- If no matching row exists, the CLI reports `task-id <value> not found` or `biz-task-id <value> not found`.
- Batch updates should be grouped into `records/batch_update` with up to 500 records per request.

## Update fields

Use `TASK_FIELD_*` env vars to override column names when the task table schema differs.

Status & routing:
- `Status`: task lifecycle status (`pending`/`running`/`success`/`failed`/`error` etc.).
- `Date`: task date (accepts epoch seconds/ms, ISO timestamp, or `YYYY-MM-DD`).
- `DispatchedDevice`: device serial bound to the task when dispatched.

Timing:
- `DispatchedAt`: dispatch timestamp (epoch ms).
- `StartAt`: start timestamp (epoch ms). If only `DispatchedAt` is given, set `StartAt` to the same value.
- `EndAt`: completion timestamp (epoch ms).
- `ElapsedSeconds`: derived from `StartAt` + `EndAt` when provided; can be set explicitly.

Metrics:
- `ItemsCollected`: number of items collected for the task (set even when the value is `0`).
- `RetryCount`: current retry count.

Reporting:
- `Logs`: log path or identifier.
- `Extra`: JSON blob for additional metadata.
  - Only update `Extra` when status is `success` and the JSON contains a non-empty `cdn_url` value.
  - For JSONL ingestion with `CDNURL`, `Extra` is updated regardless of status.

## JSONL ingestion (field passthrough)

When ingesting JSONL rows, each line is treated as a task update payload:

- Resolve `record_id` by `BizTaskID` first (if present), otherwise by `TaskID`.
- Any key that matches a task table column name is sent as a raw field update.
- `CDNURL`/`cdn_url` is mapped to `Extra` as `{"cdn_url": "<value>"}` when non-empty.
- CLI flags such as `--status` or `--date` act as defaults and override missing fields in each JSONL row.

Use `--input <file>`; the script auto-detects JSONL by `.jsonl` suffix or content.

## Skip tasks by status

Use `--skip-status success,done` to skip updates when the current task status matches one of the values.

## Suggested payload format

Input update object:

```json
{
  "task_id": 180413,
  "biz_task_id": "biz3458",
  "record_id": "recv9uh3a5va06",
  "status": "running",
  "device_serial": "1fa20bb",
  "dispatched_at": "now",
  "completed_at": 1769502582240,
  "items_collected": 0,
  "logs": "s3://bucket/path/logs.txt",
  "retry_count": 1,
  "extra": "{\"cdn_url\":\"https://...\"}"
}
```

Notes:
- `dispatched_at`, `start_at`, `completed_at`, `end_at` accept epoch seconds/ms or ISO timestamps.
- `record_id` is preferred for updates; `task_id` or `biz_task_id` is used only to resolve `record_id`.
- `fields` can be supplied to send raw column updates by column name.
