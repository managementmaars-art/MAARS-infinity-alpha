---
name: tick-collection-ops
description: "Operate and troubleshoot the MT5 tick collection system on Linux/Wine. Systemd topology, gap detection, restart recovery, daily rotation. TRIGGERS - tick collection, MT5 Wine, tick gaps, EA restart, systemd MT5, tick writer DLL."
allowed-tools: Read, Bash, Grep, Glob
---

# MT5 Tick Collection Operations

Operate, monitor, and troubleshoot the zero-gap tick collection system running on Linux via Wine.

> **Self-Evolving Skill**: This skill improves through use. If instructions are wrong, parameters drifted, or a workaround was needed — fix this file immediately, don't defer. Only update for real, reproducible issues.

## When to Use This Skill

Use this skill when:

- Deploying or restarting tick collection on bigblack
- Diagnosing tick gaps or missing data
- Troubleshooting Wine or MT5 issues
- Understanding systemd service topology
- Investigating crash recovery files
- Checking tick collection health

## System Architecture

```
TickCollector EA (MQL5)  -->  tick_writer.dll (Rust)  -->  Parquet files
     OnTick() callback         C-ABI FFI                   ZSTD compressed
     CopyTicksRange()          Buffered writes              One file per day
     Watermark dedup            Row group flush
```

- TickCollector EA runs on MT5 via Wine on headless Linux (bigblack)
- EA captures every tick via OnTick() callback + OnTimer() fallback (1-second interval)
- Ticks buffered in EA, flushed to Rust DLL (tick_writer.dll) via C-ABI FFI
- Rust DLL writes Parquet files with ZSTD level 3 compression
- **One EA instance per symbol per chart** -- this is a CRITICAL constraint (single symbol per EA)

## Production Topology

| Resource      | Path                                        |
| ------------- | ------------------------------------------- |
| Git repo      | ~/eon/mql5/                                 |
| Wine prefix   | ~/.mt5/                                     |
| MT5 install   | ~/.mt5/drive_c/Program Files/MetaTrader 5/  |
| EA source     | {repo}/mql5_ea/TickCollector.mq5            |
| DLL (Windows) | {mt5}/MQL5/Libraries/tick_writer.dll        |
| Tick data     | {mt5}/tick_data/ (symlinked to ODB cache)   |
| Systemd units | systemd user units: xvfb, xfce, x11vnc, mt5 |

## Systemd Service Chain

```
xvfb (virtual framebuffer)
  --> xfce (desktop environment)
    --> x11vnc (VNC access)
      --> mt5 (MetaTrader 5 via Wine)
```

All are user-level systemd units. MT5 depends on the display stack. The chain must start in order -- xvfb first, mt5 last.

## Daily File Rotation

- New Parquet file created each trading day
- Filename pattern: `{SYMBOL}_{YYYYMMDD}.parquet`
- EA detects day change and calls `tw_close` (finalize current file) + `tw_init` (open new file)
- Trading day runs Sunday open to Monday open (forex hours)

## Crash Recovery

On EA restart:

1. EA calls `tw_get_last_time_msc` to read resume watermark from the last Parquet file footer
2. Watermark is the timestamp of the last tick written -- resume from there
3. If an existing file is found for today, new file gets `_1`, `_2` suffix (not overwrite)
4. All recovery segments are valid, complete Parquet files with footers
5. Resume watermark prevents duplicate ticks after restart
6. Gap between shutdown and restart is backfilled via `CopyTicksRange` from the watermark

The Rust DLL renames corrupt/incomplete files to `_partial` suffix rather than attempting recovery.

## Gap Detection

Use DuckDB to check for gaps between consecutive ticks:

```sql
WITH ticks AS (
    SELECT time_msc,
           lead(time_msc) OVER (ORDER BY time_msc) - time_msc AS gap_ms
    FROM read_parquet('{base_path}/FXVIEW_{SYMBOL}/{YYYY}/{SYMBOL}_{YYYYMMDD}.parquet')
)
SELECT time_msc, gap_ms,
       make_timestamp(time_msc * 1000) AS ts
FROM ticks
WHERE gap_ms > 60000  -- gaps > 1 minute
ORDER BY gap_ms DESC;
```

**Interpreting results:**

- Weekend gaps are normal (Friday close to Sunday open)
- Mid-session gaps indicate collection interruption
- Gaps < 1 minute are normal during low-activity periods
- Check systemd journal for correlating restart events

## Wine Gotchas

These are CRITICAL anti-patterns -- violations cause silent crashes or data loss:

- **NEVER use `%I64u` or `%I64d` format specifiers in MQL5** -- crashes Wine silently. Use `IntegerToString()` instead.
- **Wine cannot follow symlinks** for file access -- use physical file copies for EA and DLL deployment
- **Headless Linux requires Xvfb** virtual framebuffer -- MT5 GUI needs a display even when no monitor is connected
- **compile.sh uses Wine CLI** for compilation -- no MetaEditor GUI needed
- **MetaEditor returns exit code 1** even on success under Wine -- check compile log instead
- **Compile log is UTF-16LE** -- use `iconv -f UTF-16LE -t UTF-8` to read it
- **`DISPLAY=:99`** must be set (Xvfb virtual display number)

## Deployment Pipeline

Use `/mql5:mql5-ship` slash command for full deployment:

- `--ea-only` for EA source changes
- `--dll-only` for Rust DLL changes
- Full pipeline: commit -> push -> pull on bigblack -> compile -> validate

Detailed deployment steps (SSH commands, file copies, compilation) are in the `headless-mt5-remote` local skill. Not duplicated here to avoid drift.

## Monitoring Commands

### Check MT5 service status

```bash
systemctl --user status mt5
```

### Check today's tick files

```bash
ls -la ~/.cache/opendeviationbar/ticks/FXVIEW_EURUSD/$(date +%Y)/
```

### Count ticks in latest file

```bash
duckdb -c "SELECT count(*) FROM read_parquet('path/to/file.parquet')"
```

### Check for recovery segments

```bash
ls ~/.cache/opendeviationbar/ticks/FXVIEW_EURUSD/$(date +%Y)/*_[0-9].parquet 2>/dev/null
```

### View systemd service chain

```bash
systemctl --user list-units --type=service | grep -E "xvfb|xfce|x11vnc|mt5"
```

### Check MT5 journal for errors

```bash
journalctl --user -u mt5 --since "1 hour ago" --no-pager
```

## Scope Boundary

- **This skill:** Operations, monitoring, troubleshooting
- **`headless-mt5-remote` local skill:** Deployment steps (SSH, file copy, compilation)
- **`fxview-parquet-consumer` skill:** Data consumption patterns (schema, DuckDB queries)

## Troubleshooting

| Issue                     | Cause                          | Solution                                         |
| ------------------------- | ------------------------------ | ------------------------------------------------ |
| MT5 service won't start   | Display stack not running      | Start xvfb first, then xfce, x11vnc, mt5         |
| EA not collecting ticks   | Symbol not in Market Watch     | Open chart for symbol in MT5, re-attach EA       |
| Wine crash on PrintFormat | Using %I64u/%I64d specifiers   | Replace with IntegerToString()                   |
| DLL load failure          | Missing tick_writer.dll        | Copy DLL to MQL5/Libraries/ (physical copy)      |
| Gaps in tick data         | EA restart or network issue    | Check journalctl, verify recovery segments exist |
| Recovery file \_1_2       | Normal after restart           | All segments are valid, union in DuckDB          |
| Compile log unreadable    | UTF-16LE encoding              | Use iconv -f UTF-16LE -t UTF-8                   |
| Xvfb not running          | Service crashed or not enabled | systemctl --user start xvfb                      |


## Post-Execution Reflection

After this skill completes, check before closing:

1. **Did the command succeed?** — If not, fix the instruction or error table that caused the failure.
2. **Did parameters or output change?** — If the underlying tool's interface drifted, update Usage examples and Parameters table to match.
3. **Was a workaround needed?** — If you had to improvise (different flags, extra steps), update this SKILL.md so the next invocation doesn't need the same workaround.

Only update if the issue is real and reproducible — not speculative.
