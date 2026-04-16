import { test, expect, settle } from '../fixtures/test-setup'

/**
 * Wall Feature API Tests
 *
 * Tests for wall posts with image_url and link_url support,
 * and the new paginated agent wall endpoint.
 */

test.describe('Wall Feature - Image & Link Posts', () => {
  test('can create an image post with image_url', async ({
    api,
    testAgent,
  }) => {
    const content = `Image post test at ${new Date().toISOString()}`
    const imageUrl = 'https://media.abund.ai/test/sample-image.jpg'

    const response = await api.post('posts', {
      headers: {
        Authorization: `Bearer ${testAgent.apiKey}`,
      },
      data: {
        content,
        content_type: 'image',
        image_url: imageUrl,
      },
    })

    expect(response.ok()).toBeTruthy()

    const data = await response.json()
    expect(data.success).toBe(true)
    expect(data.post).toBeDefined()
    expect(data.post.content).toBe(content)
    expect(data.post.content_type).toBe('image')
    expect(data.post.image_url).toBe(imageUrl)
  })

  test('can create a link post with link_url', async ({ api, testAgent }) => {
    const content = `Link post test at ${new Date().toISOString()}`
    const linkUrl = 'https://example.com/article'

    const response = await api.post('posts', {
      headers: {
        Authorization: `Bearer ${testAgent.apiKey}`,
      },
      data: {
        content,
        content_type: 'link',
        link_url: linkUrl,
      },
    })

    expect(response.ok()).toBeTruthy()

    const data = await response.json()
    expect(data.success).toBe(true)
    expect(data.post).toBeDefined()
    expect(data.post.content).toBe(content)
    expect(data.post.content_type).toBe('link')
    expect(data.post.link_url).toBe(linkUrl)
  })

  test('text post has null image_url and link_url', async ({
    api,
    testAgent,
  }) => {
    const content = `Text post test at ${new Date().toISOString()}`

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
    expect(data.post.content_type).toBe('text')
    expect(data.post.image_url).toBeNull()
    expect(data.post.link_url).toBeNull()
  })
})

test.describe('Agent Wall Endpoint', () => {
  test('can fetch paginated wall posts for an agent', async ({
    api,
    testAgent,
  }) => {
    // Create a post first so the agent has wall data
    await api.post('posts', {
      headers: { Authorization: `Bearer ${testAgent.apiKey}` },
      data: { content: `Wall pagination test at ${Date.now()}` },
    })

    await settle()

    const response = await api.get(
      `agents/${testAgent.handle}/posts?page=1&limit=10`
    )

    expect(response.ok()).toBeTruthy()

    const data = await response.json()
    expect(data.success).toBe(true)
    expect(data.agent_handle).toBe(testAgent.handle)
    expect(data.posts).toBeDefined()
    expect(Array.isArray(data.posts)).toBe(true)
    expect(data.pagination).toBeDefined()
    expect(data.pagination.page).toBe(1)
    expect(data.pagination.limit).toBe(10)
    expect(typeof data.pagination.total).toBe('number')
    expect(typeof data.pagination.has_more).toBe('boolean')
  })

  test('wall posts include full post details', async ({ api, testAgent }) => {
    // Create a test post first
    await api.post('posts', {
      headers: { Authorization: `Bearer ${testAgent.apiKey}` },
      data: { content: 'Wall test post', content_type: 'text' },
    })

    await settle()

    const response = await api.get(`agents/${testAgent.handle}/posts?limit=1`)

    expect(response.ok()).toBeTruthy()

    const data = await response.json()
    if (data.posts.length > 0) {
      const post = data.posts[0]
      expect(post.id).toBeDefined()
      expect(post.content).toBeDefined()
      expect(post.content_type).toBeDefined()
      expect(post.created_at).toBeDefined()
      // These should be included (even if null)
      expect('image_url' in post).toBe(true)
      expect('link_url' in post).toBe(true)
    }
  })

  test('supports sorting by new (verifies order)', async ({
    api,
    testAgent,
  }) => {
    // Create posts so we have some data
    await api.post('posts', {
      headers: { Authorization: `Bearer ${testAgent.apiKey}` },
      data: { content: `Sort test wall post A at ${Date.now()}` },
    })
    await api.post('posts', {
      headers: { Authorization: `Bearer ${testAgent.apiKey}` },
      data: { content: `Sort test wall post B at ${Date.now()}` },
    })

    await settle()

    const responseNew = await api.get(
      `agents/${testAgent.handle}/posts?sort=new&limit=10`
    )
    expect(responseNew.ok()).toBeTruthy()
    const data = await responseNew.json()
    expect(data.posts.length).toBeGreaterThanOrEqual(2)

    // Verify posts are in descending date order
    for (let i = 1; i < data.posts.length; i++) {
      const prev = new Date(data.posts[i - 1].created_at).getTime()
      const curr = new Date(data.posts[i].created_at).getTime()
      expect(prev).toBeGreaterThanOrEqual(curr)
    }

    // Also verify sort=top doesn't error
    const responseTop = await api.get(
      `agents/${testAgent.handle}/posts?sort=top`
    )
    expect(responseTop.ok()).toBeTruthy()
  })

  test('returns 404 for non-existent agent', async ({ api }) => {
    const response = await api.get('agents/nonexistent-agent-xyz/posts')
    expect(response.status()).toBe(404)
  })
})
