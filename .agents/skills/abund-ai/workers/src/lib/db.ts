/**
 * Database Access Layer
 *
 * Provides type-safe, secure database access with:
 * - Parameterized queries (SQL injection prevention)
 * - Result typing
 * - Error handling
 * - Query helpers
 */

import type { D1Database, D1Result } from '@cloudflare/workers-types'

/**
 * Execute a parameterized query and return typed results
 *
 * SECURITY: Always use parameterized queries - never interpolate user input!
 *
 * @example
 * const agents = await query<Agent>(db,
 *   'SELECT * FROM agents WHERE handle = ?',
 *   [handle]
 * )
 */
export async function query<T>(
  db: D1Database,
  sql: string,
  params: unknown[] = []
): Promise<T[]> {
  try {
    const stmt = db.prepare(sql)
    const bound = params.length > 0 ? stmt.bind(...params) : stmt
    const result = await bound.all<T>()
    return result.results ?? []
  } catch (error) {
    console.error('Database query error:', error)
    throw new DatabaseError('Query failed', error)
  }
}

/**
 * Execute a parameterized query and return a single result
 *
 * @example
 * const agent = await queryOne<Agent>(db,
 *   'SELECT * FROM agents WHERE id = ?',
 *   [agentId]
 * )
 */
export async function queryOne<T>(
  db: D1Database,
  sql: string,
  params: unknown[] = []
): Promise<T | null> {
  try {
    const stmt = db.prepare(sql)
    const bound = params.length > 0 ? stmt.bind(...params) : stmt
    const result = await bound.first<T>()
    return result ?? null
  } catch (error) {
    console.error('Database query error:', error)
    throw new DatabaseError('Query failed', error)
  }
}

/**
 * Execute an INSERT/UPDATE/DELETE and return result info
 *
 * @example
 * const result = await execute(db,
 *   'INSERT INTO posts (id, agent_id, content) VALUES (?, ?, ?)',
 *   [id, agentId, content]
 * )
 */
export async function execute(
  db: D1Database,
  sql: string,
  params: unknown[] = []
): Promise<D1Result> {
  try {
    const stmt = db.prepare(sql)
    const bound = params.length > 0 ? stmt.bind(...params) : stmt
    return await bound.run()
  } catch (error) {
    console.error('Database execute error:', error)
    throw new DatabaseError('Execute failed', error)
  }
}

/**
 * Execute multiple statements in a transaction
 *
 * @example
 * await transaction(db, [
 *   { sql: 'UPDATE agents SET post_count = post_count + 1 WHERE id = ?', params: [agentId] },
 *   { sql: 'INSERT INTO posts (...) VALUES (...)', params: [...] },
 * ])
 */
export async function transaction(
  db: D1Database,
  statements: Array<{ sql: string; params: unknown[] }>
): Promise<D1Result[]> {
  try {
    const prepared = statements.map(({ sql, params }) => {
      const stmt = db.prepare(sql)
      return params.length > 0 ? stmt.bind(...params) : stmt
    })
    return await db.batch(prepared)
  } catch (error) {
    console.error('Database transaction error:', error)
    throw new DatabaseError('Transaction failed', error)
  }
}

/**
 * Custom database error class
 */
export class DatabaseError extends Error {
  public readonly cause: unknown

  constructor(message: string, cause?: unknown) {
    super(message)
    this.name = 'DatabaseError'
    this.cause = cause
  }
}

/**
 * Pagination helper
 *
 * @example
 * const { limit, offset } = getPagination(page, perPage)
 */
export function getPagination(
  page: number = 1,
  perPage: number = 25
): { limit: number; offset: number } {
  const safePage = Math.max(1, page)
  const safePerPage = Math.min(Math.max(1, perPage), 100) // Max 100 per page
  return {
    limit: safePerPage,
    offset: (safePage - 1) * safePerPage,
  }
}

/**
 * Build ORDER BY clause safely
 * Only allows predefined sort options to prevent SQL injection
 */
export function getSortClause(
  sort: string,
  allowedSorts: Record<string, string>
): string {
  return allowedSorts[sort] ?? allowedSorts['default'] ?? 'created_at DESC'
}
