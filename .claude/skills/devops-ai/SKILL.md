---
name: devops-ai
description: AI DevOps skills — CI/CD pipelines, Docker, Kubernetes, Terraform, GitHub Actions, monitoring, incident response, SRE for MAARS infrastructure agents
---

# DevOps AI — MAARS Reference

## CI/CD Pipeline Templates

### GitHub Actions
```yaml
# .github/workflows/deploy.yml
name: Build & Deploy

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: pip install -r requirements.txt && pytest --cov=. --cov-report=xml
      - uses: codecov/codecov-action@v4

  build:
    needs: test
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - uses: docker/build-push-action@v5
        with:
          push: ${{ github.ref == 'refs/heads/main' }}
          tags: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:latest
          cache-from: type=gha
          cache-to: type=gha,mode=max

  deploy:
    needs: build
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v4
      - name: Deploy to production
        run: |
          echo "${{ secrets.DEPLOY_KEY }}" > key.pem
          chmod 600 key.pem
          ssh -i key.pem -o StrictHostKeyChecking=no user@${{ secrets.SERVER_IP }} \
            "docker pull ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:latest && \
             docker-compose up -d"
```

## Docker Best Practices
```dockerfile
# Multi-stage build — Python FastAPI
FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.12-slim AS runtime
WORKDIR /app
# Non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser
COPY --from=builder /root/.local /home/appuser/.local
COPY --chown=appuser:appuser . .
USER appuser
ENV PATH=/home/appuser/.local/bin:$PATH
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s \
  CMD curl -f http://localhost:8000/health || exit 1
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

## Kubernetes Deployment
```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: maars-api
  labels: { app: maars-api }
spec:
  replicas: 3
  selector:
    matchLabels: { app: maars-api }
  template:
    metadata:
      labels: { app: maars-api }
    spec:
      containers:
        - name: maars-api
          image: ghcr.io/org/maars-api:latest
          ports: [{ containerPort: 8000 }]
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef: { name: maars-secrets, key: database-url }
          resources:
            requests: { memory: "256Mi", cpu: "100m" }
            limits: { memory: "512Mi", cpu: "500m" }
          livenessProbe:
            httpGet: { path: /health, port: 8000 }
            initialDelaySeconds: 10
          readinessProbe:
            httpGet: { path: /ready, port: 8000 }
      imagePullSecrets: [{ name: ghcr-secret }]
---
apiVersion: v1
kind: Service
metadata: { name: maars-api }
spec:
  selector: { app: maars-api }
  ports: [{ port: 80, targetPort: 8000 }]
  type: ClusterIP
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata: { name: maars-api-hpa }
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: maars-api
  minReplicas: 2
  maxReplicas: 20
  metrics:
    - type: Resource
      resource:
        name: cpu
        target: { type: Utilization, averageUtilization: 70 }
```

## Terraform Infrastructure
```hcl
# main.tf — AWS ECS + RDS + ElastiCache
terraform {
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 5.0" }
  }
  backend "s3" {
    bucket = "maars-terraform-state"
    key    = "prod/terraform.tfstate"
    region = "us-east-1"
  }
}

module "vpc" {
  source = "terraform-aws-modules/vpc/aws"
  name   = "maars-vpc"
  cidr   = "10.0.0.0/16"
  azs             = ["us-east-1a", "us-east-1b", "us-east-1c"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]
  enable_nat_gateway = true
}

resource "aws_ecs_cluster" "main" {
  name = "maars-cluster"
  setting { name = "containerInsights", value = "enabled" }
}

resource "aws_db_instance" "postgres" {
  identifier        = "maars-db"
  engine            = "postgres"
  engine_version    = "16"
  instance_class    = "db.t4g.medium"
  allocated_storage = 100
  storage_encrypted = true
  multi_az          = true
  skip_final_snapshot = false
}
```

## Monitoring Stack
```python
MONITORING_STACK = {
    "metrics": {
        "tool": "Prometheus + Grafana",
        "key_metrics": [
            "request_rate", "error_rate", "latency_p99",
            "cpu_usage", "memory_usage", "db_connections",
        ],
    },
    "logs": {
        "tool": "Loki + Grafana or Datadog",
        "structured_logging": "JSON format always",
        "levels": ["DEBUG (dev only)", "INFO", "WARNING", "ERROR", "CRITICAL"],
    },
    "tracing": {
        "tool": "Jaeger or Tempo (OpenTelemetry)",
        "instrument": "All HTTP calls, DB queries, external APIs",
    },
    "alerts": {
        "tool": "PagerDuty / OpsGenie",
        "sev1": "Immediate page (P99 > 2s, error rate > 5%)",
        "sev2": "Page in 15min (P99 > 1s, error rate > 1%)",
        "sev3": "Slack only (warnings, capacity)",
    },
}

# FastAPI + OpenTelemetry
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

FastAPIInstrumentor.instrument_app(app)
SQLAlchemyInstrumentor().instrument(engine=engine)
```

## AI-Assisted Incident Response
```python
INCIDENT_RESPONSE_PROMPT = """
You are an SRE analyzing an incident.

Alert: {alert_name}
Severity: {severity}
Started: {start_time}
Services affected: {services}
Error logs (last 50 lines): {logs}
Recent deployments: {recent_deploys}
Metrics: {metrics_summary}

Provide:
1. LIKELY ROOT CAUSE: Top 2-3 hypotheses with evidence
2. IMMEDIATE ACTIONS: Steps to mitigate now (stop the bleeding)
3. INVESTIGATION STEPS: Commands to run to confirm root cause
4. ROLLBACK PLAN: If deploy-related, steps to rollback
5. CUSTOMER IMPACT: Who is affected and how to communicate
6. PREVENTION: What to add to prevent recurrence

Format as runbook for on-call engineer.
"""
```

## Models to Use
- **Incident analysis**: `claude-opus-4-6` (best reasoning for complex outages)
- **Log analysis**: `gpt-4o` (fast pattern recognition)
- **IaC generation**: `claude-sonnet-4-6` (Terraform, K8s YAML)
- **Cost optimization**: `gpt-4o` with cloud billing data
- **Security review**: `claude-opus-4-6` (subtle misconfig detection)
