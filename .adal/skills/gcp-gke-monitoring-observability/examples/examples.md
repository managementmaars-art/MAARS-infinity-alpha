# GKE Monitoring and Observability Examples

## Example 1: Complete Observability Setup

```bash
#!/bin/bash
# Set up complete observability stack for Supplier Charges Hub

CLUSTER="shared-gke-labs-01-euw2"
REGION="europe-west2"
PROJECT="ecp-wtr-supplier-charges-labs"
NAMESPACE="wtr-supplier-charges"

echo "=== Setting Up GKE Observability ==="

# Step 1: Enable cluster-level monitoring
echo ""
echo "1. Enabling Cloud Logging and Monitoring..."
gcloud container clusters update $CLUSTER \
  --region=$REGION \
  --project=$PROJECT \
  --logging=SYSTEM,WORKLOAD \
  --monitoring=SYSTEM,WORKLOAD \
  --enable-managed-prometheus

# Step 2: Apply Spring Boot metrics configuration
echo ""
echo "2. Configuring Spring Boot Actuator..."
kubectl apply -f - <<EOF
apiVersion: v1
kind: ConfigMap
metadata:
  name: application-config
  namespace: $NAMESPACE
data:
  application.yml: |
    management:
      endpoints:
        web:
          exposure:
            include: health,info,metrics,prometheus
      endpoint:
        health:
          probes:
            enabled: true
      metrics:
        distribution:
          percentiles-histogram:
            http.server.requests: true
      health:
        livenessState:
          enabled: true
        readinessState:
          enabled: true
    logging:
      pattern:
        console: '{"timestamp":"%d{ISO8601}","level":"%p","message":"%m"}%n'
EOF

# Step 3: Update deployment with Prometheus annotations
echo ""
echo "3. Adding Prometheus scrape annotations..."
kubectl patch deployment supplier-charges-hub \
  -n $NAMESPACE \
  -p '{"spec":{"template":{"metadata":{"annotations":{"prometheus.io/scrape":"true","prometheus.io/port":"8080","prometheus.io/path":"/actuator/prometheus"}}}}}'

# Step 4: Create sample dashboard
echo ""
echo "4. Creating Cloud Monitoring dashboard..."
# (Dashboards created via Cloud Console or Cloud Monitoring API)

echo ""
echo "Observability setup complete!"
echo ""
echo "Next steps:"
echo "1. View logs: gcloud logging read \"resource.type=k8s_container AND resource.labels.namespace_name=$NAMESPACE\" --limit=50"
echo "2. Access Cloud Console: https://console.cloud.google.com/monitoring"
echo "3. Create dashboards in Cloud Monitoring"
```

## Example 2: Log Analysis and Error Tracking

```bash
#!/bin/bash
# Query logs for errors and build report

NAMESPACE="wtr-supplier-charges"
HOURS=24

echo "=== Log Analysis Report ==="
echo ""

echo "1. Total Log Entries (last $HOURS hours)"
gcloud logging read "resource.type=k8s_container AND resource.labels.namespace_name=$NAMESPACE AND timestamp>=\"$(date -u -d '24 hours ago' +%Y-%m-%dT%H:%M:%SZ)\"" \
  --format="value(severity)" | wc -l

echo ""
echo "2. Error Count (last $HOURS hours)"
gcloud logging read "resource.type=k8s_container AND resource.labels.namespace_name=$NAMESPACE AND severity=ERROR AND timestamp>=\"$(date -u -d '24 hours ago' +%Y-%m-%dT%H:%M:%SZ)\"" \
  --limit=100 \
  --format="value(severity)"

echo ""
echo "3. Top Error Messages"
gcloud logging read "resource.type=k8s_container AND resource.labels.namespace_name=$NAMESPACE AND severity=ERROR AND timestamp>=\"$(date -u -d '24 hours ago' +%Y-%m-%dT%H:%M:%SZ)\"" \
  --limit=50 \
  --format="value(textPayload)" | sort | uniq -c | sort -rn | head -10

echo ""
echo "4. Exception Traces"
gcloud logging read "resource.type=k8s_container AND resource.labels.namespace_name=$NAMESPACE AND textPayload=~\"Exception\" AND timestamp>=\"$(date -u -d '24 hours ago' +%Y-%m-%dT%H:%M:%SZ)\"" \
  --limit=20 \
  --format="json" | jq '.[] | {pod: .resource.labels.pod_name, timestamp: .timestamp, message: .textPayload[:200]}'
```

## Example 3: Health Check Endpoint Testing

```bash
#!/bin/bash
# Test and verify observability endpoints

POD=$(kubectl get pods -l app=supplier-charges-hub -n wtr-supplier-charges -o jsonpath='{.items[0].metadata.name}')
NAMESPACE="wtr-supplier-charges"

echo "=== Testing Observability Endpoints ==="

echo ""
echo "1. Health Status"
kubectl exec $POD -c supplier-charges-hub-container -n $NAMESPACE -- \
  curl -s http://localhost:8080/actuator/health | jq .

echo ""
echo "2. Application Metrics Available"
kubectl exec $POD -c supplier-charges-hub-container -n $NAMESPACE -- \
  curl -s http://localhost:8080/actuator/metrics | jq '.names | length'

echo ""
echo "3. HTTP Request Metrics"
kubectl exec $POD -c supplier-charges-hub-container -n $NAMESPACE -- \
  curl -s http://localhost:8080/actuator/metrics/http.server.requests | jq '.measurements[] | select(.statistic=="COUNT")'

echo ""
echo "4. JVM Memory Metrics"
kubectl exec $POD -c supplier-charges-hub-container -n $NAMESPACE -- \
  curl -s http://localhost:8080/actuator/metrics/jvm.memory.used | jq '.measurements[] | select(.statistic=="VALUE")'

echo ""
echo "5. Prometheus Metrics Format"
kubectl exec $POD -c supplier-charges-hub-container -n $NAMESPACE -- \
  curl -s http://localhost:8080/actuator/prometheus | head -20
```

## Example 4: Create Custom Metrics Dashboard

```bash
#!/bin/bash
# Create a Cloud Monitoring dashboard for Supplier Charges Hub

PROJECT="ecp-wtr-supplier-charges-labs"
DASHBOARD_NAME="supplier-charges-hub-dashboard"

cat > dashboard.json <<EOF
{
  "displayName": "Supplier Charges Hub Dashboard",
  "mosaicLayout": {
    "columns": 12,
    "tiles": [
      {
        "width": 6,
        "height": 4,
        "widget": {
          "title": "HTTP Requests Rate",
          "xyChart": {
            "dataSets": [
              {
                "timeSeriesQuery": {
                  "timeSeriesFilter": {
                    "filter": "metric.type=\"kubernetes.io/container/restart_count\" resource.type=\"k8s_container\" resource.label.namespace_name=\"wtr-supplier-charges\""
                  }
                }
              }
            ]
          }
        }
      },
      {
        "xPos": 6,
        "width": 6,
        "height": 4,
        "widget": {
          "title": "Error Rate",
          "xyChart": {
            "dataSets": [
              {
                "timeSeriesQuery": {
                  "timeSeriesFilter": {
                    "filter": "metric.type=\"logging.googleapis.com/user_defined_metric\" resource.type=\"k8s_container\" resource.label.namespace_name=\"wtr-supplier-charges\" metric.labels.severity=\"ERROR\""
                  }
                }
              }
            ]
          }
        }
      },
      {
        "yPos": 4,
        "width": 6,
        "height": 4,
        "widget": {
          "title": "Pod Memory Usage",
          "xyChart": {
            "dataSets": [
              {
                "timeSeriesQuery": {
                  "timeSeriesFilter": {
                    "filter": "metric.type=\"kubernetes.io/container/memory/used_bytes\" resource.type=\"k8s_container\" resource.label.namespace_name=\"wtr-supplier-charges\""
                  }
                }
              }
            ]
          }
        }
      },
      {
        "xPos": 6,
        "yPos": 4,
        "width": 6,
        "height": 4,
        "widget": {
          "title": "Pod CPU Usage",
          "xyChart": {
            "dataSets": [
              {
                "timeSeriesQuery": {
                  "timeSeriesFilter": {
                    "filter": "metric.type=\"kubernetes.io/container/cpu/core_usage_time\" resource.type=\"k8s_container\" resource.label.namespace_name=\"wtr-supplier-charges\""
                  }
                }
              }
            ]
          }
        }
      }
    ]
  }
}
EOF

# Create dashboard
gcloud monitoring dashboards create --config-from-file=dashboard.json \
  --project=$PROJECT

echo "Dashboard created: $DASHBOARD_NAME"
```
