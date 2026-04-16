#!/usr/bin/env node
/**
 * QuickBooks OAuth Skill CLI
 * Command-line interface for QuickBooks OAuth operations
 */

import { 
  QuickBooksAuthClient, 
  getConnectedProfiles, 
  hasAnyConnection,
  disconnectAll,
  healthCheckAll,
  QuickBooksEnvironment,
  getAuthProvider
} from './index';

// ANSI colors for terminal output
const colors = {
  green: '\x1b[92m',
  red: '\x1b[91m',
  yellow: '\x1b[93m',
  blue: '\x1b[94m',
  reset: '\x1b[0m',
  bold: '\x1b[1m',
};

const success = (msg: string) => console.log(`${colors.green}✓${colors.reset} ${msg}`);
const error = (msg: string) => console.error(`${colors.red}✗${colors.reset} ${msg}`);
const info = (msg: string) => console.log(`${colors.blue}ℹ${colors.reset} ${msg}`);
const warning = (msg: string) => console.log(`${colors.yellow}⚠${colors.reset} ${msg}`);

function printHelp(): void {
  console.log(`
${colors.bold}QuickBooks OAuth Skill CLI${colors.reset}

Commands:
  status [profile]                     Check connection status
  connect <profile> [environment]      Initiate OAuth flow
  complete <profile> <code> <state> <realmId>  Complete OAuth with code
  disconnect [profile]                 Disconnect QuickBooks account
  health [profile]                     Check token health
  profiles                             List all connected profiles
  env                                  Show environment configuration

Environment:
  sandbox (default) or production

Examples:
  # Check status of default profile
  quickbooks-auth status

  # Check specific profile
  quickbooks-auth status mycompany

  # Connect sandbox account (default)
  quickbooks-auth connect mycompany

  # Connect production account
  quickbooks-auth connect mycompany production

  # Complete OAuth (realmId comes from callback URL)
  quickbooks-auth complete mycompany "AUTH_CODE" "STATE" "REALM_ID"

  # Disconnect all profiles
  quickbooks-auth disconnect

  # Check health of all profiles
  quickbooks-auth health
`);
}

async function cmdStatus(profile: string = 'default'): Promise<number> {
  console.log(`${colors.bold}QuickBooks OAuth Status${colors.reset}`);
  console.log('=' .repeat(50));
  
  const client = QuickBooksAuthClient.forProfile(profile);
  
  if (await client.isConnected()) {
    const tokenData = await client.getTokenData();
    const realmId = await client.getRealmId();
    const environment = await client.getEnvironment();
    
    success('Connected to QuickBooks');
    console.log(`\n  Profile: ${colors.bold}${profile}${colors.reset}`);
    console.log(`  Realm ID: ${colors.bold}${realmId || 'Unknown'}${colors.reset}`);
    console.log(`  Environment: ${environment === 'production' ? colors.green : colors.yellow}${environment}${colors.reset}`);
    
    if (tokenData?.expires_at) {
      const expiresDate = new Date(tokenData.expires_at * 1000);
      const isExpired = tokenData.expires_at < Date.now() / 1000;
      console.log(`  Expires: ${isExpired ? colors.red : colors.green}${expiresDate.toLocaleString()}${colors.reset}`);
    }
    
    if (tokenData?.scope) {
      console.log(`\n  Authorized Scopes:`);
      tokenData.scope.split(' ').forEach(scope => {
        console.log(`    ${colors.green}✓${colors.reset} ${scope}`);
      });
    }
    
    return 0;
  } else {
    error('Not connected to QuickBooks');
    console.log(`\n  Profile: ${profile}`);
    console.log('\n  To connect, run:');
    console.log(`    quickbooks-auth connect ${profile}`);
    return 1;
  }
}

async function cmdConnect(profile: string, envStr: string = 'sandbox'): Promise<number> {
  console.log(`${colors.bold}QuickBooks OAuth Connection${colors.reset}`);
  console.log('=' .repeat(50));
  
  const environment = envStr.toLowerCase() as QuickBooksEnvironment;
  
  if (environment !== 'sandbox' && environment !== 'production') {
    error(`Invalid environment: ${envStr}`);
    info('Valid environments: sandbox, production');
    return 1;
  }
  
  const client = QuickBooksAuthClient.forProfile(profile, environment);
  
  // Check if already connected
  if (await client.isConnected()) {
    const realmId = await client.getRealmId();
    warning(`Already connected (Realm: ${realmId})`);
    info('Use "disconnect" first to reconnect');
    return 0;
  }
  
  // Initiate auth
  info(`Initiating ${environment} OAuth flow...`);
  
  try {
    const auth = client.initiateAuth();
    
    success('Authorization URL generated');
    console.log(`\n  URL: ${colors.blue}${auth.url}${colors.reset}`);
    console.log(`  State: ${auth.state.substring(0, 30)}...`);
    console.log(`  Environment: ${environment}`);
    console.log(`  Scopes: ${auth.scopes.join(', ')}`);
    
    console.log(`\n${colors.bold}Next Steps:${colors.reset}`);
    console.log('  1. Open the URL in a browser');
    console.log('  2. Sign in to your Intuit/QuickBooks account');
    console.log('  3. Select your company');
    console.log('  4. Authorize the application');
    console.log('  5. Copy the authorization code');
    console.log('  6. Note the realmId from the URL (e.g., 1234567890)');
    console.log(`  7. Run: quickbooks-auth complete ${profile} "CODE" "${auth.state}" "REALM_ID"`);
    
    return 0;
  } catch (err) {
    error(err instanceof Error ? err.message : String(err));
    info('Ensure QUICKBOOKS_CLIENT_ID and QUICKBOOKS_CLIENT_SECRET are set in ~/.openclaw/.env');
    return 1;
  }
}

async function cmdComplete(profile: string, code: string, state: string, realmId: string): Promise<number> {
  console.log(`${colors.bold}Completing QuickBooks OAuth${colors.reset}`);
  console.log('=' .repeat(50));
  
  const client = QuickBooksAuthClient.forProfile(profile);
  
  info('Exchanging authorization code for tokens...');
  
  const result = await client.completeAuth(code, state, realmId);
  
  if (result.success) {
    success('Authentication successful!');
    console.log(`\n  Profile: ${colors.bold}${profile}${colors.reset}`);
    console.log(`  Realm ID: ${colors.bold}${result.realmId}${colors.reset}`);
    console.log(`  Environment: ${result.environment}`);
    if (result.scopes) {
      console.log(`  Scopes: ${result.scopes.length} permissions granted`);
    }
    if (result.expiresAt) {
      const expiresDate = new Date(result.expiresAt * 1000);
      console.log(`  Expires: ${expiresDate.toLocaleString()}`);
    }
    return 0;
  } else {
    error(`Authentication failed: ${result.error}`);
    return 1;
  }
}

async function cmdDisconnect(profile?: string): Promise<number> {
  console.log(`${colors.bold}QuickBooks OAuth Disconnect${colors.reset}`);
  console.log('=' .repeat(50));
  
  if (profile) {
    const client = QuickBooksAuthClient.forProfile(profile);
    if (await client.disconnect()) {
      success(`Disconnected profile: ${profile}`);
      return 0;
    } else {
      error(`Profile not connected: ${profile}`);
      return 1;
    }
  } else {
    const count = await disconnectAll();
    if (count > 0) {
      success(`Disconnected ${count} profile(s)`);
      return 0;
    } else {
      warning('No profiles were connected');
      return 0;
    }
  }
}

async function cmdHealth(profile?: string): Promise<number> {
  console.log(`${colors.bold}QuickBooks OAuth Health Check${colors.reset}`);
  console.log('=' .repeat(50));
  
  if (profile) {
    const client = QuickBooksAuthClient.forProfile(profile);
    const result = await client.healthCheck();
    
    console.log(`\n  Profile: ${profile}`);
    console.log(`  Status: ${result.status === 'healthy' ? colors.green : colors.red}${result.status}${colors.reset}`);
    
    if (result.realmId) {
      console.log(`  Realm ID: ${result.realmId}`);
    }
    
    if (result.message) {
      console.log(`  Message: ${result.message}`);
    }
    
    if (result.expiresAt) {
      const expiresDate = new Date(result.expiresAt * 1000);
      console.log(`  Expires: ${expiresDate.toLocaleString()}`);
    }
    
    return result.status === 'healthy' ? 0 : 1;
  } else {
    const results = await healthCheckAll();
    
    if (results.length === 0) {
      info('No QuickBooks profiles configured');
      return 0;
    }
    
    let healthyCount = 0;
    
    results.forEach(result => {
      console.log(`\n  Profile: ${result.profile}`);
      console.log(`  Status: ${result.status === 'healthy' ? colors.green : colors.red}${result.status}${colors.reset}`);
      if (result.realmId) {
        console.log(`  Realm ID: ${result.realmId}`);
      }
      if (result.message) {
        console.log(`  Message: ${result.message}`);
      }
      if (result.status === 'healthy') healthyCount++;
    });
    
    console.log(`\n${healthyCount}/${results.length} profiles healthy`);
    
    return healthyCount === results.length ? 0 : 1;
  }
}

async function cmdProfiles(): Promise<number> {
  console.log(`${colors.bold}QuickBooks OAuth Profiles${colors.reset}`);
  console.log('=' .repeat(50));
  
  const profiles = await getConnectedProfiles();
  
  if (profiles.length === 0) {
    info('No QuickBooks profiles connected');
    console.log('\nTo connect a profile, run:');
    console.log('  quickbooks-auth connect <profile>');
    return 0;
  }
  
  success(`${profiles.length} profile(s) connected`);
  
  for (const profileName of profiles) {
    const client = QuickBooksAuthClient.forProfile(profileName);
    const realmId = await client.getRealmId();
    const environment = await client.getEnvironment();
    console.log(`\n  ${colors.bold}${profileName}${colors.reset}`);
    console.log(`    Realm ID: ${realmId || 'Unknown'}`);
    console.log(`    Environment: ${environment}`);
  }
  
  return 0;
}

async function cmdEnv(): Promise<number> {
  console.log(`${colors.bold}QuickBooks OAuth Environment${colors.reset}`);
  console.log('=' .repeat(50));
  
  const clientId = process.env.QUICKBOOKS_CLIENT_ID;
  const clientSecret = process.env.QUICKBOOKS_CLIENT_SECRET;
  const redirectUri = process.env.QUICKBOOKS_REDIRECT_URI;
  const environment = process.env.QUICKBOOKS_ENVIRONMENT;
  
  console.log('\nRequired Environment Variables:');
  console.log(`  QUICKBOOKS_CLIENT_ID: ${clientId ? colors.green + '✓ Set' : colors.red + '✗ Not set'}${colors.reset}`);
  console.log(`  QUICKBOOKS_CLIENT_SECRET: ${clientSecret ? colors.green + '✓ Set' : colors.red + '✗ Not set'}${colors.reset}`);
  console.log(`  QUICKBOOKS_REDIRECT_URI: ${redirectUri ? colors.green + '✓ Set (' + redirectUri + ')' : colors.yellow + '⚠ Using default (http://localhost:8080/auth/callback)'}${colors.reset}`);
  
  console.log('\nOptional Environment Variables:');
  console.log(`  QUICKBOOKS_ENVIRONMENT: ${environment || colors.yellow + 'sandbox (default)' + colors.reset}`);
  
  console.log('\nSetup Instructions:');
  console.log('  1. Go to https://developer.intuit.com/');
  console.log('  2. Create a new app or use an existing one');
  console.log('  3. Add OAuth 2.0 redirect URI: http://localhost:8080/auth/callback');
  console.log('  4. Copy Client ID and Client Secret');
  console.log('  5. Add them to ~/.openclaw/.env');
  
  if (clientId && clientSecret) {
    console.log(`\n${colors.green}✓ Environment is configured${colors.reset}`);
    return 0;
  } else {
    console.log(`\n${colors.red}✗ Environment is not fully configured${colors.reset}`);
    return 1;
  }
}

async function main(): Promise<number> {
  const args = process.argv.slice(2);
  
  if (args.length === 0 || args[0] === '--help' || args[0] === '-h') {
    printHelp();
    return 0;
  }
  
  const command = args[0];
  
  try {
    switch (command) {
      case 'status':
        return await cmdStatus(args[1]);
        
      case 'connect':
        if (!args[1]) {
          error('Profile name required');
          info('Usage: quickbooks-auth connect <profile> [environment]');
          return 1;
        }
        return await cmdConnect(args[1], args[2]);
        
      case 'complete':
        if (!args[1] || !args[2] || !args[3] || !args[4]) {
          error('Profile, code, state, and realmId required');
          info('Usage: quickbooks-auth complete <profile> <code> <state> <realmId>');
          return 1;
        }
        return await cmdComplete(args[1], args[2], args[3], args[4]);
        
      case 'disconnect':
        return await cmdDisconnect(args[1]);
        
      case 'health':
        return await cmdHealth(args[1]);
        
      case 'profiles':
        return await cmdProfiles();
        
      case 'env':
        return await cmdEnv();
        
      default:
        error(`Unknown command: ${command}`);
        printHelp();
        return 1;
    }
  } catch (err) {
    error(err instanceof Error ? err.message : String(err));
    return 1;
  }
}

main().then(code => process.exit(code));
