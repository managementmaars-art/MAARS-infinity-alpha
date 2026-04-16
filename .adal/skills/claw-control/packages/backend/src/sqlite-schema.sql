-- SQLite Schema for Claw Control
-- This schema mirrors the PostgreSQL schema but uses SQLite-compatible syntax

-- Create agents table
CREATE TABLE IF NOT EXISTS agents (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL UNIQUE,
  description TEXT,
  status TEXT DEFAULT 'idle',
  role TEXT DEFAULT 'Agent',
  created_at TEXT DEFAULT (datetime('now'))
);

-- Create tasks table
CREATE TABLE IF NOT EXISTS tasks (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  description TEXT,
  status TEXT DEFAULT 'backlog',
  tags TEXT DEFAULT '[]',  -- JSON array stored as text
  agent_id INTEGER REFERENCES agents(id) ON DELETE SET NULL,
  created_at TEXT DEFAULT (datetime('now')),
  updated_at TEXT DEFAULT (datetime('now'))
);

-- Create agent_messages table
CREATE TABLE IF NOT EXISTS agent_messages (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  agent_id INTEGER REFERENCES agents(id) ON DELETE CASCADE,
  message TEXT NOT NULL,
  created_at TEXT DEFAULT (datetime('now'))
);

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_agent_id ON tasks(agent_id);
CREATE INDEX IF NOT EXISTS idx_messages_agent_id ON agent_messages(agent_id);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON agent_messages(created_at);
CREATE UNIQUE INDEX IF NOT EXISTS idx_agents_name ON agents(name);
