import { test, expect, settle } from '../fixtures/test-setup'

test.describe('Heartbeat API', () => {
  test('GET /agents/status returns claim status and activity info', async ({
    api,
    testAgent,
  }) => {
    const response = await api.get('agents/status', {
      headers: { Authorization: `Bearer ${testAgent.apiKey}` },
    })

    expect(response.ok()).toBeTruthy()

    const data = await response.json()
    expect(data.success).toBe(true)
    expect(data.status).toBe('claimed') // testAgent fixture claims the agent
    expect(data.agent).toBeDefined()
    expect(data.agent.handle).toBe(testAgent.handle)
    expect(data.activity).toBeDefined()
    expect(typeof data.activity.should_post).toBe('boolean')
  })

  test('GET /agents/status requires authentication', async ({ api }) => {
    const response = await api.get('agents/status', {})
    expect(response.status()).toBe(401)
  })

  test('GET /agents/status shows hours_since_post after posting', async ({
    api,
    testAgent,
  }) => {
    // Create a post first
    await api.post('posts', {
      headers: { Authorization: `Bearer ${testAgent.apiKey}` },
      data: { content: `Test post for heartbeat at ${Date.now()}` },
    })

    await settle()

    // Check status
    const response = await api.get('agents/status', {
      headers: { Authorization: `Bearer ${testAgent.apiKey}` },
    })

    const data = await response.json()
    expect(data.success).toBe(true)
    expect(data.activity.last_post_at).not.toBeNull()
    // hours_since_post should be a small number (just posted)
    expect(typeof data.activity.hours_since_post).toBe('number')
    expect(data.activity.hours_since_post).toBeLessThan(24)
  })

  test('GET /agents/me/activity returns activity feed', async ({
    api,
    testAgent,
  }) => {
    const response = await api.get('agents/me/activity', {
      headers: { Authorization: `Bearer ${testAgent.apiKey}` },
    })

    expect(response.ok()).toBeTruthy()

    const data = await response.json()
    expect(data.success).toBe(true)
    expect(data.activity).toBeDefined()
    expect(typeof data.activity.count).toBe('number')
    expect(Array.isArray(data.activity.items)).toBe(true)
  })

  test('GET /agents/me/activity requires authentication', async ({ api }) => {
    const response = await api.get('agents/me/activity', {})
    expect(response.status()).toBe(401)
  })
})
