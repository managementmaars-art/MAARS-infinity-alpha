/**
 * Slack Auth Skill
 * Slack OAuth and bot token management for team communication
 * Built on top of auth-provider for secure token storage
 */

import { AuthProvider, getAuthProvider, TokenData, SlackMetadata } from '@openclaw/auth-provider';

// Re-export auth provider for advanced users
export { AuthProvider, getAuthProvider };

/**
 * Slack API response types
 */
export interface SlackApiResponse {
  ok: boolean;
  error?: string;
}

export interface SlackAuthTestResponse extends SlackApiResponse {
  url?: string;
  team?: string;
  user?: string;
  team_id?: string;
  user_id?: string;
}

export interface SlackChannel {
  id: string;
  name: string;
  is_channel: boolean;
  is_group: boolean;
  is_im: boolean;
  created: number;
  creator: string;
  is_archived: boolean;
  is_general: boolean;
  unlinked: number;
  name_normalized: string;
  is_shared: boolean;
  is_ext_shared: boolean;
  is_org_shared: boolean;
  pending_shared: string[];
  is_pending_ext_shared: boolean;
  is_member: boolean;
  is_private: boolean;
  is_mpim: boolean;
  topic: { value: string; creator: string; last_set: number };
  purpose: { value: string; creator: string; last_set: number };
  previous_names: string[];
  num_members: number;
}

export interface SlackConversationsListResponse extends SlackApiResponse {
  channels?: SlackChannel[];
  response_metadata?: { next_cursor: string };
}

export interface SlackPostMessageResponse extends SlackApiResponse {
  channel?: string;
  ts?: string;
  message?: {
    type: string;
    user: string;
    text: string;
    ts: string;
  };
}

export interface SlackTeamInfo {
  id: string;
  name: string;
  domain: string;
  email_domain?: string;
  icon?: {
    image_132?: string;
  };
}

export interface SlackTeamInfoResponse extends SlackApiResponse {
  team?: SlackTeamInfo;
}

/**
 * Result of Slack OAuth authentication
 */
export interface SlackAuthResult {
  success: boolean;
  team?: string;
  teamId?: string;
  user?: string;
  userId?: string;
  scopes?: string[];
  error?: string;
}

/**
 * Workspace information
 */
export interface SlackWorkspaceInfo {
  team: string;
  teamId: string;
  user: string;
  userId: string;
  url: string;
}

/**
 * Validation result for Slack token
 */
export interface SlackValidationResult {
  valid: boolean;
  permissions: string[];
  team?: string;
  user?: string;
}

/**
 * Health check result
 */
export interface SlackHealthResult {
  status: 'healthy' | 'unhealthy';
  message?: string;
  profile: string;
}

/**
 * Slack Auth Client for a specific profile
 */
export class SlackAuthClient {
  private auth: AuthProvider;
  private profile: string;
  
  constructor(profile: string = 'default', auth?: AuthProvider) {
    this.auth = auth || getAuthProvider();
    this.profile = profile;
  }
  
  /**
   * Create a client for a specific profile (static factory)
   */
  static forProfile(profile: string = 'default', auth?: AuthProvider): SlackAuthClient {
    return new SlackAuthClient(profile, auth);
  }
  
  /**
   * Initiate OAuth flow and return authorization URL
   */
  initiateAuth(): {
    url: string;
    state: string;
  } {
    const result = this.auth.initiateAuth('slack', this.profile);
    
    return {
      url: result.url,
      state: result.state,
    };
  }
  
  /**
   * Complete OAuth flow with authorization code
   */
  async completeAuth(code: string, state: string): Promise<SlackAuthResult> {
    try {
      const tokenData = await this.auth.completeAuth('slack', code, state);
      
      // Extract metadata
      const metadata = tokenData.metadata as SlackMetadata | undefined;
      
      return {
        success: true,
        team: metadata?.team,
        teamId: metadata?.teamId,
        user: metadata?.user,
        userId: metadata?.userId,
        scopes: tokenData.scope?.split(',') || [],
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : String(error),
      };
    }
  }
  
  /**
   * Check if this profile is connected (has valid tokens)
   */
  async isConnected(): Promise<boolean> {
    const token = await this.auth.getToken('slack', this.profile);
    return token !== null;
  }
  
  /**
   * Get a valid access token
   */
  async getAccessToken(): Promise<string | null> {
    const token = await this.auth.getValidAccessToken('slack', this.profile);
    return token || null;
  }
  
  /**
   * Get stored token data
   */
  async getTokenData(): Promise<TokenData | null> {
    const token = await this.auth.getToken('slack', this.profile);
    return token || null;
  }
  
  /**
   * Get workspace information
   */
  async getWorkspaceInfo(): Promise<SlackWorkspaceInfo | null> {
    const token = await this.getAccessToken();
    if (!token) {
      return null;
    }
    
    try {
      const response = await fetch('https://slack.com/api/auth.test', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });
      
      if (!response.ok) {
        return null;
      }
      
      const data = await response.json() as SlackAuthTestResponse;
      
      if (!data.ok) {
        return null;
      }
      
      return {
        team: data.team || '',
        teamId: data.team_id || '',
        user: data.user || '',
        userId: data.user_id || '',
        url: data.url || '',
      };
    } catch {
      return null;
    }
  }
  
  /**
   * Get team info with details
   */
  async getTeamInfo(): Promise<SlackTeamInfo | null> {
    const token = await this.getAccessToken();
    if (!token) {
      return null;
    }
    
    try {
      const response = await fetch('https://slack.com/api/team.info', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });
      
      if (!response.ok) {
        return null;
      }
      
      const data = await response.json() as SlackTeamInfoResponse;
      
      if (!data.ok || !data.team) {
        return null;
      }
      
      return data.team;
    } catch {
      return null;
    }
  }
  
  /**
   * Get connected scopes
   */
  async getConnectedScopes(): Promise<string[]> {
    const token = await this.getTokenData();
    return token?.scope?.split(',') || [];
  }
  
  /**
   * Validate token permissions
   */
  async validatePermissions(): Promise<SlackValidationResult> {
    const token = await this.getAccessToken();
    
    if (!token) {
      return {
        valid: false,
        permissions: [],
      };
    }
    
    try {
      const response = await fetch('https://slack.com/api/auth.test', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });
      
      if (!response.ok) {
        return {
          valid: false,
          permissions: [],
        };
      }
      
      const data = await response.json() as SlackAuthTestResponse;
      const scopes = await this.getConnectedScopes();
      
      return {
        valid: data.ok,
        permissions: scopes,
        team: data.team,
        user: data.user,
      };
    } catch {
      return {
        valid: false,
        permissions: [],
      };
    }
  }
  
  /**
   * Perform health check on this connection
   */
  async healthCheck(): Promise<SlackHealthResult> {
    const result = await this.auth.healthCheck('slack', this.profile);
    return {
      status: result.status,
      message: result.message || '',
      profile: this.profile,
    };
  }
  
  /**
   * Disconnect (delete stored tokens)
   */
  async disconnect(): Promise<boolean> {
    return this.auth.deleteCredentials('slack', this.profile);
  }
  
  /**
   * Send a message to a channel
   */
  async sendMessage(channel: string, text: string): Promise<SlackPostMessageResponse> {
    const token = await this.getAccessToken();
    if (!token) {
      return { ok: false, error: 'not_authenticated' };
    }
    
    const response = await fetch('https://slack.com/api/chat.postMessage', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        channel,
        text,
      }),
    });
    
    if (!response.ok) {
      return { ok: false, error: `HTTP ${response.status}` };
    }
    
    return response.json() as Promise<SlackPostMessageResponse>;
  }
  
  /**
   * List channels in the workspace
   */
  async listChannels(types: string = 'public_channel,private_channel'): Promise<SlackChannel[]> {
    const token = await this.getAccessToken();
    if (!token) {
      return [];
    }
    
    const params = new URLSearchParams({
      types,
      limit: '100',
    });
    
    const response = await fetch(`https://slack.com/api/conversations.list?${params.toString()}`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    
    if (!response.ok) {
      return [];
    }
    
    const data = await response.json() as SlackConversationsListResponse;
    
    if (!data.ok) {
      return [];
    }
    
    return data.channels || [];
  }
  
  /**
   * Make an authenticated request to Slack API
   */
  async fetch(url: string, options: RequestInit = {}): Promise<Response> {
    const accessToken = await this.getAccessToken();
    if (!accessToken) {
      throw new Error('Not authenticated. Please connect your Slack workspace first.');
    }
    
    const headers = new Headers(options.headers);
    headers.set('Authorization', `Bearer ${accessToken}`);
    
    return fetch(url, {
      ...options,
      headers,
    });
  }
}

// Singleton instance cache
const clientCache: Map<string, SlackAuthClient> = new Map();

/**
 * Get Slack auth client for a profile (singleton pattern)
 */
export function getSlackAuth(profile: string = 'default'): SlackAuthClient {
  if (!clientCache.has(profile)) {
    clientCache.set(profile, new SlackAuthClient(profile));
  }
  return clientCache.get(profile)!;
}

/**
 * Get all connected Slack profiles
 */
export async function getConnectedProfiles(auth?: AuthProvider): Promise<string[]> {
  const provider = auth || getAuthProvider();
  return provider.listProfiles('slack');
}

/**
 * Check if any Slack workspace is connected
 */
export async function hasAnyConnection(auth?: AuthProvider): Promise<boolean> {
  const profiles = await getConnectedProfiles(auth);
  return profiles.length > 0;
}

/**
 * Disconnect all Slack workspaces
 */
export async function disconnectAll(auth?: AuthProvider): Promise<number> {
  const provider = auth || getAuthProvider();
  const profiles = await getConnectedProfiles(provider);
  let count = 0;
  
  for (const profile of profiles) {
    if (await provider.deleteCredentials('slack', profile)) {
      count++;
      // Remove from cache
      clientCache.delete(profile);
    }
  }
  
  return count;
}

/**
 * Health check all Slack connections
 */
export async function healthCheckAll(auth?: AuthProvider): Promise<SlackHealthResult[]> {
  const provider = auth || getAuthProvider();
  const results = await provider.healthCheckAll();
  
  return results
    .filter(r => r.provider === 'slack')
    .map(r => ({
      status: r.status,
      message: r.message || '',
      profile: r.profile,
    }));
}

// Default export
export default SlackAuthClient;
