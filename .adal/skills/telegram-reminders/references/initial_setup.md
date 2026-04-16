# Telegram Reminders Setup Guide

This guide will help you set up the Telegram Reminders skill, especially in sandboxed environments like Claude's computer.

## Quick Setup (3 Steps)

### Step 1: Get Your Credentials

1. **Bot Token**:

   - Open Telegram and message [@BotFather](https://t.me/BotFather)
   - Send `/newbot` and follow the prompts
   - Copy the bot token (format: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)

2. **User ID**:

   - Message [@userinfobot](https://t.me/userinfobot) on Telegram
   - Copy your numeric ID (format: `123456789`)

3. **Convex Deploy Key**:
   - Go to [dashboard.convex.dev](https://dashboard.convex.dev)
   - Create a new project (or use existing)
   - Go to Settings → Deploy Keys
   - Create a "Production" deploy key
   - Copy the key (format: `prod:name-123|abc123def...`)

### Step 2: Run Setup

```bash
cd /mnt/skills/user/telegram-reminders
npm install
tsx scripts/setup.ts <bot_token> <user_id> <deploy_key>
```

The setup will:

- Save your credentials
- Deploy to Convex Cloud
- Configure environment variables
- Attempt to send a test message

**Note**: Scripts use `undici` with automatic proxy detection for network requests, ensuring compatibility with sandboxed environments.

### Step 3: Start Chat with Your Bot

**CRITICAL**: You must do this before the bot can send you messages!

1. Open Telegram
2. Search for your bot (by the name you gave it in BotFather)
3. Click on it and press "Start"

## Using the Skill

Use the tsx scripts for all operations:

```bash
# Send a message
tsx scripts/send_message.ts "Hello!"

# Send with file attachment
tsx scripts/send_message.ts "Check this file" /path/to/file.pdf

# Schedule a reminder
tsx scripts/schedule_message.ts "Meeting" "Team standup" "tomorrow 10am"

# List pending messages
tsx scripts/list_scheduled.ts

# Cancel a message
tsx scripts/cancel_message.ts <message_id>

# View history
tsx scripts/view_history.ts 50
```

## Common Issues

### "EAI_AGAIN" DNS Error

**Cause**: DNS resolution failure in sandboxed environments.

**Solution**: Scripts now use `undici` with automatic proxy detection from `HTTP_PROXY`/`HTTPS_PROXY` environment variables. This should work automatically.

### "Unauthorized" or "bot was blocked"

**Cause**: You haven't started a chat with your bot.

**Solution**:

1. Open Telegram
2. Search for your bot
3. Press "Start"

### Messages Not Sending

**Cause**: Environment variables not set in Convex.

**Solution**:

```bash
npx convex env set TELEGRAM_BOT_TOKEN "your_token"
npx convex env set TELEGRAM_USER_ID "your_id"
```

### Setup Script Fails at Verification

**Cause**: Network issues during setup.

**Solution**: Verify manually by sending a test message:

```bash
tsx scripts/send_message.ts "Test message"
```

## Manual Setup (If Script Fails)

If the setup script doesn't work, you can set up manually:

```bash
# 1. Install dependencies
npm install

# 2. Create config file
cat > /mnt/user-data/outputs/telegram_config.json << EOF
{
  "botToken": "YOUR_BOT_TOKEN",
  "userId": "YOUR_USER_ID",
  "deployKey": "YOUR_DEPLOY_KEY",
  "setupDate": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
}
EOF

# 3. Create .env.local
echo "CONVEX_DEPLOY_KEY=YOUR_DEPLOY_KEY" > .env.local

# 4. Deploy to Convex
npx convex deploy

# 5. Set environment variables
npx convex env set TELEGRAM_BOT_TOKEN "YOUR_BOT_TOKEN"
npx convex env set TELEGRAM_USER_ID "YOUR_USER_ID"

# 6. Test
tsx scripts/send_message.ts "Setup test!"
```

## Verification

To verify everything is working:

```bash
# Check Convex deployment
npx convex env list

# Send test message
tsx scripts/send_message.ts "Test!"

# Check for message in Telegram
```

## Need Help?

- Check the main [SKILL.md](SKILL.md) for detailed documentation
- Monitor your deployment at [dashboard.convex.dev](https://dashboard.convex.dev)
- Review Convex logs: `npx convex logs --watch`
