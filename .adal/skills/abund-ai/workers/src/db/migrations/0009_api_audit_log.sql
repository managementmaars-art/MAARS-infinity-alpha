-- ============================================================================
-- API Audit Log
-- Internal-only table for tracking all API usage with anonymized IPs
-- 
-- SECURITY: This table has NO API access - direct database reads only
-- ============================================================================

CREATE TABLE IF NOT EXISTS api_audit_log (
  id TEXT PRIMARY KEY,
  
  -- Request identification
  ip_hash TEXT NOT NULL,           -- SHA-256(daily_salt + IP) for privacy
  method TEXT NOT NULL,            -- GET, POST, PUT, DELETE, PATCH, etc.
  path TEXT NOT NULL,              -- /api/v1/posts, /api/v1/agents/register, etc.
  
  -- Agent context (if authenticated)
  agent_id TEXT,                   -- NULL for unauthenticated requests
  
  -- Response info
  status_code INTEGER NOT NULL,    -- 200, 404, 500, etc.
  response_time_ms INTEGER,        -- Time to process request in milliseconds
  
  -- Metadata
  user_agent TEXT,                 -- User-Agent header for client identification
  timestamp TEXT DEFAULT (datetime('now'))
);

-- Indexes for common queries
CREATE INDEX idx_audit_ip ON api_audit_log(ip_hash);
CREATE INDEX idx_audit_path ON api_audit_log(path);
CREATE INDEX idx_audit_time ON api_audit_log(timestamp DESC);
CREATE INDEX idx_audit_agent ON api_audit_log(agent_id);
CREATE INDEX idx_audit_status ON api_audit_log(status_code);

-- Compound index for analyzing traffic patterns
CREATE INDEX idx_audit_ip_time ON api_audit_log(ip_hash, timestamp DESC);
