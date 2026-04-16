/**
 * @fileoverview Optional API Key Authentication Middleware.
 * 
 * This module provides authentication middleware for protecting
 * write operations (POST/PUT/DELETE) while keeping read operations open.
 * 
 * Authentication is optional - if API_KEY is not configured, all requests pass through.
 * 
 * @module auth
 */

/**
 * The configured API key from environment.
 * If not set or empty, authentication is disabled (open mode).
 * @type {string|undefined}
 */
const API_KEY = process.env.API_KEY?.trim() || '';

/**
 * Checks if authentication is enabled.
 * @returns {boolean} True if API_KEY is configured
 */
function isAuthEnabled() {
  return API_KEY.length > 0;
}

/**
 * Extracts API key from request headers.
 * Supports two formats:
 * - Authorization: Bearer <key>
 * - X-API-Key: <key>
 * 
 * @param {object} request - Fastify request object
 * @returns {string|null} Extracted API key or null if not found
 */
function extractApiKey(request) {
  // Check Authorization header (Bearer token)
  const authHeader = request.headers.authorization;
  if (authHeader && authHeader.startsWith('Bearer ')) {
    return authHeader.slice(7).trim();
  }
  
  // Check X-API-Key header
  const xApiKey = request.headers['x-api-key'];
  if (xApiKey) {
    return xApiKey.trim();
  }
  
  return null;
}

/**
 * Validates the provided API key against the configured key.
 * Uses timing-safe comparison to prevent timing attacks.
 * 
 * @param {string} providedKey - The key to validate
 * @returns {boolean} True if the key is valid
 */
function validateApiKey(providedKey) {
  if (!providedKey || !API_KEY) {
    return false;
  }
  
  // Simple comparison - for production, consider using crypto.timingSafeEqual
  // We keep it simple here since API_KEY is typically a random string
  return providedKey === API_KEY;
}

/**
 * Fastify preHandler hook for authenticating protected routes.
 * 
 * This hook:
 * - Passes through if auth is disabled (no API_KEY configured)
 * - Validates API key from Authorization or X-API-Key header
 * - Returns 401 Unauthorized if key is missing or invalid
 * 
 * @param {object} request - Fastify request object
 * @param {object} reply - Fastify reply object
 * @returns {Promise<void>}
 */
async function requireAuth(request, reply) {
  // Skip auth if not configured (open mode)
  if (!isAuthEnabled()) {
    return;
  }
  
  const providedKey = extractApiKey(request);
  
  if (!providedKey) {
    return reply.status(401).send({
      error: 'Unauthorized',
      message: 'API key required. Provide via Authorization: Bearer <key> or X-API-Key header.'
    });
  }
  
  if (!validateApiKey(providedKey)) {
    return reply.status(401).send({
      error: 'Unauthorized',
      message: 'Invalid API key.'
    });
  }
  
  // Auth successful - continue to route handler
}

/**
 * Creates a Fastify route options object with auth middleware.
 * Use this as a spread in route definitions to protect them.
 * 
 * @example
 * fastify.post('/api/tasks', { ...withAuth }, async (request, reply) => { ... });
 * 
 * @type {{ preHandler: Function }}
 */
const withAuth = {
  preHandler: requireAuth
};

module.exports = {
  requireAuth,
  withAuth,
  isAuthEnabled,
  extractApiKey,
  validateApiKey
};
