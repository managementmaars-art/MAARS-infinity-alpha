# Release Notes — v3.0.0

> **Release Date:** 2026-02-18  
> **Type:** Major Release  
> **Compatibility:** macOS 12+, Linux (beta)

---

## 🎉 Highlights

v3.0.0 introduces **Self-Optimization** — the system can now analyze its own operation logs, detect recurring failure patterns, and propose improvements to your `AGENTS.md` configuration. The AI doesn't just heal crashes; it learns to prevent them.

This release also includes a major README overhaul for clarity and honesty, plus official Telegram notification support (contributed by the community 🙏).

---

## ✨ What's New

### Self-Optimization Engine (Self-Evolving)

The system now performs a weekly self-review:

1. **Log Analysis** — Scans the past 7 days of recovery logs
2. **Pattern Detection** — Identifies recurring failure signatures (e.g., config corruption, API timeouts)
3. **Improvement Proposals** — Generates concrete suggestions for `AGENTS.md`
4. **User Approval** — All suggestions require explicit approval before any changes are applied

This feature absorbs the previously separate "self-evolving" functionality into the core system.

**How to use:**
```bash
# Manually trigger a self-optimization review
bash ~/openclaw/scripts/self-optimize.sh --dry-run

# View pending suggestions
cat ~/openclaw/memory/optimization-proposals.md
```

### Telegram Notifications (PR #5 by @AbhiWisdom)

Configure Telegram as an alternative (or additional) alert channel:

```bash
# Add to ~/.openclaw/.env
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
```

Both Discord and Telegram can be active simultaneously. If both are configured, alerts go to both channels.

---

## 📋 Full Changelog

### Added
- Self-Optimization: AGENTS.md 자동 분석 및 개선안 제안
- 주 1회 로그 분석 → 패턴 감지 → 개선안 생성
- 사용자 승인 필수 워크플로우

### Changed
- README 전면 개선: 496줄 → 250줄 이내
- 과대광고 배지 제거 (9.9/10, 99% recovery)
- mermaid → 텍스트 기반 다이어그램

### Fixed
- Telegram notification support (PR #5 by @AbhiWisdom)

---

## 🚀 Installation & Upgrade

### Fresh Install

```bash
curl -fsSL https://raw.githubusercontent.com/ramsbaby/openclaw-self-healing/main/install.sh | bash
```

### Upgrade from v2.x

```bash
cd ~/path/to/openclaw-self-healing

# Pull latest
git pull origin main

# Re-run installer (safe — won't overwrite .env)
bash install.sh --upgrade
```

The installer detects existing installations and performs a non-destructive upgrade.

---

## 🔄 Migration Guide: v2.x → v3.0

### What Changes

| Component | v2.x | v3.0 |
|-----------|------|------|
| Self-healing tiers | 4 tiers | 4 tiers (unchanged) |
| Self-optimization | Separate script | Integrated weekly cron |
| README | 496 lines | ~250 lines |
| Notification | Discord only | Discord + Telegram |
| Badges | 9.9/10, 99% rate | Removed (misleading) |

### Migration Steps

1. **Backup your `.env`:**
   ```bash
   cp ~/.openclaw/.env ~/.openclaw/.env.v2-backup
   ```

2. **Pull v3.0:**
   ```bash
   cd ~/openclaw-self-healing
   git pull origin main
   ```

3. **Run upgrade:**
   ```bash
   bash install.sh --upgrade
   ```

4. **(Optional) Add Telegram:**
   ```bash
   echo "TELEGRAM_BOT_TOKEN=xxx" >> ~/.openclaw/.env
   echo "TELEGRAM_CHAT_ID=yyy" >> ~/.openclaw/.env
   ```

5. **Verify:**
   ```bash
   # Check all LaunchAgents are loaded
   launchctl list | grep openclaw
   
   # Test health check
   curl http://localhost:18789/
   ```

### No Breaking Changes

v3.0 is **fully backward compatible** with v2.x configurations.

- All existing `.env` variables continue to work
- LaunchAgent plist files are unchanged
- Script interfaces are unchanged
- No database migrations required

---

## ⚠️ Known Issues

- Self-optimization cron requires `CLAUDE_API_KEY` to be set (same as emergency recovery)
- Linux systemd support remains in beta; some features may not work identically to macOS
- Prometheus metrics export (announced in v2.1 roadmap) is delayed to v3.1

---

## 🙏 Credits

- **[@AbhiWisdom](https://github.com/AbhiWisdom)** — Telegram notification support (PR #5)
- Everyone who reported issues, starred the repo, and gave feedback

---

## 📎 Resources

- [Full Changelog](../CHANGELOG.md)
- [Quick Start Guide](QUICKSTART.md)
- [Troubleshooting](TROUBLESHOOTING.md)
- [Contributing Guide](../CONTRIBUTING.md)
- [GitHub Discussions](https://github.com/ramsbaby/openclaw-self-healing/discussions)
