# API Security Headers Reference

This reference provides comprehensive guidance on security headers for APIs.

## Essential Security Headers

### Complete Header Configuration

```csharp
using System.Collections.Frozen;
using Microsoft.AspNetCore.Http;

/// <summary>
/// Middleware that adds comprehensive security headers to all responses.
/// </summary>
public sealed class SecurityHeadersMiddleware(
    RequestDelegate next,
    ISensitiveEndpointDetector sensitiveEndpointDetector)
{
    private static readonly FrozenSet<string> SensitivePathPrefixes =
        new HashSet<string>(StringComparer.OrdinalIgnoreCase)
        {
            "/api/users/me",
            "/api/auth",
            "/api/account",
            "/api/admin",
        }.ToFrozenSet();

    public async Task InvokeAsync(HttpContext context)
    {
        context.Response.OnStarting(() =>
        {
            var headers = context.Response.Headers;

            // === Content Security ===

            // Prevent MIME type sniffing
            headers["X-Content-Type-Options"] = "nosniff";

            // Content Security Policy (strict for APIs)
            headers["Content-Security-Policy"] =
                "default-src 'none'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'";

            // === Frame Protection ===

            // Prevent clickjacking
            headers["X-Frame-Options"] = "DENY";

            // === Transport Security ===

            // Force HTTPS (1 year, include subdomains, preload)
            headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload";

            // === Privacy and Referrer ===

            // Control referrer information
            headers["Referrer-Policy"] = "strict-origin-when-cross-origin";

            // Disable browser features
            headers["Permissions-Policy"] =
                "accelerometer=(), camera=(), geolocation=(), gyroscope=(), " +
                "magnetometer=(), microphone=(), payment=(), usb=()";

            // === Cache Control (for sensitive data) ===

            if (IsSensitiveEndpoint(context.Request.Path))
            {
                headers["Cache-Control"] = "no-store, no-cache, must-revalidate, private, max-age=0";
                headers["Pragma"] = "no-cache";
                headers["Expires"] = "0";
            }

            // === Legacy XSS Protection ===

            // For older browsers (modern browsers ignore this)
            headers["X-XSS-Protection"] = "1; mode=block";

            // === Custom Security Headers ===

            // Request ID for tracing (from HttpContext.TraceIdentifier or custom)
            if (context.Items.TryGetValue("RequestId", out var requestId) && requestId is string id)
            {
                headers["X-Request-ID"] = id;
            }
            else
            {
                headers["X-Request-ID"] = context.TraceIdentifier;
            }

            // Remove potentially sensitive headers
            headers.Remove("Server");
            headers.Remove("X-Powered-By");

            return Task.CompletedTask;
        });

        await next(context);
    }

    private bool IsSensitiveEndpoint(PathString path)
    {
        var pathValue = path.Value ?? string.Empty;
        return SensitivePathPrefixes.Any(prefix =>
            pathValue.StartsWith(prefix, StringComparison.OrdinalIgnoreCase));
    }
}

/// <summary>
/// Service for detecting sensitive endpoints that require stricter caching policies.
/// </summary>
public interface ISensitiveEndpointDetector
{
    bool IsSensitive(PathString path);
}

/// <summary>
/// Extension methods for registering security headers middleware.
/// </summary>
public static class SecurityHeadersExtensions
{
    public static IApplicationBuilder UseSecurityHeaders(this IApplicationBuilder app) =>
        app.UseMiddleware<SecurityHeadersMiddleware>();
}
```

## Header Reference Table

### Content Security Headers

| Header | Value | Purpose |
|--------|-------|---------|
| X-Content-Type-Options | `nosniff` | Prevent MIME sniffing |
| Content-Type | `application/json; charset=utf-8` | Explicit content type |
| Content-Security-Policy | `default-src 'none'` | Strict CSP for APIs |

### Transport Security Headers

| Header | Value | Purpose |
|--------|-------|---------|
| Strict-Transport-Security | `max-age=31536000; includeSubDomains; preload` | Force HTTPS |
| Expect-CT | `max-age=86400, enforce` | Certificate Transparency (deprecated in favor of SCT) |

### Frame Protection Headers

| Header | Value | Purpose |
|--------|-------|---------|
| X-Frame-Options | `DENY` | Prevent framing |
| Content-Security-Policy | `frame-ancestors 'none'` | Modern frame protection |

### Cache Control Headers

| Header | Value | Purpose |
|--------|-------|---------|
| Cache-Control | `no-store, private` | Prevent caching sensitive data |
| Pragma | `no-cache` | HTTP/1.0 compatibility |
| Expires | `0` | Immediate expiry |

### Privacy Headers

| Header | Value | Purpose |
|--------|-------|---------|
| Referrer-Policy | `strict-origin-when-cross-origin` | Control referrer leakage |
| Permissions-Policy | `geolocation=(), camera=()` | Disable browser features |

## Content-Security-Policy for APIs

### Strict API CSP

```text
Content-Security-Policy:
  default-src 'none';
  frame-ancestors 'none';
  base-uri 'none';
  form-action 'none'
```

### CSP Directives Explained

| Directive | Purpose | API Value |
|-----------|---------|-----------|
| default-src | Fallback for all resources | `'none'` |
| frame-ancestors | Who can frame this page | `'none'` |
| base-uri | Restrict base element | `'none'` |
| form-action | Where forms can submit | `'none'` |
| script-src | JavaScript sources | N/A for JSON APIs |
| style-src | CSS sources | N/A for JSON APIs |

### CSP Reporting

```csharp
using System.Text.Json;
using System.Text.Json.Serialization;

/// <summary>
/// Middleware that adds CSP with violation reporting.
/// </summary>
public sealed class CspReportingMiddleware(RequestDelegate next, CspReportingOptions options)
{
    public Task InvokeAsync(HttpContext context)
    {
        context.Response.OnStarting(() =>
        {
            var headers = context.Response.Headers;

            // CSP with violation reporting
            headers["Content-Security-Policy"] =
                $"default-src 'none'; frame-ancestors 'none'; " +
                $"report-uri {options.ReportUri}; report-to csp-endpoint";

            // Report-To header for modern reporting
            var reportTo = new ReportToHeader
            {
                Group = "csp-endpoint",
                MaxAge = 10886400,  // ~126 days
                Endpoints = [new ReportEndpoint { Url = options.ReportEndpointUrl }]
            };

            headers["Report-To"] = JsonSerializer.Serialize(reportTo, CspJsonContext.Default.ReportToHeader);

            return Task.CompletedTask;
        });

        return next(context);
    }
}

public sealed record CspReportingOptions
{
    public required string ReportUri { get; init; } = "/api/csp-report";
    public required string ReportEndpointUrl { get; init; } = "https://api.example.com/csp-report";
}

public sealed record ReportToHeader
{
    [JsonPropertyName("group")]
    public required string Group { get; init; }

    [JsonPropertyName("max_age")]
    public required int MaxAge { get; init; }

    [JsonPropertyName("endpoints")]
    public required IReadOnlyList<ReportEndpoint> Endpoints { get; init; }
}

public sealed record ReportEndpoint
{
    [JsonPropertyName("url")]
    public required string Url { get; init; }
}

[JsonSerializable(typeof(ReportToHeader))]
internal partial class CspJsonContext : JsonSerializerContext;
```

## CORS Headers

### CORS Header Reference

| Header | Purpose | Example |
|--------|---------|---------|
| Access-Control-Allow-Origin | Allowed origins | `https://app.example.com` |
| Access-Control-Allow-Methods | Allowed HTTP methods | `GET, POST, PUT, DELETE` |
| Access-Control-Allow-Headers | Allowed request headers | `Content-Type, Authorization` |
| Access-Control-Allow-Credentials | Allow cookies | `true` |
| Access-Control-Max-Age | Preflight cache time | `86400` |
| Access-Control-Expose-Headers | Readable response headers | `X-Request-ID` |

### Secure CORS Configuration

```csharp
using System.Collections.Frozen;
using Microsoft.AspNetCore.Cors.Infrastructure;

/// <summary>
/// Custom CORS policy provider with secure origin validation.
/// </summary>
public sealed class SecureCorsPolicy : ICorsPolicyProvider
{
    private static readonly FrozenSet<string> AllowedOrigins =
        new HashSet<string>(StringComparer.OrdinalIgnoreCase)
        {
            "https://app.example.com",
            "https://admin.example.com",
        }.ToFrozenSet();

    private static readonly string[] AllowedMethods = ["GET", "POST", "PUT", "DELETE", "PATCH"];
    private static readonly string[] AllowedHeaders = ["Content-Type", "Authorization", "X-Request-ID"];
    private static readonly string[] ExposeHeaders = ["X-Request-ID", "X-RateLimit-Remaining"];

    public Task<CorsPolicy?> GetPolicyAsync(HttpContext context, string? policyName)
    {
        var origin = context.Request.Headers.Origin.FirstOrDefault();

        // Only allow CORS for validated origins
        if (string.IsNullOrEmpty(origin) || !AllowedOrigins.Contains(origin))
        {
            return Task.FromResult<CorsPolicy?>(null);
        }

        var policy = new CorsPolicyBuilder()
            .WithOrigins(origin)
            .WithMethods(AllowedMethods)
            .WithHeaders(AllowedHeaders)
            .WithExposedHeaders(ExposeHeaders)
            .AllowCredentials()
            .SetPreflightMaxAge(TimeSpan.FromHours(24))
            .Build();

        return Task.FromResult<CorsPolicy?>(policy);
    }
}

/// <summary>
/// Middleware for handling CORS preflight requests with strict origin validation.
/// </summary>
public sealed class SecureCorsMiddleware(RequestDelegate next)
{
    private static readonly FrozenSet<string> AllowedOrigins =
        new HashSet<string>(StringComparer.OrdinalIgnoreCase)
        {
            "https://app.example.com",
            "https://admin.example.com",
        }.ToFrozenSet();

    public async Task InvokeAsync(HttpContext context)
    {
        var origin = context.Request.Headers.Origin.FirstOrDefault();

        // Handle preflight OPTIONS requests
        if (HttpMethods.IsOptions(context.Request.Method))
        {
            if (string.IsNullOrEmpty(origin) || !AllowedOrigins.Contains(origin))
            {
                context.Response.StatusCode = StatusCodes.Status403Forbidden;
                return;
            }

            // Add preflight response headers
            var headers = context.Response.Headers;
            headers["Access-Control-Allow-Origin"] = origin;
            headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, PATCH";
            headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Request-ID";
            headers["Access-Control-Allow-Credentials"] = "true";
            headers["Access-Control-Max-Age"] = "86400";
            headers["Vary"] = "Origin";

            context.Response.StatusCode = StatusCodes.Status204NoContent;
            return;
        }

        // Add CORS headers to regular responses
        if (!string.IsNullOrEmpty(origin) && AllowedOrigins.Contains(origin))
        {
            context.Response.OnStarting(() =>
            {
                var headers = context.Response.Headers;
                headers["Access-Control-Allow-Origin"] = origin;
                headers["Access-Control-Allow-Credentials"] = "true";
                headers["Access-Control-Expose-Headers"] = "X-Request-ID, X-RateLimit-Remaining";
                headers["Vary"] = "Origin";
                return Task.CompletedTask;
            });
        }

        await next(context);
    }
}
```

### CORS Security Rules

1. **Never use `*` with credentials**: `Access-Control-Allow-Origin: *` cannot be used with `Access-Control-Allow-Credentials: true`

2. **Validate origin dynamically**: Don't blindly reflect the Origin header

3. **Limit allowed methods**: Only allow methods your API uses

4. **Limit allowed headers**: Whitelist specific headers

5. **Use Vary header**: Always include `Vary: Origin` for caching

## Cache Control Strategies

### By Endpoint Type

```csharp
using System.Collections.Frozen;
using System.Text.RegularExpressions;

/// <summary>
/// Cache control strategies for different endpoint types.
/// </summary>
public enum CacheStrategy
{
    /// <summary>No caching for sensitive data.</summary>
    NoCache,
    /// <summary>Private caching (browser only) for user-specific data.</summary>
    Private,
    /// <summary>Public caching for static reference data.</summary>
    Public,
    /// <summary>Immutable caching for versioned static assets.</summary>
    Immutable
}

/// <summary>
/// Service for determining appropriate cache headers based on endpoint.
/// </summary>
public sealed class CacheStrategyResolver
{
    private static readonly FrozenDictionary<string, CacheStrategy> ExactMatches =
        new Dictionary<string, CacheStrategy>(StringComparer.OrdinalIgnoreCase)
        {
            ["/api/config"] = CacheStrategy.Private,
            ["/api/public/countries"] = CacheStrategy.Public,
        }.ToFrozenDictionary();

    private static readonly (Regex Pattern, CacheStrategy Strategy)[] PrefixPatterns =
    [
        (new Regex(@"^/api/users/me", RegexOptions.IgnoreCase | RegexOptions.Compiled), CacheStrategy.NoCache),
        (new Regex(@"^/api/users/.+/settings", RegexOptions.IgnoreCase | RegexOptions.Compiled), CacheStrategy.NoCache),
        (new Regex(@"^/api/auth/", RegexOptions.IgnoreCase | RegexOptions.Compiled), CacheStrategy.NoCache),
        (new Regex(@"^/api/static/", RegexOptions.IgnoreCase | RegexOptions.Compiled), CacheStrategy.Immutable),
    ];

    private static readonly FrozenDictionary<CacheStrategy, string> CacheControlValues =
        new Dictionary<CacheStrategy, string>
        {
            [CacheStrategy.NoCache] = "no-store, no-cache, must-revalidate, private",
            [CacheStrategy.Private] = "private, max-age=60",
            [CacheStrategy.Public] = "public, max-age=300",
            [CacheStrategy.Immutable] = "public, max-age=31536000, immutable",
        }.ToFrozenDictionary();

    /// <summary>
    /// Get appropriate cache headers for the endpoint.
    /// </summary>
    public CacheHeaders GetCacheHeaders(string path, bool isAuthenticated)
    {
        var strategy = ResolveStrategy(path);

        // Override for authenticated requests - demote public/immutable to private
        if (isAuthenticated && strategy is CacheStrategy.Public or CacheStrategy.Immutable)
        {
            strategy = CacheStrategy.Private;
        }

        return new CacheHeaders
        {
            CacheControl = CacheControlValues[strategy],
            Pragma = strategy == CacheStrategy.NoCache ? "no-cache" : null,
            Expires = strategy == CacheStrategy.NoCache ? "0" : null,
        };
    }

    private static CacheStrategy ResolveStrategy(string path)
    {
        // Check exact matches first
        if (ExactMatches.TryGetValue(path, out var exactStrategy))
        {
            return exactStrategy;
        }

        // Check prefix patterns
        foreach (var (pattern, strategy) in PrefixPatterns)
        {
            if (pattern.IsMatch(path))
            {
                return strategy;
            }
        }

        // Default to no caching for safety
        return CacheStrategy.NoCache;
    }
}

public sealed record CacheHeaders
{
    public required string CacheControl { get; init; }
    public string? Pragma { get; init; }
    public string? Expires { get; init; }

    public void ApplyTo(IHeaderDictionary headers)
    {
        headers["Cache-Control"] = CacheControl;
        if (Pragma is not null) headers["Pragma"] = Pragma;
        if (Expires is not null) headers["Expires"] = Expires;
    }
}
```

### ETags for Conditional Requests

```csharp
using System.Security.Cryptography;

/// <summary>
/// Middleware for handling ETags and conditional requests.
/// </summary>
public sealed class ETagMiddleware(RequestDelegate next)
{
    public async Task InvokeAsync(HttpContext context)
    {
        // Only handle GET/HEAD requests for ETag
        if (!HttpMethods.IsGet(context.Request.Method) &&
            !HttpMethods.IsHead(context.Request.Method))
        {
            await next(context);
            return;
        }

        // Capture the response body
        var originalBodyStream = context.Response.Body;
        using var memoryStream = new MemoryStream();
        context.Response.Body = memoryStream;

        await next(context);

        // Calculate ETag from response content
        memoryStream.Seek(0, SeekOrigin.Begin);
        var content = memoryStream.ToArray();
        var etag = GenerateETag(content);

        context.Response.Headers.ETag = $"\"{etag}\"";

        // Check If-None-Match header
        var ifNoneMatch = context.Request.Headers.IfNoneMatch.FirstOrDefault();
        if (!string.IsNullOrEmpty(ifNoneMatch))
        {
            var clientEtag = ifNoneMatch.Trim('"');
            if (string.Equals(clientEtag, etag, StringComparison.Ordinal))
            {
                // Content hasn't changed - return 304 Not Modified
                context.Response.StatusCode = StatusCodes.Status304NotModified;
                context.Response.Body = originalBodyStream;
                context.Response.ContentLength = 0;
                return;
            }
        }

        // Write the buffered content to the original stream
        memoryStream.Seek(0, SeekOrigin.Begin);
        await memoryStream.CopyToAsync(originalBodyStream);
        context.Response.Body = originalBodyStream;
    }

    private static string GenerateETag(byte[] content)
    {
        var hash = SHA256.HashData(content);
        return Convert.ToHexString(hash)[..16];  // Use first 16 chars of SHA256
    }
}
```

## Request Headers to Validate

### Security-Relevant Request Headers

```csharp
using System.Collections.Frozen;
using System.Net;

/// <summary>
/// Service for validating security-relevant request headers.
/// </summary>
public sealed class RequestHeaderValidator(IConfiguration configuration)
{
    private readonly FrozenSet<string> _allowedHosts =
        configuration.GetSection("Security:AllowedHosts")
            .Get<string[]>()
            ?.ToFrozenSet(StringComparer.OrdinalIgnoreCase)
        ?? FrozenSet<string>.Empty;

    private readonly FrozenSet<IPAddress> _trustedProxies =
        configuration.GetSection("Security:TrustedProxies")
            .Get<string[]>()
            ?.Select(ip => IPAddress.Parse(ip))
            .ToFrozenSet()
        ?? FrozenSet<IPAddress>.Empty;

    private static readonly FrozenSet<string> ForwardedHeaders = new HashSet<string>(StringComparer.OrdinalIgnoreCase)
    {
        "X-Forwarded-For",
        "X-Forwarded-Host",
        "X-Forwarded-Proto",
    }.ToFrozenSet();

    /// <summary>
    /// Validate security-relevant request headers.
    /// </summary>
    public HeaderValidationResult Validate(HttpContext context)
    {
        var issues = new List<string>();
        var request = context.Request;

        // Content-Type validation for mutating requests
        if (HttpMethods.IsPost(request.Method) ||
            HttpMethods.IsPut(request.Method) ||
            HttpMethods.IsPatch(request.Method))
        {
            var contentType = request.ContentType ?? string.Empty;
            if (!contentType.StartsWith("application/json", StringComparison.OrdinalIgnoreCase))
            {
                issues.Add("Invalid Content-Type: expected application/json");
            }
        }

        // Host header validation (prevent host header injection)
        var host = request.Host.Host;
        if (!_allowedHosts.Contains(host))
        {
            issues.Add($"Invalid Host header: {host}");
        }

        // X-Forwarded-* validation (only trust from known proxies)
        var remoteIp = context.Connection.RemoteIpAddress;
        if (remoteIp is not null && !_trustedProxies.Contains(remoteIp))
        {
            foreach (var header in ForwardedHeaders)
            {
                if (request.Headers.ContainsKey(header))
                {
                    issues.Add($"Untrusted {header} header from {remoteIp}");
                }
            }
        }

        return new HeaderValidationResult(issues.Count == 0, [.. issues]);
    }
}

public sealed record HeaderValidationResult(bool IsValid, IReadOnlyList<string> Issues);
```

### Headers to Strip from Requests

```csharp
using System.Collections.Frozen;
using System.Net;

/// <summary>
/// Middleware that strips potentially dangerous headers from untrusted sources.
/// </summary>
public sealed class HeaderStrippingMiddleware(RequestDelegate next, IConfiguration configuration)
{
    private static readonly FrozenSet<string> HeadersToStrip = new HashSet<string>(StringComparer.OrdinalIgnoreCase)
    {
        "X-Forwarded-For",
        "X-Forwarded-Host",
        "X-Forwarded-Proto",
        "X-Real-IP",
        "X-Original-URL",
        "X-Rewrite-URL",
    }.ToFrozenSet();

    private readonly FrozenSet<IPAddress> _trustedProxies =
        configuration.GetSection("Security:TrustedProxies")
            .Get<string[]>()
            ?.Select(ip => IPAddress.Parse(ip))
            .ToFrozenSet()
        ?? FrozenSet<IPAddress>.Empty;

    public Task InvokeAsync(HttpContext context)
    {
        var remoteIp = context.Connection.RemoteIpAddress;

        // Only strip headers from untrusted sources
        if (remoteIp is null || !_trustedProxies.Contains(remoteIp))
        {
            foreach (var header in HeadersToStrip)
            {
                context.Request.Headers.Remove(header);
            }
        }

        return next(context);
    }
}
```

## Error Response Headers

### Secure Error Responses

```csharp
using System.Text.Json;
using System.Text.Json.Serialization;
using Microsoft.AspNetCore.Diagnostics;

/// <summary>
/// Factory for creating secure error responses with appropriate headers.
/// </summary>
public static class SecureErrorResponse
{
    /// <summary>
    /// Write a secure error response with proper headers.
    /// </summary>
    public static async Task WriteAsync(
        HttpContext context,
        int statusCode,
        string message,
        string? errorCode = null)
    {
        var error = new ErrorResponse
        {
            Error = new ErrorDetails
            {
                Message = message,
                Code = errorCode ?? $"ERR_{statusCode}",
            }
        };

        context.Response.StatusCode = statusCode;

        // Security headers on errors too
        context.Response.Headers["X-Content-Type-Options"] = "nosniff";
        context.Response.ContentType = "application/json; charset=utf-8";

        // No caching for errors
        context.Response.Headers["Cache-Control"] = "no-store";

        // Remove potentially sensitive headers
        context.Response.Headers.Remove("Server");
        context.Response.Headers.Remove("X-Powered-By");

        await context.Response.WriteAsJsonAsync(error, ErrorJsonContext.Default.ErrorResponse);
    }
}

public sealed record ErrorResponse
{
    [JsonPropertyName("error")]
    public required ErrorDetails Error { get; init; }
}

public sealed record ErrorDetails
{
    [JsonPropertyName("message")]
    public required string Message { get; init; }

    [JsonPropertyName("code")]
    public required string Code { get; init; }
}

[JsonSerializable(typeof(ErrorResponse))]
internal partial class ErrorJsonContext : JsonSerializerContext;

/// <summary>
/// Global exception handler that returns secure error responses.
/// </summary>
public sealed class SecureExceptionHandler(ILogger<SecureExceptionHandler> logger) : IExceptionHandler
{
    public async ValueTask<bool> TryHandleAsync(
        HttpContext httpContext,
        Exception exception,
        CancellationToken cancellationToken)
    {
        // Log full error internally
        logger.LogError(exception, "Unhandled exception occurred");

        // Return generic message (don't leak details)
        await SecureErrorResponse.WriteAsync(
            httpContext,
            StatusCodes.Status500InternalServerError,
            "An internal error occurred",
            "INTERNAL_ERROR");

        return true;  // Exception was handled
    }
}

// Registration in Program.cs:
// builder.Services.AddExceptionHandler<SecureExceptionHandler>();
// app.UseExceptionHandler();
```

## Platform-Specific Configuration

### Nginx

```nginx
# Security headers in nginx
add_header X-Content-Type-Options "nosniff" always;
add_header X-Frame-Options "DENY" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
add_header Content-Security-Policy "default-src 'none'; frame-ancestors 'none'" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Permissions-Policy "geolocation=(), microphone=(), camera=()" always;

# Hide server version
server_tokens off;

# Remove X-Powered-By if set by upstream
proxy_hide_header X-Powered-By;
```

### AWS API Gateway

```yaml
# CloudFormation for API Gateway
GatewayResponses:
  DEFAULT_4XX:
    ResponseParameters:
      gatewayresponse.header.X-Content-Type-Options: "'nosniff'"
      gatewayresponse.header.X-Frame-Options: "'DENY'"
      gatewayresponse.header.Strict-Transport-Security: "'max-age=31536000'"

  DEFAULT_5XX:
    ResponseParameters:
      gatewayresponse.header.X-Content-Type-Options: "'nosniff'"
      gatewayresponse.header.X-Frame-Options: "'DENY'"
```

### Express.js (Node.js)

```javascript
const helmet = require('helmet');

app.use(helmet({
    contentSecurityPolicy: {
        directives: {
            defaultSrc: ["'none'"],
            frameAncestors: ["'none'"],
        },
    },
    hsts: {
        maxAge: 31536000,
        includeSubDomains: true,
        preload: true,
    },
    frameguard: { action: 'deny' },
    noSniff: true,
    referrerPolicy: { policy: 'strict-origin-when-cross-origin' },
}));

// Remove X-Powered-By
app.disable('x-powered-by');
```

### ASP.NET Core

```csharp
// In Program.cs or Startup.cs
app.Use(async (context, next) =>
{
    context.Response.Headers.Add("X-Content-Type-Options", "nosniff");
    context.Response.Headers.Add("X-Frame-Options", "DENY");
    context.Response.Headers.Add("X-XSS-Protection", "1; mode=block");
    context.Response.Headers.Add("Referrer-Policy", "strict-origin-when-cross-origin");
    context.Response.Headers.Add("Content-Security-Policy",
        "default-src 'none'; frame-ancestors 'none'");
    context.Response.Headers.Add("Permissions-Policy",
        "geolocation=(), microphone=(), camera=()");

    // Remove server header
    context.Response.Headers.Remove("Server");

    await next();
});

// HSTS in production
if (app.Environment.IsProduction())
{
    app.UseHsts();
}
```

## Testing Headers

### Security Scanner Integration

```csharp
using Microsoft.AspNetCore.Mvc.Testing;
using Xunit;

/// <summary>
/// Integration tests for security headers compliance.
/// </summary>
public sealed class SecurityHeadersTests(WebApplicationFactory<Program> factory)
    : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly HttpClient _client = factory.CreateClient();

    [Fact]
    public async Task Response_ContainsAllRequiredSecurityHeaders()
    {
        // Arrange & Act
        var response = await _client.GetAsync("/api/test");

        // Assert - Required headers with exact values
        AssertHeaderEquals(response, "X-Content-Type-Options", "nosniff");
        AssertHeaderEquals(response, "X-Frame-Options", "DENY");
        AssertHeaderEquals(response, "Referrer-Policy", "strict-origin-when-cross-origin");

        // Assert - Required headers with pattern matching
        AssertHeaderContains(response, "Strict-Transport-Security", "max-age=");
        AssertHeaderContains(response, "Content-Security-Policy", "default-src 'none'");
    }

    [Fact]
    public async Task Response_DoesNotContainForbiddenHeaders()
    {
        // Arrange & Act
        var response = await _client.GetAsync("/api/test");

        // Assert - Headers that should NOT be present
        string[] forbiddenHeaders = ["Server", "X-Powered-By", "X-AspNet-Version", "X-AspNetMvc-Version"];

        foreach (var header in forbiddenHeaders)
        {
            Assert.False(
                response.Headers.Contains(header) || response.Content.Headers.Contains(header),
                $"Forbidden header present: {header}");
        }
    }

    [Theory]
    [InlineData("/api/users/me")]
    [InlineData("/api/auth/token")]
    [InlineData("/api/account/settings")]
    public async Task SensitiveEndpoints_HaveNoCacheHeaders(string path)
    {
        // Arrange & Act
        var response = await _client.GetAsync(path);

        // Assert - Sensitive endpoints must not be cached
        AssertHeaderContains(response, "Cache-Control", "no-store");
        AssertHeaderEquals(response, "Pragma", "no-cache");
    }

    private static void AssertHeaderEquals(
        HttpResponseMessage response,
        string headerName,
        string expectedValue)
    {
        var found = response.Headers.TryGetValues(headerName, out var values)
                 || response.Content.Headers.TryGetValues(headerName, out values);

        Assert.True(found, $"Missing header: {headerName}");

        var value = values!.FirstOrDefault();
        Assert.Equal(expectedValue, value);
    }

    private static void AssertHeaderContains(
        HttpResponseMessage response,
        string headerName,
        string expectedSubstring)
    {
        var found = response.Headers.TryGetValues(headerName, out var values)
                 || response.Content.Headers.TryGetValues(headerName, out values);

        Assert.True(found, $"Missing header: {headerName}");

        var value = values!.FirstOrDefault() ?? string.Empty;
        Assert.Contains(expectedSubstring, value);
    }
}
```

## Security Checklist

### Required Headers

- [ ] X-Content-Type-Options: nosniff
- [ ] X-Frame-Options: DENY
- [ ] Strict-Transport-Security (HSTS)
- [ ] Content-Security-Policy
- [ ] Referrer-Policy

### Recommended Headers

- [ ] Permissions-Policy
- [ ] Cache-Control (appropriate for endpoint)
- [ ] X-Request-ID (for tracing)

### Headers to Remove

- [ ] Server (or set to generic value)
- [ ] X-Powered-By
- [ ] X-AspNet-Version
- [ ] X-AspNetMvc-Version

### CORS (if needed)

- [ ] Specific origins (not *)
- [ ] Limited methods
- [ ] Limited headers
- [ ] Vary: Origin header
