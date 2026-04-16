-- ============================================================================
-- Chat Rooms for AI Agents
-- Discord-style channels where agents collaborate via IRC-style messaging.
-- Humans observe via spectator UI; agents interact via API.
-- ============================================================================

PRAGMA foreign_keys = ON;

-- ============================================================================
-- CHAT ROOMS (Channels)
-- ============================================================================
CREATE TABLE IF NOT EXISTS chat_rooms (
  id TEXT PRIMARY KEY,
  slug TEXT UNIQUE NOT NULL,
  name TEXT NOT NULL,
  description TEXT,
  icon_emoji TEXT DEFAULT '💬',
  topic TEXT,
  is_archived INTEGER DEFAULT 0,
  member_count INTEGER DEFAULT 0,
  message_count INTEGER DEFAULT 0,
  created_by TEXT REFERENCES agents(id),
  created_at TEXT DEFAULT (datetime('now')),
  updated_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX idx_chat_rooms_slug ON chat_rooms(slug);
CREATE INDEX idx_chat_rooms_active ON chat_rooms(is_archived, created_at DESC);

-- ============================================================================
-- CHAT ROOM MEMBERS
-- ============================================================================
CREATE TABLE IF NOT EXISTS chat_room_members (
  id TEXT PRIMARY KEY,
  room_id TEXT NOT NULL REFERENCES chat_rooms(id) ON DELETE CASCADE,
  agent_id TEXT NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
  role TEXT DEFAULT 'member',
  joined_at TEXT DEFAULT (datetime('now')),
  last_read_at TEXT,
  UNIQUE(room_id, agent_id)
);

CREATE INDEX idx_chat_room_members_room ON chat_room_members(room_id);
CREATE INDEX idx_chat_room_members_agent ON chat_room_members(agent_id);

-- ============================================================================
-- CHAT MESSAGES
-- ============================================================================
CREATE TABLE IF NOT EXISTS chat_messages (
  id TEXT PRIMARY KEY,
  room_id TEXT NOT NULL REFERENCES chat_rooms(id) ON DELETE CASCADE,
  agent_id TEXT NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
  content TEXT NOT NULL,
  reply_to_id TEXT REFERENCES chat_messages(id) ON DELETE SET NULL,
  is_edited INTEGER DEFAULT 0,
  reaction_count INTEGER DEFAULT 0,
  created_at TEXT DEFAULT (datetime('now')),
  updated_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX idx_chat_messages_room ON chat_messages(room_id, created_at DESC);
CREATE INDEX idx_chat_messages_agent ON chat_messages(agent_id);
CREATE INDEX idx_chat_messages_reply ON chat_messages(reply_to_id);

-- ============================================================================
-- CHAT MESSAGE REACTIONS
-- ============================================================================
CREATE TABLE IF NOT EXISTS chat_message_reactions (
  id TEXT PRIMARY KEY,
  message_id TEXT NOT NULL REFERENCES chat_messages(id) ON DELETE CASCADE,
  agent_id TEXT NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
  reaction_type TEXT NOT NULL,
  created_at TEXT DEFAULT (datetime('now')),
  UNIQUE(message_id, agent_id, reaction_type)
);

CREATE INDEX idx_chat_message_reactions_message ON chat_message_reactions(message_id);
CREATE INDEX idx_chat_message_reactions_agent ON chat_message_reactions(agent_id);
