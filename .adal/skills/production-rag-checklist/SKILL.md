---
name: production-rag-checklist
description: |
  Comprehensive checklist for deploying RAG systems to production with reliability and scale.
  Use this skill when preparing RAG for production deployment.
  Activate when: production RAG, RAG deployment, RAG checklist, RAG scaling, RAG monitoring, production-ready RAG.
---

# Production RAG Checklist

**Everything you need to deploy RAG systems with confidence.**

## Pre-Production Checklist

### Data Pipeline

- [ ] **Document ingestion automated**
  - Scheduled updates for dynamic sources
  - Change detection for modified documents
  - Deletion handling for removed documents

- [ ] **Chunking strategy validated**
  - Chunk sizes tested with retrieval quality
  - Overlap tuned for context preservation
  - Document-specific splitters for code/tables

- [ ] **Metadata enriched**
  - Source tracking (URL, file path, version)
  - Timestamps (created, updated, indexed)
  - Document type classification
  - Access control tags (if needed)

- [ ] **Embedding pipeline robust**
  - Batch processing for efficiency
  - Rate limiting for API-based embeddings
  - Fallback for embedding failures
  - Version tracking for re-embedding

### Vector Store

- [ ] **Index configured properly**
  - Appropriate index type (HNSW, IVF, etc.)
  - Parameters tuned (ef_construction, m, nlist)
  - Distance metric matches embedding model

- [ ] **Scaling planned**
  - Estimated vector count and growth rate
  - Sharding strategy if needed
  - Backup and recovery procedures

- [ ] **High availability**
  - Replicas configured
  - Failover tested
  - Connection pooling enabled

### Retrieval Quality

- [ ] **Evaluation dataset created**
  - Minimum 100 query-answer pairs
  - Edge cases covered
  - Regular updates with new patterns

- [ ] **Baseline metrics established**
  - Recall@5 > 0.8
  - MRR > 0.7
  - Latency p99 < 500ms

- [ ] **Hybrid search configured** (if applicable)
  - BM25/keyword weight tuned
  - Reranker added and tested

### Generation Quality

- [ ] **Prompt engineering complete**
  - System prompt tested across scenarios
  - Few-shot examples if needed
  - Output format specified

- [ ] **Guardrails in place**
  - Hallucination detection
  - Toxicity filtering
  - PII redaction (if needed)

- [ ] **Fallback responses defined**
  - "I don't know" for low confidence
  - Error messages user-friendly

## Infrastructure

### API Layer

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncio

app = FastAPI()

class QueryRequest(BaseModel):
    query: str
    top_k: int = 5
    filters: dict = None

class QueryResponse(BaseModel):
    answer: str
    sources: list
    confidence: float
    latency_ms: float

@app.post("/query", response_model=QueryResponse)
async def query_rag(request: QueryRequest):
    start = time.time()

    try:
        # Timeout for long queries
        result = await asyncio.wait_for(
            rag_pipeline.ainvoke(request.query, request.top_k, request.filters),
            timeout=30.0
        )

        return QueryResponse(
            answer=result["answer"],
            sources=[doc.metadata["source"] for doc in result["documents"]],
            confidence=result.get("confidence", 0.0),
            latency_ms=(time.time() - start) * 1000
        )

    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Query timeout")
    except Exception as e:
        logger.error(f"RAG error: {e}")
        raise HTTPException(status_code=500, detail="Internal error")
```

### Caching Layer

```python
import hashlib
from redis import Redis

class RAGCache:
    def __init__(self, redis_url: str, ttl_seconds: int = 3600):
        self.redis = Redis.from_url(redis_url)
        self.ttl = ttl_seconds

    def _hash_query(self, query: str, filters: dict) -> str:
        key = f"{query}:{json.dumps(filters, sort_keys=True)}"
        return hashlib.sha256(key.encode()).hexdigest()

    def get(self, query: str, filters: dict = None) -> dict | None:
        key = self._hash_query(query, filters)
        cached = self.redis.get(key)
        return json.loads(cached) if cached else None

    def set(self, query: str, filters: dict, result: dict):
        key = self._hash_query(query, filters)
        self.redis.setex(key, self.ttl, json.dumps(result))

    def invalidate_by_source(self, source: str):
        """Invalidate cache when source document changes."""
        # Store source->keys mapping for targeted invalidation
        pattern = f"source:{source}:*"
        for key in self.redis.scan_iter(pattern):
            self.redis.delete(key)
```

### Rate Limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/query")
@limiter.limit("100/minute")  # Per IP
async def query_rag(request: QueryRequest):
    ...
```

## Monitoring

### Metrics to Track

```python
from prometheus_client import Counter, Histogram, Gauge

# Request metrics
rag_requests = Counter('rag_requests_total', 'Total RAG requests', ['status'])
rag_latency = Histogram('rag_latency_seconds', 'RAG latency', buckets=[0.1, 0.5, 1, 2, 5, 10])

# Quality metrics
retrieval_count = Histogram('rag_retrieval_count', 'Documents retrieved', buckets=[0, 1, 3, 5, 10])
confidence_score = Histogram('rag_confidence', 'Answer confidence', buckets=[0.1, 0.3, 0.5, 0.7, 0.9])

# System metrics
vector_store_latency = Histogram('vectorstore_latency_seconds', 'Vector store query time')
llm_latency = Histogram('llm_latency_seconds', 'LLM generation time')
cache_hits = Counter('rag_cache_hits_total', 'Cache hit count')

def track_request(func):
    async def wrapper(*args, **kwargs):
        with rag_latency.time():
            try:
                result = await func(*args, **kwargs)
                rag_requests.labels(status='success').inc()
                confidence_score.observe(result.get('confidence', 0))
                return result
            except Exception as e:
                rag_requests.labels(status='error').inc()
                raise
    return wrapper
```

### Alerting Rules

```yaml
# Prometheus alerting rules
groups:
  - name: rag_alerts
    rules:
      - alert: RAGHighLatency
        expr: histogram_quantile(0.99, rag_latency_seconds) > 5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "RAG p99 latency above 5s"

      - alert: RAGHighErrorRate
        expr: rate(rag_requests_total{status="error"}[5m]) / rate(rag_requests_total[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "RAG error rate above 5%"

      - alert: RAGLowConfidence
        expr: histogram_quantile(0.5, rag_confidence) < 0.5
        for: 15m
        labels:
          severity: warning
        annotations:
          summary: "RAG median confidence below 0.5"
```

### Logging

```python
import structlog

logger = structlog.get_logger()

async def log_rag_request(query: str, result: dict, latency_ms: float):
    logger.info(
        "rag_request",
        query=query[:100],  # Truncate for privacy
        query_hash=hashlib.sha256(query.encode()).hexdigest()[:8],
        num_sources=len(result.get("sources", [])),
        confidence=result.get("confidence"),
        latency_ms=latency_ms,
        cache_hit=result.get("cache_hit", False),
        model=result.get("model_used")
    )
```

## Security

- [ ] **Input validation**
  - Query length limits
  - Injection prevention
  - Rate limiting per user

- [ ] **Access control**
  - Document-level permissions
  - User authentication
  - API key management

- [ ] **Data privacy**
  - PII handling defined
  - Data retention policy
  - Audit logging enabled

## Cost Management

```python
def estimate_monthly_cost(
    queries_per_day: int,
    avg_tokens_per_query: int = 2000,
    embedding_calls_per_day: int = 1000
) -> dict:
    """Estimate monthly RAG costs."""

    # LLM costs (GPT-4)
    llm_input_cost = 0.03 / 1000  # per token
    llm_output_cost = 0.06 / 1000

    # Embedding costs (text-embedding-3-small)
    embedding_cost = 0.00002 / 1000  # per token

    # Vector DB (Pinecone Starter)
    vector_db_monthly = 70  # USD

    monthly_queries = queries_per_day * 30
    monthly_embeddings = embedding_calls_per_day * 30

    return {
        "llm_cost": monthly_queries * avg_tokens_per_query * (llm_input_cost + llm_output_cost * 0.3),
        "embedding_cost": monthly_embeddings * 500 * embedding_cost,
        "vector_db_cost": vector_db_monthly,
        "estimated_total": "Calculate based on above"
    }
```

## Go-Live Checklist

- [ ] Load testing passed (target QPS achieved)
- [ ] Failover tested
- [ ] Rollback procedure documented
- [ ] On-call rotation set up
- [ ] Runbook created
- [ ] User documentation ready
- [ ] Feedback collection mechanism in place

## Best Practices

1. **Start with caching** - reduces cost and latency significantly
2. **Monitor quality metrics** - not just uptime
3. **Version everything** - embeddings, prompts, indexes
4. **Plan for reindexing** - you will need to rebuild
5. **Set cost alerts** - LLM costs can spike unexpectedly
6. **Collect user feedback** - thumbs up/down on answers
