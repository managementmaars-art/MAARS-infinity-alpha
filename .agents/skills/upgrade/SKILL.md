---
name: upgrade
description: "Upgrade Kokoro TTS engine dependencies and model. TRIGGERS - upgrade kokoro, update tts, kokoro update, update mlx-audio."
allowed-tools: Read, Bash, Glob, AskUserQuestion
---

# Upgrade Kokoro TTS

Upgrade MLX-Audio dependencies, re-download the model, and update bundled scripts.

> **Self-Evolving Skill**: This skill improves through use. If instructions are wrong, parameters drifted, or a workaround was needed — fix this file immediately, don't defer. Only update for real, reproducible issues.

## Workflow

### Step 1: Pre-upgrade health check

```bash
PLUGIN_DIR="${CLAUDE_PLUGIN_ROOT:-$HOME/.claude/plugins/marketplaces/cc-skills/plugins/kokoro-tts}"
bash "$PLUGIN_DIR/scripts/kokoro-install.sh" --health
cat ~/.local/share/kokoro/version.json
```

### Step 2: Execute upgrade

```bash
PLUGIN_DIR="${CLAUDE_PLUGIN_ROOT:-$HOME/.claude/plugins/marketplaces/cc-skills/plugins/kokoro-tts}"
bash "$PLUGIN_DIR/scripts/kokoro-install.sh" --upgrade
```

This upgrades:

- Python packages: `mlx-audio`, `soundfile`, `numpy`
- Model weights: re-downloaded from `mlx-community/Kokoro-82M-bf16`
- Bundled scripts: `kokoro_common.py` and `tts_generate.py` re-copied from plugin
- `version.json`: rewritten with new versions

### Step 3: Post-upgrade verification

```bash
PLUGIN_DIR="${CLAUDE_PLUGIN_ROOT:-$HOME/.claude/plugins/marketplaces/cc-skills/plugins/kokoro-tts}"
bash "$PLUGIN_DIR/scripts/kokoro-install.sh" --health
cat ~/.local/share/kokoro/version.json

# Test synthesis
~/.local/share/kokoro/.venv/bin/python ~/.local/share/kokoro/tts_generate.py \
  --text "Upgrade verification" --voice af_heart --lang en-us --speed 1.0 \
  --output /tmp/kokoro-upgrade-test.wav && echo "OK"
```

## Rollback

If upgrade breaks TTS, do a clean reinstall:

```bash
PLUGIN_DIR="${CLAUDE_PLUGIN_ROOT:-$HOME/.claude/plugins/marketplaces/cc-skills/plugins/kokoro-tts}"
bash "$PLUGIN_DIR/scripts/kokoro-install.sh" --uninstall
bash "$PLUGIN_DIR/scripts/kokoro-install.sh" --install
```

Model cache is preserved across uninstall, so reinstall reuses the cached model.

## Troubleshooting

| Issue               | Cause                     | Solution                                        |
| ------------------- | ------------------------- | ----------------------------------------------- |
| Upgrade fails       | No internet or PyPI down  | Check connectivity, retry                       |
| Import error after  | mlx-audio incompatibility | Clean reinstall: `--uninstall` then `--install` |
| Model download slow | Large download            | Wait for HuggingFace download to complete       |


## Post-Execution Reflection

After this skill completes, reflect before closing the task:

0. **Locate yourself.** — Find this SKILL.md's canonical path before editing.
1. **What failed?** — Fix the instruction that caused it.
2. **What worked better than expected?** — Promote to recommended practice.
3. **What drifted?** — Fix any script, reference, or dependency that no longer matches reality.
4. **Log it.** — Evolution-log entry with trigger, fix, and evidence.

Do NOT defer. The next invocation inherits whatever you leave behind.
