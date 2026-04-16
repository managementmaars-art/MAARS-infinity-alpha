---
name: slack
description: "Send messages and notifications to Slack channels. Built on top of slack-auth for authentication, supports messaging, file uploads, channel management, DM sending, and notification templates with variable substitution."
version: 1.0.0
author: OpenClaw
entry: ./dist/cli.js
type: script
---

# Slack Skill

Send messages, upload files, and manage channels in Slack workspaces. This skill provides a high-level interface for team communication built on top of the slack-auth skill.

## Features

- **Channel Messaging**: Send messages to any channel
- **Direct Messages**: DM users by ID or email
- **File Uploads**: Upload files with optional comments
- **Thread Replies**: Reply in message threads
- **Channel Management**: Create, join, and leave channels
- **User Lookup**: Find users by ID or email
- **Notification Templates**: Create reusable message templates with variables
- **Message History**: Track sent messages locally

## Installation

```bash
cd skills/slack
npm install
npm run build
```

## Prerequisites

You must have the `slack-auth` skill configured and connected:

```bash
# In slack-auth directory
node dist/cli.js connect default
```

## CLI Usage

### Check Status

```bash
node dist/cli.js status
node dist/cli.js health
```

### List Channels and Users

```bash
# List all channels
node dist/cli.js channels

# List users (exclude bots by default)
node dist/cli.js users

# Include bots
node dist/cli.js users --include-bots

# Get user info
node dist/cli.js user U123456

# Find user by email
node dist/cli.js find-user user@example.com
```

### Send Messages

```bash
# Send to channel
node dist/cli.js send "#general" "Hello everyone!"

# Send direct message
node dist/cli.js dm U123456 "Hey there!"

# Reply in thread
node dist/cli.js reply "#general" "1234567890.123456" "Thanks for the update!"
```

### Upload Files

```bash
# Upload file to channel
node dist/cli.js upload "#general" ./report.pdf "Monthly Report"

# Upload with comment
node dist/cli.js upload "#general" ./data.csv
```

### Channel Management

```bash
# Create public channel
node dist/cli.js create-channel announcements

# Create private channel
node dist/cli.js create-channel private-team --private

# Join channel
node dist/cli.js join "#general"

# Leave channel
node dist/cli.js leave "#old-channel"
```

### Notification Templates

```bash
# List templates
node dist/cli.js templates

# Show template details
node dist/cli.js template welcome

# Create template from file
echo "Welcome {{name}} to the team!" > welcome.txt
node dist/cli.js create-template welcome "#general" ./welcome.txt

# Delete template
node dist/cli.js delete-template old-template

# Send notification using template
node dist/cli.js notify welcome --var-name="Alice"

# Send to different channel
node dist/cli.js notify welcome "#new-hires" --var-name="Bob"
```

### Message History

```bash
# Show last 50 messages
node dist/cli.js history

# Show last 100 messages
node dist/cli.js history 100
```

### Profile Selection

All commands support `--profile` to use a specific workspace:

```bash
node dist/cli.js --profile work status
node dist/cli.js --profile work send "#alerts" "Production deploy started"
```

## JavaScript/TypeScript API

### Initialize

```typescript
import { SlackSkill } from '@openclaw/slack';

// Default profile
const slack = new SlackSkill();

// Specific profile
const workSlack = SlackSkill.forProfile('work');
```

### Send Messages

```typescript
// Simple message
const result = await slack.sendMessage({
  channel: '#general',
  text: 'Hello team!'
});

// With blocks (rich formatting)
const result = await slack.sendMessage({
  channel: '#general',
  text: 'System alert',
  blocks: [
    {
      type: 'header',
      text: { type: 'plain_text', text: '⚠️ Alert' }
    },
    {
      type: 'section',
      text: { type: 'mrkdwn', text: 'Server CPU is at 90%' }
    }
  ]
});

// Direct message
await slack.sendDirectMessage('U123456', 'Hey there!');

// Thread reply
await slack.replyInThread('#general', '1234567890.123456', 'Thanks!');
```

### Upload Files

```typescript
// Upload by file path
await slack.uploadFile({
  channels: '#reports',
  file: './monthly-report.pdf',
  title: 'Monthly Report',
  initialComment: 'Here is the latest report'
});

// Upload from content
await slack.uploadFile({
  channels: '#data',
  content: 'id,name,value\n1,test,100',
  filename: 'data.csv',
  title: 'Export Data'
});
```

### Channel Management

```typescript
// Create channel
const result = await slack.createChannel({
  name: 'new-project',
  isPrivate: true,
  description: 'Discussion for the new project'
});

// Get or create (creates if not exists)
const channel = await slack.getOrCreateChannel('alerts');

// List channels
const channels = await slack.listChannels();

// Join/Leave
await slack.joinChannel('C123456');
await slack.leaveChannel('C123456');
```

### User Management

```typescript
// Get user info
const user = await slack.getUserInfo('U123456');

// Find by email
const user = await slack.findUserByEmail('user@example.com');

// List all users
const users = await slack.listUsers();

// Include bots
const allUsers = await slack.listUsers(true);
```

### Notification Templates

```typescript
// Create template
await slack.createTemplate({
  name: 'deploy-notification',
  channel: '#deployments',
  text: '🚀 Deployed {{app}} version {{version}} to {{environment}}',
  blocks: [
    {
      type: 'section',
      text: {
        type: 'mrkdwn',
        text: '*Deployment Complete*\n{{app}} v{{version}} → {{environment}}'
      }
    }
  ]
});

// Send notification (uses template)
await slack.sendNotification('deploy-notification', {
  app: 'MyApp',
  version: '1.2.3',
  environment: 'production'
});

// Send to different channel
await slack.sendNotification(
  'deploy-notification',
  { app: 'MyApp', version: '1.2.3', environment: 'staging' },
  '#staging-alerts'
);

// List templates
const templates = await slack.listTemplates();

// Get single template
const template = await slack.getTemplate('deploy-notification');

// Delete template
await slack.deleteTemplate('old-template');
```

### Error Handling

```typescript
const result = await slack.sendMessage({
  channel: '#general',
  text: 'Hello'
});

if (!result.ok) {
  if (result.error === 'channel_not_found') {
    console.error('Channel does not exist');
  } else if (result.error === 'not_in_channel') {
    console.error('Bot needs to be invited to channel');
  } else if (result.error === 'not_authenticated') {
    console.error('Run slack-auth connect first');
  }
}
```

## Template Variables

Use `{{variableName}}` syntax in templates:

```typescript
await slack.createTemplate({
  name: 'welcome',
  channel: '#general',
  text: 'Welcome {{name}} to {{team}}! 🎉'
});

// Result: "Welcome Alice to Engineering! 🎉"
await slack.sendNotification('welcome', {
  name: 'Alice',
  team: 'Engineering'
});
```

Variables work in both text and blocks.

## Storage

- Message history is stored locally in SQLite
- Templates are stored in `~/.openclaw/skills/slack/{profile}.db`
- Database permissions: 0600 (user read/write only)

## TypeScript Types

```typescript
import {
  SlackSkill,
  MessageOptions,
  FileUploadOptions,
  CreateChannelOptions,
  NotificationTemplate,
  MessageResponse,
  ChannelInfo,
  UserInfo
} from '@openclaw/slack';
```

## Dependencies

- `@openclaw/slack-auth`: Authentication and token management
- `sqlite3`: Local database for templates and history

## Error Codes

| Error | Meaning |
|-------|---------|
| `not_authenticated` | Not connected to Slack |
| `channel_not_found` | Channel doesn't exist |
| `not_in_channel` | Bot not invited to channel |
| `invalid_auth` | Token invalid or expired |
| `rate_limited` | Too many requests |
| `template_not_found` | Template doesn't exist |
| `no_file_or_content` | Missing file path or content |

## Testing

```bash
# Type checking
npm run typecheck

# Build
npm run build

# Run CLI commands
npm run cli -- status
npm run cli -- channels
```

## Troubleshooting

### "Not authenticated" error

Connect using slack-auth first:
```bash
cd ../slack-auth
node dist/cli.js connect default
```

### "Channel not found" error

Check channel exists and bot is invited:
```bash
node dist/cli.js channels
node dist/cli.js join "#channel-name"
```

### "Not in channel" error

The bot needs to be invited to the channel:
```bash
# In Slack, invite the bot:
/invite @YourBotName
```

### Permission errors

Ensure your Slack app has these scopes:
- `chat:write` - Send messages
- `chat:write.public` - Send to public channels
- `files:write` - Upload files
- `channels:read` - List channels
- `users:read` - Get user info
- `channels:join` - Join channels
