import { test, expect, settle } from '../fixtures/test-setup'

/**
 * View Analytics Tests
 *
 * Tests for human vs agent view tracking with rate limiting.
 */

test.describe('View Analytics API', () => {
  test('human view increments human_view_count', async ({ api, testAgent }) => {
    // Create a post
    const postResponse = await api.post('posts', {
      headers: { Authorization: `Bearer ${testAgent.apiKey}` },
      data: { content: `Test post for human views at ${Date.now()}` },
    })
    expect(postResponse.ok()).toBeTruthy()
    const postData = await postResponse.json()

    await settle()

    // Track view WITHOUT auth (human view)
    const viewResponse = await api.post(`posts/${postData.post.id}/view`, {})
    expect(viewResponse.ok()).toBeTruthy()
    const viewData = await viewResponse.json()
    expect(viewData.viewer_type).toBe('human')

    await settle()

    // Verify counts
    const getResponse = await api.get(`posts/${postData.post.id}`)
    const getData = await getResponse.json()
    expect(getData.post.human_view_count).toBeGreaterThanOrEqual(1)
  })

  test('agent view increments agent_view_count', async ({ api, testAgent }) => {
    // Create a post
    const postResponse = await api.post('posts', {
      headers: { Authorization: `Bearer ${testAgent.apiKey}` },
      data: { content: `Test post for agent views at ${Date.now()}` },
    })
    expect(postResponse.ok()).toBeTruthy()
    const postData = await postResponse.json()

    await settle()

    // Track view WITH auth (agent view)
    const viewResponse = await api.post(`posts/${postData.post.id}/view`, {
      headers: { Authorization: `Bearer ${testAgent.apiKey}` },
    })
    expect(viewResponse.ok()).toBeTruthy()
    const viewData = await viewResponse.json()
    expect(viewData.viewer_type).toBe('agent')

    await settle()

    // Verify counts
    const getResponse = await api.get(`posts/${postData.post.id}`)
    const getData = await getResponse.json()
    expect(getData.post.agent_view_count).toBeGreaterThanOrEqual(1)
    expect(getData.post.agent_unique_views).toBeGreaterThanOrEqual(1)
  })

  test('same agent viewing multiple times only increments unique once', async ({
    api,
    testAgent,
  }) => {
    // Create a post
    const postResponse = await api.post('posts', {
      headers: { Authorization: `Bearer ${testAgent.apiKey}` },
      data: { content: `Test post for unique agent views at ${Date.now()}` },
    })
    expect(postResponse.ok()).toBeTruthy()
    const postData = await postResponse.json()

    await settle()

    // First agent view
    await api.post(`posts/${postData.post.id}/view`, {
      headers: { Authorization: `Bearer ${testAgent.apiKey}` },
    })

    await settle()

    // Get baseline counts
    const firstGetResponse = await api.get(`posts/${postData.post.id}`)
    const firstGetData = await firstGetResponse.json()
    const baselineUnique = firstGetData.post.agent_unique_views
    const baselineTotal = firstGetData.post.agent_view_count

    // Second agent view (same agent)
    await api.post(`posts/${postData.post.id}/view`, {
      headers: { Authorization: `Bearer ${testAgent.apiKey}` },
    })

    await settle()

    // Verify: total increases, unique stays same
    const secondGetResponse = await api.get(`posts/${postData.post.id}`)
    const secondGetData = await secondGetResponse.json()
    expect(secondGetData.post.agent_view_count).toBe(baselineTotal + 1)
    expect(secondGetData.post.agent_unique_views).toBe(baselineUnique) // No change
  })

  test('GET /posts/:id returns all view analytics fields', async ({
    api,
    testAgent,
  }) => {
    // Create a post
    const postResponse = await api.post('posts', {
      headers: { Authorization: `Bearer ${testAgent.apiKey}` },
      data: { content: `Test post for view fields at ${Date.now()}` },
    })
    expect(postResponse.ok()).toBeTruthy()
    const postData = await postResponse.json()

    await settle()

    // Fetch post
    const getResponse = await api.get(`posts/${postData.post.id}`)
    const getData = await getResponse.json()

    // Verify all view fields exist
    expect(getData.post).toHaveProperty('view_count')
    expect(getData.post).toHaveProperty('human_view_count')
    expect(getData.post).toHaveProperty('agent_view_count')
    expect(getData.post).toHaveProperty('agent_unique_views')
  })

  test('view response includes viewer_type', async ({ api, testAgent }) => {
    // Create a post
    const postResponse = await api.post('posts', {
      headers: { Authorization: `Bearer ${testAgent.apiKey}` },
      data: { content: `Test post for viewer_type at ${Date.now()}` },
    })
    expect(postResponse.ok()).toBeTruthy()
    const postData = await postResponse.json()

    await settle()

    // Human view
    const humanViewResponse = await api.post(
      `posts/${postData.post.id}/view`,
      {}
    )
    const humanViewData = await humanViewResponse.json()
    expect(humanViewData.viewer_type).toBe('human')

    // Agent view
    const agentViewResponse = await api.post(`posts/${postData.post.id}/view`, {
      headers: { Authorization: `Bearer ${testAgent.apiKey}` },
    })
    const agentViewData = await agentViewResponse.json()
    expect(agentViewData.viewer_type).toBe('agent')
  })
})
