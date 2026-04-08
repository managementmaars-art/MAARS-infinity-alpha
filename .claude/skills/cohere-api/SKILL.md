---
name: cohere-api
description: Cohere API — Command R+, reranking, embeddings — used in MAARS for enterprise RAG, document reranking, and multilingual semantic search
---

# Cohere API — MAARS Reference

## Models
| Model | Context | Strength |
|-------|---------|----------|
| `command-r-plus-08-2024` | 128K | Best reasoning, RAG-optimized |
| `command-r-08-2024` | 128K | Fast, cost-efficient |
| `command-r7b-12-2024` | 128K | Ultra-fast, edge cases |
| `rerank-english-v3.0` | — | Best English reranker |
| `rerank-multilingual-v3.0` | — | 100+ language reranker |
| `embed-english-v3.0` | — | 1024d English embeddings |
| `embed-multilingual-v3.0` | — | 1024d multilingual embeddings |

## Why Cohere in MAARS
- **Best-in-class reranker**: Dramatically improves RAG precision
- **Multilingual embeddings**: Global client support
- **Command R+**: Specifically trained for RAG and tool use

## Chat (OpenAI-compatible)
```python
from openai import AsyncOpenAI

cohere_client = AsyncOpenAI(
    base_url="https://api.cohere.com/compatibility/v1",
    api_key=COHERE_API_KEY,
)

response = await cohere_client.chat.completions.create(
    model="command-r-plus-08-2024",
    messages=messages,
    stream=True,
)
```

## Native SDK (preferred for RAG)
```python
import cohere

co = cohere.ClientV2(api_key=COHERE_API_KEY)

# Chat with documents (RAG)
response = co.chat(
    model="command-r-plus-08-2024",
    messages=[{"role": "user", "content": query}],
    documents=[
        {"id": "1", "data": {"text": chunk1}},
        {"id": "2", "data": {"text": chunk2}},
    ],
)
# Citations are automatically grounded to documents
```

## Reranking (MAARS RAG pipeline)
```python
results = co.rerank(
    model="rerank-english-v3.0",
    query=user_query,
    documents=retrieved_chunks,  # list of strings
    top_n=5,
    return_documents=True,
)
reranked = [r.document.text for r in results.results]
```

## Embeddings
```python
response = co.embed(
    texts=text_list,
    model="embed-multilingual-v3.0",
    input_type="search_document",  # or "search_query"
    embedding_types=["float"],
)
vectors = response.embeddings.float_
```

## MAARS Config
```python
{
    "model_provider": "cohere",
    "model_name": "command-r-plus-08-2024",
    "api_key_env": "COHERE_API_KEY",
    "reranker": "rerank-english-v3.0",
}
```
