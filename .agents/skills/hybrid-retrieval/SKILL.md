---
name: hybrid-retrieval
description: |
  Implement hybrid search combining dense vectors and sparse retrieval for optimal RAG results.
  Use this skill when vector search alone isn't providing accurate results.
  Activate when: hybrid search, BM25, keyword search, sparse retrieval, dense retrieval, reranking, ensemble retrieval.
---

# Hybrid Retrieval for RAG

**Combine dense (semantic) and sparse (keyword) retrieval for superior results.**

## When to Use

- Vector search misses exact keyword matches
- Domain-specific terminology needs exact matching
- Users search with both natural language and specific terms
- Need to balance semantic understanding with precision

## The Problem with Vector-Only Search

```
Query: "Error code E-4521 troubleshooting"

Vector search returns:
- "Common error handling patterns" (semantically similar)
- "Debugging techniques for applications" (related topic)

Missing:
- "E-4521: Database connection timeout" (exact match needed!)
```

## Hybrid Architecture

```
┌─────────────────────────────────────────────────┐
│                   User Query                     │
└─────────────────────┬───────────────────────────┘
                      │
         ┌────────────┴────────────┐
         │                         │
         ▼                         ▼
┌─────────────────┐      ┌─────────────────┐
│  Dense Search   │      │  Sparse Search  │
│  (Embeddings)   │      │  (BM25/TF-IDF)  │
└────────┬────────┘      └────────┬────────┘
         │                         │
         └────────────┬────────────┘
                      │
                      ▼
              ┌───────────────┐
              │    Fusion     │
              │  (RRF/Linear) │
              └───────┬───────┘
                      │
                      ▼
              ┌───────────────┐
              │   Reranker    │
              │  (Optional)   │
              └───────┬───────┘
                      │
                      ▼
              ┌───────────────┐
              │ Final Results │
              └───────────────┘
```

## Implementation

### Basic Hybrid with LangChain

```python
from langchain.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
from langchain_community.vectorstores import Chroma

# Dense retriever (vector search)
vectorstore = Chroma.from_documents(docs, embeddings)
dense_retriever = vectorstore.as_retriever(search_kwargs={"k": 10})

# Sparse retriever (BM25)
bm25_retriever = BM25Retriever.from_documents(docs)
bm25_retriever.k = 10

# Combine with ensemble
hybrid_retriever = EnsembleRetriever(
    retrievers=[dense_retriever, bm25_retriever],
    weights=[0.5, 0.5]  # Adjust based on your data
)

results = hybrid_retriever.invoke("Error code E-4521")
```

### Reciprocal Rank Fusion (RRF)

```python
def reciprocal_rank_fusion(results_list: list, k: int = 60) -> list:
    """
    Combine multiple ranked lists using RRF.
    k=60 is the standard constant from the original paper.
    """
    fused_scores = {}

    for results in results_list:
        for rank, doc in enumerate(results):
            doc_id = doc.metadata.get("id", hash(doc.page_content))
            if doc_id not in fused_scores:
                fused_scores[doc_id] = {"doc": doc, "score": 0}
            fused_scores[doc_id]["score"] += 1 / (k + rank + 1)

    # Sort by fused score
    reranked = sorted(
        fused_scores.values(),
        key=lambda x: x["score"],
        reverse=True
    )
    return [item["doc"] for item in reranked]

# Usage
dense_results = dense_retriever.invoke(query)
sparse_results = bm25_retriever.invoke(query)
final_results = reciprocal_rank_fusion([dense_results, sparse_results])
```

### With Pinecone (Native Hybrid)

```python
from pinecone import Pinecone
from pinecone_text.sparse import BM25Encoder

# Initialize
pc = Pinecone(api_key="...")
index = pc.Index("hybrid-index")

# Sparse encoder
bm25 = BM25Encoder()
bm25.fit(corpus)

# Query with both dense and sparse
def hybrid_query(query: str, alpha: float = 0.5):
    # Dense vector
    dense_vec = embeddings.embed_query(query)

    # Sparse vector
    sparse_vec = bm25.encode_queries([query])[0]

    # Hybrid search
    results = index.query(
        vector=dense_vec,
        sparse_vector=sparse_vec,
        top_k=10,
        alpha=alpha,  # 0 = sparse only, 1 = dense only
        include_metadata=True
    )
    return results
```

### With Weaviate (Native Hybrid)

```python
import weaviate

client = weaviate.Client("http://localhost:8080")

result = client.query.get(
    "Document",
    ["content", "title"]
).with_hybrid(
    query="Error code E-4521",
    alpha=0.5,  # Balance between vector and keyword
    fusion_type="rankedFusion"
).with_limit(10).do()
```

## Adding a Reranker

```python
from sentence_transformers import CrossEncoder

# Load reranker model
reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

def rerank_results(query: str, docs: list, top_k: int = 5) -> list:
    """Rerank documents using cross-encoder."""
    pairs = [[query, doc.page_content] for doc in docs]
    scores = reranker.predict(pairs)

    # Sort by reranker scores
    scored_docs = list(zip(docs, scores))
    scored_docs.sort(key=lambda x: x[1], reverse=True)

    return [doc for doc, score in scored_docs[:top_k]]

# Full pipeline
hybrid_results = hybrid_retriever.invoke(query)  # Get 20 results
final_results = rerank_results(query, hybrid_results, top_k=5)  # Rerank to top 5
```

## Weight Tuning Guidelines

| Data Type | Dense Weight | Sparse Weight | Notes |
|-----------|--------------|---------------|-------|
| General text | 0.5 | 0.5 | Balanced default |
| Technical docs | 0.4 | 0.6 | Keywords matter more |
| Conversational | 0.7 | 0.3 | Semantic matters more |
| Code/APIs | 0.3 | 0.7 | Exact matches critical |
| Legal/Medical | 0.4 | 0.6 | Terminology precision |

## Evaluation

```python
def evaluate_retrieval(queries: list, ground_truth: dict, retriever) -> dict:
    """Calculate retrieval metrics."""
    metrics = {"mrr": 0, "recall@5": 0, "precision@5": 0}

    for query in queries:
        results = retriever.invoke(query)
        result_ids = [doc.metadata["id"] for doc in results[:5]]
        relevant_ids = ground_truth[query]

        # MRR
        for i, rid in enumerate(result_ids):
            if rid in relevant_ids:
                metrics["mrr"] += 1 / (i + 1)
                break

        # Recall & Precision
        hits = len(set(result_ids) & set(relevant_ids))
        metrics["recall@5"] += hits / len(relevant_ids)
        metrics["precision@5"] += hits / 5

    # Average
    n = len(queries)
    return {k: v/n for k, v in metrics.items()}
```

## Best Practices

1. **Start with 50/50 weights** - then tune based on evaluation
2. **Always add a reranker** - significant quality improvement
3. **Index sparse vectors** - BM25 on raw text, not chunks
4. **Use native hybrid** - when available (Pinecone, Weaviate, Qdrant)
5. **Monitor both paths** - log which retriever contributed to final results
