---
name: slack-auth
description: "Slack OAuth and bot token management for team communication. Built on top of auth-provider for secure token storage with automatic refresh, multi-workspace support, permission validation, and health checks."
version: 1.0.0
author: OpenClaw
entry: ./dist/cli.js
type: script
---

# Slack Auth Skill

Slack OAuth 2.0 integration for accessing Slack workspaces. This skill provides a simplified interface built on top of the auth-provider skill, handling authentication, token storage, automatic refresh, and health monitoring for Slack bot tokens.

## Features

- **Multi-Workspace Support**: Connect to multiple Slack workspaces
- **Bot Token Management**: Secure storage and validation of bot tokens
- **Permission Validation**: Verify token permissions and scopes
- **Health Checks**: Monitor token validity and workspace access
- **Auto-Refresh**: Tokens automatically refresh when needed

## Installation

```bash
npm install
npm run build
```

## Environment Configuration

The Slack auth skill uses the auth-provider skill's configuration. Ensure you have set up the auth-provider environment:

```bash
# ~/.openclaw/.env

# Slack OAuth credentials
SLACK_CLIENT_ID=your-slack-client-id
SLACK_CLIENT_SECRET=your-slack-client-secret
SLACK_REDIRECT_URI=http://localhost:8080/auth/callback

# Optional: Custom encryption key
AUTH_PROVIDER_KEY=your-encryption-key-min-32-chars
```

## CLI Usage

### Check Status

```bash
# Check default profile
node dist/cli.js status

# Check specific profile
node dist/cli.js status work
```

### Connect Workspace

```bash
# Connect with default scopes
node dist/cli.js connect default

# Connect with specific profile name
node dist/cli.js connect my-workspace
```

### Complete OAuth Flow

After opening the authorization URL and granting permission:

```bash
node dist/cli.js complete default "AUTH_CODE" "STATE"
```

### List Profiles

```bash
node dist/cli.js profiles
```

### Health Check

```bash
# Check specific profile
node dist/cli.js health default

# Check all profiles
node dist/cli.js health
```

### Disconnect

```bash
# Disconnect specific profile
node dist/cli.js disconnect default

# Disconnect all profiles
node dist/cli.js disconnect
```

### Test Connection

```bash
# Send a test message
node dist/cli.js test default #general "Hello from Slack Auth Skill!"
```

## JavaScript/TypeScript API

### Initialize Client

```typescript
import { SlackAuthClient } from '@openclaw/slack-auth';

// Create client for default profile
const slack = new SlackAuthClient();

// Or for specific workspace
const workSlack = SlackAuthClient.forProfile('work');
const personalSlack = SlackAuthClient.forProfile('personal');
```

### OAuth Flow

```typescript
// Step 1: Initiate authorization
const auth = slack.initiateAuth();

console.log('Open this URL:', auth.url);
console.log('State:', auth.state); // Save for step 2

// Step 2: Complete with authorization code
const result = await slack.completeAuth(code, state);

if (result.success) {
  console.log('Connected to workspace:', result.team);
  console.log('Scopes:', result.scopes);
} else {
  console.error('Failed:', result.error);
}
```

### Check Connection Status

```typescript
if (await slack.isConnected()) {
  console.log('Connected!');
  
  // Get workspace info
  const info = await slack.getWorkspaceInfo();
  console.log('Team:', info?.team);
  console.log('User:', info?.user);
} else {
  console.log('Not connected');
}
```

### Get Access Token

```typescript
// Gets valid token (auto-refreshes if needed)
const token = await slack.getAccessToken();

// Use with Slack API
const response = await fetch('https://slack.com/api/auth.test', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
```

### Validate Permissions

```typescript
const validation = await slack.validatePermissions();

console.log('Valid:', validation.valid);
console.log('Permissions:', validation.permissions);
```

### Health Check

```typescript
const health = await slack.healthCheck();

if (health.status === 'healthy') {
  console.log('Token is valid');
  console.log('Workspace:', health.message);
} else {
  console.warn('Token issue:', health.message);
}
```

### Send Message

```typescript
const result = await slack.sendMessage('#general', 'Hello from the skill!');

if (result.ok) {
  console.log('Message sent:', result.ts);
} else {
  console.error('Failed:', result.error);
}
```

### List Channels

```typescript
const channels = await slack.listChannels();

for (const channel of channels) {
  console.log(`${channel.name}: ${channel.num_members} members`);
}
```

### Disconnect

```typescript
// Disconnect specific profile
await slack.disconnect();

// Or disconnect all profiles
import { disconnectAll } from '@openclaw/slack-auth';
await disconnectAll();
```

### Make Authenticated Requests

```typescript
// Convenient method for authenticated requests
const response = await slack.fetch('https://slack.com/api/users.info', {
  method: 'POST',
  body: JSON.stringify({ user: 'U123456' })
});
const data = await response.json();
```

## Scope Reference

### Default Scopes

The Slack auth skill requests the following scopes by default:

| Scope | Description |
|-------|-------------|
| `chat:write` | Send messages as the app |
| `chat:write.public` | Send messages to public channels |
| `users:read` | View users in the workspace |
| `team:read` | View team information |
| `files:write` | Upload and modify files |
| `channels:read` | View public channels |
| `groups:read` | View private channels |
| `im:read` | View direct messages |
| `mpim:read` | View group direct messages |

## Multi-Workspace Support

Manage multiple Slack workspaces:

```typescript
import { SlackAuthClient, getConnectedProfiles } from '@openclaw/slack-auth';

// Different profiles for different workspaces
const work = SlackAuthClient.forProfile('work');
const community = SlackAuthClient.forProfile('community');

// Connect both
work.initiateAuth();
community.initiateAuth();

// List all connected profiles
const profiles = await getConnectedProfiles();
console.log('Connected workspaces:', profiles);

// Check each profile's health
for (const profileName of profiles) {
  const client = SlackAuthClient.forProfile(profileName);
  const health = await client.healthCheck();
  console.log(`${profileName}: ${health.status}`);
}
```

## Using with Slack API

### Send a Message

```typescript
const client = SlackAuthClient.forProfile('default');
const token = await client.getAccessToken();

const response = await client.fetch('https://slack.com/api/chat.postMessage', {
  method: 'POST',
  body: JSON.stringify({
    channel: '#general',
    text: 'Hello from Slack Auth Skill!'
  })
});

const result = await response.json();
```

### Get User Info

```typescript
const response = await client.fetch('https://slack.com/api/users.info', {
  method: 'POST',
  body: JSON.stringify({ user: 'U123456' })
});
const userInfo = await response.json();
```

### List Channels

```typescript
const response = await client.fetch('https://slack.com/api/conversations.list');
const channels = await response.json();
```

## Error Handling

```typescript
try {
  const token = await slack.getAccessToken();
  if (!token) {
    console.log('Not authenticated');
    return;
  }
  
  // Make API request
  const response = await slack.sendMessage('#general', 'Hello!');
  
  if (!response.ok) {
    if (response.error === 'channel_not_found') {
      console.error('Channel not found');
    } else if (response.error === 'not_in_channel') {
      console.error('Bot is not in the channel');
    } else if (response.error === 'invalid_auth') {
      console.error('Token invalid - try reconnecting');
    }
  }
} catch (error) {
  console.error('Request failed:', error.message);
}
```

## Storage

Tokens are securely stored by the auth-provider skill in:
```
~/.openclaw/skills/auth-provider/credentials.db
```

All sensitive data is AES-256 encrypted.

## Testing

```bash
# Type checking
npm run typecheck

# Build
npm run build

# Run CLI commands
npm run cli -- status
npm run cli -- connect default
npm run status  # shortcut
```

## Troubleshooting

### "Not authenticated" error

The user needs to connect their Slack workspace:
```bash
node dist/cli.js connect default
```

### "channel_not_found" error

The bot may not have access to the channel. Make sure:
1. The channel exists
2. The bot has been invited to the channel
3. The bot has the necessary scopes

### "invalid_auth" error

The token may be expired or revoked. Check health:
```bash
node dist/cli.js health
```

If needed, reconnect:
```bash
node dist/cli.js disconnect default
node dist/cli.js connect default
```

### Connection issues

Check your Slack OAuth credentials in `~/.openclaw/.env`:
```bash
# Verify auth-provider environment
node ../auth-provider/dist/cli.js env-check
```

## Dependencies

- `@openclaw/auth-provider`: For OAuth flow and token storage
- `sqlite3`: Database access (via auth-provider)

## Security Notes

- Tokens are stored encrypted by auth-provider
- OAuth uses PKCE flow for security
- Bot tokens don't typically expire but are validated on each health check
- Database file has 0600 permissions (user read/write only)
