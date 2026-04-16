# SQLite Schema and Column Mapping

## Defaults

- DB path default: `$HOME/.eval/records.sqlite`
- Table default: `capture_results`
- Override via environment:
  - `TRACKING_STORAGE_DB_PATH`
  - `RESULT_SQLITE_TABLE`

## Expected SQLite Columns

Business columns:
`Datetime`, `DeviceSerial`, `App`, `Scene`, `Params`, `ItemID`, `ItemCaption`, `ItemCDNURL`, `ItemURL`, `ItemDuration`, `UserName`, `UserID`, `UserAlias`, `UserAuthEntity`, `Tags`, `TaskID`, `BookID`, `Extra`, `LikeCount`, `ViewCount`, `AnchorPoint`, `CommentCount`, `CollectCount`, `ForwardCount`, `ShareCount`, `PayMode`, `Collection`, `Episode`, `PublishTime`.

Reporter bookkeeping columns: `reported`, `reported_at`, `report_error`.

## Column Mapping: SQLite -> Feishu Fields

By default, each sqlite column maps to the same Feishu field name.

Default field names can be overridden by env vars:

- `RESULT_FIELD_DATETIME` (default `Datetime`)
- `RESULT_FIELD_DEVICE_SERIAL` (default `DeviceSerial`)
- `RESULT_FIELD_APP` (default `App`)
- `RESULT_FIELD_SCENE` (default `Scene`)
- `RESULT_FIELD_PARAMS` (default `Params`)
- `RESULT_FIELD_ITEMID` (default `ItemID`)
- `RESULT_FIELD_ITEMCAPTION` (default `ItemCaption`)
- `RESULT_FIELD_ITEMCDNURL` (default `ItemCDNURL`)
- `RESULT_FIELD_ITEMURL` (default `ItemURL`)
- `RESULT_FIELD_DURATION` (default `ItemDuration`)
- `RESULT_FIELD_USERNAME` (default `UserName`)
- `RESULT_FIELD_USERID` (default `UserID`)
- `RESULT_FIELD_USERALIAS` (default `UserAlias`)
- `RESULT_FIELD_USERAUTHENTITY` (default `UserAuthEntity`)
- `RESULT_FIELD_TAGS` (default `Tags`)
- `RESULT_FIELD_TASKID` (default `TaskID`)
- `RESULT_FIELD_BOOKID` (default `BookID`)
- `RESULT_FIELD_EXTRA` (default `Extra`)
- `RESULT_FIELD_LIKECOUNT` (default `LikeCount`)
- `RESULT_FIELD_VIEWCOUNT` (default `ViewCount`)
- `RESULT_FIELD_ANCHORPOINT` (default `AnchorPoint`)
- `RESULT_FIELD_COMMENTCOUNT` (default `CommentCount`)
- `RESULT_FIELD_COLLECTCOUNT` (default `CollectCount`)
- `RESULT_FIELD_FORWARDCOUNT` (default `ForwardCount`)
- `RESULT_FIELD_SHARECOUNT` (default `ShareCount`)
- `RESULT_FIELD_PAYMODE` (default `PayMode`)
- `RESULT_FIELD_COLLECTION` (default `Collection`)
- `RESULT_FIELD_EPISODE` (default `Episode`)
- `RESULT_FIELD_PUBLISHTIME` (default `PublishTime`)

## Status Semantics

- `reported = 0`: pending (never reported or manually reset)
- `reported = -1`: previous report failed
- `reported = 1`: successfully reported

Writeback columns:
- `reported_at`: unix milliseconds of latest attempt
- `report_error`: truncated error string (<= 512 chars), or `NULL` on success

## Selection Rules

Default selection:
- `reported IN (0,-1)`
- Order by `id ASC`
- `filter`: cap with `--limit` (default 30)
- `report`: paginate by `id` and optional `--max-rows`

Optional filters: `--task-id`, `--app`, `--scene`, `--params-like`, `--item-id`, `--date-from`, `--date-to`, `--where`, `--where-arg`.

Use `--task-id <TASK_ID>` for task-scoped workflows (`TASK_ID` must be digits).

## Commands

Print count for one task:

```bash
npx tsx scripts/result_reporter.ts stat --task-id 20260206001
```

Preview pending/failed rows:

```bash
npx tsx scripts/result_reporter.ts filter --task-id 20260206001 --status 0,-1 --limit 10
```

Run report:

```bash
export FEISHU_APP_ID=...
export FEISHU_APP_SECRET=...
export RESULT_BITABLE_URL='https://.../wiki/...?...table=tbl_xxx&view=vew_xxx'
npx tsx scripts/result_reporter.ts report --task-id 20260206001 --batch-size 100
```

Reset failures then rerun report:

```bash
npx tsx scripts/result_reporter.ts retry-reset
npx tsx scripts/result_reporter.ts report --task-id 20260206001
```
