# Task Create Notes

Use these behaviors when creating new tasks in the task table.

## Create targets

- Create tasks by inserting new records in the task table.
- Use single create for 1 record, batch create for multiple records (up to 500 per request).

## Create fields

Use `TASK_FIELD_*` env vars to override column names when the task table schema differs.

Core identifiers:
- `TaskID` is auto-incremented and must not be set on create.
- `BizTaskID`, `ParentTaskID`

Task attributes:
- `App`, `Scene`, `Params`, `ItemID`, `BookID`, `URL`
- `UserID`, `UserName`, `GroupID` (auto-filled as `App_BookID_UserID` when `App`/`BookID`/`UserID` are present, with `com.smile.gifmaker` mapped to `快手`)
- `Status`, `Date`, `Logs`, `LastScreenShot`
- `DeviceSerial`, `DispatchedDevice`, `DispatchedAt`, `StartAt`, `EndAt`
- `ElapsedSeconds`, `ItemsCollected`, `RetryCount`, `Extra`

Date and timestamps:
- `Date` accepts epoch seconds/ms, ISO timestamp, or `YYYY-MM-DD`.
- `DispatchedAt`, `StartAt`, `EndAt` accept epoch seconds/ms or ISO; `StartAt` defaults to `DispatchedAt` if only dispatch time is provided.

## JSON/JSONL ingestion

When ingesting JSON/JSONL rows, each item is treated as a task payload:

- Any key that matches a task table column name is sent as a raw field update.
- Use `fields` to send raw column updates when the key is not in the standard field mapping.
- `CDNURL`/`cdn_url` is mapped to `Extra` as `{\"cdn_url\": \"<value>\"}` when non-empty.
- CLI flags such as `--status` or `--date` act as defaults and override missing fields in each item.

Use `--input <file>`; the script auto-detects JSONL by `.jsonl` suffix or content.

## Skip existing

Use `--skip-existing <fields>` to skip creation when existing records match.

- Single field: `--skip-existing BizTaskID`
- Multiple fields (all must match): `--skip-existing BookID,UserID`

Supported field names (case-insensitive): `TaskID`, `BizTaskID`, `RecordID`, `BookID`, `UserID`, `App`, `Scene`.

## Suggested payload format

Input create object:

```json
{
  "biz_task_id": "biz3458",
  "app": "com.smile.gifmaker",
  "scene": "综合页搜索",
  "status": "pending",
  "date": "2026-01-27",
  "params": "关键字",
  "user_id": "123",
  "url": "https://example.com/item/1",
  "extra": "{\"cdn_url\":\"https://...\"}"
}
```
