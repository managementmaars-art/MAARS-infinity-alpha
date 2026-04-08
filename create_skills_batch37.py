
import os
base = 'c:/Users/mirza/MAARS-Command/.claude/skills'
skills = [
    # AWS granular services
    ('ec2-advanced', 'EC2 advanced - instance types, placement groups, Nitro, ENA, SR-IOV, hibernation, launch templates'),
    ('s3-advanced', 'S3 advanced - object lock, replication, intelligent tiering, lifecycle, event notifications, S3 Express'),
    ('rds-advanced', 'RDS advanced - Multi-AZ, read replicas, proxy, Graviton, Performance Insights, Aurora I/O-Optimized'),
    ('aurora-advanced', 'Aurora advanced - Serverless v2, Global Database, blue/green, RDS Data API, Babelfish, parallel query'),
    ('lambda-advanced', 'Lambda advanced - SnapStart, extensions, VPC, provisioned concurrency, code signing, URLs, ARM'),
    ('fargate-advanced', 'Fargate advanced - task sizing, spot, Graviton, Fargate Spot, networking, storage, Windows'),
    ('eks-advanced', 'EKS advanced - managed node groups, Fargate profiles, Karpenter, networking, Pod Identity, Blueprints'),
    ('cloudfront-advanced', 'CloudFront advanced - Functions, Lambda@Edge, Origin Shield, field-level encryption, geo restriction'),
    ('route53-advanced', 'Route 53 advanced - routing policies, health checks, traffic flow, resolver, private zones, DNSSEC'),
    ('vpc-advanced', 'VPC advanced - transit gateway, PrivateLink, flow logs, Network Firewall, Reachability Analyzer'),
    ('iam-advanced', 'IAM advanced - identity center, permission sets, attribute-based, policy conditions, access analyzer'),
    ('cloudwatch-advanced', 'CloudWatch advanced - EMF, anomaly detection, composite alarms, cross-account, Logs Insights'),
    ('sqs-sns-advanced', 'SQS/SNS advanced - FIFO, deduplication, message filtering, DLQ, large messages, fan-out'),
    ('eventbridge-advanced', 'EventBridge advanced - pipes, scheduler, global endpoints, schema registry, archive, replay'),
    ('step-functions-advanced', 'Step Functions advanced - Express, SDK integration, Map state optimization, Redrive, versions'),
    ('bedrock-advanced', 'Amazon Bedrock advanced - model invocation, agents, knowledge bases, guardrails, custom models'),
    ('sagemaker-advanced', 'SageMaker advanced - pipelines, feature store, model monitor, clarify, Canvas, JumpStart, HyperPod'),
    ('athena-advanced', 'Athena advanced - Iceberg, ACID, Spark, federated queries, query result reuse, DDL/DML'),
    ('glue-advanced', 'AWS Glue advanced - Spark, Ray, streaming, DataBrew, Data Quality, G.2X, custom connectors'),
    ('redshift-advanced', 'Redshift advanced - Serverless, RA3, Auto Copy, Spectrum, ML, spatial, materialized views'),
    ('kinesis-advanced', 'Kinesis advanced - enhanced fan-out, Data Firehose, Data Analytics, Video Streams, Lambda triggers'),
    ('emr-advanced', 'EMR advanced - Serverless, on EKS, Studio, managed scaling, instance fleets, auto-termination'),
    ('opensearch-service', 'OpenSearch Service advanced - custom plugins, UltraWarm, cold storage, ML, fine-grained access'),
    ('elasticache-advanced', 'ElastiCache advanced - Serverless, global datastore, Redis v7, data tiering, TLS, encryption'),
    ('documentdb-advanced', 'DocumentDB advanced - elastic clusters, global clusters, change streams, profiler, index advisor'),
    ('appsync-advanced', 'AppSync advanced - JS resolvers, event API, merged APIs, caching, real-time, Lambda resolvers'),
    ('cognito-advanced', 'Cognito advanced - hosted UI, OIDC/SAML, triggers, advanced security, user import, tokens'),
    ('waf-advanced', 'AWS WAF advanced - managed rules, bot control, fraud control, ATP, Shield Advanced, rate-based'),
    ('secrets-manager-advanced', 'Secrets Manager advanced - rotation, cross-account, RDS integration, Lambda rotation, TTL'),
    ('config-advanced', 'AWS Config advanced - conformance packs, remediation, aggregators, custom rules, timeline, compliance'),
    # GCP granular services
    ('bigquery-advanced', 'BigQuery advanced - BI Engine, ML, Omni, Analytics Hub, authorized views, row security, INFORMATION_SCHEMA'),
    ('gke-advanced', 'GKE advanced - autopilot, workload identity, node auto-provisioning, fleet, config sync, multi-cluster'),
    ('cloud-run-advanced', 'Cloud Run advanced - services, jobs, sidecars, GPU, cloud run functions, traffic splitting, probes'),
    ('cloud-functions-advanced', 'Cloud Functions advanced - v2, triggers, concurrency, min instances, secrets, VPC connector'),
    ('pub-sub-advanced', 'Pub/Sub advanced - ordering, dead letter, push subscriptions, exactly-once, BigQuery sink, lite'),
    ('dataflow-advanced', 'Dataflow advanced - Flex templates, streaming, exactly-once, runner v2, side inputs, DoFn'),
    ('dataplex-advanced', 'Dataplex advanced - data mesh, quality, discovery, Spark tasks, profile, metadata, workspaces'),
    ('vertex-ai-advanced', 'Vertex AI advanced - training, prediction, pipeline, model garden, Colab Enterprise, TensorBoard'),
    ('cloud-spanner-advanced', 'Cloud Spanner advanced - instance types, split, statistics, NUMERIC, JSON, multi-region, DML'),
    ('alloydb-advanced', 'AlloyDB advanced - columnar engine, ML predictions, Omni, PITR, connection pooling, analytics'),
    # Azure granular services
    ('azure-openai-advanced', 'Azure OpenAI advanced - PTU, fine-tuning, assistants, DALL-E, Whisper, content filtering'),
    ('azure-ml-advanced', 'Azure ML advanced - AutoML, designer, pipelines, responsible AI, model monitoring, compute clusters'),
    ('azure-data-factory', 'Azure Data Factory advanced - mapping flows, wrangling, IR, self-hosted, triggers, monitoring'),
    ('synapse-advanced', 'Azure Synapse advanced - dedicated pool, serverless, Spark, pipelines, Link for Cosmos, purview'),
    ('azure-kubernetes', 'AKS advanced - node pools, KEDA, AGIC, workload identity, Azure CNI, cost analysis'),
    ('azure-container-apps', 'Azure Container Apps advanced - KEDA, Dapr, jobs, dedicated, workload profiles, environments'),
    ('azure-service-bus', 'Azure Service Bus advanced - sessions, duplicate detection, dead letter, geo-DR, transactions'),
    ('azure-event-grid', 'Azure Event Grid advanced - partner topics, pull delivery, namespace topics, filtering, CloudEvents'),
    ('azure-api-management', 'Azure APIM advanced - policies, backends, named values, developer portal, self-hosted gateway'),
    ('azure-cosmos-advanced', 'Azure Cosmos DB advanced - partition key design, consistency, multi-write, Synapse Link, PITR'),
    ('azure-cognitive-search', 'Azure Cognitive Search - indexers, skillsets, semantic, vector, hybrid, knowledge mining'),
    ('azure-purview', 'Microsoft Purview - data map, data catalog, data lineage, sensitivity labels, scanning, policies'),
    ('azure-monitor-advanced', 'Azure Monitor advanced - workbooks, alerts, ITSM, Log Analytics workspace, private link scope'),
    ('azure-sentinel', 'Microsoft Sentinel advanced - analytics rules, playbooks, hunting, watchlists, entity behavior, UEBA'),
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
