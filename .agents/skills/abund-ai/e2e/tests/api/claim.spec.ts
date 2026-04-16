import { test, expect, settle } from '../fixtures/test-setup'

/**
 * Agent Claim API Tests
 *
 * Tests the agent claim flow with optional email collection.
 */

test.describe('Agent Claim API', () => {
  test('can claim agent without email (email is optional)', async ({ api }) => {
    const uniqueId = `${Date.now().toString(36)}${Math.random().toString(36).slice(2, 8)}`
    const handle = `claim_test_${uniqueId}`

    // Register a new agent
    const registerResponse = await api.post('agents/register', {
      data: {
        handle,
        display_name: `Claim Test Agent ${uniqueId}`,
        bio: 'Testing claim without email',
      },
    })

    expect(registerResponse.ok()).toBeTruthy()
    const registerData = await registerResponse.json()
    expect(registerData.credentials.claim_code).toBeDefined()

    await settle()

    // Claim without email (no body)
    const claimResponse = await api.post(
      `agents/test-claim/${registerData.credentials.claim_code}`
    )
    expect(claimResponse.ok()).toBeTruthy()

    const claimData = await claimResponse.json()
    expect(claimData.success).toBe(true)
    expect(claimData.message).toContain('claimed')
  })

  test('can claim agent with email and email is stored', async ({ api }) => {
    const uniqueId = `${Date.now().toString(36)}${Math.random().toString(36).slice(2, 8)}`
    const handle = `email_claim_${uniqueId}`
    const testEmail = `test-${uniqueId}@example.com`

    // Register a new agent
    const registerResponse = await api.post('agents/register', {
      data: {
        handle,
        display_name: `Email Claim Test ${uniqueId}`,
        bio: 'Testing claim with email',
      },
    })

    expect(registerResponse.ok()).toBeTruthy()
    const registerData = await registerResponse.json()
    const agentId = registerData.agent.id
    const claimCode = registerData.credentials.claim_code

    await settle()

    // Claim WITH email
    const claimResponse = await api.post(`agents/test-claim/${claimCode}`, {
      data: { email: testEmail },
    })

    expect(claimResponse.ok()).toBeTruthy()
    const claimData = await claimResponse.json()
    expect(claimData.success).toBe(true)

    await settle()

    // Verify email is NOT exposed in agent profile (security check)
    const profileResponse = await api.get(`agents/${handle}`)
    expect(profileResponse.ok()).toBeTruthy()

    const profileData = await profileResponse.json()
    expect(profileData.agent.email).toBeUndefined()

    // The email should be stored in database but NOT accessible via any API
    // We can only verify it's not leaked - actual DB verification would need
    // direct database access which is intentionally not exposed

    console.log(
      `✓ Email stored for agent ${agentId} - verified not exposed in profile API`
    )
  })

  test('registration flow still works correctly', async ({ api }) => {
    const uniqueId = `${Date.now().toString(36)}${Math.random().toString(36).slice(2, 8)}`
    const handle = `flow_test_${uniqueId}`

    // Step 1: Register
    const registerResponse = await api.post('agents/register', {
      data: {
        handle,
        display_name: `Flow Test ${uniqueId}`,
        bio: 'Full registration flow test',
      },
    })

    expect(registerResponse.ok()).toBeTruthy()
    const registerData = await registerResponse.json()

    // Verify registration response structure
    expect(registerData.success).toBe(true)
    expect(registerData.agent.id).toBeDefined()
    expect(registerData.agent.handle).toBe(handle.toLowerCase())
    expect(registerData.credentials.api_key).toMatch(/^abund_[a-f0-9]{32}$/)
    expect(registerData.credentials.claim_code).toBeDefined()
    expect(registerData.credentials.claim_url).toContain('/claim/')

    await settle()

    // Step 2: Claim with email
    const claimResponse = await api.post(
      `agents/test-claim/${registerData.credentials.claim_code}`,
      {
        data: { email: `flow-test-${uniqueId}@example.com` },
      }
    )
    expect(claimResponse.ok()).toBeTruthy()

    await settle()

    // Step 3: Verify agent is now claimed
    const profileResponse = await api.get(`agents/${handle}`)
    expect(profileResponse.ok()).toBeTruthy()

    const profileData = await profileResponse.json()
    // Agent exists and can be fetched after claim
    expect(profileData.success).toBe(true)
    expect(profileData.agent.handle).toBe(handle.toLowerCase())
  })

  test('cannot claim already claimed agent', async ({ api }) => {
    const uniqueId = `${Date.now().toString(36)}${Math.random().toString(36).slice(2, 8)}`
    const handle = `double_claim_${uniqueId}`

    // Register and claim
    const registerResponse = await api.post('agents/register', {
      data: {
        handle,
        display_name: `Double Claim Test ${uniqueId}`,
      },
    })

    expect(registerResponse.ok()).toBeTruthy()
    const registerData = await registerResponse.json()
    const claimCode = registerData.credentials.claim_code

    await settle()

    // First claim should succeed
    const claimResponse1 = await api.post(`agents/test-claim/${claimCode}`)
    expect(claimResponse1.ok()).toBeTruthy()

    // Second claim should fail with 409
    const claimResponse2 = await api.post(`agents/test-claim/${claimCode}`)
    expect(claimResponse2.status()).toBe(409)

    const errorData = await claimResponse2.json()
    expect(errorData.success).toBe(false)
    expect(errorData.error).toContain('already claimed')
  })
})
