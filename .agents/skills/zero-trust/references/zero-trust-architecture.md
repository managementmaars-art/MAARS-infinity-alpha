# Zero Trust Architecture Reference

## Overview

This reference provides detailed zero trust architecture patterns, implementation strategies, and integration guidance for enterprise environments.

## NIST Zero Trust Architecture

### Core Components (SP 800-207)

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                        ZERO TRUST ARCHITECTURE                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                        CONTROL PLANE                                  │   │
│  │  ┌───────────────┐    ┌───────────────┐    ┌───────────────────┐    │   │
│  │  │    Policy     │◄──▶│    Policy     │◄──▶│  Policy Info      │    │   │
│  │  │  Administrator│    │    Engine     │    │  Point (PIP)      │    │   │
│  │  └───────────────┘    └───────────────┘    └───────────────────┘    │   │
│  │         ▲                    │                      ▲               │   │
│  │         │                    ▼                      │               │   │
│  │  ┌───────────────────────────────────────────────────────────────┐  │   │
│  │  │                    Trust Algorithm                             │  │   │
│  │  │  • Identity verification    • Device posture                  │  │   │
│  │  │  • Behavioral analytics     • Threat intelligence             │  │   │
│  │  │  • Access history           • Resource sensitivity            │  │   │
│  │  └───────────────────────────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                    │                                         │
│                                    ▼                                         │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                         DATA PLANE                                    │   │
│  │                                                                       │   │
│  │  ┌─────────┐    ┌─────────────────────┐    ┌──────────────────────┐  │   │
│  │  │ Subject │───▶│ Policy Enforcement  │───▶│   Enterprise         │  │   │
│  │  │ (User/  │    │ Point (PEP)         │    │   Resources          │  │   │
│  │  │ Device) │    │ (Gateway/Proxy)     │    │   (Apps/Data/Svcs)   │  │   │
│  │  └─────────┘    └─────────────────────┘    └──────────────────────┘  │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility |
| --- | --- |
| **Policy Engine (PE)** | Makes access decisions based on policy and context |
| **Policy Administrator (PA)** | Establishes/terminates connections based on PE decisions |
| **Policy Enforcement Point (PEP)** | Gateway that enforces access decisions |
| **Policy Information Point (PIP)** | Provides context data for decisions |

## Trust Evaluation Framework

### Multi-Signal Trust Score

```csharp
/// <summary>
/// Trust evaluation framework with multiple signals.
/// </summary>
public sealed record TrustSignal(
    string Name,
    double Value,        // 0.0 - 1.0
    double Weight,       // Importance weight
    string Source,
    DateTimeOffset Timestamp,
    double Confidence);  // Confidence in the signal

public sealed record TrustEvaluationResult(
    double TrustScore,
    double Confidence,
    Dictionary<string, double> CategoryScores,
    string Decision,
    int SignalsEvaluated,
    DateTimeOffset Timestamp);

public sealed class TrustEvaluatorConfig
{
    public Dictionary<string, double> SignalWeights { get; set; } = new()
    {
        ["identity"] = 0.25,
        ["device"] = 0.20,
        ["network"] = 0.15,
        ["behavior"] = 0.20,
        ["context"] = 0.10,
        ["history"] = 0.10
    };
}

public sealed class TrustEvaluator(IOptions<TrustEvaluatorConfig> config)
{
    private readonly Dictionary<string, double> _signalWeights = config.Value.SignalWeights;

    private static readonly FrozenDictionary<string, string> SignalCategoryMapping =
        new Dictionary<string, string>
        {
            ["mfa_verified"] = "identity",
            ["sso_authenticated"] = "identity",
            ["password_age"] = "identity",
            ["device_managed"] = "device",
            ["device_compliant"] = "device",
            ["device_encrypted"] = "device",
            ["source_ip_trusted"] = "network",
            ["vpn_connected"] = "network",
            ["geo_location"] = "network",
            ["request_rate"] = "behavior",
            ["unusual_access"] = "behavior",
            ["time_of_access"] = "context",
            ["resource_sensitivity"] = "context",
            ["access_frequency"] = "history",
            ["past_violations"] = "history"
        }.ToFrozenDictionary();

    public TrustEvaluationResult Evaluate(IReadOnlyList<TrustSignal> signals)
    {
        // Group signals by category
        var categories = signals
            .GroupBy(s => CategorizeSignal(s.Name))
            .ToDictionary(g => g.Key, g => g.ToList());

        // Calculate category scores
        var categoryScores = categories.ToDictionary(
            kvp => kvp.Key,
            kvp => CalculateCategoryScore(kvp.Value));

        // Calculate weighted trust score
        var totalScore = 0.0;
        var totalWeight = 0.0;

        foreach (var (category, score) in categoryScores)
        {
            var weight = _signalWeights.GetValueOrDefault(category, 0.1);
            totalScore += score * weight;
            totalWeight += weight;
        }

        var trustScore = totalWeight > 0 ? totalScore / totalWeight : 0.0;
        var confidence = CalculateConfidence(signals);

        return new TrustEvaluationResult(
            TrustScore: trustScore,
            Confidence: confidence,
            CategoryScores: categoryScores,
            Decision: MakeDecision(trustScore, confidence),
            SignalsEvaluated: signals.Count,
            Timestamp: DateTimeOffset.UtcNow);
    }

    private static double CalculateCategoryScore(IReadOnlyList<TrustSignal> signals)
    {
        if (signals.Count == 0) return 0.0;

        var total = signals.Sum(s => s.Value * s.Confidence);
        var weight = signals.Sum(s => s.Confidence);

        return weight > 0 ? total / weight : 0.0;
    }

    private double CalculateConfidence(IReadOnlyList<TrustSignal> signals)
    {
        if (signals.Count == 0) return 0.0;

        var now = DateTimeOffset.UtcNow;
        var freshSignals = signals.Count(s => (now - s.Timestamp).TotalSeconds < 300);
        var freshnessFactor = (double)freshSignals / signals.Count;

        var categories = signals.Select(s => CategorizeSignal(s.Name)).Distinct().Count();
        var diversityFactor = (double)categories / _signalWeights.Count;

        var avgConfidence = signals.Average(s => s.Confidence);

        return freshnessFactor * 0.3 + diversityFactor * 0.3 + avgConfidence * 0.4;
    }

    private static string MakeDecision(double trustScore, double confidence) =>
        (trustScore, confidence) switch
        {
            ( >= 0.8, >= 0.7) => "ALLOW",
            ( < 0.3, _) => "DENY",
            ( < 0.7, _) or (_, < 0.5) => "CHALLENGE",
            _ => "ALLOW"
        };

    private static string CategorizeSignal(string signalName) =>
        SignalCategoryMapping.GetValueOrDefault(signalName, "other");
}

// Signal collectors
public interface ISignalCollector<TContext>
{
    Task<IReadOnlyList<TrustSignal>> CollectAsync(TContext context, CancellationToken ct = default);
}

public sealed record SessionContext(string UserId, bool MfaVerified, DateTimeOffset? MfaTime, bool SsoActive, DateTimeOffset? SsoTime);

public sealed class IdentitySignalCollector : ISignalCollector<SessionContext>
{
    public Task<IReadOnlyList<TrustSignal>> CollectAsync(SessionContext session, CancellationToken ct = default)
    {
        var signals = new List<TrustSignal>
        {
            new(
                Name: "mfa_verified",
                Value: session.MfaVerified ? 1.0 : 0.3,
                Weight: 1.0,
                Source: "identity_provider",
                Timestamp: session.MfaTime ?? DateTimeOffset.UtcNow,
                Confidence: 0.95)
        };

        if (session.SsoActive)
        {
            signals.Add(new TrustSignal(
                Name: "sso_authenticated",
                Value: 0.9,
                Weight: 0.8,
                Source: "sso_provider",
                Timestamp: session.SsoTime ?? DateTimeOffset.UtcNow,
                Confidence: 0.9));
        }

        return Task.FromResult<IReadOnlyList<TrustSignal>>(signals);
    }
}

public sealed record DevicePostureContext(string DeviceId, bool Managed, bool Compliant, bool Encrypted, DateTimeOffset? LastSync);

public sealed class DeviceSignalCollector : ISignalCollector<DevicePostureContext>
{
    public Task<IReadOnlyList<TrustSignal>> CollectAsync(DevicePostureContext posture, CancellationToken ct = default)
    {
        var timestamp = posture.LastSync ?? DateTimeOffset.UtcNow;

        var signals = new List<TrustSignal>
        {
            new(Name: "device_managed", Value: posture.Managed ? 1.0 : 0.2, Weight: 1.0,
                Source: "mdm", Timestamp: timestamp, Confidence: posture.Managed ? 0.9 : 0.5),

            new(Name: "device_compliant", Value: posture.Compliant ? 1.0 : 0.3, Weight: 0.9,
                Source: "mdm", Timestamp: timestamp, Confidence: 0.85),

            new(Name: "device_encrypted", Value: posture.Encrypted ? 1.0 : 0.0, Weight: 0.8,
                Source: "mdm", Timestamp: timestamp, Confidence: 0.95)
        };

        return Task.FromResult<IReadOnlyList<TrustSignal>>(signals);
    }
}
```

## Policy Definition Language

### Policy Structure

```yaml
# zero-trust-policy.yaml
apiVersion: zerotrust/v1
kind: AccessPolicy
metadata:
  name: corporate-apps-policy
  description: Access policy for corporate applications

spec:
  # Target resources
  resources:
    - type: application
      selector:
        labels:
          classification: internal
    - type: application
      names: ["hr-portal", "finance-app", "admin-console"]

  # Access rules (evaluated in order)
  rules:
    - name: admin-console-access
      description: Restrict admin console to IT team
      priority: 100
      match:
        resources:
          names: ["admin-console"]
      conditions:
        identity:
          groups: ["it-admins"]
          mfa_required: true
          mfa_max_age_hours: 1
        device:
          managed: required
          compliant: required
          platforms: ["windows", "macos"]
        network:
          allowed_locations: ["office", "vpn"]
        time:
          allowed_hours: "08:00-20:00"
          allowed_days: ["mon", "tue", "wed", "thu", "fri"]
      action: ALLOW

    - name: finance-app-access
      description: Finance app for finance team
      priority: 200
      match:
        resources:
          names: ["finance-app"]
      conditions:
        identity:
          groups: ["finance-team", "executives"]
          mfa_required: true
        device:
          managed: required
          encrypted: required
        context:
          max_risk_score: 0.5
      action: ALLOW

    - name: hr-portal-access
      description: HR portal for managers and HR
      priority: 300
      match:
        resources:
          names: ["hr-portal"]
      conditions:
        identity:
          groups: ["managers", "hr-team"]
          mfa_required: false
        device:
          managed: preferred  # Allow unmanaged with step-up
      action: CONDITIONAL
      conditional_actions:
        - when: "device.managed == false"
          require_step_up: true
          step_up_methods: ["push", "totp"]

    - name: default-internal-apps
      description: Default access for internal apps
      priority: 1000
      match:
        resources:
          labels:
            classification: internal
      conditions:
        identity:
          authenticated: required
        device:
          any: true
        context:
          max_risk_score: 0.7
      action: ALLOW

    - name: default-deny
      description: Deny all other access
      priority: 9999
      match:
        resources:
          all: true
      action: DENY
      log_level: warning
```

### Policy Engine Implementation

```csharp
/// <summary>
/// Zero trust policy engine implementation.
/// </summary>
public sealed record PolicyMatch(
    bool Matched,
    string PolicyName,
    string Action,
    Dictionary<string, List<string>> ConditionsMet,
    List<string> ConditionsFailed,
    List<ConditionalAction>? ConditionalActions = null);

public sealed record ConditionalAction(string When, bool RequireStepUp, List<string>? StepUpMethods);

public sealed record AccessRequest(
    ResourceInfo Resource,
    IdentityInfo Identity,
    DeviceInfo Device,
    NetworkInfo Network,
    ContextInfo Context);

public sealed record ResourceInfo(string Name, Dictionary<string, string> Labels);
public sealed record IdentityInfo(List<string> Groups, bool MfaVerified, double MfaAgeHours);
public sealed record DeviceInfo(bool Managed, bool Compliant, bool Encrypted, string Platform);
public sealed record NetworkInfo(string Location, string SourceIp);
public sealed record ContextInfo(double RiskScore);

public sealed class ZeroTrustPolicyEngine
{
    private readonly List<PolicyRule> _rules;

    public ZeroTrustPolicyEngine(ZeroTrustPolicy policy)
    {
        _rules = policy.Spec.Rules
            .OrderBy(r => r.Priority)
            .ToList();
    }

    public PolicyMatch Evaluate(AccessRequest request)
    {
        foreach (var rule in _rules)
        {
            if (!MatchesResource(rule, request.Resource))
                continue;

            var conditionsResult = EvaluateConditions(rule, request);

            if (conditionsResult.AllMet)
            {
                return new PolicyMatch(
                    Matched: true,
                    PolicyName: rule.Name,
                    Action: rule.Action,
                    ConditionsMet: conditionsResult.Met,
                    ConditionsFailed: [],
                    ConditionalActions: rule.ConditionalActions);
            }

            if (rule.Action == "CONDITIONAL" && rule.ConditionalActions is not null)
            {
                foreach (var condAction in rule.ConditionalActions)
                {
                    if (EvaluateExpression(condAction.When, request))
                    {
                        return new PolicyMatch(
                            Matched: true,
                            PolicyName: rule.Name,
                            Action: "STEP_UP",
                            ConditionsMet: conditionsResult.Met,
                            ConditionsFailed: conditionsResult.Failed,
                            ConditionalActions: [condAction]);
                    }
                }
            }
        }

        // No matching rule - implicit deny
        return new PolicyMatch(
            Matched: false,
            PolicyName: "default-implicit-deny",
            Action: "DENY",
            ConditionsMet: [],
            ConditionsFailed: ["no matching policy"]);
    }

    private static bool MatchesResource(PolicyRule rule, ResourceInfo resource)
    {
        var matchSpec = rule.Match?.Resources;
        if (matchSpec is null) return false;

        // Match by name
        if (matchSpec.Names?.Contains(resource.Name) == true)
            return true;

        // Match by labels
        if (matchSpec.Labels is not null)
        {
            return matchSpec.Labels.All(kvp =>
                resource.Labels.TryGetValue(kvp.Key, out var val) && val == kvp.Value);
        }

        // Match all
        return matchSpec.All;
    }

    private static ConditionsResult EvaluateConditions(PolicyRule rule, AccessRequest request)
    {
        var result = new ConditionsResult();

        if (rule.Conditions?.Identity is not null)
        {
            var identityResult = CheckIdentityConditions(rule.Conditions.Identity, request.Identity);
            result.Met["identity"] = identityResult.Met;
            result.Failed.AddRange(identityResult.Failed);
            if (identityResult.Failed.Count > 0) result.AllMet = false;
        }

        if (rule.Conditions?.Device is not null)
        {
            var deviceResult = CheckDeviceConditions(rule.Conditions.Device, request.Device);
            result.Met["device"] = deviceResult.Met;
            result.Failed.AddRange(deviceResult.Failed);
            if (deviceResult.Failed.Count > 0) result.AllMet = false;
        }

        return result;
    }

    private static (List<string> Met, List<string> Failed) CheckIdentityConditions(
        IdentityConditions conditions, IdentityInfo identity)
    {
        List<string> met = [], failed = [];

        if (conditions.Groups is not null)
        {
            var requiredGroups = conditions.Groups.ToHashSet();
            var userGroups = identity.Groups.ToHashSet();
            if (requiredGroups.Overlaps(userGroups))
                met.Add("group_membership");
            else
                failed.Add($"User not in required groups: {string.Join(", ", requiredGroups)}");
        }

        if (conditions.MfaRequired)
        {
            if (identity.MfaVerified) met.Add("mfa_verified");
            else failed.Add("MFA not verified");
        }

        if (conditions.MfaMaxAgeHours.HasValue)
        {
            if (identity.MfaAgeHours <= conditions.MfaMaxAgeHours.Value)
                met.Add("mfa_age");
            else
                failed.Add($"MFA too old: {identity.MfaAgeHours}h > {conditions.MfaMaxAgeHours}h");
        }

        return (met, failed);
    }

    private static (List<string> Met, List<string> Failed) CheckDeviceConditions(
        DeviceConditions conditions, DeviceInfo device)
    {
        List<string> met = [], failed = [];

        if (conditions.Managed == "required")
        {
            if (device.Managed) met.Add("device_managed");
            else failed.Add("Device not managed");
        }

        if (conditions.Compliant == "required")
        {
            if (device.Compliant) met.Add("device_compliant");
            else failed.Add("Device not compliant");
        }

        if (conditions.Encrypted == "required")
        {
            if (device.Encrypted) met.Add("device_encrypted");
            else failed.Add("Device not encrypted");
        }

        if (conditions.Platforms?.Contains(device.Platform) == false)
            failed.Add($"Platform {device.Platform} not allowed");
        else if (conditions.Platforms is not null)
            met.Add("platform_allowed");

        return (met, failed);
    }

    private static bool EvaluateExpression(string expression, AccessRequest request)
    {
        // Simple expression evaluation (e.g., "device.managed == false")
        return expression switch
        {
            "device.managed == false" => !request.Device.Managed,
            "device.compliant == false" => !request.Device.Compliant,
            _ => false
        };
    }
}

// Supporting types for policy structure
public sealed class ConditionsResult
{
    public Dictionary<string, List<string>> Met { get; } = [];
    public List<string> Failed { get; } = [];
    public bool AllMet { get; set; } = true;
}

public sealed class ZeroTrustPolicy
{
    public string ApiVersion { get; set; } = "zerotrust/v1";
    public string Kind { get; set; } = "AccessPolicy";
    public PolicySpec Spec { get; set; } = new();
}

public sealed class PolicySpec
{
    public List<PolicyRule> Rules { get; set; } = [];
}

public sealed class PolicyRule
{
    public string Name { get; set; } = "";
    public int Priority { get; set; } = 1000;
    public ResourceMatch? Match { get; set; }
    public PolicyConditions? Conditions { get; set; }
    public string Action { get; set; } = "DENY";
    public List<ConditionalAction>? ConditionalActions { get; set; }
}

public sealed class ResourceMatch { public ResourceMatchSpec? Resources { get; set; } }
public sealed class ResourceMatchSpec
{
    public List<string>? Names { get; set; }
    public Dictionary<string, string>? Labels { get; set; }
    public bool All { get; set; }
}

public sealed class PolicyConditions
{
    public IdentityConditions? Identity { get; set; }
    public DeviceConditions? Device { get; set; }
}

public sealed class IdentityConditions
{
    public List<string>? Groups { get; set; }
    public bool MfaRequired { get; set; }
    public int? MfaMaxAgeHours { get; set; }
}

public sealed class DeviceConditions
{
    public string? Managed { get; set; }
    public string? Compliant { get; set; }
    public string? Encrypted { get; set; }
    public List<string>? Platforms { get; set; }
}
```

## Deployment Patterns

### Cloud-Native Zero Trust

```yaml
# Kubernetes deployment with zero trust
apiVersion: v1
kind: Namespace
metadata:
  name: zero-trust-infra
  labels:
    pod-security.kubernetes.io/enforce: restricted
---
# Identity-aware proxy deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: identity-proxy
  namespace: zero-trust-infra
spec:
  replicas: 3
  selector:
    matchLabels:
      app: identity-proxy
  template:
    metadata:
      labels:
        app: identity-proxy
    spec:
      containers:
        - name: proxy
          image: zerotrust/identity-proxy:v1.0
          ports:
            - containerPort: 8443
          env:
            - name: POLICY_ENGINE_URL
              value: "http://policy-engine:8080"
            - name: IDENTITY_PROVIDER
              valueFrom:
                secretKeyRef:
                  name: idp-config
                  key: url
          volumeMounts:
            - name: tls
              mountPath: /etc/tls
              readOnly: true
            - name: policy
              mountPath: /etc/policy
              readOnly: true
      volumes:
        - name: tls
          secret:
            secretName: proxy-tls
        - name: policy
          configMap:
            name: access-policies
---
# Policy engine deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: policy-engine
  namespace: zero-trust-infra
spec:
  replicas: 2
  selector:
    matchLabels:
      app: policy-engine
  template:
    metadata:
      labels:
        app: policy-engine
    spec:
      containers:
        - name: engine
          image: zerotrust/policy-engine:v1.0
          ports:
            - containerPort: 8080
          env:
            - name: SIGNAL_COLLECTORS
              value: "identity,device,network,behavior"
            - name: TRUST_THRESHOLD
              value: "0.7"
```

## Maturity Model

### Zero Trust Maturity Levels

| Level | Identity | Device | Network | Data | Workload |
| --- | --- | --- | --- | --- | --- |
| **Traditional** | Passwords | None | Perimeter | None | None |
| **Initial** | SSO | Inventory | Segmented | Classification | Hardened |
| **Advanced** | MFA + Context | Posture | Micro-segmented | Encrypted | Isolated |
| **Optimal** | Continuous | Real-time | Software-defined | DLP + Rights | Immutable |

## Related Documentation

- **Parent Skill**: See `../SKILL.md` for zero trust overview
- **ZTNA Implementation**: See `ztna-implementation.md` for network access

---

**Last Updated:** 2025-12-26
