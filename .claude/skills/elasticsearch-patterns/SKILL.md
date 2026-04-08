---
name: elasticsearch-patterns
description: Elasticsearch queries, aggregations, mappings, analyzers, Python client, index templates
---

# Elasticsearch Patterns

Production Elasticsearch usage: index design, query DSL, aggregations, custom analyzers, index templates, and the Python `elasticsearch` client (v8+).

## Python Client Setup

```python
from elasticsearch import Elasticsearch, helpers
from elasticsearch.exceptions import NotFoundError, ConflictError
import os

# v8 client with SSL and API key auth
es = Elasticsearch(
    hosts=[os.environ["ES_URL"]],
    api_key=os.environ["ES_API_KEY"],
    verify_certs=True,
    ssl_show_warn=False,
    retry_on_timeout=True,
    max_retries=3,
    request_timeout=30,
)

# Health check
info = es.info()
print(f"Connected to Elasticsearch {info['version']['number']}")
```

## Index Mapping Design

Define mappings explicitly — never rely on dynamic mapping in production:

```python
PRODUCTS_MAPPING = {
    "settings": {
        "number_of_shards": 3,
        "number_of_replicas": 1,
        "refresh_interval": "5s",        # delay refresh for indexing throughput
        "analysis": {
            "analyzer": {
                "english_exact": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": ["lowercase", "english_stop", "english_stemmer"]
                },
                "autocomplete": {
                    "type": "custom",
                    "tokenizer": "autocomplete_tokenizer",
                    "filter": ["lowercase"]
                },
                "autocomplete_search": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": ["lowercase"]
                }
            },
            "tokenizer": {
                "autocomplete_tokenizer": {
                    "type": "edge_ngram",
                    "min_gram": 2,
                    "max_gram": 15,
                    "token_chars": ["letter", "digit"]
                }
            },
            "filter": {
                "english_stop": {"type": "stop", "stopwords": "_english_"},
                "english_stemmer": {"type": "stemmer", "language": "english"}
            }
        }
    },
    "mappings": {
        "dynamic": "strict",
        "properties": {
            "id": {"type": "keyword"},
            "name": {
                "type": "text",
                "analyzer": "english_exact",
                "fields": {
                    "keyword": {"type": "keyword"},
                    "autocomplete": {"type": "text", "analyzer": "autocomplete", "search_analyzer": "autocomplete_search"},
                    "suggest": {"type": "completion"}
                }
            },
            "description": {"type": "text", "analyzer": "english_exact"},
            "category": {"type": "keyword"},
            "tags": {"type": "keyword"},
            "price": {"type": "double"},
            "stock": {"type": "integer"},
            "rating": {"type": "float"},
            "in_stock": {"type": "boolean"},
            "brand": {"type": "keyword"},
            "attributes": {"type": "object", "dynamic": True},
            "created_at": {"type": "date", "format": "strict_date_optional_time"},
            "location": {"type": "geo_point"},
            "embedding": {
                "type": "dense_vector",
                "dims": 1536,
                "index": True,
                "similarity": "cosine"
            }
        }
    }
}

def create_index(index_name: str):
    if not es.indices.exists(index=index_name):
        es.indices.create(index=index_name, body=PRODUCTS_MAPPING)
        print(f"Created index: {index_name}")
```

## Query DSL Patterns

```python
def search_products(
    query: str,
    categories: list[str] | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    sort_by: str = "_score",
    page: int = 1,
    page_size: int = 20,
) -> dict:
    # Build filter context (exact, cached)
    filters = [{"term": {"in_stock": True}}]
    if categories:
        filters.append({"terms": {"category": categories}})
    if min_price is not None or max_price is not None:
        price_range = {}
        if min_price is not None: price_range["gte"] = min_price
        if max_price is not None: price_range["lte"] = max_price
        filters.append({"range": {"price": price_range}})

    # Build query context (scored)
    must_queries = []
    if query:
        must_queries.append({
            "multi_match": {
                "query": query,
                "fields": ["name^3", "name.autocomplete^2", "description", "tags"],
                "type": "best_fields",
                "fuzziness": "AUTO",
                "prefix_length": 2,
            }
        })

    body = {
        "from": (page - 1) * page_size,
        "size": page_size,
        "query": {
            "bool": {
                "must": must_queries or [{"match_all": {}}],
                "filter": filters,
                "should": [
                    # Boost highly-rated products
                    {"range": {"rating": {"gte": 4.0, "boost": 1.5}}}
                ],
                "minimum_should_match": 0,
            }
        },
        "sort": [
            {"_score": {"order": "desc"}},
            {"rating": {"order": "desc"}},
        ],
        "highlight": {
            "fields": {
                "name": {"number_of_fragments": 0},
                "description": {"fragment_size": 150, "number_of_fragments": 3}
            },
            "pre_tags": ["<mark>"],
            "post_tags": ["</mark>"],
        },
        "_source": {"excludes": ["embedding"]},
    }

    result = es.search(index="products", body=body)
    return {
        "total": result["hits"]["total"]["value"],
        "page": page,
        "results": [
            {
                "id": hit["_source"]["id"],
                "score": hit["_score"],
                "highlights": hit.get("highlight", {}),
                **hit["_source"],
            }
            for hit in result["hits"]["hits"]
        ],
    }
```

## Aggregations

```python
def get_facets(query: str, filters: dict) -> dict:
    """Get facets (categories, price ranges, brands) for search results."""
    body = {
        "size": 0,  # Don't return hits, only aggregations
        "query": build_query(query, filters),
        "aggregations": {
            "categories": {
                "terms": {"field": "category", "size": 50, "min_doc_count": 1},
                "aggs": {
                    "avg_price": {"avg": {"field": "price"}}
                }
            },
            "brands": {
                "terms": {"field": "brand", "size": 20}
            },
            "price_ranges": {
                "range": {
                    "field": "price",
                    "ranges": [
                        {"to": 25},
                        {"from": 25, "to": 50},
                        {"from": 50, "to": 100},
                        {"from": 100, "to": 250},
                        {"from": 250},
                    ]
                }
            },
            "avg_rating": {"avg": {"field": "rating"}},
            "rating_histogram": {
                "histogram": {"field": "rating", "interval": 0.5, "min_doc_count": 1}
            },
            "daily_sales": {
                "date_histogram": {
                    "field": "created_at",
                    "calendar_interval": "day",
                    "format": "yyyy-MM-dd"
                },
                "aggs": {
                    "total_revenue": {"sum": {"field": "price"}}
                }
            }
        }
    }

    result = es.search(index="products", body=body)
    aggs = result["aggregations"]

    return {
        "categories": [
            {"name": b["key"], "count": b["doc_count"], "avg_price": b["avg_price"]["value"]}
            for b in aggs["categories"]["buckets"]
        ],
        "brands": [{"name": b["key"], "count": b["doc_count"]} for b in aggs["brands"]["buckets"]],
        "price_ranges": aggs["price_ranges"]["buckets"],
        "avg_rating": aggs["avg_rating"]["value"],
    }
```

## Bulk Indexing

```python
def bulk_index_products(products: list[dict], index: str = "products") -> dict:
    """Bulk index with error handling and retry."""
    actions = [
        {
            "_op_type": "index",
            "_index": index,
            "_id": product["id"],
            "_source": product,
        }
        for product in products
    ]

    success, errors = helpers.bulk(
        es,
        actions,
        chunk_size=500,
        request_timeout=60,
        raise_on_error=False,
        raise_on_exception=False,
    )

    if errors:
        for error in errors:
            print(f"Indexing error: {error}")

    return {"indexed": success, "errors": len(errors)}

def upsert_product(product: dict) -> None:
    """Upsert a single document."""
    es.update(
        index="products",
        id=product["id"],
        body={
            "doc": product,
            "doc_as_upsert": True,
        },
        retry_on_conflict=3,
    )
```

## Index Templates and Aliases

```python
# Index template for time-series indices (e.g., logs-2024-01)
INDEX_TEMPLATE = {
    "index_patterns": ["logs-*"],
    "template": {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0,    # no replicas for write-heavy hot indices
            "lifecycle": {
                "name": "logs-policy",
                "rollover_alias": "logs-write"
            }
        },
        "mappings": {
            "properties": {
                "@timestamp": {"type": "date"},
                "level": {"type": "keyword"},
                "message": {"type": "text"},
                "service": {"type": "keyword"},
                "trace_id": {"type": "keyword"},
            }
        }
    },
    "priority": 200,
    "version": 1,
}

es.indices.put_index_template(name="logs-template", body=INDEX_TEMPLATE)

# Zero-downtime reindex with alias swap
def reindex_with_alias(old_index: str, new_index: str, alias: str):
    # Start reindex
    task = es.reindex(body={
        "source": {"index": old_index},
        "dest": {"index": new_index, "version_type": "external"},
    }, wait_for_completion=False)

    # Wait for completion, then swap alias atomically
    es.indices.update_aliases(body={
        "actions": [
            {"remove": {"index": old_index, "alias": alias}},
            {"add": {"index": new_index, "alias": alias, "is_write_index": True}},
        ]
    })
```

## Vector Search (kNN)

```python
def vector_search(query_embedding: list[float], k: int = 10, num_candidates: int = 100) -> list[dict]:
    """Approximate nearest-neighbor vector search."""
    result = es.search(
        index="products",
        body={
            "knn": {
                "field": "embedding",
                "query_vector": query_embedding,
                "k": k,
                "num_candidates": num_candidates,
                "filter": {"term": {"in_stock": True}},
            },
            "_source": {"excludes": ["embedding"]},
        }
    )
    return [hit["_source"] for hit in result["hits"]["hits"]]

def hybrid_search(query: str, query_embedding: list[float]) -> list[dict]:
    """Combine BM25 + vector search with RRF."""
    result = es.search(
        index="products",
        body={
            "retriever": {
                "rrf": {                             # Reciprocal Rank Fusion
                    "retrievers": [
                        {"standard": {"query": {"match": {"name": query}}}},
                        {"knn": {"field": "embedding", "query_vector": query_embedding, "k": 10, "num_candidates": 50}},
                    ],
                    "rank_constant": 60,
                    "rank_window_size": 100,
                }
            }
        }
    )
    return [hit["_source"] for hit in result["hits"]["hits"]]
```

## Best Practices

- Always define explicit mappings with `"dynamic": "strict"` to prevent mapping explosions
- Use `keyword` type for exact filtering/aggregations; `text` for full-text search with analyzers
- Use alias patterns for zero-downtime reindexing and ILM (Index Lifecycle Management)
- Set `refresh_interval: "30s"` or higher for write-heavy indices; use `refresh=wait_for` only when needed
- Use `filter` context for yes/no criteria (cached) and `query` context only for scoring
- Monitor shard sizes: aim for 10-50 GB per shard; avoid too many small shards
- Use `_source` exclusions to avoid fetching large fields (e.g., `embedding`) in search responses
- Use `search_after` instead of `from/size` for deep pagination to avoid heap pressure
- Always use bulk API for indexing — single-document indexing is inefficient at scale
- Use the Profiling API (`"profile": true`) to diagnose slow queries

## Models to Use

- **Default**: `claude-sonnet-4-5` — query DSL, mappings, aggregations, Python client
- **Complex search architecture**: `claude-opus-4-5` — relevance tuning, vector search, ILM design
- **Quick snippets**: `claude-haiku-3-5` — simple queries, mapping fields, aggregation buckets
