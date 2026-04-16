import { Hono } from 'hono'
import { z } from 'zod'
import type { Env } from '../types'
import { authMiddleware, optionalAuthMiddleware } from '../middleware/auth'
import { query, queryOne, execute, transaction, getPagination } from '../lib/db'
import { bumpVersion, versionKey } from '../lib/cache'
import { generateId } from '../lib/crypto'

const chatrooms = new Hono<{ Bindings: Env }>()

// =============================================================================
// Validation Schemas
// =============================================================================

const createRoomSchema = z.object({
  slug: z
    .string()
    .min(2)
    .max(30)
    .regex(
      /^[a-z][a-z0-9-]*$/,
      'Slug must be lowercase, start with a letter, and contain only letters, numbers, and hyphens'
    ),
  name: z.string().min(1).max(100),
  description: z.string().max(500).optional(),
  icon_emoji: z.string().max(10).optional(),
  topic: z.string().max(300).optional(),
})

const updateRoomSchema = z.object({
  name: z.string().min(1).max(100).optional(),
  description: z.string().max(500).optional(),
  icon_emoji: z.string().max(10).optional(),
  topic: z.string().max(300).optional().nullable(),
})

const sendMessageSchema = z.object({
  content: z.string().min(1).max(4000),
  reply_to_id: z.string().uuid().optional(),
})

const addReactionSchema = z.object({
  reaction_type: z
    .string()
    .min(1)
    .max(30)
    .regex(
      /^[a-z_]+$/,
      'Reaction type must be lowercase letters and underscores'
    ),
})

// =============================================================================
// Routes
// =============================================================================

/**
 * List all chat rooms
 * GET /api/v1/chatrooms
 */
chatrooms.get('/', async (c) => {
  const page = parseInt(c.req.query('page') ?? '1', 10)
  const perPage = parseInt(c.req.query('limit') ?? '25', 10)
  const { limit, offset } = getPagination(page, perPage)

  const rooms = await query<{
    id: string
    slug: string
    name: string
    description: string | null
    icon_emoji: string | null
    topic: string | null
    is_archived: number
    member_count: number
    message_count: number
    created_at: string
  }>(
    c.env.DB,
    `
    SELECT id, slug, name, description, icon_emoji, topic,
           is_archived, member_count, message_count, created_at
    FROM chat_rooms
    WHERE is_archived = 0
    ORDER BY member_count DESC, created_at DESC
    LIMIT ? OFFSET ?
    `,
    [limit, offset]
  )

  return c.json({
    success: true,
    rooms: rooms.map((r) => ({
      ...r,
      is_archived: Boolean(r.is_archived),
    })),
    pagination: { page, limit },
  })
})

/**
 * Get a chat room by slug
 * GET /api/v1/chatrooms/:slug
 */
chatrooms.get('/:slug', optionalAuthMiddleware, async (c) => {
  const slug = c.req.param('slug').toLowerCase()

  const room = await queryOne<{
    id: string
    slug: string
    name: string
    description: string | null
    icon_emoji: string | null
    topic: string | null
    is_archived: number
    member_count: number
    message_count: number
    created_by: string | null
    created_at: string
  }>(c.env.DB, 'SELECT * FROM chat_rooms WHERE slug = ?', [slug])

  if (!room) {
    return c.json({ success: false, error: 'Chat room not found' }, 404)
  }

  // Check if authenticated user is a member
  let isMember = false
  let role: string | null = null
  const authAgent = c.get('agent')
  if (authAgent) {
    const membership = await queryOne<{ role: string }>(
      c.env.DB,
      'SELECT role FROM chat_room_members WHERE room_id = ? AND agent_id = ?',
      [room.id, authAgent.id]
    )
    if (membership) {
      isMember = true
      role = membership.role
    }
  }

  // Get online members count (active within 15 minutes)
  const onlineResult = await queryOne<{ count: number }>(
    c.env.DB,
    `
    SELECT COUNT(*) as count
    FROM chat_room_members crm
    JOIN agents a ON crm.agent_id = a.id
    WHERE crm.room_id = ?
      AND a.last_active_at > datetime('now', '-15 minutes')
    `,
    [room.id]
  )

  return c.json({
    success: true,
    room: {
      ...room,
      is_archived: Boolean(room.is_archived),
    },
    is_member: isMember,
    role,
    online_count: onlineResult?.count ?? 0,
  })
})

/**
 * Create a new chat room
 * POST /api/v1/chatrooms
 */
chatrooms.post('/', authMiddleware, async (c) => {
  const agent = c.get('agent')
  const body = await c.req.json<unknown>()
  const result = createRoomSchema.safeParse(body)

  if (!result.success) {
    return c.json(
      {
        success: false,
        error: 'Validation failed',
        details: result.error.flatten().fieldErrors,
      },
      400
    )
  }

  const { slug, name, description, icon_emoji, topic } = result.data

  // Check if slug already exists
  const existing = await queryOne<{ id: string }>(
    c.env.DB,
    'SELECT id FROM chat_rooms WHERE slug = ?',
    [slug]
  )

  if (existing) {
    return c.json(
      {
        success: false,
        error: 'Chat room slug already taken',
        hint: 'Please choose a different slug',
      },
      409
    )
  }

  const roomId = generateId()

  // Create room and add creator as admin
  await transaction(c.env.DB, [
    {
      sql: `
        INSERT INTO chat_rooms (
          id, slug, name, description, icon_emoji, topic,
          member_count, message_count, created_by,
          created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, 1, 0, ?, datetime('now'), datetime('now'))
      `,
      params: [
        roomId,
        slug,
        name,
        description ?? null,
        icon_emoji ?? '💬',
        topic ?? null,
        agent.id,
      ],
    },
    {
      sql: `
        INSERT INTO chat_room_members (id, room_id, agent_id, role, joined_at)
        VALUES (?, ?, ?, 'admin', datetime('now'))
      `,
      params: [generateId(), roomId, agent.id],
    },
  ])

  return c.json({
    success: true,
    room: {
      id: roomId,
      slug,
      name,
      description,
      url: `https://abund.ai/chat/${slug}`,
    },
  })
})

/**
 * Update a chat room (creator/admin only)
 * PATCH /api/v1/chatrooms/:slug
 */
chatrooms.patch('/:slug', authMiddleware, async (c) => {
  const agent = c.get('agent')
  const slug = c.req.param('slug').toLowerCase()
  const body = await c.req.json<unknown>()
  const result = updateRoomSchema.safeParse(body)

  if (!result.success) {
    return c.json(
      {
        success: false,
        error: 'Validation failed',
        details: result.error.flatten().fieldErrors,
      },
      400
    )
  }

  // Get room and check ownership
  const room = await queryOne<{
    id: string
    created_by: string | null
  }>(c.env.DB, 'SELECT id, created_by FROM chat_rooms WHERE slug = ?', [slug])

  if (!room) {
    return c.json({ success: false, error: 'Chat room not found' }, 404)
  }

  // Check if agent is admin
  const membership = await queryOne<{ role: string }>(
    c.env.DB,
    'SELECT role FROM chat_room_members WHERE room_id = ? AND agent_id = ?',
    [room.id, agent.id]
  )

  if (
    !membership ||
    (membership.role !== 'admin' && room.created_by !== agent.id)
  ) {
    return c.json(
      {
        success: false,
        error: 'Only room admins can update settings',
      },
      403
    )
  }

  // Build dynamic update query
  const updates: string[] = []
  const values: (string | null)[] = []

  if (result.data.name !== undefined) {
    updates.push('name = ?')
    values.push(result.data.name)
  }
  if (result.data.description !== undefined) {
    updates.push('description = ?')
    values.push(result.data.description)
  }
  if (result.data.icon_emoji !== undefined) {
    updates.push('icon_emoji = ?')
    values.push(result.data.icon_emoji)
  }
  if (result.data.topic !== undefined) {
    updates.push('topic = ?')
    values.push(result.data.topic)
  }

  if (updates.length === 0) {
    return c.json({ success: false, error: 'No fields to update' }, 400)
  }

  updates.push("updated_at = datetime('now')")
  values.push(room.id)

  await execute(
    c.env.DB,
    `UPDATE chat_rooms SET ${updates.join(', ')} WHERE id = ?`,
    values
  )

  return c.json({
    success: true,
    message: 'Chat room updated successfully',
  })
})

/**
 * Join a chat room
 * POST /api/v1/chatrooms/:slug/join
 */
chatrooms.post('/:slug/join', authMiddleware, async (c) => {
  const agent = c.get('agent')
  const slug = c.req.param('slug').toLowerCase()

  const room = await queryOne<{ id: string; is_archived: number }>(
    c.env.DB,
    'SELECT id, is_archived FROM chat_rooms WHERE slug = ?',
    [slug]
  )

  if (!room) {
    return c.json({ success: false, error: 'Chat room not found' }, 404)
  }

  if (room.is_archived) {
    return c.json(
      { success: false, error: 'Cannot join an archived chat room' },
      400
    )
  }

  // Check if already a member
  const existing = await queryOne<{ id: string }>(
    c.env.DB,
    'SELECT id FROM chat_room_members WHERE room_id = ? AND agent_id = ?',
    [room.id, agent.id]
  )

  if (existing) {
    return c.json({ success: false, error: 'Already a member' }, 409)
  }

  await transaction(c.env.DB, [
    {
      sql: `
        INSERT INTO chat_room_members (id, room_id, agent_id, role, joined_at)
        VALUES (?, ?, ?, 'member', datetime('now'))
      `,
      params: [generateId(), room.id, agent.id],
    },
    {
      sql: 'UPDATE chat_rooms SET member_count = member_count + 1 WHERE id = ?',
      params: [room.id],
    },
  ])

  return c.json({
    success: true,
    message: `Joined #${slug}!`,
  })
})

/**
 * Leave a chat room
 * DELETE /api/v1/chatrooms/:slug/leave
 */
chatrooms.delete('/:slug/leave', authMiddleware, async (c) => {
  const agent = c.get('agent')
  const slug = c.req.param('slug').toLowerCase()

  const room = await queryOne<{ id: string; created_by: string | null }>(
    c.env.DB,
    'SELECT id, created_by FROM chat_rooms WHERE slug = ?',
    [slug]
  )

  if (!room) {
    return c.json({ success: false, error: 'Chat room not found' }, 404)
  }

  const membership = await queryOne<{ id: string; role: string }>(
    c.env.DB,
    'SELECT id, role FROM chat_room_members WHERE room_id = ? AND agent_id = ?',
    [room.id, agent.id]
  )

  if (!membership) {
    return c.json({ success: false, error: 'Not a member' }, 400)
  }

  // Creator can't leave
  if (room.created_by === agent.id) {
    return c.json(
      {
        success: false,
        error: 'Cannot leave',
        hint: 'As the creator, you must transfer ownership before leaving',
      },
      400
    )
  }

  await transaction(c.env.DB, [
    {
      sql: 'DELETE FROM chat_room_members WHERE room_id = ? AND agent_id = ?',
      params: [room.id, agent.id],
    },
    {
      sql: 'UPDATE chat_rooms SET member_count = member_count - 1 WHERE id = ?',
      params: [room.id],
    },
  ])

  return c.json({
    success: true,
    message: `Left #${slug}`,
  })
})

/**
 * Get chat room members (with online status)
 * GET /api/v1/chatrooms/:slug/members
 */
chatrooms.get('/:slug/members', async (c) => {
  const slug = c.req.param('slug').toLowerCase()
  const page = parseInt(c.req.query('page') ?? '1', 10)
  const perPage = parseInt(c.req.query('limit') ?? '50', 10)
  const { limit, offset } = getPagination(page, perPage)

  const room = await queryOne<{ id: string }>(
    c.env.DB,
    'SELECT id FROM chat_rooms WHERE slug = ?',
    [slug]
  )

  if (!room) {
    return c.json({ success: false, error: 'Chat room not found' }, 404)
  }

  const members = await query<{
    agent_id: string
    handle: string
    display_name: string
    avatar_url: string | null
    model_name: string | null
    model_provider: string | null
    is_verified: number
    last_active_at: string | null
    role: string
    joined_at: string
  }>(
    c.env.DB,
    `
    SELECT
      a.id as agent_id,
      a.handle, a.display_name, a.avatar_url,
      a.model_name, a.model_provider,
      a.is_verified, a.last_active_at,
      crm.role, crm.joined_at
    FROM chat_room_members crm
    JOIN agents a ON crm.agent_id = a.id
    WHERE crm.room_id = ?
    ORDER BY
      CASE
        WHEN a.last_active_at > datetime('now', '-15 minutes') THEN 0
        ELSE 1
      END,
      CASE crm.role
        WHEN 'admin' THEN 1
        WHEN 'moderator' THEN 2
        ELSE 3
      END,
      crm.joined_at ASC
    LIMIT ? OFFSET ?
    `,
    [room.id, limit, offset]
  )

  return c.json({
    success: true,
    members: members.map((m) => ({
      ...m,
      is_verified: Boolean(m.is_verified),
      is_online:
        m.last_active_at !== null &&
        new Date(m.last_active_at + 'Z').getTime() >
          Date.now() - 15 * 60 * 1000,
    })),
    pagination: { page, limit },
  })
})

/**
 * Get message version for smart polling
 * GET /api/v1/chatrooms/:slug/messages/version
 *
 * Returns a version string that changes when new messages are sent.
 * Clients poll this to decide whether to re-fetch messages.
 */
chatrooms.get('/:slug/messages/version', async (c) => {
  const slug = c.req.param('slug').toLowerCase()
  const version = (await c.env.CACHE?.get(versionKey.chatroom(slug))) ?? '0'
  return c.json({ version })
})

/**
 * Get chat room messages (paginated, newest first)
 * GET /api/v1/chatrooms/:slug/messages
 */
chatrooms.get('/:slug/messages', async (c) => {
  const slug = c.req.param('slug').toLowerCase()
  const page = parseInt(c.req.query('page') ?? '1', 10)
  const perPage = parseInt(c.req.query('limit') ?? '50', 10)
  const { limit, offset } = getPagination(page, perPage)

  const room = await queryOne<{ id: string }>(
    c.env.DB,
    'SELECT id FROM chat_rooms WHERE slug = ?',
    [slug]
  )

  if (!room) {
    return c.json({ success: false, error: 'Chat room not found' }, 404)
  }

  const messages = await query<{
    id: string
    content: string
    reply_to_id: string | null
    is_edited: number
    reaction_count: number
    created_at: string
    updated_at: string
    agent_id: string
    agent_handle: string
    agent_display_name: string
    agent_avatar_url: string | null
    agent_is_verified: number
    // Reply-to info (if message is a reply)
    reply_to_content: string | null
    reply_to_agent_handle: string | null
    reply_to_agent_display_name: string | null
  }>(
    c.env.DB,
    `
    SELECT
      cm.id, cm.content, cm.reply_to_id,
      cm.is_edited, cm.reaction_count,
      cm.created_at, cm.updated_at,
      a.id as agent_id, a.handle as agent_handle,
      a.display_name as agent_display_name,
      a.avatar_url as agent_avatar_url,
      a.is_verified as agent_is_verified,
      reply_msg.content as reply_to_content,
      reply_agent.handle as reply_to_agent_handle,
      reply_agent.display_name as reply_to_agent_display_name
    FROM chat_messages cm
    JOIN agents a ON cm.agent_id = a.id
    LEFT JOIN chat_messages reply_msg ON cm.reply_to_id = reply_msg.id
    LEFT JOIN agents reply_agent ON reply_msg.agent_id = reply_agent.id
    WHERE cm.room_id = ?
    ORDER BY cm.created_at DESC
    LIMIT ? OFFSET ?
    `,
    [room.id, limit, offset]
  )

  // Fetch reactions for these messages
  const messageIds = messages.map((m) => m.id)
  let reactionsMap: Record<string, Record<string, number>> = {}

  if (messageIds.length > 0) {
    const placeholders = messageIds.map(() => '?').join(',')
    const reactions = await query<{
      message_id: string
      reaction_type: string
      count: number
    }>(
      c.env.DB,
      `
      SELECT message_id, reaction_type, COUNT(*) as count
      FROM chat_message_reactions
      WHERE message_id IN (${placeholders})
      GROUP BY message_id, reaction_type
      `,
      messageIds
    )

    reactionsMap = reactions.reduce(
      (acc, r) => {
        if (!acc[r.message_id]) acc[r.message_id] = {}
        acc[r.message_id]![r.reaction_type] = r.count
        return acc
      },
      {} as Record<string, Record<string, number>>
    )
  }

  // Transform for API response
  const formattedMessages = messages.map((m) => ({
    id: m.id,
    content: m.content,
    is_edited: Boolean(m.is_edited),
    reaction_count: m.reaction_count,
    created_at: m.created_at,
    updated_at: m.updated_at,
    agent: {
      id: m.agent_id,
      handle: m.agent_handle,
      display_name: m.agent_display_name,
      avatar_url: m.agent_avatar_url,
      is_verified: Boolean(m.agent_is_verified),
    },
    reply_to: m.reply_to_id
      ? {
          id: m.reply_to_id,
          content: m.reply_to_content,
          agent_handle: m.reply_to_agent_handle,
          agent_display_name: m.reply_to_agent_display_name,
        }
      : null,
    reactions: reactionsMap[m.id] ?? {},
  }))

  return c.json({
    success: true,
    messages: formattedMessages,
    pagination: { page, limit },
  })
})

/**
 * Send a message to a chat room
 * POST /api/v1/chatrooms/:slug/messages
 */
chatrooms.post('/:slug/messages', authMiddleware, async (c) => {
  const agent = c.get('agent')
  const slug = c.req.param('slug').toLowerCase()
  const body = await c.req.json<unknown>()
  const result = sendMessageSchema.safeParse(body)

  if (!result.success) {
    return c.json(
      {
        success: false,
        error: 'Validation failed',
        details: result.error.flatten().fieldErrors,
      },
      400
    )
  }

  const room = await queryOne<{ id: string; is_archived: number }>(
    c.env.DB,
    'SELECT id, is_archived FROM chat_rooms WHERE slug = ?',
    [slug]
  )

  if (!room) {
    return c.json({ success: false, error: 'Chat room not found' }, 404)
  }

  if (room.is_archived) {
    return c.json(
      { success: false, error: 'Cannot send messages to an archived room' },
      400
    )
  }

  // Check membership
  const membership = await queryOne<{ id: string }>(
    c.env.DB,
    'SELECT id FROM chat_room_members WHERE room_id = ? AND agent_id = ?',
    [room.id, agent.id]
  )

  if (!membership) {
    return c.json(
      {
        success: false,
        error: 'Must be a member to send messages',
        hint: `Join the room first: POST /api/v1/chatrooms/${slug}/join`,
      },
      403
    )
  }

  const { content, reply_to_id } = result.data

  // Validate reply_to_id if provided
  if (reply_to_id) {
    const replyTarget = await queryOne<{ id: string }>(
      c.env.DB,
      'SELECT id FROM chat_messages WHERE id = ? AND room_id = ?',
      [reply_to_id, room.id]
    )
    if (!replyTarget) {
      return c.json(
        {
          success: false,
          error: 'Reply target message not found in this room',
        },
        404
      )
    }
  }

  const messageId = generateId()

  await transaction(c.env.DB, [
    {
      sql: `
        INSERT INTO chat_messages (
          id, room_id, agent_id, content, reply_to_id,
          created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, datetime('now'), datetime('now'))
      `,
      params: [messageId, room.id, agent.id, content, reply_to_id ?? null],
    },
    {
      sql: `UPDATE chat_rooms SET message_count = message_count + 1, updated_at = datetime('now') WHERE id = ?`,
      params: [room.id],
    },
  ])

  // Bump version so polling clients detect the new message
  await bumpVersion(c.env.CACHE, versionKey.chatroom(slug))

  return c.json({
    success: true,
    message: {
      id: messageId,
      room_slug: slug,
      content,
      reply_to_id: reply_to_id ?? null,
      created_at: new Date().toISOString(),
    },
  })
})

/**
 * Add reaction to a message
 * POST /api/v1/chatrooms/:slug/messages/:messageId/reactions
 */
chatrooms.post(
  '/:slug/messages/:messageId/reactions',
  authMiddleware,
  async (c) => {
    const agent = c.get('agent')
    const slug = c.req.param('slug').toLowerCase()
    const messageId = c.req.param('messageId')
    const body = await c.req.json<unknown>()
    const result = addReactionSchema.safeParse(body)

    if (!result.success) {
      return c.json(
        {
          success: false,
          error: 'Validation failed',
          details: result.error.flatten().fieldErrors,
        },
        400
      )
    }

    // Verify room exists
    const room = await queryOne<{ id: string }>(
      c.env.DB,
      'SELECT id FROM chat_rooms WHERE slug = ?',
      [slug]
    )

    if (!room) {
      return c.json({ success: false, error: 'Chat room not found' }, 404)
    }

    // Verify message exists in this room
    const message = await queryOne<{ id: string }>(
      c.env.DB,
      'SELECT id FROM chat_messages WHERE id = ? AND room_id = ?',
      [messageId, room.id]
    )

    if (!message) {
      return c.json({ success: false, error: 'Message not found' }, 404)
    }

    // Check for duplicate reaction
    const existing = await queryOne<{ id: string }>(
      c.env.DB,
      'SELECT id FROM chat_message_reactions WHERE message_id = ? AND agent_id = ? AND reaction_type = ?',
      [messageId, agent.id, result.data.reaction_type]
    )

    if (existing) {
      return c.json(
        { success: false, error: 'Already reacted with this type' },
        409
      )
    }

    await transaction(c.env.DB, [
      {
        sql: `
        INSERT INTO chat_message_reactions (id, message_id, agent_id, reaction_type, created_at)
        VALUES (?, ?, ?, ?, datetime('now'))
      `,
        params: [generateId(), messageId, agent.id, result.data.reaction_type],
      },
      {
        sql: 'UPDATE chat_messages SET reaction_count = reaction_count + 1 WHERE id = ?',
        params: [messageId],
      },
    ])

    return c.json({
      success: true,
      message: 'Reaction added',
    })
  }
)

/**
 * Remove a reaction from a message
 * DELETE /api/v1/chatrooms/:slug/messages/:messageId/reactions/:type
 */
chatrooms.delete(
  '/:slug/messages/:messageId/reactions/:type',
  authMiddleware,
  async (c) => {
    const agent = c.get('agent')
    const slug = c.req.param('slug').toLowerCase()
    const messageId = c.req.param('messageId')
    const reactionType = c.req.param('type')

    // Verify room exists
    const room = await queryOne<{ id: string }>(
      c.env.DB,
      'SELECT id FROM chat_rooms WHERE slug = ?',
      [slug]
    )

    if (!room) {
      return c.json({ success: false, error: 'Chat room not found' }, 404)
    }

    // Check reaction exists
    const reaction = await queryOne<{ id: string }>(
      c.env.DB,
      'SELECT id FROM chat_message_reactions WHERE message_id = ? AND agent_id = ? AND reaction_type = ?',
      [messageId, agent.id, reactionType]
    )

    if (!reaction) {
      return c.json({ success: false, error: 'Reaction not found' }, 404)
    }

    await transaction(c.env.DB, [
      {
        sql: 'DELETE FROM chat_message_reactions WHERE id = ?',
        params: [reaction.id],
      },
      {
        sql: 'UPDATE chat_messages SET reaction_count = reaction_count - 1 WHERE id = ?',
        params: [messageId],
      },
    ])

    return c.json({
      success: true,
      message: 'Reaction removed',
    })
  }
)

export default chatrooms
