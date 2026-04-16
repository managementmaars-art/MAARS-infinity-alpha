# ZTNA Implementation Reference

## Overview

Zero Trust Network Access (ZTNA) replaces traditional VPN with identity-aware, application-specific access. This reference covers implementation patterns for ZTNA solutions.

## ZTNA vs VPN

| Aspect | Traditional VPN | ZTNA |
| --- | --- | --- |
| **Trust Model** | Network-centric | Identity-centric |
| **Access Scope** | Full network access | Application-specific |
| **Authentication** | Once at connection | Continuous |
| **Visibility** | Limited | Full session visibility |
| **Lateral Movement** | Enabled | Prevented |
| **User Experience** | Client required | Often clientless |

## ZTNA Architecture Patterns

### Service-Initiated ZTNA

```text
┌──────────────────────────────────────────────────────────────────┐
│                 SERVICE-INITIATED ZTNA                           │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────┐    HTTPS    ┌────────────────┐                      │
│  │  User   │────────────▶│   ZTNA Cloud   │                      │
│  │ Browser │◀────────────│   Controller   │                      │
│  └─────────┘             └───────┬────────┘                      │
│                                  │                                │
│                                  │ Outbound-only                  │
│                                  │ connection                     │
│                                  │                                │
│  ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─│─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─   │
│                          Corporate Network                        │
│                                  │                                │
│                          ┌───────▼────────┐                      │
│                          │  ZTNA Connector│                      │
│                          │  (Outbound)    │                      │
│                          └───────┬────────┘                      │
│                                  │                                │
│              ┌───────────────────┼───────────────────┐           │
│              │                   │                   │           │
│         ┌────▼────┐        ┌────▼────┐        ┌────▼────┐       │
│         │  App A  │        │  App B  │        │  App C  │       │
│         └─────────┘        └─────────┘        └─────────┘       │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

### Connector Implementation

```csharp
/// <summary>
/// ZTNA Connector for service-initiated architecture.
/// Establishes outbound-only connection to cloud controller.
/// </summary>
public sealed record ZtnaApplication(
    string Id,
    string Name,
    string InternalHost,
    int InternalPort,
    string Protocol,  // http, https, tcp
    string? HealthCheckPath = null);

public sealed record ZtnaConnectorConfig(
    string ControllerUrl,
    string ConnectorId,
    string ConnectorSecret);

public sealed record UserContext(
    string UserId,
    string Email,
    List<string> Groups,
    string SessionId);

public sealed class ZtnaConnector(
    ZtnaConnectorConfig config,
    IHttpClientFactory httpClientFactory,
    ILogger<ZtnaConnector> logger) : BackgroundService
{
    private readonly ConcurrentDictionary<string, ZtnaApplication> _applications = new();
    private readonly ConcurrentDictionary<string, InternalSession> _activeSessions = new();
    private ClientWebSocket? _webSocket;

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        while (!stoppingToken.IsCancellationRequested)
        {
            try
            {
                await ConnectToControllerAsync(stoppingToken);
            }
            catch (Exception ex) when (!stoppingToken.IsCancellationRequested)
            {
                logger.LogError(ex, "Connection error, reconnecting in 5s...");
                await Task.Delay(TimeSpan.FromSeconds(5), stoppingToken);
            }
        }
    }

    private async Task ConnectToControllerAsync(CancellationToken ct)
    {
        // Authenticate with controller
        var client = httpClientFactory.CreateClient("ZtnaController");
        var authResponse = await client.PostAsJsonAsync(
            $"{config.ControllerUrl}/api/connector/auth",
            new { connector_id = config.ConnectorId, secret = config.ConnectorSecret },
            ct);

        authResponse.EnsureSuccessStatusCode();
        var authResult = await authResponse.Content.ReadFromJsonAsync<AuthResponse>(ct);
        var token = authResult?.Token ?? throw new InvalidOperationException("No token received");

        // Connect WebSocket with authentication
        var wsUrl = config.ControllerUrl.Replace("https://", "wss://");
        _webSocket = new ClientWebSocket();
        _webSocket.Options.SetRequestHeader("Authorization", $"Bearer {token}");

        await _webSocket.ConnectAsync(new Uri($"{wsUrl}/connector/ws"), ct);

        // Register applications
        await RegisterApplicationsAsync(ct);

        // Handle incoming messages
        await HandleMessagesAsync(ct);
    }

    private async Task RegisterApplicationsAsync(CancellationToken ct)
    {
        foreach (var app in _applications.Values)
        {
            var message = JsonSerializer.SerializeToUtf8Bytes(new
            {
                type = "register_app",
                app_id = app.Id,
                app_name = app.Name,
                protocol = app.Protocol
            });

            await _webSocket!.SendAsync(message, WebSocketMessageType.Text, true, ct);
        }
    }

    private async Task HandleMessagesAsync(CancellationToken ct)
    {
        var buffer = new byte[4096];

        while (_webSocket?.State == WebSocketState.Open && !ct.IsCancellationRequested)
        {
            var result = await _webSocket.ReceiveAsync(buffer, ct);
            if (result.MessageType == WebSocketMessageType.Close)
                break;

            var message = JsonSerializer.Deserialize<JsonObject>(buffer.AsSpan(0, result.Count));
            var messageType = message?["type"]?.GetValue<string>();

            switch (messageType)
            {
                case "session_request":
                    await HandleSessionRequestAsync(message!, ct);
                    break;
                case "session_data":
                    await HandleSessionDataAsync(message!);
                    break;
                case "session_close":
                    HandleSessionClose(message!);
                    break;
            }
        }
    }

    private async Task HandleSessionRequestAsync(JsonObject data, CancellationToken ct)
    {
        var sessionId = data["session_id"]!.GetValue<string>();
        var appId = data["app_id"]!.GetValue<string>();
        var userContextNode = data["user_context"]!.AsObject();

        var userContext = new UserContext(
            UserId: userContextNode["user_id"]?.GetValue<string>() ?? "",
            Email: userContextNode["email"]?.GetValue<string>() ?? "",
            Groups: userContextNode["groups"]?.AsArray().Select(g => g!.GetValue<string>()).ToList() ?? [],
            SessionId: userContextNode["session_id"]?.GetValue<string>() ?? "");

        if (!_applications.TryGetValue(appId, out var app))
        {
            await SendResponseAsync(new { type = "session_response", session_id = sessionId, status = "error", message = "Application not found" }, ct);
            return;
        }

        try
        {
            var session = CreateInternalSession(app, userContext);
            _activeSessions[sessionId] = session;
            await SendResponseAsync(new { type = "session_response", session_id = sessionId, status = "connected" }, ct);
        }
        catch (Exception ex)
        {
            await SendResponseAsync(new { type = "session_response", session_id = sessionId, status = "error", message = ex.Message }, ct);
        }
    }

    private InternalSession CreateInternalSession(ZtnaApplication app, UserContext userContext)
    {
        var client = httpClientFactory.CreateClient($"App_{app.Id}");
        client.BaseAddress = new Uri($"{app.Protocol}://{app.InternalHost}:{app.InternalPort}");
        client.DefaultRequestHeaders.Add("X-ZTNA-User-ID", userContext.UserId);
        client.DefaultRequestHeaders.Add("X-ZTNA-User-Email", userContext.Email);
        client.DefaultRequestHeaders.Add("X-ZTNA-Groups", string.Join(",", userContext.Groups));
        client.DefaultRequestHeaders.Add("X-ZTNA-Session-ID", userContext.SessionId);

        return new InternalSession(app, userContext, client);
    }

    private async Task SendResponseAsync(object message, CancellationToken ct)
    {
        var bytes = JsonSerializer.SerializeToUtf8Bytes(message);
        await _webSocket!.SendAsync(bytes, WebSocketMessageType.Text, true, ct);
    }

    private Task HandleSessionDataAsync(JsonObject data) => Task.CompletedTask;
    private void HandleSessionClose(JsonObject data)
    {
        var sessionId = data["session_id"]?.GetValue<string>();
        if (sessionId is not null)
            _activeSessions.TryRemove(sessionId, out _);
    }

    public void RegisterApplication(ZtnaApplication app) => _applications[app.Id] = app;
}

public sealed record InternalSession(ZtnaApplication App, UserContext Context, HttpClient Client);
public sealed record AuthResponse(string Token);
```

### Cloud Controller

```csharp
/// <summary>
/// ZTNA Cloud Controller for managing access.
/// </summary>
public sealed record ControllerSession(
    string Id,
    string UserId,
    string? DeviceId,
    string AppId,
    DateTimeOffset CreatedAt,
    DateTimeOffset ExpiresAt,
    DateTimeOffset LastActivity,
    double RiskScore);

public sealed record ApplicationInfo(string ConnectorId, string AppId, string AppName, string Protocol);

public sealed class ZtnaController
{
    private readonly ConcurrentDictionary<string, WebSocket> _connectors = new();
    private readonly ConcurrentDictionary<string, ApplicationInfo> _applications = new();
    private readonly ConcurrentDictionary<string, ControllerSession> _sessions = new();
    private readonly IPolicyEngine _policyEngine;

    public ZtnaController(IPolicyEngine policyEngine) => _policyEngine = policyEngine;

    public void RegisterConnector(string connectorId, WebSocket websocket) =>
        _connectors[connectorId] = websocket;

    public void UnregisterConnector(string connectorId) =>
        _connectors.TryRemove(connectorId, out _);

    public void RegisterApplication(string connectorId, string appId, string appName, string protocol) =>
        _applications[appId] = new ApplicationInfo(connectorId, appId, appName, protocol);

    public async Task<IResult> HandleAccessRequestAsync(HttpContext context, string appId, CancellationToken ct)
    {
        // Step 1: Authenticate user
        var user = await AuthenticateUserAsync(context);
        if (user is null)
            return Results.Redirect("/login");

        // Step 2: Get device posture
        var device = await GetDevicePostureAsync(context);

        // Step 3: Check access policy
        var policyContext = new PolicyContext(
            User: user,
            Device: device,
            AppId: appId,
            SourceIp: context.Connection.RemoteIpAddress?.ToString() ?? "unknown",
            Timestamp: DateTimeOffset.UtcNow);

        var decision = await _policyEngine.EvaluateAsync(policyContext, ct);

        if (decision.Action == PolicyAction.Deny)
            return Results.Forbid();

        if (decision.Action == PolicyAction.StepUp)
            return Results.Redirect($"/step-up?reason={Uri.EscapeDataString(decision.Reason ?? "")}");

        // Step 4: Create session
        var session = CreateSession(user, device, appId);

        // Step 5: Route request to connector
        if (!_applications.TryGetValue(appId, out var appInfo))
            return Results.NotFound("Application not found");

        if (!_connectors.TryGetValue(appInfo.ConnectorId, out var connectorWs))
            return Results.Problem("Application offline", statusCode: StatusCodes.Status503ServiceUnavailable);

        // Send session request to connector
        var requestMessage = JsonSerializer.SerializeToUtf8Bytes(new
        {
            type = "session_request",
            session_id = session.Id,
            app_id = appId,
            user_context = new
            {
                user_id = user.Id,
                email = user.Email,
                groups = user.Groups,
                session_id = session.Id
            }
        });

        await connectorWs.SendAsync(requestMessage, WebSocketMessageType.Text, true, ct);
        return Results.Ok(session);
    }

    private ControllerSession CreateSession(UserInfo user, DeviceInfo? device, string appId)
    {
        var sessionId = Guid.NewGuid().ToString("N");
        var session = new ControllerSession(
            Id: sessionId,
            UserId: user.Id,
            DeviceId: device?.Id,
            AppId: appId,
            CreatedAt: DateTimeOffset.UtcNow,
            ExpiresAt: DateTimeOffset.UtcNow.AddHours(8),
            LastActivity: DateTimeOffset.UtcNow,
            RiskScore: 0.0);

        _sessions[sessionId] = session;
        return session;
    }

    private Task<UserInfo?> AuthenticateUserAsync(HttpContext context) => Task.FromResult<UserInfo?>(null);
    private Task<DeviceInfo?> GetDevicePostureAsync(HttpContext context) => Task.FromResult<DeviceInfo?>(null);
}

public sealed record PolicyContext(UserInfo User, DeviceInfo? Device, string AppId, string SourceIp, DateTimeOffset Timestamp);
public sealed record UserInfo(string Id, string Email, List<string> Groups);
public sealed record DeviceInfo(string Id, bool IsTrusted);
public enum PolicyAction { Allow, Deny, StepUp }
public sealed record PolicyDecision(PolicyAction Action, string? Reason = null);

public interface IPolicyEngine
{
    Task<PolicyDecision> EvaluateAsync(PolicyContext context, CancellationToken ct = default);
}

// WebSocket endpoint for connectors
public static class ZtnaControllerEndpoints
{
    public static void MapZtnaEndpoints(this WebApplication app)
    {
        app.MapGet("/access/{appId}", async (string appId, HttpContext ctx, ZtnaController controller, CancellationToken ct) =>
            await controller.HandleAccessRequestAsync(ctx, appId, ct));

        app.Map("/connector/ws", async (HttpContext context, ZtnaController controller, IConnectorAuthValidator validator) =>
        {
            if (!context.WebSockets.IsWebSocketRequest)
            {
                context.Response.StatusCode = StatusCodes.Status400BadRequest;
                return;
            }

            using var websocket = await context.WebSockets.AcceptWebSocketAsync();
            var buffer = new byte[4096];

            // Authenticate connector
            var result = await websocket.ReceiveAsync(buffer, CancellationToken.None);
            var auth = JsonSerializer.Deserialize<ConnectorAuth>(buffer.AsSpan(0, result.Count));

            if (auth is null || !await validator.ValidateAsync(auth))
            {
                await websocket.CloseAsync(WebSocketCloseStatus.PolicyViolation, "Auth failed", CancellationToken.None);
                return;
            }

            controller.RegisterConnector(auth.ConnectorId, websocket);

            try
            {
                while (websocket.State == WebSocketState.Open)
                {
                    result = await websocket.ReceiveAsync(buffer, CancellationToken.None);
                    if (result.MessageType == WebSocketMessageType.Close)
                        break;

                    var message = JsonSerializer.Deserialize<JsonObject>(buffer.AsSpan(0, result.Count));
                    var messageType = message?["type"]?.GetValue<string>();

                    if (messageType == "register_app")
                    {
                        controller.RegisterApplication(
                            auth.ConnectorId,
                            message!["app_id"]!.GetValue<string>(),
                            message["app_name"]?.GetValue<string>() ?? "",
                            message["protocol"]?.GetValue<string>() ?? "https");
                    }
                }
            }
            finally
            {
                controller.UnregisterConnector(auth.ConnectorId);
            }
        });
    }
}

public sealed record ConnectorAuth(string ConnectorId, string Secret);
public interface IConnectorAuthValidator
{
    Task<bool> ValidateAsync(ConnectorAuth auth, CancellationToken ct = default);
}
```

## Application-Level ZTNA

### OAuth2/OIDC Protected Application

```csharp
/// <summary>
/// Application protected with ZTNA using OAuth2/OIDC.
/// </summary>
public sealed record ZtnaVerifyRequest(string AppId, string RequestedPath, string Method);
public sealed record ZtnaUserContext(string UserId, string Email, List<string> Groups);

public sealed class ZtnaMiddleware(
    RequestDelegate next,
    IHttpClientFactory httpClientFactory,
    IOptions<ZtnaOptions> options)
{
    private const string ZtnaTokenHeader = "X-ZTNA-Token";
    private const string ZtnaSessionCookie = "ztna_session";

    public async Task InvokeAsync(HttpContext context)
    {
        // Check for ZTNA session token
        var ztnaToken = context.Request.Headers[ZtnaTokenHeader].FirstOrDefault()
            ?? context.Request.Cookies[ZtnaSessionCookie];

        if (string.IsNullOrEmpty(ztnaToken))
        {
            RedirectToLogin(context);
            return;
        }

        // Verify token with ZTNA controller
        try
        {
            var client = httpClientFactory.CreateClient("ZtnaVerify");
            var request = new HttpRequestMessage(HttpMethod.Post, options.Value.VerifyUrl);
            request.Headers.Authorization = new AuthenticationHeaderValue("Bearer", ztnaToken);
            request.Content = JsonContent.Create(new ZtnaVerifyRequest(
                AppId: options.Value.AppId,
                RequestedPath: context.Request.Path.Value ?? "/",
                Method: context.Request.Method));

            var response = await client.SendAsync(request);

            if (!response.IsSuccessStatusCode)
            {
                RedirectToLogin(context);
                return;
            }

            // Add user context to request
            var userContext = await response.Content.ReadFromJsonAsync<ZtnaUserContext>();
            context.Items["ztna_user"] = userContext;
        }
        catch
        {
            context.Response.StatusCode = StatusCodes.Status503ServiceUnavailable;
            await context.Response.WriteAsync("ZTNA verification failed");
            return;
        }

        await next(context);
    }

    private void RedirectToLogin(HttpContext context)
    {
        var redirectUrl = $"{options.Value.LoginUrl}?redirect={Uri.EscapeDataString(context.Request.GetDisplayUrl())}";
        context.Response.Redirect(redirectUrl);
    }
}

public sealed class ZtnaOptions
{
    public string VerifyUrl { get; set; } = "https://ztna.example.com/api/verify";
    public string LoginUrl { get; set; } = "https://ztna.example.com/login";
    public string AppId { get; set; } = "my-app";
}

// Registration and usage
public static class ZtnaExtensions
{
    public static IServiceCollection AddZtna(this IServiceCollection services, Action<ZtnaOptions> configure)
    {
        services.Configure(configure);
        services.AddHttpClient("ZtnaVerify");
        return services;
    }

    public static IApplicationBuilder UseZtna(this IApplicationBuilder app) =>
        app.UseMiddleware<ZtnaMiddleware>();
}

// Protected endpoint example
public static class ZtnaProtectedEndpoints
{
    public static void MapProtectedEndpoints(this WebApplication app)
    {
        app.MapGet("/api/data", (HttpContext context) =>
        {
            var user = context.Items["ztna_user"] as ZtnaUserContext;
            return Results.Ok(new { data = "sensitive", user = user?.Email });
        }).RequireAuthorization();
    }
}
```

## Session Management

### Continuous Session Verification

```csharp
/// <summary>
/// Continuous session verification for ZTNA.
/// </summary>
public sealed class ZtnaSession
{
    public required string SessionId { get; init; }
    public required string UserId { get; init; }
    public required string DeviceId { get; init; }
    public required string AppId { get; init; }
    public DateTimeOffset CreatedAt { get; init; } = DateTimeOffset.UtcNow;
    public DateTimeOffset ExpiresAt { get; init; }
    public DateTimeOffset LastVerification { get; set; }
    public double RiskScore { get; set; }
    public bool IsValid { get; set; } = true;
}

public sealed record SessionVerificationContext(
    DevicePosture? DevicePosture,
    ActivitySummary? Activity,
    bool LocationChanged,
    bool DeviceChanged,
    bool UnusualActivity);

public sealed record DevicePosture(string DeviceId, bool Compliant, DateTimeOffset LastCheck);
public sealed record ActivitySummary(int RequestCount, string? LastIp, DateTimeOffset LastActive);

public sealed record SessionVerificationResult(
    bool Valid,
    string? Reason = null,
    double? RiskScore = null,
    string? UserId = null,
    double? RemainingSeconds = null);

public sealed class SessionManager : IHostedService
{
    private readonly ConcurrentDictionary<string, ZtnaSession> _sessions = new();
    private readonly TimeSpan _verificationInterval;
    private readonly double _riskThreshold;
    private readonly ISessionNotifier _notifier;
    private readonly IDevicePostureService _deviceService;
    private readonly IActivityService _activityService;
    private CancellationTokenSource? _cts;

    public SessionManager(
        IOptions<SessionManagerOptions> options,
        ISessionNotifier notifier,
        IDevicePostureService deviceService,
        IActivityService activityService)
    {
        _verificationInterval = TimeSpan.FromSeconds(options.Value.VerificationIntervalSeconds);
        _riskThreshold = options.Value.RiskThreshold;
        _notifier = notifier;
        _deviceService = deviceService;
        _activityService = activityService;
    }

    public Task StartAsync(CancellationToken ct)
    {
        _cts = CancellationTokenSource.CreateLinkedTokenSource(ct);
        return Task.CompletedTask;
    }

    public Task StopAsync(CancellationToken ct)
    {
        _cts?.Cancel();
        return Task.CompletedTask;
    }

    public async Task<ZtnaSession> CreateSessionAsync(
        string userId, string deviceId, string appId, double initialRiskScore)
    {
        var session = new ZtnaSession
        {
            SessionId = Guid.NewGuid().ToString("N"),
            UserId = userId,
            DeviceId = deviceId,
            AppId = appId,
            ExpiresAt = DateTimeOffset.UtcNow.AddHours(8),
            LastVerification = DateTimeOffset.UtcNow,
            RiskScore = initialRiskScore
        };

        _sessions[session.SessionId] = session;

        // Start continuous verification
        _ = ContinuousVerifyAsync(session.SessionId, _cts?.Token ?? CancellationToken.None);

        return session;
    }

    public async Task<SessionVerificationResult> VerifySessionAsync(string sessionId, SessionVerificationContext context)
    {
        if (!_sessions.TryGetValue(sessionId, out var session))
            return new SessionVerificationResult(Valid: false, Reason: "Session not found");

        if (!session.IsValid)
            return new SessionVerificationResult(Valid: false, Reason: "Session invalidated");

        if (DateTimeOffset.UtcNow > session.ExpiresAt)
        {
            session.IsValid = false;
            return new SessionVerificationResult(Valid: false, Reason: "Session expired");
        }

        // Update risk score
        var newRisk = CalculateSessionRisk(session, context);
        session.RiskScore = newRisk;
        session.LastVerification = DateTimeOffset.UtcNow;

        if (newRisk > _riskThreshold)
        {
            session.IsValid = false;
            return new SessionVerificationResult(Valid: false, Reason: "Risk threshold exceeded", RiskScore: newRisk);
        }

        return new SessionVerificationResult(
            Valid: true,
            RiskScore: newRisk,
            UserId: session.UserId,
            RemainingSeconds: (session.ExpiresAt - DateTimeOffset.UtcNow).TotalSeconds);
    }

    private async Task ContinuousVerifyAsync(string sessionId, CancellationToken ct)
    {
        while (!ct.IsCancellationRequested)
        {
            await Task.Delay(_verificationInterval, ct);

            if (!_sessions.TryGetValue(sessionId, out var session) || !session.IsValid)
                break;

            var context = await GatherContextAsync(session, ct);
            var result = await VerifySessionAsync(sessionId, context);

            if (!result.Valid)
            {
                await _notifier.NotifySessionTerminatedAsync(session, result.Reason ?? "Unknown", ct);
                break;
            }
        }
    }

    private double CalculateSessionRisk(ZtnaSession session, SessionVerificationContext context)
    {
        var risk = session.RiskScore * 0.5; // Decay existing risk

        if (context.LocationChanged) risk += 0.3;
        if (context.DeviceChanged) risk += 0.4;
        if (context.UnusualActivity) risk += 0.2;

        // Time-based risk increase
        var sessionAgeHours = (DateTimeOffset.UtcNow - session.CreatedAt).TotalHours;
        risk += Math.Min(0.1, sessionAgeHours * 0.01);

        return Math.Min(1.0, risk);
    }

    private async Task<SessionVerificationContext> GatherContextAsync(ZtnaSession session, CancellationToken ct)
    {
        var devicePosture = await _deviceService.GetPostureAsync(session.DeviceId, ct);
        var activity = await _activityService.GetRecentActivityAsync(session.SessionId, ct);

        return new SessionVerificationContext(
            DevicePosture: devicePosture,
            Activity: activity,
            LocationChanged: DetectLocationChange(session, activity),
            DeviceChanged: DetectDeviceChange(session, devicePosture),
            UnusualActivity: DetectUnusualActivity(activity));
    }

    public void InvalidateSession(string sessionId, string reason)
    {
        if (_sessions.TryGetValue(sessionId, out var session))
        {
            session.IsValid = false;
            _ = _notifier.NotifySessionTerminatedAsync(session, reason, CancellationToken.None);
        }
    }

    private bool DetectLocationChange(ZtnaSession session, ActivitySummary? activity) => false;
    private bool DetectDeviceChange(ZtnaSession session, DevicePosture? posture) => false;
    private bool DetectUnusualActivity(ActivitySummary? activity) => false;
}

public sealed class SessionManagerOptions
{
    public int VerificationIntervalSeconds { get; set; } = 60;
    public double RiskThreshold { get; set; } = 0.7;
}

public interface ISessionNotifier
{
    Task NotifySessionTerminatedAsync(ZtnaSession session, string reason, CancellationToken ct);
}

public interface IDevicePostureService
{
    Task<DevicePosture?> GetPostureAsync(string deviceId, CancellationToken ct);
}

public interface IActivityService
{
    Task<ActivitySummary?> GetRecentActivityAsync(string sessionId, CancellationToken ct);
}
```

## Client Integration

### Browser Extension

```javascript
// ZTNA browser extension for device posture and seamless access
class ZTNAExtension {
  constructor(config) {
    this.controllerUrl = config.controllerUrl;
    this.deviceId = this.getDeviceId();
  }

  // Collect device posture information
  async collectDevicePosture() {
    const posture = {
      deviceId: this.deviceId,
      platform: navigator.platform,
      userAgent: navigator.userAgent,
      screenResolution: `${screen.width}x${screen.height}`,
      timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
      language: navigator.language,
      cookiesEnabled: navigator.cookieEnabled,
      doNotTrack: navigator.doNotTrack,
      hardwareConcurrency: navigator.hardwareConcurrency,

      // Security indicators
      secureContext: window.isSecureContext,
      // Additional checks require native app/agent
    };

    // Calculate device fingerprint
    posture.fingerprint = await this.calculateFingerprint(posture);

    return posture;
  }

  // Intercept navigation to protected applications
  async interceptRequest(url) {
    const protectedDomains = await this.getProtectedDomains();
    const urlObj = new URL(url);

    if (protectedDomains.includes(urlObj.hostname)) {
      // Check if we have a valid session
      const session = await this.getSession(urlObj.hostname);

      if (!session) {
        // Redirect to ZTNA authentication
        return this.initiateAuthentication(url);
      }

      // Add ZTNA headers to request
      return {
        headers: {
          "X-ZTNA-Session": session.token,
          "X-ZTNA-Device": this.deviceId,
        },
      };
    }

    return null;
  }

  // Initiate ZTNA authentication flow
  async initiateAuthentication(targetUrl) {
    const posture = await this.collectDevicePosture();

    // Store target URL for redirect after auth
    sessionStorage.setItem("ztna_redirect", targetUrl);

    // Redirect to ZTNA controller
    const authUrl = new URL(`${this.controllerUrl}/auth/start`);
    authUrl.searchParams.set("redirect", targetUrl);
    authUrl.searchParams.set("device_id", this.deviceId);
    authUrl.searchParams.set("posture", JSON.stringify(posture));

    window.location.href = authUrl.toString();
  }

  // Handle authentication callback
  async handleCallback(params) {
    const token = params.get("token");
    const appDomain = params.get("app_domain");

    if (token && appDomain) {
      // Store session
      await this.storeSession(appDomain, {
        token: token,
        expiresAt: Date.now() + 8 * 60 * 60 * 1000, // 8 hours
      });

      // Redirect to original target
      const redirect = sessionStorage.getItem("ztna_redirect");
      if (redirect) {
        sessionStorage.removeItem("ztna_redirect");
        window.location.href = redirect;
      }
    }
  }

  // Continuous device posture reporting
  startPostureReporting() {
    setInterval(async () => {
      const posture = await this.collectDevicePosture();

      await fetch(`${this.controllerUrl}/api/device/posture`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          deviceId: this.deviceId,
          posture: posture,
          timestamp: new Date().toISOString(),
        }),
      });
    }, 60000); // Every minute
  }

  async calculateFingerprint(posture) {
    const data = JSON.stringify(posture);
    const buffer = new TextEncoder().encode(data);
    const hash = await crypto.subtle.digest("SHA-256", buffer);
    return Array.from(new Uint8Array(hash))
      .map((b) => b.toString(16).padStart(2, "0"))
      .join("");
  }
}

// Initialize extension
const ztna = new ZTNAExtension({
  controllerUrl: "https://ztna.example.com",
});

ztna.startPostureReporting();
```

## Monitoring and Analytics

### Session Analytics

```csharp
/// <summary>
/// ZTNA session analytics and monitoring.
/// </summary>
public sealed record SessionMetrics(
    int TotalSessions,
    int ActiveSessions,
    double AvgSessionDurationMinutes,
    Dictionary<string, int> SessionsByApp,
    Dictionary<string, int> SessionsByLocation,
    int DeniedRequests,
    int StepUpChallenges,
    RiskScoreDistribution RiskScoreDistribution);

public sealed record RiskScoreDistribution(int Low, int Medium, int High);

public sealed record ZtnaEvent(DateTimeOffset Timestamp, string EventType, Dictionary<string, object> Details);

public sealed class ZtnaAnalytics(ISessionStore sessionStore)
{
    private readonly ConcurrentQueue<ZtnaEvent> _eventLog = new();

    public void LogEvent(string eventType, Dictionary<string, object> details) =>
        _eventLog.Enqueue(new ZtnaEvent(DateTimeOffset.UtcNow, eventType, details));

    public SessionMetrics GetMetrics(int periodHours = 24)
    {
        var cutoff = DateTimeOffset.UtcNow.AddHours(-periodHours);

        var sessions = sessionStore.GetAll()
            .Where(s => s.CreatedAt >= cutoff)
            .ToList();

        var active = sessions.Where(s => s.IsValid).ToList();

        // Calculate average duration
        var durations = sessions.Select(s =>
        {
            var end = s.IsValid ? DateTimeOffset.UtcNow : s.ExpiresAt;
            return (end - s.CreatedAt).TotalMinutes;
        }).ToList();

        var avgDuration = durations.Count > 0 ? durations.Average() : 0;

        // Group by app
        var byApp = sessions
            .GroupBy(s => s.AppId)
            .ToDictionary(g => g.Key, g => g.Count());

        // Risk score distribution
        var riskDist = new RiskScoreDistribution(
            Low: sessions.Count(s => s.RiskScore < 0.3),
            Medium: sessions.Count(s => s.RiskScore >= 0.3 && s.RiskScore < 0.7),
            High: sessions.Count(s => s.RiskScore >= 0.7));

        // Count events
        var periodEvents = _eventLog.Where(e => e.Timestamp >= cutoff).ToList();
        var denied = periodEvents.Count(e => e.EventType == "access_denied");
        var stepUps = periodEvents.Count(e => e.EventType == "step_up_required");

        return new SessionMetrics(
            TotalSessions: sessions.Count,
            ActiveSessions: active.Count,
            AvgSessionDurationMinutes: avgDuration,
            SessionsByApp: byApp,
            SessionsByLocation: [], // Would need location data
            DeniedRequests: denied,
            StepUpChallenges: stepUps,
            RiskScoreDistribution: riskDist);
    }
}

public interface ISessionStore
{
    IEnumerable<ZtnaSession> GetAll();
    ZtnaSession? Get(string sessionId);
}
```

## Related Documentation

- **Parent Skill**: See `../SKILL.md` for zero trust overview
- **Zero Trust Architecture**: See `zero-trust-architecture.md` for architecture patterns

---

**Last Updated:** 2025-12-26
