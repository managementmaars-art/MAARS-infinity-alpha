# Telegram Reminders Skill

Send immediate messages and schedule reminders to Telegram with cloud-based scheduling powered by Convex.

## Quick Start

### 1. Install dependencies

```bash
npm install
```

### 2. Get credentials

You will need three things:

**a) Telegram bot token**:

- Message @BotFather on Telegram
- Send `/newbot` and follow prompts
- Copy the token (format: `123456789:ABC...`)

**b) Your Telegram user ID**:

- Message @userinfobot on Telegram
- Copy your user ID (numeric)

**c) Convex deploy key**:

- Sign up at https://dashboard.convex.dev (free)
- Create a new project
- Go to Settings > Deploy Keys
- Create a "Production" deploy key
- Copy the full key (format: `prod:deployment-name|key...`)

### 3. Run setup

```bash
npm run setup <bot_token> <user_id> <convex_deploy_key>
```

Important: start a chat with your bot on Telegram first. Search for it and press "Start".

### 4. Use the system

```bash
# Send immediate message
npm run send "Hello from Telegram Reminders!"

# Schedule a reminder
npm run schedule "tomorrow 10am" "Meeting" "Team standup at 10"

# List scheduled messages
npm run list

# Cancel a reminder
npm run cancel <message_id>

# View history
npm run history
```

## Known Limitations

In the Claude sandbox, the environment typically sets `HTTP_PROXY`/`HTTPS_PROXY`. Node.js 22 `fetch` does not accept a proxy/agent directly, so we use `undici` and `ProxyAgent` to set a global dispatcher. If you see networking issues, confirm the proxy environment variables are set and the scripts are using the shared proxy setup.

## Documentation

- `SKILL.md` - Complete documentation with setup, usage, and troubleshooting
- `references/convex.md` - Convex platform details
- `references/telegram_api.md` - Telegram Bot API reference

## Architecture

- Convex Cloud: runs 24/7 with database, functions, and cron jobs
- Cron job: checks for messages every minute
- Telegram Bot API: delivers messages to your Telegram
- Client scripts: schedule and manage messages (when network permits)

## Free Tier

Convex offers unlimited:

- Database storage
- Function executions
- Bandwidth
- No credit card required

## Security

- Bot token stored as a Convex environment variable
- All communication over HTTPS
- Enterprise-grade Convex security
- Never share your bot token or deploy key

## File Structure

```
telegram-reminders/
  convex/                    # Backend (runs in Convex Cloud)
    schema.ts                # Database schema
    messages.ts              # Queries and mutations
    telegram.ts              # Telegram API actions
    crons.ts                 # Cron job
  scripts/                   # Client scripts
    setup.ts                 # Initial setup
    send_message.ts          # Send immediately
    schedule_message.ts      # Schedule messages
    list_scheduled.ts        # List scheduled messages
    cancel_message.ts        # Cancel scheduled message
    view_history.ts          # View message history
    logger.ts                # Shared CLI logger
    proxy-util.ts            # Shared proxy setup
  references/                # Documentation
  SKILL.md                   # Full documentation
  package.json               # Dependencies
  package-lock.json          # Dependency lockfile
```

## Troubleshooting

See `references/error_handling.md` for:

- "fetch failed" errors
- Deployment issues
- Messages not sending
- Cron job problems
- Environment variable issues

## License

This skill is provided as-is for use with Claude Skills.

---

**Version**: 1  
**Last Updated**: January 2026  
**Status**: Production ready
