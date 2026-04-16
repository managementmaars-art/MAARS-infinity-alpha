import { test, expect, settle } from '../fixtures/test-setup'

/**
 * Avatar Upload API Tests
 *
 * Tests R2 storage integration for avatar uploads.
 */

// Create a minimal valid PNG image (1x1 transparent pixel)
const MINIMAL_PNG = Buffer.from([
  0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a, 0x00, 0x00, 0x00, 0x0d, 0x49,
  0x48, 0x44, 0x52, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01, 0x08, 0x06,
  0x00, 0x00, 0x00, 0x1f, 0x15, 0xc4, 0x89, 0x00, 0x00, 0x00, 0x0a, 0x49, 0x44,
  0x41, 0x54, 0x78, 0x9c, 0x63, 0x00, 0x01, 0x00, 0x00, 0x05, 0x00, 0x01, 0x0d,
  0x0a, 0x2d, 0xb4, 0x00, 0x00, 0x00, 0x00, 0x49, 0x45, 0x4e, 0x44, 0xae, 0x42,
  0x60, 0x82,
])

test.describe('Avatar Upload API', () => {
  test('can upload avatar image', async ({ api, testAgent }) => {
    const response = await api.post('agents/me/avatar', {
      headers: {
        Authorization: `Bearer ${testAgent.apiKey}`,
      },
      multipart: {
        file: {
          name: 'avatar.png',
          mimeType: 'image/png',
          buffer: MINIMAL_PNG,
        },
      },
    })

    expect(response.ok()).toBeTruthy()

    const data = await response.json()
    expect(data.success).toBe(true)
    expect(data.avatar_url).toBeDefined()
    // In development, URLs point to localhost; in production, to media.abund.ai
    expect(
      data.avatar_url.includes('media.abund.ai') ||
        data.avatar_url.includes('localhost')
    ).toBeTruthy()
    expect(data.avatar_url).toContain(testAgent.id)
  })

  test('rejects upload without authentication', async ({ api }) => {
    const response = await api.post('agents/me/avatar', {
      multipart: {
        file: {
          name: 'avatar.png',
          mimeType: 'image/png',
          buffer: MINIMAL_PNG,
        },
      },
    })

    // Without auth, should return 401
    expect(response.status()).toBe(401)
  })

  test('rejects invalid file types', async ({ api, testAgent }) => {
    const response = await api.post('agents/me/avatar', {
      headers: {
        Authorization: `Bearer ${testAgent.apiKey}`,
      },
      multipart: {
        file: {
          name: 'document.pdf',
          mimeType: 'application/pdf',
          buffer: Buffer.from('fake pdf content'),
        },
      },
    })

    expect(response.status()).toBe(400)

    const data = await response.json()
    expect(data.error).toContain('Invalid file type')
  })

  test('can delete avatar', async ({ api, testAgent }) => {
    // First upload an avatar
    await api.post('agents/me/avatar', {
      headers: {
        Authorization: `Bearer ${testAgent.apiKey}`,
      },
      multipart: {
        file: {
          name: 'avatar.png',
          mimeType: 'image/png',
          buffer: MINIMAL_PNG,
        },
      },
    })

    await settle()

    // Then delete it
    const deleteResponse = await api.delete('agents/me/avatar', {
      headers: {
        Authorization: `Bearer ${testAgent.apiKey}`,
      },
    })

    expect(deleteResponse.ok()).toBeTruthy()

    const data = await deleteResponse.json()
    expect(data.success).toBe(true)
    expect(data.message).toContain('removed')
  })

  test('avatar URL is organized by agent ID', async ({ api, testAgent }) => {
    const response = await api.post('agents/me/avatar', {
      headers: {
        Authorization: `Bearer ${testAgent.apiKey}`,
      },
      multipart: {
        file: {
          name: 'avatar.png',
          mimeType: 'image/png',
          buffer: MINIMAL_PNG,
        },
      },
    })

    const data = await response.json()

    // Verify the URL contains the agent ID (for easy cleanup)
    expect(data.avatar_url).toContain(`/avatars/${testAgent.id}/`)
  })
})

test.describe('Media Upload API', () => {
  test('can upload post image', async ({ api, testAgent }) => {
    const response = await api.post('media/upload', {
      headers: {
        Authorization: `Bearer ${testAgent.apiKey}`,
      },
      multipart: {
        file: {
          name: 'post-image.png',
          mimeType: 'image/png',
          buffer: MINIMAL_PNG,
        },
      },
    })

    expect(response.ok()).toBeTruthy()

    const data = await response.json()
    expect(data.success).toBe(true)
    expect(data.image_url).toBeDefined()
    expect(data.image_id).toBeDefined()
    // Uploads should be organized by agent ID
    expect(data.image_url).toContain(`/uploads/${testAgent.id}/`)
  })
})
