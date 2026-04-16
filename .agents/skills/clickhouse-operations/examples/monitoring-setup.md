# Real-World Monitoring Setup Examples

Production-ready monitoring implementations for ClickHouse using Prometheus, Grafana, and other tools.

## Prometheus Configuration for ClickHouse

### prometheus.yml Configuration

```yaml
global:
  scrape_interval: 30s
  evaluation_interval: 30s
  external_labels:
    cluster: 'production'
    environment: 'prod'

scrape_configs:
  - job_name: 'clickhouse-metrics'
    metrics_path: '/metrics'
    static_configs:
      - targets:
          - 'clickhouse1.example.com:8888'
          - 'clickhouse2.example.com:8888'
          - 'clickhouse3.example.com:8888'
        labels:
          service: 'clickhouse'
          tier: 'database'
    relabel_configs:
      - source_labels: [__address__]
        target_label: instance
      - source_labels: [__scheme__]
        target_label: scheme

  - job_name: 'clickhouse-native'
    # Uses ClickHouse built-in prometheus endpoint
    static_configs:
      - targets:
          - 'clickhouse1.example.com:9090'
          - 'clickhouse2.example.com:9090'
          - 'clickhouse3.example.com:9090'
    scrape_interval: 60s  # Less frequent for system metrics

alerting:
  alertmanagers:
    - static_configs:
        - targets: ['alertmanager:9093']

rule_files:
  - '/etc/prometheus/rules/clickhouse-alerts.yml'
```

### Prometheus Alert Rules (clickhouse-alerts.yml)

```yaml
groups:
  - name: clickhouse
    interval: 30s
    rules:
      # Critical Alerts
      - alert: ClickHouseDiskSpaceLow
        expr: (node_filesystem_avail_bytes{mountpoint="/var/lib/clickhouse"} / node_filesystem_size_bytes{mountpoint="/var/lib/clickhouse"}) < 0.15
        for: 5m
        annotations:
          severity: critical
          summary: 'ClickHouse disk space critically low (< 15%)'
          description: 'Instance {{ $labels.instance }} has < 15% disk space free'

      - alert: ClickHouseMemoryUsageHigh
        expr: (process_resident_memory_bytes{job="clickhouse-metrics"} / node_memory_MemTotal_bytes) > 0.85
        for: 10m
        annotations:
          severity: critical
          summary: 'ClickHouse memory usage > 85%'
          description: 'Instance {{ $labels.instance }} memory usage: {{ $value | humanizePercentage }}'

      - alert: ClickHouseQueryTimeoutRate
        expr: rate(clickhouse_query_duration_ms_bucket{le="+Inf"}[5m]) < rate(clickhouse_query_duration_ms_bucket{le="5000"}[5m]) * 0.01
        for: 5m
        annotations:
          severity: warning
          summary: 'High ClickHouse query timeout rate'
          description: 'Query timeout rate > 1% on {{ $labels.instance }}'

      # Warning Alerts
      - alert: ClickHouseReplicationLagHigh
        expr: clickhouse_replication_lag_seconds > 60
        for: 5m
        annotations:
          severity: warning
          summary: 'ClickHouse replication lag > 60s'
          description: 'Table {{ $labels.table }} lag: {{ $value }}s'

      - alert: ClickHouseConnectionsNearLimit
        expr: (clickhouse_tcp_connections_total / 4096) > 0.8
        for: 5m
        annotations:
          severity: warning
          summary: 'ClickHouse connections > 80% of limit'
          description: 'Current connections: {{ $value }}/4096'

      - alert: ClickHouseInsertSlowdown
        expr: rate(clickhouse_inserted_rows_total[5m]) < on (table) rate(clickhouse_inserted_rows_total[1h]) * 0.5
        for: 10m
        annotations:
          severity: warning
          summary: 'ClickHouse insert rate dropped > 50%'
          description: 'Table {{ $labels.table }} insert rate significantly reduced'

      - alert: ClickHousePartCountHigh
        expr: clickhouse_parts_active > 1000
        for: 15m
        annotations:
          severity: warning
          summary: 'ClickHouse table fragmentation (> 1000 parts)'
          description: 'Table {{ $labels.table }}: {{ $value }} parts (performance degrading)'

      - alert: ClickHouseErrorRateHigh
        expr: rate(clickhouse_query_duration_ms_count{status="error"}[5m]) / rate(clickhouse_query_duration_ms_count[5m]) > 0.01
        for: 5m
        annotations:
          severity: warning
          summary: 'ClickHouse error rate > 1%'
          description: 'Error rate: {{ $value | humanizePercentage }}'

      # Informational
      - alert: ClickHouseBackupNotRecent
        expr: (time() - clickhouse_last_successful_backup_time) / 3600 > 24
        for: 1h
        annotations:
          severity: info
          summary: 'ClickHouse backup older than 24 hours'
          description: 'Last backup: {{ $value | humanizeDuration }} ago'
```

---

## Grafana Dashboard Configuration

### JSON Dashboard for Cluster Overview

```json
{
  "dashboard": {
    "title": "ClickHouse Cluster Overview",
    "tags": ["clickhouse", "cluster", "production"],
    "timezone": "browser",
    "panels": [
      {
        "title": "Cluster Health Status",
        "type": "stat",
        "targets": [
          {
            "expr": "count(up{job='clickhouse-metrics'})"
          }
        ]
      },
      {
        "title": "Query Latency (p95)",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(clickhouse_query_duration_ms_bucket[5m]))"
          }
        ],
        "yaxes": [
          {
            "label": "Duration (ms)",
            "format": "short"
          }
        ],
        "alert": {
          "name": "High Query Latency",
          "conditions": [
            {
              "evaluator": {
                "params": [5000],
                "type": "gt"
              }
            }
          ]
        }
      },
      {
        "title": "Insert Rate (rows/sec)",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(clickhouse_inserted_rows_total[5m])"
          }
        ]
      },
      {
        "title": "Memory Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "process_resident_memory_bytes{job='clickhouse-metrics'} / 1024 / 1024 / 1024"
          }
        ],
        "yaxes": [
          {
            "label": "Memory (GB)"
          }
        ]
      },
      {
        "title": "Disk Space Usage",
        "type": "bargauge",
        "targets": [
          {
            "expr": "(node_filesystem_size_bytes{mountpoint='/var/lib/clickhouse'} - node_filesystem_avail_bytes{mountpoint='/var/lib/clickhouse'}) / node_filesystem_size_bytes{mountpoint='/var/lib/clickhouse'} * 100"
          }
        ]
      },
      {
        "title": "Replication Lag",
        "type": "graph",
        "targets": [
          {
            "expr": "clickhouse_replication_lag_seconds"
          }
        ],
        "yaxes": [
          {
            "label": "Lag (seconds)"
          }
        ]
      },
      {
        "title": "Error Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(clickhouse_query_duration_ms_count{status='error'}[5m]) / rate(clickhouse_query_duration_ms_count[5m]) * 100"
          }
        ],
        "yaxes": [
          {
            "label": "Error Rate (%)"
          }
        ]
      },
      {
        "title": "Table Fragmentation (parts count)",
        "type": "table",
        "targets": [
          {
            "expr": "topk(10, clickhouse_parts_active)"
          }
        ]
      }
    ]
  }
}
```

### ClickHouse Query for Grafana (via datasource)

Create ClickHouse as Grafana datasource pointing to `http://clickhouse:8123`

**Query Examples for Grafana Panels:**

```sql
-- Query Latency Percentiles (P50, P95, P99)
SELECT
    toStartOfMinute(event_time) as time,
    quantile(0.50)(query_duration_ms) as p50,
    quantile(0.95)(query_duration_ms) as p95,
    quantile(0.99)(query_duration_ms) as p99
FROM system.query_log
WHERE event_date >= today() - 7
  AND type = 'QueryFinish'
GROUP BY time
ORDER BY time DESC;

-- Insert Throughput by Table
SELECT
    toStartOfMinute(event_time) as time,
    table,
    SUM(rows) / max(CAST(query_duration_ms as Float64)) * 1000 as rows_per_sec
FROM system.query_log
WHERE query LIKE 'INSERT%'
  AND type = 'QueryFinish'
  AND event_date >= today()
GROUP BY time, table
ORDER BY time DESC;

-- Query Count by User
SELECT
    user,
    COUNT() as query_count
FROM system.query_log
WHERE event_date >= today()
  AND type = 'QueryFinish'
GROUP BY user
ORDER BY query_count DESC;
```

---

## DataDog Integration

### Python Script for Custom Metrics

```python
#!/usr/bin/env python3
"""ClickHouse metrics exporter to DataDog"""

import os
import time
from clickhouse_driver import Client
from datadog import initialize, api

# Configuration
CLICKHOUSE_HOST = os.getenv('CLICKHOUSE_HOST', 'localhost')
CLICKHOUSE_PORT = int(os.getenv('CLICKHOUSE_PORT', '9000'))
DD_API_KEY = os.getenv('DD_API_KEY')
DD_APP_KEY = os.getenv('DD_APP_KEY')
ENVIRONMENT = os.getenv('ENVIRONMENT', 'production')

client = Client(CLICKHOUSE_HOST, CLICKHOUSE_PORT, database='default')

def send_metric(metric_name, value, tags=None):
    """Send metric to DataDog"""
    if tags is None:
        tags = []
    tags.extend([f'env:{ENVIRONMENT}', 'service:clickhouse'])

    api.Metric.send(
        metric='clickhouse.' + metric_name,
        points=value,
        tags=tags
    )

def collect_query_metrics():
    """Collect query performance metrics"""
    result = client.execute("""
        SELECT
            quantile(0.95)(query_duration_ms) as p95_latency,
            COUNT() as query_count,
            SUM(if(exception != '', 1, 0)) as error_count
        FROM system.query_log
        WHERE event_date >= today()
          AND type = 'QueryFinish'
    """)

    p95_latency, query_count, error_count = result[0]

    send_metric('query.latency_p95', p95_latency, tags=['metric:latency'])
    send_metric('query.count', query_count, tags=['metric:throughput'])
    send_metric('query.error_count', error_count, tags=['metric:errors'])

def collect_insert_metrics():
    """Collect insert performance metrics"""
    result = client.execute("""
        SELECT
            table,
            SUM(rows) as total_rows,
            SUM(rows) / SUM(CAST(query_duration_ms as Float64)) * 1000 as rows_per_second
        FROM system.query_log
        WHERE query LIKE 'INSERT%'
          AND type = 'QueryFinish'
          AND event_date >= today()
        GROUP BY table
    """)

    for table, rows, throughput in result:
        send_metric('insert.rows', rows, tags=[f'table:{table}'])
        send_metric('insert.throughput', throughput, tags=[f'table:{table}'])

def collect_resource_metrics():
    """Collect resource utilization"""
    # Memory
    result = client.execute("""
        SELECT value FROM system.metrics WHERE metric = 'MemoryTracking'
    """)
    memory_bytes = result[0][0]
    send_metric('memory.usage', memory_bytes / 1024 / 1024 / 1024, tags=['metric:memory'])

    # Disk
    result = client.execute("""
        SELECT
            free_space,
            total_space
        FROM system.disks
    """)
    free, total = result[0]
    disk_pct = (total - free) / total * 100
    send_metric('disk.usage_percent', disk_pct, tags=['metric:disk'])

def collect_replication_metrics():
    """Collect replication lag"""
    result = client.execute("""
        SELECT
            table,
            absolute_delay
        FROM system.replicas
        WHERE absolute_delay > 0
    """)

    for table, lag in result:
        send_metric('replication.lag', lag, tags=[f'table:{table}'])

def collect_part_metrics():
    """Collect table fragmentation"""
    result = client.execute("""
        SELECT
            table,
            COUNT() as parts_count
        FROM system.parts
        WHERE active = 1
        GROUP BY table
        HAVING COUNT() > 100
    """)

    for table, parts in result:
        send_metric('table.parts_count', parts, tags=[f'table:{table}'])

def main():
    """Main collection loop"""
    options = {
        'api_key': DD_API_KEY,
        'app_key': DD_APP_KEY
    }
    initialize(**options)

    while True:
        try:
            print(f'[{time.ctime()}] Collecting ClickHouse metrics...')
            collect_query_metrics()
            collect_insert_metrics()
            collect_resource_metrics()
            collect_replication_metrics()
            collect_part_metrics()
            print('✓ Metrics sent to DataDog')
        except Exception as e:
            print(f'✗ Error collecting metrics: {e}')

        time.sleep(60)  # Collect every minute

if __name__ == '__main__':
    main()
```

### SystemD Service for Exporter

```ini
[Unit]
Description=ClickHouse DataDog Metrics Exporter
After=network.target clickhouse-server.service
Wants=clickhouse-server.service

[Service]
Type=simple
User=clickhouse
Environment="DD_API_KEY=your_api_key"
Environment="DD_APP_KEY=your_app_key"
Environment="ENVIRONMENT=production"
Environment="CLICKHOUSE_HOST=localhost"
ExecStart=/usr/local/bin/clickhouse_datadog_exporter.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

---

## Custom Health Check Script

```bash
#!/bin/bash
# clickhouse_health_check.sh
# Run regularly to validate ClickHouse cluster health

set -e

CLICKHOUSE_HOST=${CLICKHOUSE_HOST:-localhost}
CLICKHOUSE_PORT=${CLICKHOUSE_PORT:-9000}
ALERTS=()

echo "=== ClickHouse Health Check ==="
echo "Time: $(date)"
echo "Host: $CLICKHOUSE_HOST:$CLICKHOUSE_PORT"
echo

# 1. Connectivity Check
if ! timeout 5 bash -c "echo '' | nc -w1 $CLICKHOUSE_HOST $CLICKHOUSE_PORT" 2>/dev/null; then
    ALERTS+=("❌ CRITICAL: Cannot connect to ClickHouse")
else
    echo "✓ ClickHouse server responding"
fi

# 2. Table Status Check
TABLE_COUNT=$(clickhouse-client --host $CLICKHOUSE_HOST --query "SELECT COUNT() FROM system.tables WHERE database NOT IN ('system', 'information_schema')")
echo "✓ Total tables: $TABLE_COUNT"

# 3. Disk Space Check
DISK_FREE=$(clickhouse-client --host $CLICKHOUSE_HOST --query "SELECT round(free_space / total_space * 100, 1) FROM system.disks LIMIT 1")
echo "✓ Free disk space: ${DISK_FREE}%"
if (( $(echo "$DISK_FREE < 20" | bc -l) )); then
    ALERTS+=("⚠️  WARNING: Free disk space < 20%")
fi

# 4. Memory Usage Check
MEMORY_GB=$(clickhouse-client --host $CLICKHOUSE_HOST --query "SELECT round(value / 1024 / 1024 / 1024, 1) FROM system.metrics WHERE metric = 'MemoryTracking'")
echo "✓ Memory usage: ${MEMORY_GB}GB"

# 5. Replication Lag Check (if replicated)
MAX_LAG=$(clickhouse-client --host $CLICKHOUSE_HOST --query "SELECT max(absolute_delay) FROM system.replicas" 2>/dev/null || echo "0")
if [ ! -z "$MAX_LAG" ] && (( $(echo "$MAX_LAG > 60" | bc -l) )); then
    ALERTS+=("⚠️  WARNING: Replication lag > 60 seconds")
fi

# 6. Error Rate Check
ERROR_RATE=$(clickhouse-client --host $CLICKHOUSE_HOST --query "SELECT round(SUM(if(exception != '', 1, 0)) * 100 / COUNT(), 2) FROM system.query_log WHERE event_date >= today()")
echo "✓ Error rate: ${ERROR_RATE}%"
if (( $(echo "$ERROR_RATE > 1" | bc -l) )); then
    ALERTS+=("⚠️  WARNING: Error rate > 1%")
fi

# 7. Query Performance Check
LATENCY_P95=$(clickhouse-client --host $CLICKHOUSE_HOST --query "SELECT round(quantile(0.95)(query_duration_ms)) FROM system.query_log WHERE event_date >= today() AND type = 'QueryFinish'")
echo "✓ Query latency p95: ${LATENCY_P95}ms"
if (( $(echo "$LATENCY_P95 > 5000" | bc -l) )); then
    ALERTS+=("⚠️  WARNING: Query latency p95 > 5 seconds")
fi

echo
if [ ${#ALERTS[@]} -eq 0 ]; then
    echo "✅ All checks passed"
    exit 0
else
    echo "⚠️  Issues detected:"
    printf '%s\n' "${ALERTS[@]}"
    exit 1
fi
```

---

## Monitoring Checklist

**Daily Checks:**
- [ ] Disk space > 20%
- [ ] Memory usage < 80%
- [ ] Error rate < 1%
- [ ] Replication lag < 60 seconds
- [ ] Query latency p95 < 5 seconds

**Weekly Checks:**
- [ ] Backup completed and verified
- [ ] No long-running queries queued
- [ ] Table fragmentation manageable (< 1000 parts/table)
- [ ] Insert throughput stable
- [ ] Cluster coordination stable

**Monthly Checks:**
- [ ] Disaster recovery test
- [ ] Capacity planning review
- [ ] Performance baseline comparison
- [ ] Log rotation working
- [ ] Team training on alerting procedures
