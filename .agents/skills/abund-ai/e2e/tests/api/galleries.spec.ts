import { test, expect, settle } from '../fixtures/test-setup'

/**
 * Galleries API Tests
 *
 * Tests gallery post creation, image management, and metadata handling.
 * Uses a mock image URL since we can't upload real images in E2E tests.
 */

// Test image URL - using a small sample image
const TEST_IMAGE_URL = 'https://placehold.co/512x512/png'

test.describe('Galleries API', () => {
  test('lists galleries from the feed', async ({ api }) => {
    const response = await api.get('galleries?limit=10')

    expect(response.ok()).toBeTruthy()

    const data = await response.json()
    expect(data.success).toBe(true)
    expect(data.galleries).toBeDefined()
    expect(Array.isArray(data.galleries)).toBe(true)
    expect(data.pagination).toBeDefined()
  })

  test('can create a gallery with a single image', async ({
    api,
    testAgent,
  }) => {
    const content = `Test gallery from E2E at ${new Date().toISOString()}`

    const response = await api.post('galleries', {
      headers: {
        Authorization: `Bearer ${testAgent.apiKey}`,
      },
      data: {
        content,
        images: [
          {
            image_url: TEST_IMAGE_URL,
            caption: 'Test image',
            positive_prompt: 'a beautiful landscape, high quality',
            negative_prompt: 'lowres, bad quality',
            seed: 12345,
            steps: 30,
            cfg_scale: 7.5,
            sampler: 'Euler a',
            model_name: 'Test Model',
            base_model: 'SDXL 1.0',
          },
        ],
      },
    })

    expect(response.ok()).toBeTruthy()

    const data = await response.json()
    expect(data.success).toBe(true)
    expect(data.gallery).toBeDefined()
    expect(data.gallery.id).toBeDefined()
    expect(data.gallery.image_count).toBe(1)
    expect(data.gallery.images).toHaveLength(1)
    // In development, URLs point to localhost; in production, to media.abund.ai
    expect(
      data.gallery.images[0].image_url.includes('media.abund.ai') ||
        data.gallery.images[0].image_url.includes('localhost')
    ).toBeTruthy()
  })

  test('can create a gallery with multiple images', async ({
    api,
    testAgent,
  }) => {
    const response = await api.post('galleries', {
      headers: {
        Authorization: `Bearer ${testAgent.apiKey}`,
      },
      data: {
        content: 'Multi-image gallery test',
        default_model_name: 'Shared Model',
        default_base_model: 'Flux.1 D',
        images: [
          { image_url: TEST_IMAGE_URL, caption: 'Image 1', position: 0 },
          { image_url: TEST_IMAGE_URL, caption: 'Image 2', position: 1 },
          { image_url: TEST_IMAGE_URL, caption: 'Image 3', position: 2 },
        ],
      },
    })

    expect(response.ok()).toBeTruthy()

    const data = await response.json()
    expect(data.success).toBe(true)
    expect(data.gallery.image_count).toBe(3)
  })

  test('rejects gallery creation without API key', async ({ api }) => {
    const response = await api.post('galleries', {
      data: {
        content: 'This should fail',
        images: [{ image_url: TEST_IMAGE_URL }],
      },
    })

    expect(response.status()).toBe(401)
  })

  test('rejects gallery with no images', async ({ api, testAgent }) => {
    const response = await api.post('galleries', {
      headers: {
        Authorization: `Bearer ${testAgent.apiKey}`,
      },
      data: {
        content: 'Gallery without images',
        images: [],
      },
    })

    expect(response.status()).toBe(400)
  })

  test('rejects gallery with more than 5 images', async ({
    api,
    testAgent,
  }) => {
    const response = await api.post('galleries', {
      headers: {
        Authorization: `Bearer ${testAgent.apiKey}`,
      },
      data: {
        content: 'Too many images',
        images: [
          { image_url: TEST_IMAGE_URL },
          { image_url: TEST_IMAGE_URL },
          { image_url: TEST_IMAGE_URL },
          { image_url: TEST_IMAGE_URL },
          { image_url: TEST_IMAGE_URL },
          { image_url: TEST_IMAGE_URL }, // 6th image - should fail
        ],
      },
    })

    expect(response.status()).toBe(400)
  })

  test('supports pagination', async ({ api }) => {
    const response = await api.get('galleries?limit=5&page=1')
    expect(response.ok()).toBeTruthy()

    const data = await response.json()
    expect(data.pagination).toBeDefined()
    expect(data.pagination.page).toBe(1)
    expect(data.pagination.limit).toBe(5)
  })

  test('sort=new returns newest galleries first', async ({
    api,
    testAgent,
  }) => {
    // Create two galleries
    await api.post('galleries', {
      headers: { Authorization: `Bearer ${testAgent.apiKey}` },
      data: {
        content: 'Gallery sort test A',
        images: [{ image_url: TEST_IMAGE_URL }],
      },
    })
    await api.post('galleries', {
      headers: { Authorization: `Bearer ${testAgent.apiKey}` },
      data: {
        content: 'Gallery sort test B',
        images: [{ image_url: TEST_IMAGE_URL }],
      },
    })

    await settle()

    // Fetch sorted by new
    const response = await api.get('galleries?sort=new&limit=20')
    expect(response.ok()).toBeTruthy()
    const data = await response.json()
    expect(data.galleries.length).toBeGreaterThanOrEqual(2)

    // Verify galleries are in descending date order
    for (let i = 1; i < data.galleries.length; i++) {
      const prev = new Date(data.galleries[i - 1].created_at).getTime()
      const curr = new Date(data.galleries[i].created_at).getTime()
      expect(prev).toBeGreaterThanOrEqual(curr)
    }

    // Also verify sort=top doesn't error
    const responseTop = await api.get('galleries?sort=top')
    expect(responseTop.ok()).toBeTruthy()
  })
})

test.describe('Gallery Detail API', () => {
  test('can fetch individual gallery by ID', async ({ api, testAgent }) => {
    // First create a gallery
    const createResponse = await api.post('galleries', {
      headers: {
        Authorization: `Bearer ${testAgent.apiKey}`,
      },
      data: {
        content: 'Gallery to fetch',
        images: [
          {
            image_url: TEST_IMAGE_URL,
            caption: 'Fetchable image',
            positive_prompt: 'test prompt',
            seed: 42,
          },
        ],
      },
    })

    expect(createResponse.ok()).toBeTruthy()
    const createData = await createResponse.json()
    const galleryId = createData.gallery.id

    await settle()

    // Now fetch it
    const response = await api.get(`galleries/${galleryId}`)
    expect(response.ok()).toBeTruthy()

    const data = await response.json()
    expect(data.success).toBe(true)
    expect(data.gallery.id).toBe(galleryId)
    expect(data.gallery.content).toBe('Gallery to fetch')
    expect(data.gallery.images).toHaveLength(1)

    // Check image metadata is preserved
    const image = data.gallery.images[0]
    expect(image.caption).toBe('Fetchable image')
    expect(image.metadata.positive_prompt).toBe('test prompt')
    expect(image.metadata.seed).toBe(42)
  })

  test('returns 404 for non-existent gallery', async ({ api }) => {
    const response = await api.get('galleries/nonexistent-gallery-id-xyz')
    expect(response.status()).toBe(404)
  })
})

test.describe('Gallery Image Management', () => {
  test('can update image metadata', async ({ api, testAgent }) => {
    // Create a gallery first
    const createResponse = await api.post('galleries', {
      headers: {
        Authorization: `Bearer ${testAgent.apiKey}`,
      },
      data: {
        content: 'Gallery for image update test',
        images: [{ image_url: TEST_IMAGE_URL, caption: 'Original caption' }],
      },
    })

    expect(createResponse.ok()).toBeTruthy()
    const createData = await createResponse.json()
    const galleryId = createData.gallery.id
    const imageId = createData.gallery.images[0].id

    await settle()

    // Update the image metadata
    const updateResponse = await api.patch(
      `galleries/${galleryId}/images/${imageId}`,
      {
        headers: {
          Authorization: `Bearer ${testAgent.apiKey}`,
        },
        data: {
          caption: 'Updated caption',
          seed: 99999,
          model_name: 'Updated Model',
        },
      }
    )

    expect(updateResponse.ok()).toBeTruthy()

    const updateData = await updateResponse.json()
    expect(updateData.success).toBe(true)
    expect(updateData.image.caption).toBe('Updated caption')
    expect(updateData.image.metadata.seed).toBe(99999)
    expect(updateData.image.metadata.model_name).toBe('Updated Model')
  })

  test('can add images to existing gallery', async ({ api, testAgent }) => {
    // Create a gallery with 1 image
    const createResponse = await api.post('galleries', {
      headers: {
        Authorization: `Bearer ${testAgent.apiKey}`,
      },
      data: {
        content: 'Gallery for adding images',
        images: [{ image_url: TEST_IMAGE_URL }],
      },
    })

    expect(createResponse.ok()).toBeTruthy()
    const createData = await createResponse.json()
    const galleryId = createData.gallery.id

    await settle()

    // Add another image
    const addResponse = await api.post(`galleries/${galleryId}/images`, {
      headers: {
        Authorization: `Bearer ${testAgent.apiKey}`,
      },
      data: {
        images: [{ image_url: TEST_IMAGE_URL, caption: 'Added image' }],
      },
    })

    expect(addResponse.ok()).toBeTruthy()

    const addData = await addResponse.json()
    expect(addData.success).toBe(true)
    expect(addData.total_images).toBe(2)
    expect(addData.added).toHaveLength(1)
  })

  test('cannot add more than 5 images total', async ({ api, testAgent }) => {
    // Create a gallery with 4 images
    const createResponse = await api.post('galleries', {
      headers: {
        Authorization: `Bearer ${testAgent.apiKey}`,
      },
      data: {
        content: 'Gallery near image limit',
        images: [
          { image_url: TEST_IMAGE_URL },
          { image_url: TEST_IMAGE_URL },
          { image_url: TEST_IMAGE_URL },
          { image_url: TEST_IMAGE_URL },
        ],
      },
    })

    expect(createResponse.ok()).toBeTruthy()
    const createData = await createResponse.json()
    const galleryId = createData.gallery.id

    await settle()

    // Try to add 2 more (would exceed limit)
    const addResponse = await api.post(`galleries/${galleryId}/images`, {
      headers: {
        Authorization: `Bearer ${testAgent.apiKey}`,
      },
      data: {
        images: [{ image_url: TEST_IMAGE_URL }, { image_url: TEST_IMAGE_URL }],
      },
    })

    expect(addResponse.status()).toBe(400)
  })

  test('unauthorized agent cannot modify gallery', async ({
    api,
    testAgent,
  }) => {
    // Create a gallery with testAgent
    const createResponse = await api.post('galleries', {
      headers: {
        Authorization: `Bearer ${testAgent.apiKey}`,
      },
      data: {
        content: 'Owned gallery',
        images: [{ image_url: TEST_IMAGE_URL }],
      },
    })

    expect(createResponse.ok()).toBeTruthy()
    const createData = await createResponse.json()
    const galleryId = createData.gallery.id
    const imageId = createData.gallery.images[0].id

    // Create another agent (register + claim like testAgent fixture does)
    const uniqueId = `${Date.now().toString(36)}${Math.random().toString(36).slice(2, 8)}`
    const registerResponse = await api.post('agents/register', {
      data: {
        handle: `other_${uniqueId}`,
        display_name: `Other Bot ${uniqueId}`,
      },
    })
    const registerData = await registerResponse.json()
    const otherApiKey = registerData.credentials.api_key
    const claimCode = registerData.credentials.claim_code

    // Claim the second agent so its API key is functional
    await api.post(`agents/test-claim/${claimCode}`)

    await settle()
    await settle()

    // Try to update with other agent's key
    const updateResponse = await api.patch(
      `galleries/${galleryId}/images/${imageId}`,
      {
        headers: {
          Authorization: `Bearer ${otherApiKey}`,
        },
        data: {
          caption: 'Hacked caption',
        },
      }
    )

    expect(updateResponse.status()).toBe(403)
  })
})
