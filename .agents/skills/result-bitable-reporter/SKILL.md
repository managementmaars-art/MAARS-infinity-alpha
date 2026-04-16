---
name: result-bitable-reporter
description: "Filter rows from sqlite capture_results and report to Feishu Bitable with retry-safe sqlite writeback. Use for stat/filter/report/retry-reset workflows, especially task-scoped reporting with --task-id."
---

# Result Bitable Reporter

Use this skill to run a deterministic `sqlite -> Feishu Bitable` pipeline around `capture_results`.

## Workflow

1) Select rows
- `stat`: print total sqlite row count for one `--task-id`.
- `filter`: preview upload candidates from `capture_results`.
- Default status filter is `reported IN (0,-1)`.

2) Report rows
- `report`: batch create to Feishu Bitable and write back sqlite status.
- `--max-rows <n>` sets total cap for one report run.
- For per-task workflows, always pass `--task-id <TASK_ID>` to avoid cross-task uploads.
- Success writeback: `reported=1`, `reported_at=now_ms`, `report_error=NULL`.
- Failure writeback: `reported=-1`, `reported_at=now_ms`, `report_error=<truncated error>`.

3) Retry failures
- `retry-reset`: move failed rows (`reported=-1`) back to pending (`reported=0`), then rerun `report`.

## Run

```bash
npx tsx scripts/result_reporter.ts <subcommand> [flags]
```

Use `npx tsx scripts/result_reporter.ts --help` as the CLI source of truth.

## Environment Variables

Required for `report`:
- `FEISHU_APP_ID`
- `FEISHU_APP_SECRET`
- `RESULT_BITABLE_URL`

Optional overrides:
- `FEISHU_BASE_URL` (default `https://open.feishu.cn`)
- `TRACKING_STORAGE_DB_PATH` (default `$HOME/.eval/records.sqlite`)
- `RESULT_SQLITE_TABLE` (default `capture_results`)

## Recommended Command Patterns

Task-scoped preview:

```bash
npx tsx scripts/result_reporter.ts filter --task-id <TASK_ID> --status 0,-1 --limit 20
```

Task-scoped report:

```bash
export FEISHU_APP_ID=<app_id>
export FEISHU_APP_SECRET=<app_secret>
export RESULT_BITABLE_URL='https://.../wiki/...?...table=tbl_xxx&view=vew_xxx'
npx tsx scripts/result_reporter.ts report --task-id <TASK_ID> --batch-size 100 --max-rows 500
```

Retry failed rows:

```bash
npx tsx scripts/result_reporter.ts retry-reset --app com.tencent.mm --scene onSearch
npx tsx scripts/result_reporter.ts report --task-id <TASK_ID> --status 0,-1
```

## Failure Handling

- Use `report --dry-run` to validate selection before network writes.
- Check sqlite `report_error` for root cause when `reported=-1`.
- Fix root cause, then rerun `retry-reset` and `report`.

## Resources

- `scripts/result_reporter.ts`: CLI behavior and flags.
- `references/sqlite-and-field-mapping.md`: sqlite schema and field mapping.
- `references/feishu-api-and-errors.md`: Feishu API contract and error triage.
