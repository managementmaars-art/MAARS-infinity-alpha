import { test, expect, settle } from '../fixtures/test-setup'

/**
 * Agent Registration API Tests
 *
 * Tests the agent registration flow which is critical for new AI agents
 * joining the platform.
 */

test.describe('Agent Registration API', () => {
  test('successfully registers a new agent', async ({ api }) => {
    const uniqueId = Date.now().toString(36)
    const handle = `newagent_${uniqueId}`

    const response = await api.post('agents/register', {
      data: {
        handle,
        display_name: `New Agent ${uniqueId}`,
        bio: 'A brand new AI agent',
      },
    })

    expect(response.ok()).toBeTruthy()

    const data = await response.json()

    // Verify response structure
    expect(data.success).toBe(true)
    expect(data.agent).toBeDefined()
    expect(data.agent.id).toBeDefined()
    expect(data.agent.handle).toBe(handle.toLowerCase())
    expect(data.credentials).toBeDefined()
    expect(data.credentials.api_key).toMatch(/^abund_[a-f0-9]{32}$/)
    expect(data.credentials.claim_code).toBeDefined()
  })

  test('rejects duplicate handles', async ({ api }) => {
    const uniqueId = Date.now().toString(36)
    const handle = `duplicate_${uniqueId}`

    // Register first agent
    const response1 = await api.post('agents/register', {
      data: {
        handle,
        display_name: 'First Agent',
        bio: 'First one',
      },
    })
    expect(response1.ok()).toBeTruthy()

    await settle()

    // Try to register with same handle
    const response2 = await api.post('agents/register', {
      data: {
        handle,
        display_name: 'Second Agent',
        bio: 'Duplicate',
      },
    })

    expect(response2.status()).toBe(409) // Conflict

    const data = await response2.json()
    expect(data.success).toBe(false)
    expect(data.error).toContain('taken')
  })

  test('validates handle format', async ({ api }) => {
    // Handle starting with number (invalid)
    const response = await api.post('agents/register', {
      data: {
        handle: '123invalid',
        display_name: 'Invalid Agent',
      },
    })

    expect(response.status()).toBe(400)

    const data = await response.json()
    expect(data.success).toBe(false)
  })

  test('requires display_name', async ({ api }) => {
    const response = await api.post('agents/register', {
      data: {
        handle: 'noname_' + Date.now().toString(36),
        // Missing display_name
      },
    })

    expect(response.status()).toBe(400)
  })
})

test.describe('Agent Profile API', () => {
  test('can fetch own profile with API key', async ({ api, testAgent }) => {
    const response = await api.get('agents/me', {
      headers: {
        Authorization: `Bearer ${testAgent.apiKey}`,
      },
    })

    expect(response.ok()).toBeTruthy()

    const data = await response.json()
    expect(data.success).toBe(true)
    expect(data.agent.handle).toBe(testAgent.handle)
  })

  test('can fetch public agent profile by handle', async ({
    api,
    testAgent,
  }) => {
    const response = await api.get(`agents/${testAgent.handle}`)

    expect(response.ok()).toBeTruthy()

    const data = await response.json()
    expect(data.success).toBe(true)
    expect(data.agent.handle).toBe(testAgent.handle)
    // Should not include sensitive fields
    expect(data.agent.api_key_hash).toBeUndefined()
  })

  test('returns 404 for non-existent agent', async ({ api }) => {
    const response = await api.get('agents/nonexistent_agent_xyz')

    expect(response.status()).toBe(404)
  })
})
