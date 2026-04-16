#!/usr/bin/env node
/**
 * Slack Auth CLI
 * Command-line interface for Slack OAuth operations
 */

import { 
  SlackAuthClient, 
  getConnectedProfiles, 
  hasAnyConnection,
  disconnectAll,
  healthCheckAll,
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
${colors.bold}Slack Auth Skill CLI${colors.reset}

Commands:
  status [profile]              Check connection status
  connect <profile>             Initiate OAuth flow
  complete <profile> <code> <state>  Complete OAuth with code
  disconnect [profile]          Disconnect Slack workspace
  health [profile]              Check token health
  profiles                      List all connected profiles
  test <profile> <channel> [message]  Send test message

Examples:
  # Check status of default profile
  slack-auth status

  # Check specific profile
  slack-auth status work

  # Connect a workspace
  slack-auth connect default

  # Complete OAuth
  slack-auth complete default "AUTH_CODE" "STATE"

  # Disconnect all profiles
  slack-auth disconnect

  # Check health of all profiles
  slack-auth health

  # Send test message
  slack-auth test default #general "Hello!"
`);
}

async function cmdStatus(profile: string = 'default'): Promise<number> {
  console.log(`${colors.bold}Slack Auth Status${colors.reset}`);
  console.log('=' .repeat(50));
  
  const client = SlackAuthClient.forProfile(profile);
  
  if (await client.isConnected()) {
    const workspaceInfo = await client.getWorkspaceInfo();
    const scopes = await client.getConnectedScopes();
    
    success('Connected to Slack');
    console.log(`\n  Profile: ${colors.bold}${profile}${colors.reset}`);
    
    if (workspaceInfo) {
      console.log(`  Workspace: ${colors.bold}${workspaceInfo.team}${colors.reset}`);
      console.log(`  Team ID: ${workspaceInfo.teamId}`);
      console.log(`  User: ${workspaceInfo.user}`);
      console.log(`  URL: ${workspaceInfo.url}`);
    }
    
    if (scopes.length > 0) {
      console.log(`\n  Authorized Scopes:`);
      scopes.forEach(scope => {
        console.log(`    ${colors.green}✓${colors.reset} ${scope}`);
      });
    }
    
    return 0;
  } else {
    error('Not connected to Slack');
    console.log(`\n  Profile: ${profile}`);
    console.log('\n  To connect, run:');
    console.log(`    slack-auth connect ${profile}`);
    return 1;
  }
}

async function cmdConnect(profile: string): Promise<number> {
  console.log(`${colors.bold}Slack OAuth Connection${colors.reset}`);
  console.log('=' .repeat(50));
  
  if (!profile) {
    error('Profile name is required');
    info('Usage: slack-auth connect <profile>');
    return 1;
  }
  
  const client = SlackAuthClient.forProfile(profile);
  
  // Check if already connected
  if (await client.isConnected()) {
    const workspaceInfo = await client.getWorkspaceInfo();
    warning(`Already connected to ${workspaceInfo?.team || 'a workspace'}`);
    info('Use "disconnect" first to reconnect');
    return 0;
  }
  
  // Initiate auth
  info('Generating authorization URL...');
  
  const auth = client.initiateAuth();
  
  success('Authorization URL generated');
  console.log(`\n  URL: ${colors.blue}${auth.url}${colors.reset}`);
  console.log(`  State: ${auth.state.substring(0, 30)}...`);
  
  console.log(`\n${colors.bold}Next Steps:${colors.reset}`);
  console.log('  1. Open the URL in a browser');
  console.log('  2. Authorize the app in your Slack workspace');
  console.log('  3. Copy the authorization code');
  console.log(`  4. Run: slack-auth complete ${profile} "CODE" "${auth.state}"`);
  
  return 0;
}

async function cmdComplete(profile: string, code: string, state: string): Promise<number> {
  console.log(`${colors.bold}Completing Slack OAuth${colors.reset}`);
  console.log('=' .repeat(50));
  
  if (!profile || !code || !state) {
    error('Profile, code, and state are required');
    info('Usage: slack-auth complete <profile> <code> <state>');
    return 1;
  }
  
  const client = SlackAuthClient.forProfile(profile);
  
  info('Exchanging authorization code for tokens...');
  
  const result = await client.completeAuth(code, state);
  
  if (result.success) {
    success('Authentication successful!');
    console.log(`\n  Profile: ${colors.bold}${profile}${colors.reset}`);
    if (result.team) {
      console.log(`  Workspace: ${colors.bold}${result.team}${colors.reset}`);
    }
    if (result.user) {
      console.log(`  User: ${result.user}`);
    }
    if (result.teamId) {
      console.log(`  Team ID: ${result.teamId}`);
    }
    if (result.scopes) {
      console.log(`  Scopes: ${result.scopes.length} permissions granted`);
    }
    return 0;
  } else {
    error(`Authentication failed: ${result.error}`);
    return 1;
  }
}

async function cmdDisconnect(profile?: string): Promise<number> {
  console.log(`${colors.bold}Slack Auth Disconnect${colors.reset}`);
  console.log('=' .repeat(50));
  
  if (profile) {
    const client = SlackAuthClient.forProfile(profile);
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
  console.log(`${colors.bold}Slack Auth Health Check${colors.reset}`);
  console.log('=' .repeat(50));
  
  if (profile) {
    const client = SlackAuthClient.forProfile(profile);
    const result = await client.healthCheck();
    
    console.log(`\n  Profile: ${profile}`);
    console.log(`  Status: ${result.status === 'healthy' ? colors.green : colors.red}${result.status}${colors.reset}`);
    
    if (result.message) {
      console.log(`  Message: ${result.message}`);
    }
    
    return result.status === 'healthy' ? 0 : 1;
  } else {
    const results = await healthCheckAll();
    
    if (results.length === 0) {
      info('No Slack profiles configured');
      return 0;
    }
    
    let healthyCount = 0;
    
    results.forEach(result => {
      console.log(`\n  Profile: ${result.profile}`);
      console.log(`  Status: ${result.status === 'healthy' ? colors.green : colors.red}${result.status}${colors.reset}`);
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
  console.log(`${colors.bold}Slack Auth Profiles${colors.reset}`);
  console.log('=' .repeat(50));
  
  const profiles = await getConnectedProfiles();
  
  if (profiles.length === 0) {
    info('No Slack workspaces connected');
    console.log('\nTo connect a workspace, run:');
    console.log('  slack-auth connect <profile>');
    return 0;
  }
  
  success(`${profiles.length} workspace(s) connected`);
  
  for (const profileName of profiles) {
    const client = SlackAuthClient.forProfile(profileName);
    const workspaceInfo = await client.getWorkspaceInfo();
    const scopes = await client.getConnectedScopes();
    console.log(`\n  ${colors.bold}${profileName}${colors.reset}`);
    console.log(`    Workspace: ${workspaceInfo?.team || 'Unknown'}`);
    console.log(`    User: ${workspaceInfo?.user || 'Unknown'}`);
    console.log(`    Scopes: ${scopes.length} permissions`);
  }
  
  return 0;
}

async function cmdTest(profile: string, channel: string, message?: string): Promise<number> {
  if (!profile || !channel) {
    error('Profile and channel are required');
    info('Usage: slack-auth test <profile> <channel> [message]');
    return 1;
  }
  
  console.log(`${colors.bold}Slack Test Message${colors.reset}`);
  console.log('=' .repeat(50));
  
  const client = SlackAuthClient.forProfile(profile);
  
  if (!(await client.isConnected())) {
    error(`Profile "${profile}" is not connected`);
    return 1;
  }
  
  const testMessage = message || 'Hello from Slack Auth Skill! 👋';
  
  info(`Sending message to ${channel}...`);
  
  const result = await client.sendMessage(channel, testMessage);
  
  if (result.ok) {
    success('Message sent successfully!');
    console.log(`  Channel: ${channel}`);
    console.log(`  Timestamp: ${result.ts}`);
    return 0;
  } else {
    error(`Failed to send message: ${result.error}`);
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
        return await cmdConnect(args[1]);
        
      case 'complete':
        if (!args[1] || !args[2] || !args[3]) {
          error('Profile, code, and state required');
          info('Usage: slack-auth complete <profile> <code> <state>');
          return 1;
        }
        return await cmdComplete(args[1], args[2], args[3]);
        
      case 'disconnect':
        return await cmdDisconnect(args[1]);
        
      case 'health':
        return await cmdHealth(args[1]);
        
      case 'profiles':
        return await cmdProfiles();
        
      case 'test':
        return await cmdTest(args[1], args[2], args[3]);
        
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
