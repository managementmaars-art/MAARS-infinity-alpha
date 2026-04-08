---
name: system-design
description: System design patterns — scalability, distributed systems, CAP theorem, microservices, event-driven architecture, databases, caching for MAARS architecture agents
---

# System Design — MAARS Reference

## Design Framework
```
System Design Interview Framework:

1. CLARIFY REQUIREMENTS (5 min)
   - Functional: What features?
   - Non-functional: Scale, latency, availability, consistency
   - Scale: DAU/MAU, data size, read/write ratio

2. ESTIMATE SCALE (2 min)
   - 1M DAU x 10 requests = 10M req/day = ~115 RPS (peak: 2-5x)
   - Storage: 1M users x 1KB profile = 1GB/year

3. HIGH-LEVEL DESIGN (10 min)
   - Draw: Client → LB → App Servers → Cache → DB
   - Cover: DNS, CDN, Load Balancer, App tier, DB, Cache

4. DEEP DIVE (15 min)
   - Pick 2-3 critical components to detail
   - Discuss trade-offs explicitly

5. BOTTLENECKS (5 min)
   - Single points of failure
   - What breaks at 10x scale?
```

## Scalability Patterns
```python
SCALABILITY = {
    "horizontal_scaling": "Add servers (stateless app + LB + shared storage)",
    "vertical_scaling": "Bigger server (limit: hardware ceiling)",
    "read_replicas": "DB replicas for read scaling",
    "sharding": "Partition data across DBs by key",
    "caching_layers": ["CDN (static)", "Redis (computed)", "DB cache", "Browser"],
}
```

## CAP Theorem
```python
CAP = {
    "CP_systems": "HBase, Zookeeper, etcd — consistent, may be unavailable",
    "AP_systems": "Cassandra, DynamoDB — always available, eventual consistency",
    "consistency_models": {
        "strong": "Read always returns latest write",
        "eventual": "All replicas converge eventually",
        "read_your_writes": "You always see your own writes",
    }
}
```

## Classic Designs
```python
DESIGNS = {
    "url_shortener": {
        "stack": "API + Redis + PostgreSQL + CDN",
        "key": "Base62 ID, 301 vs 302 redirect trade-off",
        "scale": "Read-heavy 100:1, cache popular URLs in CDN",
    },
    "twitter_feed": {
        "approaches": {
            "fan_out_write": "Pre-compute feeds (fast read, heavy write, celebrity problem)",
            "fan_out_read": "Pull on read (slow for mega-followers)",
            "hybrid": "Pre-compute for normal users, pull for celebrities",
        },
        "storage": "tweets table + Redis sorted set per user feed",
    },
    "rate_limiter": {
        "algorithms": ["Token bucket", "Sliding window", "Fixed window"],
        "distributed": "Redis Lua script for atomic increment",
        "placement": "API gateway layer",
    },
    "notification_system": {
        "stack": "Event producers → Kafka → Workers → Push/Email/SMS providers",
        "reliability": "At-least-once + idempotency keys",
    },
}
```

## Event-Driven Patterns
```python
PATTERNS = {
    "event_sourcing": "Store events not state — audit trail, replay",
    "saga": {
        "choreography": "Services emit events, others react (decoupled)",
        "orchestration": "Central orchestrator (easier to debug)",
    },
    "outbox_pattern": "Write to outbox table in same transaction, poll to publish",
    "cqrs": "Separate read/write models — read side in Elasticsearch/cache",
}
```

## Database Selection
```python
DB_GUIDE = {
    "relational": "Complex joins, ACID, strict schema — PostgreSQL",
    "document": "Flexible schema, object data, scale out — MongoDB",
    "wide_column": "Time series, write-heavy, known access patterns — Cassandra",
    "graph": "Social networks, recommendations, fraud — Neo4j",
    "key_value": "Caching, sessions, simple lookups — Redis",
    "search": "Full-text, facets, relevance — Elasticsearch",
}
```

## Back of Envelope
```python
ESTIMATES = {
    "time": {
        "RAM": "100 ns", "SSD": "100 us", "HDD": "10 ms", "network_dc": "0.5 ms"
    },
    "storage": {
        "1 char": "1 byte", "1 UUID": "36 bytes",
        "1 tweet": "300 bytes", "1 photo": "2 MB"
    },
    "throughput": {
        "single_server": "10K RPS reads / 1-3K RPS writes",
        "redis": "100K ops/sec",
        "kafka": "1M msgs/sec",
    },
    "uptime": {"99.9%": "8.7 hrs/yr downtime", "99.99%": "52 min/yr downtime"},
}
```

## Models to Use
- **Architecture design**: `claude-opus-4-6` (deep systems reasoning)
- **Trade-off analysis**: `claude-opus-4-6`
- **Capacity planning**: `gpt-4o` with calculations
