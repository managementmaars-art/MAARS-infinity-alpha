---
name: rag-patterns
description: Retrieval-Augmented Generation patterns for MAARS — vector search, chunking, hybrid retrieval, reranking, knowledge base integration, and agent memory augmentation
---

# RAG Patterns — MAARS Reference

## MAARS RAG Architecture
```
Documents → Chunking → Embedding → Vector DB (pgvector)
                                        ↓
User Query → Query Embedding → Similarity Search → Reranking → Context → LLM
```

## Chunking Strategies
```python
# Semantic chunking (preferred for MAARS knowledge base)
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=512,         # tokens, not chars
    chunk_overlap=64,       # overlap for context continuity
    separators=["\n\n", "\n", ". ", " ", ""],
    length_function=count_tokens,
)
chunks = splitter.split_text(document)

# For structured docs (code, tables)
splitter = RecursiveCharacterTextSplitter.from_language(
    language=Language.PYTHON,
    chunk_size=256,
    chunk_overlap=32,
)
```

## Embedding Generation
```python
# OpenAI embeddings (MAARS default)
async def embed_texts(texts: list[str]) -> list[list[float]]:
    response = await openai_client.embeddings.create(
        model="text-embedding-3-large",
        input=texts,
        dimensions=1536,  # 1536 for balance, 3072 for max quality
    )
    return [r.embedding for r in response.data]

# Batch embedding with rate limit handling
async def embed_batch(texts: list[str], batch_size=100) -> list:
    all_embeddings = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        embeddings = await embed_texts(batch)
        all_embeddings.extend(embeddings)
        await asyncio.sleep(0.1)  # rate limit buffer
    return all_embeddings
```

## pgvector Storage (MAARS uses PostgreSQL)
```python
# Schema
CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS knowledge_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    knowledge_base_id UUID REFERENCES knowledge_bases(id),
    content TEXT NOT NULL,
    embedding vector(1536),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX ON knowledge_chunks USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);
"""

# Semantic search
async def similarity_search(
    query_embedding: list[float],
    knowledge_base_id: str,
    limit: int = 5,
    threshold: float = 0.75,
) -> list[dict]:
    sql = """
    SELECT content, metadata,
           1 - (embedding <=> $1::vector) AS similarity
    FROM knowledge_chunks
    WHERE knowledge_base_id = $2
      AND 1 - (embedding <=> $1::vector) > $3
    ORDER BY embedding <=> $1::vector
    LIMIT $4
    """
    return await db.fetch(sql, query_embedding, knowledge_base_id, threshold, limit)
```

## Hybrid Search (Semantic + BM25)
```python
async def hybrid_search(query: str, kb_id: str, alpha: float = 0.7) -> list:
    # alpha=0.7 means 70% semantic, 30% keyword
    
    # Semantic results
    q_embedding = await embed_texts([query])
    semantic = await similarity_search(q_embedding[0], kb_id, limit=20)
    
    # Keyword results (using PostgreSQL full-text search)
    keyword_sql = """
    SELECT content, metadata,
           ts_rank(to_tsvector('english', content), plainto_tsquery($1)) AS rank
    FROM knowledge_chunks
    WHERE knowledge_base_id = $2
      AND to_tsvector('english', content) @@ plainto_tsquery($1)
    ORDER BY rank DESC LIMIT 20
    """
    keyword = await db.fetch(keyword_sql, query, kb_id)
    
    # Reciprocal Rank Fusion
    return rrf_merge(semantic, keyword, alpha=alpha, k=60)
```

## Reranking
```python
# Cohere reranker (best quality)
from cohere import Client as Cohere

async def rerank(query: str, documents: list[str], top_n: int = 5) -> list:
    cohere = Cohere(api_key=COHERE_API_KEY)
    results = cohere.rerank(
        model="rerank-english-v3.0",
        query=query,
        documents=documents,
        top_n=top_n,
    )
    return [documents[r.index] for r in results.results]
```

## RAG Prompt Construction
```python
def build_rag_prompt(query: str, chunks: list[dict]) -> list[dict]:
    context = "\n\n---\n\n".join([
        f"[Source {i+1}]: {chunk['content']}"
        for i, chunk in enumerate(chunks)
    ])
    
    return [
        {
            "role": "system",
            "content": f"""Answer the question using ONLY the provided context.
If the answer is not in the context, say "I don't have information about that."
Always cite sources as [Source N].

CONTEXT:
{context}"""
        },
        {"role": "user", "content": query}
    ]
```

## MAARS Agent Memory Integration
```python
# backend/memory_system/semantic.py pattern
class SemanticMemory:
    async def store(self, agent_id: str, content: str, metadata: dict):
        embedding = await embed_texts([content])
        await db.execute(
            "INSERT INTO agent_memories (agent_id, content, embedding, metadata) VALUES ($1,$2,$3,$4)",
            agent_id, content, embedding[0], metadata
        )
    
    async def recall(self, agent_id: str, query: str, limit: int = 5) -> list:
        q_emb = await embed_texts([query])
        return await similarity_search(q_emb[0], agent_id=agent_id, limit=limit)
    
    async def augment_context(self, agent_id: str, query: str, messages: list) -> list:
        memories = await self.recall(agent_id, query)
        if memories:
            memory_ctx = "\n".join(m["content"] for m in memories)
            messages.insert(1, {
                "role": "system",
                "content": f"Relevant memory:\n{memory_ctx}"
            })
        return messages
```

## Performance Tips
- **Chunk overlap**: 10-15% of chunk size prevents information loss at boundaries
- **Batch embeddings**: Always batch, never embed one-by-one
- **Cache embeddings**: Store in DB, never re-embed unchanged documents
- **IVFFlat index**: Use `lists = sqrt(num_rows)` for optimal performance
- **HNSW index**: Better for < 1M vectors and high recall requirement
- **Threshold tuning**: Start at 0.75, tune per domain (code needs higher ~0.85)
