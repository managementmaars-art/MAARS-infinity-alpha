---
name: quickbooks-auth
description: "QuickBooks OAuth adapter for QuickBooks Online accounting integration. Built on top of auth-provider for secure token management with automatic refresh, multi-profile support, sandbox/production toggle, and health checks."
version: 1.0.0
author: OpenClaw
entry: ./dist/cli.js
type: script
---

# QuickBooks OAuth Skill

QuickBooks OAuth 2.0 integration for accessing QuickBooks Online accounting API. This skill provides a simplified interface built on top of the auth-provider skill, handling authentication, token storage, automatic refresh, and health monitoring.

## Features

- **Multi-Profile**: Manage multiple QuickBooks companies
- **Environment Toggle**: Switch between sandbox and production
- **Realm ID Storage**: Automatic storage of company Realm ID
- **Auto-Refresh**: Tokens automatically refresh before expiration
- **Health Checks**: Monitor token validity and expiration

## Installation

```bash
npm install
npm run build
```

## Environment Configuration

The QuickBooks OAuth skill uses the auth-provider skill's configuration. Ensure you have set up the auth-provider environment:

```bash
# ~/.openclaw/.env

# QuickBooks OAuth credentials (from https://developer.intuit.com/)
QUICKBOOKS_CLIENT_ID=your-quickbooks-client-id
QUICKBOOKS_CLIENT_SECRET=your-quickbooks-client-secret
QUICKBOOKS_REDIRECT_URI=http://localhost:8080/auth/callback

# Optional: Default environment (sandbox or production)
QUICKBOOKS_ENVIRONMENT=sandbox

# Optional: Custom encryption key
AUTH_PROVIDER_KEY=your-encryption-key-min-32-chars
```

### Getting QuickBooks Credentials

1. Go to [Intuit Developer](https://developer.intuit.com/)
2. Sign in or create a developer account
3. Create a new app or select an existing one
4. Go to the "Keys & Credentials" section
5. Copy the Client ID and Client Secret
6. Add `http://localhost:8080/auth/callback` to the redirect URIs

## CLI Usage

### Check Status

```bash
# Check default profile
node dist/cli.js status

# Check specific profile
node dist/cli.js status mycompany
```

### Connect Account

```bash
# Connect to sandbox (default)
node dist/cli.js connect mycompany

# Connect to production
node dist/cli.js connect mycompany production
```

### Complete OAuth Flow

After opening the authorization URL and granting permission:

```bash
node dist/cli.js complete mycompany "AUTH_CODE" "STATE" "REALM_ID"
```

**Note:** The Realm ID is provided by QuickBooks in the callback URL after authorization.

### List Profiles

```bash
node dist/cli.js profiles
```

### Health Check

```bash
# Check specific profile
node dist/cli.js health mycompany

# Check all profiles
node dist/cli.js health
```

### Disconnect

```bash
# Disconnect specific profile
node dist/cli.js disconnect mycompany

# Disconnect all profiles
node dist/cli.js disconnect
```

### Environment Check

```bash
node dist/cli.js env
```

## JavaScript/TypeScript API

### Initialize Client

```typescript
import { QuickBooksAuthClient } from './index';

// Create client for default profile (sandbox)
const client = new QuickBooksAuthClient();

// Or for specific profile and environment
const productionClient = QuickBooksAuthClient.forProfile('mycompany', 'production');
const sandboxClient = QuickBooksAuthClient.forProfile('testcompany', 'sandbox');
```

### OAuth Flow

```typescript
// Step 1: Initiate authorization
const auth = client.initiateAuth();

console.log('Open this URL:', auth.url);
console.log('State:', auth.state); // Save for step 2

// Step 2: Complete with authorization code and realmId
const result = await client.completeAuth(code, state, realmId);

if (result.success) {
  console.log('Connected!');
  console.log('Realm ID:', result.realmId);
  console.log('Environment:', result.environment);
} else {
  console.error('Failed:', result.error);
}
```

### Check Connection Status

```typescript
if (await client.isConnected()) {
  console.log('Connected!');
  
  // Get realm ID
  const realmId = await client.getRealmId();
  console.log('Realm ID:', realmId);
  
  // Get environment
  const environment = await client.getEnvironment();
  console.log('Environment:', environment);
} else {
  console.log('Not connected');
}
```

### Get Access Token

```typescript
// Gets valid token (auto-refreshes if needed)
const token = await client.getAccessToken();

// Use with QuickBooks API
const baseUrl = await client.getApiBaseUrl();
const response = await fetch(`${baseUrl}/${realmId}/companyinfo/${realmId}`, {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Accept': 'application/json'
  }
});
```

### Make Authenticated Requests

```typescript
// Convenient method for authenticated requests
const response = await client.fetch('/companyinfo/1234567890');
const data = await response.json();
```

### Health Check

```typescript
const health = await client.healthCheck();

if (health.status === 'healthy') {
  console.log('Token is valid');
  console.log('Realm ID:', health.realmId);
  console.log('Expires at:', new Date(health.expiresAt! * 1000));
} else {
  console.warn('Token issue:', health.message);
}
```

### Disconnect

```typescript
// Disconnect specific profile
await client.disconnect();

// Or disconnect all profiles
import { disconnectAll } from './index';
await disconnectAll();
```

## Multi-Profile Support

Manage multiple QuickBooks companies:

```typescript
import { QuickBooksAuthClient, getConnectedProfiles } from './index';

// Different profiles for different companies
const companyA = QuickBooksAuthClient.forProfile('company-a', 'production');
const companyB = QuickBooksAuthClient.forProfile('company-b', 'sandbox');
const testCompany = QuickBooksAuthClient.forProfile('test', 'sandbox');

// Connect each
companyA.initiateAuth();
companyB.initiateAuth();

// List all connected profiles
const profiles = await getConnectedProfiles();
console.log('Connected profiles:', profiles);

// Check each profile's health
for (const profileName of profiles) {
  const client = QuickBooksAuthClient.forProfile(profileName);
  const health = await client.healthCheck();
  const realmId = await client.getRealmId();
  console.log(`${profileName} (${realmId}): ${health.status}`);
}
```

## Environment Support

### Sandbox

Use sandbox environment for development and testing:

```bash
# Connect to sandbox
node dist/cli.js connect mycompany sandbox
```

Sandbox API base URL: `https://sandbox-quickbooks.api.intuit.com/v3/company`

### Production

Use production environment for live data:

```bash
# Connect to production
node dist/cli.js connect mycompany production
```

Production API base URL: `https://quickbooks.api.intuit.com/v3/company`

## Using with QuickBooks API

### Company Info

```typescript
const client = QuickBooksAuthClient.forProfile('mycompany');
const realmId = await client.getRealmId();

// Get company info
const response = await client.fetch(`/companyinfo/${realmId}`);
const data = await response.json();
console.log('Company:', data.CompanyInfo.CompanyName);
```

### Customers

```typescript
// List customers
const response = await client.fetch('/query?query=select * from Customer maxresults 10');
const customers = await response.json();
```

### Invoices

```typescript
// List invoices
const response = await client.fetch('/query?query=select * from Invoice maxresults 10');
const invoices = await response.json();
```

### Create Invoice

```typescript
const invoice = {
  Line: [{
    DetailType: 'SalesItemLineDetail',
    Amount: 100.00,
    SalesItemLineDetail: {
      ItemRef: { value: '1', name: 'Services' }
    }
  }],
  CustomerRef: { value: '1' }
};

const response = await client.fetch('/invoice', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(invoice)
});
```

## Error Handling

```typescript
try {
  const token = await client.getAccessToken();
  if (!token) {
    console.log('Not authenticated');
    return;
  }
  
  // Make API request
  const response = await client.fetch('/companyinfo/1234567890');
  
  if (!response.ok) {
    if (response.status === 401) {
      console.error('Token expired or invalid - will auto-refresh on next call');
    } else if (response.status === 403) {
      console.error('Permission denied - check QuickBooks subscription');
    } else if (response.status === 404) {
      console.error('Company or resource not found');
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

All sensitive data is AES-256 encrypted. The Realm ID is stored in the token metadata.

## Testing

```bash
# Type checking
npm run typecheck

# Build
npm run build

# Run CLI commands
npm run cli -- status
npm run cli -- connect mycompany
npm run status  # shortcut
```

## Troubleshooting

### "Not authenticated" error

The user needs to connect their QuickBooks account:
```bash
node dist/cli.js connect mycompany
```

### "QuickBooks adapter not found" error

Ensure your environment variables are set:
```bash
node dist/cli.js env
```

### "Realm ID not found" error

The Realm ID is required and must be captured from the OAuth callback URL. When completing auth:
```bash
node dist/cli.js complete mycompany "CODE" "STATE" "REALM_ID"
```

### Token expired

Tokens auto-refresh when calling `getAccessToken()` or `fetch()`. If issues persist, check health:
```bash
node dist/cli.js health
```

### Connection issues

Check your QuickBooks OAuth credentials in `~/.openclaw/.env`:
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
- Tokens auto-refresh 5 minutes before expiration
- Database file has 0600 permissions (user read/write only)
- Realm ID is stored alongside tokens for API calls
