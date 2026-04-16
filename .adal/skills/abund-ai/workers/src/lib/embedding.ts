/**
 * Embedding Generation Helper
 *
 * Uses Cloudflare Workers AI to generate text embeddings for semantic search.
 * Model: @cf/baai/bge-base-en-v1.5 (768 dimensions)
 */

// Type for the embedding response
interface EmbeddingResponse {
  data: number[][]
}

/**
 * Generate an embedding vector for the given text.
 *
 * @param ai - Workers AI binding
 * @param text - Text to embed (will be truncated if too long)
 * @returns 768-dimensional embedding vector
 */
export async function generateEmbedding(
  ai: Ai,
  text: string
): Promise<number[]> {
  // Truncate to ~500 words to stay within model limits
  const truncated = text.slice(0, 2000)

  const result = (await ai.run('@cf/baai/bge-base-en-v1.5', {
    text: [truncated],
  })) as unknown as EmbeddingResponse

  // The model returns { data: [[...embedding]] }
  const embedding = result.data[0]
  if (!embedding) {
    throw new Error('Failed to generate embedding')
  }
  return embedding
}

/**
 * Generate embeddings for multiple texts in a batch.
 *
 * @param ai - Workers AI binding
 * @param texts - Array of texts to embed
 * @returns Array of 768-dimensional embedding vectors
 */
export async function generateEmbeddings(
  ai: Ai,
  texts: string[]
): Promise<number[][]> {
  // Truncate each text
  const truncated = texts.map((t) => t.slice(0, 2000))

  const result = (await ai.run('@cf/baai/bge-base-en-v1.5', {
    text: truncated,
  })) as unknown as EmbeddingResponse

  return result.data
}
