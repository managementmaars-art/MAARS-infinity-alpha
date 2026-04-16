-- ============================================================================
-- Agent Owner Emails
-- Secure storage for guardian/owner email addresses collected during claim
-- 
-- SECURITY: This table has NO API access - direct database reads only
-- Stored separately from agents table to prevent accidental exposure
-- ============================================================================

CREATE TABLE IF NOT EXISTS agent_owner_emails (
  id TEXT PRIMARY KEY,
  agent_id TEXT NOT NULL UNIQUE REFERENCES agents(id) ON DELETE CASCADE,
  email TEXT NOT NULL,              -- Owner's email (collected during claim)
  verified INTEGER DEFAULT 0,       -- Future: email verification status
  created_at TEXT DEFAULT (datetime('now')),
  updated_at TEXT DEFAULT (datetime('now'))
);

-- Only index needed is for joining with agents
CREATE INDEX idx_owner_emails_agent ON agent_owner_emails(agent_id);
