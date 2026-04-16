# Rate Limiting Patterns Reference

This reference provides advanced rate limiting strategies and implementations.

## Algorithm Deep Dive

### Fixed Window

Simplest approach - count requests in fixed time windows.

```csharp
using StackExchange.Redis;

/// <summary>
/// Fixed window rate limiter.
/// </summary>
/// <remarks>
/// Pros:
/// - Simple to implement
/// - Memory efficient (one counter per window)
/// - Predictable limits
///
/// Cons:
/// - Burst at window boundaries
/// - Example: 100/min limit, user sends 100 at 0:59, 100 at 1:01
/// </remarks>
public sealed class FixedWindowLimiter(IConnectionMultiplexer redis, int limit, int window)
{
    private readonly IDatabase _db = redis.GetDatabase();

    /// <summary>
    /// Check if request is allowed. Returns (allowed, remaining).
    /// </summary>
    public async Task<(bool Allowed, int Remaining)> IsAllowedAsync(
        string key,
        CancellationToken ct = default)
    {
        var windowStart = DateTimeOffset.UtcNow.ToUnixTimeSeconds() / window;
        var bucketKey = $"ratelimit:fixed:{key}:{windowStart}";

        var current = await _db.StringIncrementAsync(bucketKey);
        if (current == 1)
            await _db.KeyExpireAsync(bucketKey, TimeSpan.FromSeconds(window));

        var allowed = current <= limit;
        var remaining = Math.Max(0, limit - (int)current);

        return (allowed, remaining);
    }
}
```

### Sliding Window Log

Track timestamps of each request for precise limiting.

```csharp
/// <summary>
/// Sliding window log rate limiter.
/// </summary>
/// <remarks>
/// Pros:
/// - Precise limiting
/// - No boundary issues
///
/// Cons:
/// - Higher memory usage (stores each timestamp)
/// - More Redis operations
/// </remarks>
public sealed class SlidingWindowLogLimiter(IConnectionMultiplexer redis, int limit, int window)
{
    private readonly IDatabase _db = redis.GetDatabase();

    /// <summary>
    /// Check if request is allowed using sliding window log.
    /// </summary>
    public async Task<(bool Allowed, int Remaining)> IsAllowedAsync(
        string key,
        CancellationToken ct = default)
    {
        var now = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds() / 1000.0;
        var windowStart = now - window;
        var bucketKey = $"ratelimit:sliding:{key}";

        var batch = _db.CreateBatch();

        // Remove old entries
        var removeTask = batch.SortedSetRemoveRangeByScoreAsync(bucketKey, 0, windowStart);
        // Count entries in window
        var countTask = batch.SortedSetLengthAsync(bucketKey);
        // Add current request
        var addTask = batch.SortedSetAddAsync(bucketKey, now.ToString(), now);
        var expireTask = batch.KeyExpireAsync(bucketKey, TimeSpan.FromSeconds(window));

        batch.Execute();
        await Task.WhenAll(removeTask, countTask, addTask, expireTask);

        var count = await countTask;
        var allowed = count < limit;
        var remaining = Math.Max(0, limit - (int)count - 1);

        return (allowed, remaining);
    }
}
```

### Sliding Window Counter

Hybrid approach - weighted count from current and previous windows.

```csharp
/// <summary>
/// Sliding window counter rate limiter (hybrid approach).
/// </summary>
/// <remarks>
/// Pros:
/// - Smooth limiting (no boundary bursts)
/// - Lower memory than sliding log
/// - More accurate than fixed window
///
/// Cons:
/// - Approximate (good enough for most cases)
/// </remarks>
public sealed class SlidingWindowCounterLimiter(IConnectionMultiplexer redis, int limit, int window)
{
    private readonly IDatabase _db = redis.GetDatabase();

    /// <summary>
    /// Check using weighted window counts.
    /// </summary>
    public async Task<(bool Allowed, int Remaining)> IsAllowedAsync(
        string key,
        CancellationToken ct = default)
    {
        var now = DateTimeOffset.UtcNow.ToUnixTimeSeconds();
        var currentWindow = now / window;
        var previousWindow = currentWindow - 1;

        // Position within current window (0 to 1)
        var windowPosition = (double)(now % window) / window;

        var currentKey = $"ratelimit:swc:{key}:{currentWindow}";
        var previousKey = $"ratelimit:swc:{key}:{previousWindow}";

        // Get counts
        var batch = _db.CreateBatch();
        var currentTask = batch.StringGetAsync(currentKey);
        var previousTask = batch.StringGetAsync(previousKey);
        batch.Execute();

        var currentCount = (int)(await currentTask).GetValueOrDefault();
        var previousCount = (int)(await previousTask).GetValueOrDefault();

        // Weighted count: full current + partial previous
        var weightedCount = currentCount + previousCount * (1 - windowPosition);
        var allowed = weightedCount < limit;

        if (allowed)
        {
            await _db.StringIncrementAsync(currentKey);
            await _db.KeyExpireAsync(currentKey, TimeSpan.FromSeconds(window * 2));
        }

        var remaining = Math.Max(0, (int)(limit - weightedCount - 1));
        return (allowed, remaining);
    }
}
```

### Token Bucket

Allows bursts while maintaining long-term rate.

```csharp
/// <summary>
/// Token bucket rate limiter.
/// </summary>
/// <remarks>
/// Example: 10 tokens/sec, 50 capacity
/// - Allows burst of 50 requests
/// - Sustained rate of 10/sec
/// - Recovers 1 token every 100ms
/// </remarks>
public sealed class TokenBucketLimiter(IConnectionMultiplexer redis, double rate, int capacity)
{
    private readonly IDatabase _db = redis.GetDatabase();

    private const string LuaScript = """
        local key = KEYS[1]
        local rate = tonumber(ARGV[1])
        local capacity = tonumber(ARGV[2])
        local now = tonumber(ARGV[3])
        local requested = tonumber(ARGV[4])

        local data = redis.call('HMGET', key, 'tokens', 'timestamp')
        local tokens = tonumber(data[1]) or capacity
        local timestamp = tonumber(data[2]) or now

        -- Replenish tokens
        local elapsed = math.max(0, now - timestamp)
        tokens = math.min(capacity, tokens + (elapsed * rate))

        local allowed = 0
        local wait_time = 0

        if tokens >= requested then
            tokens = tokens - requested
            allowed = 1
        else
            -- Calculate wait time for requested tokens
            wait_time = (requested - tokens) / rate
        end

        redis.call('HMSET', key, 'tokens', tokens, 'timestamp', now)
        redis.call('EXPIRE', key, math.ceil(capacity / rate) + 1)

        return {allowed, math.floor(tokens), wait_time}
        """;

    /// <summary>
    /// Check if request is allowed and consume tokens.
    /// </summary>
    /// <returns>(allowed, remaining_tokens, wait_time_if_denied)</returns>
    public async Task<(bool Allowed, int Remaining, double WaitTime)> IsAllowedAsync(
        string key,
        int tokens = 1,
        CancellationToken ct = default)
    {
        var now = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds() / 1000.0;
        var result = (RedisResult[]?)await _db.ScriptEvaluateAsync(
            LuaScript,
            keys: [$"ratelimit:tb:{key}"],
            values: [rate, capacity, now, tokens]);

        if (result is null || result.Length < 3)
            return (false, 0, 60);

        return (
            (int)result[0] == 1,
            (int)result[1],
            (double)result[2]);
    }
}
```

### Leaky Bucket

Processes requests at a constant rate.

```csharp
using System.Collections.Concurrent;

/// <summary>
/// Leaky bucket rate limiter with queue.
/// </summary>
/// <remarks>
/// Pros:
/// - Smooths traffic perfectly
/// - Predictable processing rate
///
/// Cons:
/// - Adds latency (requests wait in queue)
/// - More complex implementation
/// </remarks>
public sealed class LeakyBucketLimiter
{
    private readonly double _rate;  // Requests processed per second
    private readonly int _capacity;  // Queue size
    private readonly ConcurrentQueue<(string RequestId, double Timestamp)> _queue = new();
    private double _lastLeak;
    private readonly Lock _lock = new();

    public LeakyBucketLimiter(double rate, int capacity)
    {
        _rate = rate;
        _capacity = capacity;
        _lastLeak = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds() / 1000.0;
    }

    /// <summary>
    /// Add request to bucket.
    /// </summary>
    /// <returns>(accepted, queue_position)</returns>
    public (bool Accepted, int QueuePosition) AddRequest(string requestId)
    {
        lock (_lock)
        {
            Leak();

            if (_queue.Count < _capacity)
            {
                var now = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds() / 1000.0;
                _queue.Enqueue((requestId, now));
                return (true, _queue.Count);
            }

            return (false, -1);
        }
    }

    /// <summary>
    /// Process requests (drain the bucket).
    /// </summary>
    private void Leak()
    {
        var now = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds() / 1000.0;
        var elapsed = now - _lastLeak;
        var toLeak = (int)(elapsed * _rate);

        for (var i = 0; i < Math.Min(toLeak, _queue.Count); i++)
            _queue.TryDequeue(out _);

        if (toLeak > 0)
            _lastLeak = now;
    }
}
```

## Multi-Tier Rate Limiting

### Different Limits for Different Tiers

```csharp
/// <summary>
/// Rate limiting tier levels.
/// </summary>
public enum Tier { Free, Basic, Premium, Enterprise }

/// <summary>
/// Rate limit configuration per tier.
/// </summary>
public sealed record RateLimitConfig(
    int RequestsPerSecond,
    int RequestsPerMinute,
    int RequestsPerHour,
    int BurstSize);

/// <summary>
/// Rate limiter with tier-based limits.
/// </summary>
public sealed class MultiTierLimiter(IConnectionMultiplexer redis)
{
    private static readonly FrozenDictionary<Tier, RateLimitConfig> TierLimits =
        new Dictionary<Tier, RateLimitConfig>
        {
            [Tier.Free] = new(1, 30, 500, 5),
            [Tier.Basic] = new(10, 300, 5000, 20),
            [Tier.Premium] = new(50, 1500, 25000, 100),
            [Tier.Enterprise] = new(200, 6000, 100000, 500),
        }.ToFrozenDictionary();

    /// <summary>
    /// Check all rate limits for a tier.
    /// </summary>
    public async Task<(bool Allowed, Dictionary<string, WindowResult> Results)> CheckAsync(
        string key,
        Tier tier,
        CancellationToken ct = default)
    {
        var config = TierLimits[tier];
        var results = new Dictionary<string, WindowResult>();

        // Check each time window
        var checks = new (string Name, int Limit, int WindowSize)[]
        {
            ("second", config.RequestsPerSecond, 1),
            ("minute", config.RequestsPerMinute, 60),
            ("hour", config.RequestsPerHour, 3600),
        };

        var allAllowed = true;
        foreach (var (windowName, limit, windowSize) in checks)
        {
            var limiter = new TokenBucketLimiter(
                redis,
                rate: (double)limit / windowSize,
                capacity: Math.Min(config.BurstSize, limit));

            var (allowed, remaining, waitTime) = await limiter.IsAllowedAsync($"{key}:{windowName}", ct: ct);
            results[windowName] = new WindowResult(allowed, remaining, waitTime);

            if (!allowed)
                allAllowed = false;
        }

        return (allAllowed, results);
    }
}

public sealed record WindowResult(bool Allowed, int Remaining, double WaitTime);
```

### Endpoint-Specific Limits

```csharp
using Microsoft.AspNetCore.Mvc.Filters;

/// <summary>
/// Endpoint-specific rate limit configuration.
/// </summary>
public sealed record EndpointLimit(int Limit, int Window);

/// <summary>
/// Rate limit filter attribute with endpoint-specific limits.
/// </summary>
[AttributeUsage(AttributeTargets.Method | AttributeTargets.Class)]
public sealed class RateLimitAttribute : Attribute, IAsyncActionFilter
{
    private static readonly FrozenDictionary<string, EndpointLimit> EndpointLimits =
        new Dictionary<string, EndpointLimit>
        {
            ["/api/search"] = new(30, 60),
            ["/api/export"] = new(5, 60),
            ["/api/upload"] = new(10, 60),
            ["default"] = new(100, 60),
        }.ToFrozenDictionary();

    public int? CustomLimit { get; init; }
    public int? CustomWindow { get; init; }

    public async Task OnActionExecutionAsync(
        ActionExecutingContext context,
        ActionExecutionDelegate next)
    {
        var httpContext = context.HttpContext;
        var endpoint = httpContext.Request.Path.Value ?? "default";
        var config = EndpointLimits.GetValueOrDefault(endpoint, EndpointLimits["default"]);

        var limit = CustomLimit ?? config.Limit;
        var window = CustomWindow ?? config.Window;

        var identifier = GetIdentifier(httpContext);
        var key = $"{identifier}:{endpoint}";

        var redis = httpContext.RequestServices.GetRequiredService<IConnectionMultiplexer>();
        var limiter = new SlidingWindowCounterLimiter(redis, limit, window);
        var (allowed, remaining) = await limiter.IsAllowedAsync(key);

        if (!allowed)
        {
            httpContext.Response.StatusCode = StatusCodes.Status429TooManyRequests;
            httpContext.Response.Headers["Retry-After"] = window.ToString();
            await httpContext.Response.WriteAsJsonAsync(new
            {
                error = "Rate limit exceeded",
                endpoint,
                retry_after = window
            });
            return;
        }

        httpContext.Response.Headers["X-RateLimit-Limit"] = limit.ToString();
        httpContext.Response.Headers["X-RateLimit-Remaining"] = remaining.ToString();

        await next();
    }

    private static string GetIdentifier(HttpContext context)
        => context.Request.Headers["X-API-Key"].FirstOrDefault()
           ?? context.Connection.RemoteIpAddress?.ToString()
           ?? "unknown";
}

// Usage in controller
[ApiController]
[Route("api")]
public sealed class SearchController : ControllerBase
{
    [HttpGet("search")]
    [RateLimit]  // Uses endpoint-specific limits
    public IActionResult Search() => Ok();

    [HttpPost("heavy-operation")]
    [RateLimit(CustomLimit = 3, CustomWindow = 300)]  // Override: 3 per 5 minutes
    public IActionResult HeavyOperation() => Ok();
}
```

## Distributed Rate Limiting

### Redis Cluster Support

```csharp
/// <summary>
/// Rate limiter for distributed systems with Redis Cluster.
/// </summary>
public sealed class DistributedRateLimiter(IConnectionMultiplexer redis)
{
    private readonly IDatabase _db = redis.GetDatabase();

    private const string LuaScript = """
        local key = KEYS[1]
        local limit = tonumber(ARGV[1])
        local window = tonumber(ARGV[2])
        local now = tonumber(ARGV[3])

        local window_start = math.floor(now / window) * window
        local bucket_key = key .. ':' .. window_start

        local current = redis.call('INCR', bucket_key)
        if current == 1 then
            redis.call('EXPIRE', bucket_key, window * 2)
        end

        local allowed = current <= limit and 1 or 0
        local remaining = math.max(0, limit - current)

        return {allowed, remaining}
        """;

    /// <summary>
    /// Atomic rate limit check across cluster.
    /// Uses hash tags to ensure key locality.
    /// </summary>
    public async Task<(bool Allowed, int Remaining)> IsAllowedAsync(
        string key,
        int limit,
        int window,
        CancellationToken ct = default)
    {
        // Use hash tags for key locality: {user123}:ratelimit
        var taggedKey = $"{{{key}}}:ratelimit";
        var now = DateTimeOffset.UtcNow.ToUnixTimeSeconds();

        var result = (RedisResult[]?)await _db.ScriptEvaluateAsync(
            LuaScript,
            keys: [taggedKey],
            values: [limit, window, now]);

        if (result is null || result.Length < 2)
            return (false, 0);

        return ((int)result[0] == 1, (int)result[1]);
    }
}
```

### Handling Redis Failures

```csharp
using System.Collections.Concurrent;
using Microsoft.Extensions.Logging;

public enum FallbackPolicy { Allow, Deny }

/// <summary>
/// Rate limiter with fallback on Redis failure.
/// </summary>
public sealed class ResilientRateLimiter(
    IConnectionMultiplexer redis,
    ILogger<ResilientRateLimiter> logger,
    FallbackPolicy fallbackPolicy = FallbackPolicy.Allow)
{
    private readonly IDatabase _db = redis.GetDatabase();
    private readonly ConcurrentDictionary<string, int> _localCache = new();

    /// <summary>
    /// Check rate limit with fallback.
    /// </summary>
    public async Task<(bool Allowed, int Remaining)> IsAllowedAsync(
        string key,
        int limit,
        int window,
        CancellationToken ct = default)
    {
        try
        {
            return await RedisCheckAsync(key, limit, window);
        }
        catch (RedisException ex)
        {
            logger.LogWarning(ex, "Redis error, using fallback for key {Key}", key);
            return FallbackCheck(key, limit, window);
        }
    }

    private async Task<(bool Allowed, int Remaining)> RedisCheckAsync(
        string key, int limit, int window)
    {
        var windowStart = DateTimeOffset.UtcNow.ToUnixTimeSeconds() / window;
        var bucketKey = $"ratelimit:{key}:{windowStart}";

        var current = await _db.StringIncrementAsync(bucketKey);
        if (current == 1)
            await _db.KeyExpireAsync(bucketKey, TimeSpan.FromSeconds(window));

        var allowed = current <= limit;
        var remaining = Math.Max(0, limit - (int)current);
        return (allowed, remaining);
    }

    private (bool Allowed, int Remaining) FallbackCheck(string key, int limit, int window)
    {
        if (fallbackPolicy == FallbackPolicy.Deny)
            return (false, 0);  // Fail closed: deny all requests

        // Fail open with local tracking
        var now = DateTimeOffset.UtcNow.ToUnixTimeSeconds();
        var windowKey = $"{key}:{now / window}";

        // Clean old entries periodically
        CleanupLocalCache(window);

        var count = _localCache.AddOrUpdate(windowKey, 1, (_, c) => c + 1);

        // Apply stricter local limit (conservative)
        var localLimit = limit / 2;
        var allowed = count <= localLimit;
        var remaining = Math.Max(0, localLimit - count);

        return (allowed, remaining);
    }

    private void CleanupLocalCache(int window)
    {
        var now = DateTimeOffset.UtcNow.ToUnixTimeSeconds();
        var cutoff = now / window - 2;

        foreach (var key in _localCache.Keys)
        {
            if (long.TryParse(key.Split(':')[^1], out var keyWindow) && keyWindow < cutoff)
                _localCache.TryRemove(key, out _);
        }
    }
}
```

## Response Headers

### Standard Rate Limit Headers

```csharp
/// <summary>
/// Rate limit information stored in HttpContext.Items.
/// </summary>
public sealed record RateLimitInfo(
    int Limit,
    int Remaining,
    long ResetTimestamp,
    bool Allowed,
    int RetryAfter = 0);

/// <summary>
/// Middleware that adds standard rate limit headers to responses.
/// </summary>
public sealed class RateLimitHeadersMiddleware(RequestDelegate next)
{
    private const string RateLimitInfoKey = "RateLimitInfo";

    public async Task InvokeAsync(HttpContext context)
    {
        context.Response.OnStarting(() =>
        {
            if (context.Items.TryGetValue(RateLimitInfoKey, out var infoObj)
                && infoObj is RateLimitInfo info)
            {
                var headers = context.Response.Headers;
                var now = DateTimeOffset.UtcNow.ToUnixTimeSeconds();

                // Standard X-RateLimit headers
                headers["X-RateLimit-Limit"] = info.Limit.ToString();
                headers["X-RateLimit-Remaining"] = info.Remaining.ToString();
                headers["X-RateLimit-Reset"] = info.ResetTimestamp.ToString();

                // Draft IETF standard headers (RFC 7231)
                headers["RateLimit-Limit"] = info.Limit.ToString();
                headers["RateLimit-Remaining"] = info.Remaining.ToString();
                headers["RateLimit-Reset"] = (info.ResetTimestamp - now).ToString();

                if (!info.Allowed)
                    headers["Retry-After"] = info.RetryAfter.ToString();
            }

            return Task.CompletedTask;
        });

        await next(context);
    }

    /// <summary>
    /// Helper to set rate limit info for header middleware.
    /// </summary>
    public static void SetRateLimitInfo(HttpContext context, RateLimitInfo info)
        => context.Items[RateLimitInfoKey] = info;
}
```

### Multiple Limit Headers

```csharp
/// <summary>
/// Individual rate limit info for multi-limit scenarios.
/// </summary>
public sealed record LimitInfo(int Limit, int Remaining, long Reset, int Window);

/// <summary>
/// Formats multiple rate limits into IETF draft RateLimit headers.
/// </summary>
public static class RateLimitHeaderFormatter
{
    /// <summary>
    /// Format multiple rate limits into headers.
    /// </summary>
    /// <remarks>
    /// Example output:
    /// RateLimit-Limit: 10
    /// RateLimit-Remaining: 5
    /// RateLimit-Reset: 30
    /// RateLimit-Policy: 100;w=60;name="per-minute", 1000;w=3600;name="per-hour"
    /// </remarks>
    public static Dictionary<string, string> FormatHeaders(
        IReadOnlyDictionary<string, LimitInfo> limits)
    {
        var headers = new Dictionary<string, string>();

        // Combined limit (most restrictive)
        var minRemaining = limits.Values.Min(l => l.Remaining);
        var minReset = limits.Values.Min(l => l.Reset);
        var minLimit = limits.Values.Min(l => l.Limit);

        headers["RateLimit-Limit"] = minLimit.ToString();
        headers["RateLimit-Remaining"] = minRemaining.ToString();
        headers["RateLimit-Reset"] = minReset.ToString();

        // Detailed breakdown
        var policyParts = limits.Select(kv =>
            $"{kv.Value.Limit};w={kv.Value.Window};name=\"{kv.Key}\"");
        headers["RateLimit-Policy"] = string.Join(", ", policyParts);

        return headers;
    }
}
```

## Monitoring and Alerting

### Metrics to Track

```csharp
using System.Diagnostics.Metrics;

/// <summary>
/// Rate limiting metrics using .NET Meters (OpenTelemetry compatible).
/// </summary>
public sealed class RateLimitMetrics : IDisposable
{
    private readonly Meter _meter;
    private readonly Counter<long> _requestsTotal;
    private readonly Histogram<double> _remainingRatio;
    private readonly ObservableGauge<double> _utilization;
    private readonly ConcurrentDictionary<string, double> _utilizationValues = new();

    public RateLimitMetrics(IMeterFactory meterFactory)
    {
        _meter = meterFactory.Create("RateLimiting");

        // Counter: Total rate limit checks
        _requestsTotal = _meter.CreateCounter<long>(
            "rate_limit_requests_total",
            description: "Total rate limit checks");

        // Histogram: Ratio of remaining quota when checked
        _remainingRatio = _meter.CreateHistogram<double>(
            "rate_limit_remaining_ratio",
            description: "Ratio of remaining quota when checked");

        // Gauge: Current rate limit utilization
        _utilization = _meter.CreateObservableGauge(
            "rate_limit_utilization_percent",
            () => _utilizationValues.Select(kv =>
                new Measurement<double>(kv.Value, new KeyValuePair<string, object?>("key", kv.Key))),
            description: "Current rate limit utilization");
    }

    /// <summary>
    /// Record rate limit check metrics.
    /// </summary>
    public void RecordCheck(string endpoint, string tier, bool allowed, int remaining, int limit)
    {
        var result = allowed ? "allowed" : "denied";
        var tags = new TagList
        {
            { "endpoint", endpoint },
            { "tier", tier },
            { "result", result }
        };

        _requestsTotal.Add(1, tags);

        var ratio = limit > 0 ? (double)remaining / limit : 0;
        _remainingRatio.Record(ratio, new TagList { { "endpoint", endpoint }, { "tier", tier } });
    }

    /// <summary>
    /// Update utilization gauge for a client.
    /// </summary>
    public void UpdateUtilization(string clientId, string tier, double percent)
        => _utilizationValues[$"{clientId}:{tier}"] = percent;

    public void Dispose() => _meter.Dispose();
}
```

### Alerting Rules

```yaml
# Prometheus alerting rules
groups:
  - name: rate_limiting
    rules:
      - alert: HighRateLimitDenials
        expr: |
          rate(rate_limit_requests_total{result="denied"}[5m])
          / rate(rate_limit_requests_total[5m]) > 0.1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High rate of rate limit denials"
          description: "More than 10% of requests denied due to rate limiting"

      - alert: ClientApproachingLimit
        expr: |
          rate_limit_utilization_percent > 80
        for: 10m
        labels:
          severity: info
        annotations:
          summary: "Client approaching rate limit"
          description: "Client {{ $labels.client_id }} at {{ $value }}% of limit"
```

## Security Considerations

### Preventing Bypass

```csharp
using System.Net;
using System.Security.Cryptography;

/// <summary>
/// Reliable client identifier extraction for rate limiting.
/// </summary>
public sealed class ClientIdentifierResolver(IConfiguration config)
{
    private static readonly string[] TrustedProxyRanges =
    [
        "10.0.0.0/8",      // Internal
        "172.16.0.0/12",   // Internal
        "192.168.0.0/16",  // Internal
        // Add your CDN/proxy ranges from config
    ];

    /// <summary>
    /// Get reliable client identifier for rate limiting.
    /// Order of preference: API key > User ID > Forwarded IP > Direct IP
    /// </summary>
    public string GetIdentifier(HttpContext context)
    {
        // Prefer authenticated identifiers
        var apiKey = context.Request.Headers["X-API-Key"].FirstOrDefault();
        if (!string.IsNullOrEmpty(apiKey))
            return $"apikey:{HashKey(apiKey)}";

        var userId = context.User.FindFirst("sub")?.Value;
        if (!string.IsNullOrEmpty(userId))
            return $"user:{userId}";

        // IP-based (less reliable)
        var remoteIp = context.Connection.RemoteIpAddress;
        if (remoteIp is null)
            return "ip:unknown";

        // Trust X-Forwarded-For only from known proxies
        if (IsTrustedProxy(remoteIp))
        {
            var forwarded = context.Request.Headers["X-Forwarded-For"]
                .FirstOrDefault()?.Split(',')[0].Trim();

            if (IPAddress.TryParse(forwarded, out var forwardedIp))
                return $"ip:{forwardedIp}";
        }

        return $"ip:{remoteIp}";
    }

    private static string HashKey(string apiKey)
    {
        var hash = SHA256.HashData(Encoding.UTF8.GetBytes(apiKey));
        return Convert.ToHexString(hash)[..16];  // First 16 chars
    }

    private static bool IsTrustedProxy(IPAddress ip)
    {
        foreach (var range in TrustedProxyRanges)
        {
            var parts = range.Split('/');
            if (parts.Length != 2) continue;

            if (IPAddress.TryParse(parts[0], out var networkIp) &&
                int.TryParse(parts[1], out var prefixLength))
            {
                if (IsInRange(ip, networkIp, prefixLength))
                    return true;
            }
        }
        return false;
    }

    private static bool IsInRange(IPAddress ip, IPAddress network, int prefixLength)
    {
        var ipBytes = ip.GetAddressBytes();
        var networkBytes = network.GetAddressBytes();

        if (ipBytes.Length != networkBytes.Length)
            return false;

        var maskBytes = prefixLength / 8;
        var maskBits = prefixLength % 8;

        for (var i = 0; i < maskBytes; i++)
        {
            if (ipBytes[i] != networkBytes[i])
                return false;
        }

        if (maskBits > 0 && maskBytes < ipBytes.Length)
        {
            var mask = (byte)(0xFF << (8 - maskBits));
            if ((ipBytes[maskBytes] & mask) != (networkBytes[maskBytes] & mask))
                return false;
        }

        return true;
    }
}
```

### Rate Limit Security Checklist

- [ ] Don't rely solely on IP addresses (easily spoofed, NAT issues)
- [ ] Apply rate limits before expensive operations
- [ ] Use atomic operations (Redis Lua scripts)
- [ ] Handle Redis failures gracefully
- [ ] Monitor for rate limit bypass attempts
- [ ] Different limits for authenticated vs anonymous
- [ ] Consider geographic distribution (CDN edge limiting)
- [ ] Protect against enumeration via timing
