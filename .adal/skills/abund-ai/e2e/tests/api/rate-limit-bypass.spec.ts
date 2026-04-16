import { test, expect, settle } from '../fixtures/test-setup'

/**
 * Rate Limit Bypass E2E Tests
 *
 * Verifies that the rate_limit_bypass flag on API keys is correctly
 * read by the rate limiting middleware. Uses the diagnostic
 * X-RateLimit-Bypass header that the middleware sets in development mode.
 */

test.describe('Rate Limit Bypass', () => {
  test('authenticated request without bypass does NOT have X-RateLimit-Bypass header', async ({
    api,
    testAgent,
  }) => {
    // Make an authenticated request — bypass should NOT be set
    const response = await api.get('posts?limit=1', {
      headers: { Authorization: `Bearer ${testAgent.apiKey}` },
    })

    expect(response.ok()).toBeTruthy()
    expect(response.headers()['x-ratelimit-bypass']).toBeUndefined()
  })

  test('enabling bypass sets X-RateLimit-Bypass header on subsequent requests', async ({
    api,
    testAgent,
  }) => {
    // Step 1: Verify no bypass header initially
    const before = await api.get('posts?limit=1', {
      headers: { Authorization: `Bearer ${testAgent.apiKey}` },
    })
    expect(before.ok()).toBeTruthy()
    expect(before.headers()['x-ratelimit-bypass']).toBeUndefined()

    // Step 2: Enable bypass via test endpoint
    const setBypass = await api.post('agents/test-set-bypass', {
      data: { api_key: testAgent.apiKey, bypass: true },
    })
    expect(setBypass.ok()).toBeTruthy()
    const bypassData = await setBypass.json()
    expect(bypassData.success).toBe(true)
    expect(bypassData.message).toContain('enabled')

    await settle()

    // Step 3: Verify bypass header is now present
    const after = await api.get('posts?limit=1', {
      headers: { Authorization: `Bearer ${testAgent.apiKey}` },
    })
    expect(after.ok()).toBeTruthy()
    expect(after.headers()['x-ratelimit-bypass']).toBe('true')
  })

  test('disabling bypass removes X-RateLimit-Bypass header', async ({
    api,
    testAgent,
  }) => {
    // Step 1: Enable bypass
    const enable = await api.post('agents/test-set-bypass', {
      data: { api_key: testAgent.apiKey, bypass: true },
    })
    expect(enable.ok()).toBeTruthy()

    await settle()

    // Step 2: Verify it's on
    const withBypass = await api.get('posts?limit=1', {
      headers: { Authorization: `Bearer ${testAgent.apiKey}` },
    })
    expect(withBypass.headers()['x-ratelimit-bypass']).toBe('true')

    // Step 3: Disable bypass
    const disable = await api.post('agents/test-set-bypass', {
      data: { api_key: testAgent.apiKey, bypass: false },
    })
    expect(disable.ok()).toBeTruthy()
    const disableData = await disable.json()
    expect(disableData.message).toContain('disabled')

    await settle()

    // Step 4: Verify it's off
    const withoutBypass = await api.get('posts?limit=1', {
      headers: { Authorization: `Bearer ${testAgent.apiKey}` },
    })
    expect(withoutBypass.headers()['x-ratelimit-bypass']).toBeUndefined()
  })

  test('bypass flag is per-key, not global', async ({ api, testAgent }) => {
    // Enable bypass on the test agent
    const enable = await api.post('agents/test-set-bypass', {
      data: { api_key: testAgent.apiKey, bypass: true },
    })
    expect(enable.ok()).toBeTruthy()

    await settle()

    // Unauthenticated request should NOT have bypass header
    const unauthResponse = await api.get('posts?limit=1')
    expect(unauthResponse.ok()).toBeTruthy()
    expect(unauthResponse.headers()['x-ratelimit-bypass']).toBeUndefined()

    // Authenticated request SHOULD have bypass header
    const authResponse = await api.get('posts?limit=1', {
      headers: { Authorization: `Bearer ${testAgent.apiKey}` },
    })
    expect(authResponse.ok()).toBeTruthy()
    expect(authResponse.headers()['x-ratelimit-bypass']).toBe('true')
  })

  test('test-set-bypass rejects invalid input', async ({ api }) => {
    // Missing fields
    const noBody = await api.post('agents/test-set-bypass', {
      data: {},
    })
    expect(noBody.status()).toBe(400)

    // Missing bypass field
    const noBypass = await api.post('agents/test-set-bypass', {
      data: { api_key: 'abund_fakekeyfakekeyfake' },
    })
    expect(noBypass.status()).toBe(400)
  })

  test('test-set-bypass returns 404 for non-existent key', async ({ api }) => {
    const response = await api.post('agents/test-set-bypass', {
      data: {
        api_key: 'abund_0000000000000000000000000000000000000',
        bypass: true,
      },
    })
    expect(response.status()).toBe(404)
  })
})
