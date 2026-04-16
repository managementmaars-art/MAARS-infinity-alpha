# Feishu Bitable API and Error Handling

## API Contract

Use Feishu OpenAPI with tenant token:

1. `POST /open-apis/auth/v3/tenant_access_token/internal/`
2. `POST /open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/batch_create`

Optional for wiki URLs:

- `GET /open-apis/wiki/v2/spaces/get_node?token=<wiki_token>` to resolve `obj_token` as bitable app token.

## Required Inputs for `report`

- `FEISHU_APP_ID`
- `FEISHU_APP_SECRET`
- `RESULT_BITABLE_URL` (or `--bitable-url`)

Optional:

- `FEISHU_BASE_URL` (default `https://open.feishu.cn`)

## Bitable URL Requirement

`RESULT_BITABLE_URL` must contain `table=<table_id>` and one of:

- `/base/<app_token>?table=<table_id>`
- `/wiki/<wiki_token>?table=<table_id>`

The script accepts common escaped forms (`\?`, `\&`, `\=`, `&amp;`).

## Batch Behavior

- Default `--batch-size 100`
- Allowed range in script: `1..500`
- Paginate sqlite rows and upload in chunks
- Fallback to single-row create when batch create fails

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

- Invalid `FEISHU_APP_ID` or `FEISHU_APP_SECRET`
- Invalid `RESULT_BITABLE_URL` / unresolved wiki token
- Field name mismatch in bitable
- Temporary API failures or rate limits

## Practical Triage Steps

1. Run `report --dry-run` to confirm selection and filters.
2. Verify target bitable URL and field names.
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
