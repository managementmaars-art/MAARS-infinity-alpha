# Task Claim Notes

Use `claim` to safely grab a single task across multiple machines by updating the task status and binding a device, then verifying the change.

## Claim flow

1) Fetch candidates by `App + Scene + Status + Date`.
   - `Scene` supports comma-separated priority list, e.g. `个人页搜索,综合页搜索`.
   - It attempts earlier scenes first, then falls back to later scenes when no tasks are found.
2) For each candidate, set:
   - `Status = running`
   - `DispatchedDevice = <device_serial>`
   - `DispatchedAt = now`
   - `StartAt = now`
3) Verify with `record_id`:
   - `GET /records/{record_id}`
   - If it fails, wait 1s and fall back to `search` by `TaskID`
4) Validate:
   - `Status == running`
   - `DispatchedDevice == <device_serial>`
5) Only proceed if verification succeeds; otherwise try the next candidate.

## Stale running tasks

Before claiming, optionally scan `Status=running` tasks:
- If `StartAt` or `DispatchedAt` is older than `stale-minutes`, mark as `failed` (default).
- `stale-action` supports `failed`, `pending`, `log`, or `skip`.

## CLI usage

```bash
npx tsx scripts/bitable_task.ts claim \
  --app com.tencent.mm \
  --scene 综合页搜索 \
  --device-serial <serial> \
  --status pending,failed \
  --date Today \
  --candidate-limit 5 \
  --log-level debug
```

Notes:
- `claim` always returns at most one task; `--limit` is not a valid flag for this subcommand.
- `--candidate-limit` controls how many candidate rows are attempted in this run, not how many tasks are returned (default is `5`).
- Do not infer `--candidate-limit 1` from "claim one task"; these are independent semantics.
