---
name: component-version-upgrade
description: Upgrade Kokoro model, bot dependencies, or TTS components. TRIGGERS - upgrade kokoro, update model, upgrade bot, update dependencies, version bump, component update.
allowed-tools: Read, Write, Edit, Bash, Glob, AskUserQuestion
disable-model-invocation: false
---

# Component Version Upgrade

Upgrade individual components of the TTS + Telegram bot stack without rebuilding the entire system.

> **Platform**: macOS (Apple Silicon)

---

> **Self-Evolving Skill**: This skill improves through use. If instructions are wrong, parameters drifted, or a workaround was needed — fix this file immediately, don't defer. Only update for real, reproducible issues.

## When to Use This Skill

- User wants to upgrade Kokoro TTS engine, Python dependencies, or the model
- User wants to update bot dependencies (Bun packages)
- User wants to refresh `tts_generate.py` from the plugin bundle
- User wants to bump the Bun runtime version

---

## Requirements

- `uv` installed (`brew install uv`)
- `mise` installed and configured
- Internet connectivity for package downloads
- Existing installation (run `full-stack-bootstrap` first if not installed)

---

## Upgradeable Components

| Component         | Command                                                      | What It Does                                                   |
| ----------------- | ------------------------------------------------------------ | -------------------------------------------------------------- |
| Kokoro TTS engine | `kokoro-install.sh --upgrade`                                | Upgrades Python deps, re-downloads model, updates version.json |
| Bot dependencies  | `cd ~/.claude/automation/claude-telegram-sync && bun update` | Updates Bun packages per package.json                          |
| tts_generate.py   | Re-copy from plugin `scripts/` to `~/.local/share/kokoro/`   | Updates the TTS generation script                              |
| Bun runtime       | `mise use bun@latest`                                        | Updates the Bun version in mise.toml                           |

---

## Workflow Phases

### Phase 1: Component Selection

Ask the user which component to upgrade using AskUserQuestion. Present the four options above.

### Phase 2: Pre-Upgrade Health Check

```bash
# Run health check to establish baseline
~/.local/share/kokoro/../../eon/cc-skills/plugins/tts-tg-sync/scripts/kokoro-install.sh --health

# Record current versions
cat ~/.local/share/kokoro/version.json
```

### Phase 3: Execute Upgrade

Run the appropriate upgrade command for the selected component.

### Phase 4: Post-Upgrade Verification

```bash
# Health check again
kokoro-install.sh --health

# Generate test audio to verify TTS still works
~/.local/share/kokoro/.venv/bin/python ~/.local/share/kokoro/tts_generate.py \
  --text "Upgrade verification test" --voice af_heart --lang en-us --speed 1.0 \
  --output /tmp/kokoro-tts-upgrade-test.wav
```

### Phase 5: Bot Restart (if needed)

If bot dependencies or Bun runtime were upgraded, restart the bot:

```bash
pkill -f 'bun.*src/main.ts' || true
cd ~/.claude/automation/claude-telegram-sync && bun --watch run src/main.ts
```

---

## TodoWrite Task Templates

```
1. [Identify] Present upgradeable components via AskUserQuestion
2. [Preflight] Run health check on target component
3. [Backup] Note current versions (version.json, package.json)
4. [Upgrade] Execute upgrade command
5. [Verify] Run post-upgrade health check
6. [Test] Generate test audio to verify TTS still works
7. [Restart] Restart bot if needed
8. [Report] Show before/after versions
```

---

## Post-Change Checklist

- [ ] Health check passes (all 6 checks OK)
- [ ] version.json updated with new versions
- [ ] Test audio generates and plays correctly
- [ ] Bot is running if it was restarted


## Troubleshooting

| Problem                       | Likely Cause                         | Fix                                                              |
| ----------------------------- | ------------------------------------ | ---------------------------------------------------------------- |
| Upgrade fails                 | No internet or PyPI issue            | Check connectivity, retry                                        |
| Model download slow           | First-time ~400MB, subsequent cached | Wait for download to complete                                    |
| Version mismatch              | Stale version.json                   | Re-run `kokoro-install.sh --health` to check, `--upgrade` to fix |
| MLX-Audio import fails        | mlx-audio version incompatibility    | `kokoro-install.sh --upgrade` reinstalls mlx-audio               |
| Bot won't start after upgrade | Dependency conflict                  | `cd ~/.claude/automation/claude-telegram-sync && bun install`    |

---

## Reference Documentation

- [Upgrade Procedures](./references/upgrade-procedures.md) -- Step-by-step upgrade instructions with rollback for each component
- [Evolution Log](./references/evolution-log.md) -- Change history for this skill

## Post-Execution Reflection

After this skill completes, reflect before closing the task:

0. **Locate yourself.** — Find this SKILL.md's canonical path (Glob for this skill's name) before editing. All corrections target THIS file and its sibling references/ — never other documentation.
1. **What failed?** — Fix the instruction that caused it. If it could recur, add it as an anti-pattern.
2. **What worked better than expected?** — Promote it to recommended practice. Document why.
3. **What drifted?** — Any script, reference, or external dependency that no longer matches reality gets fixed now.
4. **Log it.** — Every change gets an evolution-log entry with trigger, fix, and evidence.

Do NOT defer. The next invocation inherits whatever you leave behind.

---
---
