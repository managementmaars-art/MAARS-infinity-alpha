-- ============================================================================
-- Add rate_limit_bypass flag to api_keys
-- Allows specific API keys to bypass rate limiting (admin/trusted keys)
--
-- Enable bypass for a key:
--   UPDATE api_keys SET rate_limit_bypass = 1 WHERE key_prefix = 'XXXX';
--
-- NOTE: This column already exists in 0001_initial_schema.sql.
-- This migration exists for databases created before the initial schema
-- was updated. It is now a no-op for fresh installs.
-- ============================================================================

-- No-op: column already exists in initial schema
SELECT 1;
