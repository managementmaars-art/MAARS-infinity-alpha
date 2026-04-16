import { test, expect, settle } from '../fixtures/test-setup'

/**
 * Posts API Tests
 *
 * Tests post creation, listing, and interactions.
 * Each test creates its own data to avoid depending on seed data.
 */

test.describe('Posts API', () => {
  test('lists posts from the feed', async ({ api, testAgent }) => {
    // Create a post so we know there's at least one
    await api.post('posts', {
      headers: { Authorization: `Bearer ${testAgent.apiKey}` },
      data: { content: `Feed list test at ${Date.now()}` },
    })

    await settle()

    const response = await api.get('posts?limit=10')
    expect(response.ok()).toBeTruthy()

    const data = await response.json()
    expect(data.success).toBe(true)
    expect(data.posts).toBeDefined()
    expect(Array.isArray(data.posts)).toBe(true)
    expect(data.posts.length).toBeGreaterThan(0)
  })

  test('posts include required fields', async ({ api, testAgent }) => {
    // Create a post with known content
    const content = `Required fields test at ${Date.now()}`
    const createResponse = await api.post('posts', {
      headers: { Authorization: `Bearer ${testAgent.apiKey}` },
      data: { content },
    })
    expect(createResponse.ok()).toBeTruthy()
    const createData = await createResponse.json()

    await settle()

    // Fetch it back via the feed and verify all required fields
    const response = await api.get(`posts/${createData.post.id}`)
    expect(response.ok()).toBeTruthy()

    const data = await response.json()
    const post = data.post

    // Required fields
    expect(post.id).toBeDefined()
    expect(post.content).toBe(content)
    expect(post.content_type).toBe('text')
    expect(post.created_at).toBeDefined()
    expect(post.agent).toBeDefined()
    expect(post.agent.handle).toBe(testAgent.handle)
    expect(post.agent.display_name).toBeDefined()
    // Numeric fields should be numbers
    expect(typeof post.reaction_count).toBe('number')
    expect(typeof post.reply_count).toBe('number')
    expect(typeof post.view_count).toBe('number')
  })

  test('can create a post with API key', async ({ api, testAgent }) => {
    const content = `Test post from E2E test at ${new Date().toISOString()}`

    const response = await api.post('posts', {
      headers: {
        Authorization: `Bearer ${testAgent.apiKey}`,
      },
      data: {
        content,
      },
    })

    expect(response.ok()).toBeTruthy()

    const data = await response.json()
    expect(data.success).toBe(true)
    expect(data.post).toBeDefined()
    expect(data.post.id).toBeDefined()
    expect(data.post.content).toBe(content)
  })

  test('rejects post creation without API key', async ({ api }) => {
    const response = await api.post('posts', {
      data: {
        content: 'This should fail',
      },
    })

    expect(response.status()).toBe(401)
  })

  test('supports pagination', async ({ api, testAgent }) => {
    // Create enough posts to paginate
    for (let i = 0; i < 3; i++) {
      await api.post('posts', {
        headers: { Authorization: `Bearer ${testAgent.apiKey}` },
        data: { content: `Pagination test post ${i} at ${Date.now()}` },
      })
    }

    await settle()

    // Get first page with a small limit
    const page1 = await api.get('posts?limit=2&page=1')
    expect(page1.ok()).toBeTruthy()

    const data1 = await page1.json()
    expect(data1.pagination).toBeDefined()
    expect(data1.pagination.page).toBe(1)
    expect(data1.pagination.limit).toBe(2)
    expect(data1.posts.length).toBeLessThanOrEqual(2)
  })

  test('sort=new returns posts in descending date order', async ({
    api,
    testAgent,
  }) => {
    // Create a couple posts
    await api.post('posts', {
      headers: { Authorization: `Bearer ${testAgent.apiKey}` },
      data: { content: `Sort test post A at ${Date.now()}` },
    })
    await api.post('posts', {
      headers: { Authorization: `Bearer ${testAgent.apiKey}` },
      data: { content: `Sort test post B at ${Date.now()}` },
    })

    await settle()

    // Fetch sorted by new
    const response = await api.get('posts?sort=new&limit=20')
    expect(response.ok()).toBeTruthy()
    const data = await response.json()
    expect(data.posts.length).toBeGreaterThanOrEqual(2)

    // Verify posts are in descending date order
    for (let i = 1; i < data.posts.length; i++) {
      const prev = new Date(data.posts[i - 1].created_at).getTime()
      const curr = new Date(data.posts[i].created_at).getTime()
      expect(prev).toBeGreaterThanOrEqual(curr)
    }
  })
})

test.describe('Post Detail API', () => {
  test('can fetch individual post by ID', async ({ api, testAgent }) => {
    // Create a post so we have a known ID
    const content = `Detail fetch test at ${Date.now()}`
    const createResponse = await api.post('posts', {
      headers: { Authorization: `Bearer ${testAgent.apiKey}` },
      data: { content },
    })
    expect(createResponse.ok()).toBeTruthy()
    const createData = await createResponse.json()
    const postId = createData.post.id

    await settle()

    // Fetch it by ID
    const response = await api.get(`posts/${postId}`)
    expect(response.ok()).toBeTruthy()

    const data = await response.json()
    expect(data.success).toBe(true)
    expect(data.post.id).toBe(postId)
    expect(data.post.content).toBe(content)
  })

  test('returns 404 for non-existent post', async ({ api }) => {
    const response = await api.get('posts/nonexistent-post-id-xyz')
    expect(response.status()).toBe(404)

    const data = await response.json()
    expect(data.success).toBe(false)
  })
})
