/**
 * Cryptographic utilities for secure API key handling
 *
 * Security principles:
 * 1. Never store API keys in plaintext - always hash
 * 2. Use constant-time comparison to prevent timing attacks
 * 3. Generate cryptographically secure random keys
 */

/**
 * Generate a cryptographically secure API key
 * Format: abund_<32 random hex chars>
 *
 * @example
 * const key = generateApiKey()
 * // Returns: "abund_a1b2c3d4e5f6..."
 */
export function generateApiKey(): string {
  const randomBytes = crypto.getRandomValues(new Uint8Array(16))
  const hex = Array.from(randomBytes)
    .map((b) => b.toString(16).padStart(2, '0'))
    .join('')
  return `abund_${hex}`
}

/**
 * Extract the prefix from an API key for identification
 * This is safely stored and used for key lookup
 *
 * @example
 * getKeyPrefix("abund_a1b2c3d4e5f6...")
 * // Returns: "abund_a1"
 */
export function getKeyPrefix(apiKey: string): string {
  return apiKey.slice(0, 9) // "abund_" + first 3 chars
}

/**
 * Hash an API key using SHA-256
 * The hash is what we store in the database, never the plaintext
 *
 * @example
 * const hash = await hashApiKey("abund_a1b2c3d4...")
 * // Returns: "5e884898da28047d..."
 */
export async function hashApiKey(apiKey: string): Promise<string> {
  const encoder = new TextEncoder()
  const data = encoder.encode(apiKey)
  const hashBuffer = await crypto.subtle.digest('SHA-256', data)
  const hashArray = Array.from(new Uint8Array(hashBuffer))
  return hashArray.map((b) => b.toString(16).padStart(2, '0')).join('')
}

/**
 * Constant-time string comparison to prevent timing attacks
 *
 * Regular string comparison (a === b) can leak information about
 * how many characters matched before failure. This function always
 * takes the same amount of time regardless of where strings differ.
 *
 * @example
 * constantTimeCompare("abc", "abc") // true
 * constantTimeCompare("abc", "abd") // false (same time as above)
 */
export function constantTimeCompare(a: string, b: string): boolean {
  if (a.length !== b.length) {
    // Still do a fake comparison to maintain constant time
    // even when lengths differ. XOR against b (wrapped) to prevent
    // the optimizer from eliding the loop as a no-op.
    let _result = 0
    for (let i = 0; i < a.length; i++) {
      _result |= a.charCodeAt(i) ^ b.charCodeAt(i % b.length)
    }
    void _result // Prevent unused variable warning
    return false
  }

  let result = 0
  for (let i = 0; i < a.length; i++) {
    result |= a.charCodeAt(i) ^ b.charCodeAt(i)
  }
  return result === 0
}

/**
 * Verify an API key against a stored hash
 * Combines hashing with constant-time comparison
 *
 * @example
 * const isValid = await verifyApiKey("abund_...", storedHash)
 */
export async function verifyApiKey(
  providedKey: string,
  storedHash: string
): Promise<boolean> {
  const providedHash = await hashApiKey(providedKey)
  return constantTimeCompare(providedHash, storedHash)
}

/**
 * Generate a secure random ID (for posts, comments, etc.)
 * Uses UUID v4 format
 */
export function generateId(): string {
  return crypto.randomUUID()
}

/**
 * Generate a claim code for agent verification
 * Shorter format for easier human entry
 */
export function generateClaimCode(): string {
  // 16 bytes = 128 bits of entropy to prevent brute-force
  const randomBytes = crypto.getRandomValues(new Uint8Array(16))
  const hex = Array.from(randomBytes)
    .map((b) => b.toString(16).padStart(2, '0'))
    .join('')
  return hex.toUpperCase()
}

// =============================================================================
// Privacy-Preserving Analytics
// =============================================================================

/**
 * Generate a daily rotating salt for privacy-preserving hashing
 * This ensures the same IP produces different hashes on different days,
 * preventing long-term tracking while still detecting unique views per day.
 */
export function getDailySalt(): string {
  const today = new Date().toISOString().split('T')[0] // YYYY-MM-DD
  return `abund_view_salt_${today}`
}

/**
 * Hash a viewer's IP address with a daily salt for privacy-preserving analytics.
 *
 * SECURITY: The IP address is NEVER stored. Only this one-way hash is recorded.
 * The daily rotating salt means:
 * - Same IP = different hash each day (no long-term tracking)
 * - Same IP on same day = same hash (detect unique views)
 *
 * @param ipAddress - The viewer's IP address (will NOT be stored)
 * @returns A SHA-256 hash that can be safely stored
 */
export async function hashViewerIdentity(ipAddress: string): Promise<string> {
  const salt = getDailySalt()
  const data = `${salt}:${ipAddress}`
  const encoder = new TextEncoder()
  const hashBuffer = await crypto.subtle.digest('SHA-256', encoder.encode(data))
  const hashArray = Array.from(new Uint8Array(hashBuffer))
  return hashArray.map((b) => b.toString(16).padStart(2, '0')).join('')
}
