---
title: Monitor API and Content Performance
impact: MEDIUM
impactDescription: ensures optimal content delivery and identifies issues
tags: monitoring, performance, metrics, observability, cdn
---

## Monitor API and Content Performance

**Impact: MEDIUM (ensures optimal content delivery and identifies issues)**

Monitor Storyblok API response times, CDN cache hit rates, and content delivery performance. Set up alerts for degradation and track Core Web Vitals impact.

**Incorrect (no monitoring):**

```javascript
// Bad: No visibility into API performance
const fetchStory = async (slug) => {
  const { data } = await storyblokApi.get(`cdn/stories/${slug}`);
  return data.story;
  // No timing, no error tracking, no cache visibility
};

// Bad: Silent failures
const getContent = async () => {
  try {
    return await fetchStory('home');
  } catch (error) {
    return null; // Error swallowed, no alerting
  }
};
```

**Correct (comprehensive monitoring):**

```javascript
// Good: Instrumented API wrapper
// lib/storyblok-instrumented.js
import { getStoryblokApi } from '@storyblok/react';

const metrics = {
  apiCalls: 0,
  cacheHits: 0,
  cacheMisses: 0,
  errors: 0,
  totalLatency: 0
};

export const instrumentedGet = async (path, params = {}) => {
  const startTime = performance.now();
  const api = getStoryblokApi();

  try {
    const response = await api.get(path, params);
    const latency = performance.now() - startTime;

    // Track metrics
    metrics.apiCalls++;
    metrics.totalLatency += latency;

    // Check cache header
    const cacheStatus = response.headers?.['x-cache'] || 'unknown';
    if (cacheStatus.includes('HIT')) {
      metrics.cacheHits++;
    } else {
      metrics.cacheMisses++;
    }

    // Log for monitoring
    logApiCall({
      path,
      latency,
      cacheStatus,
      status: 'success'
    });

    return response;

  } catch (error) {
    const latency = performance.now() - startTime;
    metrics.errors++;

    logApiCall({
      path,
      latency,
      status: 'error',
      error: error.message
    });

    throw error;
  }
};

const logApiCall = (data) => {
  // Send to your monitoring service
  if (process.env.NODE_ENV === 'production') {
    // DataDog, New Relic, etc.
    sendToMonitoring('storyblok.api', data);
  } else {
    console.log('[Storyblok API]', data);
  }
};

export const getMetrics = () => ({
  ...metrics,
  averageLatency: metrics.apiCalls > 0
    ? metrics.totalLatency / metrics.apiCalls
    : 0,
  cacheHitRate: metrics.apiCalls > 0
    ? (metrics.cacheHits / metrics.apiCalls) * 100
    : 0
});
```

```javascript
// Good: Rate limit monitoring
// lib/rate-limit-monitor.js
const rateLimitState = {
  remaining: null,
  limit: null,
  resetTime: null,
  warnings: []
};

export const trackRateLimits = (headers) => {
  rateLimitState.remaining = parseInt(headers['x-ratelimit-remaining']) || null;
  rateLimitState.limit = parseInt(headers['x-ratelimit-limit']) || null;
  rateLimitState.resetTime = parseInt(headers['x-ratelimit-reset']) || null;

  // Warn when approaching limit
  if (rateLimitState.remaining !== null && rateLimitState.remaining < 10) {
    const warning = {
      message: `Rate limit warning: ${rateLimitState.remaining} requests remaining`,
      timestamp: Date.now(),
      resetIn: rateLimitState.resetTime
        ? rateLimitState.resetTime - Math.floor(Date.now() / 1000)
        : null
    };

    rateLimitState.warnings.push(warning);
    alertRateLimitWarning(warning);
  }
};

const alertRateLimitWarning = (warning) => {
  console.warn('[Storyblok Rate Limit]', warning);

  // Send alert to Slack, PagerDuty, etc.
  if (process.env.NODE_ENV === 'production') {
    sendAlert('storyblok-rate-limit', warning);
  }
};
```

```javascript
// Good: Core Web Vitals tracking for Storyblok pages
// lib/web-vitals.js
import { onCLS, onFID, onLCP, onFCP, onTTFB } from 'web-vitals';

const trackWebVitals = (metric) => {
  const data = {
    name: metric.name,
    value: metric.value,
    rating: metric.rating,
    delta: metric.delta,
    id: metric.id,
    page: window.location.pathname,
    // Track if page is Storyblok-driven
    isStoryblokPage: document.querySelector('[data-blok-uid]') !== null
  };

  // Send to analytics
  sendToAnalytics('web-vitals', data);

  // Alert on poor performance
  if (metric.rating === 'poor') {
    sendAlert('web-vitals-poor', {
      metric: metric.name,
      value: metric.value,
      page: window.location.pathname
    });
  }
};

export const initWebVitals = () => {
  onCLS(trackWebVitals);
  onFID(trackWebVitals);
  onLCP(trackWebVitals);
  onFCP(trackWebVitals);
  onTTFB(trackWebVitals);
};
```

```javascript
// Good: API health check endpoint
// app/api/health/storyblok/route.js
export async function GET() {
  const startTime = Date.now();
  const checks = {
    api: { status: 'unknown', latency: null },
    cdn: { status: 'unknown', cacheVersion: null }
  };

  try {
    // Check CDN API
    const cdnStart = Date.now();
    const { data: space } = await storyblokApi.get('cdn/spaces/me');
    checks.cdn = {
      status: 'healthy',
      latency: Date.now() - cdnStart,
      cacheVersion: space.version
    };
  } catch (error) {
    checks.cdn = { status: 'unhealthy', error: error.message };
  }

  const totalLatency = Date.now() - startTime;
  const isHealthy = Object.values(checks).every(c => c.status === 'healthy');

  return Response.json({
    status: isHealthy ? 'healthy' : 'degraded',
    timestamp: new Date().toISOString(),
    latency: totalLatency,
    checks
  }, {
    status: isHealthy ? 200 : 503
  });
}
```

```javascript
// Good: Dashboard metrics collector
// lib/metrics-collector.js
import { collectDefaultMetrics, register, Gauge, Counter, Histogram } from 'prom-client';

// Prometheus metrics
const storyblokApiLatency = new Histogram({
  name: 'storyblok_api_latency_seconds',
  help: 'Storyblok API request latency',
  labelNames: ['endpoint', 'status'],
  buckets: [0.1, 0.5, 1, 2, 5]
});

const storyblokCacheHits = new Counter({
  name: 'storyblok_cache_hits_total',
  help: 'Storyblok CDN cache hits',
  labelNames: ['endpoint']
});

const storyblokCacheMisses = new Counter({
  name: 'storyblok_cache_misses_total',
  help: 'Storyblok CDN cache misses',
  labelNames: ['endpoint']
});

const storyblokErrors = new Counter({
  name: 'storyblok_errors_total',
  help: 'Storyblok API errors',
  labelNames: ['endpoint', 'error_type']
});

export const recordApiCall = (endpoint, latency, cacheHit, error = null) => {
  storyblokApiLatency.observe(
    { endpoint, status: error ? 'error' : 'success' },
    latency / 1000
  );

  if (cacheHit) {
    storyblokCacheHits.inc({ endpoint });
  } else {
    storyblokCacheMisses.inc({ endpoint });
  }

  if (error) {
    storyblokErrors.inc({ endpoint, error_type: error.type || 'unknown' });
  }
};

// Metrics endpoint
// app/api/metrics/route.js
export async function GET() {
  const metrics = await register.metrics();
  return new Response(metrics, {
    headers: { 'Content-Type': register.contentType }
  });
}
```

```yaml
# Good: Grafana dashboard queries
# Storyblok API Latency (95th percentile)
histogram_quantile(0.95, sum(rate(storyblok_api_latency_seconds_bucket[5m])) by (le, endpoint))

# Cache Hit Rate
sum(rate(storyblok_cache_hits_total[5m])) /
(sum(rate(storyblok_cache_hits_total[5m])) + sum(rate(storyblok_cache_misses_total[5m]))) * 100

# Error Rate
sum(rate(storyblok_errors_total[5m])) by (error_type)
```

**Key metrics to track:**

| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| API Latency (p95) | < 200ms | > 500ms |
| Cache Hit Rate | > 90% | < 70% |
| Error Rate | < 0.1% | > 1% |
| LCP (Storyblok pages) | < 2.5s | > 4s |
| Rate Limit Remaining | > 50 | < 10 |

**Alerting checklist:**

- [ ] API latency spikes
- [ ] Cache hit rate drops
- [ ] Error rate increases
- [ ] Rate limit warnings
- [ ] Webhook delivery failures
- [ ] Core Web Vitals degradation

Reference: [Performance Best Practices](https://www.storyblok.com/docs/guide/in-depth/performance)
