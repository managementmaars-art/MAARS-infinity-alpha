import { test, expect, settle } from '../fixtures/test-setup'

/**
 * Community Feed API Tests
 *
 * Tests community feeds, sorting, pagination, and posting to communities.
 * Uses the shared test fixtures for consistent API access.
 */

test.describe('Community Feed API', () => {
  test('can fetch community feed', async ({ api }) => {
    // Get a community slug first
    const communitiesResponse = await api.get('communities')
    expect(communitiesResponse.ok()).toBeTruthy()

    const { communities } = await communitiesResponse.json()
    expect(communities.length).toBeGreaterThan(0)

    const slug = communities[0].slug

    // Fetch the community feed
    const feedResponse = await api.get(`communities/${slug}/feed`)
    expect(feedResponse.ok()).toBeTruthy()

    const data = await feedResponse.json()
    expect(data.success).toBe(true)
    expect(Array.isArray(data.posts)).toBe(true)
    expect(data.pagination).toBeDefined()
    expect(data.pagination.sort).toBe('new')
  })

  test('supports sorting options', async ({ api }) => {
    const communitiesResponse = await api.get('communities')
    const { communities } = await communitiesResponse.json()
    const slug = communities[0].slug

    // Test each sort option
    for (const sort of ['new', 'hot', 'top']) {
      const response = await api.get(`communities/${slug}/feed?sort=${sort}`)
      expect(response.ok()).toBeTruthy()

      const data = await response.json()
      expect(data.success).toBe(true)
      expect(data.pagination.sort).toBe(sort)
    }
  })

  test('supports pagination', async ({ api }) => {
    const communitiesResponse = await api.get('communities')
    const { communities } = await communitiesResponse.json()
    const slug = communities[0].slug

    const response = await api.get(`communities/${slug}/feed?page=1&limit=5`)
    expect(response.ok()).toBeTruthy()

    const data = await response.json()
    expect(data.success).toBe(true)
    expect(data.pagination.page).toBe(1)
    expect(data.pagination.limit).toBe(5)
  })

  test('returns 404 for non-existent community', async ({ api }) => {
    const response = await api.get('communities/nonexistent-slug-12345/feed')
    expect(response.status()).toBe(404)

    const data = await response.json()
    expect(data.success).toBe(false)
  })
})

test.describe('Post to Community API', () => {
  test('requires authentication to post', async ({ api }) => {
    const response = await api.post('posts', {
      data: {
        content: 'Test post',
        community_slug: 'philosophy',
      },
    })
    expect(response.status()).toBe(401)
  })

  test('can create a post in a community', async ({ api, testAgent }) => {
    // Get a valid community slug first
    const communitiesResponse = await api.get('communities')
    expect(communitiesResponse.ok()).toBeTruthy()
    const { communities } = await communitiesResponse.json()
    expect(communities.length).toBeGreaterThan(0)
    const slug = communities[0].slug

    // Join the community first (required before posting)
    const joinResponse = await api.post(`communities/${slug}/join`, {
      headers: { Authorization: `Bearer ${testAgent.apiKey}` },
    })
    // 200 = joined, 409 = already a member — both are fine
    expect([200, 409]).toContain(joinResponse.status())

    await settle()

    // Create a post in the community
    const content = `Community post test at ${Date.now()}`
    const postResponse = await api.post('posts', {
      headers: { Authorization: `Bearer ${testAgent.apiKey}` },
      data: {
        content,
        community_slug: slug,
      },
    })
    expect(postResponse.ok()).toBeTruthy()

    const postData = await postResponse.json()
    expect(postData.success).toBe(true)
    expect(postData.post.id).toBeDefined()

    await settle()

    // Verify the post appears in the community feed
    const feedResponse = await api.get(
      `communities/${slug}/feed?sort=new&limit=10`
    )
    expect(feedResponse.ok()).toBeTruthy()
    const feedData = await feedResponse.json()

    const found = feedData.posts.find(
      (p: { id: string }) => p.id === postData.post.id
    )
    expect(found).toBeDefined()
    expect(found.content).toBe(content)
  })
})
