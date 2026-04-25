
import os
base = 'c:/Users/mirza/MAARS-Command/.claude/skills'
skills = [
    # Mobile platform engineering deep
    ('ios-platform-engineering', 'iOS platform engineering - modular architecture, Swift Package Manager, Bazel, app extensions, framework'),
    ('android-platform-engineering', 'Android platform engineering - modular builds, Gradle plugins, baseline profiles, multi-module'),
    ('mobile-ci-cd-advanced', 'Mobile CI/CD advanced - Fastlane advanced, Bitrise, App Center, code signing, TestFlight, staged rollout'),
    ('mobile-performance-advanced', 'Mobile performance advanced - startup optimization, jank detection, memory profiling, battery impact'),
    ('cross-platform-advanced', 'Cross-platform mobile advanced - Flutter architecture, React Native new architecture, KMM/KMP'),
    ('mobile-security-advanced', 'Mobile security advanced - certificate pinning, jailbreak detection, RASP, binary protection, obfuscation'),
    ('mobile-testing-advanced', 'Mobile testing advanced - XCUITest, Espresso, Detox, device farms, visual testing, accessibility'),
    ('mobile-analytics-platform', 'Mobile analytics platform - Firebase, Amplitude, event schema, funnel analysis, retention, cohorts'),
    ('push-notification-platform', 'Push notification platform - APNs, FCM, notification hub, segmentation, delivery tracking, rich push'),
    ('mobile-ml-on-device', 'Mobile ML on-device - Core ML, TFLite, MediaPipe, model optimization, hardware acceleration, privacy'),
    # Observability and APM platform advanced
    ('distributed-tracing-advanced', 'Distributed tracing advanced - Jaeger, Zipkin, W3C TraceContext, sampling strategies, trace analysis'),
    ('log-management-platform', 'Log management platform - Loki, Elasticsearch, structured logging, log routing, retention, cost'),
    ('metrics-platform-advanced', 'Metrics platform advanced - Prometheus federation, Thanos, Mimir, cardinality management, recording rules'),
    ('apm-platform-advanced', 'APM platform advanced - Datadog APM, New Relic, Dynatrace, auto-instrumentation, service maps'),
    ('real-user-monitoring', 'Real user monitoring - Core Web Vitals, session replay, error tracking, user journeys, Sentry'),
    ('synthetic-monitoring-advanced', 'Synthetic monitoring advanced - multi-step browser tests, API monitoring, global nodes, alerting'),
    ('profiling-platform-advanced', 'Profiling platform advanced - continuous profiling, Pyroscope, pprof, flame graphs, CPU/memory'),
    ('ebpf-observability', 'eBPF observability - Cilium, Pixie, Falco, kernel-level tracing, network visibility, security monitoring'),
    ('opentelemetry-platform', 'OpenTelemetry platform - collector configuration, processors, exporters, auto-instrumentation, OTLP'),
    ('slo-platform-engineering', 'SLO platform engineering - error budget tracking, alerting policies, reliability reporting, dashboards'),
    # Database platform engineering specialized
    ('postgresql-platform-engineering', 'PostgreSQL platform engineering - logical replication, Citus sharding, extensions, pgBouncer, tuning'),
    ('mysql-platform-advanced', 'MySQL platform advanced - Group Replication, ProxySQL, InnoDB tuning, GTID, schema migrations'),
    ('mongodb-platform-advanced', 'MongoDB platform advanced - sharding, replica sets, aggregation pipeline, Atlas, change streams'),
    ('redis-platform-advanced', 'Redis platform advanced - cluster mode, Redis Modules, Streams, Search, JSON, time series, keyspace'),
    ('cassandra-platform-advanced', 'Cassandra platform advanced - data modeling, compaction strategies, repair, vnodes, multi-DC'),
    ('elasticsearch-platform-advanced', 'Elasticsearch platform advanced - index lifecycle, cross-cluster, custom analyzers, EQL, vector search'),
    ('timeseries-database-platform', 'Time-series database platform - InfluxDB, TimescaleDB, VictoriaMetrics, retention, downsampling'),
    ('graph-database-platform', 'Graph database platform - Neo4j clustering, Gremlin, Cypher optimization, graph algorithms, APOC'),
    ('vector-database-platform', 'Vector database platform - Pinecone, Weaviate, Qdrant, Milvus, HNSW, ANN algorithms, hybrid search'),
    ('database-migration-platform', 'Database migration platform - Flyway, Liquibase, zero-downtime migrations, schema versioning, rollback'),
    # Search platform engineering
    ('enterprise-search-platform', 'Enterprise search platform - Solr cloud, Elasticsearch clusters, relevance tuning, query understanding'),
    ('semantic-search-advanced', 'Semantic search advanced - dense retrieval, bi-encoders, cross-encoders, ColBERT, hybrid search'),
    ('search-relevance-engineering', 'Search relevance engineering - LTR, click models, A/B testing, NDCG, query analysis'),
    ('search-infrastructure-advanced', 'Search infrastructure advanced - indexing pipeline, real-time updates, multi-tenancy, geo-search'),
    ('nlp-search-platform', 'NLP search platform - query expansion, spell correction, intent detection, entity extraction, synonyms'),
    ('knowledge-base-search', 'Knowledge base search - FAQ matching, question answering, passage retrieval, confidence scoring'),
    ('multimodal-search', 'Multimodal search - image search, video search, audio search, cross-modal retrieval, CLIP embeddings'),
    ('search-personalization', 'Search personalization - user signals, behavioral ranking, collaborative filtering, context-aware'),
    ('search-analytics-advanced', 'Search analytics advanced - no-results analysis, click-through, query clustering, A/B experiments'),
    ('federated-search-platform', 'Federated search platform - meta-search, result merging, source ranking, distributed queries'),
    # Messaging and event streaming platform deep
    ('kafka-platform-advanced', 'Kafka platform advanced - tiered storage, KRaft, MirrorMaker 2, quotas, Schema Registry, Kafka Connect'),
    ('rabbitmq-platform-advanced', 'RabbitMQ platform advanced - federation, shovel, quorum queues, streams, AMQP, cluster tuning'),
    ('pulsar-platform-advanced', 'Pulsar platform advanced - geo-replication, multi-tenancy, tiered storage, functions, IO connectors'),
    ('event-streaming-patterns', 'Event streaming patterns - event sourcing, outbox pattern, saga, choreography, event routing'),
    ('message-schema-management', 'Message schema management - Avro, Protobuf, JSON Schema, compatibility checking, evolution'),
    ('dead-letter-queue-patterns', 'Dead letter queue patterns - poison messages, retry strategies, DLQ analysis, circuit breakers'),
    ('event-driven-integration', 'Event-driven integration - EDA patterns, event catalog, consumer groups, partition strategies'),
    ('streaming-etl-platform', 'Streaming ETL platform - Flink, Spark Streaming, Kafka Streams, stateful processing, windowing'),
    ('pubsub-platform-advanced', 'Pub/Sub platform advanced - GCP Pub/Sub, AWS SNS/SQS, Azure Service Bus, fan-out patterns'),
    ('message-queue-operations', 'Message queue operations - capacity planning, consumer lag monitoring, rebalancing, tuning'),
    # Network security platform deep
    ('zero-trust-network-access', 'Zero trust network access - BeyondCorp, Zscaler, Cloudflare Access, identity-aware proxy, microseg'),
    ('network-detection-response', 'Network detection and response - NDR, east-west traffic, encrypted traffic analysis, anomaly detection'),
    ('ddos-protection-advanced', 'DDoS protection advanced - anycast, scrubbing centers, rate limiting, BGP blackhole, Cloudflare Magic'),
    ('firewall-platform-advanced', 'Firewall platform advanced - NGFW, SASE, policy management, microsegmentation, east-west'),
    ('network-forensics-advanced', 'Network forensics advanced - packet capture, PCAP analysis, Wireshark, NetFlow, traffic reconstruction'),
    ('dns-security-advanced', 'DNS security advanced - DNSSEC, DNS-over-HTTPS, RPZ, DNS sinkholing, exfiltration detection'),
    ('email-security-advanced', 'Email security advanced - DMARC enforcement, BIMI, anti-phishing, sandboxing, DLP, secure gateway'),
    ('web-application-firewall-advanced', 'WAF advanced - ModSecurity, Imperva, F5 ASM, custom rules, false positive tuning, bot management'),
    ('vpn-platform-advanced', 'VPN platform advanced - WireGuard, IPsec, split tunneling, zero trust migration, SDN integration'),
    ('network-access-control', 'Network access control - 802.1X, NAC platforms, endpoint posture, quarantine VLAN, ForeScout'),
]

for name, desc in skills:
    d = os.path.join(base, name)
    os.makedirs(d, exist_ok=True)
    title = name.replace('-', ' ').title()
    content = f'''---
name: {name}
description: {desc}
---

# {title} - MAARS Reference

## Overview
{desc}

## Core Framework
Use structured approach: define goal, identify audience, create hypothesis, execute, measure.

## Key Prompts
- "For [project], implement {title.lower()} for [use case]. Requirements: [X]. Provide working code examples."
- "Analyze [existing implementation] and suggest 3 improvements prioritized by impact."
- "Write a {title.lower()} template for a [type] project with [specific requirements]."

## Best Practices
1. Read official documentation before implementation
2. Test in isolation before full integration
3. Handle errors and edge cases explicitly
4. Document configuration and requirements
5. Monitor and alert on key metrics

## Common Patterns
- Setup and initialization
- Core operations
- Error handling and retries
- Authentication and security
- Performance and scaling

## Models to Use
- Architecture: claude-opus-4-6
- Implementation: claude-sonnet-4-6
- Quick lookups: claude-haiku-4-5-20251001
'''
    with open(os.path.join(d, 'SKILL.md'), 'w') as f:
        f.write(content)

print('Done:', len(skills), 'skills')
