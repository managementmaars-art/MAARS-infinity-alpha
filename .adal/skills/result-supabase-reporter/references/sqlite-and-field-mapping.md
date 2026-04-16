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

## Column Mapping: SQLite -> Supabase

| SQLite (PascalCase) | Supabase (snake_case) | Type |
|---|---|---|
| Datetime | datetime | bigint (unix ms) |
| DeviceSerial | device_serial | text |
| App | app | text |
| Scene | scene | text |
| Params | params | text |
| ItemID | item_id | text |
| ItemCaption | item_caption | text |
| ItemCDNURL | item_cdn_url | text |
| ItemURL | item_url | text |
| ItemDuration | item_duration | numeric |
| UserName | user_name | text |
| UserID | user_id | text |
| UserAlias | user_alias | text |
| UserAuthEntity | user_auth_entity | text |
| Tags | tags | text |
| TaskID | task_id | bigint |
| BookID | book_id | text |
| Extra | extra | text |
| LikeCount | like_count | integer |
| ViewCount | view_count | integer |
| AnchorPoint | anchor_point | text |
| CommentCount | comment_count | integer |
| CollectCount | collect_count | integer |
| ForwardCount | forward_count | integer |
| ShareCount | share_count | integer |
| PayMode | pay_mode | text |
| Collection | collection | text |
| Episode | episode | text |
| PublishTime | publish_time | text |

## Stable Upsert Key

Use a stable `item_id` value to support `onConflict: "task_id,item_id"`:
- Prefer `ItemID` when present.
- Fallback to `ItemURL` when `ItemID` is empty/null.
- Mark row as failed when both are empty.

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
export SUPABASE_URL=https://xxx.supabase.co
export SUPABASE_SERVICE_ROLE_KEY=eyJ...
npx tsx scripts/result_reporter.ts report --task-id 20260206001 --batch-size 100
```

Reset failures then rerun report:

```bash
npx tsx scripts/result_reporter.ts retry-reset
npx tsx scripts/result_reporter.ts report --task-id 20260206001
```
