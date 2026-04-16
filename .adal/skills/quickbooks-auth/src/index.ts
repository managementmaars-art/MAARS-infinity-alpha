/**
 * QuickBooks OAuth Skill
 * Simplified QuickBooks OAuth interface built on top of auth-provider
 * Provides easy access to QuickBooks Online accounting API
 */

import { AuthProvider, getAuthProvider, TokenData } from '@openclaw/auth-provider';

// Re-export auth provider for advanced users
export { AuthProvider, getAuthProvider };

/**
 * QuickBooks environments
 */
export type QuickBooksEnvironment = 'production' | 'sandbox';

/**
 * QuickBooks scopes
 */
export const QuickBooksScopes = {
  /** Accounting - Access to company data, invoices, customers, etc. */
  ACCOUNTING: 'com.intuit.quickbooks.accounting',
  /** Payment - Process payments (separate approval required) */
  PAYMENT: 'com.intuit.quickbooks.payment',
  /** Payroll - Access payroll data (separate approval required) */
  PAYROLL: 'com.intuit.quickbooks.payroll',
} as const;

/**
 * Result of QuickBooks OAuth authentication
 */
export interface QuickBooksAuthResult {
  success: boolean;
  realmId?: string;
  companyName?: string;
  environment?: QuickBooksEnvironment;
  scopes?: string[];
  expiresAt?: number;
  error?: string;
}

/**
 * QuickBooks company info
 */
export interface QuickBooksCompanyInfo {
  companyName: string;
  legalName?: string;
  email?: string;
  phone?: string;
  country?: string;
}

/**
 * QuickBooks OAuth client for a specific profile
 */
export class QuickBooksAuthClient {
  private auth: AuthProvider;
  private profile: string;
  private environment: QuickBooksEnvironment;
  
  constructor(
    profile: string = 'default', 
    environment: QuickBooksEnvironment = 'sandbox',
    auth?: AuthProvider
  ) {
    this.auth = auth || getAuthProvider();
    this.profile = profile;
    this.environment = environment;
  }
  
  /**
   * Create a client for a specific profile (static factory)
   */
  static forProfile(
    profile: string = 'default',
    environment: QuickBooksEnvironment = 'sandbox',
    auth?: AuthProvider
  ): QuickBooksAuthClient {
    return new QuickBooksAuthClient(profile, environment, auth);
  }
  
  /**
   * Initiate OAuth flow and return authorization URL
   */
  initiateAuth(): {
    url: string;
    state: string;
    scopes: string[];
  } {
    const scopes = [QuickBooksScopes.ACCOUNTING];
    const adapter = this.auth.getAdapter('quickbooks');
    
    if (!adapter) {
      throw new Error('QuickBooks adapter not found. Ensure QUICKBOOKS_CLIENT_ID and QUICKBOOKS_CLIENT_SECRET are set in environment.');
    }
    
    const result = adapter.generateAuthUrl(this.profile, scopes);
    
    return {
      url: result.url,
      state: result.state,
      scopes,
    };
  }
  
  /**
   * Complete OAuth flow with authorization code
   * Note: realmId is provided in the callback URL by QuickBooks
   */
  async completeAuth(code: string, state: string, realmId: string): Promise<QuickBooksAuthResult> {
    try {
      // Store realmId in metadata for later use
      const tokenData = await this.auth.completeAuth('quickbooks', code, state, {
        realmId,
        environment: this.environment,
      });
      
      return {
        success: true,
        realmId,
        environment: this.environment,
        scopes: tokenData.scope?.split(' ') || [QuickBooksScopes.ACCOUNTING],
        expiresAt: tokenData.expires_at,
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
    const token = await this.auth.getToken('quickbooks', this.profile);
    return token !== undefined;
  }
  
  /**
   * Get a valid access token (auto-refreshes if needed)
   */
  async getAccessToken(): Promise<string | null> {
    const token = await this.auth.getValidAccessToken('quickbooks', this.profile);
    return token || null;
  }
  
  /**
   * Get stored token data
   */
  async getTokenData(): Promise<TokenData | null> {
    const token = await this.auth.getToken('quickbooks', this.profile);
    return token || null;
  }
  
  /**
   * Get the Realm ID for this connection
   */
  async getRealmId(): Promise<string | null> {
    const token = await this.getTokenData();
    return token?.metadata?.realmId || null;
  }
  
  /**
   * Get the environment (production or sandbox)
   */
  async getEnvironment(): Promise<QuickBooksEnvironment> {
    const token = await this.getTokenData();
    return token?.metadata?.environment || this.environment;
  }
  
  /**
   * Perform health check on this connection
   */
  async healthCheck(): Promise<{
    status: 'healthy' | 'unhealthy';
    message?: string;
    expiresAt?: number;
    realmId?: string;
  }> {
    const result = await this.auth.healthCheck('quickbooks', this.profile);
    const realmId = await this.getRealmId();
    
    return {
      status: result.status,
      message: result.message,
      expiresAt: result.expires_at,
      realmId: realmId || undefined,
    };
  }
  
  /**
   * Disconnect (delete stored tokens)
   */
  async disconnect(): Promise<boolean> {
    return this.auth.deleteCredentials('quickbooks', this.profile);
  }
  
  /**
   * Get the base URL for API calls based on environment
   */
  async getApiBaseUrl(): Promise<string> {
    const env = await this.getEnvironment();
    return env === 'production'
      ? 'https://quickbooks.api.intuit.com/v3/company'
      : 'https://sandbox-quickbooks.api.intuit.com/v3/company';
  }
  
  /**
   * Make an authenticated request to QuickBooks API
   */
  async fetch(endpoint: string, options: RequestInit = {}): Promise<Response> {
    const accessToken = await this.getAccessToken();
    if (!accessToken) {
      throw new Error('Not authenticated. Please connect your QuickBooks account first.');
    }
    
    const realmId = await this.getRealmId();
    if (!realmId) {
      throw new Error('Realm ID not found. Please reconnect your QuickBooks account.');
    }
    
    const baseUrl = await this.getApiBaseUrl();
    const url = endpoint.startsWith('http') 
      ? endpoint 
      : `${baseUrl}/${realmId}${endpoint.startsWith('/') ? endpoint : '/' + endpoint}`;
    
    const headers = new Headers(options.headers);
    headers.set('Authorization', `Bearer ${accessToken}`);
    headers.set('Accept', 'application/json');
    
    return fetch(url, {
      ...options,
      headers,
    });
  }
}

/**
 * Get all connected QuickBooks profiles
 */
export async function getConnectedProfiles(auth?: AuthProvider): Promise<string[]> {
  const provider = auth || getAuthProvider();
  return provider.listProfiles('quickbooks');
}

/**
 * Check if any QuickBooks account is connected
 */
export async function hasAnyConnection(auth?: AuthProvider): Promise<boolean> {
  const profiles = await getConnectedProfiles(auth);
  return profiles.length > 0;
}

/**
 * Disconnect all QuickBooks accounts
 */
export async function disconnectAll(auth?: AuthProvider): Promise<number> {
  const provider = auth || getAuthProvider();
  const profiles = await getConnectedProfiles(provider);
  let count = 0;
  
  for (const profile of profiles) {
    if (await provider.deleteCredentials('quickbooks', profile)) {
      count++;
    }
  }
  
  return count;
}

/**
 * Health check all QuickBooks connections
 */
export async function healthCheckAll(auth?: AuthProvider): Promise<
  Array<{
    profile: string;
    status: 'healthy' | 'unhealthy';
    message?: string;
    expiresAt?: number;
    realmId?: string;
  }>
> {
  const provider = auth || getAuthProvider();
  const results = await provider.healthCheckAll();
  
  // Get realm IDs for all profiles
  const profiles = await getConnectedProfiles(provider);
  const realmIdMap: Record<string, string> = {};
  
  for (const profile of profiles) {
    const client = QuickBooksAuthClient.forProfile(profile, 'sandbox', provider);
    const realmId = await client.getRealmId();
    if (realmId) {
      realmIdMap[profile] = realmId;
    }
  }
  
  return results
    .filter(r => r.provider === 'quickbooks')
    .map(r => ({
      profile: r.profile,
      status: r.status,
      message: r.message,
      expiresAt: r.expires_at,
      realmId: realmIdMap[r.profile],
    }));
}

// Default export
export default QuickBooksAuthClient;
