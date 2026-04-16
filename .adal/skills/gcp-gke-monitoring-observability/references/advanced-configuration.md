# Advanced GKE Monitoring Configuration

## Complete Spring Boot Actuator Configuration

```yaml
# application.yml - Comprehensive configuration
management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics,prometheus,env,configprops,beans,mappings
      base-path: /actuator
  endpoint:
    health:
      probes:
        enabled: true
      show-details: always
      show-components: always
    metrics:
      enabled: true
    prometheus:
      enabled: true
  metrics:
    distribution:
      percentiles-histogram:
        http.server.requests: true
      slo:
        http.server.requests: 50ms,100ms,200ms,500ms
    tags:
      application: ${spring.application.name}
      environment: ${ENVIRONMENT:dev}
      region: ${GCP_REGION:europe-west2}
    export:
      prometheus:
        enabled: true
  health:
    livenessState:
      enabled: true
    readinessState:
      enabled: true
    defaults:
      enabled: true
  server:
    port: 8081  # Separate management port for isolation

logging:
  pattern:
    console: '{"timestamp":"%d{ISO8601}","level":"%p","logger":"%c{1}","thread":"%t","message":"%m","trace_id":"%X{trace_id}","span_id":"%X{span_id}"}%n'
  level:
    root: INFO
    com.company.project: DEBUG
    org.springframework: WARN
```

## Prometheus Scrape Configuration

### PodMonitor (Recommended for GKE Managed Prometheus)

```yaml
apiVersion: monitoring.coreos.com/v1
kind: PodMonitor
metadata:
  name: supplier-charges-hub-monitor
  namespace: wtr-supplier-charges
spec:
  selector:
    matchLabels:
      app: supplier-charges-hub
  podMetricsEndpoints:
  - port: metrics
    path: /actuator/prometheus
    interval: 30s
    scrapeTimeout: 10s
    scheme: http
    honorLabels: true
```

### ServiceMonitor (Alternative)

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: supplier-charges-hub-monitor
  namespace: wtr-supplier-charges
spec:
  selector:
    matchLabels:
      app: supplier-charges-hub
  endpoints:
  - port: metrics
    path: /actuator/prometheus
    interval: 30s
    metricRelabelings:
    - sourceLabels: [__name__]
      regex: 'http_server_requests_seconds_.*'
      action: keep
```

## Advanced Log Queries

### Structured Log Filtering

```bash
# Filter by JSON log level
gcloud logging read '
  resource.type="k8s_container"
  AND resource.labels.namespace_name="wtr-supplier-charges"
  AND jsonPayload.level="ERROR"
' --limit=50 --format=json

# Filter by trace ID
gcloud logging read '
  resource.type="k8s_container"
  AND resource.labels.namespace_name="wtr-supplier-charges"
  AND jsonPayload.trace_id="abc123"
' --limit=100

# Filter by custom fields
gcloud logging read '
  resource.type="k8s_container"
  AND resource.labels.namespace_name="wtr-supplier-charges"
  AND jsonPayload.order_id="12345"
' --limit=20
```

### Log Export to BigQuery

```bash
# Create log sink for long-term analysis
gcloud logging sinks create gke-logs-to-bigquery \
  bigquery.googleapis.com/projects/ecp-wtr-supplier-charges-prod/datasets/application_logs \
  --log-filter='
    resource.type="k8s_container"
    AND resource.labels.namespace_name="wtr-supplier-charges"
    AND severity>=WARNING
  '
```

## Dashboard Configuration

### Cloud Monitoring Dashboard JSON

```json
{
  "displayName": "Supplier Charges Hub - Production Dashboard",
  "gridLayout": {
    "widgets": [
      {
        "title": "Request Rate",
        "xyChart": {
          "dataSets": [{
            "timeSeriesQuery": {
              "timeSeriesFilter": {
                "filter": "metric.type=\"prometheus.googleapis.com/http_server_requests_seconds_count/counter\" AND resource.type=\"k8s_pod\" AND resource.labels.namespace_name=\"wtr-supplier-charges\"",
                "aggregation": {
                  "alignmentPeriod": "60s",
                  "perSeriesAligner": "ALIGN_RATE",
                  "crossSeriesReducer": "REDUCE_SUM"
                }
              }
            }
          }]
        }
      },
      {
        "title": "Error Rate",
        "xyChart": {
          "dataSets": [{
            "timeSeriesQuery": {
              "timeSeriesFilter": {
                "filter": "metric.type=\"prometheus.googleapis.com/http_server_requests_seconds_count/counter\" AND resource.type=\"k8s_pod\" AND resource.labels.namespace_name=\"wtr-supplier-charges\" AND metric.labels.status=~\"5..\"",
                "aggregation": {
                  "alignmentPeriod": "60s",
                  "perSeriesAligner": "ALIGN_RATE",
                  "crossSeriesReducer": "REDUCE_SUM"
                }
              }
            }
          }]
        }
      },
      {
        "title": "P95 Latency",
        "xyChart": {
          "dataSets": [{
            "timeSeriesQuery": {
              "timeSeriesFilter": {
                "filter": "metric.type=\"prometheus.googleapis.com/http_server_requests_seconds/histogram\" AND resource.type=\"k8s_pod\" AND resource.labels.namespace_name=\"wtr-supplier-charges\"",
                "aggregation": {
                  "alignmentPeriod": "60s",
                  "perSeriesAligner": "ALIGN_DELTA",
                  "crossSeriesReducer": "REDUCE_PERCENTILE_95"
                }
              }
            }
          }]
        }
      }
    ]
  }
}
```

## Alert Policy Configuration

### Comprehensive Alert Policies

```yaml
# alert-policies.yaml
---
# High Error Rate Alert
displayName: "Supplier Charges Hub - High Error Rate"
combiner: OR
conditions:
  - displayName: "5xx error rate > 5%"
    conditionThreshold:
      filter: |
        resource.type="k8s_container"
        AND resource.namespace_name="wtr-supplier-charges"
        AND metric.type="prometheus.googleapis.com/http_server_requests_seconds_count/counter"
        AND metric.labels.status=~"5.."
      comparison: COMPARISON_GT
      thresholdValue: 0.05
      duration: 300s
      aggregations:
        - alignmentPeriod: 60s
          perSeriesAligner: ALIGN_RATE
          crossSeriesReducer: REDUCE_SUM
notificationChannels:
  - projects/ecp-wtr-supplier-charges-prod/notificationChannels/email-ops
  - projects/ecp-wtr-supplier-charges-prod/notificationChannels/slack-alerts
alertStrategy:
  autoClose: 1800s
  notificationRateLimit:
    period: 300s

---
# High Memory Usage Alert
displayName: "Supplier Charges Hub - High Memory Usage"
conditions:
  - displayName: "Memory usage > 85%"
    conditionThreshold:
      filter: |
        resource.type="k8s_container"
        AND resource.namespace_name="wtr-supplier-charges"
        AND metric.type="kubernetes.io/container/memory/usage_bytes"
      comparison: COMPARISON_GT
      thresholdValue: 0.85
      duration: 600s
      aggregations:
        - alignmentPeriod: 60s
          perSeriesAligner: ALIGN_MEAN
      denominator_filter: |
        resource.type="k8s_container"
        AND resource.namespace_name="wtr-supplier-charges"
        AND metric.type="kubernetes.io/container/memory/limit_bytes"
notificationChannels:
  - projects/ecp-wtr-supplier-charges-prod/notificationChannels/email-ops
```

## Distributed Tracing Configuration

### Spring Cloud Sleuth with Cloud Trace

```gradle
// build.gradle.kts
dependencies {
    implementation("org.springframework.cloud:spring-cloud-starter-sleuth")
    implementation("com.google.cloud:spring-cloud-gcp-starter-trace")
}
```

```yaml
# application.yml
spring:
  cloud:
    gcp:
      trace:
        enabled: true
        project-id: ecp-wtr-supplier-charges-prod
        credentials:
          location: file:/var/secrets/google/key.json
  sleuth:
    sampler:
      probability: 0.1  # Sample 10% of requests
    baggage:
      remote-fields:
        - user-id
        - request-id
      correlation-fields:
        - user-id
        - request-id
```

### Trace Analysis Queries

```bash
# List recent traces
gcloud traces list \
  --project=ecp-wtr-supplier-charges-prod \
  --filter="spanName:process_order" \
  --limit=10

# Describe specific trace
gcloud traces describe TRACE_ID \
  --project=ecp-wtr-supplier-charges-prod

# Filter traces by latency
gcloud traces list \
  --project=ecp-wtr-supplier-charges-prod \
  --filter="latency>500ms" \
  --limit=20
```

## Custom Metrics

### Micrometer Custom Metrics

```java
@Component
public class OrderMetrics {
    private final MeterRegistry registry;
    private final Counter ordersProcessed;
    private final Timer orderProcessingTime;
    private final Gauge activeOrders;

    public OrderMetrics(MeterRegistry registry) {
        this.registry = registry;

        this.ordersProcessed = Counter.builder("orders.processed")
            .description("Total orders processed")
            .tags("application", "supplier-charges-hub")
            .register(registry);

        this.orderProcessingTime = Timer.builder("orders.processing.time")
            .description("Order processing time")
            .tags("application", "supplier-charges-hub")
            .register(registry);

        this.activeOrders = Gauge.builder("orders.active", this, OrderMetrics::getActiveOrderCount)
            .description("Currently active orders")
            .tags("application", "supplier-charges-hub")
            .register(registry);
    }

    public void recordOrderProcessed() {
        ordersProcessed.increment();
    }

    public void recordOrderProcessingTime(Duration duration) {
        orderProcessingTime.record(duration);
    }

    private double getActiveOrderCount() {
        // Implementation to count active orders
        return activeOrdersService.count();
    }
}
```

## Performance Optimization

### Metric Cardinality Control

```yaml
# Limit high-cardinality metrics
management:
  metrics:
    tags:
      # Use low-cardinality tags only
      application: ${spring.application.name}
      environment: ${ENVIRONMENT}
      # Avoid: customer_id, order_id (high cardinality)
    enable:
      # Disable unnecessary metrics
      jvm.gc.pause: false
      jvm.memory.committed: false
```

### Log Volume Reduction

```xml
<!-- logback-spring.xml -->
<configuration>
    <appender name="STDOUT" class="ch.qos.logback.core.ConsoleAppender">
        <filter class="ch.qos.logback.classic.filter.ThresholdFilter">
            <level>INFO</level>
        </filter>
        <encoder>
            <pattern>%msg%n</pattern>
        </encoder>
    </appender>

    <!-- Sample DEBUG logs (10%) -->
    <turboFilter class="ch.qos.logback.classic.turbo.MarkerFilter">
        <Marker>DEBUG</Marker>
        <OnMatch>NEUTRAL</OnMatch>
        <OnMismatch>ACCEPT</OnMismatch>
    </turboFilter>

    <root level="INFO">
        <appender-ref ref="STDOUT" />
    </root>
</configuration>
```
