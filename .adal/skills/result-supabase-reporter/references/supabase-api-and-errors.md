# Supabase API and Error Handling

## API Contract

Use `@supabase/supabase-js` with service-role credentials:

- `createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)`
- `from(<table>).upsert(records, { onConflict: "task_id,item_id" })`

Notes:
- Upsert key is `(task_id, item_id)` and must have a unique constraint in Supabase.
- `item_id` is resolved from sqlite `ItemID`; fallback is `ItemURL` when `ItemID` is empty/null.

## Required Inputs for `report`

- `SUPABASE_URL`: project URL, e.g. `https://<project>.supabase.co`
- `SUPABASE_SERVICE_ROLE_KEY`: service role key with write access

Optional:
- `SUPABASE_RESULT_TABLE` or `--supabase-table <name>`

## Batch Behavior

- Default `--batch-size 100`
- Allowed range in script: `1..1000`
- Paginate sqlite rows and upload in chunks
- Fallback to single-row upload when batch upsert fails

## Writeback Rules

On report failure, sqlite writeback marks each failed row:

- `reported = -1`
- `reported_at = now_ms`
- `report_error = <truncated error>`

On success:

- `reported = 1`
- `reported_at = now_ms`
- `report_error = NULL`

## Common Error Causes

- Invalid `SUPABASE_URL`
- Invalid/expired `SUPABASE_SERVICE_ROLE_KEY`
- Missing target table or schema mismatch
- `onConflict` columns not backed by a unique constraint

## Practical Triage Steps

1. Run `report --dry-run` to confirm selection and filters.
2. Confirm table DDL includes unique key for `(task_id, item_id)`.
3. Inspect sqlite failures:

```bash
sqlite3 ~/.eval/records.sqlite "SELECT id, TaskID, ItemID, report_error, reported_at FROM capture_results WHERE reported = -1 ORDER BY reported_at DESC LIMIT 20;"
```

4. Fix root cause.
5. Retry:

```bash
npx tsx scripts/result_reporter.ts retry-reset
npx tsx scripts/result_reporter.ts report --task-id <TASK_ID> --status 0,-1
```
