
import os
base = 'c:/Users/mirza/MAARS-Command/.claude/skills'
skills = [
    # Database systems deep coverage
    ('mysql-advanced', 'MySQL advanced - InnoDB, partitioning, replication, group replication, JSON, optimizer, tuning'),
    ('oracle-database', 'Oracle Database - PL/SQL, RAC, Data Guard, partitioning, AWR, optimizer, materialized views'),
    ('sql-server-advanced', 'SQL Server advanced - Always On, columnstore, R/Python, Query Store, in-memory OLTP'),
    ('ibm-db2', 'IBM Db2 - pureScale, BLU, WLM, federation, row compression, monitoring, admin API'),
    ('sybase-ase', 'SAP Sybase ASE - databases, segments, procedures, replication, monitoring, performance'),
    ('hbase-advanced', 'HBase advanced - regions, compaction, coprocessors, Phoenix, splits, monitoring, RowKey design'),
    ('apache-solr', 'Apache Solr - schema, analyzers, faceting, spatial, clustering, SolrCloud, replication, plugins'),
    ('couchdb-advanced', 'CouchDB advanced - MVCC, replication, Mango queries, MapReduce, Fauxton, Couchbase migration'),
    ('rethinkdb', 'RethinkDB - changefeeds, ReQL, joins, aggregation, admin UI, failover, clustering'),
    ('arangodb', 'ArangoDB - multi-model, AQL, graph traversal, smart graphs, replication, Foxx, enterprise'),
    ('orientdb', 'OrientDB - document, graph, SQL, schema, clustering, distributed, gremlin, security'),
    ('couchbase-advanced', 'Couchbase advanced - N1QL, FTS, Eventing, Analytics, sync gateway, mobile, capella'),
    ('cosmosdb-advanced', 'Cosmos DB advanced - partitioning, consistency models, multi-master, Gremlin, Mongo API, HTAP'),
    ('dynamodb-advanced', 'DynamoDB advanced - GSI/LSI, streams, TTL, transactions, DAX, single-table design, costs'),
    ('bigtable-advanced', 'Bigtable advanced - schema design, reads/writes, replication, row key, column families, HBase API'),
    ('spanner-advanced', 'Cloud Spanner advanced - interleaving, indexes, DML, read-write transactions, autoscaler, SQL'),
    ('firestore-advanced', 'Firestore advanced - data modeling, composite indexes, transactions, security rules, bundles'),
    ('supabase-advanced', 'Supabase advanced - RLS, realtime, storage, edge functions, auth, vector, pg_cron, webhooks'),
    ('planetscale-advanced', 'PlanetScale advanced - branching, deploy requests, non-blocking DDL, insights, sharding'),
    ('neon-postgres', 'Neon serverless Postgres - branching, autoscaling, logical replication, pgvector, connection pooling'),
    ('turso-database', 'Turso (libSQL) - SQLite at edge, replication, branching, embedding, platform API, multi-tenant'),
    ('singlestore', 'SingleStore - distributed, columnstore, rowstore, pipeline, vector, geospatial, JSON, notebooks'),
    ('tidb-advanced', 'TiDB advanced - HTAP, TiKV, TiFlash, distributed transactions, BR, TiUP, CDC, monitoring'),
    ('cockroachdb-advanced', 'CockroachDB advanced - multi-region, survivability, changefeeds, CDC, cost-based optimizer'),
    ('yugabytedb', 'YugabyteDB - distributed SQL, YSQL, YCQL, xCluster, colocation, tablespaces, CDC, backups'),
    ('vitess-advanced', 'Vitess advanced - sharding, VSchema, vtgate, vttablet, MoveTables, Reshard, keyspaces'),
    ('percona-mysql', 'Percona MySQL/XtraDB - XtraBackup, toolkit, ProxySQL, Percona Monitoring and Management'),
    ('mariadb-advanced', 'MariaDB advanced - Galera cluster, ColumnStore, Spider, sequences, JSON, roles, encryption'),
    # Time series databases
    ('influxdb-advanced', 'InfluxDB advanced - Flux, tasks, dashboards, downsampling, continuous queries, clustering'),
    ('prometheus-advanced', 'Prometheus advanced - remote write, exemplars, TSDB internals, rules, federation, thanos'),
    ('victoria-metrics', 'VictoriaMetrics - single-node, cluster, MetricsQL, vmbackup, alerts, anomaly detection'),
    ('timescaledb-advanced', 'TimescaleDB advanced - hypertables, continuous aggregates, compression, OSS vs Timescale Cloud'),
    ('questdb-advanced', 'QuestDB advanced - SQL dialect, WAL, out-of-order ingestion, ILP, REST API, Grafana'),
    ('m3db', 'M3DB - distributed, m3query, m3coordinator, M3QL, durability, operational challenges'),
    ('opentsdb', 'OpenTSDB - HBase backend, tags, compaction, TSD, gnuplot, HTTP API, schema design'),
    ('kdb-plus', 'kdb+/Q - q language, time series, tick, tick.q, HDB, RDB, qSQL, IPC, analytics'),
    # Vector databases
    ('pinecone-advanced', 'Pinecone advanced - namespaces, metadata filtering, sparse-dense, hybrid search, collections'),
    ('weaviate-advanced', 'Weaviate advanced - schema, modules, BM25, hybrid, generative, cross-references, multi-tenancy'),
    ('qdrant-advanced', 'Qdrant advanced - collections, payload filtering, sparse vectors, snapshots, clustering, optimization'),
    ('milvus-advanced', 'Milvus advanced - partitions, index types, hybrid search, GPU, CDC, data pipeline, Zilliz'),
    ('chroma-advanced', 'Chroma - embedding functions, persistence, filtering, collections, multi-modal, recipes'),
    ('pgvector-advanced', 'pgvector advanced - HNSW, IVFFlat, approximate search, distance functions, indexing, filtering'),
    # Search engines
    ('elasticsearch-advanced', 'Elasticsearch advanced - mappings, analyzers, aggregations, ML, EQL, ILM, cross-cluster'),
    ('opensearch-advanced', 'OpenSearch advanced - ML plugin, k-NN, anomaly detection, PPL, Dashboards, security'),
    ('algolia-advanced', 'Algolia advanced - relevance, merchandising, A/B test, neural, recommend, personalisation'),
    ('typesense-advanced', 'Typesense advanced - schema, search params, curation, synonyms, geo, analytics, cloud'),
    ('meilisearch-advanced', 'Meilisearch advanced - filterable, sortable, faceting, multi-search, snapshots, cloud'),
    ('sphinx-search', 'Sphinx Search - indexing, searching, SphinxQL, RT indexes, distributed, Python API'),
    # Graph databases
    ('neo4j-advanced', 'Neo4j advanced - Cypher, APOC, Graph Data Science, causal cluster, bloom, enterprise'),
    ('neptune-advanced', 'Amazon Neptune advanced - Gremlin, SPARQL, full-text, ML, streams, notebooks, export'),
    ('tigergraph', 'TigerGraph - GSQL, algorithms, ML workbench, graph studio, cloud, REST++, enterprise'),
    ('janusgraph', 'JanusGraph - Gremlin, Cassandra/HBase backend, Elasticsearch indexing, distributed, schema'),
    ('dgraph-advanced', 'Dgraph advanced - DQL, GraphQL, mutations, lambdas, multi-tenancy, ACL, slash graphql'),
    ('memgraph', 'Memgraph - in-memory, Cypher, MAGE algorithms, streams, triggers, multi-tenancy, HA'),
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
