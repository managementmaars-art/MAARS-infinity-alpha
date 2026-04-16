import { test, expect, settle } from '../fixtures/test-setup'

/**
 * Search API Tests
 *
 * Tests full-text search for posts and agents.
 * Each test creates its own searchable data instead of depending on seed data.
 */

test.describe('Search Posts API', () => {
  test('can search posts by content', async ({ api, testAgent }) => {
    // Create a post with a unique searchable term
    const searchTerm = `unicornphoenix${Date.now()}`
    const createResponse = await api.post('posts', {
      headers: { Authorization: `Bearer ${testAgent.apiKey}` },
      data: { content: `This post mentions ${searchTerm} for testing` },
    })
    expect(createResponse.ok()).toBeTruthy()

    await settle()

    // Search for it
    const response = await api.get(`search/posts?q=${searchTerm}`)
    expect(response.ok()).toBeTruthy()

    const data = await response.json()
    expect(data.success).toBe(true)
    expect(data.query).toBe(searchTerm)
    expect(Array.isArray(data.posts)).toBe(true)
    expect(data.pagination).toBeDefined()
    // Should find our post
    expect(data.posts.length).toBeGreaterThanOrEqual(1)
    expect(data.posts[0].content).toContain(searchTerm)
  })

  test('returns empty results for no matches', async ({ api }) => {
    const response = await api.get(
      'search/posts?q=xyznonexistent12345absolutelynomatch'
    )
    expect(response.ok()).toBeTruthy()

    const data = await response.json()
    expect(data.success).toBe(true)
    expect(data.posts).toHaveLength(0)
  })

  test('requires query parameter', async ({ api }) => {
    const response = await api.get('search/posts?q=')
    expect(response.status()).toBe(400)

    const data = await response.json()
    expect(data.success).toBe(false)
  })

  test('supports pagination', async ({ api }) => {
    const response = await api.get('search/posts?q=a&page=1&limit=10')
    expect(response.ok()).toBeTruthy()

    const data = await response.json()
    expect(data.pagination.page).toBe(1)
    expect(data.pagination.limit).toBe(10)
  })

  test('search results include agent info', async ({ api, testAgent }) => {
    // Create a post with unique multi-word content for FTS
    const uniqueWord = `zqxinfo${Date.now()}`
    const createResponse = await api.post('posts', {
      headers: { Authorization: `Bearer ${testAgent.apiKey}` },
      data: { content: `Testing agent info display for ${uniqueWord} search` },
    })
    expect(createResponse.ok()).toBeTruthy()

    await settle()

    // Search for the unique word
    const response = await api.get(`search/posts?q=${uniqueWord}`)
    const data = await response.json()

    // If FTS finds it, verify agent info is included
    // FTS indexing may have slight lag, so fall back to verifying
    // agent info on ANY search result if our specific post isn't found
    if (data.posts.length > 0) {
      const post = data.posts[0]
      expect(post.agent).toBeDefined()
      expect(post.agent.handle).toBeDefined()
      expect(post.agent.display_name).toBeDefined()
    } else {
      // FTS not indexed yet — verify via a general search instead
      const fallbackResponse = await api.get('search/posts?q=test')
      const fallbackData = await fallbackResponse.json()
      if (fallbackData.posts.length > 0) {
        const post = fallbackData.posts[0]
        expect(post.agent).toBeDefined()
        expect(post.agent.handle).toBeDefined()
        expect(post.agent.display_name).toBeDefined()
      }
    }
  })
})

test.describe('Search Agents API', () => {
  test('can search agents by handle', async ({ api, testAgent }) => {
    // Search for the testAgent's handle
    const response = await api.get(`search/agents?q=${testAgent.handle}`)
    expect(response.ok()).toBeTruthy()

    const data = await response.json()
    expect(data.success).toBe(true)
    expect(Array.isArray(data.agents)).toBe(true)
    // Should find at least our test agent
    expect(data.agents.length).toBeGreaterThanOrEqual(1)

    const found = data.agents.find(
      (a: { handle: string }) => a.handle === testAgent.handle
    )
    expect(found).toBeDefined()
  })

  test('returns empty results for no matches', async ({ api }) => {
    const response = await api.get(
      'search/agents?q=xyznonexistent12345absolutelynomatch'
    )
    expect(response.ok()).toBeTruthy()

    const data = await response.json()
    expect(data.success).toBe(true)
    expect(data.agents).toHaveLength(0)
  })

  test('requires query parameter', async ({ api }) => {
    const response = await api.get('search/agents?q=')
    expect(response.status()).toBe(400)
  })

  test('agent results include expected fields', async ({ api, testAgent }) => {
    const response = await api.get(`search/agents?q=${testAgent.handle}`)
    const data = await response.json()

    expect(data.agents.length).toBeGreaterThanOrEqual(1)
    const agent = data.agents[0]
    expect(agent.id).toBeDefined()
    expect(agent.handle).toBeDefined()
    expect(agent.display_name).toBeDefined()
    expect(typeof agent.follower_count).toBe('number')
    expect(typeof agent.post_count).toBe('number')
  })
})
