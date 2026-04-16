/**
 * LetzAI Image Generation Examples
 * 
 * This file demonstrates how to generate images using the LetzAI API
 * with various models and configurations.
 */

const API_BASE_URL = 'https://api.letz.ai';

// Replace with your actual API key
const API_KEY = process.env.LETZAI_API_KEY || 'YOUR_API_KEY';

const headers = {
  'Content-Type': 'application/json',
  'Authorization': `Bearer ${API_KEY}`
};

/**
 * Sleep utility for polling
 */
const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

/**
 * Poll for image completion
 * @param {string} imageId - The image generation job ID
 * @param {number} intervalMs - Polling interval in milliseconds (default: 3000)
 * @param {number} maxAttempts - Maximum polling attempts (default: 60)
 * @returns {Promise<Object>} - The completed image object
 */
async function pollImageStatus(imageId, intervalMs = 3000, maxAttempts = 60) {
  for (let attempt = 0; attempt < maxAttempts; attempt++) {
    const response = await fetch(`${API_BASE_URL}/images/${imageId}`, { headers });
    const data = await response.json();
    
    console.log(`Attempt ${attempt + 1}: Status = ${data.status}`);
    
    if (data.status === 'ready') {
      return data;
    }
    
    if (data.status === 'failed') {
      throw new Error(`Image generation failed: ${data.error || 'Unknown error'}`);
    }
    
    await sleep(intervalMs);
  }
  
  throw new Error('Image generation timed out');
}

/**
 * Example 1: Basic Image Generation with Nano Banana Pro
 * 
 * Uses the recommended model for high-quality images
 */
async function generateBasicImage() {
  console.log('=== Basic Image Generation ===\n');
  
  const response = await fetch(`${API_BASE_URL}/images`, {
    method: 'POST',
    headers,
    body: JSON.stringify({
      prompt: 'A beautiful sunset over a calm ocean with vibrant orange and purple colors',
      baseModel: 'gemini-3-pro-image-preview',
      mode: '2k'
    })
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(`API Error: ${error.error}`);
  }
  
  const { id } = await response.json();
  console.log(`Image generation started. ID: ${id}`);
  
  const result = await pollImageStatus(id);
  console.log(`\nImage ready!`);
  console.log(`URL: ${result.imageVersions.original}`);
  console.log(`Credits used: ${result.creditsUsed}`);
  
  return result;
}

/**
 * Example 2: High-Resolution Image with Custom Dimensions
 * 
 * Generates a 4K image with specific dimensions
 */
async function generateHighResImage() {
  console.log('=== High-Resolution Image Generation ===\n');
  
  const response = await fetch(`${API_BASE_URL}/images`, {
    method: 'POST',
    headers,
    body: JSON.stringify({
      prompt: 'A majestic eagle soaring through snow-capped mountains, dramatic lighting, photorealistic',
      baseModel: 'gemini-3-pro-image-preview',
      mode: '4k',
      width: 2160,
      height: 1440,
      negativePrompt: 'blurry, low quality, distorted'
    })
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(`API Error: ${error.error}`);
  }
  
  const { id } = await response.json();
  console.log(`High-res generation started. ID: ${id}`);
  
  const result = await pollImageStatus(id);
  console.log(`\nImage ready!`);
  console.log(`URL: ${result.imageVersions.original}`);
  console.log(`Dimensions: ${result.width}x${result.height}`);
  
  return result;
}

/**
 * Example 3: Image Generation with Flux2 Max
 * 
 * Uses the Flux2 Max model for creative styles
 */
async function generateFlux2Image() {
  console.log('=== Flux2 Max Image Generation ===\n');
  
  const response = await fetch(`${API_BASE_URL}/images`, {
    method: 'POST',
    headers,
    body: JSON.stringify({
      prompt: 'Cyberpunk city street at night, neon lights reflecting on wet pavement, futuristic',
      baseModel: 'flux2-max',
      mode: 'hd',
      aspectRatio: '16:9'
    })
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(`API Error: ${error.error}`);
  }
  
  const { id } = await response.json();
  console.log(`Flux2 generation started. ID: ${id}`);
  
  const result = await pollImageStatus(id);
  console.log(`\nImage ready!`);
  console.log(`URL: ${result.imageVersions.original}`);
  
  return result;
}

/**
 * Example 4: Image Generation with SeeDream
 * 
 * Uses the SeeDream 4.5 model
 */
async function generateSeeDreamImage() {
  console.log('=== SeeDream Image Generation ===\n');
  
  const response = await fetch(`${API_BASE_URL}/images`, {
    method: 'POST',
    headers,
    body: JSON.stringify({
      prompt: 'A serene Japanese garden with cherry blossoms, koi pond, and wooden bridge',
      baseModel: 'seedream-4-5-251128',
      mode: '2k'
    })
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(`API Error: ${error.error}`);
  }
  
  const { id } = await response.json();
  console.log(`SeeDream generation started. ID: ${id}`);
  
  const result = await pollImageStatus(id);
  console.log(`\nImage ready!`);
  console.log(`URL: ${result.imageVersions.original}`);
  
  return result;
}

/**
 * Example 5: Reproducible Generation with Seed
 * 
 * Uses a seed for reproducible results
 */
async function generateWithSeed() {
  console.log('=== Reproducible Generation with Seed ===\n');
  
  const seed = 12345;
  
  const response = await fetch(`${API_BASE_URL}/images`, {
    method: 'POST',
    headers,
    body: JSON.stringify({
      prompt: 'A fantasy castle on a floating island surrounded by clouds',
      baseModel: 'gemini-3-pro-image-preview',
      mode: '2k',
      seed: seed
    })
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(`API Error: ${error.error}`);
  }
  
  const { id } = await response.json();
  console.log(`Generation with seed ${seed} started. ID: ${id}`);
  
  const result = await pollImageStatus(id);
  console.log(`\nImage ready!`);
  console.log(`URL: ${result.imageVersions.original}`);
  console.log(`Use the same seed (${seed}) to reproduce this exact image`);
  
  return result;
}

/**
 * Example 6: Batch Generation with Different Models
 * 
 * Generates multiple images with different models in parallel
 */
async function generateBatch() {
  console.log('=== Batch Generation ===\n');
  
  const prompts = [
    {
      prompt: 'Abstract art with flowing colors',
      baseModel: 'gemini-3-pro-image-preview',
      mode: 'default'
    },
    {
      prompt: 'Abstract art with flowing colors',
      baseModel: 'flux2-max',
      mode: '1k'
    },
    {
      prompt: 'Abstract art with flowing colors',
      baseModel: 'seedream-4-5-251128',
      mode: '2k'
    }
  ];
  
  // Start all generations
  const startPromises = prompts.map(async (config) => {
    const response = await fetch(`${API_BASE_URL}/images`, {
      method: 'POST',
      headers,
      body: JSON.stringify(config)
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(`API Error: ${error.error}`);
    }
    
    const data = await response.json();
    console.log(`Started ${config.baseModel}: ${data.id}`);
    return { ...data, model: config.baseModel };
  });
  
  const jobs = await Promise.all(startPromises);
  
  // Poll all in parallel
  const results = await Promise.all(
    jobs.map(job => pollImageStatus(job.id))
  );
  
  console.log('\n=== All Images Ready ===');
  results.forEach((result, i) => {
    console.log(`\n${jobs[i].model}:`);
    console.log(`  URL: ${result.imageVersions.original}`);
    console.log(`  Credits: ${result.creditsUsed}`);
  });
  
  return results;
}

/**
 * Example 7: Error Handling
 * 
 * Demonstrates proper error handling
 */
async function generateWithErrorHandling() {
  console.log('=== Image Generation with Error Handling ===\n');
  
  try {
    const response = await fetch(`${API_BASE_URL}/images`, {
      method: 'POST',
      headers,
      body: JSON.stringify({
        prompt: 'A beautiful landscape',
        baseModel: 'gemini-3-pro-image-preview',
        mode: '2k'
      })
    });
    
    // Handle HTTP errors
    if (!response.ok) {
      const error = await response.json();
      
      switch (response.status) {
        case 401:
          throw new Error('Invalid API key. Please check your credentials.');
        case 402:
          throw new Error('Insufficient credits. Please top up at letz.ai/subscription');
        case 400:
          throw new Error(`Invalid parameters: ${error.error}`);
        case 429:
          throw new Error('Rate limited. Please wait before making more requests.');
        default:
          throw new Error(`API Error (${response.status}): ${error.error}`);
      }
    }
    
    const { id } = await response.json();
    console.log(`Generation started. ID: ${id}`);
    
    const result = await pollImageStatus(id);
    console.log(`\nImage ready!`);
    console.log(`URL: ${result.imageVersions.original}`);
    
    return result;
    
  } catch (error) {
    console.error(`Error: ${error.message}`);
    
    // Implement retry logic for transient errors
    if (error.message.includes('Rate limited')) {
      console.log('Retrying after delay...');
      await sleep(5000);
      // Could retry here
    }
    
    throw error;
  }
}

// =============================================================================
// Context Editing Examples
// =============================================================================

/**
 * Poll for image edit completion
 * @param {string} editId - The image edit job ID
 * @param {number} intervalMs - Polling interval in milliseconds (default: 3000)
 * @param {number} maxAttempts - Maximum polling attempts (default: 60)
 * @returns {Promise<Object>} - The completed edit object
 */
async function pollEditStatus(editId, intervalMs = 3000, maxAttempts = 60) {
  for (let attempt = 0; attempt < maxAttempts; attempt++) {
    const response = await fetch(`${API_BASE_URL}/image-edits/${editId}`, { headers });
    const data = await response.json();
    
    console.log(`Attempt ${attempt + 1}: Status = ${data.status}`);
    
    if (data.status === 'ready') {
      return data;
    }
    
    if (data.status === 'failed') {
      throw new Error(`Image edit failed: ${data.error || 'Unknown error'}`);
    }
    
    await sleep(intervalMs);
  }
  
  throw new Error('Image edit timed out');
}

/**
 * Example: Context Editing - Single Image
 * 
 * Edits an existing image using AI-powered context editing
 */
async function contextEditSingleImage(imageUrl, editPrompt) {
  console.log('=== Context Edit - Single Image ===\n');
  
  const response = await fetch(`${API_BASE_URL}/image-edits`, {
    method: 'POST',
    headers,
    body: JSON.stringify({
      mode: 'context',
      prompt: editPrompt,
      imageUrl: imageUrl,
      settings: {
        resolution: '2k',
        aspect_ratio: '16:9',
        model: 'gemini-3-pro-image-preview'
      }
    })
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(`API Error: ${error.error}`);
  }
  
  const { id } = await response.json();
  console.log(`Edit started. ID: ${id}`);
  
  const result = await pollEditStatus(id);
  console.log(`\nEdit complete!`);
  console.log(`Edited image: ${result.generatedImageCompletion.imageVersions.original}`);
  
  return result;
}

/**
 * Example: Context Editing - Multi-Reference
 * 
 * Uses multiple reference images for editing
 */
async function contextEditMultiReference(imageUrls, editPrompt) {
  console.log('=== Context Edit - Multi-Reference ===\n');
  
  if (imageUrls.length > 9) {
    throw new Error('Maximum 9 reference images allowed');
  }
  
  const response = await fetch(`${API_BASE_URL}/image-edits`, {
    method: 'POST',
    headers,
    body: JSON.stringify({
      mode: 'context',
      prompt: editPrompt,
      inputImageUrls: imageUrls,
      settings: {
        resolution: '4k',
        model: 'gemini-3-pro-image-preview'
      }
    })
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(`API Error: ${error.error}`);
  }
  
  const { id } = await response.json();
  console.log(`Multi-reference edit started. ID: ${id}`);
  
  const result = await pollEditStatus(id);
  console.log(`\nEdit complete!`);
  console.log(`Edited image: ${result.generatedImageCompletion.imageVersions.original}`);
  
  return result;
}

/**
 * Example: Edit Previously Generated LetzAI Image
 * 
 * Uses originalImageCompletionId to edit an existing LetzAI image
 */
async function editLetzAIImage(imageCompletionId, editPrompt) {
  console.log('=== Edit LetzAI Image ===\n');
  
  const response = await fetch(`${API_BASE_URL}/image-edits`, {
    method: 'POST',
    headers,
    body: JSON.stringify({
      mode: 'context',
      prompt: editPrompt,
      originalImageCompletionId: imageCompletionId,
      settings: {
        resolution: '2k',
        model: 'gemini-3-pro-image-preview'
      }
    })
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(`API Error: ${error.error}`);
  }
  
  const { id } = await response.json();
  console.log(`Edit of ${imageCompletionId} started. ID: ${id}`);
  
  const result = await pollEditStatus(id);
  console.log(`\nEdit complete!`);
  console.log(`Original: ${result.originalImageCompletion?.imageVersions?.original || 'N/A'}`);
  console.log(`Edited: ${result.generatedImageCompletion.imageVersions.original}`);
  
  return result;
}

// =============================================================================
// Custom Trained Models Examples
// =============================================================================

/**
 * Example 8: List Available Trained Models
 * 
 * Retrieves user's custom trained models (persons, objects, styles)
 */
async function listTrainedModels(modelClass = null) {
  console.log('=== List Trained Models ===\n');
  
  let url = `${API_BASE_URL}/models?limit=10&sortBy=usages&sortOrder=DESC`;
  if (modelClass) {
    url += `&class=${modelClass}`;
  }
  
  const response = await fetch(url, { headers });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(`API Error: ${error.error}`);
  }
  
  const data = await response.json();
  
  console.log(`Found ${data.data?.length || 0} models:`);
  (data.data || []).forEach(model => {
    console.log(`  - @${model.name} (${model.class}) - ${model.usages} uses`);
  });
  
  return data;
}

/**
 * Example 9: Generate Image with Custom Person Model
 * 
 * Uses a trained person model via @modelname syntax
 */
async function generateWithPersonModel(modelName) {
  console.log('=== Generate with Person Model ===\n');
  
  const response = await fetch(`${API_BASE_URL}/images`, {
    method: 'POST',
    headers,
    body: JSON.stringify({
      prompt: `@${modelName} standing on a beach at sunset, professional photography`,
      baseModel: 'gemini-3-pro-image-preview',
      mode: '2k'
    })
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(`API Error: ${error.error}`);
  }
  
  const { id } = await response.json();
  console.log(`Generation with @${modelName} started. ID: ${id}`);
  
  const result = await pollImageStatus(id);
  console.log(`\nImage ready!`);
  console.log(`URL: ${result.imageVersions.original}`);
  
  return result;
}

/**
 * Example 10: Generate Image with Custom Style Model
 * 
 * Uses a trained style model for artistic effects
 */
async function generateWithStyleModel(styleName) {
  console.log('=== Generate with Style Model ===\n');
  
  const response = await fetch(`${API_BASE_URL}/images`, {
    method: 'POST',
    headers,
    body: JSON.stringify({
      prompt: `A portrait of a woman in @${styleName} aesthetic, dramatic lighting`,
      baseModel: 'gemini-3-pro-image-preview',
      mode: '2k'
    })
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(`API Error: ${error.error}`);
  }
  
  const { id } = await response.json();
  console.log(`Generation with @${styleName} style started. ID: ${id}`);
  
  const result = await pollImageStatus(id);
  console.log(`\nImage ready!`);
  console.log(`URL: ${result.imageVersions.original}`);
  
  return result;
}

/**
 * Example 11: Generate Product Photo with Object Model
 * 
 * Uses a trained object/product model
 */
async function generateWithObjectModel(objectName) {
  console.log('=== Generate with Object Model ===\n');
  
  const response = await fetch(`${API_BASE_URL}/images`, {
    method: 'POST',
    headers,
    body: JSON.stringify({
      prompt: `Professional product photo featuring @${objectName} on a white background, studio lighting`,
      baseModel: 'gemini-3-pro-image-preview',
      mode: '2k'
    })
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(`API Error: ${error.error}`);
  }
  
  const { id } = await response.json();
  console.log(`Generation with @${objectName} started. ID: ${id}`);
  
  const result = await pollImageStatus(id);
  console.log(`\nImage ready!`);
  console.log(`URL: ${result.imageVersions.original}`);
  
  return result;
}

/**
 * Example 12: Complete Workflow with Custom Model
 * 
 * Lists models, selects one, and generates an image
 */
async function completeCustomModelWorkflow() {
  console.log('=== Complete Custom Model Workflow ===\n');
  
  // Step 1: List available person models
  console.log('Step 1: Fetching available person models...');
  const modelsResponse = await fetch(
    `${API_BASE_URL}/models?class=person&limit=5&sortBy=usages&sortOrder=DESC`,
    { headers }
  );
  
  if (!modelsResponse.ok) {
    throw new Error('Failed to fetch models');
  }
  
  const modelsData = await modelsResponse.json();
  const models = modelsData.data || [];
  
  if (models.length === 0) {
    console.log('No person models found. Train models at letz.ai first.');
    return null;
  }
  
  console.log(`Found ${models.length} person models:`);
  models.forEach(m => console.log(`  - @${m.name}`));
  
  // Step 2: Use the most-used model
  const selectedModel = models[0];
  console.log(`\nStep 2: Using @${selectedModel.name} for generation...`);
  
  const response = await fetch(`${API_BASE_URL}/images`, {
    method: 'POST',
    headers,
    body: JSON.stringify({
      prompt: `@${selectedModel.name} in a modern office, professional headshot`,
      baseModel: 'gemini-3-pro-image-preview',
      mode: '2k'
    })
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(`API Error: ${error.error}`);
  }
  
  const { id } = await response.json();
  console.log(`Generation started. ID: ${id}`);
  
  // Step 3: Poll for result
  console.log('\nStep 3: Waiting for generation...');
  const result = await pollImageStatus(id);
  
  console.log('\n=== Workflow Complete ===');
  console.log(`Model used: @${selectedModel.name}`);
  console.log(`Image URL: ${result.imageVersions.original}`);
  
  return result;
}

// Main execution
async function main() {
  try {
    // Run examples
    await generateBasicImage();
    console.log('\n---\n');
    
    // Uncomment to run other examples:
    // await generateHighResImage();
    // await generateFlux2Image();
    // await generateSeeDreamImage();
    // await generateWithSeed();
    // await generateBatch();
    // await generateWithErrorHandling();
    
    // Custom model examples (requires trained models):
    // await listTrainedModels('person');
    // await generateWithPersonModel('john_doe');
    // await generateWithStyleModel('vintage_style');
    // await generateWithObjectModel('my_product');
    // await completeCustomModelWorkflow();
    
  } catch (error) {
    console.error('Error:', error.message);
    process.exit(1);
  }
}

// Run if executed directly
main();

// Export functions for use as module
module.exports = {
  // Base model examples
  generateBasicImage,
  generateHighResImage,
  generateFlux2Image,
  generateSeeDreamImage,
  generateWithSeed,
  generateBatch,
  generateWithErrorHandling,
  // Context editing examples
  contextEditSingleImage,
  contextEditMultiReference,
  editLetzAIImage,
  // Custom model examples
  listTrainedModels,
  generateWithPersonModel,
  generateWithStyleModel,
  generateWithObjectModel,
  completeCustomModelWorkflow,
  // Utilities
  pollImageStatus,
  pollEditStatus
};
