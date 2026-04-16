**Skill**: [asciinema-streaming-backup](../SKILL.md)

# Troubleshooting Guide

Common issues and fixes for the streaming backup system.

---

## "Cannot push to orphan branch"

**Cause**: Authentication or permissions issue.

**Fix**:

```bash
# Check gh auth status
gh auth status

# Re-authenticate if needed
gh auth login
```

## "Chunks not being created"

**Cause**: Idle threshold not reached, or file not growing.

**Fix**:

- Verify recording is active: `tail -f $CAST_FILE`
- Lower threshold: `IDLE_THRESHOLD=15`
- Check file permissions

## "GitHub Action not triggering"

**Cause**: Workflow file missing or wrong branch filter.

**Fix**:

```bash
# Verify workflow exists
cat ~/asciinema_recordings/REPO/.github/workflows/recompress.yml

# Check branch filter includes gh-recordings
grep -A2 "branches:" ~/asciinema_recordings/REPO/.github/workflows/recompress.yml
```

## "Brotli archive empty or corrupted"

**Cause**: zstd chunks not concatenating properly (overlapping data).

**Fix**: Ensure idle-chunker uses `last_chunk_pos` to avoid overlap:

```bash
/usr/bin/env bash << 'PREFLIGHT_EOF_2'
# Check for overlaps - each chunk should be sequential
for f in chunks/*.zst; do
  zstd -d "$f" -c | head -1
done
PREFLIGHT_EOF_2
```

## Validation Failure Quick Reference

| Failure                             | Cause                | Resolution                                                    |
| ----------------------------------- | -------------------- | ------------------------------------------------------------- |
| `asciinema MISSING`                 | Not installed        | `brew install asciinema` (macOS) or `pipx install asciinema`  |
| `zstd MISSING`                      | Not installed        | `brew install zstd` (macOS) or `apt install zstd` (Linux)     |
| `brotli MISSING`                    | Not installed        | `brew install brotli` (macOS) or `apt install brotli` (Linux) |
| `gh not authenticated`              | No GitHub login      | Run `gh auth login` and follow prompts                        |
| `gh-recordings NOT found on remote` | Branch not pushed    | Run orphan branch setup from Phase 4 of skill                 |
| `local directory NOT found`         | Clone failed         | Check repo URL and permissions, re-run clone                  |
| `recompress.yml MISSING`            | Workflow not created | Re-run orphan branch setup to create workflow                 |
| `workflow trigger failed`           | No workflow_dispatch | Add `workflow_dispatch:` trigger to workflow                  |
| `zstd concatenation FAILED`         | zstd version issue   | Update zstd: `brew upgrade zstd`                              |
| `brotli round-trip FAILED`          | brotli corrupted     | Reinstall: `brew reinstall brotli`                            |
