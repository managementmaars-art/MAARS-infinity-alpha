# Upgrade Procedures

Detailed upgrade steps for each component of the TTS + Telegram bot stack.

---

## Kokoro TTS Engine

The primary upgrade path. Updates Python dependencies, re-downloads the model, and writes a new `version.json`.

### Upgrade Steps

```bash
# 1. Record current state
cat ~/.local/share/kokoro/version.json

# 2. Run health check (baseline)
~/.claude/eon/cc-skills/plugins/tts-tg-sync/scripts/kokoro-install.sh --health

# 3. Execute upgrade
~/.claude/eon/cc-skills/plugins/tts-tg-sync/scripts/kokoro-install.sh --upgrade

# 4. Verify
~/.claude/eon/cc-skills/plugins/tts-tg-sync/scripts/kokoro-install.sh --health
cat ~/.local/share/kokoro/version.json
```

### What Gets Updated

- Python packages: `mlx-audio`, `soundfile`, `numpy`
- Model weights: re-downloaded from `mlx-community/Kokoro-82M-bf16` (uses HuggingFace cache)
- `kokoro_common.py` and `tts_generate.py`: re-copied from plugin bundle to `~/.local/share/kokoro/`
- `version.json`: rewritten with new versions and timestamp

### Rollback

```bash
# If upgrade breaks TTS, do a clean reinstall:
~/.claude/eon/cc-skills/plugins/tts-tg-sync/scripts/kokoro-install.sh --uninstall
~/.claude/eon/cc-skills/plugins/tts-tg-sync/scripts/kokoro-install.sh --install
```

The model cache at `~/.cache/huggingface/hub/models--mlx-community--Kokoro-82M-bf16` is preserved across uninstall, so reinstall reuses the cached model.

---

## Bot Dependencies (Bun Packages)

Updates the Telegram bot's npm dependencies.

### Upgrade Steps

```bash
# 1. Record current state
cd ~/.claude/automation/claude-telegram-sync
cat package.json | grep -A 20 '"dependencies"'

# 2. Update packages
bun update

# 3. Verify lock file updated
git diff bun.lock

# 4. Restart bot
pkill -f 'bun.*src/main.ts' || true
bun --watch run src/main.ts
```

### Rollback

```bash
# Restore previous lock file
cd ~/.claude/automation/claude-telegram-sync
git checkout bun.lock
bun install
```

---

## tts_generate.py Script

Updates the TTS generation script from the plugin bundle without touching the venv.

### Upgrade Steps

```bash
# 1. Compare current vs bundle
diff ~/.local/share/kokoro/tts_generate.py \
     ~/eon/cc-skills/plugins/tts-tg-sync/scripts/tts_generate.py

# 2. Copy from bundle
cp ~/eon/cc-skills/plugins/tts-tg-sync/scripts/tts_generate.py \
   ~/.local/share/kokoro/tts_generate.py

# 3. Verify
~/.local/share/kokoro/.venv/bin/python ~/.local/share/kokoro/tts_generate.py \
  --text "Script update test" --voice af_heart --lang en-us --speed 1.0 \
  --output /tmp/kokoro-tts-test.wav && echo "OK" || echo "FAIL"
```

### Rollback

The previous version is not automatically backed up. If the new script fails, use `kokoro-install.sh --upgrade` to re-copy from the bundle, or check git history in the cc-skills repo.

---

## Bun Runtime

Updates the Bun version managed by mise.

### Upgrade Steps

```bash
# 1. Check current version
bun --version

# 2. Update via mise
cd ~/.claude/automation/claude-telegram-sync
mise use bun@latest

# 3. Verify
bun --version

# 4. Reinstall deps with new Bun
bun install

# 5. Restart bot
pkill -f 'bun.*src/main.ts' || true
bun --watch run src/main.ts
```

### Rollback

```bash
# Pin back to previous version (e.g., 1.3)
cd ~/.claude/automation/claude-telegram-sync
mise use bun@1.3
bun install
```

---

## Version Tracking

After any upgrade, `version.json` at `~/.local/share/kokoro/` should reflect current state:

```json
{
  "mlx_audio": "0.3.x",
  "backend": "mlx",
  "python": "3.13",
  "model": "mlx-community/Kokoro-82M-bf16",
  "upgraded_at": "2026-02-28T00:00:00Z",
  "source": "kokoro-install.sh --upgrade",
  "venv_path": "~/.local/share/kokoro/.venv"
}
```

For bot dependencies, the source of truth is `~/.claude/automation/claude-telegram-sync/package.json` and `bun.lock`.
